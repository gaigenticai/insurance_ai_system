```markdown
# Configurable Insurance AI Platform - High-Level Design

## 1. Introduction

The primary goal of this project is to refactor the Insurance AI System into a highly configurable platform. This will enable diverse insurance companies (tenants/institutions) to tailor the system to their specific products, operational processes, business rules, and analytical needs without requiring extensive custom development for each.

The key functional areas of focus for this enhanced configurability are:
*   Underwriting
*   Claims Processing
*   Actuarial Reporting

This document outlines the high-level design for the core foundations enabling this configurability and its application across the key modules, UI, testing, and documentation.

## 2. Core Configurability Foundations

Three foundational pillars will support system-wide configurability:

### 2.1. Dynamic Data Model / Schema Extension

This foundation allows institutions to define custom data fields for their specific needs, extending the core system entities.

*   **Leveraging `JSONB` Columns:** Core entity tables (e.g., `policies`, `claims`, `customers`, `products`) will utilize `JSONB` columns (e.g., `custom_fields`, `additional_attributes`) to store instance data for custom fields.
*   **Custom Field Metadata Tables:**
    *   `custom_field_definitions`: Stores metadata for each custom field, including `institution_id`, `entity_type` (e.g., "policy", "claim"), `field_name`, `display_name`, `field_type` (text, number, date, boolean, enum), and `validation_rules` (JSONB).
    *   `custom_field_enum_options`: Stores predefined options for "enum" type custom fields.
*   **Management:** Institutions will manage custom field definitions via dedicated API endpoints and a "Custom Field Manager" UI.
*   **Validation:** Custom field data will be validated at the API level against their definitions. The UI will provide client-side validation guidance.

### 2.2. Centralized Configurable Rules Engine

This engine enables institutions to define and manage business logic dynamically.

*   **Rule Definition & Storage:**
    *   Rules will be defined in JSON or YAML format.
    *   Stored in a `JSONB` column (`definition`) within a `rule_sets` table, linked to `institutions` and identified by `rule_set_name`, `version`, and `is_active` status.
    *   Rule structure includes conditions (evaluating facts against values or other facts using operators like `equals`, `lessThan`, `contains`) and actions (e.g., `set_status`, `set_payout`, `trigger_event`).
*   **Architecture (Python-based):**
    *   `RuleLoader`: Fetches rule definitions.
    *   `ContextBuilder`: Prepares input "facts" (data from various sources like claim data, policy data, custom fields, product configurations).
    *   `RuleEvaluator`: Evaluates rules against the context.
    *   `ActionExecutor`: Executes actions for triggered rules.
*   **Agent Refactoring:** Existing agents (e.g., `ClaimTriageAgent`, `FraudDetectorAgent`, `AutoResolutionAgent`) will be refactored to prepare context, invoke the Rules Engine with specific rule sets, and act upon the results.

### 2.3. Declarative Workflow Engine

This engine allows institutions to define and customize the sequence of operations and transitions for core processes.

*   **Workflow Definition & Storage:**
    *   Workflow definitions in JSON or YAML, stored in a `JSONB` column (`definition`) in a `workflow_definitions` table (linked to `institutions`, with `workflow_name`, `version`, `is_active`).
    *   Structure includes `name`, `initial_state`, a map of `states` (each with `actions` like `execute_agent`, `execute_ruleset`, `invoke_ai_service`), and `transitions` between states (with conditions based on facts or rule set evaluations).
*   **Architecture (Python-based):**
    *   `WorkflowLoader`: Fetches workflow definitions.
    *   `WorkflowStateManager`: Manages the state of each workflow instance (e.g., in a `workflow_instances` table).
    *   `ActionInvoker`: Interprets and executes actions defined for a state.
    *   `TransitionHandler`: Evaluates transition conditions to move to the next state.
*   **Flow Class Refactoring:** Existing imperative flow classes (e.g., `ClaimsFlow`) will be refactored. They will primarily initiate workflow instances with the Workflow Engine, which then orchestrates the process based on the declarative definition.

## 3. Configurable Underwriting Module

*   **Insurance Product Definition:**
    *   A new `insurance_products` table will store product details (`institution_id`, `product_code`, `name`, `status`, `base_config` (JSONB for parameters like default coverages, AI prompt template codes), and foreign keys to default `workflow_definitions` and `rule_sets` for eligibility/pricing.
    *   A `product_custom_field_associations` table will link products to `custom_field_definitions`, specifying product-specific requirements and UI groupings.
*   **Underwriting Workflow Configuration:**
    *   Product-specific underwriting workflows (e.g., "Personal Auto Gold Underwriting") will be defined declaratively.
    *   Steps will include Application Intake, Data Validation (including custom fields), Document Collection, OCR, AI Risk Assessment, Scoring & Rating, and Decisioning.
    *   Actions within steps will call refactored agents, product-specific rule sets (e.g., `product.eligibility_ruleset_id`), and AI services (using `product.base_config.ai_uw_prompt_template_code`).
*   **Underwriting Rules Configuration:**
    *   Rule sets for eligibility (e.g., age restrictions), data validation, pricing adjustments (e.g., telematics discounts based on custom fields), and referral triggers will be configurable per product.
    *   Rules will access standard application data, `custom_fields` (e.g., `custom_fields.vehicle_vin`), and product-specific parameters from `insurance_products.base_config`.
*   **AI Integration Customization:**
    *   Product-specific AI prompt templates will be stored (e.g., in an `ai_prompt_templates` table) and referenced in workflow configurations.
    *   Future support for institutions to configure and use their own custom AI models for specific underwriting tasks, managed via `AIServiceManager`.

## 4. Configurable Claims Module

*   **Claim Type Definition:**
    *   A new `claim_type_configurations` table, linked to `insurance_products`, will define specific claim types (e.g., "Auto Windshield Repair" under "Personal Auto Gold").
    *   This table will store `claim_type_code`, `name`, links to default claims workflow, FNOL/fraud/settlement rulesets, and `base_config` (JSONB for parameters like required documents, fast-track criteria, AI model preferences).
    *   A `claim_type_custom_field_associations` table will link claim types to relevant "claim" entity `custom_field_definitions`.
*   **Claims Workflow Configuration:**
    *   Claim-type-specific workflows will be defined (e.g., a streamlined "Windshield Repair Workflow").
    *   Steps will include FNOL, Document Collection, AI Damage Assessment, Coverage Verification, Fraud Screening, and Settlement/Referral.
    *   Actions will reference `claim_type.base_config` for parameters like required documents or specific AI models for damage assessment.
*   **Claims Rules Configuration:**
    *   Rule sets for FNOL validation, fraud flagging (e.g., based on claim history or AI scores), coverage adjudication (checking policy terms against claim type), and settlement authority (e.g., auto-approval limits for fast-track claims).
    *   Rules will use data from the claim, policy, custom fields, AI outputs, and `claim_type.base_config`.
*   **AI Integration Customization:**
    *   Claim-type-specific AI prompt templates (e.g., for image-based damage assessment, claim summary generation) will be configurable.
    *   The system will support configuring different AI models for specific claim processing tasks (e.g., specialized fraud detection model, glass damage assessment model) referenced in the `claim_type.base_config`.

## 5. Configurable Actuarial Reporting Module

*   **Report Definition Structure:**
    *   A new `report_definitions` table will store report metadata (`institution_id`, `report_code`, `name`, `category`, `definition` JSONB).
    *   The JSON `definition` will specify:
        *   `data_sources`: Core entities (policies, claims) and lists of standard and `custom_fields_to_include`.
        *   `runtime_parameters`: For user inputs like date ranges.
        *   `filters`: Criteria applied to sourced data.
        *   `grouping_and_aggregation`: Dimensions and metrics with aggregate expressions (SUM, AVG, COUNT).
        *   `calculated_metrics`: Post-aggregation calculations (e.g., Loss Ratio).
        *   `presentation`: Default views, chart configurations.
        *   `ai_tasks` (Optional): For forecasting or anomaly detection on report results.
*   **Custom Calculation Logic:** An embedded expression language will be used within report definitions for defining calculations on sourced or aggregated data.
*   **Data Sourcing & Custom Fields:** The reporting engine will dynamically build queries to include specified custom fields by referencing `custom_field_definitions` and extracting data from `JSONB` columns. For performance, a reporting data mart or materialized views may be considered for large datasets, with ETL processes aware of custom field structures.

## 6. UI Adaptations for Configurability

The UI will be significantly enhanced to manage and utilize these configurations.

*   **Administration UI Sections:**
    *   **Custom Field Manager:** CRUD operations for `custom_field_definitions`, including type and validation rule specification.
    *   **Product/Claim Type Definition UI:** Interface to create/edit products and claim types, associate custom fields, link to workflow/ruleset definitions, and manage `base_config` parameters.
    *   **Workflow Editor UI:** A visual or structured form-based editor for defining workflow states, actions (calling agents, rulesets, AI models), and conditional transitions.
    *   **Rules Editor UI:** Interface for building rule conditions (facts, operators, values) and actions, and organizing them into rule sets.
    *   **Report Definition UI:** A multi-step wizard or tabbed interface for creating report templates, selecting data sources (including custom fields), defining filters, aggregations, calculations, and presentation elements.
*   **Dynamic UI Rendering in Operational Screens:**
    *   **Dynamic Forms:** Data entry forms (e.g., policy application, FNOL) will dynamically render input fields based on the custom fields configured for the selected product or claim type, including data types and validation.
    *   **Dynamic Data Displays:** Tables and detail views for policies, claims, etc., will allow users to select and display relevant custom fields as columns, with support for filtering and sorting on these fields.

## 7. Testing Strategy

*   **Core Framework Testing:** Rigorous unit, integration, and E2E tests for the dynamic data model, rules engine, workflow engine, reporting engine, and base UI components using "reference configurations."
*   **Tenant-Specific Configuration Testing:** Provide tools for configuration validation (syntax, basic logic), "Dry Run"/"Simulation" modes for workflows and rule sets, and support for institution-led UAT in sandboxed environments.
*   **Performance and Scalability Testing:** Focus on scenarios with many custom fields, complex rule/workflow executions, and large-scale report generation.
*   **Security Testing:** Emphasize tenant data isolation, secure admin interfaces, and safe evaluation of configured expressions/rules.

## 8. Documentation Strategy

*   **Administrator Guides:** Comprehensive guides covering core configurability concepts and detailed "how-to" instructions for using each administration UI (Custom Fields, Products, Claims, Workflows, Rules, Reports, AI settings). Will include best practices and examples.
*   **User Guides (Operational Staff):** Focus on core tasks, explaining that UIs are dynamic. Rely on in-UI contextual help (tooltips from custom field definitions) and encourage institution-specific supplements.
*   **Developer Documentation:** API specifications, details on the expression language, and (if applicable) guides for extending the system with new agent types or custom integrations.
*   **Living Documentation Concepts:** Embed help within UIs, make configurations exportable and human-readable, auto-generate summaries for reports/workflows, and provide auditing for configuration changes.
```
