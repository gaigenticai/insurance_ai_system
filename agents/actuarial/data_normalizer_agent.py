from agents.base.base_agent import BaseAgent
from typing import Any, Dict, List
import json
import os
import logging # Ensure logging is imported if not already

class DataNormalizerAgent(BaseAgent):
    """Ingests and validates actuarial data against expected schemas."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="DataNormalizerAgent", config_agent=config_agent)
        # In a real system, schemas might be more complex or loaded dynamically
        self.expected_policy_keys = ["policy_id", "product_line", "geography", "issue_date", "premium_amount", "status"]
        self.expected_claims_keys = ["claim_id", "policy_id", "product_line", "geography", "loss_date", "report_date", "paid_amount", "reserve_amount", "status"]
        self.expected_financial_keys = ["earned_premium", "incurred_losses", "expenses"]

    def _validate_records(self, records: List[Dict[str, Any]], expected_keys: List[str], record_type: str, institution_id: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Validates a list of records against expected keys."""
        valid_records = []
        invalid_records = []
        if not isinstance(records, list):
            self.logger.error(f"Invalid input for _validate_records: expected list, got {type(records)}. Record type: {record_type}")
            return [], [] # Return empty lists if input is not a list
            
        for i, record in enumerate(records):
            if not isinstance(record, dict):
                error_detail = {"record_index": i, "error": "Record is not a dictionary", "record_preview": str(record)[:100]}
                invalid_records.append(error_detail)
                self.logger.warning(f"Invalid {record_type} record found for institution {institution_id} at index {i}. Expected dict, got {type(record)}.")
                continue
                
            missing_keys = [key for key in expected_keys if key not in record]
            if not missing_keys:
                valid_records.append(record)
            else:
                error_detail = {"record_index": i, "missing_keys": missing_keys, "record_preview": dict(list(record.items())[:3])}
                invalid_records.append(error_detail)
                self.logger.warning(f"Invalid {record_type} record found for institution {institution_id} at index {i}. Missing keys: {missing_keys}")
        return valid_records, invalid_records

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Loads data from a specified path or uses provided data, then validates it.

        Args:
            data: Dictionary potentially containing the raw data or a path to a data file.
                  Expected keys: "data_path" (optional, path to JSON file like sample_actuarial_input.json) 
                                 or "raw_data" (optional, the dictionary or list itself).
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the validated data and validation status.
            Example: {"normalized_data": {...}, "validation_status": "success"/"partial"/"failed", "errors": {...}}
        """
        self.logger.info(f"Executing data normalization for institution {institution_id}.")
        
        raw_data = None
        data_source_description = "unknown"
        if "raw_data" in data:
            raw_data = data["raw_data"]
            data_source_description = "provided raw_data argument"
        elif "data_path" in data:
            data_path = data["data_path"]
            data_source_description = f"file at {data_path}"
            if not os.path.exists(data_path):
                 self.logger.error(f"Data file not found at path: {data_path}")
                 self.log_audit(institution_id, "normalization_failed_file_not_found", {"path": data_path})
                 return {"normalized_data": None, "validation_status": "failed", "errors": {"file_error": "Data file not found"}}
            try:
                with open(data_path, 'r') as f:
                    raw_data = json.load(f)
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding JSON from data file {data_path}: {e}")
                self.log_audit(institution_id, "normalization_failed_json_error", {"path": data_path, "error": str(e)})
                return {"normalized_data": None, "validation_status": "failed", "errors": {"json_error": str(e)}}
            except Exception as e:
                self.logger.error(f"Failed to load data from {data_path}: {e}")
                self.log_audit(institution_id, "normalization_failed_load_error", {"path": data_path, "error": str(e)})
                return {"normalized_data": None, "validation_status": "failed", "errors": {"load_error": str(e)}}
        else:
            self.logger.error("No data source provided (expected 'data_path' or 'raw_data').")
            self.log_audit(institution_id, "normalization_failed_no_source", {})
            return {"normalized_data": None, "validation_status": "failed", "errors": {"source_error": "No data source specified"}}

        # Initialize data structures
        policy_records = []
        claims_records = []
        financial_data = {}
        metadata = {}

        # Handle raw_data based on its type (dict or list)
        if isinstance(raw_data, dict):
            policy_records = raw_data.get("policy_data", [])
            claims_records = raw_data.get("claims_data", [])
            financial_data = raw_data.get("financial_data", {})
            metadata = raw_data.get("metadata", {})
            self.logger.info(f"Processing dictionary-formatted actuarial data from {data_source_description}.")
        elif isinstance(raw_data, list):
            # Assumption: If raw_data is a list, treat it as claims_data
            claims_records = raw_data
            self.logger.warning(f"Processing list-formatted actuarial data from {data_source_description}. Assuming it represents claims_data. Policy, financial, and metadata will be considered empty/default.")
            self.log_audit(institution_id, "data_normalization_list_input", {"info": "Input data was a list, treated as claims_data.", "source": data_source_description})
        else:
             self.logger.error(f"Loaded data from {data_source_description} is not a dictionary or list, but type {type(raw_data)}.")
             self.log_audit(institution_id, "normalization_failed_invalid_format", {"source": data_source_description, "type": str(type(raw_data))})
             return {"normalized_data": None, "validation_status": "failed", "errors": {"format_error": f"Data must be a dictionary or list, got {type(raw_data)}"}}

        # --- Validation --- 
        valid_policies, policy_errors = self._validate_records(policy_records, self.expected_policy_keys, "policy", institution_id)
        valid_claims, claims_errors = self._validate_records(claims_records, self.expected_claims_keys, "claim", institution_id)
        
        # Validate financial data (only if raw_data was a dict)
        financial_missing_keys = []
        financial_errors = []
        if isinstance(raw_data, dict):
            financial_missing_keys = [key for key in self.expected_financial_keys if key not in financial_data]
            if financial_missing_keys:
                financial_errors.append({"missing_keys": financial_missing_keys})
                self.logger.warning(f"Financial data missing keys for institution {institution_id}: {financial_missing_keys}")
        elif isinstance(raw_data, list):
             # If input was a list, financial data is considered missing by definition of our handling
             financial_errors.append({"info": "Financial data not applicable for list input format."}) 

        errors = {
            "policy_errors": policy_errors,
            "claims_errors": claims_errors,
            "financial_errors": financial_errors
        }
        has_errors = bool(policy_errors or claims_errors or financial_errors)
        
        # Determine overall status
        is_financial_valid = not financial_errors or (len(financial_errors) == 1 and financial_errors[0].get("info")) # Valid if no errors or only the info message
        status = "failed"
        if valid_policies or valid_claims or (is_financial_valid and isinstance(raw_data, dict)):
             status = "partial" if has_errors else "success"

        normalized_data = {
            "metadata": metadata, # Metadata only present if input was dict
            "policy_data": valid_policies,
            "claims_data": valid_claims,
            "financial_data": financial_data if is_financial_valid and isinstance(raw_data, dict) else {} # Only include if valid and applicable
        }

        self.logger.info(f"Data normalization completed for institution {institution_id}. Status: {status}. Policies: {len(valid_policies)}/{len(policy_records)}, Claims: {len(valid_claims)}/{len(claims_records)}, Financial Valid: {is_financial_valid}")
        self.log_audit(institution_id, "data_normalization_completed", {"status": status, "policy_errors": len(policy_errors), "claims_errors": len(claims_errors), "financial_errors": len(financial_errors)})

        return {"normalized_data": normalized_data, "validation_status": status, "errors": errors}


