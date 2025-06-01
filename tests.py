"""
Test module for the Insurance AI System.
Validates functionality of the enhanced system.
"""

import os
import unittest
import json
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from api import app
from db_connection import execute_query, insert_record, get_record_by_id
from tasks import run_underwriting_task, run_claims_task, run_actuarial_task
from events import publish_event
from schemas import TaskStatus, TaskType, EventType


class TestDatabaseConnection(unittest.TestCase):
    """Test database connection functionality."""
    
    @patch('db_connection.get_db_cursor')
    def test_execute_query(self, mock_get_db_cursor):
        """Test execute_query function."""
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchall.return_value = [{"id": 1, "name": "test"}]
        mock_get_db_cursor.return_value = mock_cursor
        
        # Execute query
        result = execute_query("SELECT * FROM test")
        
        # Assert
        self.assertEqual(result, [{"id": 1, "name": "test"}])
        mock_cursor.__enter__.return_value.execute.assert_called_once()
    
    @patch('db_connection.get_db_cursor')
    def test_insert_record(self, mock_get_db_cursor):
        """Test insert_record function."""
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchone.return_value = {"id": 1}
        mock_get_db_cursor.return_value = mock_cursor
        
        # Insert record
        result = insert_record("test", {"name": "test"})
        
        # Assert
        self.assertEqual(result, {"id": 1})
        mock_cursor.__enter__.return_value.execute.assert_called_once()
    
    @patch('db_connection.get_db_cursor')
    def test_get_record_by_id(self, mock_get_db_cursor):
        """Test get_record_by_id function."""
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchone.return_value = {"id": 1, "name": "test"}
        mock_get_db_cursor.return_value = mock_cursor
        
        # Get record
        result = get_record_by_id("test", 1)
        
        # Assert
        self.assertEqual(result, {"id": 1, "name": "test"})
        mock_cursor.__enter__.return_value.execute.assert_called_once()


class TestAPI(unittest.TestCase):
    """Test API functionality."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
    
    @patch('api.validate_institution')
    @patch('api.run_underwriting_task')
    @patch('api.create_task_record')
    def test_run_underwriting(self, mock_create_task_record, mock_run_underwriting_task, mock_validate_institution):
        """Test run_underwriting endpoint."""
        # Mock dependencies
        mock_validate_institution.return_value = "test_institution"
        mock_run_underwriting_task.apply_async.return_value = MagicMock()
        
        # Make request
        response = self.client.post(
            "/run/underwriting",
            json={
                "applicant_id": "test_applicant",
                "full_name": "Test Applicant",
                "address": "123 Test St",
                "date_of_birth": "01/01/1990",
                "income": 50000,
                "credit_score": 700,
                "debt_to_income_ratio": 0.3,
                "address_location_tag": "SafeZoneA",
                "document_text": "Test document"
            },
            headers={"X-Institution-ID": "test_institution"}
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        mock_create_task_record.assert_called_once()
        mock_run_underwriting_task.apply_async.assert_called_once()


@pytest.mark.asyncio
class TestCeleryTasks:
    """Test Celery tasks."""
    
    @patch('tasks.ConfigAgent')
    @patch('tasks.UnderwritingFlow')
    @patch('tasks.publish_event')
    @patch('tasks.update_record')
    def test_run_underwriting_task(self, mock_update_record, mock_publish_event, mock_underwriting_flow, mock_config_agent):
        """Test run_underwriting_task function."""
        # Mock dependencies
        mock_config_agent.return_value = MagicMock()
        mock_underwriting_flow.return_value.process_application.return_value = {
            "decision": "approved",
            "risk_score": 0.8
        }
        
        # Create mock task
        mock_task = MagicMock()
        mock_task.request.id = "test_task_id"
        
        # Run task
        with patch.object(run_underwriting_task, 'request', mock_task.request):
            result = run_underwriting_task({"applicant_id": "test_applicant"}, "test_institution")
        
        # Assert
        self.assertEqual(result["decision"], "approved")
        self.assertEqual(result["risk_score"], 0.8)
        mock_underwriting_flow.return_value.process_application.assert_called_once_with("test_applicant")
        mock_publish_event.assert_called_once()


class TestEvents:
    """Test event broker functionality."""
    
    @patch('events.redis_client')
    @patch('events.insert_record')
    def test_publish_event(self, mock_insert_record, mock_redis_client):
        """Test publish_event function."""
        # Mock dependencies
        mock_redis_client.xadd.return_value = "test_event_id"
        
        # Publish event
        result = publish_event(
            EventType.UNDERWRITING_COMPLETED.value,
            {
                "application_id": "test_applicant",
                "decision": "approved",
                "risk_score": 0.8,
                "institution_id": "test_institution"
            }
        )
        
        # Assert
        assert result is True
        mock_redis_client.xadd.assert_called_once()
        mock_insert_record.assert_called_once()


if __name__ == "__main__":
    unittest.main()
