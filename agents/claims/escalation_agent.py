from agents.base.base_agent import BaseAgent
from typing import Any, Dict

class EscalationAgent(BaseAgent):
    """Determines if a claim needs escalation to human review based on complexity or status."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="EscalationAgent", config_agent=config_agent)

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Flags a claim for escalation if it wasn't auto-resolved or meets other criteria.

        Args:
            data: Dictionary containing claim details and current processing status.
                  Expected keys: "claim_id", "triage_category", "policy_valid", "resolution_status", "fraud_flags" (optional).
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the original claim data plus an escalation flag and reason.
            Example: {"claim_id": "...", ..., "escalate": True/False, "escalation_reason": "..."}
        """
        claim_id = data.get("claim_id", "unknown")
        self.logger.info(f"Executing escalation check for claim {claim_id}, institution {institution_id}.")

        resolution_status = data.get("resolution_status")
        triage_category = data.get("triage_category")
        policy_valid = data.get("policy_valid", False)
        fraud_flags = data.get("fraud_flags", []) # Assumes FraudDetectorAgent runs before this

        escalate = False
        escalation_reason = "No escalation required."

        # --- Escalation Logic --- 
        # Escalate if not auto-approved
        if resolution_status != "AutoApproved":
            escalate = True
            escalation_reason = f"Claim requires manual review (Status: {resolution_status})."
            if not policy_valid:
                 escalation_reason += " Policy invalid." # Add more context
        
        # Escalate if high severity, regardless of auto-resolution (might need review anyway)
        if triage_category == "HighSeverity":
             if not escalate: # Avoid duplicate reason if already escalating
                 escalate = True
                 escalation_reason = "Claim triaged as High Severity."
             else:
                 escalation_reason += " Triaged as High Severity."

        # Escalate if fraud flags are present
        if fraud_flags:
            if not escalate:
                escalate = True
                escalation_reason = f"Potential fraud flags detected: {', '.join(fraud_flags)}."
            else:
                 escalation_reason += f" Potential fraud flags: {', '.join(fraud_flags)}."

        # Add more complex escalation rules here based on config if needed
        # e.g., escalate claims above a certain amount even if auto-approved for audit

        if escalate:
            self.logger.warning(f"Claim {claim_id} flagged for escalation. Reason: {escalation_reason}")
            self.log_audit(institution_id, "claim_escalated", {"claim_id": claim_id, "reason": escalation_reason})
        else:
             self.logger.info(f"Claim {claim_id} does not require escalation.")
             self.log_audit(institution_id, "claim_not_escalated", {"claim_id": claim_id})


        data["escalate"] = escalate
        data["escalation_reason"] = escalation_reason
        return data

