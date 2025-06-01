from ..base.base_agent import BaseAgent
from typing import Any, Dict, List
import datetime

class FraudDetectorAgent(BaseAgent):
    """Applies simple fraud detection rules based on claim data and configured settings."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="FraudDetectorAgent", config_agent=config_agent)
        # In a real system, this might involve more complex checks, external databases, or ML models.
        # Mock history for demonstration
        self.mock_claim_history = {
            "POLICY_ACTIVE_001": [
                {"claim_id": "CLAIM_OLD_001", "claim_date": "2025-05-10", "amount": 300},
            ],
             "POLICY_ACTIVE_003": [
                {"claim_id": "CLAIM_OLD_002", "claim_date": "2025-05-20", "amount": 150},
                {"claim_id": "CLAIM_OLD_003", "claim_date": "2025-05-25", "amount": 200}, # Multiple recent claims
            ]
        }

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Checks for potential fraud flags based on configured rules.

        Args:
            data: Dictionary containing claim details.
                  Expected keys: "claim_id", "policy_id", "claim_date" (ISO YYYY-MM-DD), "claim_description".
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the original claim data plus a list of detected fraud flags.
            Example: {"claim_id": "...", ..., "fraud_flags": ["MultipleClaimsRecently", "SuspiciousKeyword"]}
        """
        claim_id = data.get("claim_id", "unknown")
        policy_id = data.get("policy_id")
        claim_date_str = data.get("claim_date", datetime.date.today().isoformat())
        # claim_description = data.get("claim_description", "").lower()
        self.logger.info(f"Executing fraud detection check for claim {claim_id}, institution {institution_id}.")

        fraud_flags: List[str] = []
        claims_config = self.config_agent.get_claims_rules(institution_id)
        fraud_rules = claims_config.get("fraud_rules", {})
        multiple_claims_window_days: int = fraud_rules.get("multiple_claims_window_days", 30)
        # suspicious_keywords: List[str] = fraud_rules.get("suspicious_activity_flags", []) # Example: could check description

        # --- Fraud Rule: Multiple Claims Recently --- 
        if policy_id and policy_id in self.mock_claim_history:
            try:
                claim_date = datetime.date.fromisoformat(claim_date_str)
                recent_claims_count = 0
                for past_claim in self.mock_claim_history[policy_id]:
                    past_claim_date = datetime.date.fromisoformat(past_claim["claim_date"])
                    if (claim_date - past_claim_date).days <= multiple_claims_window_days:
                        recent_claims_count += 1
                
                # Check if the *current* claim makes it multiple within the window
                # (e.g., if there was already 1 recent claim, this is the 2nd)
                if recent_claims_count >= 1: # Threshold could be configurable (e.g., > 1)
                    flag = "MultipleClaimsRecently"
                    fraud_flags.append(flag)
                    self.logger.warning(f"Fraud flag 	'{flag}	' triggered for claim {claim_id} (Policy: {policy_id}). Found {recent_claims_count} other claims within {multiple_claims_window_days} days.")

            except (ValueError, TypeError) as e:
                self.logger.error(f"Error processing dates for fraud check on claim {claim_id}: {e}")

        # --- Fraud Rule: Suspicious Keywords/Patterns (Example) ---
        # This is highly dependent on the domain and data available.
        # Example: Check if description contains certain phrases (from config)
        # suspicious_flags_found = [flag for flag in suspicious_keywords if flag.lower() in claim_description]
        # if suspicious_flags_found:
        #     fraud_flags.extend(suspicious_flags_found)
        #     self.logger.warning(f"Fraud flags triggered by keywords for claim {claim_id}: {suspicious_flags_found}")

        # --- Add more rules as needed --- 
        # e.g., Check against known fraud lists, analyze claim patterns, etc.

        if fraud_flags:
            self.log_audit(institution_id, "fraud_check_flags_found", {"claim_id": claim_id, "flags": fraud_flags})
        else:
            self.logger.info(f"No fraud flags detected for claim {claim_id}.")
            self.log_audit(institution_id, "fraud_check_no_flags", {"claim_id": claim_id})

        data["fraud_flags"] = fraud_flags
        return data

