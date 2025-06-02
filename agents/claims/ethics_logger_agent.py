from agents.base.base_agent import BaseAgent
from typing import Any, Dict
import json
import os
import datetime
from datetime import datetime, timezone


class EthicsLoggerAgent(BaseAgent):
    """Logs key decisions and potential ethical considerations during claims processing."""

    def __init__(self, config_agent: Any, ethics_log_dir: str = "/home/ubuntu/insurance_ai_system/logs/ethics"):
        super().__init__(agent_name="EthicsLoggerAgent", config_agent=config_agent)
        self.ethics_log_dir = ethics_log_dir
        os.makedirs(self.ethics_log_dir, exist_ok=True) # Ensure directory exists

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Logs ethically relevant events like claim denials or escalations.

        Args:
            data: Dictionary containing claim details and processing outcomes.
                  Expected keys: "claim_id", "decision_point" (e.g., "Denial", "Escalation"), 
                                 "reasoning" (e.g., resolution_notes, escalation_reason), 
                                 "relevant_data" (subset of claim data).
            institution_id: The ID of the institution.

        Returns:
            A dictionary confirming the logging status.
            Example: {"ethics_log_recorded": True/False, "log_path": "..."}
        """
        claim_id = data.get("claim_id", "unknown")
        decision_point = data.get("decision_point")
        reasoning = data.get("reasoning")
        relevant_data = data.get("relevant_data", {})
        self.logger.info(f"Executing ethics logging for claim {claim_id}, decision point: {decision_point}, institution {institution_id}.")

        if not decision_point or claim_id == "unknown":
            self.logger.error(f"Missing decision_point or claim_id for ethics logging. Data: {data}")
            # Not logging an audit event here as this agent *is* the logger
            return {"ethics_log_recorded": False, "log_path": None}

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().isoformat(),
            "institution_id": institution_id,
            "claim_id": claim_id,
            "decision_point": decision_point,
            "reasoning": reasoning,
            "relevant_data": relevant_data, # Log data used for the decision
            "agent_responsible": data.get("triggering_agent", self.agent_name) # Track which agent triggered the log
        }

        # Store logs, perhaps separated by institution or date
        log_file_path = os.path.join(self.ethics_log_dir, f"{institution_id}_ethics.jsonl")

        try:
            with open(log_file_path, "a") as f:
                # Use default=str to handle potential non-serializable types like datetime
                f.write(json.dumps(log_entry, default=str) + "\n") 
            self.logger.info(f"Successfully recorded ethics log for claim {claim_id} to {log_file_path}")
            # This agent logs ethics, so it doesn't call self.log_audit for its own success/failure
            return {"ethics_log_recorded": True, "log_path": log_file_path}
        except Exception as e:
            self.logger.error(f"Failed to write ethics log for claim {claim_id} to {log_file_path}: {e}")
            return {"ethics_log_recorded": False, "log_path": log_file_path}

