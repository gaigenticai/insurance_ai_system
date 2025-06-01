from typing import Dict, Any, Optional
import os
import json
from datetime import datetime

class BrandingManager:
    """
    Production-grade branding manager for the insurance AI system.
    Handles consistent application of institution-specific branding across all modules.
    """
    
    def __init__(self, config_agent):
        """
        Initialize the branding manager with the config agent.
        
        Args:
            config_agent: The system's ConfigAgent instance
        """
        self.config_agent = config_agent
        
    def get_branding(self, institution_id: str) -> Dict[str, Any]:
        """
        Get the branding configuration for a specific institution.
        
        Args:
            institution_id: ID of the institution
            
        Returns:
            Dictionary containing branding elements
        """
        config = self.config_agent.get_config(institution_id)
        return config.get("branding", {})
    
    def apply_branding_to_report(self, 
                               report_content: str, 
                               institution_id: str, 
                               report_type: str = "markdown") -> str:
        """
        Apply institution-specific branding to a report.
        
        Args:
            report_content: Original report content
            institution_id: ID of the institution
            report_type: Type of report (markdown, json, html)
            
        Returns:
            Branded report content
        """
        branding = self.get_branding(institution_id)
        institution_name = branding.get("name", "Insurance Company")
        report_style = branding.get("report_style", "standard")
        
        if report_type == "markdown":
            # Add branded header to markdown report
            current_date = datetime.now().strftime("%Y-%m-%d")
            branded_header = f"""# {institution_name} Report
## Generated on {current_date}

---

"""
            return branded_header + report_content
            
        elif report_type == "json":
            # For JSON reports, add branding as metadata
            try:
                report_json = json.loads(report_content)
                report_json["metadata"] = {
                    "institution": institution_name,
                    "generated_date": datetime.now().isoformat(),
                    "report_style": report_style
                }
                return json.dumps(report_json, indent=2)
            except json.JSONDecodeError:
                # If not valid JSON, return as is
                return report_content
                
        elif report_type == "html":
            # Add branded styling to HTML
            logo_url = branding.get("logo_url", "")
            css_class = f"report-style-{report_style}"
            
            branded_header = f"""<!DOCTYPE html>
<html>
<head>
    <title>{institution_name} Report</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .header {{ display: flex; align-items: center; margin-bottom: 20px; }}
        .logo {{ max-height: 60px; margin-right: 20px; }}
        .institution-name {{ font-size: 24px; font-weight: bold; }}
        .{css_class} {{ /* Custom styling based on institution preferences */ }}
    </style>
</head>
<body class="{css_class}">
    <div class="header">
        <img src="{logo_url}" alt="{institution_name} Logo" class="logo">
        <div class="institution-name">{institution_name}</div>
    </div>
    <div class="content">
"""
            branded_footer = """
    </div>
    <div class="footer">
        <p>Generated on """ + datetime.now().strftime("%Y-%m-%d") + """</p>
    </div>
</body>
</html>"""

            # If content is complete HTML, extract body content
            if "<body" in report_content and "</body>" in report_content:
                start = report_content.find("<body")
                start = report_content.find(">", start) + 1
                end = report_content.find("</body>")
                body_content = report_content[start:end]
                return branded_header + body_content + branded_footer
            else:
                # Assume content is just the body part
                return branded_header + report_content + branded_footer
                
        # Default case - return unmodified
        return report_content
    
    def get_email_template(self, 
                          institution_id: str, 
                          template_type: str = "general") -> Dict[str, str]:
        """
        Get a branded email template for a specific institution.
        
        Args:
            institution_id: ID of the institution
            template_type: Type of email template (general, claim, underwriting)
            
        Returns:
            Dictionary with email template parts
        """
        branding = self.get_branding(institution_id)
        institution_name = branding.get("name", "Insurance Company")
        email_header = branding.get("email_template_header", f"From {institution_name}:")
        
        templates = {
            "general": {
                "subject": f"{institution_name} - Information",
                "header": email_header,
                "footer": f"\n\nRegards,\n{institution_name} Team"
            },
            "claim": {
                "subject": f"{institution_name} - Claim Update",
                "header": f"{email_header} Claim Status Update",
                "footer": f"\n\nFor any questions, please contact our claims department.\n\nRegards,\n{institution_name} Claims Team"
            },
            "underwriting": {
                "subject": f"{institution_name} - Application Status",
                "header": f"{email_header} Application Status Update",
                "footer": f"\n\nFor any questions, please contact our underwriting department.\n\nRegards,\n{institution_name} Underwriting Team"
            }
        }
        
        return templates.get(template_type, templates["general"])

# Singleton factory function
def get_branding_manager(config_agent):
    """Factory function to get a BrandingManager instance"""
    return BrandingManager(config_agent)
