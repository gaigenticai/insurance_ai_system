"""
Dashboard Configuration

Configuration settings for the Insurance AI System Dashboard UI.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

class UserRole(str, Enum):
    ADMIN = "Admin"
    UNDERWRITER = "Underwriter"
    CLAIMS_ADJUSTER = "Claims Adjuster"
    ACTUARY = "Actuary"
    COMPLIANCE = "Compliance"
    VIEWER = "Viewer"

@dataclass
class DashboardConfig:
    """Dashboard configuration settings"""
    
    # API Configuration
    api_base_url: str = "http://localhost:8080"
    api_timeout: int = 30
    
    # UI Configuration
    theme: Theme = Theme.LIGHT
    page_title: str = "Insurance AI Control Tower"
    page_icon: str = "🏢"
    layout: str = "wide"
    
    # Feature Flags
    enable_ai_features: bool = True
    enable_real_time_updates: bool = True
    enable_notifications: bool = True
    enable_export_features: bool = True
    enable_advanced_analytics: bool = True
    
    # Security Settings
    session_timeout_minutes: int = 480  # 8 hours
    require_authentication: bool = False  # Set to True for production
    enable_audit_logging: bool = True
    
    # Performance Settings
    cache_timeout_seconds: int = 300  # 5 minutes
    max_records_per_page: int = 100
    enable_pagination: bool = True
    
    # Notification Settings
    notification_refresh_interval: int = 30  # seconds
    max_notifications_display: int = 50
    
    # Chart Settings
    default_chart_height: int = 400
    enable_chart_animations: bool = True
    chart_color_scheme: str = "plotly"

@dataclass
class RolePermissions:
    """Role-based permissions configuration"""
    
    # Page access permissions
    dashboard: bool = True
    policy_management: bool = False
    claims_processing: bool = False
    analytics: bool = False
    fraud_detection: bool = False
    knowledge_base: bool = False
    system_config: bool = False
    notifications: bool = False
    user_management: bool = False
    human_escalation: bool = False
    
    # Action permissions
    can_edit_policies: bool = False
    can_approve_claims: bool = False
    can_deny_claims: bool = False
    can_escalate_cases: bool = False
    can_export_data: bool = False
    can_configure_system: bool = False
    can_manage_users: bool = False
    can_view_audit_logs: bool = False

# Role-based permission mapping
ROLE_PERMISSIONS: Dict[UserRole, RolePermissions] = {
    UserRole.ADMIN: RolePermissions(
        dashboard=True,
        policy_management=True,
        claims_processing=True,
        analytics=True,
        fraud_detection=True,
        knowledge_base=True,
        system_config=True,
        notifications=True,
        user_management=True,
        human_escalation=True,
        can_edit_policies=True,
        can_approve_claims=True,
        can_deny_claims=True,
        can_escalate_cases=True,
        can_export_data=True,
        can_configure_system=True,
        can_manage_users=True,
        can_view_audit_logs=True
    ),
    
    UserRole.UNDERWRITER: RolePermissions(
        dashboard=True,
        policy_management=True,
        claims_processing=False,
        analytics=True,
        fraud_detection=False,
        knowledge_base=True,
        system_config=False,
        notifications=True,
        user_management=False,
        human_escalation=True,
        can_edit_policies=True,
        can_approve_claims=False,
        can_deny_claims=False,
        can_escalate_cases=True,
        can_export_data=True,
        can_configure_system=False,
        can_manage_users=False,
        can_view_audit_logs=False
    ),
    
    UserRole.CLAIMS_ADJUSTER: RolePermissions(
        dashboard=True,
        policy_management=False,
        claims_processing=True,
        analytics=True,
        fraud_detection=True,
        knowledge_base=True,
        system_config=False,
        notifications=True,
        user_management=False,
        human_escalation=True,
        can_edit_policies=False,
        can_approve_claims=True,
        can_deny_claims=True,
        can_escalate_cases=True,
        can_export_data=True,
        can_configure_system=False,
        can_manage_users=False,
        can_view_audit_logs=False
    ),
    
    UserRole.ACTUARY: RolePermissions(
        dashboard=True,
        policy_management=False,
        claims_processing=False,
        analytics=True,
        fraud_detection=False,
        knowledge_base=True,
        system_config=False,
        notifications=True,
        user_management=False,
        human_escalation=False,
        can_edit_policies=False,
        can_approve_claims=False,
        can_deny_claims=False,
        can_escalate_cases=False,
        can_export_data=True,
        can_configure_system=False,
        can_manage_users=False,
        can_view_audit_logs=False
    ),
    
    UserRole.COMPLIANCE: RolePermissions(
        dashboard=True,
        policy_management=True,
        claims_processing=True,
        analytics=True,
        fraud_detection=True,
        knowledge_base=True,
        system_config=False,
        notifications=True,
        user_management=False,
        human_escalation=True,
        can_edit_policies=False,
        can_approve_claims=False,
        can_deny_claims=False,
        can_escalate_cases=True,
        can_export_data=True,
        can_configure_system=False,
        can_manage_users=False,
        can_view_audit_logs=True
    ),
    
    UserRole.VIEWER: RolePermissions(
        dashboard=True,
        policy_management=False,
        claims_processing=False,
        analytics=True,
        fraud_detection=False,
        knowledge_base=False,
        system_config=False,
        notifications=False,
        user_management=False,
        human_escalation=False,
        can_edit_policies=False,
        can_approve_claims=False,
        can_deny_claims=False,
        can_escalate_cases=False,
        can_export_data=False,
        can_configure_system=False,
        can_manage_users=False,
        can_view_audit_logs=False
    )
}

# Navigation menu configuration
NAVIGATION_MENU = [
    {
        "name": "🏠 Dashboard",
        "key": "Dashboard",
        "icon": "🏠",
        "description": "Control tower overview"
    },
    {
        "name": "📋 Policy Management",
        "key": "Policy Management",
        "icon": "📋",
        "description": "Policy and underwriting management"
    },
    {
        "name": "⚖️ Claims Processing",
        "key": "Claims Processing", 
        "icon": "⚖️",
        "description": "Claims processing center"
    },
    {
        "name": "📊 Analytics & Risk",
        "key": "Analytics",
        "icon": "📊",
        "description": "Actuarial and risk analytics"
    },
    {
        "name": "🕵️ Fraud Detection",
        "key": "Fraud Detection",
        "icon": "🕵️",
        "description": "Fraud and ethics monitoring"
    },
    {
        "name": "📚 Knowledge Base",
        "key": "Knowledge Base",
        "icon": "📚",
        "description": "Knowledge base and model feedback"
    },
    {
        "name": "⚙️ System Config",
        "key": "System Config",
        "icon": "⚙️",
        "description": "System configuration"
    },
    {
        "name": "📩 Notifications",
        "key": "Notifications",
        "icon": "📩",
        "description": "Notifications and logging"
    },
    {
        "name": "👤 User Management",
        "key": "User Management",
        "icon": "👤",
        "description": "User management and access control"
    },
    {
        "name": "📞 Human Escalation",
        "key": "Human Escalation",
        "icon": "📞",
        "description": "Human escalation and AI co-pilot"
    }
]

# Chart color schemes
CHART_COLORS = {
    "primary": "#2a5298",
    "secondary": "#1e3c72",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# Status color mapping
STATUS_COLORS = {
    "Active": "#28a745",
    "Pending": "#ffc107",
    "Expired": "#6c757d",
    "Cancelled": "#dc3545",
    "Open": "#17a2b8",
    "Under Review": "#ffc107",
    "Approved": "#28a745",
    "Denied": "#dc3545",
    "Closed": "#6c757d",
    "High": "#dc3545",
    "Medium": "#ffc107",
    "Low": "#28a745",
    "Critical": "#dc3545"
}

# Default dashboard metrics
DEFAULT_METRICS = {
    "total_policies": 1247,
    "claims_processed": 89,
    "flagged_risks": 15,
    "pending_reviews": 7,
    "ai_accuracy": 0.942
}

def get_dashboard_config() -> DashboardConfig:
    """Get dashboard configuration from environment variables or defaults"""
    return DashboardConfig(
        api_base_url=os.getenv("DASHBOARD_API_URL", "http://localhost:8080"),
        api_timeout=int(os.getenv("DASHBOARD_API_TIMEOUT", "30")),
        theme=Theme(os.getenv("DASHBOARD_THEME", "light")),
        enable_ai_features=os.getenv("DASHBOARD_ENABLE_AI", "true").lower() == "true",
        enable_real_time_updates=os.getenv("DASHBOARD_REAL_TIME", "true").lower() == "true",
        require_authentication=os.getenv("DASHBOARD_AUTH_REQUIRED", "false").lower() == "true",
        session_timeout_minutes=int(os.getenv("DASHBOARD_SESSION_TIMEOUT", "480")),
        cache_timeout_seconds=int(os.getenv("DASHBOARD_CACHE_TIMEOUT", "300"))
    )

def get_user_permissions(role: UserRole) -> RolePermissions:
    """Get permissions for a user role"""
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS[UserRole.VIEWER])

def can_access_page(role: UserRole, page_key: str) -> bool:
    """Check if a user role can access a specific page"""
    permissions = get_user_permissions(role)
    
    page_permission_map = {
        "Dashboard": permissions.dashboard,
        "Policy Management": permissions.policy_management,
        "Claims Processing": permissions.claims_processing,
        "Analytics": permissions.analytics,
        "Fraud Detection": permissions.fraud_detection,
        "Knowledge Base": permissions.knowledge_base,
        "System Config": permissions.system_config,
        "Notifications": permissions.notifications,
        "User Management": permissions.user_management,
        "Human Escalation": permissions.human_escalation
    }
    
    return page_permission_map.get(page_key, False)

def get_available_pages(role: UserRole) -> List[Dict[str, Any]]:
    """Get list of pages available to a user role"""
    available_pages = []
    
    for page in NAVIGATION_MENU:
        if can_access_page(role, page["key"]):
            available_pages.append(page)
    
    return available_pages