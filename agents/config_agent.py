"""
Configuration agent module for the Insurance AI System.
Handles loading and managing configuration data from PostgreSQL.
"""

import logging
import uuid
from typing import Dict, Any, Optional

from db_connection import (
    get_record_by_id,
    get_records,
    insert_record,
    update_record,
    execute_query
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConfigAgent:
    """
    Agent responsible for loading and managing configuration data.
    Replaces the previous JSON-based configuration with PostgreSQL.
    """
    
    def __init__(self, institution_code: str):
        """
        Initialize the ConfigAgent with an institution code.
        
        Args:
            institution_code: Unique code identifying the institution
        """
        self.institution_code = institution_code
        self.institution_id = None
        self.institution_data = None
        self._load_institution()
    
    def _load_institution(self) -> None:
        """Load institution data from the database."""
        try:
            # Query the institution by code
            institutions = get_records('institutions', {'code': self.institution_code})
            
            if not institutions:
                logger.warning(f"Institution with code {self.institution_code} not found")
                return
            
            self.institution_data = institutions[0]
            self.institution_id = self.institution_data['id']
            logger.info(f"Loaded institution: {self.institution_code}")
            
        except Exception as e:
            logger.error(f"Error loading institution {self.institution_code}: {e}")
            raise
    
    def get_institution_setting(self, setting_key: str, default: Any = None) -> Any:
        """
        Get a specific institution setting.
        
        Args:
            setting_key: Key of the setting to retrieve
            default: Default value if setting is not found
            
        Returns:
            Setting value or default
        """
        if not self.institution_data:
            return default
        
        settings = self.institution_data.get('settings', {})
        return settings.get(setting_key, default)
    
    def update_institution_setting(self, setting_key: str, value: Any) -> bool:
        """
        Update a specific institution setting.
        
        Args:
            setting_key: Key of the setting to update
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        if not self.institution_id:
            logger.error("Cannot update settings: Institution not loaded")
            return False
        
        try:
            # Get current settings
            current_settings = self.institution_data.get('settings', {})
            
            # Update the specific setting
            current_settings[setting_key] = value
            
            # Update in database
            success = update_record(
                'institutions',
                self.institution_id,
                {'settings': current_settings}
            )
            
            if success:
                # Update local cache
                self.institution_data['settings'] = current_settings
                logger.info(f"Updated institution setting: {setting_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating institution setting {setting_key}: {e}")
            return False
    
    
    def get_claims_rules(self, institution_id: str) -> Dict[str, Any]:
        """
        Extracts and returns claims-related configuration rules for the institution.

        These rules include triage, fraud, and auto-resolution logic.
        """
        return self.get_institution_setting("claims_rules", default={})
    
    
    def get_agent_configuration(self, agent_type: str) -> Dict:
        """
        Get configuration for a specific agent type.
        
        Args:
            agent_type: Type of agent to get configuration for
            
        Returns:
            Agent configuration dictionary
        """
        if not self.institution_id:
            logger.error("Cannot get agent configuration: Institution not loaded")
            return {}
        
        try:
            # Query agent configuration
            query = """
                SELECT * FROM insurance_ai.agent_configurations
                WHERE institution_id = %(institution_id)s AND agent_type = %(agent_type)s
                AND active = TRUE
            """
            
            results = execute_query(query, {
                'institution_id': self.institution_id,
                'agent_type': agent_type
            })
            
            if results:
                return results[0].get('configuration', {})
            
            logger.warning(f"No configuration found for agent type: {agent_type}")
            return {}
            
        except Exception as e:
            logger.error(f"Error getting agent configuration for {agent_type}: {e}")
            return {}
    
    def update_agent_configuration(self, agent_type: str, configuration: Dict) -> bool:
        """
        Update configuration for a specific agent type.
        
        Args:
            agent_type: Type of agent to update configuration for
            configuration: New configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.institution_id:
            logger.error("Cannot update agent configuration: Institution not loaded")
            return False
        
        try:
            # Check if configuration exists
            query = """
                SELECT id FROM insurance_ai.agent_configurations
                WHERE institution_id = %(institution_id)s AND agent_type = %(agent_type)s
            """
            
            results = execute_query(query, {
                'institution_id': self.institution_id,
                'agent_type': agent_type
            })
            
            if results:
                # Update existing configuration
                config_id = results[0]['id']
                return update_record(
                    'agent_configurations',
                    config_id,
                    {'configuration': configuration}
                )
            else:
                # Create new configuration
                insert_record('agent_configurations', {
                    'institution_id': self.institution_id,
                    'agent_type': agent_type,
                    'configuration': configuration,
                    'active': True
                })
                return True
            
        except Exception as e:
            logger.error(f"Error updating agent configuration for {agent_type}: {e}")
            return False
    
    def get_module_configuration(self, module_type: str) -> Dict:
        """
        Get configuration for a specific module type.
        
        Args:
            module_type: Type of module to get configuration for
            
        Returns:
            Module configuration dictionary
        """
        if not self.institution_id:
            logger.error("Cannot get module configuration: Institution not loaded")
            return {}
        
        try:
            # Query module configuration
            query = """
                SELECT * FROM insurance_ai.module_configurations
                WHERE institution_id = %(institution_id)s AND module_type = %(module_type)s
                AND active = TRUE
            """
            
            results = execute_query(query, {
                'institution_id': self.institution_id,
                'module_type': module_type
            })
            
            if results:
                return results[0].get('configuration', {})
            
            logger.warning(f"No configuration found for module type: {module_type}")
            return {}
            
        except Exception as e:
            logger.error(f"Error getting module configuration for {module_type}: {e}")
            return {}
    
    def update_module_configuration(self, module_type: str, configuration: Dict) -> bool:
        """
        Update configuration for a specific module type.
        
        Args:
            module_type: Type of module to update configuration for
            configuration: New configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.institution_id:
            logger.error("Cannot update module configuration: Institution not loaded")
            return False
        
        try:
            # Check if configuration exists
            query = """
                SELECT id FROM insurance_ai.module_configurations
                WHERE institution_id = %(institution_id)s AND module_type = %(module_type)s
            """
            
            results = execute_query(query, {
                'institution_id': self.institution_id,
                'module_type': module_type
            })
            
            if results:
                # Update existing configuration
                config_id = results[0]['id']
                return update_record(
                    'module_configurations',
                    config_id,
                    {'configuration': configuration}
                )
            else:
                # Create new configuration
                insert_record('module_configurations', {
                    'institution_id': self.institution_id,
                    'module_type': module_type,
                    'configuration': configuration,
                    'active': True
                })
                return True
            
        except Exception as e:
            logger.error(f"Error updating module configuration for {module_type}: {e}")
            return False
    
    def log_audit_event(self, entity_type: str, entity_id: str, action: str, actor: str, details: Dict = None) -> bool:
        """
        Log an audit event.
        
        Args:
            entity_type: Type of entity (application, claim, etc.)
            entity_id: ID of the entity
            action: Action performed (create, read, update, delete, process, decision)
            actor: Actor who performed the action
            details: Additional details about the action
            
        Returns:
            True if successful, False otherwise
        """
        try:
            insert_record('audit_logs', {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'action': action,
                'actor': actor,
                'details': details or {}
            })
            return True
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return False
