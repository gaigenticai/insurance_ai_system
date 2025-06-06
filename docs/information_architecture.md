```markdown
# Information Architecture: Configurable Insurance Platform

This document outlines the Information Architecture (IA) for the configurable insurance platform, designed to support the needs of various user personas including operational staff (Claims Processors, Underwriters, Actuaries) and administrators.

## I. Operational Sections

This section details the primary navigation and sub-sections for users performing day-to-day operational tasks. A global search functionality will be available across all sections.

1.  **Dashboard**
    *   Overview (Default View)
        *   Key Performance Indicators (KPIs)
        *   Recent Activity Feed
        *   Pending Tasks/Alerts
    *   My Tasks
    *   Team Performance (for managers)
    *   System Health Overview

2.  **Claims**
    *   **Claims Queue/List:**
        *   All Claims
        *   My Assigned Claims
        *   Unassigned Claims
        *   Claims Awaiting Information
        *   Flagged/Suspicious Claims
        *   Recently Closed Claims
    *   **Create New Claim (FNOL):**
        *   Select Policy/Claimant
        *   Enter Claim Details (dynamically based on Claim Type)
        *   Upload Documents
    *   **Claim Details View:** (Accessed by selecting a claim from the queue)
        *   Summary Tab
        *   Policy Information Tab
        *   Claimant Details Tab
        *   Incident Details Tab (with custom fields)
        *   Document Management Tab
        *   AI Insights Tab (Fraud Score, Damage Assessment, etc.)
        *   Rules & Decision Log Tab
        *   Notes & Communication Log Tab
        *   Audit Trail Tab
    *   **Search Claims**

3.  **Underwriting**
    *   **Applications Queue/List:**
        *   All Applications
        *   My Assigned Applications
        *   New Applications
        *   Applications Pending Information
        *   Flagged/High-Risk Applications
        *   Recently Decisioned Applications
    *   **Create New Application:**
        *   Select Product
        *   Enter Applicant & Risk Details (dynamically based on Product)
        *   Upload Documents
    *   **Application Details View:** (Accessed by selecting an application)
        *   Summary Tab
        *   Applicant Information Tab (with custom fields)
        *   Product Details Tab
        *   Document Management Tab
        *   AI Risk Assessment Tab
        *   Rules & Decision Log Tab
        *   Notes & Communication Log Tab
        *   Audit Trail Tab
    *   **Search Applications**

4.  **Policies**
    *   **Policy List:**
        *   Search/Filter Policies (by policy number, customer, status, product type, custom fields)
    *   **Policy Details View:**
        *   Summary & Coverage Information
        *   Insured Parties & Objects
        *   Endorsements & History
        *   Billing & Payment Information
        *   Associated Claims
        *   Custom Fields Data
    *   **Create New Policy (typically from an approved application)**

5.  **Reports**
    *   **My Reports:** Saved or frequently run reports.
    *   **Standard Reports:** Pre-defined operational and actuarial reports.
    *   **Run Report:** Interface to select a report definition, input runtime parameters, and generate.
    *   **Report History:** List of previously generated reports with options to view/download.

6.  **Search (Global)**
    *   Universal search bar accessible from the main navigation.
    *   Search across Policies, Claims, Customers, Documents, etc.
    *   Advanced filtering options.

## II. Administration Sections

This section details the navigation for administrators (like Maria) responsible for configuring and maintaining the platform. This will likely be a distinct area within the application, possibly labeled "Admin Console" or "System Settings."

1.  **System Configuration Hub (Main Admin Dashboard)**
    *   Overview of system health, recent configuration changes, user activity.
    *   Quick links to key configuration areas.

2.  **Data Management**
    *   **Custom Field Manager:**
        *   View/Create/Edit Custom Field Definitions
        *   Define Validation Rules
        *   Manage Enum Values
    *   **Data Import/Export Utilities:** (For bulk data operations)

3.  **Product & Claim Type Management**
    *   **Product Definitions:**
        *   View/Create/Edit Insurance Products
        *   Associate Custom Fields to Products
        *   Link Underwriting Workflows & Rule Sets
        *   Configure Product Base Parameters (`base_config`)
    *   **Claim Type Definitions:**
        *   View/Create/Edit Claim Type Configurations (linked to Products)
        *   Associate Custom Fields to Claim Types
        *   Link Claims Workflows & Rule Sets
        *   Configure Claim Type Base Parameters (`base_config`)

4.  **Process Automation**
    *   **Workflow Editor:**
        *   View/Create/Edit Workflow Definitions (for Underwriting, Claims, etc.)
        *   Define States, Actions (Agent Calls, Rule Executions, AI Calls), Transitions, Conditions.
        *   Workflow Versioning.
    *   **Rules Engine Configuration:**
        *   View/Create/Edit Rule Sets
        *   Rule Editor (for defining conditions and actions)
        *   Rule Set Versioning.

5.  **Reporting & Analytics Configuration**
    *   **Report Builder/Definition Manager:**
        *   View/Create/Edit Report Definitions
        *   Define Data Sources (including custom fields)
        *   Configure Filters, Groupings, Aggregations
        *   Define Calculated Metrics
        *   Manage Presentation (Charts, Tables)
        *   Configure AI Tasks for Reports
    *   **Analytics Dashboards Configuration:** (If customizable dashboards are supported beyond standard reports)

6.  **AI & Integrations**
    *   **AI Model Management:**
        *   Configure AI Provider Settings (API Keys, Default Models)
        *   Manage Prompt Templates (link to specific workflows/tasks)
        *   (Future) Register and configure custom/tenant-specific AI models.
    *   **Third-Party Integrations:**
        *   Manage connections and configurations for external services (e.g., payment gateways, communication APIs, data providers).

7.  **User & Access Management**
    *   **User Administration:**
        *   View/Create/Edit User Accounts
        *   Assign Roles
        *   Manage User Status (Active/Inactive)
    *   **Role & Permission Management:**
        *   Define Roles
        *   Assign Permissions to Roles (for accessing specific features and data, including admin functions).
    *   **Audit Logs:** View system-wide audit trails for configuration changes and critical user actions.

8.  **System Settings & Monitoring**
    *   **General Settings:** Application-wide settings (e.g., branding elements, default notification settings).
    *   **System Health Monitoring:** Detailed logs and performance metrics.
    *   **Background Job Management:** Monitor and manage scheduled tasks (e.g., report generation, data synchronization).

This IA aims to provide a logical structure for both operational users and administrators, ensuring that functionalities are discoverable and aligned with their tasks and goals. The separation of Operational and Administration sections helps maintain clarity and security.
```
