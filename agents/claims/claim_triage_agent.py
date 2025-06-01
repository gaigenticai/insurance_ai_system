from ..base.base_agent import BaseAgent
from typing import Any, Dict, List

class ClaimTriageAgent(BaseAgent):
    """Ingests and triages incoming claims based on configured rules."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="ClaimTriageAgent", config_agent=config_agent)

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Triages a claim based on severity keywords and value thresholds from config.

        Args:
            data: Dictionary containing claim details.
                  Expected keys: "claim_id", "claim_description", "claimed_amount".
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the original claim data plus the triage category.
            Example: {"claim_id": "...", ..., "triage_category": "HighSeverity"/"LowValue"/"Standard"}
        """
        claim_id = data.get("claim_id", "unknown")
        self.logger.info(f"Executing claim triage for claim {claim_id}, institution {institution_id}.")

        claim_description = data.get("claim_description", "").lower()
        claimed_amount = data.get("claimed_amount")

        claims_config = self.config_agent.get_claims_rules(institution_id)
        triage_rules = claims_config.get("triage_rules", {})
        high_severity_keywords: List[str] = triage_rules.get("high_severity_keywords", [])
        low_value_threshold: float | None = triage_rules.get("low_value_threshold")

        triage_category = "Standard" # Default category

        # Check for high severity keywords
        if any(keyword.lower() in claim_description for keyword in high_severity_keywords):
            triage_category = "HighSeverity"
            self.logger.info(f"Claim {claim_id} triaged as HighSeverity based on keywords.")
        
        # Check for low value (only if not already high severity)
        elif low_value_threshold is not None and claimed_amount is not None:
            try:
                if float(claimed_amount) <= low_value_threshold:
                    triage_category = "LowValue"
                    self.logger.info(f"Claim {claim_id} triaged as LowValue based on amount ({claimed_amount}).")
            except ValueError:
                self.logger.warning(f"Invalid claimed_amount format for claim {claim_id}: {claimed_amount}. Cannot apply low value rule.")

        if triage_category == "Standard":
             self.logger.info(f"Claim {claim_id} triaged as Standard.")

        self.log_audit(institution_id, "claim_triaged", {"claim_id": claim_id, "category": triage_category})

        # Return original data enriched with the triage category
        data["triage_category"] = triage_category
        return data

