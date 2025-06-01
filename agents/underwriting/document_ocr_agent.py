from agents.base.base_agent import BaseAgent
from typing import Any, Dict
import re

class DocumentOCRAgent(BaseAgent):
    """Simulates OCR extraction from unstructured text based on configured patterns."""

    def __init__(self, config_agent: Any):
        super().__init__(agent_name="DocumentOCRAgent", config_agent=config_agent)

    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Extracts data from simulated document text using regex patterns from config.

        Args:
            data: Dictionary containing document text, e.g., {"document_text": "...", "applicant_id": "..."}
            institution_id: The ID of the institution.

        Returns:
            A dictionary containing the extracted data.
            Example: {"extracted_data": {"field1": "value1", ...}, "ocr_status": "success"/"partial"/"failed"}
        """
        self.logger.info(f"Executing document OCR simulation for institution {institution_id}.")
        applicant_id = data.get("applicant_id", "unknown")
        document_text = data.get("document_text", "")
        
        if not document_text:
            self.logger.warning(f"No document text provided for applicant {applicant_id}, institution {institution_id}. Skipping OCR.")
            self.log_audit(institution_id, "ocr_skipped_no_text", {"applicant_id": applicant_id})
            return {"extracted_data": {}, "ocr_status": "failed"}

        ocr_config = self.config_agent.get_setting(institution_id, "underwriting", "ocr_extraction_map", default={})
        if not ocr_config:
            self.logger.warning(f"No OCR extraction patterns configured for institution {institution_id}. Skipping OCR.")
            self.log_audit(institution_id, "ocr_skipped_no_config", {"applicant_id": applicant_id})
            return {"extracted_data": {}, "ocr_status": "failed"}

        extracted_data = {}
        patterns_found = 0
        for field, pattern in ocr_config.items():
            try:
                match = re.search(pattern, document_text)
                if match:
                    # Assuming the first capturing group contains the desired value
                    extracted_value = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
                    extracted_data[field.replace("_pattern", "")] = extracted_value
                    patterns_found += 1
                    # Removed excessive tabs for clarity
                    self.logger.debug(f"Extracted 	'{field.replace(	'_pattern	', 	''	)}	' : 	'{extracted_value}	' using pattern: {pattern}")
                else:
                    self.logger.debug(f"Pattern for 	'{field}	' did not match.")
            except re.error as e:
                self.logger.error(f"Invalid regex pattern configured for {field} in institution {institution_id}: {pattern} - Error: {e}")
            except Exception as e:
                 self.logger.error(f"Error during regex matching for field {field} with pattern {pattern}: {e}")

        status = "success" if patterns_found == len(ocr_config) else ("partial" if patterns_found > 0 else "failed")
        self.logger.info(f"OCR simulation completed for applicant {applicant_id}. Status: {status}. Extracted fields: {list(extracted_data.keys())}")
        self.log_audit(institution_id, "ocr_processed", {"applicant_id": applicant_id, "status": status, "extracted_fields_count": len(extracted_data)})

        return {"extracted_data": extracted_data, "ocr_status": status}


