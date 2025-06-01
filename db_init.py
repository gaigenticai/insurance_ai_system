"""
Database initialization script for the Insurance AI System.
Creates the required tables and initial data in PostgreSQL.
"""

import os
import sys
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get database connection details from environment variables
DB_HOST = os.environ.get('PGHOST', 'localhost')
DB_PORT = os.environ.get('PGPORT', '5432')
DB_NAME = os.environ.get('PGDATABASE', 'insurance_ai')
DB_USER = os.environ.get('PGUSER', 'postgres')
DB_PASSWORD = os.environ.get('PGPASSWORD', 'postgres')

# Path to schema SQL file
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'postgresql_schema.sql')


def connect_to_database():
    """Connect to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        connection.autocommit = False
        logger.info(f"Connected to database: {DB_NAME}")
        return connection
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise


def execute_schema_file(connection):
    """Execute the schema SQL file to create tables."""
    try:
        with open(SCHEMA_FILE, 'r') as file:
            schema_sql = file.read()
        
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)
        
        connection.commit()
        logger.info("Schema created successfully")
    except Exception as e:
        connection.rollback()
        logger.error(f"Error creating schema: {e}")
        raise


def load_institution_data(connection, institution_json_path):
    """Load institution data from JSON file into PostgreSQL."""
    try:
        # Read the JSON file
        with open(institution_json_path, 'r') as file:
            institution_data = json.load(file)
        
        # Extract institution details
        institution_code = institution_data.get('code', 'institution_a')
        institution_name = institution_data.get('name', 'Institution A')
        institution_settings = institution_data.get('settings', {})
        
        # Insert into database
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if institution already exists
            cursor.execute(
                "SELECT id FROM insurance_ai.institutions WHERE code = %s",
                (institution_code,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing institution
                cursor.execute(
                    """
                    UPDATE insurance_ai.institutions
                    SET name = %s, settings = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE code = %s
                    RETURNING id
                    """,
                    (institution_name, json.dumps(institution_settings), institution_code)
                )
                institution_id = cursor.fetchone()['id']
                logger.info(f"Updated institution: {institution_code}")
            else:
                # Insert new institution
                cursor.execute(
                    """
                    INSERT INTO insurance_ai.institutions (code, name, settings)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (institution_code, institution_name, json.dumps(institution_settings))
                )
                institution_id = cursor.fetchone()['id']
                logger.info(f"Inserted institution: {institution_code}")
            
            # Load agent configurations
            agent_configs = institution_data.get('agent_configurations', {})
            for agent_type, config in agent_configs.items():
                cursor.execute(
                    """
                    INSERT INTO insurance_ai.agent_configurations 
                    (institution_id, agent_type, configuration)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (institution_id, agent_type) 
                    DO UPDATE SET configuration = EXCLUDED.configuration,
                                  updated_at = CURRENT_TIMESTAMP
                    """,
                    (institution_id, agent_type, json.dumps(config))
                )
            
            # Load module configurations
            module_configs = institution_data.get('module_configurations', {})
            for module_type, config in module_configs.items():
                cursor.execute(
                    """
                    INSERT INTO insurance_ai.module_configurations 
                    (institution_id, module_type, configuration)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (institution_id, module_type) 
                    DO UPDATE SET configuration = EXCLUDED.configuration,
                                  updated_at = CURRENT_TIMESTAMP
                    """,
                    (institution_id, module_type, json.dumps(config))
                )
        
        connection.commit()
        logger.info(f"Loaded institution data for: {institution_code}")
        return institution_id
    except Exception as e:
        connection.rollback()
        logger.error(f"Error loading institution data: {e}")
        raise


def main():
    """Main function to initialize the database."""
    try:
        # Connect to database
        connection = connect_to_database()
        
        # Execute schema file
        execute_schema_file(connection)
        
        # Load institution data if JSON file exists
        institution_json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'insurance_ai_system', 'config', 'institution_a.json'
        )
        
        if os.path.exists(institution_json_path):
            load_institution_data(connection, institution_json_path)
        else:
            logger.warning(f"Institution JSON file not found: {institution_json_path}")
        
        logger.info("Database initialization completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1
    finally:
        if 'connection' in locals() and connection:
            connection.close()


if __name__ == "__main__":
    sys.exit(main())
