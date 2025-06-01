from agents.base.base_agent import BaseAgent
from typing import Any, Dict

class BenchmarkComparisonAgent(BaseAgent):
    """Compares calculated KPIs against benchmarks defined in the configuration."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="BenchmarkComparisonAgent", config_agent=config_agent)

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Compares analysis results (KPIs) against configured benchmarks.

        Args:
            data: Dictionary containing the analysis results.
                  Expected keys: "analysis_results" (output from TrendAnalyzerAgent).
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the comparison results.
            Example: {"benchmark_comparison": {"kpi_name": {"value": ..., "benchmark": ..., "status": "Above"/"Below"/"Met"/"N/A"}, ...}}
        """
        self.logger.info(f"Executing benchmark comparison for institution {institution_id}.")
        
        analysis_results = data.get("analysis_results")
        if not analysis_results or not analysis_results.get("kpis"):
            self.logger.warning(f"Skipping benchmark comparison due to missing analysis results/KPIs for institution {institution_id}.")
            self.log_audit(institution_id, "benchmark_comparison_skipped_no_kpis", {})
            return {"benchmark_comparison": None, "status": "skipped"}

        kpis = analysis_results.get("kpis", {})
        actuarial_settings = self.config_agent.get_actuarial_settings(institution_id)
        benchmarks = actuarial_settings.get("benchmarks", {})

        if not benchmarks:
            self.logger.warning(f"No benchmarks configured for institution {institution_id}. Skipping comparison.")
            self.log_audit(institution_id, "benchmark_comparison_skipped_no_config", {})
            return {"benchmark_comparison": {kpi: {"value": val, "benchmark": None, "status": "N/A"} for kpi, val in kpis.items()}, "status": "no_benchmarks"}

        comparison_results = {}
        for kpi_name, kpi_value in kpis.items():
            benchmark_value = benchmarks.get(kpi_name) # Or map KPI names to benchmark names if different
            status = "N/A"
            
            if benchmark_value is not None:
                try:
                    # Simple comparison logic (can be expanded based on KPI meaning)
                    # Assuming lower is better for loss_ratio, higher for others (needs refinement)
                    val = float(kpi_value)
                    bench = float(benchmark_value)
                    tolerance = 0.01 # Example tolerance for floating point comparison

                    if abs(val - bench) <= tolerance:
                        status = "Met"
                    elif kpi_name == "loss_ratio": # Lower is better
                        status = "Above" if val > bench else "Below"
                    else: # Assume higher is better for other simple KPIs here
                        status = "Above" if val > bench else "Below"
                        
                    self.logger.debug(f"KPI 	 	{kpi_name}	 	: Value={val}, Benchmark={bench}, Status={status}")
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Could not compare KPI 	 	{kpi_name}	 	 due to type error. Value: {kpi_value}, Benchmark: {benchmark_value}. Error: {e}")
                    status = "Error"
            else:
                 self.logger.debug(f"No benchmark found for KPI: {kpi_name}")

            comparison_results[kpi_name] = {
                "value": kpi_value,
                "benchmark": benchmark_value,
                "status": status
            }

        self.logger.info(f"Benchmark comparison completed for institution {institution_id}. Compared {len(comparison_results)} KPIs.")
        self.log_audit(institution_id, "benchmark_comparison_completed", {"compared_kpi_count": len(comparison_results)})

        return {"benchmark_comparison": comparison_results, "status": "success"}

