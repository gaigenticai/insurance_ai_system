from ..base.base_agent import BaseAgent
from typing import Any, Dict, List

class ApplicantIntakeAgent(BaseAgent):
    """Handles the initial intake and basic validation of applicant data."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="ApplicantIntakeAgent", config_agent=config_agent)

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Validates incoming applicant data against required fields defined in config.

        Args:
            data: The applicant data dictionary.
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the original data and a validation status.
            Example: {"applicant_data": data, "validation_passed": True/False, "missing_fields": [...]}
        """
        self.logger.info(f"Executing intake for institution {institution_id}.")
        
        required_fields: List[str] = self.config_agent.get_setting(
            institution_id, "underwriting", "required_fields", default=[]
        )
        
        if not required_fields:
            self.logger.warning(f"No required fields configured for institution {institution_id}. Skipping validation.")
            self.log_audit(institution_id, "intake_processed", {"status": "success", "validation_skipped": True, "applicant_id": data.get("applicant_id", "unknown")})
            return {"applicant_data": data, "validation_passed": True, "missing_fields": []}

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        validation_passed = not bool(missing_fields)
        
        if validation_passed:
            self.logger.info(f"Applicant data validation passed for institution {institution_id}.")
            self.log_audit(institution_id, "intake_validation_passed", {"applicant_id": data.get("applicant_id", "unknown")})
            result = {"applicant_data": data, "validation_passed": True, "missing_fields": []}
        else:
            self.logger.warning(f"Applicant data validation failed for institution {institution_id}. Missing fields: {missing_fields}")
            self.log_audit(institution_id, "intake_validation_failed", {"missing_fields": missing_fields, "applicant_id": data.get("applicant_id", "unknown")})
            result = {"applicant_data": data, "validation_passed": False, "missing_fields": missing_fields}
            
        return result

