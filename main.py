#!/usr/bin/env python3

import argparse
import json
import os
import sys

# Add project root parent to Python path to allow package imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(project_root))

from agents.config_agent import ConfigAgent
from modules.underwriting.flow import UnderwritingFlow
from modules.claims.flow import ClaimsFlow
from modules.actuarial.flow import ActuarialFlow
from utils.logging_utils import audit_logger

def run_underwriting_examples(config_agent, institution_id):
    """Run example underwriting scenarios for demonstration and testing."""
    logger = audit_logger.get_logger("main")
    logger.info(f"Running Underwriting Flow Examples for {institution_id}")
    print(f"\n--- Running Underwriting Flow Examples for {institution_id} ---")
    
    flow = UnderwritingFlow(config_agent)
    
    # Example application with enough data
    app_data_complete = {
        "applicant_id": "UW-TEST-001",
        "full_name": "Alice Example",
        "address": "123 Main St",
        "date_of_birth": "01/01/1990",
        "income": 80000,
        "credit_score": 720,
        "debt_to_income_ratio": 0.3,
        "address_location_tag": "SafeZoneC",
        "document_text": "Name: Alice Example\nDOB: 01/01/1990\nOther info..."
    }
    result_complete = flow.run(app_data_complete, institution_id)
    print("\n--- Complete Application Result ---")
    print(json.dumps(result_complete, indent=2))

    # Example application missing data
    app_data_incomplete = {
        "applicant_id": "UW-TEST-002",
        "full_name": "Bob Test",
        "address": "456 Side St",
        # Missing DOB, income, credit_score
        "document_text": "Name: Bob Test"
    }
    result_incomplete = flow.run(app_data_incomplete, institution_id)
    print("\n--- Incomplete Application Result ---")
    print(json.dumps(result_incomplete, indent=2))

    # Example application with low score
    app_data_low_score = {
        "applicant_id": "UW-TEST-003",
        "full_name": "Charlie Risk",
        "address": "789 Danger Ave",
        "date_of_birth": "03/15/1985",
        "income": 50000,
        "credit_score": 580, # Below threshold
        "debt_to_income_ratio": 0.5, # Above threshold
        "address_location_tag": "FloodZoneA", # High risk
        "document_text": "Name: Charlie Risk\nDOB: 03/15/1985"
    }
    result_low_score = flow.run(app_data_low_score, institution_id)
    print("\n--- Low Score Application Result ---")
    print(json.dumps(result_low_score, indent=2))

