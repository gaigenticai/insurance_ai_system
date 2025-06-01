from ..base.base_agent import BaseAgent
from typing import Any, Dict, List

class AdaptiveQuestioningAgent(BaseAgent):
    """Identifies missing information required for underwriting and generates questions."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="AdaptiveQuestioningAgent", config_agent=config_agent)

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Checks for missing required fields and generates questions based on config.

        Args:
            data: Dictionary containing the current state of the application, 
                  including validation results and applicant data.
                  Expected keys: "validation_passed", "missing_fields", "applicant_id".
            institution_id: The ID of the institution.

        Returns:
            A dictionary indicating if further questions are needed and the questions themselves.
            Example: {"needs_more_info": True/False, "questions": ["Please provide X", "Clarify Y"]}
        """
        self.logger.info(f"Executing adaptive questioning for institution {institution_id}.")
        applicant_id = data.get("applicant_id", "unknown")
        missing_fields = data.get("missing_fields", [])
        # Potentially, this agent could also identify fields needed based on risk score/decision
        # For now, it relies on the initial intake validation

        needs_more_info = bool(missing_fields)
        questions = []

        if needs_more_info:
            self.logger.info(f"Missing information identified for applicant {applicant_id}: {missing_fields}")
            # Generate user-friendly questions based on field names
            # This could be made more sophisticated using a mapping in the config
            questions = [f'Please provide your {field.replace("_", " ")}.' for field in missing_fields]
            self.log_audit(institution_id, "adaptive_questioning_triggered", {"applicant_id": applicant_id, "missing_fields": missing_fields, "questions_generated": len(questions)})
        else:
            self.logger.info(f"No missing information identified for applicant {applicant_id}. No further questions needed at this stage.")
            self.log_audit(institution_id, "adaptive_questioning_skipped", {"applicant_id": applicant_id})

        return {"needs_more_info": needs_more_info, "questions": questions}


