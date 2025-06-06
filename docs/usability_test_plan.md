```markdown
# Usability Test Plan: Configurable Insurance Platform - Interactive Prototypes

## 1. Overall Objectives

The primary goals of this usability testing round for the interactive prototypes are:

*   **Validate Ease of Use:** Assess how easily target users can understand and navigate the core functionalities presented in the prototypes.
*   **Identify Major Usability Issues:** Uncover significant pain points, areas of confusion, or inefficiencies in the prototyped user flows.
*   **Assess Task Completion:** Determine if users can successfully complete the defined key tasks within the prototype.
*   **Gather Qualitative Feedback:** Collect user opinions, perceptions, and suggestions regarding the design, layout, and interaction patterns.
*   **Evaluate Clarity of Configurable Elements:** Specifically for admin users, assess if the methods for configuring products, workflows, and rules are understandable. For operational users, determine if dynamically presented information (custom fields, AI insights) is clear and useful.
*   **Gauge Initial User Satisfaction:** Get a preliminary sense of user satisfaction with the proposed UI/UX direction.

## 2. Target User Profiles & Recruitment

Based on the defined personas, we will recruit participants who closely match their characteristics. Aim for 3-5 participants per persona group for this initial round.

*   **Persona 1: Sarah - Claims Processor**
    *   **Recruitment Criteria:**
        *   Currently working or recent experience (within 2 years) as a claims processor/adjuster in the insurance industry (P&C, Life, or Health).
        *   Experience processing a moderate to high volume of claims.
        *   Familiar with using claims management software.
        *   Comfortable using web applications.
        *   Technical Proficiency: Intermediate.

*   **Persona 2: Maria - Institution Administrator / Business Analyst**
    *   **Recruitment Criteria:**
        *   Experience in configuring or managing insurance products, business rules, or workflows within an insurance software system.
        *   Roles could include Product Manager, Business Systems Analyst, IT Configuration Specialist, or Operations Manager with system configuration responsibilities.
        *   Familiarity with insurance product structures and underwriting/claims processes.
        *   Technical Proficiency: Advanced (in terms of understanding system logic and configuration, not necessarily coding).

*   **Persona 3: Tom - Actuarial Analyst**
    *   **Recruitment Criteria:**
        *   Currently working or recent experience as an actuary or data analyst in the insurance industry.
        *   Experience with generating and analyzing reports related to claims, policies, and financial performance.
        *   Familiar with common actuarial metrics and reporting needs.
        *   Comfortable using data analysis and reporting tools.
        *   Technical Proficiency: Advanced (strong analytical and data interpretation skills).

## 3. Test Scope & Tasks

The test will focus on the interactive prototypes as defined in `docs/interactive_prototypes_scope.md`.

**Task Set 1: Claim File Overview & Processing (for Sarah - Claims Processor)**

*   **Scenario:** "You have received a new 'Auto Windshield Repair' claim. Your goal is to review the claim, understand its details, and decide on the next step based on the information provided."
    *   **Task 1.1 (Information Gathering):** "Open the claim for 'John Doe - Claim CLM-001'. Find out the reported date of loss, the claimed amount, the type of damage reported in the custom fields, and check if a photo of the damage has been uploaded."
    *   **Task 1.2 (AI & Policy Review):** "Review any AI-generated insights regarding this claim, such as fraud risk or damage assessment. Also, verify if the policy associated with this claim covers windshield repair."
    *   **Task 1.3 (Action Taking):**
        *   "Based on the information and system recommendations, if the claim seems straightforward and meets auto-approval criteria (assume it does for this scenario), proceed to approve the claim."
        *   (Alternative for a different scenario/prototype branch) "Imagine the AI fraud score is high. Escalate this claim for further review, adding a note about your concern."

**Task Set 2: Product Configuration (for Maria - Institution Administrator)**

*   **Scenario:** "Your institution wants to launch a new 'Basic Gadget Insurance' product. Your task is to set up the basic structure for this product in the system."
    *   **Task 2.1 (Product Creation & Basic Info):** "Navigate to the product configuration area and begin creating a new product. Enter 'Basic Gadget Insurance' as the name and 'GADGET_BASIC_V1' as the product code. Save this basic information."
    *   **Task 2.2 (Custom Field Association):** "For this gadget insurance, you need to add two custom fields: 'Device Type' (e.g., Smartphone, Laptop) and 'Purchase Date'. Find these fields (assume they are pre-defined for selection) and associate them with your new product. Make 'Device Type' mandatory."
    *   **Task 2.3 (Workflow & Rule Association):** "Assign a pre-defined 'Simple Underwriting Workflow' and a 'Basic Gadget Approval Ruleset' to this product from the available options."

**Task Set 3: Report Viewing & Basic Interaction (for Tom - Actuary)**

*   **Scenario:** "You need to review the company's performance for the last quarter. Your goal is to run a report, view the data, and make a minor adjustment to see different results."
    *   **Task 3.1 (Report Selection & Execution):** "Navigate to the reporting section and find the 'Loss Ratio by Product Line' report. Run this report for the period of January 1, 2024, to March 31, 2024."
    *   **Task 3.2 (Data Interpretation):** "Once the report is generated, identify the product line with the highest loss ratio from the table. Then, switch to the chart view to see this visually."
    *   **Task 3.3 (Parameter Adjustment):** "Now, change the reporting period to only cover January 2024 and re-run the report to see how the data changes."

## 4. Methodology

*   **Method:** Moderated Remote Usability Testing.
    *   Sessions will be conducted via video conferencing software (e.g., Zoom, Google Meet, Microsoft Teams).
    *   The moderator will guide the participant, observe their interactions, and ask probing questions.
    *   Sessions will be recorded (with participant consent) for later analysis.
*   **Session Structure (approx. 60-90 minutes per participant):**
    1.  **Introduction & Consent (5-10 mins):** Welcome, explain the purpose of the session, assure them it's not a test of them but of the prototype, obtain consent for recording, explain the think-aloud protocol.
    2.  **Pre-test Questionnaire (5 mins):** Brief questions about their role, experience with similar software, and general tech comfort (can be a short online survey link).
    3.  **Task Performance (40-60 mins):** Participant shares their screen and attempts the assigned tasks for their persona. The moderator observes and encourages thinking aloud. Probing questions will be used to understand their thought process and identify pain points.
    4.  **Post-test Questionnaire/Interview (10-15 mins):**
        *   Administer System Usability Scale (SUS) or a similar standardized questionnaire.
        *   Open-ended questions about their overall experience, likes, dislikes, and suggestions for improvement.

## 5. Key Metrics to Collect

*   **Qualitative:**
    *   **Think-aloud protocol:** Direct user verbalizations of thoughts, expectations, and frustrations during task performance.
    *   **Observation notes:** Moderator's observations of user behavior, hesitation points, errors, workarounds, and facial expressions.
    *   **User-reported issues:** Specific problems or points of confusion identified by the participant.
    *   **User satisfaction/feedback:** Responses to post-test interview questions regarding ease of use, clarity, efficiency, and overall impression.
    *   Answers to open-ended questions about specific features or flows.
*   **Quantitative (to be collected where feasible with prototypes):**
    *   **Task Success Rate:** Binary (Complete / Incomplete with assistance / Incomplete) for each task.
    *   **Critical Error Count:** Number of errors that prevented task completion or led to an incorrect outcome.
    *   **Non-Critical Error Count:** Number of recoverable errors or slips.
    *   **Subjective Ratings:**
        *   System Usability Scale (SUS) score.
        *   Ease of use ratings for specific tasks (e.g., on a 1-5 Likert scale).

## 6. Test Environment & Tools (Conceptual)

*   **Interactive Prototype:** A link to the clickable prototype (e.g., built in Figma, Axure, or a similar tool) that covers the defined user flows. The prototype will use mock data but simulate key interactions.
*   **Video Conferencing Tool:** Software like Zoom, Microsoft Teams, or Google Meet for screen sharing, observation, and recording.
*   **Note-Taking Tools:** Digital note-taking app (e.g., Notion, OneNote) or traditional pen and paper for the moderator.
*   **Survey Tool (Optional):** For pre-test and post-test questionnaires (e.g., Google Forms, SurveyMonkey).

## 7. Moderator Script Outline (Key Sections)

*   **A. Introduction & Welcome (5 mins)**
    *   Thank participant for their time.
    *   Introduce self and purpose of the session (evaluating a new platform design, not testing them).
    *   Explain that their feedback is valuable and there are no right/wrong answers.
    *   Mention recording and ask for consent.
    *   Explain the "think aloud" protocol.
    *   Opportunity for participant questions.
*   **B. Pre-Test Questions (if not done via survey - 5 mins)**
    *   Briefly confirm role, experience, and tech comfort.
*   **C. Task Presentation & Execution (40-60 mins)**
    *   For each task:
        *   Clearly present the scenario and the task.
        *   "Imagine you are [Persona] and you need to [Goal related to the task]..."
        *   "Please try to complete this task using the prototype. Remember to think out loud as you go."
        *   Observe silently, taking notes.
        *   Use probing questions if the user gets stuck or makes an interesting comment (e.g., "What are you expecting to see here?", "What made that confusing?"). Avoid leading questions.
*   **D. Post-Test Interview & Questionnaire (10-15 mins)**
    *   Administer SUS questionnaire.
    *   Ask general questions:
        *   "Overall, what was your impression of the system?"
        *   "What did you like most/least?"
        *   "Was there anything you found particularly confusing or difficult?"
        *   "If you had a magic wand, what would you change?"
        *   "Do you have any other feedback or suggestions?"
*   **E. Wrap-up and Thank You (2 mins)**
    *   Thank the participant again for their valuable input.
    *   Explain next steps if any (e.g., how feedback will be used).

This usability test plan provides a framework for evaluating the interactive prototypes and gathering crucial feedback to refine the design of the configurable insurance platform.
```
