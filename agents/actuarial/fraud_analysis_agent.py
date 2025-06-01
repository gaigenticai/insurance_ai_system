from agents.base.base_agent import BaseAgent
from typing import Any, Dict, List

class FraudAnalysisAgent(BaseAgent):
    """Analyzes normalized actuarial data for potential fraud indicators."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="FraudAnalysisAgent", config_agent=config_agent)
        # In a real system, this would involve more sophisticated anomaly detection or ML models.

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Identifies potential fraud indicators in the claims and policy data.

        Args:
            data: Dictionary containing the normalized actuarial data.
                  Expected keys: "normalized_data" (output from DataNormalizerAgent).
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing identified fraud insights.
            Example: {"fraud_insights": {"flagged_claims_count": ..., "suspicious_patterns": [...]}}
        """
        self.logger.info(f"Executing fraud analysis for institution {institution_id}.")
        
        normalized_data = data.get("normalized_data")
        if not normalized_data or data.get("validation_status") in ["failed", "partial"]:
            self.logger.warning(f"Skipping fraud analysis due to missing or invalid normalized data for institution {institution_id}.")
            self.log_audit(institution_id, "fraud_analysis_skipped_invalid_data", {})
            return {"fraud_insights": None, "status": "skipped"}

        claims_data = normalized_data.get("claims_data", [])
        # policy_data = normalized_data.get("policy_data", []) # Could analyze policy data too

        # --- Fraud Indicator Logic --- 
        flagged_claims_count = 0
        suspicious_patterns = []
        high_value_open_claims = []

        # Indicator 1: Count claims already flagged during processing (example)
        for claim in claims_data:
            if claim.get("potential_fraud_flag") == True: # Check for explicit flags
                flagged_claims_count += 1
                suspicious_patterns.append(f'Claim {claim.get("claim_id")} previously flagged for potential fraud.')

        # Indicator 2: Identify high-value open claims (could be a simple rule)
        # Threshold could be configurable
        high_value_threshold = 10000 # Example threshold
        for claim in claims_data:
            if claim.get("status") == "Open" and claim.get("reserve_amount", 0) > high_value_threshold:
                 pattern = f'High-value open claim {claim.get("claim_id")} with reserve ${claim.get("reserve_amount")}.'
                 high_value_open_claims.append(pattern)
                 # Optionally add to main suspicious_patterns list
                 # suspicious_patterns.append(pattern) 
        
        if high_value_open_claims:
             self.logger.info(f"Found {len(high_value_open_claims)} high-value open claims potentially needing review.")
             # Add a summary pattern
             suspicious_patterns.append(f"Identified {len(high_value_open_claims)} open claims with reserves > ${high_value_threshold}.")

        # Indicator 3: Look for unusual claim frequency by policy (example)
        # (Could reuse logic similar to FraudDetectorAgent but on the whole dataset)
        # claims_per_policy = defaultdict(int)
        # for claim in claims_data:
        #     claims_per_policy[claim.get("policy_id")] += 1
        # frequent_claim_policies = {pid: count for pid, count in claims_per_policy.items() if count > 2} # Example threshold
        # if frequent_claim_policies:
        #     suspicious_patterns.append(f"Policies with high claim frequency detected: {list(frequent_claim_policies.keys())}")

        # --- Consolidate Insights --- 
        fraud_insights = {
            "flagged_claims_count": flagged_claims_count,
            "suspicious_patterns_found": suspicious_patterns,
            "high_value_open_claims_details": high_value_open_claims # Keep detailed list separate if needed
        }

        self.logger.info(f"Fraud analysis completed for institution {institution_id}. Found {flagged_claims_count} flagged claims and {len(suspicious_patterns)} suspicious patterns.")
        self.log_audit(institution_id, "fraud_analysis_completed", {"flagged_claims_count": flagged_claims_count, "patterns_found": len(suspicious_patterns)})

        return {"fraud_insights": fraud_insights, "status": "success"}

