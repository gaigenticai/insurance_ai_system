#!/usr/bin/env python3

import argparse
import os
import sys
from typing import Dict, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import API framework
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import system modules
from agents.config_agent import ConfigAgent
from modules.underwriting.flow import UnderwritingFlow
from modules.claims.flow import ClaimsFlow
from modules.actuarial.flow import ActuarialFlow
from utils.logging_utils import audit_logger
from utils.error_utils import get_error_handler

# Create FastAPI app
app = FastAPI(
    title="Insurance AI System API",
    description="Production-grade API for insurance underwriting, claims, and actuarial analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system components
config_agent = ConfigAgent(config_dir=os.path.join(project_root, "insurance_ai_system/config"))
logger = audit_logger.get_logger("api")
error_handler = get_error_handler(logger)

# Dependency for institution ID validation
async def validate_institution(request: Request):
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
    try:
        return await call_next(request)
    except Exception as e:
        # Log the error
        logger.error(f"API error: {str(e)}")
        
        # Return structured error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "Error",
                "message": "An internal server error occurred",
                "error_type": type(e).__name__,
                "error_detail": str(e)
            }
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Underwriting endpoints
@app.post("/underwriting/evaluate")
async def evaluate_application(
    application: Dict[str, Any],
    institution_id: str = Depends(validate_institution)
):
    logger.info(f"Received underwriting request for institution: {institution_id}")
    
    try:
        flow = UnderwritingFlow(config_agent)
        result = flow.run(application, institution_id)
        
        # Log successful processing
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="UNDERWRITING_PROCESSED",
            details={"application_id": application.get("applicant_id"), "result_status": result.get("status")},
            severity="INFO"
        )
        
        return result
    except Exception as e:
        # Log error
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="UNDERWRITING_ERROR",
            details={"application_id": application.get("applicant_id"), "error": str(e)},
            severity="ERROR"
        )
        
        raise HTTPException(status_code=500, detail=str(e))

# Claims endpoints
@app.post("/claims/process")
async def process_claim(
    claim: Dict[str, Any],
    institution_id: str = Depends(validate_institution)
):
    logger.info(f"Received claims processing request for institution: {institution_id}")
    
    try:
        flow = ClaimsFlow(config_agent)
        result = flow.run(claim, institution_id)
        
        # Log successful processing
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="CLAIM_PROCESSED",
            details={"claim_id": claim.get("claim_id"), "result_status": result.get("status")},
            severity="INFO"
        )
        
        return result
    except Exception as e:
        # Log error
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="CLAIM_ERROR",
            details={"claim_id": claim.get("claim_id"), "error": str(e)},
            severity="ERROR"
        )
        
        raise HTTPException(status_code=500, detail=str(e))

# Actuarial endpoints
@app.post("/actuarial/analyze")
async def analyze_data(
    data_source_info: Dict[str, Any],
    institution_id: str = Depends(validate_institution)
):
    logger.info(f"Received actuarial analysis request for institution: {institution_id}")
    
    try:
        flow = ActuarialFlow(config_agent)
        result = flow.run(data_source_info, institution_id)
        
        # Log successful processing
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="ACTUARIAL_ANALYZED",
            details={"data_source": data_source_info.get("data_path"), "result_status": result.get("status")},
            severity="INFO"
        )
        
        return result
    except Exception as e:
        # Log error
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="API",
            event_type="ACTUARIAL_ERROR",
            details={"data_source": data_source_info.get("data_path"), "error": str(e)},
            severity="ERROR"
        )
        
        raise HTTPException(status_code=500, detail=str(e))

# Run the API server if executed directly
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Insurance AI System API.")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the API server")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the API server")
    args = parser.parse_args()
    
    logger.info(f"Starting Insurance AI System API on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
