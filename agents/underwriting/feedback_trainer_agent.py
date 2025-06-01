from ..base.base_agent import BaseAgent
from typing import Any, Dict
import json
import os
import datetime

class FeedbackTrainerAgent(BaseAgent):
    """Logs underwriting decisions and feedback for potential future training."""

    def __init__(self, config_agent: Any, feedback_dir: str = "/home/ubuntu/insurance_ai_system/data/feedback"):
        super().__init__(agent_name="FeedbackTrainerAgent", config_agent=config_agent)
        self.feedback_dir = feedback_dir
        os.makedirs(self.feedback_dir, exist_ok=True) # Ensure feedback directory exists

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Logs the final decision and any provided feedback.

        Args:
            data: Dictionary containing the final decision, rationale, score, applicant_id,
                  and potentially feedback data.
                  Expected keys: "decision", "rationale", "score", "applicant_id", "feedback" (optional).
            institution_id: The ID of the institution.

        Returns:
            A dictionary confirming the logging status.
            Example: {"feedback_logged": True/False, "log_path": "..."}
        """
        self.logger.info(f"Executing feedback logging for institution {institution_id}.")
        applicant_id = data.get("applicant_id", "unknown")
        decision = data.get("decision")
        rationale = data.get("rationale")
        score = data.get("score")
        feedback = data.get("feedback", None) # Optional feedback from human review or outcome

        if not decision or applicant_id == "unknown":
            self.logger.error(f"Missing decision or applicant_id for feedback logging. Data: {data}")
            self.log_audit(institution_id, "feedback_logging_failed_missing_data", {"applicant_id": applicant_id})
            return {"feedback_logged": False, "log_path": None}

        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "institution_id": institution_id,
            "applicant_id": applicant_id,
            "decision": decision,
            "score": score,
            "rationale": rationale,
            "feedback_provided": feedback is not None,
            "feedback_content": feedback
        }

        # Store feedback in a structured way, e.g., one file per institution or per day
        # Using one file per institution for simplicity here.
        log_file_path = os.path.join(self.feedback_dir, f"{institution_id}_underwriting_feedback.jsonl")

        try:
            with open(log_file_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            self.logger.info(f"Successfully logged feedback for applicant {applicant_id} to {log_file_path}")
            self.log_audit(institution_id, "feedback_logged_success", {"applicant_id": applicant_id, "log_path": log_file_path})
            return {"feedback_logged": True, "log_path": log_file_path}
        except Exception as e:
            self.logger.error(f"Failed to write feedback log for applicant {applicant_id} to {log_file_path}: {e}")
            self.log_audit(institution_id, "feedback_logging_failed_io_error", {"applicant_id": applicant_id, "error": str(e)})
            return {"feedback_logged": False, "log_path": log_file_path}

