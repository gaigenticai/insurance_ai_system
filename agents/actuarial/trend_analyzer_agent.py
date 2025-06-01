from ...base.base_agent import BaseAgent
from typing import Any, Dict, List
import pandas as pd
from collections import defaultdict

class TrendAnalyzerAgent(BaseAgent):
    """Performs basic trend analysis on normalized actuarial data."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="TrendAnalyzerAgent", config_agent=config_agent)
        # In a real system, analysis could be much more complex (time series, ML models)

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Calculates key metrics and summaries from the normalized data.

        Args:
            data: Dictionary containing the normalized actuarial data.
                  Expected keys: "normalized_data" (output from DataNormalizerAgent).
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the analysis results.
            Example: {"analysis_results": {"kpis": {...}, "segment_analysis": {...}}}
        """
        self.logger.info(f"Executing trend analysis for institution {institution_id}.")
        
        normalized_data = data.get("normalized_data")
        if not normalized_data or data.get("validation_status") in ["failed", "partial"]:
            self.logger.warning(f"Skipping trend analysis due to missing or invalid normalized data for institution {institution_id}.")
            self.log_audit(institution_id, "trend_analysis_skipped_invalid_data", {})
            return {"analysis_results": None, "status": "skipped"}

        policy_data = normalized_data.get("policy_data", [])
        claims_data = normalized_data.get("claims_data", [])
        financial_data = normalized_data.get("financial_data", {})
        actuarial_settings = self.config_agent.get_actuarial_settings(institution_id)
        reporting_segments = actuarial_settings.get("reporting_segments", ["geography", "product_line"]) # Default segments

        # --- Basic KPI Calculation --- 
        kpis = {}
        try:
            # Use financial data if available
            earned_premium = financial_data.get("earned_premium", 0)
            incurred_losses = financial_data.get("incurred_losses", 0)
            
            # Fallback: Calculate from raw data if financial aggregates missing (less accurate)
            if earned_premium == 0 and policy_data:
                 earned_premium = sum(p.get("premium_amount", 0) for p in policy_data if p.get("status") == "active") # Simplified premium calculation
                 self.logger.warning("Financial data missing earned_premium, calculating approximation from active policies.")
            
            if incurred_losses == 0 and claims_data:
                 incurred_losses = sum(c.get("paid_amount", 0) + c.get("reserve_amount", 0) for c in claims_data) # Simplified incurred loss
                 self.logger.warning("Financial data missing incurred_losses, calculating approximation from claims data.")

            kpis["total_earned_premium"] = earned_premium
            kpis["total_incurred_losses"] = incurred_losses
            kpis["loss_ratio"] = (incurred_losses / earned_premium) if earned_premium else 0
            kpis["active_policy_count"] = sum(1 for p in policy_data if p.get("status") == "active")
            kpis["open_claims_count"] = sum(1 for c in claims_data if c.get("status") == "Open")
            kpis["total_claims_paid"] = sum(c.get("paid_amount", 0) for c in claims_data if c.get("status") == "Closed")

        except Exception as e:
            self.logger.error(f"Error calculating basic KPIs for institution {institution_id}: {e}")
            self.log_audit(institution_id, "trend_analysis_kpi_error", {"error": str(e)})
            # Continue with segment analysis if possible

        # --- Segment Analysis --- 
        segment_analysis = defaultdict(lambda: defaultdict(lambda: {"policy_count": 0, "premium": 0, "claim_count": 0, "paid_losses": 0}))
        
        # Use pandas for easier aggregation if available and data is large enough
        # For simplicity here, using basic loops
        
        valid_segments = [seg for seg in reporting_segments if seg in policy_data[0] and seg in claims_data[0]] if policy_data and claims_data else []
        if not valid_segments:
             self.logger.warning(f"Configured reporting segments {reporting_segments} not found in data. Skipping segment analysis.")
        else:
            try:
                # Aggregate Policy Data by Segment
                for policy in policy_data:
                    if policy.get("status") == "active": # Analyze active policies
                        for segment_key in valid_segments:
                            segment_value = policy.get(segment_key, "Unknown")
                            segment_analysis[segment_key][segment_value]["policy_count"] += 1
                            segment_analysis[segment_key][segment_value]["premium"] += policy.get("premium_amount", 0)
                
                # Aggregate Claims Data by Segment
                for claim in claims_data:
                     for segment_key in valid_segments:
                        segment_value = claim.get(segment_key, "Unknown")
                        segment_analysis[segment_key][segment_value]["claim_count"] += 1
                        segment_analysis[segment_key][segment_value]["paid_losses"] += claim.get("paid_amount", 0)
                
                # Calculate Loss Ratio per segment
                for segment_key in segment_analysis:
                    for segment_value in segment_analysis[segment_key]:
                        premium = segment_analysis[segment_key][segment_value]["premium"]
                        paid_losses = segment_analysis[segment_key][segment_value]["paid_losses"]
                        # Note: This uses paid losses / premium, a simplified loss ratio for this example
                        segment_analysis[segment_key][segment_value]["segment_loss_ratio"] = (paid_losses / premium) if premium else 0

            except Exception as e:
                self.logger.error(f"Error during segment analysis for institution {institution_id}: {e}")
                self.log_audit(institution_id, "trend_analysis_segment_error", {"error": str(e)})
                segment_analysis = {} # Clear partial results on error

        analysis_results = {
            "kpis": kpis,
            "segment_analysis": dict(segment_analysis) # Convert defaultdict back to dict for output
        }

        self.logger.info(f"Trend analysis completed for institution {institution_id}. Calculated {len(kpis)} KPIs and analyzed {len(segment_analysis)} segments.")
        self.log_audit(institution_id, "trend_analysis_completed", {"kpi_count": len(kpis), "segment_count": len(segment_analysis)})

        return {"analysis_results": analysis_results, "status": "success"}

