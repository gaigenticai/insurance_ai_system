"""
Enhanced API server for the Insurance AI System.
Implements FastAPI with async processing via Celery.
"""

import os
import logging
import uuid
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn

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

# Initialize system components
config_agent = ConfigAgent(config_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "config"))

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
        config_agent.get_config(institution_id)
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


# Underwriting endpoint
@app.post("/run/underwriting", response_model=UnderwritingResponse, tags=["Underwriting"])
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
            details={"application_id": application_data.get("applicant_id"), "task_id": task_id},
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
            details={"application_id": request.applicant_id, "error": str(e)},
            severity="ERROR"
        )
        
        raise HTTPException(status_code=500, detail=str(e))


# Claims endpoint
@app.post("/run/claims", response_model=ClaimsResponse, tags=["Claims"])
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
            details={"claim_id": claim_data.get("claim_id"), "task_id": task_id},
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
            details={"claim_id": request.claim_id, "error": str(e)},
            severity="ERROR"
        )
        
        raise HTTPException(status_code=500, detail=str(e))


# Actuarial endpoint
@app.post("/run/actuarial", response_model=ActuarialResponse, tags=["Actuarial"])
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
            details={"analysis_id": data_source_info.get("analysis_id"), "task_id": task_id},
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
            details={"analysis_id": request.analysis_id, "error": str(e)},
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
            "status": task_data.get("status"),
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
