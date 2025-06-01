import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Import utility modules
from utils.logging_utils import audit_logger
from utils.error_utils import get_error_handler
from utils.branding_utils import get_branding_manager

class BaseAgent(ABC):
    """
    Production-grade abstract base class for all agents in the system.
    Provides common functionality for logging, error handling, and branding.
    """

    def __init__(self, agent_name: str, config_agent: Any):
        """
        Initialize the base agent with common utilities.

        Args:
            agent_name: The name of the agent (for logging).
            config_agent: An instance of the ConfigAgent.
        """
        self.agent_name = agent_name
        self.config_agent = config_agent
        
        # Set up logging
        self.logger = audit_logger.get_logger(self.agent_name)
        
        # Set up error handling
        self.error_handler = get_error_handler(self.logger)
        
        # Set up branding manager
        self.branding_manager = get_branding_manager(self.config_agent)
        
        self.logger.info(f"Agent '{self.agent_name}' initialized.")

    @abstractmethod
    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """
        Execute the agent's primary logic.

        Args:
            data: The input data for the agent.
            institution_id: The ID of the institution for context/configuration.

        Returns:
            A dictionary containing the results of the agent's execution.
        """
        pass

    def log_audit(self, institution_id: str, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """
        Log an audit event for the agent's activity.
        
        Args:
            institution_id: ID of the institution context
            event_type: Type of event being logged
            details: Dictionary of event details
            severity: Event severity level
        """
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name=self.agent_name,
            event_type=event_type,
            details=details,
            severity=severity
        )
    
    def validate_input(self, data: Dict[str, Any], required_fields: list, institution_id: str) -> Dict[str, Any]:
        """
        Validate input data against required fields.
        
        Args:
            data: Input data dictionary
            required_fields: List of required field names
            institution_id: ID of the institution context
            
        Returns:
            Validation result dictionary with status and any missing fields
        """
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            self.log_audit(
                institution_id=institution_id,
                event_type="VALIDATION_ERROR",
                details={"missing_fields": missing_fields, "data_keys": list(data.keys())},
                severity="WARNING"
            )
            
            return {
                "status": "Incomplete",
                "missing_fields": missing_fields,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        return {"status": "Valid"}
    
    def handle_error(self, error: Exception, context: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """
        Handle an exception with proper logging and context.
        
        Args:
            error: The exception that occurred
            context: Dictionary with contextual information
            institution_id: ID of the institution context
            
        Returns:
            Error response dictionary
        """
        # Add institution context
        context["institution_id"] = institution_id
        
        # Log the error
        self.log_audit(
            institution_id=institution_id,
            event_type="ERROR",
            details={"error_message": str(error), "context": context},
            severity="ERROR"
        )
        
        # Use error handler
        return self.error_handler.handle_error(error, context)
    
    def safe_execute(self, func, args=(), kwargs={}, context={}, institution_id="system", default_return=None):
        """
        Execute a function with error handling and audit logging.
        
        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            context: Error context information
            institution_id: ID of the institution context
            default_return: Value to return on error
            
        Returns:
            Function result or default_return on error
        """
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_response = self.handle_error(e, context, institution_id)
            return default_return if default_return is not None else error_response
