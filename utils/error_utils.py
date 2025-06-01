import os
import sys
import traceback
from typing import Dict, Any, Optional, Callable, Tuple

class ErrorHandler:
    """
    Production-grade error handling utility for the insurance AI system.
    Provides consistent error handling, logging, and recovery mechanisms.
    """
    
    def __init__(self, logger):
        """
        Initialize the error handler with a logger.
        
        Args:
            logger: Logger instance for error reporting
        """
        self.logger = logger
    
    def handle_error(self, 
                    error: Exception, 
                    context: Dict[str, Any],
                    severity: str = "ERROR") -> Dict[str, Any]:
        """
        Handle an exception with proper logging and context.
        
        Args:
            error: The exception that occurred
            context: Dictionary with contextual information about the error
            severity: Error severity level
            
        Returns:
            Error response dictionary with status and details
        """
        # Get full traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stack_trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
        
        # Log the error with context
        error_details = {
            "error_type": exc_type.__name__ if exc_type else type(error).__name__,
            "error_message": str(error),
            "stack_trace": stack_trace,
            "context": context
        }
        
        # Log to system logger
        self.logger.error(f"Error in {context.get('component', 'unknown')}: {str(error)}")
        
        # For critical errors, log full details
        if severity == "CRITICAL":
            self.logger.critical(f"Critical error details: {error_details}")
        
        # Return standardized error response
        return {
            "status": "Error",
            "error_type": exc_type.__name__ if exc_type else type(error).__name__,
            "error_message": str(error),
            "error_code": getattr(error, 'code', None)
        }
    
    def safe_execute(self, 
                    func: Callable, 
                    args: Tuple = (), 
                    kwargs: Dict[str, Any] = {},
                    context: Dict[str, Any] = {},
                    default_return: Any = None) -> Any:
        """
        Execute a function with error handling.
        
        Args:
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            context: Error context information
            default_return: Value to return if an error occurs
            
        Returns:
            Function result or default_return on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_response = self.handle_error(e, context)
            return default_return if default_return is not None else error_response
    
    def validate_input(self, 
                      data: Dict[str, Any], 
                      required_fields: list,
                      field_types: Dict[str, type] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate input data against required fields and types.
        
        Args:
            data: Input data dictionary
            required_fields: List of required field names
            field_types: Dictionary mapping field names to expected types
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Check field types if specified
        if field_types:
            for field, expected_type in field_types.items():
                if field in data and not isinstance(data[field], expected_type):
                    actual_type = type(data[field]).__name__
                    expected_name = expected_type.__name__
                    return False, f"Invalid type for {field}: expected {expected_name}, got {actual_type}"
        
        return True, None

# Factory function to create error handler
def get_error_handler(logger):
    """Factory function to get an ErrorHandler instance"""
    return ErrorHandler(logger)
