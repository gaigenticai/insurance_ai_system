"""
Enhanced API server for the Insurance AI System.
Implements FastAPI with async processing via Celery.
"""

import os
import logging
import uuid
from typing import Dict, Any, Optional
from psycopg2.extras import Json

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn
from fastapi_limiter.depends import RateLimiter
import redis
from fastapi_limiter import FastAPILimiter
import redis
from fastapi_limiter import FastAPILimiter

from utils.knowledge_base import get_answer

from agents.config_agent import ConfigAgent
from schemas import (
    UnderwritingRequest, UnderwritingResponse,
    ClaimsRequest, ClaimsResponse,
    ActuarialRequest, ActuarialResponse,
    TaskStatusResponse, ReportResponse,
    BaseResponse, TaskStatus, TaskType
)
from tasks import (
    run_underwriting_task, run_claims_task, run_actuarial_task,
    generate_report_task, create_task_record, get_task_status
)
from db_connection import get_record_by_id
from utils.logging_utils import audit_logger

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Insurance AI System API",
    description="Production-grade API for insurance underwriting, claims, and actuarial analysis",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system components lazily
config_agent = None

def get_config_agent():
    """Get config agent, initializing if needed"""
    global config_agent
    if config_agent is None:
        config_agent = ConfigAgent(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config"))
    return config_agent

# Dependency for institution ID validation
async def validate_institution(request: Request) -> str:
    """
    Validate the institution ID from the request header.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Validated institution ID
        
    Raises:
        HTTPException: If institution ID is missing or invalid
    """
    institution_id = request.headers.get("X-Institution-ID")
    if not institution_id:
        raise HTTPException(status_code=400, detail="Missing institution ID header")
    
    # Validate institution exists in config
    try:
        get_config_agent().get_config(institution_id)
        return institution_id
    except Exception as e:
        logger.error(f"Invalid institution ID: {institution_id}, error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid institution ID: {institution_id}")


# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """
    Middleware for handling errors in API requests.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware function
        
    Returns:
        Response object
    """
    try:
        return await call_next(request)
    except Exception as e:
        # Log the error
        logger.error(f"API error: {str(e)}")
        
        # Return structured error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "An internal server error occurred",
                "error_type": type(e).__name__,
                "error_detail": str(e)
            }
        )


# Custom docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI endpoint.
    
    Returns:
        HTML response with Swagger UI
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


# Health check endpoint
@app.get("/health", response_model=BaseResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status response
    """
    return {
        "status": "healthy",
        "message": "Insurance AI System API is running"
    }


# Simple chatbot endpoint using the knowledge base
@app.post("/chatbot", tags=["System"])
async def chatbot(question: Dict[str, str]):
    """Return a canned answer from the knowledge base."""
    q = question.get("question", "")
    answer = get_answer(q)
    return {"answer": answer}


# Underwriting endpoint
@app.post("/run/underwriting", response_model=UnderwritingResponse, tags=["Underwriting"], dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def run_underwriting(
    request: UnderwritingRequest,
    background_tasks: BackgroundTasks,
    institution_id: str = Depends(validate_institution)
):
    """
    Run underwriting analysis asynchronously.
    
    Args:
        request: Underwriting request data
        background_tasks: FastAPI background tasks
        institution_id: Validated institution ID
        
    Returns:
        Response with task ID
    """
    logger.info(f"Received underwriting request for institution: {institution_id}")
    
    try:
        # Convert request to dictionary
        application_data = request.dict()
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create task record
        create_task_record(task_id, TaskType.UNDERWRITING.value, institution_id)
        
        # Run task asynchronously
        task = run_underwriting_task.apply_async(
            args=[application_data, institution_id],
            task_id=task_id
        )
        
        # Log audit event
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="UNDERWRITING_REQUESTED",
            details=Json({"application_id": application_data.get("applicant_id"), "task_id": task_id}),
            severity="INFO"
        )
        
        return {
            "status": "success",
            "message": "Underwriting task created successfully",
            "task_id": task_id,
            "application_id": application_data.get("applicant_id")
        }
    except Exception as e:
        # Log error
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="UNDERWRITING_ERROR",
            details=Json({"application_id": request.applicant_id, "error": str(e)}),
            severity="ERROR"
        )
        
        raise HTTPException(status_code=500, detail=str(e))


