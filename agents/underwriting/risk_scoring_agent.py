from ..base.base_agent import BaseAgent
from typing import Any, Dict

class RiskScoringAgent(BaseAgent):
    """Scores underwriting risk based on applicant data and institution-specific rules."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="RiskScoringAgent", config_agent=config_agent)

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Applies configured risk rules to applicant data to determine underwriting decision.

        Args:
            data: Dictionary containing validated and potentially OCR-extracted applicant data.
                  Expected keys might include: "applicant_data", "extracted_data", "applicant_id".
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the underwriting decision and rationale.
            Example: {"decision": "Approve"/"Deny"/"Modify Terms", "rationale": "...", "score": ...}
        """
        self.logger.info(f"Executing risk scoring for institution {institution_id}.")
        applicant_id = data.get("applicant_id", "unknown")
        # Combine base applicant data with any OCR extracted data
        applicant_info = {**data.get("applicant_data", {}), **data.get("extracted_data", {})}

        rules = self.config_agent.get_underwriting_rules(institution_id)
        if not rules:
            self.logger.error(f"No underwriting rules found for institution {institution_id}. Cannot score risk.")
            self.log_audit(institution_id, "risk_scoring_failed_no_rules", {"applicant_id": applicant_id})
            # Defaulting to Deny if rules are missing - requires careful consideration in production
            return {"decision": "Deny", "rationale": "Configuration error: Missing underwriting rules.", "score": None}

        # --- Production-Grade Rule Evaluation Logic --- 
        # This is a simplified example. Real systems would use more complex models, 
        # potentially external rule engines, or ML models.
        score = 100  # Start with a base score
        rationale_points = []

        # Rule: Minimum Credit Score
        min_score = rules.get("min_credit_score")
        applicant_score = applicant_info.get("credit_score")
        if min_score is not None and applicant_score is not None:
            try:
                if int(applicant_score) < min_score:
                    score -= 50
                    rationale_points.append(f"Credit score ({applicant_score}) below minimum ({min_score}).")
            except ValueError:
                 self.logger.warning(f"Invalid credit score format for applicant {applicant_id}: {applicant_score}")
                 rationale_points.append(f"Could not validate credit score format ({applicant_score}).")

        # Rule: Max Debt-to-Income Ratio
        max_dti = rules.get("max_debt_to_income_ratio")
        applicant_dti = applicant_info.get("debt_to_income_ratio") # Assuming this field exists
        if max_dti is not None and applicant_dti is not None:
             try:
                if float(applicant_dti) > max_dti:
                    score -= 30
                    rationale_points.append(f"DTI ratio ({applicant_dti}) exceeds maximum ({max_dti}).")
             except ValueError:
                 self.logger.warning(f"Invalid DTI format for applicant {applicant_id}: {applicant_dti}")
                 rationale_points.append(f"Could not validate DTI format ({applicant_dti}).")

        # Rule: High-Risk Locations
        high_risk_locations = rules.get("high_risk_locations", [])
        applicant_location = applicant_info.get("address_location_tag") # Assuming a field like this exists
        if applicant_location and applicant_location in high_risk_locations:
            score -= 20
            rationale_points.append(f"Property located in high-risk area: {applicant_location}.")

        # Rule: Auto-Approve Age Range (Simplified example - might adjust terms instead)
        # This rule is simplistic; real systems might use age differently.
        # auto_approve_age = rules.get("auto_approve_age_range", [])
        # applicant_age = applicant_info.get("age") # Assuming age exists
        # if len(auto_approve_age) == 2 and applicant_age is not None:
        #     try:
        #         if not (auto_approve_age[0] <= int(applicant_age) <= auto_approve_age[1]):
        #             # Outside optimal range, maybe slightly lower score
        #             score -= 10 
        #             rationale_points.append(f"Applicant age ({applicant_age}) outside optimal range {auto_approve_age}.")
        #     except ValueError:
        #          self.logger.warning(f"Invalid age format for applicant {applicant_id}: {applicant_age}")

        # --- Decision Logic --- 
        # Thresholds could also be configurable
        decision = "Deny" # Default
        if score >= 80:
            decision = "Approve"
        elif score >= 50:
            decision = "Modify Terms" # Requires further definition of what terms
        else:
            decision = "Deny"

        final_rationale = " | ".join(rationale_points) if rationale_points else "Applicant meets standard criteria."
        if decision == "Deny" and not rationale_points:
             final_rationale = "Score below threshold based on overall profile."
        elif decision == "Modify Terms" and not rationale_points:
             final_rationale = "Score indicates need for modified terms based on overall profile."

        self.logger.info(f"Risk scoring completed for applicant {applicant_id}. Score: {score}, Decision: {decision}")
        self.log_audit(institution_id, "risk_scoring_completed", {"applicant_id": applicant_id, "score": score, "decision": decision, "rationale": final_rationale})

        return {"decision": decision, "rationale": final_rationale, "score": score}

