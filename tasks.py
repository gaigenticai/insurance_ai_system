"""
Celery tasks for the Insurance AI System.
Wraps existing flow functions as asynchronous Celery tasks.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from celery import Task
from celery.utils.log import get_task_logger

from celery_app import celery_app
from agents.config_agent import ConfigAgent
from modules.underwriting.flow import UnderwritingFlow
from modules.claims.flow import ClaimsFlow
from modules.actuarial.flow import ActuarialFlow
from db_connection import insert_record, update_record, get_record_by_id, execute_query
from events import publish_event
from schemas import TaskStatus, TaskType, EventType

# Configure logging
logger = get_task_logger(__name__)


class BaseTask(Task):
    """Base task class with common functionality."""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Task {task_id} failed: {exc}")
        
        # Update task status in database
        try:
            update_record(
                'tasks',
                task_id,
                {
                    'status': TaskStatus.FAILURE.value,
                    'error': str(exc),
                    'updated_at': datetime.utcnow()
                },
                id_column='task_id'
            )
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        logger.info(f"Task {task_id} completed successfully")
        
        # Update task status in database
        try:
            update_record(
                'tasks',
                task_id,
                {
                    'status': TaskStatus.SUCCESS.value,
                    'result': retval,
                    'updated_at': datetime.utcnow()
                },
                id_column='task_id'
            )
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")


@celery_app.task(bind=True, base=BaseTask)
def run_underwriting_task(self, application_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
    """
    Process an underwriting application asynchronously.
    
    Args:
        application_data: Application data dictionary
        institution_id: Institution identifier
        
    Returns:
        Dictionary containing the underwriting decision and details
    """
    task_id = self.request.id
    logger.info(f"Starting underwriting task {task_id} for institution {institution_id}")
    
    try:
        # Initialize configuration agent
        config_agent = ConfigAgent(institution_id)
        
        # Initialize underwriting flow
        flow = UnderwritingFlow(config_agent)
        
        # Process application
        result = flow.process_application(application_data.get('applicant_id'))
        
        # Publish event
        if result and 'error' not in result:
            publish_event(
                EventType.UNDERWRITING_COMPLETED.value,
                {
                    'application_id': application_data.get('applicant_id'),
                    'decision': result.get('decision'),
                    'risk_score': result.get('risk_score'),
                    'institution_id': institution_id
                }
            )
        
        return result
    except Exception as e:
        logger.error(f"Error in underwriting task: {e}")
        raise


@celery_app.task(bind=True, base=BaseTask)
def run_claims_task(self, claim_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
    """
    Process a claim asynchronously.
    
    Args:
        claim_data: Claim data dictionary
        institution_id: Institution identifier
        
    Returns:
        Dictionary containing the claim processing result
    """
    task_id = self.request.id
    logger.info(f"Starting claims task {task_id} for institution {institution_id}")
    
    try:
        # Initialize configuration agent
        config_agent = ConfigAgent(institution_id)
        
        # Initialize claims flow
        flow = ClaimsFlow(config_agent)
        
        # Process claim
        result = flow.process_claim(claim_data)
        
        # Check if claim was flagged
        if result and result.get('flagged'):
            # Publish event
            publish_event(
                EventType.CLAIMS_FLAGGED.value,
                {
                    'claim_id': claim_data.get('claim_id'),
                    'flag_reason': result.get('flag_reason'),
                    'severity': result.get('severity', 'medium'),
                    'institution_id': institution_id
                }
            )
        
        return result
    except Exception as e:
        logger.error(f"Error in claims task: {e}")
        raise


@celery_app.task(bind=True, base=BaseTask)
def run_actuarial_task(self, data_source_info: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
    """
    Run actuarial analysis asynchronously.
    
    Args:
        data_source_info: Data source information dictionary
        institution_id: Institution identifier
        
    Returns:
        Dictionary containing the actuarial analysis result
    """
    task_id = self.request.id
    logger.info(f"Starting actuarial task {task_id} for institution {institution_id}")
    
    try:
        # Initialize configuration agent
        config_agent = ConfigAgent(institution_id)
        
        # Initialize actuarial flow
        flow = ActuarialFlow(config_agent)
        
        # Run analysis
        result = flow.calculate_risk_model(data_source_info)
        
        # Check if benchmarking was performed
        if result and result.get('benchmarked'):
            # Publish event
            publish_event(
                EventType.ACTUARIAL_BENCHMARKED.value,
                {
                    'analysis_id': data_source_info.get('analysis_id'),
                    'benchmark_results': result.get('benchmark_results', {}),
                    'institution_id': institution_id
                }
            )
        
        return result
    except Exception as e:
        logger.error(f"Error in actuarial task: {e}")
        raise


@celery_app.task(bind=True, base=BaseTask)
def generate_report_task(self, report_type: str, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
    """
    Generate a report asynchronously.
    
    Args:
        report_type: Type of report to generate
        data: Data for the report
        institution_id: Institution identifier
        
    Returns:
        Dictionary containing the report details
    """
    task_id = self.request.id
    logger.info(f"Starting report generation task {task_id} for institution {institution_id}")
    
    try:
        # Initialize configuration agent
        config_agent = ConfigAgent(institution_id)
        
        # Generate report ID
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
        
        # Generate report content based on type
        if report_type == 'underwriting':
            from agents.underwriting.report_generator_agent import ReportGeneratorAgent
            agent = ReportGeneratorAgent(config_agent)
            content = agent.generate_report(data)
        elif report_type == 'claims':
            from agents.claims.report_generator_agent import ReportGeneratorAgent
            agent = ReportGeneratorAgent(config_agent)
            content = agent.generate_report(data)
        elif report_type == 'actuarial':
            from agents.actuarial.report_generator_agent import ReportGeneratorAgent
            agent = ReportGeneratorAgent(config_agent)
            content = agent.generate_report(data)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        # Save report to database
        report_data = {
            'report_id': report_id,
            'type': report_type,
            'content': content,
            'created_at': datetime.utcnow(),
            'institution_id': institution_id,
            'task_id': task_id
        }
        
        insert_record('reports', report_data)
        
        # Update task with report ID
        update_record(
            'tasks',
            task_id,
            {'report_id': report_id},
            id_column='task_id'
        )
        
        return {
            'report_id': report_id,
            'report_type': report_type,
            'content': content
        }
    except Exception as e:
        logger.error(f"Error in report generation task: {e}")
        raise


@celery_app.task
def cleanup_old_tasks():
    """Cleanup old tasks from the database."""
    try:
        # Delete tasks older than 30 days
        query = """
            DELETE FROM insurance_ai.tasks
            WHERE created_at < NOW() - INTERVAL '30 days'
        """
        
        execute_query(query, commit=True)
        logger.info("Cleaned up old tasks")
    except Exception as e:
        logger.error(f"Error cleaning up old tasks: {e}")
        raise


def create_task_record(task_id: str, task_type: str, institution_id: str) -> Dict[str, Any]:
    """
    Create a task record in the database.
    
    Args:
        task_id: Celery task ID
        task_type: Type of task
        institution_id: Institution identifier
        
    Returns:
        Dictionary containing the task record
    """
    try:
        task_data = {
            'task_id': task_id,
            'type': task_type,
            'status': TaskStatus.PENDING.value,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'institution_id': institution_id
        }
        
        insert_record('tasks', task_data)
        
        return task_data
    except Exception as e:
        logger.error(f"Error creating task record: {e}")
        raise


def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the status of a task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Dictionary containing the task status
    """
    try:
        return get_record_by_id('tasks', task_id, id_column='task_id')
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return None
