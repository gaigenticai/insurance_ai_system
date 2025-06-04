"""
Pydantic schemas for the Insurance AI System API.
Provides strict typing and validation for API requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Enum definitions
class TaskStatus(str, Enum):
    """Task status enum for tracking Celery tasks."""
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"
    RETRY = "RETRY"


class TaskType(str, Enum):
    """Task type enum for categorizing tasks."""
    UNDERWRITING = "underwriting"
    CLAIMS = "claims"
    ACTUARIAL = "actuarial"
    REPORT = "report"


class ReportType(str, Enum):
    """Report type enum for categorizing reports."""
    UNDERWRITING = "underwriting"
    CLAIMS = "claims"
    ACTUARIAL = "actuarial"
    AUDIT = "audit"


class EventType(str, Enum):
    """Event type enum for categorizing events."""
    UNDERWRITING_COMPLETED = "underwriting.completed"
    CLAIMS_FLAGGED = "claims.flagged"
    ACTUARIAL_BENCHMARKED = "actuarial.benchmarked"


# Base models
class BaseRequest(BaseModel):
    """Base model for all API requests."""
    institution_id: str = Field(..., description="Institution identifier")


class BaseResponse(BaseModel):
    """Base model for all API responses."""
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")


# Underwriting models
class UnderwritingRequest(BaseRequest):
    """Request model for underwriting applications."""
    applicant_id: str = Field(..., description="Unique identifier for the applicant")
    full_name: str = Field(..., description="Full name of the applicant")
    address: str = Field(..., description="Address of the applicant")
    date_of_birth: str = Field(..., description="Date of birth of the applicant")
    income: float = Field(..., description="Annual income of the applicant")
    credit_score: Optional[int] = Field(None, description="Credit score of the applicant")
    debt_to_income_ratio: Optional[float] = Field(None, description="Debt to income ratio of the applicant")
    address_location_tag: Optional[str] = Field(None, description="Location tag for the address")
    document_text: Optional[str] = Field(None, description="OCR text from submitted documents")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional data for the application")

    class Config:
        schema_extra = {
            "example": {
                "institution_id": "institution_a",
                "applicant_id": "UW-TEST-100",
                "full_name": "Alice Example",
                "address": "123 Main St",
                "date_of_birth": "01/01/1990",
                "income": 80000,
                "credit_score": 720,
                "debt_to_income_ratio": 0.3,
                "address_location_tag": "SafeZoneC",
                "document_text": "Name: Alice Example\nDOB: 01/01/1990\nOther info..."
            }
        }


class UnderwritingResponse(BaseResponse):
    """Response model for underwriting requests."""
    task_id: str = Field(..., description="Unique identifier for the task")
    application_id: str = Field(..., description="Unique identifier for the application")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Underwriting task created successfully",
                "task_id": "12345678-1234-5678-1234-567812345678",
                "application_id": "UW-TEST-010"
            }
        }


# Claims models
class ClaimsRequest(BaseRequest):
    """Request model for claims processing."""
    claim_id: str = Field(..., description="Unique identifier for the claim")
    policy_id: str = Field(..., description="Policy identifier")
    claimant_name: str = Field(..., description="Name of the claimant")
    incident_date: str = Field(..., description="Date of the incident")
    claim_amount: float = Field(..., description="Amount claimed")
    incident_description: str = Field(..., description="Description of the incident")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional data for the claim")

    class Config:
        schema_extra = {
            "example": {
                "institution_id": "institution_a",
                "claim_id": "CL-TEST-001",
                "policy_id": "POL-123456",
                "claimant_name": "Alice Example",
                "incident_date": "2023-05-15",
                "claim_amount": 5000,
                "incident_description": "Water damage from burst pipe"
            }
        }


class ClaimsResponse(BaseResponse):
    """Response model for claims requests."""
    task_id: str = Field(..., description="Unique identifier for the task")
    claim_id: str = Field(..., description="Unique identifier for the claim")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Claims task created successfully",
                "task_id": "12345678-1234-5678-1234-567812345678",
                "claim_id": "CL-TEST-001"
            }
        }


# Actuarial models
class ActuarialRequest(BaseRequest):
    """Request model for actuarial analysis."""
    analysis_id: str = Field(..., description="Unique identifier for the analysis")
    data_source: Dict[str, Any] = Field(..., description="Data source information")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Analysis parameters")

    class Config:
        schema_extra = {
            "example": {
                "institution_id": "institution_a",
                "analysis_id": "ACT-TEST-001",
                "data_source": {
                    "type": "demographic",
                    "age_group": "30-40",
                    "region": "Northeast",
                    "coverage_type": "comprehensive"
                },
                "parameters": {
                    "confidence_level": 0.95,
                    "time_horizon": "1y"
                }
            }
        }


class ActuarialResponse(BaseResponse):
    """Response model for actuarial requests."""
    task_id: str = Field(..., description="Unique identifier for the task")
    analysis_id: str = Field(..., description="Unique identifier for the analysis")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Actuarial task created successfully",
                "task_id": "12345678-1234-5678-1234-567812345678",
                "analysis_id": "ACT-TEST-001"
            }
        }


# Task status models
class TaskStatusResponse(BaseResponse):
    """Response model for task status requests."""
    task_id: str = Field(..., description="Unique identifier for the task")
    task_type: TaskType = Field(..., description="Type of task")
    task_status: TaskStatus = Field(..., description="Current status of the task")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if available")
    error: Optional[str] = Field(None, description="Error message if task failed")
    report_id: Optional[str] = Field(None, description="Report ID if a report was generated")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Task status retrieved successfully",
                "task_id": "12345678-1234-5678-1234-567812345678",
                "task_type": "underwriting",
                "task_status": "SUCCESS",
                "created_at": "2023-06-01T10:00:00",
                "updated_at": "2023-06-01T10:01:30",
                "result": {
                    "decision": "approved",
                    "risk_score": 25.5,
                    "decision_factors": {
                        "credit_score": -10.0,
                        "income": -5.0,
                        "debt_to_income_ratio": 2.5
                    }
                },
                "report_id": "RPT-12345"
            }
        }


# Report models
class ReportResponse(BaseResponse):
    """Response model for report requests."""
    report_id: str = Field(..., description="Unique identifier for the report")
    report_type: ReportType = Field(..., description="Type of report")
    created_at: datetime = Field(..., description="Report creation timestamp")
    content: Dict[str, Any] = Field(..., description="Report content")
    task_id: Optional[str] = Field(None, description="Task ID that generated the report")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Report retrieved successfully",
                "report_id": "RPT-12345",
                "report_type": "underwriting",
                "created_at": "2023-06-01T10:01:30",
                "content": {
                    "title": "Underwriting Decision Report",
                    "applicant_id": "UW-TEST-010",
                    "decision": "approved",
                    "risk_score": 25.5,
                    "decision_factors": {
                        "credit_score": -10.0,
                        "income": -5.0,
                        "debt_to_income_ratio": 2.5
                    },
                    "notes": "Applicant has excellent credit history and stable income."
                },
                "task_id": "12345678-1234-5678-1234-567812345678"
            }
        }


# Event models
class EventPayload(BaseModel):
    """Base model for event payloads."""
    event_id: str = Field(..., description="Unique identifier for the event")
    timestamp: datetime = Field(..., description="Event timestamp")
    source: str = Field(..., description="Event source")
    institution_id: str = Field(..., description="Institution identifier")
    data: Dict[str, Any] = Field(..., description="Event data")


class UnderwritingCompletedEvent(EventPayload):
    """Event payload for underwriting.completed events."""
    application_id: str = Field(..., description="Application identifier")
    decision: str = Field(..., description="Underwriting decision")
    risk_score: float = Field(..., description="Risk score")


class ClaimsFlaggedEvent(EventPayload):
    """Event payload for claims.flagged events."""
    claim_id: str = Field(..., description="Claim identifier")
    flag_reason: str = Field(..., description="Reason for flagging")
    severity: str = Field(..., description="Flag severity")


class ActuarialBenchmarkedEvent(EventPayload):
    """Event payload for actuarial.benchmarked events."""
    analysis_id: str = Field(..., description="Analysis identifier")
    benchmark_results: Dict[str, Any] = Field(..., description="Benchmark results")
