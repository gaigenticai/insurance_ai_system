```markdown
# Low-Fidelity Wireframes: Configurable Insurance Platform

This document presents low-fidelity wireframes (textual descriptions and block layouts) for key screens of the configurable insurance platform. These are based on the User Personas, UI/UX Requirements, User Journey Maps, and Information Architecture.

---

## 1. Operational Screen: Claim File Overview (for Sarah - Claims Processor)

*   **Persona:** Sarah - Claims Processor
*   **Goal:** Quickly understand the status of a claim, access relevant information, and take necessary actions based on system guidance and configured workflows.
*   **Screen Purpose:** To provide a comprehensive, at-a-glance view of a single claim, including its current status, key details, associated policy information, documents, AI insights, and available actions.

*   **Block-Level Layout Sketch:**

    ```
    +--------------------------------------------------------------------------+
    | [Header: Claim ID | Claimant Name | Claim Type | Current Status Badge]    |
    |--------------------------------------------------------------------------|
    | Main Content Area (Left - 70%)             | Right Sidebar (30%)        |
    |--------------------------------------------|----------------------------|
    | [Tab Navigation:                            | [Contextual Actions]       |
    |  Summary | Details | Policy | Documents   |  - Approve Claim           |
    |  AI Insights | Notes | Audit Trail ]      |  - Deny Claim              |
    |                                            |  - Escalate Claim          |
    |--------------------------------------------|  - Request Information     |
    | [Tab Content Area - Dynamic based on tab]  |  - Add Note                |
    |                                            |                            |
    |  **If 'Summary' Tab Active:**              |----------------------------|
    |  - Key Claim Info (Date of Loss, Amount)   | [AI Insights Summary]      |
    |  - Policy Snapshot (Policy #, Status)      |  - Fraud Score: [Score]    |
    |  - Claimant Snapshot (Name, Contact)       |  - Recommendation: [Text]  |
    |  - Current Workflow Step / Next Steps      |  - Key Factors: [List]     |
    |  - Urgent Alerts/Flags                     |                            |
    |                                            |----------------------------|
    |  **If 'Details' Tab Active:**              | [Related Items]            |
    |  - Incident Details (Standard Fields)      |  - Link to Policy          |
    |  - Custom Fields (Dynamically Rendered     |  - Link to Customer        |
    |    based on Claim Type Configuration)      |  - Similar Claims (Opt.)   |
    |    - Group 1: [Field1], [Field2]         |                            |
    |    - Group 2: [Field3], [Field4]         |                            |
    |                                            |----------------------------|
    |  **If 'Documents' Tab Active:**            | [Document Upload/Link]     |
    |  - List of Required Documents (status)     |                            |
    |  - Uploaded Documents (viewer/downloader)  |                            |
    |                                            |                            |
    |  (Other tabs follow similar detailed views) |                            |
    |                                            |                            |
    +--------------------------------------------------------------------------+
    ```

*   **Key Elements & Dynamic Content:**
    *   **Header:** Displays essential claim identifiers and its current workflow status (e.g., "Open," "Under Review," "Pending AI Analysis").
    *   **Tab Navigation:** Allows Sarah to switch between different aspects of the claim.
    *   **Summary Tab:** Provides a quick overview. "Current Workflow Step / Next Steps" would be dynamic based on the workflow engine's state for this claim. "Urgent Alerts/Flags" would show system-generated warnings.
    *   **Details Tab:** The "Custom Fields" section is critical. It will dynamically render input fields or display values based on the `custom_field_definitions` associated with the specific `claim_type_configuration` of this claim. Fields will be grouped as defined in `claim_type_custom_field_associations`.
    *   **Policy Tab:** Displays relevant policy information, including coverages applicable to the claim type.
    *   **Documents Tab:** Lists required documents (dynamically from `claim_type.base_config.required_documents`) and uploaded documents.
    *   **AI Insights Tab:** Shows outputs from AI models (e.g., fraud score, damage assessment details), which might be specific to the claim type's configuration.
    *   **Right Sidebar - Contextual Actions:** Buttons like "Approve," "Deny," "Escalate" would be enabled/disabled or change based on the current workflow state and Sarah's permissions.
    *   **Right Sidebar - AI Insights Summary:** A condensed view of key AI outputs, always visible for quick reference.

---

## 2. Administrative Screen: Product Configuration (for Maria - Institution Administrator)

*   **Persona:** Maria - Institution Administrator
*   **Goal:** Define or modify an insurance product, including its basic attributes, custom data fields, associated underwriting workflow, and business rule sets.
*   **Screen Purpose:** To provide a comprehensive interface for creating and managing insurance product definitions.

*   **Block-Level Layout Sketch:**

    ```
    +---------------------------------------------------------------------------------+
    | [Header: Product Configuration - [Product Name / "New Product"]]                |
    | [Save Button] [Cancel Button] [New Version Button (if editing existing)]        |
    |---------------------------------------------------------------------------------|
    | Left Navigation Panel (Tabs for different sections) | Main Content Area         |
    |-----------------------------------------------------|---------------------------|
    | - Basic Information                                 | [Content for Selected Tab]|
    | - Custom Fields                                     |                           |
    | - Workflow Assignment                               |                           |
    | - Rule Set Assignments                              |                           |
    | - Base Configuration (JSON/Structured)              |                           |
    | - AI Integration                                    |                           |
    | - Status & Versioning                               |                           |
    |-----------------------------------------------------|---------------------------|
    |                                                     |                           |
    | **If 'Custom Fields' Tab Active:**                  |                           |
    |   [Section: Available Custom Fields]                |                           |
    |     - Search/Filter for custom fields             |                           |
    |     - List of available (unassigned) custom fields|                           |
    |     - "Add to Product" button                     |                           |
    |   [Section: Associated Custom Fields for Product]   |                           |
    |     - Table: [Field Display Name] [Data Type]       |                           |
    |       [Is Mandatory (checkbox)] [UI Group] [Order]  |                           |
    |       [Validation Override (button)] [Remove]       |                           |
    |                                                     |                           |
    +---------------------------------------------------------------------------------+
    ```

*   **Key Elements & Dynamic Content:**
    *   **Header:** Indicates if it's a new product or editing an existing one. Core action buttons (Save, Cancel).
    *   **Left Navigation Panel:** Provides access to different configuration aspects of the product.
    *   **Basic Information Tab:** Standard fields like `Product Name`, `Product Code`, `Description`, `Product Line`, `Status`, `Effective/Expiration Dates`.
    *   **Custom Fields Tab (Dynamic):**
        *   Lists available custom fields (from `custom_field_definitions` filtered by a relevant `entity_type` like "policy_application" or "product").
        *   Allows associating these fields with the current product.
        *   For each associated field, allows setting product-specific properties like `is_mandatory_for_product`, `field_group`, `sort_order_in_group`, and overriding `validation_rules`.
    *   **Workflow Assignment Tab:** Dropdowns to select pre-defined `workflow_definitions` (e.g., for underwriting, claims related to this product). The list of available workflows would be filtered by type.
    *   **Rule Set Assignments Tab:** Dropdowns to select pre-defined `rule_sets` (e.g., for eligibility, pricing, fraud). List of available rule sets filtered by context.
    *   **Base Configuration Tab:**
        *   A structured form or a JSON editor for defining product-specific parameters (e.g., `min_coverage_liability`, `telematics_discount_eligible`, `required_document_types_for_claim`). This content is dynamic based on what the institution needs to configure per product.
    *   **AI Integration Tab:** Fields to specify codes for prompt templates or AI models relevant to this product (e.g., `ai_uw_prompt_template_code`).
    *   **Status & Versioning Tab:** Manage product status (Draft, Active, Discontinued) and view version history.

---

## 3. Data-Intensive Screen: Report Viewing/Configuration (for Tom - Actuary)

*   **Persona:** Tom - Actuarial Analyst
*   **Goal:** Generate, view, and customize actuarial reports to analyze trends, assess risk, and fulfill regulatory requirements.
*   **Screen Purpose:** To allow users to select a report definition, provide runtime parameters, view the generated report (data and visualizations), and potentially access the report definition for modification (if permissions allow).

*   **Block-Level Layout Sketch:**

    ```
    +--------------------------------------------------------------------------------------+
    | [Header: Reports - [Report Name]]                                                    |
    | [Actions: Run | Schedule | Export (CSV, PDF) | Edit Definition (if admin)]           |
    |--------------------------------------------------------------------------------------|
    | Left Panel (25%): Report Parameters & Options      | Main Content Area (75%): Report Output |
    |----------------------------------------------------|--------------------------------------|
    | [Section: Runtime Parameters (Dynamic)]            | [Tab Navigation:                      |
    |  - Parameter 1 (e.g., Start Date) [Date Picker]  |    Data Table | Charts | AI Insights ] |
    |  - Parameter 2 (e.g., Product Line) [Dropdown]   |                                      |
    |  - ... (other params as per definition)            |--------------------------------------|
    |  [Run/Refresh Report Button]                       | [Tab Content Area - Dynamic]         |
    |                                                    |                                      |
    | [Section: Display Options (if applicable)]         |  **If 'Data Table' Tab Active:**       |
    |  - Group By (if report supports dynamic grouping)  |   - [Toolbar: Filter, Sort, Columns] |
    |  - Chart Type (if multiple chart views defined)    |   - [Paginated Data Table displaying |
    |                                                    |      report results including custom |
    | [Section: AI Task Controls (if applicable)]        |      fields and calculated metrics]  |
    |  - Run Forecast (Checkbox)                         |                                      |
    |  - Anomaly Detection Sensitivity (Slider)          |  **If 'Charts' Tab Active:**         |
    |                                                    |   - [Multiple Chart Views as per    |
    |                                                    |      report definition]              |
    |                                                    |                                      |
    |                                                    |  **If 'AI Insights' Tab Active:**    |
    |                                                    |   - [Forecasted Data/Charts]         |
    |                                                    |   - [List of Detected Anomalies]     |
    +--------------------------------------------------------------------------------------+
    ```

*   **Key Elements & Dynamic Content:**
    *   **Header:** Displays the name of the currently viewed/configured report. Action buttons relevant to the report.
    *   **Left Panel - Runtime Parameters (Dynamic):** This section is dynamically generated based on the `runtime_parameters` defined in the selected `report_definition`. Input fields (date pickers, dropdowns, text boxes) will match the parameter types.
    *   **Left Panel - Display Options:** May allow users to change how the current report output is viewed if the report definition allows for such flexibility (e.g., choosing a different chart type from pre-defined options).
    *   **Left Panel - AI Task Controls (Dynamic):** If the report definition includes `ai_tasks`, controls to trigger or adjust these tasks would appear here.
    *   **Main Content Area - Tab Navigation:** Allows switching between tabular data, graphical charts, and AI-generated insights.
    *   **Main Content Area - Data Table (Dynamic):**
        *   Columns are dynamically generated based on the `dimensions`, `metrics`, and `calculated_metrics` in the report definition. This includes any custom fields that were part of the data sources.
        *   Data itself is the result of the `ReportGeneratorAgent` processing the definition.
        *   Toolbar for client-side filtering, sorting, and column visibility toggle (including custom fields).
    *   **Main Content Area - Charts (Dynamic):** Visualizations are rendered based on the `presentation.charts` array in the report definition.
    *   **Main Content Area - AI Insights (Dynamic):** Displays results from AI tasks (forecasts, anomalies) if configured and executed.
    *   **Edit Definition Button:** If the user (like Maria) has permissions, this would navigate to the Report Definition UI (described in 1.e) for the current report.

---

These low-fidelity wireframes provide a basic structural guide for how these key screens could be organized to support the configurable nature of the platform and meet the needs of the defined user personas.
```
