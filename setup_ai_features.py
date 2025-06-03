#!/usr/bin/env python3
"""
AI Features Setup and Enhancement Script

This script sets up and enhances AI features for the Insurance AI System,
including OpenAI and local LLM integration.
"""

import os
import sys
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings
from ai_services.ai_service_manager import AIServiceManager
from ai_services.llm_providers import OpenAIProvider, LocalLLMProvider

logger = logging.getLogger(__name__)

class AISetupManager:
    """Manager for setting up and testing AI features."""
    
    def __init__(self):
        self.settings = get_settings()
        self.ai_manager = None
        
    async def setup_ai_environment(self):
        """Set up AI environment variables and configuration."""
        print("🤖 Setting up AI Environment...")
        
        # Check for existing API keys
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not openai_key:
            print("⚠️  OPENAI_API_KEY not found in environment")
            print("   To use OpenAI, set: export OPENAI_API_KEY='your-api-key'")
        else:
            print(f"✅ OpenAI API key found: {openai_key[:8]}...")
            
        if not anthropic_key:
            print("⚠️  ANTHROPIC_API_KEY not found in environment")
            print("   To use Anthropic, set: export ANTHROPIC_API_KEY='your-api-key'")
        else:
            print(f"✅ Anthropic API key found: {anthropic_key[:8]}...")
            
        # Set up default AI configuration
        ai_config = {
            'AI_ENABLED': 'true',
            'AI_PROVIDER': 'openai' if openai_key else 'local',
            'AI_MODEL': 'gpt-3.5-turbo' if openai_key else 'llama2:7b',
            'AI_TEMPERATURE': '0.7',
            'AI_MAX_TOKENS': '2000',
            'AI_ENABLE_FALLBACK': 'true',
            'AI_ENABLE_CACHING': 'true',
            'LOCAL_LLM_BASE_URL': 'http://localhost:11434',
            'LOCAL_LLM_PROVIDER_TYPE': 'ollama'
        }
        
        # Set environment variables if not already set
        for key, value in ai_config.items():
            if not os.getenv(key):
                os.environ[key] = value
                print(f"   Set {key}={value}")
        
        print("✅ AI environment configured")
        
    async def test_ai_providers(self):
        """Test available AI providers."""
        print("\n🧪 Testing AI Providers...")
        
        self.ai_manager = AIServiceManager()
        await self.ai_manager.initialize()
        
        # Test OpenAI if available
        if os.getenv('OPENAI_API_KEY'):
            await self._test_openai()
        
        # Test local LLM if available
        await self._test_local_llm()
        
        # Test Anthropic if available
        if os.getenv('ANTHROPIC_API_KEY'):
            await self._test_anthropic()
            
    async def _test_openai(self):
        """Test OpenAI connection."""
        try:
            print("   Testing OpenAI connection...")
            config = {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 100
            }
            
            provider = OpenAIProvider(config)
            response = await provider.generate_response(
                "Test message: Respond with 'OpenAI connection successful'"
            )
            
            if response.error:
                print(f"   ❌ OpenAI test failed: {response.error}")
            else:
                print(f"   ✅ OpenAI test successful: {response.content[:50]}...")
                
        except Exception as e:
            print(f"   ❌ OpenAI test error: {e}")
            
    async def _test_local_llm(self):
        """Test local LLM connection."""
        try:
            print("   Testing local LLM connection...")
            config = {
                'base_url': os.getenv('LOCAL_LLM_BASE_URL', 'http://localhost:11434'),
                'model': os.getenv('LOCAL_LLM_MODEL', 'llama2:7b'),
                'provider_type': 'ollama',
                'temperature': 0.7,
                'max_tokens': 100
            }
            
            provider = LocalLLMProvider(config)
            response = await provider.generate_response(
                "Test message: Respond with 'Local LLM connection successful'"
            )
            
            if response.error:
                print(f"   ⚠️  Local LLM test failed: {response.error}")
                print("   💡 To use local LLM, install Ollama: https://ollama.ai")
                print("   💡 Then run: ollama pull llama2:7b")
            else:
                print(f"   ✅ Local LLM test successful: {response.content[:50]}...")
                
        except Exception as e:
            print(f"   ⚠️  Local LLM test error: {e}")
            
    async def _test_anthropic(self):
        """Test Anthropic connection."""
        try:
            print("   Testing Anthropic connection...")
            # Note: Anthropic provider would need to be implemented
            print("   ⚠️  Anthropic provider implementation pending")
                
        except Exception as e:
            print(f"   ❌ Anthropic test error: {e}")
            
    async def demonstrate_ai_features(self):
        """Demonstrate AI features with sample data."""
        print("\n🎯 Demonstrating AI Features...")
        
        if not self.ai_manager:
            self.ai_manager = AIServiceManager()
            await self.ai_manager.initialize()
            
        # Underwriting demo
        await self._demo_underwriting()
        
        # Claims demo
        await self._demo_claims()
        
        # Actuarial demo
        await self._demo_actuarial()
        
    async def _demo_underwriting(self):
        """Demo underwriting AI analysis."""
        print("\n   📋 Underwriting Analysis Demo:")
        
        sample_data = {
            "applicant_id": "UW-DEMO-001",
            "full_name": "Jane Smith",
            "age": 32,
            "income": 85000,
            "credit_score": 750,
            "debt_to_income_ratio": 0.20,
            "property_value": 350000,
            "loan_amount": 280000,
            "employment_history": "5 years at current job",
            "property_type": "Single family home"
        }
        
        try:
            response = await self.ai_manager.analyze_underwriting(sample_data)
            if response.error:
                print(f"      ❌ Error: {response.error}")
            else:
                print(f"      ✅ Analysis: {response.content[:200]}...")
                if hasattr(response, 'confidence'):
                    print(f"      📊 Confidence: {response.confidence}")
        except Exception as e:
            print(f"      ❌ Demo error: {e}")
            
    async def _demo_claims(self):
        """Demo claims AI analysis."""
        print("\n   ⚖️ Claims Analysis Demo:")
        
        sample_data = {
            "claim_id": "CLM-DEMO-001",
            "policy_number": "POL-789012",
            "claim_type": "auto_accident",
            "incident_date": "2024-01-20",
            "description": "Vehicle collision at intersection during heavy rain",
            "estimated_damage": 8500,
            "claimant_statement": "The other driver ran a red light and hit my car",
            "police_report": True,
            "witnesses": 2
        }
        
        try:
            response = await self.ai_manager.analyze_claims(sample_data)
            if response.error:
                print(f"      ❌ Error: {response.error}")
            else:
                print(f"      ✅ Analysis: {response.content[:200]}...")
                if hasattr(response, 'confidence'):
                    print(f"      📊 Confidence: {response.confidence}")
        except Exception as e:
            print(f"      ❌ Demo error: {e}")
            
    async def _demo_actuarial(self):
        """Demo actuarial AI analysis."""
        print("\n   📊 Actuarial Analysis Demo:")
        
        sample_data = {
            "analysis_id": "ACT-DEMO-001",
            "data_type": "claims_frequency",
            "time_period": "2023-Q4",
            "region": "Northeast",
            "policy_type": "auto",
            "claims_data": [
                {"month": "Oct", "claims": 145, "premiums": 250000},
                {"month": "Nov", "claims": 162, "premiums": 255000},
                {"month": "Dec", "claims": 178, "premiums": 260000}
            ]
        }
        
        try:
            response = await self.ai_manager.analyze_actuarial(sample_data)
            if response.error:
                print(f"      ❌ Error: {response.error}")
            else:
                print(f"      ✅ Analysis: {response.content[:200]}...")
                if hasattr(response, 'confidence'):
                    print(f"      📊 Confidence: {response.confidence}")
        except Exception as e:
            print(f"      ❌ Demo error: {e}")
            
    async def create_ai_config_file(self):
        """Create AI configuration file for easy setup."""
        print("\n📝 Creating AI Configuration File...")
        
        config = {
            "ai_configuration": {
                "enabled": True,
                "provider": os.getenv('AI_PROVIDER', 'openai'),
                "model": os.getenv('AI_MODEL', 'gpt-3.5-turbo'),
                "temperature": float(os.getenv('AI_TEMPERATURE', '0.7')),
                "max_tokens": int(os.getenv('AI_MAX_TOKENS', '2000')),
                "enable_fallback": True,
                "enable_caching": True
            },
            "providers": {
                "openai": {
                    "api_key": "YOUR_OPENAI_API_KEY_HERE",
                    "base_url": "https://api.openai.com/v1",
                    "models": ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
                },
                "local": {
                    "base_url": "http://localhost:11434",
                    "provider_type": "ollama",
                    "models": ["llama2:7b", "llama2:13b", "codellama:7b"]
                },
                "anthropic": {
                    "api_key": "YOUR_ANTHROPIC_API_KEY_HERE",
                    "models": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
                }
            },
            "features": {
                "enhanced_prompts": True,
                "multi_provider_fallback": True,
                "performance_monitoring": True,
                "caching": True
            }
        }
        
        config_file = project_root / "ai_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"   ✅ Configuration saved to: {config_file}")
        print("   💡 Edit this file to customize AI settings")
        
    def print_setup_instructions(self):
        """Print setup instructions for users."""
        print("\n" + "="*60)
        print("🚀 AI FEATURES SETUP COMPLETE!")
        print("="*60)
        print()
        print("📋 NEXT STEPS:")
        print()
        print("1. 🔑 Set up API Keys (if using cloud providers):")
        print("   export OPENAI_API_KEY='your-openai-api-key'")
        print("   export ANTHROPIC_API_KEY='your-anthropic-api-key'")
        print()
        print("2. 🏠 Set up Local LLM (optional):")
        print("   # Install Ollama")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("   # Pull a model")
        print("   ollama pull llama2:7b")
        print()
        print("3. 🎯 Test the Dashboard:")
        print("   python launch_dashboard.py")
        print("   # Then visit: http://localhost:8501")
        print()
        print("4. 🔧 API Testing:")
        print("   python -m uvicorn api:app --host 0.0.0.0 --port 8080")
        print("   # Then visit: http://localhost:8080/docs")
        print()
        print("📊 AVAILABLE AI FEATURES:")
        print("   • Underwriting Risk Assessment")
        print("   • Claims Fraud Detection")
        print("   • Actuarial Trend Analysis")
        print("   • Document Analysis")
        print("   • Automated Report Generation")
        print("   • Multi-provider Fallback")
        print("   • Performance Monitoring")
        print()
        print("🔗 INTEGRATION OPTIONS:")
        print("   • OpenAI GPT Models")
        print("   • Local LLMs (Ollama, vLLM, LM Studio)")
        print("   • Anthropic Claude (coming soon)")
        print("   • Custom Model Endpoints")
        print()

async def main():
    """Main setup function."""
    print("🏢 Insurance AI System - AI Features Setup")
    print("="*50)
    
    setup_manager = AISetupManager()
    
    try:
        # Setup AI environment
        await setup_manager.setup_ai_environment()
        
        # Test AI providers
        await setup_manager.test_ai_providers()
        
        # Demonstrate AI features
        await setup_manager.demonstrate_ai_features()
        
        # Create configuration file
        await setup_manager.create_ai_config_file()
        
        # Print instructions
        setup_manager.print_setup_instructions()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        logger.exception("Setup failed")

if __name__ == "__main__":
    asyncio.run(main())