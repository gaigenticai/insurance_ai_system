from ...agents.config_agent import ConfigAgent
from ...agents.underwriting.applicant_intake_agent import ApplicantIntakeAgent
from ...agents.underwriting.document_ocr_agent import DocumentOCRAgent
from ...agents.underwriting.risk_scoring_agent import RiskScoringAgent
from ...agents.underwriting.adaptive_questioning_agent import AdaptiveQuestioningAgent
from ...agents.underwriting.feedback_trainer_agent import FeedbackTrainerAgent
from typing import Dict, Any
import logging

class UnderwritingFlow:
    """Orchestrates the autonomous underwriting process."""

    def __init__(self, config_agent: ConfigAgent):
        self.config_agent = config_agent
        self.logger = logging.getLogger("UnderwritingFlow")
        # Instantiate agents
        self.intake_agent = ApplicantIntakeAgent(config_agent)
        self.ocr_agent = DocumentOCRAgent(config_agent)
        self.scoring_agent = RiskScoringAgent(config_agent)
        self.questioning_agent = AdaptiveQuestioningAgent(config_agent)
        self.feedback_agent = FeedbackTrainerAgent(config_agent)
        self.logger.info("UnderwritingFlow initialized with all required agents.")

    def run(self, application_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Runs the full underwriting flow for a given application.

        Args:
            application_data: The initial application data, including structured fields 
                              and potentially unstructured document text.
                              Requires an "applicant_id" for tracking.
                              Example: {"applicant_id": "APP123", "full_name": "...", "document_text": "..."}
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the final underwriting decision and status.
            Example: {"applicant_id": "APP123", "status": "Complete"/"NeedsInfo", 
                      "decision": "Approve"/"Deny"/"Modify Terms"/None, 
                      "questions": [...], "rationale": "..."}
        """
        applicant_id = application_data.get("applicant_id")
        if not applicant_id:
            self.logger.error("Missing applicant_id in application data. Aborting flow.")
            return {"status": "Error", "message": "Missing applicant_id"}

        self.logger.info(f"Starting underwriting flow for applicant {applicant_id}, institution {institution_id}.")

        # 1. Intake and Initial Validation
        intake_result = self.intake_agent.execute(application_data, institution_id)
        current_data = intake_result.get("applicant_data", application_data)
        current_data["applicant_id"] = applicant_id # Ensure ID persists

        # 2. Document OCR (if applicable)
        ocr_result = {"extracted_data": {}, "ocr_status": "not_run"}
        if "document_text" in current_data and current_data["document_text"]:
            ocr_result = self.ocr_agent.execute({"document_text": current_data["document_text"], "applicant_id": applicant_id}, institution_id)
            # Merge extracted data - careful about overwriting existing fields if names clash
            current_data.update(ocr_result.get("extracted_data", {}))
        else:
            self.logger.info(f"No document text found for applicant {applicant_id}. Skipping OCR.")

        # 3. Check for missing info *after* initial intake and OCR
        # Re-evaluate required fields against the combined data
        required_fields = self.config_agent.get_setting(institution_id, "underwriting", "required_fields", default=[])
        missing_fields_after_ocr = [field for field in required_fields if field not in current_data or not current_data[field]]
        
        questioning_result = self.questioning_agent.execute(
            {"missing_fields": missing_fields_after_ocr, "applicant_id": applicant_id}, 
            institution_id
        )

        if questioning_result.get("needs_more_info"):
            self.logger.warning(f"Underwriting paused for applicant {applicant_id}. Needs more information.")
            return {
                "applicant_id": applicant_id,
                "status": "NeedsInfo",
                "decision": None,
                "questions": questioning_result.get("questions", []),
                "rationale": "Missing required information."
            }

        # 4. Risk Scoring (if all required info is present)
        scoring_result = self.scoring_agent.execute({"applicant_data": current_data, "applicant_id": applicant_id}, institution_id)
        decision = scoring_result.get("decision")
        rationale = scoring_result.get("rationale")
        score = scoring_result.get("score")

        # 5. Feedback Logging
        feedback_data = {
            "applicant_id": applicant_id,
            "decision": decision,
            "rationale": rationale,
            "score": score,
            # 'feedback' field could be added later if human review occurs
        }
        self.feedback_agent.execute(feedback_data, institution_id)

        self.logger.info(f"Underwriting flow completed for applicant {applicant_id}. Decision: {decision}")
        return {
            "applicant_id": applicant_id,
            "status": "Complete",
            "decision": decision,
            "questions": [],
            "rationale": rationale
        }

# Example Usage (for testing)
# if __name__ == "__main__":
#     config = ConfigAgent()
#     flow = UnderwritingFlow(config)
#     
#     # Example application with enough data
#     app_data_complete = {
#         "applicant_id": "UW-TEST-001",
#         "full_name": "Alice Example",
#         "address": "123 Main St",
#         "date_of_birth": "01/01/1990",
#         "income": 80000,
#         "credit_score": 720,
#         "debt_to_income_ratio": 0.3,
#         "address_location_tag": "SafeZoneC",
#         "document_text": "Name: Alice Example\nDOB: 01/01/1990\nOther info..."
#     }
#     result_complete = flow.run(app_data_complete, "institution_a")
#     print("\n--- Complete Application Result ---")
#     print(json.dumps(result_complete, indent=2))
# 
#     # Example application missing data
#     app_data_incomplete = {
#         "applicant_id": "UW-TEST-002",
#         "full_name": "Bob Test",
#         "address": "456 Side St",
#         # Missing DOB, income, credit_score
#         "document_text": "Name: Bob Test"
#     }
#     result_incomplete = flow.run(app_data_incomplete, "institution_a")
#     print("\n--- Incomplete Application Result ---")
#     print(json.dumps(result_incomplete, indent=2))
#
#     # Example application with low score
#     app_data_low_score = {
#         "applicant_id": "UW-TEST-003",
#         "full_name": "Charlie Risk",
#         "address": "789 Danger Ave",
#         "date_of_birth": "03/15/1985",
#         "income": 50000,
#         "credit_score": 580, # Below threshold
#         "debt_to_income_ratio": 0.5, # Above threshold
#         "address_location_tag": "FloodZoneA", # High risk
#         "document_text": "Name: Charlie Risk\nDOB: 03/15/1985"
#     }
#     result_low_score = flow.run(app_data_low_score, "institution_a")
#     print("\n--- Low Score Application Result ---")
#     print(json.dumps(result_low_score, indent=2))

# Need json for example usage
import json