# Claims endpoint
@app.post("/run/claims", response_model=ClaimsResponse, tags=["Claims"], dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def run_claims(
    request: ClaimsRequest,
    background_tasks: BackgroundTasks,
    institution_id: str = Depends(validate_institution)
):
    """
    Run claims processing asynchronously.
    
    Args:
        request: Claims request data
        background_tasks: FastAPI background tasks
        institution_id: Validated institution ID
        
    Returns:
        Response with task ID
    """
    logger.info(f"Received claims processing request for institution: {institution_id}")
    
    try:
        # Convert request to dictionary
        claim_data = request.dict()
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create task record
        create_task_record(task_id, TaskType.CLAIMS.value, institution_id)
        
        # Run task asynchronously
        task = run_claims_task.apply_async(
            args=[claim_data, institution_id],
            task_id=task_id
        )
        
        # Log audit event
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="CLAIM_REQUESTED",
            details=Json({"claim_id": claim_data.get("claim_id"), "task_id": task_id}),
            severity="INFO"
        )
        
        return {
            "status": "success",
            "message": "Claims task created successfully",
            "task_id": task_id,
            "claim_id": claim_data.get("claim_id")
        }
    except Exception as e:
        # Log error
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="CLAIM_ERROR",
            details=Json({"claim_id": request.claim_id, "error": str(e)}),
            severity="ERROR"
        )
        
        raise HTTPException(status_code=500, detail=str(e))


# Actuarial endpoint
@app.post("/run/actuarial", response_model=ActuarialResponse, tags=["Actuarial"], dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def run_actuarial(
    request: ActuarialRequest,
    background_tasks: BackgroundTasks,
    institution_id: str = Depends(validate_institution)
):
    """
    Run actuarial analysis asynchronously.
    
    Args:
        request: Actuarial request data
        background_tasks: FastAPI background tasks
        institution_id: Validated institution ID
        
    Returns:
        Response with task ID
    """
    logger.info(f"Received actuarial analysis request for institution: {institution_id}")
    
    try:
        # Convert request to dictionary
        data_source_info = request.dict()
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create task record
        create_task_record(task_id, TaskType.ACTUARIAL.value, institution_id)
        
        # Run task asynchronously
        task = run_actuarial_task.apply_async(
            args=[data_source_info, institution_id],
            task_id=task_id
        )
        
        # Log audit event
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="ACTUARIAL_REQUESTED",
            details=Json({"analysis_id": data_source_info.get("analysis_id"), "task_id": task_id}),
            severity="INFO"
        )
        
        return {
            "status": "success",
            "message": "Actuarial task created successfully",
            "task_id": task_id,
            "analysis_id": data_source_info.get("analysis_id")
        }
    except Exception as e:
        # Log error
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="ACTUARIAL_ERROR",
            details=Json({"analysis_id": request.analysis_id, "error": str(e)}),
            severity="ERROR"
        )
        
        raise HTTPException(status_code=500, detail=str(e))


