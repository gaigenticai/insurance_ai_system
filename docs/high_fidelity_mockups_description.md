```markdown
# High-Fidelity Mockup Descriptions: Configurable Insurance Platform

This document describes the high-fidelity mockups for key screens of the configurable insurance platform. These descriptions are based on the previously defined User Personas, UI/UX Requirements, User Journey Maps, Information Architecture, Low-Fidelity Wireframes, and the Visual Design System & Style Guide Brief.

The aim is to visualize how the application will look and feel, ensuring it is "pleasing, interactive, data-rich, and layman-usable" while maintaining a modern, clean, and professional aesthetic.

---

## 1. Operational Screen: Claim File Overview (for Sarah - Claims Processor)

*   **Persona:** Sarah - Claims Processor
*   **Goal:** Quickly understand the status of a claim, access relevant information, and take necessary actions based on system guidance and configured workflows.
*   **Screen Purpose:** To provide a comprehensive, at-a-glance view of a single claim, including its current status, key details, associated policy information, documents, AI insights, and available actions.

*   **Visual Design Application:**
    *   **Overall Layout:** Adheres to the low-fidelity wireframe: a clear header, a main content area with tabs, and a right sidebar for actions and key insights. The 8pt grid system ensures consistent spacing and alignment, promoting a clean and organized look.
    *   **Color Palette:**
        *   **Primary Color (Professional Blue):** Used for the main action buttons in the sidebar (e.g., "Approve Claim," "Escalate Claim"), active tab indicators, key interactive elements like links, and potentially section headers for emphasis.
        *   **Secondary/Accent Color (Muted Teal/Green):** Used for secondary actions ("Request Information," "Add Note"), informational icons, or highlighting less critical interactive elements.
        *   **Neutral Colors:** Light gray (e.g., #F8F9FA) for the main background of content areas. Slightly darker grays for card backgrounds or subtle dividers. Dark gray text (e.g., #212529) for high readability, with lighter grays for secondary text or disabled states. Borders are thin and light gray (#CED4DA) to define elements without being visually heavy.
        *   **Semantic Colors:**
            *   `Current Status Badge` in the header will use semantic colors: Success Green for "Approved/Closed," Warning Orange for "Under Review/Pending," Error Red for "Denied/Flagged." These colors will be consistent with form validation messages and alert notifications.
            *   Urgent alerts/flags in the Summary tab will also use these semantic colors with appropriate icons.
    *   **Typography:**
        *   **Headings (H1-H3):** Inter SemiBold. H1 for "Claim ID - Claimant Name" will be prominent. Tab titles and section headers within tabs (e.g., "Incident Details," "Custom Fields") will use H3 or H4 for clear hierarchy.
        *   **Body Text & Labels:** Inter Regular for all descriptive text, field labels, and values within cards or tables, ensuring excellent legibility. Size will be around 14px-16px for body text.
        *   **Data Values:** May use Inter Medium or a slightly darker shade of neutral gray for emphasis on key data points.
    *   **Iconography (Clean Line Icons):**
        *   Icons (SVG, consistently styled) will accompany tab names for quick recognition.
        *   Action buttons in the sidebar may feature subtle icons alongside text.
        *   Icons for alert types (info, warning, error), document types, and status indicators.

*   **Key Element Styling:**
    *   **Header:** A clean, well-spaced bar. Claim ID is the most prominent (larger font, perhaps primary color). Claimant Name and Claim Type are secondary. The `Current Status Badge` will be a soft-cornered rectangle with a semantic background color and contrasting text.
    *   **Tab Navigation:** Modern, flat tabs with clear text labels. The active tab will have a solid primary color underline and potentially a slightly bolder text or subtle background highlight. Generous padding for easy clicking.
    *   **Tab Content Area:**
        *   **Summary Tab:** Information presented in "value pairs" (Label: Value) or small, well-spaced cards with clear headings. "Urgent Alerts/Flags" will use semantic colors and icons (e.g., red exclamation mark for critical alerts). "Current Workflow Step" clearly indicated, possibly with a minimalist progress bar or stepper.
        *   **Details Tab (Dynamic Custom Fields):**
            *   Custom fields rendered as standard, modern form elements (text inputs, dropdowns, date pickers with consistent styling).
            *   Each field will have its `Display Name` as a label (Inter Medium), with a small info icon (i) next to it, revealing `custom_field_definitions.description` on hover/click.
            *   Fields grouped under subtle section headers (H4 style) based on `field_group`.
            *   Mandatory fields marked with a primary color asterisk or a small "Required" label.
            *   Read-only custom field data presented cleanly, aligned with labels.
        *   **Documents Tab:** A clean list or card view for documents. Each entry shows document name (with file type icon), upload date, and status tags (e.g., "Verified" - green, "OCR Pending" - orange). A primary styled "Upload New Document" button.
        *   **AI Insights Tab:**
            *   **Fraud Score:** Displayed using a radial progress bar or a prominent number with color coding (green/yellow/red). Key contributing factors listed as bullet points with clear, concise language.
            *   **Damage Assessment:** If image-based, a thumbnail preview. Key findings (e.g., "Severity: Moderate," "Estimated Cost: $X - $Y") presented clearly.
            *   All AI insights will be visually distinct, perhaps in a card with a subtle AI-themed icon or header, and clearly labeled "AI Analysis" or "System Suggestion."
    *   **Right Sidebar:**
        *   **Contextual Actions:** Buttons styled according to the visual design system (Primary Blue for "Approve," "Escalate"; Secondary Teal/Gray for "Add Note," "Request Info"). Hover and focus states will be clear. Disabled buttons will be grayed out with reduced opacity.
        *   **AI Insights Summary:** A compact, bordered card with a clear title. Key AI metrics displayed concisely.
        *   **Related Items:** Styled as clear hyperlinks, possibly with icons.

*   **User Experience Goals Met:**
    *   **Layman-Usable:** Clear labels, intuitive tab structure, consistent iconography, and contextual help for custom fields.
    *   **Data-Rich:** All relevant information is accessible, with custom fields and AI insights integrated seamlessly and visually distinguished.
    *   **Interactive:** Clear affordances for clickable elements (tabs, buttons, links) with distinct interactive states.
    *   **Pleasing:** Modern, clean design with good use of white space, professional typography, and a cohesive color scheme.

---

## 2. Administrative Screen: Product Configuration (for Maria - Institution Administrator)

*   **Persona:** Maria - Institution Administrator
*   **Goal:** Efficiently and accurately define or modify an insurance product.
*   **Screen Purpose:** To provide a structured, intuitive, yet powerful interface for managing complex product configurations.

*   **Visual Design Application:**
    *   **Overall Layout:** A two-column layout: a fixed left navigation panel (acting as vertical tabs) and a larger main content area that updates based on the selected tab. Consistent header for product name and global actions (Save, Cancel).
    *   **Color Palette:**
        *   **Primary Color (Professional Blue):** Used for the "Save" button, active navigation tab indicator, and main section headers within the content area.
        *   **Neutral Colors:** Predominantly light grays for backgrounds to reduce visual noise. Dark gray text for readability. Subtle borders for separation.
        *   **Semantic Colors:** Used for validation messages within forms (e.g., green for success on save, red for input errors).
    *   **Typography:**
        *   Clear hierarchy: H2 for the main screen title ("Configure Product: [Product Name]"), H3 for tab titles in the content area, H4 for sub-section titles. Form labels will be clear and legible (Inter Regular/Medium).
        *   Monospace font for any direct JSON input/display areas (e.g., `base_config` advanced view).
    *   **Iconography (Clean Line Icons):**
        *   Each item in the left navigation panel will have a distinct, relevant icon.
        *   Icons for actions within tables or lists (e.g., edit, delete, add).

*   **Key Element Styling:**
    *   **Header:** Clean, with product name prominent. "Save" button styled as a primary action, "Cancel" as a secondary/text button. "New Version" button clearly visible when applicable.
    *   **Left Navigation Panel (Vertical Tabs):**
        *   Each item with an icon and clear label (e.g., "Basic Information," "Custom Fields," "Workflow").
        *   Active tab clearly indicated with a background color change (primary color, lightened) and/or a contrasting border/indicator line.
        *   Sufficient spacing for readability and clickability.
    *   **Main Content Area (per tab):**
        *   **Forms (Basic Info, AI Integration, etc.):** Standard, well-spaced form elements. Input fields with clear borders, placeholder text, and associated labels. Dropdowns styled consistently. Validation messages appear inline near the relevant field.
        *   **Custom Fields Tab:**
            *   "Available Custom Fields" could be a searchable listbox or a card-based layout for selection.
            *   "Associated Custom Fields" displayed in a clean table. Rows with actions (checkbox for "Mandatory," text input for "UI Group," "Order," "Validation Override" button leading to a modal). "Remove" action typically an icon button.
        *   **Workflow/Rule Set Assignment Tabs:** Dropdown selectors will be styled for clarity, possibly with search functionality for long lists. Currently selected workflow/ruleset clearly displayed, with an "Edit" or "Change" button.
        *   **Base Configuration Tab:** If using a structured form, it will follow standard styling. If a JSON editor is provided as an advanced option, it will use a monospace font, syntax highlighting, and line numbers.
    *   **Tables (e.g., for listing associated custom fields, rules within a ruleset):** Clean design, clear headers, alternating row colors for readability if lists are long. Action icons within rows (edit, delete) should be subtle but clear.
    *   **Buttons:** Primary (Save), Secondary (Cancel, Add New Item to List), Tertiary/Icon-only (delete item from list). All with standard interactive states.

*   **User Experience Goals Met:**
    *   **Layman-Usable (for Admin):** Structured navigation (tabs), clear forms, and progressive disclosure within tabs make complex configuration manageable.
    *   **Interactive:** Clear feedback on actions, dynamic form elements based on selections.
    *   **Pleasing:** Professional, organized, and uncluttered. The use of white space and clear typography will be critical to avoid overwhelming Maria.

---

## 3. Data-Intensive Screen: Report Viewing (for Tom - Actuary)

*   **Persona:** Tom - Actuarial Analyst
*   **Goal:** Generate, view, analyze, and customize actuarial reports efficiently.
*   **Screen Purpose:** To display report data clearly through tables and visualizations, allow parameterization, and offer options for further interaction or export.

*   **Visual Design Application:**
    *   **Overall Layout:** Adheres to the wireframe: a header for report title and global actions, a left panel for parameters and options, and a main content area with tabs for Data Table, Charts, and AI Insights.
    *   **Color Palette:**
        *   **Neutral Colors:** Predominant for the report display area to ensure data and visualizations are the focus. Light backgrounds, dark text.
        *   **Data Visualization Colors:** Utilize the pre-defined accessible and distinct color palette for charts. Ensure categorical, sequential, or diverging palettes are applied appropriately based on the data.
        *   **Primary Color (Professional Blue):** Used for interactive elements like the "Run Report" button, active tab indicators, and selected filter controls.
        *   **Accent Color (Muted Teal/Green):** For secondary actions like "Export" options or highlighting chart interaction elements.
    *   **Typography:**
        *   Highly legible sans-serif font for all table data, chart labels, and axis titles.
        *   Clear typographic hierarchy for report titles, section headers, and parameter labels.
    *   **Iconography (Clean Line Icons):**
        *   Icons for actions like "Run," "Schedule," "Export," "Filter," "Sort," different chart types, and AI insight indicators.

*   **Key Element Styling:**
    *   **Header:** Report title is prominent. Action buttons ("Run Report," "Schedule," "Export") are clearly styled and grouped. "Edit Definition" (if available based on permissions) might be slightly less prominent.
    *   **Left Panel (Parameters & Options):**
        *   Parameter input fields (date pickers, dropdowns, text boxes) will use standard, clean component styling. Each parameter clearly labeled.
        *   "Run/Refresh Report" button styled as a primary action, easily accessible.
        *   Sections for "Display Options" and "AI Task Controls" are visually separated using subtle dividers or card-like containers.
    *   **Main Content Area:**
        *   **Tab Navigation:** Clear, modern tabs. Active tab highlighted with primary color.
        *   **Data Table Tab:**
            *   Table headers: Slightly darker background, bold text, sort icons.
            *   Cell data: Clear, well-aligned, with appropriate formatting for numbers, dates, and currency (as defined in `report_definition.presentation.column_formats`).
            *   Interactive table toolbar with icon-based buttons for filtering, sorting, and column visibility.
        *   **Charts Tab:**
            *   Charts rendered with the defined visualization color palette. Axis labels, titles, and legends are clear and legible.
            *   Tooltips on hover are styled consistently with the application's theme, providing precise data values.
            *   Sufficient padding around charts.
        *   **AI Insights Tab:**
            *   Forecasted data visually integrated with existing charts or as new, clearly labeled forecast charts.
            *   Anomalies listed in a clean, readable format, perhaps with severity indicators (using semantic colors) and links to drill down into the underlying data points in the table view.
    *   **Interactive Elements:**
        *   **Filters/Date Pickers:** Standard, modern calendar controls and multi-select dropdowns. Applied filters clearly displayed.
        *   **Chart Interactivity:** Visual cues for clickable/hoverable chart elements (e.g., segments changing opacity or border on hover). Drill-down actions clearly indicated.

*   **User Experience Goals Met:**
    *   **Data-Rich:** Capable of displaying large, complex datasets in various forms, including custom fields.
    *   **Interactive:** Users can easily manipulate parameters, filter/sort data, and drill into visualizations.
    *   **Pleasing:** Clean, professional presentation of data. Visualizations are aesthetically pleasing and easy to understand.
    *   **Layman-Usable (for an Analyst):** While the data can be complex, the interface for interacting with reports is intuitive.

---

This high-fidelity mockup description provides a textual visualization of how the design system will bring the wireframes to life, focusing on creating a user experience that is both powerful for configuration and intuitive for daily operations.
```
