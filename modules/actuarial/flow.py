from agents.config_agent import ConfigAgent
from agents.actuarial.data_normalizer_agent import DataNormalizerAgent
from agents.actuarial.trend_analyzer_agent import TrendAnalyzerAgent
from agents.actuarial.benchmark_comparison_agent import BenchmarkComparisonAgent
from agents.actuarial.fraud_analysis_agent import FraudAnalysisAgent
from agents.actuarial.report_generator_agent import ReportGeneratorAgent
from ai_services.ai_agents import AIActuarialAgent
from typing import Dict, Any
import logging
import json # For example usage
import asyncio

class ActuarialFlow:
    """Orchestrates the actuarial analysis and reporting process."""

    def __init__(self, config_agent: ConfigAgent):
        self.config_agent = config_agent
        self.logger = logging.getLogger("ActuarialFlow")
        # Instantiate agents
        self.normalizer_agent = DataNormalizerAgent(config_agent)
        self.analyzer_agent = TrendAnalyzerAgent(config_agent)
        self.benchmark_agent = BenchmarkComparisonAgent(config_agent)
        self.fraud_agent = FraudAnalysisAgent(config_agent)
        self.reporter_agent = ReportGeneratorAgent(config_agent)
        self.ai_agent = AIActuarialAgent(config_agent)
        self.logger.info("ActuarialFlow initialized with all required agents including AI agent.")


    def calculate_risk_model(self, data_source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wrapper method to perform risk modeling using the actuarial pipeline.
        Args:
            data_source (dict): Dictionary containing input data or file path.
        Returns:
            dict: Output from the full actuarial analysis flow.
        """
        institution_id = data_source.get("institution_id", "unknown")
        return self.run(data_source, institution_id)



    def run(self, data_source: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Runs the full actuarial analysis and reporting flow.

        Args:
            data_source: Dictionary specifying the data source.
                         Expected keys: "data_path" (path to JSON file) or "raw_data".
                         Example: {"data_path": "/path/to/sample_actuarial_input.json"}
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the paths to the generated reports or an error status.
            Example: {"status": "Success"/"Failed"/"Partial", "report_paths": {...}, "errors": {...}}
        """
        self.logger.info(f"Starting actuarial flow for institution {institution_id}.")

        # 1. Normalize Data
        normalization_result = self.normalizer_agent.execute(data_source, institution_id)
        if normalization_result.get("validation_status") == "failed":
            self.logger.error(f"Actuarial flow failed at data normalization for institution {institution_id}.")
            return {"status": "Failed", "message": "Data normalization failed.", "errors": normalization_result.get("errors")}
        
        # Pass normalized data and status to subsequent agents
        current_analysis_data = {
            "normalized_data": normalization_result.get("normalized_data"),
            "validation_status": normalization_result.get("validation_status") 
        }

        # 2. Analyze Trends
        analysis_result = self.analyzer_agent.execute(current_analysis_data, institution_id)
        if analysis_result.get("status") != "success":
             self.logger.warning(f"Trend analysis skipped or failed for institution {institution_id}. Report may be incomplete.")
        current_analysis_data["analysis_results"] = analysis_result.get("analysis_results")

        # 3. AI-Enhanced Analysis
        ai_result = None
        try:
            ai_result = asyncio.run(self._process_with_ai(current_analysis_data, institution_id))
            current_analysis_data['ai_analysis'] = ai_result
            self.logger.info(f"AI actuarial analysis completed for institution {institution_id}")
        except Exception as e:
            self.logger.warning(f"AI actuarial analysis failed for institution {institution_id}: {str(e)}")

        # 4. Compare Benchmarks
        benchmark_result = self.benchmark_agent.execute(current_analysis_data, institution_id)
        if benchmark_result.get("status") != "success":
             self.logger.warning(f"Benchmark comparison skipped or failed for institution {institution_id}. Report may be incomplete.")
        current_analysis_data["benchmark_comparison"] = benchmark_result.get("benchmark_comparison")

        # 5. Analyze Fraud Indicators
        fraud_result = self.fraud_agent.execute(current_analysis_data, institution_id)
        if fraud_result.get("status") != "success":
             self.logger.warning(f"Fraud analysis skipped or failed for institution {institution_id}. Report may be incomplete.")
        current_analysis_data["fraud_insights"] = fraud_result.get("fraud_insights")

        # 6. Generate Reports
        report_result = self.reporter_agent.execute(current_analysis_data, institution_id)

        final_status = report_result.get("status", "failed").capitalize()
        self.logger.info(f"Actuarial flow completed for institution {institution_id}. Final Status: {final_status}")

        return {
            "status": final_status,
            "report_paths": report_result.get("report_paths"),
            "errors": report_result.get("errors"),
            "ai_insights": ai_result
        }
    
    async def _process_with_ai(self, analysis_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """
        Process actuarial data using AI-enhanced analysis.
        
        Args:
            analysis_data: Analysis data dictionary
            institution_id: Institution identifier
            
        Returns:
            AI analysis result
        """
        return await self.ai_agent.execute(analysis_data, institution_id)

# Example Usage (for testing)
# if __name__ == "__main__":
#     config = ConfigAgent()
#     flow = ActuarialFlow(config)
# 
#     # Run the flow using the sample data file
#     data_source_info = {
#         "data_path": "/home/ubuntu/insurance_ai_system/data/sample_actuarial_input.json"
#     }
#     result = flow.run(data_source_info, "institution_a")
# 
#     print("\n--- Actuarial Flow Result ---")
#     print(json.dumps(result, indent=2))
# 
#     # Optionally, read and print the generated markdown report
#     if result.get("status") in ["Success", "Partial"] and result.get("report_paths", {}).get("markdown"):
#         try:
#             with open(result["report_paths"]["markdown"], 'r') as f_report:
#                 print("\n--- Generated Markdown Report ---")
#                 print(f_report.read())
#         except Exception as e:
#             print(f"\nError reading generated report: {e}")

