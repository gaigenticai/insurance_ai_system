"""
Application data management module for the Insurance AI System.
Handles storing and retrieving application data from PostgreSQL.
"""

import logging
import json

import uuid
from typing import Dict, Any, Optional, List

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


class ApplicationManager:
    """
    Manager for insurance application data.
    Replaces the previous JSON-based storage with PostgreSQL.
    """
    
    def __init__(self, institution_id: str):
        """
        Initialize the ApplicationManager with an institution ID.
        
        Args:
            institution_id: UUID of the institution
        """
        self.institution_id = institution_id
    
    def create_application(self, application_data: Dict) -> Optional[str]:
        """
        Create a new insurance application.
        
        Args:
            application_data: Dictionary containing application data
            
        Returns:
            Application ID if successful, None otherwise
        """
        try:
            # Extract key fields
            applicant_full_name = application_data.get('full_name', '')
            applicant_address = application_data.get('address', '')
            applicant_date_of_birth = application_data.get('date_of_birth', None)
            application_id = application_data.get('applicant_id', f"APP-{uuid.uuid4().hex[:8].upper()}")
            
            # Insert into database
            result = insert_record('applications', {
                'application_id': application_id,
                'institution_id': self.institution_id,
                'applicant_full_name': applicant_full_name,
                'applicant_address': applicant_address,
                'applicant_date_of_birth': applicant_date_of_birth,
                'application_data': json.dumps(application_data),
                'status': 'pending'
            })
            
            if result:
                logger.info(f"Created application: {application_id}")
                return application_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating application: {e}")
            return None
    
    def get_application(self, application_id: str) -> Optional[Dict]:
        """
        Get an application by its ID.
        
        Args:
            application_id: Unique identifier for the application
            
        Returns:
            Application data dictionary if found, None otherwise
        """
        try:
            # Query by application_id field (not the primary key)
            applications = get_records('applications', {'application_id': application_id})
            
            if applications:
                return applications[0]
            
            logger.warning(f"Application not found: {application_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting application {application_id}: {e}")
            return None
    
    def update_application(self, application_id: str, update_data: Dict) -> bool:
        """
        Update an existing application.
        
        Args:
            application_id: Unique identifier for the application
            update_data: Dictionary containing fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the application first
            applications = get_records('applications', {'application_id': application_id})
            
            if not applications:
                logger.warning(f"Cannot update: Application not found: {application_id}")
                return False
            
            app = applications[0]
            app_uuid = app['id']
            
            # Prepare update data
            current_app_data = app['application_data']
            
            # Update specific fields in application_data
            for key, value in update_data.items():
                if key not in ['id', 'application_id', 'institution_id']:
                    current_app_data[key] = value
            
            # Update the record
            update_data = {
                'application_data': current_app_data
            }
            
            # Update specific fields if provided
            if 'status' in update_data:
                update_data['status'] = update_data['status']
            
            if 'applicant_full_name' in update_data:
                update_data['applicant_full_name'] = update_data['applicant_full_name']
                
            if 'applicant_address' in update_data:
                update_data['applicant_address'] = update_data['applicant_address']
                
            if 'applicant_date_of_birth' in update_data:
                update_data['applicant_date_of_birth'] = update_data['applicant_date_of_birth']
            
            success = update_record('applications', app_uuid, update_data)
            
            if success:
                logger.info(f"Updated application: {application_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating application {application_id}: {e}")
            return False
    
    def update_application_status(self, application_id: str, status: str) -> bool:
        """
        Update the status of an application.
        
        Args:
            application_id: Unique identifier for the application
            status: New status value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the application first
            applications = get_records('applications', {'application_id': application_id})
            
            if not applications:
                logger.warning(f"Cannot update status: Application not found: {application_id}")
                return False
            
            app = applications[0]
            app_uuid = app['id']
            
            # Update the status
            success = update_record('applications', app_uuid, {'status': status})
            
            if success:
                logger.info(f"Updated application status: {application_id} -> {status}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating application status {application_id}: {e}")
            return False
    
    def get_applications_by_status(self, status: str, limit: int = 100) -> List[Dict]:
        """
        Get applications by status.
        
        Args:
            status: Status to filter by
            limit: Maximum number of applications to return
            
        Returns:
            List of application dictionaries
        """
        try:
            query = """
                SELECT * FROM insurance_ai.applications
                WHERE institution_id = %(institution_id)s AND status = %(status)s
                ORDER BY created_at DESC
                LIMIT %(limit)s
            """
            
            results = execute_query(query, {
                'institution_id': self.institution_id,
                'status': status,
                'limit': limit
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting applications by status {status}: {e}")
            return []
    
    def delete_application(self, application_id: str) -> bool:
        """
        Delete an application.
        
        Args:
            application_id: Unique identifier for the application
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the application first
            applications = get_records('applications', {'application_id': application_id})
            
            if not applications:
                logger.warning(f"Cannot delete: Application not found: {application_id}")
                return False
            
            app = applications[0]
            app_uuid = app['id']
            
            # Delete from database
            query = """
                DELETE FROM insurance_ai.applications
                WHERE id = %(app_uuid)s
            """
            
            execute_query(query, {'app_uuid': app_uuid}, commit=True)
            logger.info(f"Deleted application: {application_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting application {application_id}: {e}")
            return False
