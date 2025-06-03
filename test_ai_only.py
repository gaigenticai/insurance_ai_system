#!/usr/bin/env python3
"""
Simplified AI-only test that doesn't require database connections

This test focuses on the core AI functionality without external dependencies.
"""

import asyncio
import logging
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set environment variables for testing
os.environ['AI_ENABLED'] = 'true'
os.environ['AI_PROVIDER'] = 'local'  # Use local provider to avoid API key requirements
os.environ['LOCAL_LLM_BASE_URL'] = 'http://localhost:11434'
os.environ['ENABLE_MONITORING'] = 'false'  # Disable monitoring
os.environ['CACHE_ENABLED'] = 'false'  # Disable caching
os.environ['DEMO_MODE'] = 'true'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_ai_configuration():
    """Test AI configuration"""
    print("\n=== Testing AI Configuration ===")
    
    try:
        from config.settings import get_settings
        
        settings = get_settings()
        
        print(f"✅ AI Enabled: {settings.ai.enabled}")
        print(f"✅ AI Provider: {settings.ai.provider}")
        print(f"✅ AI Model: {settings.ai.model}")
        print(f"✅ App Environment: {settings.app.environment}")
        print(f"✅ App Debug: {settings.app.debug}")
        print(f"✅ Cache Enabled: {settings.cache.enabled}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Configuration: FAILED - {e}")
        return False

async def test_ai_service_manager_standalone():
    """Test AI service manager without external dependencies"""
    print("\n=== Testing AI Service Manager (Standalone) ===")
    
    try:
        from ai_services.ai_service_manager import AIServiceManager
        
        # Create AI service manager
        ai_manager = AIServiceManager()
        
        # Initialize
        await ai_manager.initialize()
        
        # Test health check
        health = await ai_manager.health_check()
        print(f"✅ Health Check: {health}")
        
        # Test provider status
        status = ai_manager.get_provider_status()
        print(f"✅ Provider Status: {status}")
        
        # Test available providers
        providers = ai_manager.get_available_providers()
        print(f"✅ Available Providers: {providers}")
        
        # Shutdown
        await ai_manager.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ AI Service Manager: FAILED - {e}")
        logger.exception("AI Service Manager test failed")
        return False

async def test_main_application_demo():
    """Test main application in demo mode"""
    print("\n=== Testing Main Application (Demo Mode) ===")
    
    try:
        from main import InsuranceAIApplication
        
        # Create application
        app = InsuranceAIApplication()
        
        # Initialize
        await app.initialize()
        
        # Test health check
        health = await app.health_check()
        print(f"✅ Application Health: {health.get('status', 'unknown')}")
        
        # Test demo scenarios (this should work even without real AI providers)
        print("✅ Running demo scenarios...")
        await app.run_demo_scenarios()
        
        # Shutdown
        await app.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Main Application: FAILED - {e}")
        logger.exception("Main Application test failed")
        return False

async def test_service_registry_only():
    """Test service registry in isolation"""
    print("\n=== Testing Service Registry (Isolated) ===")
    
    try:
        from core.service_registry import ServiceRegistry, ServiceInterface
        
        # Create test service
        class MockAIService(ServiceInterface):
            def __init__(self):
                self.initialized = False
            
            async def initialize(self):
                self.initialized = True
                print("Mock AI service initialized")
            
            async def health_check(self):
                return self.initialized
            
            async def shutdown(self):
                self.initialized = False
                print("Mock AI service shutdown")
        
        # Test registry
        registry = ServiceRegistry()
        registry.register_singleton(MockAIService, MockAIService)
        
        # Get service
        service = await registry.get(MockAIService)
        assert service.initialized, "Service should be initialized"
        
        # Health check
        health = await registry.health_check()
        print(f"✅ Registry Health: {health}")
        
        # Shutdown
        await registry.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Service Registry: FAILED - {e}")
        logger.exception("Service Registry test failed")
        return False

async def run_ai_only_tests():
    """Run AI-focused tests without external dependencies"""
    print("🚀 Starting AI-Only Integration Tests")
    print("=" * 60)
    
    tests = [
        ("AI Configuration", test_ai_configuration),
        ("Service Registry (Isolated)", test_service_registry_only),
        ("AI Service Manager (Standalone)", test_ai_service_manager_standalone),
        ("Main Application (Demo Mode)", test_main_application_demo),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏁 AI-Only Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All AI tests passed! Core AI functionality is working.")
        return 0
    else:
        print("⚠️  Some AI tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_ai_only_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner crashed: {e}")
        sys.exit(1)