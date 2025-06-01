"""
Validation script for PostgreSQL integration.
Tests database connection and basic CRUD operations.
"""

import os
import sys
import logging
import uuid
from typing import Dict, Any

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_connection import (
    get_db_connection,
    get_db_cursor,
    execute_query,
    insert_record,
    update_record,
    get_record_by_id,
    get_records,
    delete_record,
    close_all_connections
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_database_connection():
    """Test database connection."""
    logger.info("Testing database connection...")
    try:
        with get_db_connection() as connection:
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def test_crud_operations():
    """Test CRUD operations."""
    logger.info("Testing CRUD operations...")
    
    # Generate a unique test institution code
    test_code = f"test-institution-{uuid.uuid4().hex[:8]}"
    test_name = "Test Institution"
    test_settings = {"test_setting": "test_value"}
    
    try:
        # Test INSERT
        logger.info("Testing INSERT operation...")
        insert_result = insert_record('institutions', {
            'code': test_code,
            'name': test_name,
            'settings': test_settings
        })
        
        if not insert_result:
            logger.error("INSERT operation failed")
            return False
        
        institution_id = insert_result['id']
        logger.info(f"INSERT successful, ID: {institution_id}")
        
        # Test SELECT
        logger.info("Testing SELECT operation...")
        select_result = get_record_by_id('institutions', institution_id)
        
        if not select_result:
            logger.error("SELECT operation failed")
            return False
        
        if select_result['code'] != test_code:
            logger.error(f"SELECT returned incorrect data: {select_result}")
            return False
        
        logger.info("SELECT successful")
        
        # Test UPDATE
        logger.info("Testing UPDATE operation...")
        updated_settings = {"test_setting": "updated_value"}
        update_result = update_record('institutions', institution_id, {
            'settings': updated_settings
        })
        
        if not update_result:
            logger.error("UPDATE operation failed")
            return False
        
        # Verify UPDATE
        updated_record = get_record_by_id('institutions', institution_id)
        if updated_record['settings'].get('test_setting') != "updated_value":
            logger.error(f"UPDATE verification failed: {updated_record}")
            return False
        
        logger.info("UPDATE successful")
        
        # Test DELETE
        logger.info("Testing DELETE operation...")
        delete_result = delete_record('institutions', institution_id)
        
        if not delete_result:
            logger.error("DELETE operation failed")
            return False
        
        # Verify DELETE
        deleted_check = get_record_by_id('institutions', institution_id)
        if deleted_check:
            logger.error(f"DELETE verification failed: {deleted_check}")
            return False
        
        logger.info("DELETE successful")
        
        return True
    except Exception as e:
        logger.error(f"CRUD test failed: {e}")
        return False


def main():
    """Main validation function."""
    try:
        # Test database connection
        if not test_database_connection():
            logger.error("Database connection validation failed")
            return 1
        
        # Test CRUD operations
        if not test_crud_operations():
            logger.error("CRUD operations validation failed")
            return 1
        
        logger.info("All validation tests passed successfully")
        return 0
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        return 1
    finally:
        close_all_connections()


if __name__ == "__main__":
    sys.exit(main())
