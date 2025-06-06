```markdown
# High-Fidelity Mockup Descriptions: Configurable Insurance Platform

This document describes the high-fidelity mockups for key screens of the configurable insurance platform. These descriptions are based on the previously defined User Personas, UI/UX Requirements, User Journey Maps, Information Architecture, Low-Fidelity Wireframes, and the Visual Design System & Style Guide Brief.

The aim is to visualize how the application will look and feel, ensuring it is "pleasing, interactive, data-rich, and layman-usable" while maintaining a modern, clean, and professional aesthetic.

---

## 1. Operational Screen: Claim File Overview (for Sarah - Claims Processor)

**Purpose:** To provide Sarah with a comprehensive, intuitive, and actionable view of a single claim, enabling efficient processing and informed decision-making.

**Visual Design Application:**

*   **Overall Layout:** Adheres to the low-fidelity wireframe: a clear header, a main content area with tabs, and a right sidebar for actions and key insights. The 8pt grid system ensures consistent spacing and alignment.
*   **Color Palette:**
    *   **Primary Color (e.g., Professional Blue):** Used for the main action buttons in the sidebar ("Approve Claim," "Escalate Claim"), active tab indicators, and important links.
    *   **Secondary/Accent Color (e.g., Muted Teal):** Used for secondary actions ("Request Information," "Add Note") or less critical highlights.
    *   **Neutral Colors:** Light gray (#F8F9FA) for the main background, slightly darker gray for card backgrounds within tabs, and dark gray (#343A40) for primary text. Borders are subtle light gray (#DEE2E6).
    *   **Semantic Colors:**
        *   `Current Status Badge` in the header will use semantic colors: Green for "Approved/Closed," Orange for "Under Review/Pending," Red for "Denied/Flagged."
        *   Alerts/Flags in the Summary tab will also use these colors.
*   **Typography:**
    *   **Headings (H1-H3):** Clean sans-serif (e.g., Inter SemiBold), with H1 for "Claim ID - Claimant Name" in the header. Tab titles and section headers within tabs will use H3.
    *   **Body Text:** Inter Regular for content, labels, and descriptions, ensuring high readability.
    *   **Labels:** Slightly smaller or lighter weight text for field labels.
    *   **Data Values:** Clear, legible font, potentially slightly bolder for key figures.
*   **Iconography (Line Icons):**
    *   Icons will be used sparingly but effectively: next to tab names, in action buttons (optional), for alert indicators, and to denote document types. Icons will be crisp and universally understandable.

**Key Element Styling:**

*   **Header:** Clean, with the Claim ID as the most prominent element. Claimant Name and Claim Type are clearly legible. The `Current Status Badge` will be a rounded pill shape with appropriate semantic color and bold text.
*   **Tab Navigation:** Tabs will have a modern, flat design. The active tab will be highlighted with the primary color (e.g., an underline or a slightly different background). Sufficient padding for clickability.
*   **Tab Content Area:**
    *   **Summary Tab:** Key info displayed in clear "Key-Value" pairs or small info cards. "Urgent Alerts/Flags" will use semantic colors and icons. "Current Workflow Step" will be clearly indicated, perhaps with a visual progress indicator.
    *   **Details Tab (Dynamic Custom Fields):**
        *   Custom fields will be rendered as standard form elements (text input, dropdown, date picker) consistent with the overall UI component styling.
        *   Each field will have a clear `Display Name` as its label, with a small help icon (tooltip) showing `custom_field_definitions.description` if available.
        *   Fields will be grouped under headings derived from `field_group` in `product_custom_field_associations`, using H4 styling.
        *   Mandatory fields will be clearly marked (e.g., with an asterisk or "Required" text).
        *   Read-only display of custom field data will be clean and well-aligned with their labels.
    *   **Documents Tab:** A clean list or grid view of documents. Each item showing document name (icon for type), upload date, and status (e.g., "Verified," "OCR Pending"). A clear "Upload New Document" button.
    *   **AI Insights Tab:**
        *   **Fraud Score:** Displayed prominently, perhaps as a gauge chart or a colored numerical value (green/yellow/red). Key contributing factors listed as bullet points or short, readable sentences.
        *   **Damage Assessment:** If applicable, might include a small image thumbnail (if image-based), a summary of detected damage, and an estimated cost range.
        *   All AI insights will be clearly labeled as "AI Suggestion" or "AI Analysis" to manage user expectations.
*   **Right Sidebar:**
    *   **Contextual Actions:** Primary action buttons (e.g., "Approve Claim") will use the primary color. Secondary actions ("Add Note") will use the secondary color or a more muted style. Disabled buttons will be visually distinct (e.g., grayed out).
    *   **AI Insights Summary:** Presented in a compact card with clear typography, using semantic colors for scores where appropriate.
    *   **Related Items:** Links styled clearly as interactive elements.

**User Experience Goals Met:**
*   **Layman-Usable:** Clear labels, intuitive tab structure, and contextual help for custom fields.
*   **Data-Rich:** All relevant information is accessible, with custom fields and AI insights integrated.
*   **Interactive:** Clickable tabs, action buttons, and potentially interactive AI insight elements.
*   **Pleasing:** Modern, clean design with consistent use of color and typography.

---

## 2. Administrative Screen: Product Configuration (for Maria - Institution Administrator)

*   **Persona:** Maria - Institution Administrator
*   **Goal:** Efficiently and accurately define or modify insurance products, including custom fields, workflows, and rules.
*   **Screen Purpose:** To provide a structured and intuitive interface for managing the complexities of product configuration.

**Visual Design Application:**

*   **Overall Layout:** Follows the low-fidelity wireframe with a clear header, left navigation panel (styled as vertical tabs or a distinct navigation list), and a main content area for the selected configuration section.
*   **Color Palette:**
    *   **Primary Color:** Used for "Save" buttons, active navigation items, and section headers.
    *   **Neutral Colors:** Predominantly light grays and whites for the background and content areas to maintain a clean, professional look and reduce visual fatigue during extended configuration tasks. Dark gray for text.
    *   **Semantic Colors:** Used subtly for validation messages (e.g., green for successful save, red for errors).
*   **Typography:**
    *   Clear hierarchy for titles, section headers, labels, and help text using the defined typographic scale.
    *   Monospace font for any raw JSON/YAML display or input areas (e.g., `base_config` if an advanced editor is used).
*   **Iconography:**
    *   Icons used for navigation items in the left panel, action buttons (e.g., "Add," "Edit," "Remove"), and to denote types of configuration elements (e.g., workflow icon, ruleset icon).

**Key Element Styling:**

*   **Header:** Clean, with the product name prominent. "Save," "Cancel," and "New Version" buttons clearly styled as primary/secondary actions.
*   **Left Navigation Panel (Tabs):** Vertically arranged tabs with icons and labels. The active tab will be clearly highlighted using the primary color (e.g., background change or a prominent left border).
*   **Main Content Area (per tab):**
    *   **Basic Information Tab:** Standard form layout with well-spaced input fields, dropdowns, and date pickers, all styled consistently.
    *   **Custom Fields Tab:**
        *   "Available Custom Fields" list: Clean list items, possibly with a small icon indicating data type. "Add to Product" button styled as a secondary action.
        *   "Associated Custom Fields" table: Clean table design. Interactive elements like checkboxes (`Is Mandatory`) and buttons ("Validation Override," "Remove") will have clear hover/focus states. The "Validation Override" button might open a modal.
    *   **Workflow/Rule Set Assignment Tabs:** Dropdowns will be styled for easy selection, potentially with search functionality if lists are long. Selected items clearly displayed. "Link" or "Change" buttons for modification.
    *   **Base Configuration Tab:** If a structured form, it will follow standard form styling. If a JSON editor, it will use a monospace font with syntax highlighting.
    *   **AI Integration Tab:** Clear input fields for template codes or model identifiers.
*   **Buttons:** Consistent styling for primary (e.g., "Save," "Add New"), secondary (e.g., "Cancel," "Edit"), and tertiary/icon buttons (e.g., "Remove" icon in a list).
*   **Tables:** Clean, with clear headers, good row separation, and hover states for rows if they are selectable or have row-level actions.

**User Experience Goals Met:**
*   **Layman-Usable (for an Admin):** Structured navigation and clear forms break down complexity. Contextual help is key.
*   **Interactive:** Clear feedback on actions, dynamic updates as configurations are made.
*   **Pleasing:** Professional, organized, and uncluttered, reducing overwhelm despite the density of information.

---

## 3. Data-Intensive Screen: Report Viewing (for Tom - Actuary)

*   **Persona:** Tom - Actuarial Analyst
*   **Goal:** Generate, view, analyze, and customize actuarial reports efficiently.
*   **Screen Purpose:** To display report data clearly through tables and visualizations, allow parameterization, and offer options for further interaction or export.

**Visual Design Application:**

*   **Overall Layout:** Consistent with the wireframe: header with report title and actions, a left panel for parameters/options, and a main content area with tabs for Data Table, Charts, and AI Insights.
*   **Color Palette:**
    *   **Neutral Colors:** Predominant for the report display itself to ensure data is the focus.
    *   **Data Visualization Colors:** Use the defined accessible and distinct color palette for charts. Ensure sequential or diverging palettes are used appropriately.
    *   **Primary/Accent Colors:** Used for interactive elements like buttons ("Run Report," "Export"), active tabs, and filter controls.
*   **Typography:**
    *   Highly legible fonts for table data and chart labels.
    *   Clear distinction between labels, values, and headers in tables and charts.
*   **Iconography:**
    *   Icons for actions like "Export," "Schedule," "Filter," "Sort," chart types.

**Key Element Styling:**

*   **Header:** Report title prominent. Action buttons ("Run," "Schedule," "Export") clearly styled. "Edit Definition" button might be less prominent or access-controlled.
*   **Left Panel (Parameters & Options):**
    *   Form elements (date pickers, dropdowns for parameters) will follow standard UI component styling.
    *   "Run/Refresh Report" button styled as a primary action.
    *   Sections for "Display Options" and "AI Task Controls" clearly delineated.
*   **Main Content Area:**
    *   **Tab Navigation:** Clear, active tab highlighted.
    *   **Data Table Tab:**
        *   Table headers clearly distinct (e.g., slightly bolder background, primary color text).
        *   Cell padding adequate for readability.
        *   Alternating row colors (zebra striping) for enhanced readability of large tables.
        *   Interactive elements in the toolbar (Filter, Sort, Columns) will use clear icons and consistent button styling.
    *   **Charts Tab:**
        *   Charts will be rendered using the defined visualization palette, ensuring good contrast and clarity.
        *   Tooltips on hover for data points will be styled consistently.
        *   Chart titles and axis labels will use clear typography.
        *   If multiple charts, they will be arranged with adequate spacing.
    *   **AI Insights Tab:**
        *   Forecasted data presented as an extension of existing charts or in a new chart.
        *   Anomalies listed clearly, perhaps with severity indicators and links to drill down into the underlying data.
*   **Interactive Elements:**
    *   **Filters/Date Pickers:** Standard, clean calendar controls and dropdowns. Applied filters clearly indicated.
    *   **Chart Drill-Downs:** Visual cues (e.g., clickable segments changing appearance on hover) to indicate interactivity.

**User Experience Goals Met:**
*   **Data-Rich:** Capable of displaying complex datasets in both tabular and visual formats, including custom fields.
*   **Interactive:** Users can filter, sort, drill down, and adjust parameters to explore data.
*   **Pleasing:** Clean presentation, effective use of color in visualizations, and a professional look that supports serious data analysis.
*   **Layman-Usable (for an Analyst):** While data-intensive, the interface for running and viewing reports should be straightforward. The report *definition* UI (covered in Admin section) handles the complexity of creation.

---

These descriptions aim to bridge the gap between low-fidelity wireframes and actual visual design, ensuring that the application of the Visual Design System aligns with the user needs and the platform's goals for configurability and usability.
```
