"""
Enhanced Insurance AI System API

Extended API with comprehensive endpoints for the dashboard UI including:
- Dashboard metrics and analytics
- Policy and claims management
- User management and access control
- System configuration
- Notifications and logging
- Human escalation features
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import uuid
import logging
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import existing modules
from main import InsuranceAIApplication
from config.settings import get_settings
from ai_services.ai_service_manager import AIServiceManager
from ai_services.ai_analytics import AIMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Insurance AI System - Enhanced API",
    description="Comprehensive API for Insurance AI System with full dashboard support",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
ai_service_manager = None
ai_monitor = None
insurance_app = None

# Pydantic Models
class PolicyStatus(str, Enum):
    ACTIVE = "Active"
    PENDING = "Pending"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"

class ClaimStatus(str, Enum):
    OPEN = "Open"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    DENIED = "Denied"
    CLOSED = "Closed"

class UserRole(str, Enum):
    ADMIN = "Admin"
    UNDERWRITER = "Underwriter"
    CLAIMS_ADJUSTER = "Claims Adjuster"
    ACTUARY = "Actuary"
    COMPLIANCE = "Compliance"

class AlertSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class PolicyData(BaseModel):
    id: str
    customer_name: str
    policy_type: str
    status: PolicyStatus
    premium: float
    risk_score: float
    created_date: datetime
    ai_decision: str
    confidence: float

class ClaimData(BaseModel):
    id: str
    policy_id: str
    customer_name: str
    claim_type: str
    amount: float
    status: ClaimStatus
    created_date: datetime
    ai_decision: str
    fraud_score: float
    confidence: float

class UserData(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    status: str
    last_login: Optional[datetime]
    created_date: datetime

class AlertData(BaseModel):
    id: str
    type: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool

class DashboardMetrics(BaseModel):
    total_policies: int
    claims_processed: int
    flagged_risks: int
    pending_reviews: int
    ai_accuracy: float

class AgentActivity(BaseModel):
    agent_name: str
    status: str
    current_task: str
    last_activity: datetime
    tasks_completed: int
    success_rate: float

class SystemHealth(BaseModel):
    api_response_time: float
    database_connections: int
    ai_model_latency: float
    error_rate: float
    memory_usage: float

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global ai_service_manager, ai_monitor, insurance_app
    
    try:
        # Initialize AI services
        settings = get_settings()
        ai_service_manager = AIServiceManager()
        ai_monitor = AIMonitor()
        
        # Initialize insurance application
        insurance_app = InsuranceAIApplication()
        
        logger.info("Enhanced API services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")

# Health check
@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_service_manager": ai_service_manager is not None,
            "ai_monitor": ai_monitor is not None,
            "insurance_app": insurance_app is not None
        }
    }

# Dashboard Endpoints
@app.get("/api/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    """Get main dashboard metrics"""
    # Mock data - replace with actual database queries
    return DashboardMetrics(
        total_policies=1247,
        claims_processed=89,
        flagged_risks=15,
        pending_reviews=7,
        ai_accuracy=0.942
    )

@app.get("/api/dashboard/agent-activity")
async def get_agent_activity():
    """Get AI agent activity data"""
    agents = [
        AgentActivity(
            agent_name="Underwriting Agent",
            status="Active",
            current_task="Analyzing Policy POL-1023",
            last_activity=datetime.now(),
            tasks_completed=45,
            success_rate=0.92
        ),
        AgentActivity(
            agent_name="Claims Agent", 
            status="Active",
            current_task="Processing Claim CLM-2015",
            last_activity=datetime.now(),
            tasks_completed=32,
            success_rate=0.88
        ),
        AgentActivity(
            agent_name="Fraud Detection Agent",
            status="Idle",
            current_task="Monitoring for anomalies",
            last_activity=datetime.now() - timedelta(minutes=5),
            tasks_completed=18,
            success_rate=0.95
        )
    ]
    return {"agents": agents}

@app.get("/api/dashboard/alerts")
async def get_active_alerts():
    """Get active system alerts"""
    alerts = [
        AlertData(
            id="ALT-001",
            type="SLA Violation",
            severity=AlertSeverity.HIGH,
            message="Claim CLM-2008 exceeds 48-hour SLA",
            timestamp=datetime.now() - timedelta(hours=2),
            resolved=False
        ),
        AlertData(
            id="ALT-002",
            type="Fraud Detection",
            severity=AlertSeverity.CRITICAL,
            message="Suspicious pattern detected in claims cluster",
            timestamp=datetime.now() - timedelta(minutes=30),
            resolved=False
        )
    ]
    return {"alerts": alerts}

@app.get("/api/dashboard/system-health", response_model=SystemHealth)
async def get_system_health():
    """Get system health metrics"""
    return SystemHealth(
        api_response_time=245.0,
        database_connections=12,
        ai_model_latency=1.2,
        error_rate=0.3,
        memory_usage=68.0
    )

# Policy Management Endpoints
@app.get("/api/policies")
async def get_policies(
    policy_type: Optional[str] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get policies with filtering and pagination"""
    # Mock data - replace with actual database queries
    policies = []
    for i in range(limit):
        policy = PolicyData(
            id=f"POL-{1000+i+offset}",
            customer_name=f"Customer {i+1+offset}",
            policy_type="Auto",
            status=PolicyStatus.ACTIVE,
            premium=2500.0,
            risk_score=0.45,
            created_date=datetime.now() - timedelta(days=i),
            ai_decision="Approved",
            confidence=0.89
        )
        policies.append(policy)
    
    return {
        "policies": policies,
        "total": 1247,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/policies/{policy_id}")
async def get_policy_details(policy_id: str):
    """Get detailed policy information"""
    # Mock policy details
    return {
        "policy": {
            "id": policy_id,
            "customer_name": "John Doe",
            "policy_type": "Auto",
            "status": "Active",
            "premium": 2500.0,
            "risk_score": 0.45,
            "ai_decision": "Approved",
            "confidence": 0.89,
            "details": {
                "coverage_amount": 500000,
                "deductible": 1000,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        },
        "ai_analysis": {
            "risk_factors": [
                "Age: 35 (Standard risk)",
                "Credit Score: 750 (Good)",
                "Claims History: None (Positive)",
                "Location: Suburban (Low risk)"
            ],
            "decision_reasoning": "Applicant meets all standard criteria with good credit score and no claims history.",
            "confidence_factors": [
                "Complete application data",
                "Verified identity",
                "Standard risk profile"
            ]
        }
    }

@app.post("/api/policies/{policy_id}/reanalyze")
async def reanalyze_policy(policy_id: str):
    """Trigger AI re-analysis of a policy"""
    if ai_service_manager:
        try:
            # Mock re-analysis
            result = {
                "policy_id": policy_id,
                "status": "reanalysis_started",
                "estimated_completion": datetime.now() + timedelta(minutes=5)
            }
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=503, detail="AI service not available")

# Claims Management Endpoints
@app.get("/api/claims")
async def get_claims(
    status: Optional[str] = None,
    claim_type: Optional[str] = None,
    fraud_risk: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get claims with filtering and pagination"""
    # Mock data
    claims = []
    for i in range(limit):
        claim = ClaimData(
            id=f"CLM-{2000+i+offset}",
            policy_id=f"POL-{1000+i}",
            customer_name=f"Customer {i+1+offset}",
            claim_type="Auto Accident",
            amount=5000.0,
            status=ClaimStatus.OPEN,
            created_date=datetime.now() - timedelta(days=i),
            ai_decision="Approve",
            fraud_score=0.15,
            confidence=0.87
        )
        claims.append(claim)
    
    return {
        "claims": claims,
        "total": 89,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/claims/{claim_id}")
async def get_claim_details(claim_id: str):
    """Get detailed claim information"""
    return {
        "claim": {
            "id": claim_id,
            "policy_id": "POL-1023",
            "customer_name": "Jane Smith",
            "claim_type": "Auto Accident",
            "amount": 5000.0,
            "status": "Under Review",
            "ai_decision": "Approve",
            "fraud_score": 0.15,
            "confidence": 0.87,
            "details": {
                "incident_date": "2024-01-10",
                "location": "Main St & Oak Ave",
                "description": "Rear-end collision at traffic light",
                "police_report": True,
                "witnesses": 2
            }
        },
        "ai_analysis": {
            "fraud_indicators": [
                "Location verified through police report",
                "Damage consistent with description",
                "No suspicious patterns detected"
            ],
            "decision_reasoning": "All evidence supports legitimate claim. Damage assessment matches reported incident.",
            "recommended_action": "Approve claim for full amount"
        },
        "audit_trail": [
            {
                "timestamp": "2024-01-15 09:30",
                "action": "Claim submitted",
                "user": "Customer Portal"
            },
            {
                "timestamp": "2024-01-15 09:31", 
                "action": "AI triage completed",
                "user": "Claims Agent"
            },
            {
                "timestamp": "2024-01-15 09:35",
                "action": "Documents validated",
                "user": "Document Agent"
            }
        ]
    }

@app.post("/api/claims/{claim_id}/decision")
async def make_claim_decision(
    claim_id: str,
    decision: str = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True)
):
    """Make a decision on a claim"""
    valid_decisions = ["approve", "deny", "investigate", "escalate"]
    if decision.lower() not in valid_decisions:
        raise HTTPException(status_code=400, detail="Invalid decision")
    
    return {
        "claim_id": claim_id,
        "decision": decision,
        "reason": reason,
        "timestamp": datetime.now(),
        "status": "decision_recorded"
    }

# Analytics Endpoints
@app.get("/api/analytics/trends")
async def get_analytics_trends(
    metric: str = Query("loss_ratio"),
    period: str = Query("30d")
):
    """Get analytics trends data"""
    # Mock trend data
    if metric == "loss_ratio":
        data = [
            {"date": "2024-01-01", "value": 0.68},
            {"date": "2024-01-08", "value": 0.65},
            {"date": "2024-01-15", "value": 0.62}
        ]
    elif metric == "claims_volume":
        data = [
            {"date": "2024-01-01", "value": 45},
            {"date": "2024-01-08", "value": 52},
            {"date": "2024-01-15", "value": 48}
        ]
    else:
        data = []
    
    return {
        "metric": metric,
        "period": period,
        "data": data
    }

@app.get("/api/analytics/insights")
async def get_ai_insights():
    """Get AI-generated insights"""
    insights = [
        {
            "title": "Fraud Ring Detection",
            "description": "AI identified a potential fraud ring involving 12 claims with similar damage patterns.",
            "confidence": 0.89,
            "impact": "High",
            "action": "Investigation initiated"
        },
        {
            "title": "Risk Cluster Analysis",
            "description": "Geographic cluster of high-risk policies identified in downtown area.",
            "confidence": 0.76,
            "impact": "Medium", 
            "action": "Premium adjustment recommended"
        }
    ]
    return {"insights": insights}

@app.post("/api/analytics/simulation")
async def run_simulation(
    premium_change: float = Body(...),
    deductible_change: float = Body(...),
    coverage_change: float = Body(...)
):
    """Run what-if simulation"""
    # Mock simulation results
    base_revenue = 15600000
    base_claims = 10140000
    base_profit = 5460000
    
    new_revenue = base_revenue * (1 + premium_change/100)
    new_claims = base_claims * (1 - premium_change/200)  # Inverse relationship
    new_profit = new_revenue - new_claims
    
    return {
        "simulation_id": str(uuid.uuid4()),
        "parameters": {
            "premium_change": premium_change,
            "deductible_change": deductible_change,
            "coverage_change": coverage_change
        },
        "results": {
            "projected_revenue": new_revenue,
            "projected_claims": new_claims,
            "projected_profit": new_profit,
            "profit_change_pct": ((new_profit - base_profit) / base_profit) * 100
        }
    }

# Fraud Detection Endpoints
@app.get("/api/fraud/flagged-claims")
async def get_flagged_claims():
    """Get claims flagged for fraud"""
    flagged_claims = [
        {
            "claim_id": "CLM-2045",
            "risk_score": 0.89,
            "reason": "Unusual damage pattern, multiple similar claims from same area",
            "status": "Under Investigation",
            "flagged_date": "2024-01-15"
        },
        {
            "claim_id": "CLM-2051",
            "risk_score": 0.76,
            "reason": "Repair shop not in network, high estimate",
            "status": "Pending Review",
            "flagged_date": "2024-01-14"
        }
    ]
    return {"flagged_claims": flagged_claims}

@app.get("/api/fraud/patterns")
async def get_fraud_patterns():
    """Get detected fraud patterns"""
    patterns = [
        {
            "pattern_id": "PAT-001",
            "type": "Geographic Cluster",
            "description": "Multiple claims from same intersection",
            "claims_involved": 8,
            "confidence": 0.82
        },
        {
            "pattern_id": "PAT-002", 
            "type": "Repair Shop Network",
            "description": "Claims directed to specific repair shops",
            "claims_involved": 12,
            "confidence": 0.91
        }
    ]
    return {"patterns": patterns}

# User Management Endpoints
@app.get("/api/users")
async def get_users(
    role: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get users with filtering"""
    users = [
        UserData(
            id="USR-001",
            name="John Smith",
            email="john.smith@company.com",
            role=UserRole.ADMIN,
            status="Active",
            last_login=datetime.now() - timedelta(hours=2),
            created_date=datetime.now() - timedelta(days=180)
        ),
        UserData(
            id="USR-002",
            name="Sarah Johnson",
            email="sarah.johnson@company.com", 
            role=UserRole.UNDERWRITER,
            status="Active",
            last_login=datetime.now() - timedelta(minutes=30),
            created_date=datetime.now() - timedelta(days=120)
        )
    ]
    return {"users": users, "total": len(users)}

@app.post("/api/users")
async def create_user(user_data: dict = Body(...)):
    """Create a new user"""
    new_user = UserData(
        id=f"USR-{uuid.uuid4().hex[:6].upper()}",
        name=user_data["name"],
        email=user_data["email"],
        role=UserRole(user_data["role"]),
        status="Active",
        last_login=None,
        created_date=datetime.now()
    )
    return {"user": new_user, "status": "created"}

@app.get("/api/users/{user_id}/sessions")
async def get_user_sessions(user_id: str):
    """Get user session history"""
    sessions = [
        {
            "session_id": "SES-001",
            "start_time": datetime.now() - timedelta(hours=2),
            "end_time": datetime.now() - timedelta(hours=1),
            "ip_address": "192.168.1.100",
            "user_agent": "Chrome 120.0.0.0",
            "actions": 45
        }
    ]
    return {"sessions": sessions}

# System Configuration Endpoints
@app.get("/api/config/institution")
async def get_institution_config():
    """Get institution configuration"""
    return {
        "institution_name": "Acme Insurance Co.",
        "license_number": "INS-12345-TX",
        "regulatory_jurisdiction": "Texas",
        "business_hours": "8:00 AM - 6:00 PM CST",
        "sla_target_hours": 24,
        "risk_thresholds": {
            "low_risk": 0.3,
            "high_risk": 0.7
        },
        "auto_approval_threshold": 0.85
    }

@app.put("/api/config/institution")
async def update_institution_config(config: dict = Body(...)):
    """Update institution configuration"""
    return {"status": "updated", "config": config}

@app.get("/api/config/agents")
async def get_agent_config():
    """Get AI agent configuration"""
    agents = [
        {
            "agent_name": "Underwriting Agent",
            "status": "Active",
            "permissions": ["read_policies", "write_policies"],
            "rate_limit": 100,
            "model": "gpt-3.5-turbo"
        },
        {
            "agent_name": "Claims Agent",
            "status": "Active", 
            "permissions": ["read_claims", "write_claims"],
            "rate_limit": 150,
            "model": "gpt-3.5-turbo"
        }
    ]
    return {"agents": agents}

@app.put("/api/config/agents/{agent_name}")
async def update_agent_config(agent_name: str, config: dict = Body(...)):
    """Update agent configuration"""
    return {"agent_name": agent_name, "status": "updated", "config": config}

# Notifications Endpoints
@app.get("/api/notifications")
async def get_notifications(
    severity: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000)
):
    """Get system notifications"""
    notifications = [
        {
            "id": "NOT-001",
            "type": "SLA Breach",
            "severity": "High",
            "message": "Claim CLM-2045 has exceeded 48-hour processing SLA",
            "timestamp": datetime.now() - timedelta(hours=2),
            "status": "Unread"
        },
        {
            "id": "NOT-002",
            "type": "Fraud Alert",
            "severity": "Critical",
            "message": "Potential fraud ring detected - 8 related claims identified",
            "timestamp": datetime.now() - timedelta(minutes=30),
            "status": "Unread"
        }
    ]
    return {"notifications": notifications}

@app.post("/api/notifications/{notification_id}/acknowledge")
async def acknowledge_notification(notification_id: str):
    """Acknowledge a notification"""
    return {
        "notification_id": notification_id,
        "status": "acknowledged",
        "timestamp": datetime.now()
    }

@app.get("/api/logs")
async def get_system_logs(
    level: Optional[str] = None,
    component: Optional[str] = None,
    time_range: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get system logs"""
    logs = [
        {
            "timestamp": datetime.now() - timedelta(minutes=5),
            "level": "INFO",
            "component": "AI Service",
            "message": "Underwriting analysis completed for policy POL-1089",
            "user": "system",
            "request_id": "req-789123"
        },
        {
            "timestamp": datetime.now() - timedelta(minutes=10),
            "level": "WARN",
            "component": "API",
            "message": "Rate limit approaching for user admin@company.com",
            "user": "admin@company.com",
            "request_id": "req-789122"
        }
    ]
    return {"logs": logs}

# Human Escalation Endpoints
@app.get("/api/escalation/pending-cases")
async def get_pending_cases():
    """Get cases pending human assignment"""
    cases = [
        {
            "case_id": "CLM-2045",
            "type": "Claims",
            "priority": "High",
            "reason": "Fraud suspicion - requires investigation",
            "ai_confidence": 0.67,
            "estimated_time": "2-4 hours",
            "suggested_assignee": "Mike Wilson"
        },
        {
            "case_id": "POL-1089",
            "type": "Underwriting",
            "priority": "Medium",
            "reason": "Complex risk profile - manual review needed",
            "ai_confidence": 0.72,
            "estimated_time": "1-2 hours",
            "suggested_assignee": "Sarah Johnson"
        }
    ]
    return {"pending_cases": cases}

@app.post("/api/escalation/assign")
async def assign_case(
    case_id: str = Body(...),
    assignee: str = Body(...),
    priority: str = Body(...),
    notes: Optional[str] = Body(None)
):
    """Assign a case to a human reviewer"""
    return {
        "case_id": case_id,
        "assignee": assignee,
        "priority": priority,
        "notes": notes,
        "assigned_at": datetime.now(),
        "status": "assigned"
    }

@app.get("/api/escalation/team-workload")
async def get_team_workload():
    """Get team workload information"""
    workload = [
        {
            "name": "Sarah Johnson",
            "active_cases": 8,
            "capacity_pct": 75,
            "specialization": "Underwriting"
        },
        {
            "name": "Mike Wilson",
            "active_cases": 12,
            "capacity_pct": 90,
            "specialization": "Claims"
        }
    ]
    return {"team_workload": workload}

@app.post("/api/escalation/reprocess")
async def request_reprocessing(
    item_id: str = Body(...),
    reprocess_type: str = Body(...),
    reason: str = Body(...),
    priority: str = Body(...)
):
    """Request reprocessing of an item"""
    return {
        "item_id": item_id,
        "reprocess_type": reprocess_type,
        "reason": reason,
        "priority": priority,
        "queued_at": datetime.now(),
        "estimated_completion": datetime.now() + timedelta(minutes=30),
        "status": "queued"
    }

# Chat/Co-pilot Endpoints
@app.post("/api/copilot/chat")
async def chat_with_copilot(
    message: str = Body(...),
    context: Optional[dict] = Body(None)
):
    """Chat with AI co-pilot"""
    if ai_service_manager:
        try:
            # Use AI service to generate response
            response = await ai_service_manager.analyze_with_ai(
                "customer_service",
                {"query": message, "context": context or {}}
            )
            
            return {
                "response": response.get("analysis", "I'm here to help! How can I assist you?"),
                "confidence": response.get("confidence", 0.8),
                "timestamp": datetime.now()
            }
        except Exception as e:
            logger.error(f"Co-pilot chat error: {e}")
            return {
                "response": "I'm sorry, I'm having trouble processing your request right now.",
                "confidence": 0.0,
                "timestamp": datetime.now()
            }
    else:
        return {
            "response": "AI co-pilot is currently unavailable.",
            "confidence": 0.0,
            "timestamp": datetime.now()
        }

# Export endpoints
@app.get("/api/export/policies")
async def export_policies(format: str = Query("json")):
    """Export policies data"""
    # Mock export
    return {"export_id": str(uuid.uuid4()), "format": format, "status": "generating"}

@app.get("/api/export/claims")
async def export_claims(format: str = Query("json")):
    """Export claims data"""
    # Mock export
    return {"export_id": str(uuid.uuid4()), "format": format, "status": "generating"}

@app.get("/api/export/analytics")
async def export_analytics(format: str = Query("json")):
    """Export analytics data"""
    # Mock export
    return {"export_id": str(uuid.uuid4()), "format": format, "status": "generating"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)