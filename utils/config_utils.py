import os
from typing import Dict, Any, Optional, Tuple

class ConfigValidator:
    """
    Production-grade configuration validator for the insurance AI system.
    Ensures all required configuration elements are present and valid.
    """
    
    @staticmethod
    def validate_institution_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate an institution configuration for completeness and correctness.
        
        Args:
            config: Institution configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required top-level sections
        required_sections = ["institution_id", "branding", "underwriting", "claims", "actuarial"]
        for section in required_sections:
            if section not in config:
                return False, f"Missing required configuration section: {section}"
        
        # Validate branding section
        branding = config.get("branding", {})
        required_branding_fields = ["name", "logo_url"]
        for field in required_branding_fields:
            if field not in branding:
                return False, f"Missing required branding field: {field}"
        
        # Validate underwriting section
        underwriting = config.get("underwriting", {})
        if "risk_rules" not in underwriting:
            return False, f"Missing required underwriting.risk_rules section"
        if "required_fields" not in underwriting:
            return False, f"Missing required underwriting.required_fields section"
        
        # Validate claims section
        claims = config.get("claims", {})
        required_claims_fields = ["triage_rules", "auto_resolution_threshold"]
        for field in required_claims_fields:
            if field not in claims:
                return False, f"Missing required claims field: {field}"
        
        # Validate actuarial section
        actuarial = config.get("actuarial", {})
        required_actuarial_fields = ["trend_analysis_params", "benchmarks"]
        for field in required_actuarial_fields:
            if field not in actuarial:
                return False, f"Missing required actuarial field: {field}"
        
        return True, None
