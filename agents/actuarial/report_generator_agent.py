from agents.base.base_agent import BaseAgent
from typing import Any, Dict
import json
import os
from datetime import datetime, timezone


class ReportGeneratorAgent(BaseAgent):
    """Generates reports based on actuarial analysis results."""

    def __init__(self, config_agent: Any, report_dir: str = "/home/ubuntu/insurance_ai_system/logs/reports"):
        super().__init__(agent_name="ReportGeneratorAgent", config_agent=config_agent)
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True) # Ensure report directory exists

    def _generate_markdown_report(self, data: Dict[str, Any], institution_id: str, branding: Dict[str, Any], report_metadata: Dict[str, Any]) -> str:
        """Generates a Markdown formatted report."""
        report_lines = []
        inst_name = branding.get("name", institution_id)
        report_period_start = report_metadata.get("report_period_start", "N/A")
        report_period_end = report_metadata.get("report_period_end", "N/A")
        generated_at = datetime.now(timezone.utc).isoformat().strftime("%Y-%m-%d %H:%M:%S UTC")

        report_lines.append(f"# Actuarial Analysis Report for {inst_name}")
        report_lines.append(f"*Report Period: {report_period_start} to {report_period_end}*")
        report_lines.append(f"*Generated On: {generated_at}*")
        report_lines.append("--- ")

        # KPIs Section
        kpis = data.get("analysis_results", {}).get("kpis", {})
        benchmark_comparison = data.get("benchmark_comparison", {})
        if kpis:
            report_lines.append("## Key Performance Indicators (KPIs)")
            report_lines.append("| KPI Name | Value | Benchmark | Status |")
            report_lines.append("|---|---|---|---|")
            for name, value in kpis.items():
                comp = benchmark_comparison.get(name, {})
                bench_val = comp.get("benchmark", "N/A")
                status = comp.get("status", "N/A")
                # Format numbers nicely
                try:
                    formatted_value = f"{float(value):,.2f}" if isinstance(value, (int, float)) else value
                except:
                    formatted_value = value # Keep original if formatting fails
                report_lines.append(f'| {name.replace("_", " ").title()} | {formatted_value} | {bench_val} | {status} |')
            report_lines.append("\n")
        
        # Segment Analysis Section
        segment_analysis = data.get("analysis_results", {}).get("segment_analysis", {})
        if segment_analysis:
            report_lines.append("## Segment Analysis")
            for segment_key, segments in segment_analysis.items():
                report_lines.append(f'### By {segment_key.replace("_", " ").title()}')
                report_lines.append("| Segment Value | Policy Count | Premium | Claim Count | Paid Losses | Loss Ratio |")
                report_lines.append("|---|---|---|---|---|---|")
                for segment_value, metrics in segments.items():
                    pol_count = metrics.get("policy_count", 0)
                    premium = metrics.get("premium", 0)
                    claim_count = metrics.get("claim_count", 0)
                    paid_losses = metrics.get("paid_losses", 0)
                    loss_ratio = metrics.get("segment_loss_ratio", 0)
                    report_lines.append(f"| {segment_value} | {pol_count:,} | ${premium:,.2f} | {claim_count:,} | ${paid_losses:,.2f} | {loss_ratio:.2%} |")
                report_lines.append("\n") # Add newline after segment table

        # Fraud Insights Section
        fraud_insights = data.get("fraud_insights", {})
        if fraud_insights:
            report_lines.append("## Fraud Insights")
            report_lines.append(f"- Claims previously flagged during processing: {fraud_insights.get('flagged_claims_count', 0)}")
            report_lines.append("- Potential Suspicious Patterns Detected:")
            patterns = fraud_insights.get("suspicious_patterns_found", [])
            for pattern in patterns:
                report_lines.append(f"  - {pattern}")
            report_lines.append("\n") # Add newline after the section
        report_lines.append("*End of Report*")

        return "\n".join(report_lines)

    def _generate_json_report(self, data: Dict[str, Any], institution_id: str, branding: Dict[str, Any], report_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a JSON formatted report."""
        generated_at = datetime.now(timezone.utc).isoformat().isoformat()
        json_report = {
            "report_metadata": {
                **report_metadata,
                "institution_id": institution_id,
                "institution_name": branding.get("name", institution_id),
                "generated_at": generated_at
            },
            "kpi_summary": data.get("benchmark_comparison", {}),
            "segment_analysis": data.get("analysis_results", {}).get("segment_analysis", {}),
            "fraud_insights": data.get("fraud_insights", {})
        }
        return json_report

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Generates reports in specified formats based on analysis results.

        Args:
            data: Dictionary containing the combined results from previous actuarial agents.
                  Expected keys: "analysis_results", "benchmark_comparison", "fraud_insights", "normalized_data" (for metadata).
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing paths to the generated reports.
            Example: {"report_paths": {"markdown": "...", "json": "..."}, "status": "success"}
        """
        self.logger.info(f"Executing report generation for institution {institution_id}.")

        if not all(key in data for key in ["analysis_results", "benchmark_comparison", "fraud_insights", "normalized_data"]):
            self.logger.warning(f"Skipping report generation due to missing analysis data for institution {institution_id}.")
            self.log_audit(institution_id, "report_generation_skipped_missing_data", {})
            return {"report_paths": None, "status": "skipped"}

        branding = self.config_agent.get_branding(institution_id)
        report_metadata = data.get("normalized_data", {}).get("metadata", {})
        report_timestamp = datetime.now(timezone.utc).isoformat().isoformat().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{institution_id}_actuarial_report_{report_timestamp}"

        report_paths = {}
        errors = []

        # Generate Markdown Report
        try:
            md_content = self._generate_markdown_report(data, institution_id, branding, report_metadata)
            md_path = os.path.join(self.report_dir, f"{base_filename}.md")
            with open(md_path, "w") as f:
                f.write(md_content)
            report_paths["markdown"] = md_path
            self.logger.info(f"Markdown report generated successfully: {md_path}")
        except Exception as e:
            self.logger.error(f"Failed to generate Markdown report for {institution_id}: {e}")
            errors.append(f"Markdown generation failed: {e}")

        # Generate JSON Report
        try:
            json_content = self._generate_json_report(data, institution_id, branding, report_metadata)
            json_path = os.path.join(self.report_dir, f"{base_filename}.json")
            with open(json_path, "w") as f:
                # Use default=str for potential non-serializable types like datetime
                json.dump(json_content, f, indent=2, default=str)
            report_paths["json"] = json_path
            self.logger.info(f"JSON report generated successfully: {json_path}")
        except Exception as e:
            self.logger.error(f"Failed to generate JSON report for {institution_id}: {e}")
            errors.append(f"JSON generation failed: {e}")

        status = "success" if report_paths else "failed"
        if errors and report_paths:
            status = "partial"
        
        self.log_audit(institution_id, "report_generation_completed", {"status": status, "formats_generated": list(report_paths.keys()), "errors": errors})

        return {"report_paths": report_paths, "status": status, "errors": errors}

