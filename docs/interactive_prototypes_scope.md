```markdown
# Interactive Prototypes: Scope and Key Interactions

This document outlines the scope and key interactions for the interactive prototypes of the configurable insurance platform. These prototypes are derived from the User Personas, UI/UX Requirements, User Journey Maps, Information Architecture, and High-Fidelity Mockup Descriptions. The primary goal of these prototypes is to test core user flows and validate the usability of dynamic and configurable elements.

---

## 1. Operational Screen: Claim File Overview & Processing

*   **Persona:** Sarah - Claims Processor
*   **Goal:** Process a new 'Auto Windshield Repair' claim from FNOL to either auto-approval or escalation.
*   **Key User Flow to Prototype:**
    1.  **Claim Selection:** Sarah selects an "Auto Windshield Repair" claim from a simplified claims queue.
    2.  **Claim Overview:** Lands on the Claim Detail View, initially on the 'Summary' tab.
    3.  **Information Review:**
        *   Navigates through tabs: 'Summary', 'Details', 'Policy', 'Documents', 'AI Insights'.
        *   Scrolls within tab content to view all information.
    4.  **Action Taking:**
        *   **Scenario A (Auto-Approval):** If data implies auto-approval (e.g., low amount, low fraud score, coverage verified), Sarah clicks "Approve Claim." The system shows a confirmation, and the claim status updates.
        *   **Scenario B (Escalation):** If data implies escalation (e.g., AI fraud score is high), Sarah clicks "Escalate Claim," potentially selects a reason, adds a note, and submits. The system confirms escalation, and the claim status updates.
        *   **Scenario C (Add Note):** Sarah clicks "Add Note," types a note in a modal/panel, and saves it. The note appears in the 'Notes' tab or activity feed.

*   **Specific Interactions to Demonstrate:**
    *   **Navigation:**
        *   Clicking on a claim in a list to open the Claim Detail View.
        *   Switching between tabs (Summary, Details, Policy, Documents, AI Insights).
    *   **Information Consumption:**
        *   Viewing key claim data in the header and Summary tab.
        *   Scrolling to view custom fields within the 'Details' tab (these fields will be pre-defined for the "Auto Windshield Repair" claim type in the prototype).
        *   Viewing a mock AI summary (fraud score, damage assessment snippet) in the sidebar or 'AI Insights' tab.
        *   Viewing a list of required and uploaded documents.
    *   **Actions:**
        *   Clicking action buttons in the sidebar (e.g., "Approve Claim," "Escalate Claim," "Add Note").
        *   Interacting with a simple modal/form for adding a note or confirming escalation.
        *   Seeing visual feedback (e.g., status change, confirmation message) after an action.

---

## 2. Administrative Screen: Product Configuration

*   **Persona:** Maria - Institution Administrator
*   **Goal:** Configure a new, simple insurance product ("Basic Gadget Insurance"), including defining a few custom fields, a simple underwriting workflow, and one or two approval rules.
*   **Key User Flow to Prototype:**
    1.  **Navigate to Product Configuration:** Maria navigates from the Admin Dashboard to the "Product Definitions" section.
    2.  **Create New Product:** Clicks "Create New Product."
    3.  **Enter Basic Information:** Fills out the product name ("Basic Gadget Insurance"), code, and description on the 'Basic Information' tab.
    4.  **Define Custom Fields:**
        *   Navigates to the "Custom Fields" tab.
        *   Simulates adding 1-2 new custom fields (e.g., "Device Make," "Device Model" - these might be pre-selectable from a mock list of globally defined custom fields for simplicity in the prototype, rather than full custom field creation).
        *   Associates these fields with the product, marking one as mandatory.
    5.  **Assign Workflow:** Navigates to the "Workflow Assignment" tab and selects a pre-defined simplified "Basic Underwriting Workflow" from a dropdown.
    6.  **Assign Rule Set:** Navigates to the "Rule Set Assignments" tab and selects a pre-defined "Basic Approval Ruleset" from a dropdown for eligibility.
    7.  **Save Product:** Saves the new product configuration.

*   **Specific Interactions to Demonstrate:**
    *   **Navigation:**
        *   Navigating from a main admin menu to "Product Definitions."
        *   Using tab navigation within the Product Configuration screen (Basic Info, Custom Fields, Workflow Assignment, Rule Set Assignments).
    *   **Form Interaction:**
        *   Entering text into input fields (Product Name, Code).
        *   Selecting options from dropdowns (Workflow, Rule Set).
    *   **Custom Field Association:**
        *   Simulating the selection/addition of custom fields to the product (e.g., from a modal or a dual-list component).
        *   Checking a "mandatory" checkbox for an associated custom field.
    *   **Saving Configuration:** Clicking a "Save" button and receiving confirmation.
    *   **Visual Feedback:** Clear indication of active tabs, selected items, and successful save operations.

---

## 3. Data-Intensive Screen: Report Viewing & Basic Interaction

*   **Persona:** Tom - Actuarial Analyst
*   **Goal:** Select, run, and interact with a pre-defined report to analyze data.
*   **Key User Flow to Prototype:**
    1.  **Navigate to Reports:** Tom navigates to the "Reports" section.
    2.  **Select Report:** Selects a pre-defined report (e.g., "Loss Ratio by Product Line") from a list.
    3.  **Set Parameters:** The report view loads, displaying a panel for runtime parameters (e.g., "Start Date," "End Date"). Tom changes the date range.
    4.  **Run Report:** Clicks "Run Report."
    5.  **View Data Table:** System displays the report results in a data table. Tom can scroll and view the data.
    6.  **View Chart:** Switches to a "Charts" tab to view a visual representation of the data (e.g., a bar chart of Loss Ratio by Product Line).
    7.  **(Optional) Basic Interaction with Chart:** Hovers over chart elements to see tooltips with specific values.

*   **Specific Interactions to Demonstrate:**
    *   **Navigation:** Accessing the "Reports" section and selecting a report from a list/menu.
    *   **Parameter Input:**
        *   Using date pickers to select a date range.
        *   Selecting an option from a dropdown (e.g., for `product_line_filter`).
        *   Clicking a "Run Report" button.
    *   **Data Display:**
        *   Viewing data in a paginated/scrollable table. Column headers should reflect the report definition (including any custom fields that were part of the source data).
        *   Switching between "Data Table" and "Charts" tabs.
        *   Viewing a pre-defined chart (e.g., bar chart) based on the report data.
    *   **Chart Interaction (Basic):**
        *   Hovering over chart bars/segments to display tooltips with data values.
    *   **Visual Feedback:** Loading indicators while the report is generating/updating. Clear presentation of parameters used for the current view.

---

These prototype scopes are designed to test the core dynamic and configurable aspects of the UI, ensuring that the designs are intuitive and meet the primary needs of the key personas identified. They will focus on flow and interaction rather than pixel-perfect visual fidelity or comprehensive data accuracy at this stage.
```
