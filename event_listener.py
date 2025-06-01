"""
Event listener module for the Insurance AI System.
Listens for events from Redis Streams and processes them.
"""

import logging
import os
import time
from typing import Dict, Any

from events import EventSubscriber
from db_connection import insert_record, update_record, get_record_by_id
from utils.logging_utils import audit_logger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables
INSTITUTION_ID = os.environ.get('INSTITUTION_ID', 'default')


def handle_underwriting_completed(payload: Dict[str, Any]):
    """
    Handle underwriting completed event.
    
    Args:
        payload: Event payload
    """
    logger.info(f"Processing underwriting completed event: {payload.get('event_id')}")
    
    try:
        application_id = payload.get('application_id')
        decision = payload.get('decision')
        risk_score = payload.get('risk_score')
        institution_id = payload.get('institution_id', INSTITUTION_ID)
        
        # Log the event
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="EventListener",
            event_type="UNDERWRITING_COMPLETED_PROCESSED",
            details={
                "application_id": application_id,
                "decision": decision,
                "risk_score": risk_score
            },
            severity="INFO"
        )
        
        # Update application status in database
        try:
            # Get application by application_id
            query = f"""
                SELECT id FROM insurance_ai.applications 
                WHERE application_id = '{application_id}'
            """
            result = get_record_by_id('applications', application_id, id_column='application_id')
            
            if result:
                # Update application status
                update_record(
                    'applications',
                    result.get('id'),
                    {
                        'status': 'completed',
                        'updated_at': 'NOW()'
                    }
                )
                
                # Insert underwriting decision
                insert_record(
                    'underwriting_decisions',
                    {
                        'application_id': result.get('id'),
                        'decision': decision,
                        'decision_factors': payload,
                        'risk_score': risk_score,
                        'created_by': 'event_listener'
                    }
                )
                
                logger.info(f"Updated application status for {application_id}")
            else:
                logger.warning(f"Application not found: {application_id}")
        except Exception as e:
            logger.error(f"Error updating application status: {e}")
    except Exception as e:
        logger.error(f"Error processing underwriting completed event: {e}")


def handle_claims_flagged(payload: Dict[str, Any]):
    """
    Handle claims flagged event.
    
    Args:
        payload: Event payload
    """
    logger.info(f"Processing claims flagged event: {payload.get('event_id')}")
    
    try:
        claim_id = payload.get('claim_id')
        flag_reason = payload.get('flag_reason')
        severity = payload.get('severity', 'medium')
        institution_id = payload.get('institution_id', INSTITUTION_ID)
        
        # Log the event
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="EventListener",
            event_type="CLAIMS_FLAGGED_PROCESSED",
            details={
                "claim_id": claim_id,
                "flag_reason": flag_reason,
                "severity": severity
            },
            severity="WARNING"
        )
        
        # Update claim status in database
        try:
            # Get claim by claim_id
            result = get_record_by_id('claims', claim_id, id_column='claim_id')
            
            if result:
                # Update claim status
                update_record(
                    'claims',
                    result.get('id'),
                    {
                        'status': 'flagged',
                        'updated_at': 'NOW()'
                    }
                )
                
                # Insert claim decision
                insert_record(
                    'claim_decisions',
                    {
                        'claim_id': result.get('id'),
                        'decision': 'flagged',
                        'decision_factors': {
                            'flag_reason': flag_reason,
                            'severity': severity
                        },
                        'created_by': 'event_listener'
                    }
                )
                
                logger.info(f"Updated claim status for {claim_id}")
            else:
                logger.warning(f"Claim not found: {claim_id}")
        except Exception as e:
            logger.error(f"Error updating claim status: {e}")
    except Exception as e:
        logger.error(f"Error processing claims flagged event: {e}")


def handle_actuarial_benchmarked(payload: Dict[str, Any]):
    """
    Handle actuarial benchmarked event.
    
    Args:
        payload: Event payload
    """
    logger.info(f"Processing actuarial benchmarked event: {payload.get('event_id')}")
    
    try:
        analysis_id = payload.get('analysis_id')
        benchmark_results = payload.get('benchmark_results', {})
        institution_id = payload.get('institution_id', INSTITUTION_ID)
        
        # Log the event
        audit_logger.log_audit_event(
            institution_id=institution_id,
            agent_name="EventListener",
            event_type="ACTUARIAL_BENCHMARKED_PROCESSED",
            details={
                "analysis_id": analysis_id,
                "benchmark_results": benchmark_results
            },
            severity="INFO"
        )
        
        # Update actuarial analysis in database
        try:
            # Get analysis by analysis_id
            result = get_record_by_id('actuarial_analyses', analysis_id, id_column='analysis_id')
            
            if result:
                # Update analysis status and results
                update_record(
                    'actuarial_analyses',
                    result.get('id'),
                    {
                        'status': 'benchmarked',
                        'results': {
                            **result.get('results', {}),
                            'benchmark_results': benchmark_results
                        },
                        'updated_at': 'NOW()'
                    }
                )
                
                logger.info(f"Updated actuarial analysis for {analysis_id}")
            else:
                logger.warning(f"Actuarial analysis not found: {analysis_id}")
        except Exception as e:
            logger.error(f"Error updating actuarial analysis: {e}")
    except Exception as e:
        logger.error(f"Error processing actuarial benchmarked event: {e}")


def main():
    """Main function."""
    logger.info("Starting event listener")
    
    # Create event subscriber
    subscriber = EventSubscriber(
        event_types=[
            "underwriting.completed",
            "claims.flagged",
            "actuarial.benchmarked"
        ],
        consumer_group="insurance_ai_event_listeners",
        consumer_name="main_event_listener"
    )
    
    # Register handlers
    subscriber.register_handler("underwriting.completed", handle_underwriting_completed)
    subscriber.register_handler("claims.flagged", handle_claims_flagged)
    subscriber.register_handler("actuarial.benchmarked", handle_actuarial_benchmarked)
    
    # Start listening for events
    logger.info("Listening for events...")
    
    try:
        subscriber.start()
    except KeyboardInterrupt:
        logger.info("Event listener stopped")
    except Exception as e:
        logger.error(f"Error in event listener: {e}")
        # Wait and retry
        time.sleep(5)
        main()


if __name__ == "__main__":
    main()
