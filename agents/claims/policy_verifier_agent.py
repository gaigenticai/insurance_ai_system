from agents.base.base_agent import BaseAgent
from typing import Any, Dict
import datetime

class PolicyVerifierAgent(BaseAgent):
    """Verifies claim eligibility against policy data (simulated)."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="PolicyVerifierAgent", config_agent=config_agent)
        # In a real system, this agent would connect to a policy database or API.
        # Here, we simulate a simple policy store.
        self.mock_policy_store = {
            "POLICY_ACTIVE_001": {"status": "active", "coverage_limit": 5000, "deductible": 500, "valid_until": "2026-12-31"},
            "POLICY_EXPIRED_002": {"status": "expired", "coverage_limit": 10000, "deductible": 1000, "valid_until": "2023-01-01"},
            "POLICY_ACTIVE_003": {"status": "active", "coverage_limit": 1000, "deductible": 100, "valid_until": "2025-08-15"}
        }

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Checks if the policy associated with the claim is active and valid.

        Args:
            data: Dictionary containing claim details, including the policy ID.
                  Expected keys: "claim_id", "policy_id", "claim_date" (optional, ISO format YYYY-MM-DD).
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the original claim data plus policy verification status.
            Example: {"claim_id": "...", ..., "policy_valid": True/False, "policy_details": {...}, "verification_notes": "..."}
        """
        claim_id = data.get("claim_id", "unknown")
        policy_id = data.get("policy_id")
        claim_date_str = data.get("claim_date", datetime.date.today().isoformat())
        self.logger.info(f"Executing policy verification for claim {claim_id}, policy {policy_id}, institution {institution_id}.")

        if not policy_id:
            self.logger.error(f"Missing policy_id for claim {claim_id}. Cannot verify policy.")
            self.log_audit(institution_id, "policy_verification_failed_missing_id", {"claim_id": claim_id})
            data["policy_valid"] = False
            data["policy_details"] = None
            data["verification_notes"] = "Missing policy ID in claim data."
            return data

        policy_details = self.mock_policy_store.get(policy_id)

        if not policy_details:
            self.logger.warning(f"Policy {policy_id} not found in mock store for claim {claim_id}.")
            self.log_audit(institution_id, "policy_verification_failed_not_found", {"claim_id": claim_id, "policy_id": policy_id})
            data["policy_valid"] = False
            data["policy_details"] = None
            data["verification_notes"] = f"Policy ID {policy_id} not found."
            return data

        # Check policy status
        is_active = policy_details.get("status") == "active"
        
        # Check policy validity date
        is_date_valid = False
        notes = []
        try:
            valid_until_date = datetime.date.fromisoformat(policy_details.get("valid_until", ""))
            claim_date = datetime.date.fromisoformat(claim_date_str)
            if claim_date <= valid_until_date:
                is_date_valid = True
            else:
                notes.append(f'Policy expired on {policy_details.get("valid_until")}, claim date is {claim_date_str}.')
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error parsing dates for policy {policy_id}, claim {claim_id}: {e}")
            notes.append(f'Could not validate policy dates due to format error ({policy_details.get("valid_until")}, {claim_date_str}).')

        policy_valid = is_active and is_date_valid
        if not is_active:(f'Policy status is \'{policy_details.get("status")}\'.')

        verification_notes = "Policy is active and valid for claim date." if policy_valid else " | ".join(notes)
        
        self.logger.info(f"Policy verification completed for claim {claim_id}. Policy valid: {policy_valid}. Notes: {verification_notes}")
        self.log_audit(institution_id, "policy_verification_completed", {"claim_id": claim_id, "policy_id": policy_id, "is_valid": policy_valid, "notes": verification_notes})

        data["policy_valid"] = policy_valid
        data["policy_details"] = policy_details # Return fetched details
        data["verification_notes"] = verification_notes
        return data

