import json
import os
from typing import Any, Dict, Optional, Tuple

# Import utility modules
from insurance_ai_system.utils.logging_utils import audit_logger
from insurance_ai_system.utils.config_utils import ConfigValidator
from insurance_ai_system.utils.error_utils import get_error_handler

class ConfigAgent:
    """
    Production-grade configuration agent that loads and provides institution-specific configuration.
    Includes validation, error handling, and audit logging.
    """

    def __init__(self, config_dir: str = "/home/ubuntu/insurance_ai_system/config"):
        """
        Initialize the ConfigAgent with the specified configuration directory.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir
        self.loaded_configs: Dict[str, Dict[str, Any]] = {}
        
        # Set up logging and error handling
        self.logger = audit_logger.get_logger("ConfigAgent")
        self.error_handler = get_error_handler(self.logger)
        
        self.logger.info(f"ConfigAgent initialized with config directory: {config_dir}")

    def _load_config(self, institution_id: str) -> Dict[str, Any]:
        """
        Load and validate a configuration file for a given institution ID.
        
        Args:
            institution_id: ID of the institution
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration is invalid
            RuntimeError: For other loading errors
        """
        config_path = os.path.join(self.config_dir, f"{institution_id}.json")
        
        # Check if file exists
        if not os.path.exists(config_path):
            error_msg = f"Configuration file not found for institution: {institution_id} at {config_path}"
            self.logger.error(error_msg)
            audit_logger.log_audit_event(
                institution_id="system",
                agent_name="ConfigAgent",
                event_type="CONFIG_ERROR",
                details={"error": error_msg, "institution_id": institution_id},
                severity="ERROR"
            )
            raise FileNotFoundError(error_msg)
        
        try:
            # Load configuration file
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Validate institution ID
            if config_data.get("institution_id") != institution_id:
                error_msg = f"Institution ID mismatch in config file: {config_path}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Validate configuration structure
            is_valid, validation_error = ConfigValidator.validate_institution_config(config_data)
            if not is_valid:
                error_msg = f"Invalid configuration for {institution_id}: {validation_error}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Log successful load
            self.logger.info(f"Successfully loaded configuration for {institution_id}")
            audit_logger.log_audit_event(
                institution_id=institution_id,
                agent_name="ConfigAgent",
                event_type="CONFIG_LOADED",
                details={"config_path": config_path},
                severity="INFO"
            )
            
            return config_data
            
        except json.JSONDecodeError as e:
            error_msg = f"Error decoding JSON configuration for {institution_id}: {e}"
            self.logger.error(error_msg)
            audit_logger.log_audit_event(
                institution_id="system",
                agent_name="ConfigAgent",
                event_type="CONFIG_ERROR",
                details={"error": error_msg, "institution_id": institution_id},
                severity="ERROR"
            )
            raise ValueError(error_msg)
            
        except Exception as e:
            error_msg = f"Failed to load configuration for {institution_id}: {e}"
            self.logger.error(error_msg)
            audit_logger.log_audit_event(
                institution_id="system",
                agent_name="ConfigAgent",
                event_type="CONFIG_ERROR",
                details={"error": error_msg, "institution_id": institution_id},
                severity="ERROR"
            )
            raise RuntimeError(error_msg)

    def get_config(self, institution_id: str) -> Dict[str, Any]:
        """
        Retrieve the configuration for a specific institution, loading if necessary.
        
        Args:
            institution_id: ID of the institution
            
        Returns:
            Configuration dictionary
        """
        # Use error handler for safe execution
        return self.error_handler.safe_execute(
            func=self._get_config_internal,
            args=(institution_id,),
            context={"component": "ConfigAgent", "operation": "get_config", "institution_id": institution_id},
            default_return={}
        )
    
    def _get_config_internal(self, institution_id: str) -> Dict[str, Any]:
        """Internal method to get configuration with caching"""
        if institution_id not in self.loaded_configs:
            self.logger.info(f"Loading configuration for institution: {institution_id}")
            self.loaded_configs[institution_id] = self._load_config(institution_id)
        
        return self.loaded_configs[institution_id]

    def get_setting(self, institution_id: str, section: str, key: str, default: Any = None) -> Any:
        """
        Retrieve a specific setting from the configuration.
        
        Args:
            institution_id: ID of the institution
            section: Configuration section name
            key: Setting key within section
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        config = self.get_config(institution_id)
        return config.get(section, {}).get(key, default)

    def get_branding(self, institution_id: str) -> Dict[str, Any]:
        """
        Retrieve branding settings.
        
        Args:
            institution_id: ID of the institution
            
        Returns:
            Branding configuration dictionary
        """
        return self.get_config(institution_id).get("branding", {})

    def get_underwriting_rules(self, institution_id: str) -> Dict[str, Any]:
        """
        Retrieve underwriting rules.
        
        Args:
            institution_id: ID of the institution
            
        Returns:
            Underwriting rules dictionary
        """
        return self.get_config(institution_id).get("underwriting", {}).get("risk_rules", {})

    def get_claims_rules(self, institution_id: str) -> Dict[str, Any]:
        """
        Retrieve claims rules and thresholds.
        
        Args:
            institution_id: ID of the institution
            
        Returns:
            Claims rules dictionary
        """
        return self.get_config(institution_id).get("claims", {})

    def get_actuarial_settings(self, institution_id: str) -> Dict[str, Any]:
        """
        Retrieve actuarial analysis settings.
        
        Args:
            institution_id: ID of the institution
            
        Returns:
            Actuarial settings dictionary
        """
        return self.get_config(institution_id).get("actuarial", {})
    
    def reload_config(self, institution_id: str) -> Tuple[bool, Optional[str]]:
        """
        Force reload of configuration for an institution.
        
        Args:
            institution_id: ID of the institution
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if institution_id in self.loaded_configs:
                del self.loaded_configs[institution_id]
            
            # This will trigger a reload
            self.get_config(institution_id)
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to reload configuration for {institution_id}: {e}"
            self.logger.error(error_msg)
            return False, error_msg
