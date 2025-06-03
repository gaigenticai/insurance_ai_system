"""
Database migrations module for the Insurance AI System.
Creates and updates database schema and tables.
"""

import logging
import os
from typing import List, Dict, Any

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configure logging
logger = logging.getLogger(__name__)

# Get database connection details from environment variables
DB_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
DB_NAME = os.environ.get('POSTGRES_DB', 'insurance_ai')
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
DB_SCHEMA = os.getenv("DB_SCHEMA", "insurance_ai")


def get_admin_connection():
    """
    Get a connection to the database with admin privileges.
    
    Returns:
        Database connection
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def create_schema_if_not_exists():
    """Create the schema if it doesn't exist."""
    with get_admin_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # Check if schema exists
                cursor.execute(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
                    (DB_SCHEMA,)
                )
                if not cursor.fetchone():
                    # Create schema
                    cursor.execute(
                        sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(DB_SCHEMA))
                    )
                    logger.info(f"Created schema: {DB_SCHEMA}")
                else:
                    logger.info(f"Schema already exists: {DB_SCHEMA}")
            except Exception as e:
                logger.error(f"Error creating schema: {e}")
                raise


def create_tables_if_not_exist():
    """Create tables if they don't exist."""
    with get_admin_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # Set search path
                cursor.execute(f"SET search_path TO {DB_SCHEMA}, public")
                
                # Create applications table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS applications (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        application_id VARCHAR(255) UNIQUE NOT NULL,
                        application_data JSONB NOT NULL,
                        status VARCHAR(50) NOT NULL DEFAULT 'pending',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        institution_id VARCHAR(255) NOT NULL
                    )
                """)
                
                # Create underwriting_decisions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS underwriting_decisions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        application_id UUID NOT NULL REFERENCES applications(id),
                        decision VARCHAR(50) NOT NULL,
                        decision_factors JSONB,
                        risk_score FLOAT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        created_by VARCHAR(255) NOT NULL
                    )
                """)
                
                # Create claims table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS claims (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        claim_id VARCHAR(255) UNIQUE NOT NULL,
                        policy_id VARCHAR(255) NOT NULL,
                        claim_data JSONB NOT NULL,
                        status VARCHAR(50) NOT NULL DEFAULT 'pending',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        institution_id VARCHAR(255) NOT NULL
                    )
                """)
                
                # Create claim_decisions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS claim_decisions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        claim_id UUID NOT NULL REFERENCES claims(id),
                        decision VARCHAR(50) NOT NULL,
                        decision_factors JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        created_by VARCHAR(255) NOT NULL
                    )
                """)
                
                # Create actuarial_analyses table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS actuarial_analyses (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        analysis_id VARCHAR(255) UNIQUE NOT NULL,
                        data_source JSONB NOT NULL,
                        parameters JSONB,
                        results JSONB,
                        status VARCHAR(50) NOT NULL DEFAULT 'pending',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        institution_id VARCHAR(255) NOT NULL
                    )
                """)
                
                # Create tasks table (new)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        task_id VARCHAR(255) UNIQUE NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        result JSONB,
                        error TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        institution_id VARCHAR(255) NOT NULL,
                        report_id VARCHAR(255)
                    )
                """)
                
                # Create reports table (new)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reports (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        report_id VARCHAR(255) UNIQUE NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        content JSONB NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        institution_id VARCHAR(255) NOT NULL,
                        task_id VARCHAR(255)
                    )
                """)
                
                # Create events table (new)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        event_id VARCHAR(255) UNIQUE NOT NULL,
                        event_type VARCHAR(255) NOT NULL,
                        payload JSONB NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        source VARCHAR(255) NOT NULL,
                        institution_id VARCHAR(255) NOT NULL
                    )
                """)
                
                # Create AI configurations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_configurations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        institution_id UUID NOT NULL,
                        configuration JSONB NOT NULL,
                        active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create AI interactions table for logging
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_interactions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        institution_id UUID NOT NULL,
                        agent_name VARCHAR(255) NOT NULL,
                        template_name VARCHAR(255) NOT NULL,
                        provider_name VARCHAR(255) NOT NULL,
                        model_name VARCHAR(255) NOT NULL,
                        prompt_tokens INTEGER,
                        completion_tokens INTEGER,
                        total_tokens INTEGER,
                        response_time_ms INTEGER,
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create AI model performance table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_model_performance (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        institution_id UUID NOT NULL,
                        model_name VARCHAR(255) NOT NULL,
                        task_type VARCHAR(255) NOT NULL,
                        accuracy_score DECIMAL(5,4),
                        precision_score DECIMAL(5,4),
                        recall_score DECIMAL(5,4),
                        f1_score DECIMAL(5,4),
                        evaluation_date DATE NOT NULL,
                        sample_size INTEGER,
                        notes TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_institution_id ON applications(institution_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_claims_institution_id ON claims(institution_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_actuarial_analyses_institution_id ON actuarial_analyses(institution_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_institution_id ON tasks(institution_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_institution_id ON reports(institution_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_institution_id ON events(institution_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_configurations_institution_id ON ai_configurations(institution_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_interactions_institution_id ON ai_interactions(institution_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_interactions_agent_name ON ai_interactions(agent_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_model_performance_institution_id ON ai_model_performance(institution_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_model_performance_model_name ON ai_model_performance(model_name)")
                
                logger.info("Created tables successfully")
            except Exception as e:
                logger.error(f"Error creating tables: {e}")
                raise


def run_migrations():
    """Run database migrations."""
    try:
        # Create schema
        create_schema_if_not_exists()
        
        # Create tables
        create_tables_if_not_exist()
        
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Database migrations failed: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run migrations
    run_migrations()
