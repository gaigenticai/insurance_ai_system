from enum import Enum
from typing import Set

class UserRole(str, Enum):
    ADMIN = "admin"
    UNDERWRITER = "underwriter"
    CLAIMS_ADJUSTER = "claims_adjuster"
    ACTUARY = "actuary"
    CUSTOMER = "customer"
    REVIEWER = "reviewer"
    COMPLIANCE = "compliance"

class Permission(str, Enum):
    # General
    VIEW_DASHBOARD = "view:dashboard"
    VIEW_AUDIT_LOGS = "view:audit_logs"

    # Underwriting
    CREATE_UNDERWRITING_APPLICATION = "create:underwriting_application"
    VIEW_UNDERWRITING_APPLICATION = "view:underwriting_application"
    EDIT_UNDERWRITING_APPLICATION = "edit:underwriting_application"
    APPROVE_UNDERWRITING_APPLICATION = "approve:underwriting_application"

    # Claims
    CREATE_CLAIM = "create:claim"
    VIEW_CLAIM = "view:claim"
    EDIT_CLAIM = "edit:claim"
    APPROVE_CLAIM = "approve:claim"

    # Actuarial
    RUN_ACTUARIAL_ANALYSIS = "run:actuarial_analysis"
    VIEW_ACTUARIAL_REPORT = "view:actuarial_report"

    # Document Management
    UPLOAD_DOCUMENT = "upload:document"
    VIEW_DOCUMENT = "view:document"
    DELETE_DOCUMENT = "delete:document"

    # User Management
    MANAGE_USERS = "manage:users"
    MANAGE_ROLES = "manage:roles"

    # System Configuration
    MANAGE_SETTINGS = "manage:settings"
    VIEW_METRICS = "view:metrics"


ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_AUDIT_LOGS,
        Permission.CREATE_UNDERWRITING_APPLICATION,
        Permission.VIEW_UNDERWRITING_APPLICATION,
        Permission.EDIT_UNDERWRITING_APPLICATION,
        Permission.APPROVE_UNDERWRITING_APPLICATION,
        Permission.CREATE_CLAIM,
        Permission.VIEW_CLAIM,
        Permission.EDIT_CLAIM,
        Permission.APPROVE_CLAIM,
        Permission.RUN_ACTUARIAL_ANALYSIS,
        Permission.VIEW_ACTUARIAL_REPORT,
        Permission.UPLOAD_DOCUMENT,
        Permission.VIEW_DOCUMENT,
        Permission.DELETE_DOCUMENT,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_METRICS,
    },
    UserRole.UNDERWRITER: {
        Permission.VIEW_DASHBOARD,
        Permission.CREATE_UNDERWRITING_APPLICATION,
        Permission.VIEW_UNDERWRITING_APPLICATION,
        Permission.EDIT_UNDERWRITING_APPLICATION,
        Permission.APPROVE_UNDERWRITING_APPLICATION,
        Permission.UPLOAD_DOCUMENT,
        Permission.VIEW_DOCUMENT,
    },
    UserRole.CLAIMS_ADJUSTER: {
        Permission.VIEW_DASHBOARD,
        Permission.CREATE_CLAIM,
        Permission.VIEW_CLAIM,
        Permission.EDIT_CLAIM,
        Permission.APPROVE_CLAIM,
        Permission.UPLOAD_DOCUMENT,
        Permission.VIEW_DOCUMENT,
    },
    UserRole.ACTUARY: {
        Permission.VIEW_DASHBOARD,
        Permission.RUN_ACTUARIAL_ANALYSIS,
        Permission.VIEW_ACTUARIAL_REPORT,
        Permission.VIEW_DOCUMENT,
    },
    UserRole.CUSTOMER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_UNDERWRITING_APPLICATION,
        Permission.VIEW_CLAIM,
        Permission.UPLOAD_DOCUMENT,
        Permission.VIEW_DOCUMENT,
    },
    UserRole.REVIEWER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_UNDERWRITING_APPLICATION,
        Permission.VIEW_CLAIM,
        Permission.VIEW_ACTUARIAL_REPORT,
        Permission.VIEW_DOCUMENT,
    },
    UserRole.COMPLIANCE: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_UNDERWRITING_APPLICATION,
        Permission.VIEW_CLAIM,
        Permission.VIEW_ACTUARIAL_REPORT,
        Permission.VIEW_DOCUMENT,
    },
}

def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a given role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


