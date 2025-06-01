"""
Underwriting flow module for the Insurance AI System.
Handles underwriting decisions using PostgreSQL for data storage.
"""

import logging
import uuid
from typing import Dict, Any, Optional

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


class UnderwritingFlow:
    """
    Handles the underwriting flow for insurance applications.
    Replaces the previous JSON-based storage with PostgreSQL.
    """
    
    def __init__(self, config_agent):
        """
        Initialize the UnderwritingFlow with a configuration agent.
        
        Args:
            config_agent: Configuration agent instance
        """
        self.config_agent = config_agent
        self.institution_id = config_agent.institution_id
    
    def process_application(self, application_id: str) -> Dict:
        """
        Process an insurance application for underwriting.
        
        Args:
            application_id: Unique identifier for the application
            
        Returns:
            Dictionary containing the underwriting decision and details
        """
        try:
            # Get the application data
            query = """
                SELECT * FROM insurance_ai.applications
                WHERE application_id = %(application_id)s
            """
            
            results = execute_query(query, {'application_id': application_id})
            
            if not results:
                logger.warning(f"Application not found: {application_id}")
                return {'error': 'Application not found'}
            
            application = results[0]
            application_data = application['application_data']
            
            # Get underwriting rules from configuration
            underwriting_config = self.config_agent.get_module_configuration('underwriting')
            
            # Apply underwriting rules and calculate risk score
            risk_score, decision_factors = self._calculate_risk_score(application_data, underwriting_config)
            
            # Determine decision based on risk score
            decision = self._determine_decision(risk_score, underwriting_config)
            
            # Store the underwriting decision
            decision_data = {
                'application_id': application['id'],
                'decision': decision,
                'decision_factors': decision_factors,
                'risk_score': risk_score,
                'created_by': 'underwriting_flow'
            }
            
            insert_record('underwriting_decisions', decision_data)
            
            # Update application status based on decision
            status_map = {
                'approved': 'approved',
                'rejected': 'rejected',
                'referred': 'under_review',
                'pending_information': 'incomplete'
            }
            
            new_status = status_map.get(decision, 'under_review')
            
            query = """
                UPDATE insurance_ai.applications
                SET status = %(new_status)s
                WHERE id = %(application_id)s
            """
            
            execute_query(query, {
                'new_status': new_status,
                'application_id': application['id']
            }, commit=True)
            
            # Log the underwriting decision
            self.config_agent.log_audit_event(
                'application',
                str(application['id']),
                'decision',
                'underwriting_flow',
                {
                    'decision': decision,
                    'risk_score': risk_score
                }
            )
            
            # Return the decision
            return {
                'application_id': application_id,
                'decision': decision,
                'risk_score': risk_score,
                'decision_factors': decision_factors
            }
            
        except Exception as e:
            logger.error(f"Error processing application {application_id}: {e}")
            return {'error': str(e)}
    
    def _calculate_risk_score(self, application_data: Dict, underwriting_config: Dict) -> tuple:
        """
        Calculate risk score based on application data and underwriting rules.
        
        Args:
            application_data: Application data dictionary
            underwriting_config: Underwriting configuration dictionary
            
        Returns:
            Tuple of (risk_score, decision_factors)
        """
        # Default risk score
        risk_score = 50.0
        decision_factors = {}
        
        # Get risk factors from configuration
        risk_factors = underwriting_config.get('risk_factors', {})
        
        # Apply risk factors
        for factor, config in risk_factors.items():
            if factor in application_data:
                factor_value = application_data[factor]
                factor_score = self._evaluate_factor(factor_value, config)
                risk_score += factor_score
                decision_factors[factor] = factor_score
        
        # Ensure risk score is within bounds
        risk_score = max(0.0, min(100.0, risk_score))
        
        return risk_score, decision_factors
    
    def _evaluate_factor(self, factor_value: Any, factor_config: Dict) -> float:
        """
        Evaluate a single risk factor.
        
        Args:
            factor_value: Value of the factor from application data
            factor_config: Configuration for the factor
            
        Returns:
            Score adjustment for the factor
        """
        factor_type = factor_config.get('type', 'string')
        
        if factor_type == 'numeric':
            return self._evaluate_numeric_factor(factor_value, factor_config)
        elif factor_type == 'categorical':
            return self._evaluate_categorical_factor(factor_value, factor_config)
        elif factor_type == 'boolean':
            return self._evaluate_boolean_factor(factor_value, factor_config)
        else:
            return 0.0
    
    def _evaluate_numeric_factor(self, value: Any, config: Dict) -> float:
        """Evaluate a numeric risk factor."""
        try:
            value = float(value)
            ranges = config.get('ranges', [])
            
            for range_config in ranges:
                min_val = range_config.get('min', float('-inf'))
                max_val = range_config.get('max', float('inf'))
                
                if min_val <= value <= max_val:
                    return range_config.get('score', 0.0)
            
            return 0.0
        except (ValueError, TypeError):
            return config.get('default_score', 0.0)
    
    def _evaluate_categorical_factor(self, value: Any, config: Dict) -> float:
        """Evaluate a categorical risk factor."""
        categories = config.get('categories', {})
        return categories.get(str(value), config.get('default_score', 0.0))
    
    def _evaluate_boolean_factor(self, value: Any, config: Dict) -> float:
        """Evaluate a boolean risk factor."""
        if isinstance(value, bool):
            return config.get('true_score', 0.0) if value else config.get('false_score', 0.0)
        elif isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ('true', 'yes', 'y', '1'):
                return config.get('true_score', 0.0)
            elif value_lower in ('false', 'no', 'n', '0'):
                return config.get('false_score', 0.0)
        
        return config.get('default_score', 0.0)
    
    def _determine_decision(self, risk_score: float, underwriting_config: Dict) -> str:
        """
        Determine underwriting decision based on risk score.
        
        Args:
            risk_score: Calculated risk score
            underwriting_config: Underwriting configuration dictionary
            
        Returns:
            Decision string: 'approved', 'rejected', 'referred', or 'pending_information'
        """
        thresholds = underwriting_config.get('decision_thresholds', {})
        
        if risk_score <= thresholds.get('approve_threshold', 30.0):
            return 'approved'
        elif risk_score >= thresholds.get('reject_threshold', 70.0):
            return 'rejected'
        elif risk_score >= thresholds.get('refer_threshold', 50.0):
            return 'referred'
        else:
            return 'pending_information'
    
    def get_underwriting_decision(self, application_id: str) -> Optional[Dict]:
        """
        Get the underwriting decision for an application.
        
        Args:
            application_id: Unique identifier for the application
            
        Returns:
            Decision dictionary if found, None otherwise
        """
        try:
            # First get the application to get its UUID
            query = """
                SELECT id FROM insurance_ai.applications
                WHERE application_id = %(application_id)s
            """
            
            app_results = execute_query(query, {'application_id': application_id})
            
            if not app_results:
                logger.warning(f"Application not found: {application_id}")
                return None
            
            app_uuid = app_results[0]['id']
            
            # Now get the decision
            query = """
                SELECT * FROM insurance_ai.underwriting_decisions
                WHERE application_id = %(app_uuid)s
                ORDER BY created_at DESC
                LIMIT 1
            """
            
            decision_results = execute_query(query, {'app_uuid': app_uuid})
            
            if decision_results:
                return decision_results[0]
            
            logger.warning(f"No underwriting decision found for application: {application_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting underwriting decision for {application_id}: {e}")
            return None
