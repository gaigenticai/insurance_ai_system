from agents.config_agent import ConfigAgent
from agents.claims.claim_triage_agent import ClaimTriageAgent
from agents.claims.policy_verifier_agent import PolicyVerifierAgent
from agents.claims.fraud_detector_agent import FraudDetectorAgent
from agents.claims.auto_resolution_agent import AutoResolutionAgent
from agents.claims.escalation_agent import EscalationAgent
from agents.claims.ethics_logger_agent import EthicsLoggerAgent
from ai_services.ai_agents import AIClaimsAgent
from typing import Dict, Any
import logging
import json # For ethics logging data
import asyncio
# Trigger redeploy

class ClaimsFlow:
    """Orchestrates the automated claims processing workflow."""

    def __init__(self, config_agent: ConfigAgent):
        self.config_agent = config_agent
        self.logger = logging.getLogger("ClaimsFlow")
        # Instantiate agents
        self.triage_agent = ClaimTriageAgent(config_agent)
        self.verifier_agent = PolicyVerifierAgent(config_agent)
        self.fraud_agent = FraudDetectorAgent(config_agent)
        self.resolution_agent = AutoResolutionAgent(config_agent)
        self.escalation_agent = EscalationAgent(config_agent)
        self.ethics_agent = EthicsLoggerAgent(config_agent)
        self.ai_agent = AIClaimsAgent(config_agent)
        self.logger.info("ClaimsFlow initialized with all required agents including AI agent.")

    def run(self, claim_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Runs the full claims processing flow for a given claim.

        Args:
            claim_data: The initial claim data.
                        Requires "claim_id", "policy_id", "claimed_amount", "claim_description", "claim_date".
                        Example: {"claim_id": "CLM456", "policy_id": "POLICY_ACTIVE_001", ...}
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the final claim status and outcome.
            Example: {"claim_id": "CLM456", "status": "Processed", 
                      "resolution": "AutoApproved"/"Escalated", 
                      "payout_amount": ..., "escalation_reason": "..."}
        """
        claim_id = claim_data.get("claim_id")
        if not claim_id:
            self.logger.error("Missing claim_id in claim data. Aborting flow.")
            return {"status": "Error", "message": "Missing claim_id"}

        self.logger.info(f"Starting claims flow for claim {claim_id}, institution {institution_id}.")
        
        # Use a single dictionary to pass data between agents, enriching it at each step
        current_claim_state = claim_data.copy()

        # 1. Triage Claim
        current_claim_state = self.triage_agent.execute(current_claim_state, institution_id)

        # 2. Verify Policy
        current_claim_state = self.verifier_agent.execute(current_claim_state, institution_id)
        if not current_claim_state.get("policy_valid", False):
            self.logger.warning(f"Claim {claim_id} processing stopped due to invalid policy.")
            # Log ethical consideration for denial based on policy
            self.ethics_agent.execute({
                "claim_id": claim_id,
                "decision_point": "DenialDueToPolicy",
                "reasoning": current_claim_state.get("verification_notes", "Policy invalid or expired."),
                "relevant_data": {"policy_id": current_claim_state.get("policy_id"), "claim_date": current_claim_state.get("claim_date")},
                "triggering_agent": "PolicyVerifierAgent"
            }, institution_id)
            return {
                "claim_id": claim_id,
                "status": "Processed",
                "resolution": "Denied",
                "payout_amount": 0,
                "escalation_reason": "Policy invalid."
            }

        # 3. AI-Enhanced Analysis
        ai_result = None
        try:
            ai_result = asyncio.run(self._process_with_ai(current_claim_state, institution_id))
            current_claim_state['ai_analysis'] = ai_result
            self.logger.info(f"AI analysis completed for claim {claim_id}")
        except Exception as e:
            self.logger.warning(f"AI analysis failed for claim {claim_id}: {str(e)}")

        # 4. Detect Fraud (enhanced with AI insights)
        current_claim_state = self.fraud_agent.execute(current_claim_state, institution_id)

        # 5. Attempt Auto-Resolution (enhanced with AI insights)
        current_claim_state = self.resolution_agent.execute(current_claim_state, institution_id)

        # 6. Check for Escalation
        # Pass fraud flags to escalation agent
        current_claim_state = self.escalation_agent.execute(current_claim_state, institution_id)

        # 7. Ethics Logging for key decisions (Escalation / AutoApproval / Denial implicitly handled above)
        if current_claim_state.get("escalate"): 
             self.ethics_agent.execute({
                "claim_id": claim_id,
                "decision_point": "EscalationToHuman",
                "reasoning": current_claim_state.get("escalation_reason", "Requires manual review."),
                "relevant_data": {
                    "triage": current_claim_state.get("triage_category"), 
                    "fraud_flags": current_claim_state.get("fraud_flags"),
                    "resolution_status": current_claim_state.get("resolution_status")
                },
                "triggering_agent": "EscalationAgent"
            }, institution_id)
        elif current_claim_state.get("resolution_status") == "AutoApproved":
             self.ethics_agent.execute({
                "claim_id": claim_id,
                "decision_point": "AutoApproval",
                "reasoning": current_claim_state.get("resolution_notes", "Claim met auto-approval criteria."),
                "relevant_data": {
                    "amount": current_claim_state.get("claimed_amount"), 
                    "payout": current_claim_state.get("resolution_amount")
                },
                "triggering_agent": "AutoResolutionAgent"
            }, institution_id)

        # 7. Final Output Preparation
        final_status = "Processed"
        resolution_outcome = "Escalated" if current_claim_state.get("escalate") else current_claim_state.get("resolution_status", "NeedsReview")
        payout = current_claim_state.get("resolution_amount") if resolution_outcome == "AutoApproved" else 0
        reason = current_claim_state.get("escalation_reason") if resolution_outcome == "Escalated" else current_claim_state.get("resolution_notes", "")

        self.logger.info(f"Claims flow completed for claim {claim_id}. Final Resolution: {resolution_outcome}, Payout: {payout}")
        return {
            "claim_id": claim_id,
            "status": final_status,
            "resolution": resolution_outcome,
            "payout_amount": payout,
            "escalation_reason": reason if resolution_outcome == "Escalated" else None,
            "ai_insights": ai_result
        }
    
    async def _process_with_ai(self, claim_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """
        Process claim using AI-enhanced analysis.
        
        Args:
            claim_data: Claim data dictionary
            institution_id: Institution identifier
            
        Returns:
            AI analysis result
        """
        return await self.ai_agent.execute(claim_data, institution_id)

# Example Usage (for testing)
# if __name__ == "__main__":
#     config = ConfigAgent()
#     flow = ClaimsFlow(config)
# 
#     # Example 1: Simple, low-value, valid claim -> AutoApproved
#     claim_low_value = {
#         "claim_id": "CLM-AUTO-001",
#         "policy_id": "POLICY_ACTIVE_001",
#         "claimed_amount": 450, # Below threshold 500
#         "claim_description": "Minor windshield chip repair",
#         "claim_date": "2025-05-28"
#     }
#     result_low_value = flow.run(claim_low_value, "institution_a")
#     print("\n--- Low Value Claim Result ---")
#     print(json.dumps(result_low_value, indent=2))
# 
#     # Example 2: High severity claim -> Escalated
#     claim_high_severity = {
#         "claim_id": "CLM-HIGH-002",
#         "policy_id": "POLICY_ACTIVE_001",
#         "claimed_amount": 8000,
#         "claim_description": "Major structural damage from fire", # High severity keyword
#         "claim_date": "2025-05-29"
#     }
#     result_high_severity = flow.run(claim_high_severity, "institution_a")
#     print("\n--- High Severity Claim Result ---")
#     print(json.dumps(result_high_severity, indent=2))
# 
#     # Example 3: Claim with expired policy -> Denied
#     claim_expired_policy = {
#         "claim_id": "CLM-EXPIRED-003",
#         "policy_id": "POLICY_EXPIRED_002", # Expired policy
#         "claimed_amount": 1200,
#         "claim_description": "Water damage in basement",
#         "claim_date": "2025-05-30"
#     }
#     result_expired_policy = flow.run(claim_expired_policy, "institution_a")
#     print("\n--- Expired Policy Claim Result ---")
#     print(json.dumps(result_expired_policy, indent=2))
# 
#     # Example 4: Claim with potential fraud flag -> Escalated
#     claim_fraud_flag = {
#         "claim_id": "CLM-FRAUD-004",
#         "policy_id": "POLICY_ACTIVE_003", # Policy with recent claims
#         "claimed_amount": 250, # Below auto-approve threshold
#         "claim_description": "Another small dent repair",
#         "claim_date": "2025-05-31"
#     }
#     result_fraud_flag = flow.run(claim_fraud_flag, "institution_a")
#     print("\n--- Fraud Flag Claim Result ---")
#     print(json.dumps(result_fraud_flag, indent=2))
# 
#     # Example 5: Standard claim, above auto-approve -> Escalated
#     claim_standard = {
#         "claim_id": "CLM-STD-005",
#         "policy_id": "POLICY_ACTIVE_001",
#         "claimed_amount": 750, # Above auto-approve, below high value
#         "claim_description": "Rear bumper replacement",
#         "claim_date": "2025-06-01"
#     }
#     result_standard = flow.run(claim_standard, "institution_a")
#     print("\n--- Standard Escalation Claim Result ---")
#     print(json.dumps(result_standard, indent=2))

