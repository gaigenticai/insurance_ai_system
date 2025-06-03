#!/usr/bin/env python3
"""
Test script for AI integration in the Insurance AI System.
Tests AI-enhanced underwriting, claims, and actuarial flows.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.config_agent import ConfigAgent
from ai_services.ai_service_manager import AIServiceManager
from ai_services.ai_agents import AIUnderwritingAgent, AIClaimsAgent, AIActuarialAgent
from modules.underwriting.flow import UnderwritingFlow
from modules.claims.flow import ClaimsFlow
from modules.actuarial.flow import ActuarialFlow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIIntegrationTester:
    """Test AI integration across all insurance modules."""
    
    def __init__(self):
        """Initialize the tester with configuration and AI services."""
        self.config_agent = ConfigAgent()
        self.ai_service_manager = AIServiceManager(self.config_agent)
        
        # Initialize flows
        self.underwriting_flow = UnderwritingFlow(self.config_agent)
        self.claims_flow = ClaimsFlow(self.config_agent)
        self.actuarial_flow = ActuarialFlow(self.config_agent)
        
        # Test data
        self.institution_id = "institution_a"
        
    def setup_test_environment(self):
        """Set up test environment with mock AI configuration."""
        logger.info("Setting up test environment...")
        
        # Set environment variables for testing (using mock values)
        os.environ.setdefault("OPENAI_API_KEY", "test-key-openai")
        os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-anthropic")
        os.environ.setdefault("AI_PROVIDER", "openai")
        os.environ.setdefault("AI_MODEL", "gpt-3.5-turbo")
        os.environ.setdefault("AI_TEMPERATURE", "0.7")
        os.environ.setdefault("AI_MAX_TOKENS", "2000")
        
        logger.info("Test environment configured")
    
    async def test_ai_underwriting_agent(self):
        """Test AI underwriting agent."""
        logger.info("Testing AI Underwriting Agent...")
        
        test_application = {
            "applicant_name": "John Doe",
            "age": 35,
            "occupation": "Software Engineer",
            "annual_income": 85000,
            "credit_score": 750,
            "coverage_amount": 500000,
            "policy_type": "term_life",
            "health_conditions": ["none"],
            "smoking_status": "non_smoker",
            "driving_record": "clean"
        }
        
        try:
            ai_agent = AIUnderwritingAgent(self.config_agent)
            result = await ai_agent.execute(test_application, self.institution_id)
            
            logger.info("AI Underwriting Agent Result:")
            logger.info(json.dumps(result, indent=2, default=str))
            
            # Verify result structure
            assert "risk_assessment" in result
            assert "recommendation" in result
            assert "confidence_score" in result
            
            logger.info("✅ AI Underwriting Agent test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ AI Underwriting Agent test failed: {str(e)}")
            return False
    
    async def test_ai_claims_agent(self):
        """Test AI claims agent."""
        logger.info("Testing AI Claims Agent...")
        
        test_claim = {
            "claim_id": "CLM-AI-001",
            "policy_id": "POLICY_ACTIVE_001",
            "claimed_amount": 2500,
            "claim_description": "Vehicle collision damage to front bumper and headlight",
            "claim_date": "2025-06-01",
            "incident_location": "Main Street intersection",
            "police_report": True,
            "photos_provided": True,
            "witness_statements": 2
        }
        
        try:
            ai_agent = AIClaimsAgent(self.config_agent)
            result = await ai_agent.execute(test_claim, self.institution_id)
            
            logger.info("AI Claims Agent Result:")
            logger.info(json.dumps(result, indent=2, default=str))
            
            # Verify result structure
            assert "fraud_assessment" in result
            assert "damage_evaluation" in result
            assert "settlement_recommendation" in result
            
            logger.info("✅ AI Claims Agent test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ AI Claims Agent test failed: {str(e)}")
            return False
    
    async def test_ai_actuarial_agent(self):
        """Test AI actuarial agent."""
        logger.info("Testing AI Actuarial Agent...")
        
        test_data = {
            "normalized_data": {
                "claims_data": [
                    {"amount": 1000, "type": "auto", "date": "2025-01-15"},
                    {"amount": 2500, "type": "auto", "date": "2025-02-20"},
                    {"amount": 800, "type": "property", "date": "2025-03-10"}
                ],
                "policy_data": [
                    {"premium": 1200, "coverage": 50000, "type": "auto"},
                    {"premium": 800, "coverage": 100000, "type": "property"}
                ]
            },
            "analysis_results": {
                "claim_frequency": 0.15,
                "average_claim_amount": 1433,
                "loss_ratio": 0.65
            }
        }
        
        try:
            ai_agent = AIActuarialAgent(self.config_agent)
            result = await ai_agent.execute(test_data, self.institution_id)
            
            logger.info("AI Actuarial Agent Result:")
            logger.info(json.dumps(result, indent=2, default=str))
            
            # Verify result structure
            assert "risk_modeling" in result
            assert "pricing_recommendations" in result
            assert "trend_analysis" in result
            
            logger.info("✅ AI Actuarial Agent test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ AI Actuarial Agent test failed: {str(e)}")
            return False
    
    def test_underwriting_flow_with_ai(self):
        """Test underwriting flow with AI integration."""
        logger.info("Testing Underwriting Flow with AI...")
        
        test_application = {
            "application_id": "APP-AI-001",
            "applicant_name": "Jane Smith",
            "age": 28,
            "occupation": "Teacher",
            "annual_income": 55000,
            "credit_score": 720,
            "coverage_amount": 300000,
            "policy_type": "term_life"
        }
        
        try:
            result = self.underwriting_flow.run(test_application, self.institution_id)
            
            logger.info("Underwriting Flow with AI Result:")
            logger.info(json.dumps(result, indent=2, default=str))
            
            # Verify AI insights are included
            if "ai_insights" in result:
                logger.info("✅ AI insights included in underwriting flow")
            else:
                logger.warning("⚠️ AI insights not found in underwriting flow result")
            
            logger.info("✅ Underwriting Flow with AI test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Underwriting Flow with AI test failed: {str(e)}")
            return False
    
    def test_claims_flow_with_ai(self):
        """Test claims flow with AI integration."""
        logger.info("Testing Claims Flow with AI...")
        
        test_claim = {
            "claim_id": "CLM-AI-002",
            "policy_id": "POLICY_ACTIVE_001",
            "claimed_amount": 1800,
            "claim_description": "Water damage from burst pipe",
            "claim_date": "2025-06-02"
        }
        
        try:
            result = self.claims_flow.run(test_claim, self.institution_id)
            
            logger.info("Claims Flow with AI Result:")
            logger.info(json.dumps(result, indent=2, default=str))
            
            # Verify AI insights are included
            if "ai_insights" in result:
                logger.info("✅ AI insights included in claims flow")
            else:
                logger.warning("⚠️ AI insights not found in claims flow result")
            
            logger.info("✅ Claims Flow with AI test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Claims Flow with AI test failed: {str(e)}")
            return False
    
    def test_actuarial_flow_with_ai(self):
        """Test actuarial flow with AI integration."""
        logger.info("Testing Actuarial Flow with AI...")
        
        # Use the existing sample data file
        data_source = {
            "data_path": "/workspace/insurance_ai_system/data/sample_actuarial_input.json"
        }
        
        try:
            result = self.actuarial_flow.run(data_source, self.institution_id)
            
            logger.info("Actuarial Flow with AI Result:")
            logger.info(json.dumps(result, indent=2, default=str))
            
            # Verify AI insights are included
            if "ai_insights" in result:
                logger.info("✅ AI insights included in actuarial flow")
            else:
                logger.warning("⚠️ AI insights not found in actuarial flow result")
            
            logger.info("✅ Actuarial Flow with AI test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Actuarial Flow with AI test failed: {str(e)}")
            return False
    
    def test_ai_configuration(self):
        """Test AI configuration management."""
        logger.info("Testing AI Configuration...")
        
        try:
            # Test getting AI configuration
            config = self.config_agent.get_ai_configuration()
            logger.info(f"Current AI Configuration: {config}")
            
            # Test updating AI configuration
            new_config = {
                "provider": "openai",
                "model_name": "gpt-4",
                "temperature": 0.5,
                "max_tokens": 1500
            }
            
            updated_config = self.config_agent.update_ai_configuration(new_config)
            logger.info(f"Updated AI Configuration: {updated_config}")
            
            logger.info("✅ AI Configuration test passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ AI Configuration test failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all AI integration tests."""
        logger.info("🚀 Starting AI Integration Tests...")
        
        # Setup test environment
        self.setup_test_environment()
        
        test_results = []
        
        # Test individual AI agents
        test_results.append(await self.test_ai_underwriting_agent())
        test_results.append(await self.test_ai_claims_agent())
        test_results.append(await self.test_ai_actuarial_agent())
        
        # Test flows with AI integration
        test_results.append(self.test_underwriting_flow_with_ai())
        test_results.append(self.test_claims_flow_with_ai())
        test_results.append(self.test_actuarial_flow_with_ai())
        
        # Test configuration
        test_results.append(self.test_ai_configuration())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        logger.info(f"\n📊 Test Results Summary:")
        logger.info(f"Passed: {passed_tests}/{total_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            logger.info("🎉 All AI integration tests passed!")
        else:
            logger.warning(f"⚠️ {total_tests - passed_tests} tests failed")
        
        return passed_tests == total_tests

async def main():
    """Main test execution function."""
    tester = AIIntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("✅ AI Integration testing completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ AI Integration testing failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())