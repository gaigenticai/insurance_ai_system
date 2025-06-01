import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

class AuditLogger:
    """
    Production-grade audit logging utility for the insurance AI system.
    Handles structured logging with consistent format across all modules.
    """
    
    def __init__(self, base_log_dir: str = "/home/ubuntu/insurance_ai_system/logs"):
        """
        Initialize the audit logger with the specified base log directory.
        
        Args:
            base_log_dir: Base directory for all log files
        """
        self.base_log_dir = base_log_dir
        os.makedirs(base_log_dir, exist_ok=True)
        
        # Configure system-wide logging
        self.system_logger = logging.getLogger('insurance_system')
        self.system_logger.setLevel(logging.INFO)
        
        # Create system log handler if not already configured
        if not self.system_logger.handlers:
            system_log_path = os.path.join(base_log_dir, 'system.log')
            file_handler = logging.FileHandler(system_log_path)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.system_logger.addHandler(file_handler)
            
            # Add console handler for development visibility
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.system_logger.addHandler(console_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a named logger for a specific component.
        
        Args:
            name: Name of the component (e.g., agent name)
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(f'insurance_system.{name}')
        return logger
    
    def log_audit_event(self, 
                        institution_id: str, 
                        agent_name: str, 
                        event_type: str, 
                        details: Dict[str, Any],
                        user_id: Optional[str] = None,
                        severity: str = "INFO") -> None:
        """
        Log a structured audit event to the institution-specific audit log.
        
        Args:
            institution_id: ID of the institution context
            agent_name: Name of the agent or component
            event_type: Type of event (e.g., "DECISION", "ERROR", "WARNING")
            details: Dictionary of event details
            user_id: Optional user ID if applicable
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        """
        # Ensure logs directory exists
        institution_log_dir = os.path.join(self.base_log_dir, institution_id)
        os.makedirs(institution_log_dir, exist_ok=True)
        
        # Create audit log entry
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "institution_id": institution_id,
            "agent": agent_name,
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        if user_id:
            log_entry["user_id"] = user_id
            
        # Write to institution-specific audit log
        audit_log_path = os.path.join(institution_log_dir, 'audit.log')
        try:
            with open(audit_log_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.system_logger.error(f"Failed to write audit log to {audit_log_path}: {e}")
            
        # Also log to system log for critical events
        if severity in ["ERROR", "CRITICAL"]:
            self.system_logger.error(f"AUDIT: {json.dumps(log_entry)}")
        elif severity == "WARNING":
            self.system_logger.warning(f"AUDIT: {json.dumps(log_entry)}")
        else:
            self.system_logger.info(f"AUDIT: {json.dumps(log_entry)}")

# Singleton instance for system-wide use
audit_logger = AuditLogger()
