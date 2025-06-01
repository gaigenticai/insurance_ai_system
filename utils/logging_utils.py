"""
Utility module for logging in the Insurance AI System.
Provides audit logging functionality.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create audit logger
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)

# Add file handler for audit logs
audit_log_dir = os.environ.get('AUDIT_LOG_DIR', 'logs')
os.makedirs(audit_log_dir, exist_ok=True)
audit_log_file = os.path.join(audit_log_dir, 'audit.log')
file_handler = logging.FileHandler(audit_log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
audit_logger.addHandler(file_handler)


class AuditLogger:
    """Audit logger for the Insurance AI System."""
    
    @staticmethod
    def log_audit_event(institution_id: str, agent_name: str, event_type: str, 
                        details: Dict[str, Any], severity: str = "INFO") -> None:
        """
        Log an audit event.
        
        Args:
            institution_id: Institution identifier
            agent_name: Name of the agent or component
            event_type: Type of event
            details: Event details
            severity: Event severity (INFO, WARNING, ERROR)
        """
        try:
            # Create audit event
            audit_event = {
                "timestamp": datetime.utcnow().isoformat(),
                "institution_id": institution_id,
                "agent_name": agent_name,
                "event_type": event_type,
                "details": details,
                "severity": severity
            }
            
            # Log audit event
            audit_logger.info(json.dumps(audit_event))
            
            # Also store in database if available
            try:
                from db_connection import insert_record
                
                # Insert audit event into database
                insert_record(
                    'audit_logs',
                    {
                        'institution_id': institution_id,
                        'agent_name': agent_name,
                        'event_type': event_type,
                        'details': details,
                        'severity': severity,
                        'created_at': datetime.utcnow()
                    }
                )
            except Exception as e:
                # Just log the error, don't raise
                logging.error(f"Failed to store audit event in database: {e}")
        except Exception as e:
            logging.error(f"Failed to log audit event: {e}")


# Export audit logger instance
audit_logger = AuditLogger()