def run_claims_examples(config_agent, institution_id):
    """Run example claims scenarios for demonstration and testing."""
    logger = audit_logger.get_logger("main")
    logger.info(f"Running Claims Flow Examples for {institution_id}")
    print(f"\n--- Running Claims Flow Examples for {institution_id} ---")
    
    flow = ClaimsFlow(config_agent)

    # Example 1: Simple, low-value, valid claim -> AutoApproved
    claim_low_value = {
        "claim_id": "CLM-AUTO-001",
        "policy_id": "POLICY_ACTIVE_001",
        "claimed_amount": 450, # Below threshold 500
        "claim_description": "Minor windshield chip repair",
        "claim_date": "2025-05-28"
    }
    result_low_value = flow.run(claim_low_value, institution_id)
    print("\n--- Low Value Claim Result ---")
    print(json.dumps(result_low_value, indent=2))

    # Example 2: High severity claim -> Escalated
    claim_high_severity = {
        "claim_id": "CLM-HIGH-002",
        "policy_id": "POLICY_ACTIVE_001",
        "claimed_amount": 8000,
        "claim_description": "Major structural damage from fire", # High severity keyword
        "claim_date": "2025-05-29"
    }
    result_high_severity = flow.run(claim_high_severity, institution_id)
    print("\n--- High Severity Claim Result ---")
    print(json.dumps(result_high_severity, indent=2))

    # Example 3: Claim with expired policy -> Denied
    claim_expired_policy = {
        "claim_id": "CLM-EXPIRED-003",
        "policy_id": "POLICY_EXPIRED_002", # Expired policy
        "claimed_amount": 1200,
        "claim_description": "Water damage in basement",
        "claim_date": "2025-05-30"
    }
    result_expired_policy = flow.run(claim_expired_policy, institution_id)
    print("\n--- Expired Policy Claim Result ---")
    print(json.dumps(result_expired_policy, indent=2))

    # Example 4: Claim with potential fraud flag -> Escalated
    claim_fraud_flag = {
        "claim_id": "CLM-FRAUD-004",
        "policy_id": "POLICY_ACTIVE_003", # Policy with recent claims
        "claimed_amount": 250, # Below auto-approve threshold
        "claim_description": "Another small dent repair",
        "claim_date": "2025-05-31"
    }
    result_fraud_flag = flow.run(claim_fraud_flag, institution_id)
    print("\n--- Fraud Flag Claim Result ---")
    print(json.dumps(result_fraud_flag, indent=2))

    # Example 5: Standard claim, above auto-approve -> Escalated
    claim_standard = {
        "claim_id": "CLM-STD-005",
        "policy_id": "POLICY_ACTIVE_001",
        "claimed_amount": 750, # Above auto-approve, below high value
        "claim_description": "Rear bumper replacement",
        "claim_date": "2025-06-01"
    }
    result_standard = flow.run(claim_standard, institution_id)
    print("\n--- Standard Escalation Claim Result ---")
    print(json.dumps(result_standard, indent=2))

def run_actuarial_example(config_agent, institution_id):
    """Run example actuarial analysis for demonstration and testing."""
    logger = audit_logger.get_logger("main")
    logger.info(f"Running Actuarial Flow Example for {institution_id}")
    print(f"\n--- Running Actuarial Flow Example for {institution_id} ---")
    
    flow = ActuarialFlow(config_agent)

    # Run the flow using the sample data file
    data_source_info = {
        "data_path": os.path.join(project_root, "data/sample_actuarial_input.json")
    }
    result = flow.run(data_source_info, institution_id)

    print("\n--- Actuarial Flow Result ---")
    print(json.dumps(result, indent=2))

    # Optionally, read and print the generated markdown report
    if result.get("status") in ["Success", "Partial"] and result.get("report_paths", {}).get("markdown"):
        try:
            md_path = result["report_paths"]["markdown"]
            print(f"\n--- Generated Markdown Report ({md_path}) --- ")
            # Ensure path is absolute for reading
            if not os.path.isabs(md_path):
                md_path = os.path.join(project_root, md_path)
                
            if os.path.exists(md_path):
                with open(md_path, 'r') as f_report:
                    print(f_report.read())
            else:
                print(f"Report file not found at: {md_path}")
        except Exception as e:
            print(f"\nError reading generated report: {e}")

def main():
    """Main entry point for the insurance AI system."""
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Run Insurance AI System Flows.")
    parser.add_argument("--module", required=True, choices=["underwriting", "claims", "actuarial", "all"], 
                        help="Which module flow to run.")
    parser.add_argument("--institution", default="institution_a", 
                        help="Institution ID to use for configuration.")
    args = parser.parse_args()

    # Initialize logger
    logger = audit_logger.get_logger("main")
    logger.info(f"Starting Insurance AI System with module: {args.module}, institution: {args.institution}")

    # Initialize configuration agent
    config = ConfigAgent(config_dir=os.path.join(project_root, "config"))

    # Run the requested module(s)
    if args.module == "underwriting" or args.module == "all":
        run_underwriting_examples(config, args.institution)
    
    if args.module == "claims" or args.module == "all":
        run_claims_examples(config, args.institution)

    if args.module == "actuarial" or args.module == "all":
        run_actuarial_example(config, args.institution)
    
    logger.info(f"Completed running Insurance AI System modules: {args.module}")

if __name__ == "__main__":
    main()