# Task status endpoint
@app.get("/status/{task_id}", response_model=TaskStatusResponse, tags=["Tasks"])
async def get_task_status_endpoint(
    task_id: str,
    institution_id: str = Depends(validate_institution)
):
    """
    Get the status of a task.
    
    Args:
        task_id: Task ID
        institution_id: Validated institution ID
        
    Returns:
        Task status response
    """
    logger.info(f"Received task status request for task: {task_id}")
    
    try:
        # Get task status
        task_data = get_task_status(task_id)
        
        if not task_data:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
        
        # Check if task belongs to institution
        if task_data.get("institution_id") != institution_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this task")
        
        # Return task status
        return {
            "status": "success",
            "message": "Task status retrieved successfully",
            "task_id": task_id,
            "task_type": task_data.get("type"),
            "task_status": task_data.get("status"),
            "created_at": task_data.get("created_at"),
            "updated_at": task_data.get("updated_at"),
            "result": task_data.get("result"),
            "error": task_data.get("error"),
            "report_id": task_data.get("report_id")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Report endpoint
@app.get("/report/{report_id}", response_model=ReportResponse, tags=["Reports"])
async def get_report(
    report_id: str,
    institution_id: str = Depends(validate_institution)
):
    """
    Get a report by ID.
    
    Args:
        report_id: Report ID
        institution_id: Validated institution ID
        
    Returns:
        Report response
    """
    logger.info(f"Received report request for report: {report_id}")
    
    try:
        # Get report
        report_data = get_record_by_id("reports", report_id, id_column="report_id")
        
        if not report_data:
            raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
        
        # Check if report belongs to institution
        if report_data.get("institution_id") != institution_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this report")
        
        # Return report
        return {
            "status": "success",
            "message": "Report retrieved successfully",
            "report_id": report_id,
            "report_type": report_data.get("type"),
            "created_at": report_data.get("created_at"),
            "content": report_data.get("content"),
            "task_id": report_data.get("task_id")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI-Enhanced Endpoints
# ============================================================================

from pydantic import BaseModel, Field
from datetime import datetime
from ai_services.ai_service_manager import AIServiceManager
from ai_services.ai_agents import AIUnderwritingAgent, AIClaimsAgent, AIActuarialAgent

# AI Request/Response Models
class AIUnderwritingRequest(BaseModel):
    application_data: Dict[str, Any] = Field(..., description="Underwriting application data")
    use_ai_only: bool = Field(default=False, description="Use AI-only processing")

class AIClaimsRequest(BaseModel):
    claim_data: Dict[str, Any] = Field(..., description="Claims data")
    use_ai_only: bool = Field(default=False, description="Use AI-only processing")

class AIActuarialRequest(BaseModel):
    analysis_data: Dict[str, Any] = Field(..., description="Actuarial analysis data")
    use_ai_only: bool = Field(default=False, description="Use AI-only processing")

class AIConfigurationRequest(BaseModel):
    provider: str = Field(..., description="AI provider (openai, anthropic, local)")
    model_name: str = Field(..., description="Model name")
    api_key: Optional[str] = Field(None, description="API key")
    base_url: Optional[str] = Field(None, description="Base URL for local models")
    temperature: float = Field(default=0.7, description="Model temperature")
    max_tokens: int = Field(default=2000, description="Maximum tokens")

class AIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    ai_insights: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# AI Service Manager dependency
def get_ai_service_manager() -> AIServiceManager:
    return AIServiceManager()

@app.post("/ai/underwriting/analyze", response_model=AIResponse, tags=["AI Services"])
async def ai_underwriting_analysis(
    request: AIUnderwritingRequest,
    institution_id: str = Depends(validate_institution),
    ai_manager: AIServiceManager = Depends(get_ai_service_manager)
):
    """Perform AI-enhanced underwriting analysis."""
    try:
        start_time = datetime.utcnow()
        
        ai_agent = AIUnderwritingAgent(config_agent)
        result = await ai_agent.execute(request.application_data, institution_id)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AIResponse(
            success=True,
            data=result,
            ai_insights=result,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"AI underwriting analysis failed: {str(e)}")
        return AIResponse(success=False, error=str(e))

@app.post("/ai/claims/analyze", response_model=AIResponse, tags=["AI Services"])
async def ai_claims_analysis(
    request: AIClaimsRequest,
    institution_id: str = Depends(validate_institution),
    ai_manager: AIServiceManager = Depends(get_ai_service_manager)
):
    """Perform AI-enhanced claims analysis."""
    try:
        start_time = datetime.utcnow()
        
        ai_agent = AIClaimsAgent(config_agent)
        result = await ai_agent.execute(request.claim_data, institution_id)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AIResponse(
            success=True,
            data=result,
            ai_insights=result,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"AI claims analysis failed: {str(e)}")
        return AIResponse(success=False, error=str(e))

@app.post("/ai/actuarial/analyze", response_model=AIResponse, tags=["AI Services"])
async def ai_actuarial_analysis(
    request: AIActuarialRequest,
    institution_id: str = Depends(validate_institution),
    ai_manager: AIServiceManager = Depends(get_ai_service_manager)
):
    """Perform AI-enhanced actuarial analysis."""
    try:
        start_time = datetime.utcnow()
        
        ai_agent = AIActuarialAgent(config_agent)
        result = await ai_agent.execute(request.analysis_data, institution_id)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AIResponse(
            success=True,
            data=result,
            ai_insights=result,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"AI actuarial analysis failed: {str(e)}")
        return AIResponse(success=False, error=str(e))

@app.post("/ai/configuration", response_model=AIResponse, tags=["AI Services"])
async def update_ai_configuration(
    request: AIConfigurationRequest,
    institution_id: str = Depends(validate_institution)
):
    """Update AI configuration settings."""
    try:
        config_data = {
            "provider": request.provider,
            "model_name": request.model_name,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        if request.api_key:
            config_data["api_key"] = request.api_key
        if request.base_url:
            config_data["base_url"] = request.base_url
            
        result = get_config_agent().update_ai_configuration(config_data)
        
        return AIResponse(
            success=True,
            data={"configuration_updated": True, "settings": result}
        )
        
    except Exception as e:
        logger.error(f"AI configuration update failed: {str(e)}")
        return AIResponse(success=False, error=str(e))

@app.get("/ai/configuration", response_model=AIResponse, tags=["AI Services"])
async def get_ai_configuration(
    institution_id: str = Depends(validate_institution)
):
    """Get current AI configuration settings."""
    try:
        result = get_config_agent().get_ai_configuration()
        return AIResponse(success=True, data=result)
        
    except Exception as e:
        logger.error(f"AI configuration retrieval failed: {str(e)}")
        return AIResponse(success=False, error=str(e))

@app.get("/ai/models/available", response_model=AIResponse, tags=["AI Services"])
async def get_available_models():
    """Get list of available AI models."""
    try:
        models = {
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
            "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "local": ["llama2-7b", "llama2-13b", "mistral-7b", "codellama-7b"]
        }
        
        return AIResponse(success=True, data={"available_models": models})
        
    except Exception as e:
        logger.error(f"Failed to get available models: {str(e)}")
        return AIResponse(success=False, error=str(e))

@app.get("/ai/health", response_model=AIResponse, tags=["AI Services"])
async def ai_health_check(
    ai_manager: AIServiceManager = Depends(get_ai_service_manager)
):
    """Check AI services health status."""
    try:
        health_status = {
            "ai_service_manager": "healthy",
            "configuration": "loaded",
            "providers": {}
        }
        
        # Test each provider
        for provider_name in ["openai", "anthropic", "local"]:
            try:
                ai_manager.get_provider(provider_name)
                health_status["providers"][provider_name] = "available"
            except:
                health_status["providers"][provider_name] = "unavailable"
        
        return AIResponse(success=True, data=health_status)
        
    except Exception as e:
        logger.error(f"AI health check failed: {str(e)}")
        return AIResponse(success=False, error=str(e))


@app.get("/ai/analytics", response_model=AIResponse, tags=["AI Analytics"])
async def get_ai_analytics(
    hours_back: int = 24,
    ai_manager: AIServiceManager = Depends(get_ai_service_manager)
):
    """Get comprehensive AI analytics and performance metrics."""
    try:
        analytics = ai_manager.get_ai_analytics(hours_back)
        
        return AIResponse(
            success=True,
            data=analytics
        )
    except Exception as e:
        logger.error(f"Failed to get AI analytics: {e}")
        return AIResponse(
            success=False,
            error=f"Failed to get AI analytics: {str(e)}"
        )


@app.get("/ai/analytics/export", tags=["AI Analytics"])
async def export_ai_metrics(
    format: str = "json",
    ai_manager: AIServiceManager = Depends(get_ai_service_manager)
):
    """Export AI metrics in specified format."""
    try:
        metrics_data = ai_manager.export_ai_metrics(format)
        
        if format.lower() == "json":
            from fastapi.responses import Response
            return Response(
                content=metrics_data,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=ai_metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"}
            )
        else:
            return AIResponse(
                success=False,
                error=f"Unsupported export format: {format}"
            )
    except Exception as e:
        logger.error(f"Failed to export AI metrics: {e}")
        return AIResponse(
            success=False,
            error=f"Failed to export AI metrics: {str(e)}"
        )


@app.post("/ai/benchmark", response_model=AIResponse, tags=["AI Analytics"])
async def benchmark_ai_providers(
    test_prompt: Optional[str] = None,
    ai_manager: AIServiceManager = Depends(get_ai_service_manager)
):
    """Benchmark all available AI providers."""
    try:
        if not test_prompt:
            test_prompt = "Analyze this insurance application: 35-year-old software engineer, $85,000 annual income, excellent credit score, requesting $500,000 term life insurance."
        
        benchmark_results = await ai_manager.benchmark_providers(test_prompt)
        
        return AIResponse(
            success=True,
            data=benchmark_results
        )
    except Exception as e:
        logger.error(f"AI provider benchmark failed: {e}")
        return AIResponse(
            success=False,
            error=f"AI provider benchmark failed: {str(e)}"
        )


@app.get("/ai/providers/comparison", response_model=AIResponse, tags=["AI Analytics"])
async def get_provider_comparison(
    ai_manager: AIServiceManager = Depends(get_ai_service_manager)
):
    """Get performance comparison between AI providers."""
    try:
        analytics = ai_manager.get_ai_analytics()
        
        return AIResponse(
            success=True,
            data={
                "provider_comparison": analytics["provider_comparison"],
                "model_performance": analytics["model_performance"]
            }
        )
    except Exception as e:
        logger.error(f"Failed to get provider comparison: {e}")
        return AIResponse(
            success=False,
            error=f"Failed to get provider comparison: {str(e)}"
        )


# Run the API server if executed directly
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Insurance AI System API.")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the API server")
    parser.add_argument("--port", type=int, default=int(os.environ.get("API_PORT", 8080)), 
                       help="Port to bind the API server")
    args = parser.parse_args()
    
    logger.info(f"Starting Insurance AI System API on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from schemas import User, UserCreate, Token, TokenData
from core.security.rbac import UserRole, Permission, has_permission




# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    # In a real application, you would fetch the user from the database
    # For this example, we'll use a dummy user
    if token_data.username == "admin":
        return User(id=uuid.uuid4(), email="admin@example.com", username="admin", is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow(), role="admin")
    elif token_data.username == "user":
        return User(id=uuid.uuid4(), email="user@example.com", username="user", is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow(), role="customer")
    raise credentials_exception

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_permission(permission: Permission):
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not has_permission(UserRole(current_user.role), permission):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return permission_checker




@app.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    if form_data.username == "admin" and form_data.password == "admin":
        user = User(id=uuid.uuid4(), email="admin@example.com", username="admin", is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow(), role="admin")
    elif form_data.username == "user" and form_data.password == "user":
        user = User(id=uuid.uuid4(), email="user@example.com", username="user", is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow(), role="customer")

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/protected-admin-route", tags=["Admin"], dependencies=[Depends(require_permission(Permission.MANAGE_USERS))])
async def protected_admin_route():
    return {"message": "Welcome, admin user! You have access to this protected route."}




from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis




from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    redis_instance = redis.from_url("redis://default:dDkwkLMlexeGsZTkWbfOcxXYJsJMRfpM@hopper.proxy.rlwy.net:20859", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_instance)
    yield
    # Cleanup: Release resources
    await redis_instance.close()

app = FastAPI(
    title="Insurance AI System API",
    description="Production-grade API for insurance underwriting, claims, and actuarial analysis",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    lifespan=lifespan
)


