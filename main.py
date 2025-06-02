#!/usr/bin/env python3
"""
Main module for the Insurance AI System.
Entry point for the application with PostgreSQL integration.
"""

import argparse
import logging
import os
import sys
from typing import Dict, Any
import subprocess

# Add project root parent to Python path to allow package imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(project_root))

# Import from db_connection for PostgreSQL operations
from db_connection import execute_query, close_all_connections

# Import original modules and agents
from agents.config_agent import ConfigAgent
from modules.underwriting.flow import UnderwritingFlow
from modules.claims.flow import ClaimsFlow
from modules.actuarial.flow import ActuarialFlow
from application_manager import ApplicationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', 'insurance_ai.log'), 'a')
    ]
)
logger = logging.getLogger(__name__)

# Configure formatter for console output
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def run_underwriting_examples(config_agent, institution_id):
    """Run example underwriting scenarios for demonstration and testing."""
    logger.info(f"Running Underwriting Flow Examples for {institution_id}")
    print(f"\n--- Running Underwriting Flow Examples for {institution_id} ---")
    
    # Initialize application manager
    app_manager = ApplicationManager(config_agent.institution_id)
    
    # Example application with enough data
    app_data_complete = {
        "applicant_id": "UW-TEST-222",
        "full_name": "Alice Example",
        "address": "123 Main St",
        "date_of_birth": "01/01/1990",
        "income": 80000,
        "credit_score": 720,
        "debt_to_income_ratio": 0.3,
        "address_location_tag": "SafeZoneC",
        "document_text": "Name: Alice Example\nDOB: 01/01/1990\nOther info..."
    }
    
    # Create application
    application_id = app_manager.create_application(app_data_complete)
    
    if not application_id:
        logger.error("Failed to create application")
        return
    
    logger.info(f"Created application: {application_id}")
    
    # Initialize underwriting flow
    flow = UnderwritingFlow(config_agent)
    
    # Process application
    result = flow.process_application(application_id)
    
    logger.info(f"Underwriting result: {result}")
    
    # Get decision
    decision = flow.get_underwriting_decision(application_id)
    
    if decision:
        logger.info(f"Decision details: {decision}")
    else:
        logger.warning("No decision found")
    
    # Example with incomplete data
    app_data_incomplete = {
        "applicant_id": "UW-TEST-002",
        "full_name": "Bob Example",
        "address": "456 Oak St",
        # Missing other fields
    }
    
    # Create application
    application_id2 = app_manager.create_application(app_data_incomplete)
    
    if application_id2:
        logger.info(f"Created incomplete application: {application_id2}")
        
        # Process application
        result2 = flow.process_application(application_id2)
        logger.info(f"Underwriting result for incomplete application: {result2}")


def run_claims_examples(config_agent, institution_id):
    """Run example claims scenarios for demonstration and testing."""
    logger.info(f"Running Claims Flow Examples for {institution_id}")
    print(f"\n--- Running Claims Flow Examples for {institution_id} ---")
    
    # Initialize claims flow
    flow = ClaimsFlow(config_agent)
    
    # Example claim data
    claim_data = {
        "claim_id": "CL-TEST-001",
        "policy_id": "POL-123456",
        "claimant_name": "Alice Example",
        "incident_date": "2023-05-15",
        "claim_amount": 5000,
        "incident_description": "Water damage from burst pipe"
    }
    
    # Process claim
    result = flow.run(claim_data, args.institution)
    
    logger.info(f"Claims processing result: {result}")


def run_actuarial_examples(config_agent, institution_id):
    """Run example actuarial scenarios for demonstration and testing."""
    logger.info(f"Running Actuarial Flow Examples for {institution_id}")
    print(f"\n--- Running Actuarial Flow Examples for {institution_id} ---")
    
    # Initialize actuarial flow
    flow = ActuarialFlow(config_agent)
    
    # Example actuarial calculation
    result = flow.calculate_risk_model({
        "raw_data": [
            {
                "age_group": "30-40",
                "region": "Northeast",
                "coverage_type": "comprehensive",
                "claim_history": 2,
                "premium_paid": 1200
            }
        ],
        "institution_id": institution_id
    })
    
    logger.info(f"Actuarial calculation result: {result}")


def main(args):
    """Main entry point for the Insurance AI System."""
    parser = argparse.ArgumentParser(description='Insurance AI System')
    parser.add_argument('--institution', type=str, default='institution_a',
                        help='Institution code to use')
    parser.add_argument('--module', type=str, choices=['underwriting', 'claims', 'actuarial', 'all'],
                        default='all', help='Module to run examples for')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize configuration agent
        config_agent = ConfigAgent(args.institution)
        
        if not config_agent.institution_id:
            logger.error(f"Institution not found: {args.institution}")
            return 1
        
        # Run examples based on module selection
        if args.module in ['underwriting', 'all']:
            run_underwriting_examples(config_agent, args.institution)
        
        if args.module in ['claims', 'all']:
            run_claims_examples(config_agent, args.institution)
        
        if args.module in ['actuarial', 'all']:
            run_actuarial_examples(config_agent, args.institution)
        
        return 0
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        return 1
    finally:
        # Close all database connections
        close_all_connections()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If arguments are passed, expect --institution etc.
        sys.exit(main(sys.argv))
    else:
        # No arguments passed → launch Streamlit UI
        print("Launching Streamlit UI (no args detected)...")
        subprocess.run([
            "streamlit",
            "run",
            "/app/insurance_ai_system/ui/streamlit_app.py",
            "--server.port", "8080",
            "--server.address", "0.0.0.0"
        ])
#trigger dev