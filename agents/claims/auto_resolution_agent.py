from ..base.base_agent import BaseAgent
from typing import Any, Dict

class AutoResolutionAgent(BaseAgent):
    """Attempts to automatically resolve claims based on configured thresholds and policy status."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="AutoResolutionAgent", config_agent=config_agent)

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Resolves the claim automatically if it meets criteria (e.g., low value, valid policy).

        Args:
            data: Dictionary containing claim details, triage category, and policy verification results.
                  Expected keys: "claim_id", "claimed_amount", "triage_category", "policy_valid", "policy_details".
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the original claim data plus the resolution status.
            Example: {"claim_id": "...", ..., "resolution_status": "AutoApproved"/"NeedsReview", "resolution_amount": ..., "resolution_notes": "..."}
        """
        claim_id = data.get("claim_id", "unknown")
        self.logger.info(f"Executing auto-resolution check for claim {claim_id}, institution {institution_id}.")

        claimed_amount = data.get("claimed_amount")
        policy_valid = data.get("policy_valid", False)
        policy_details = data.get("policy_details", {})
        triage_category = data.get("triage_category") # Optional: could use triage result

        claims_config = self.config_agent.get_claims_rules(institution_id)
        auto_resolution_threshold: float | None = claims_config.get("auto_resolution_threshold")

        resolution_status = "NeedsReview" # Default: requires human review
        resolution_amount = None
        resolution_notes = "Claim does not meet auto-resolution criteria."

        # --- Auto-Resolution Logic --- 
        can_auto_resolve = False
        if auto_resolution_threshold is not None and claimed_amount is not None and policy_valid:
            try:
                amount = float(claimed_amount)
                coverage_limit = float(policy_details.get("coverage_limit", 0))
                deductible = float(policy_details.get("deductible", 0))
                
                # Check if amount is below threshold AND within policy limits (after deductible)
                potential_payout = max(0, amount - deductible)

                if amount <= auto_resolution_threshold and potential_payout <= coverage_limit:
                    can_auto_resolve = True
                    resolution_status = "AutoApproved"
                    resolution_amount = potential_payout # Pay amount less deductible
                    resolution_notes = f"Claim auto-approved based on amount (${amount}) being below threshold (${auto_resolution_threshold}) and within policy limits (Coverage: ${coverage_limit}, Deductible: ${deductible}). Payout: ${resolution_amount:.2f}."
                    self.logger.info(f"Claim {claim_id} meets auto-resolution criteria. Amount: {amount}, Threshold: {auto_resolution_threshold}. Payout: {resolution_amount}")
                else:
                    notes = []
                    if amount > auto_resolution_threshold:
                        notes.append(f"Amount (${amount}) exceeds auto-resolution threshold (${auto_resolution_threshold}).")
                    if potential_payout > coverage_limit:
                         notes.append(f"Potential payout (${potential_payout}) exceeds coverage limit (${coverage_limit}).")
                    resolution_notes = " | ".join(notes)
                    self.logger.info(f"Claim {claim_id} does not meet auto-resolution criteria. {resolution_notes}")

            except ValueError:
                self.logger.warning(f"Invalid numeric format in claim data or policy details for claim {claim_id}. Cannot auto-resolve. Amount: {claimed_amount}, Policy: {policy_details}")
                resolution_notes = "Invalid numeric data prevented auto-resolution check."
        else:
            notes = []
            if not policy_valid:
                notes.append("Policy is not valid.")
            if auto_resolution_threshold is None:
                notes.append("Auto-resolution threshold not configured.")
            if claimed_amount is None:
                notes.append("Claimed amount missing.")
            resolution_notes = " | ".join(notes)
            self.logger.info(f"Claim {claim_id} cannot be auto-resolved. Reason: {resolution_notes}")

        self.log_audit(institution_id, "auto_resolution_attempted", {
            "claim_id": claim_id,
            "status": resolution_status,
            "amount_approved": resolution_amount,
            "notes": resolution_notes
        })

        data["resolution_status"] = resolution_status
        data["resolution_amount"] = resolution_amount
        data["resolution_notes"] = resolution_notes
        return data

