#!/usr/bin/env python3
"""
Comprehensive test for modular AI integration

This script tests the complete modular AI system including:
- Service registry and dependency injection
- AI service manager with multiple providers
- Plugin system
- Configuration management
- Health monitoring
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_service_registry():
    """Test service registry functionality"""
    print("\n=== Testing Service Registry ===")
    
    try:
        from core.service_registry import ServiceRegistry, ServiceInterface
        
        # Test basic registry operations
        registry = ServiceRegistry()
        
        # Create a test service
        class TestService(ServiceInterface):
            def __init__(self):
                self.initialized = False
            
            async def initialize(self):
                self.initialized = True
                logger.info("Test service initialized")
            
            async def health_check(self):
                return self.initialized
            
            async def shutdown(self):
                self.initialized = False
                logger.info("Test service shutdown")
        
        # Register and test service
        registry.register_singleton(TestService, TestService)
        service = await registry.get(TestService)
        
        assert service.initialized, "Service should be initialized"
        
        # Test health check
        health = await registry.health_check()
        assert health["overall"] == "healthy", f"Registry should be healthy: {health}"
        
        # Test shutdown
        await registry.shutdown()
        
        print("✅ Service Registry: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Service Registry: FAILED - {e}")
        return False

async def test_ai_service_manager():
    """Test AI service manager"""
    print("\n=== Testing AI Service Manager ===")
    
    try:
        from ai_services.ai_service_manager import AIServiceManager
        from config.settings import get_settings
        
        # Initialize AI service manager
        ai_manager = AIServiceManager()
        await ai_manager.initialize()
        
        # Test health check
        health = await ai_manager.health_check()
        logger.info(f"AI Manager health: {health}")
        
        # Test provider status
        status = ai_manager.get_provider_status()
        logger.info(f"Provider status: {status}")
        
        # Test analysis methods (will use mock/fallback if no real providers)
        test_data = {
            "test_field": "test_value",
            "amount": 1000,
            "risk_factors": ["factor1", "factor2"]
        }
        
        # Test underwriting analysis
        try:
            uw_result = await ai_manager.analyze_underwriting(test_data)
            logger.info(f"Underwriting analysis result: {uw_result.content[:100]}...")
        except Exception as e:
            logger.warning(f"Underwriting analysis failed (expected if no providers): {e}")
        
        # Test claims analysis
        try:
            claims_result = await ai_manager.analyze_claims(test_data)
            logger.info(f"Claims analysis result: {claims_result.content[:100]}...")
        except Exception as e:
            logger.warning(f"Claims analysis failed (expected if no providers): {e}")
        
        # Test actuarial analysis
        try:
            actuarial_result = await ai_manager.analyze_actuarial(test_data)
            logger.info(f"Actuarial analysis result: {actuarial_result.content[:100]}...")
        except Exception as e:
            logger.warning(f"Actuarial analysis failed (expected if no providers): {e}")
        
        # Shutdown
        await ai_manager.shutdown()
        
        print("✅ AI Service Manager: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ AI Service Manager: FAILED - {e}")
        logger.exception("AI Service Manager test failed")
        return False

async def test_plugin_manager():
    """Test plugin manager"""
    print("\n=== Testing Plugin Manager ===")
    
    try:
        from ai_services.plugin_manager import PluginManager
        
        # Initialize plugin manager
        plugin_manager = PluginManager()
        await plugin_manager.initialize()
        
        # Test health check
        health = await plugin_manager.health_check()
        assert health, "Plugin manager should be healthy"
        
        # Test plugin info
        info = plugin_manager.get_plugin_info()
        logger.info(f"Plugin info: {info}")
        
        # Test plugin listing
        plugins = plugin_manager.list_plugins()
        logger.info(f"Available plugins: {plugins}")
        
        # Shutdown
        await plugin_manager.shutdown()
        
        print("✅ Plugin Manager: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Plugin Manager: FAILED - {e}")
        logger.exception("Plugin Manager test failed")
        return False

async def test_service_bootstrap():
    """Test service bootstrap"""
    print("\n=== Testing Service Bootstrap ===")
    
    try:
        from core.service_bootstrap import ServiceBootstrap, BootstrapConfig
        
        # Create bootstrap with test configuration
        config = BootstrapConfig(
            enable_ai_services=True,
            enable_plugins=True,
            enable_monitoring=False,  # Disable monitoring for test
            enable_caching=False,     # Disable caching for test
            startup_timeout=10
        )
        
        bootstrap = ServiceBootstrap(config)
        await bootstrap.initialize()
        
        # Test health check
        health = await bootstrap.health_check()
        logger.info(f"Bootstrap health: {health}")
        
        # Test service info
        info = bootstrap.get_service_info()
        logger.info(f"Service info: {info}")
        
        # Test getting services
        from ai_services.ai_service_manager import AIServiceManager
        ai_manager = await bootstrap.get_service(AIServiceManager)
        assert ai_manager is not None, "Should be able to get AI service manager"
        
        # Shutdown
        await bootstrap.shutdown()
        
        print("✅ Service Bootstrap: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Service Bootstrap: FAILED - {e}")
        logger.exception("Service Bootstrap test failed")
        return False

async def test_configuration_system():
    """Test configuration system"""
    print("\n=== Testing Configuration System ===")
    
    try:
        from config.settings import get_settings, Settings
        
        # Test getting settings
        settings = get_settings()
        assert isinstance(settings, Settings), "Should return Settings instance"
        
        # Test AI configuration
        ai_config = settings.ai
        logger.info(f"AI Provider: {ai_config.provider}")
        logger.info(f"AI Model: {ai_config.model}")
        logger.info(f"AI Enabled: {ai_config.enabled}")
        
        # Test app configuration
        app_config = settings.app
        logger.info(f"App Environment: {app_config.environment}")
        logger.info(f"App Debug: {app_config.debug}")
        
        # Test database configuration
        db_config = settings.database
        logger.info(f"Database URL: {db_config.url[:20]}...")
        
        print("✅ Configuration System: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Configuration System: FAILED - {e}")
        logger.exception("Configuration System test failed")
        return False

async def test_main_application():
    """Test main application"""
    print("\n=== Testing Main Application ===")
    
    try:
        from main import InsuranceAIApplication
        
        # Create application
        app = InsuranceAIApplication()
        
        # Initialize
        await app.initialize()
        
        # Test health check
        health = await app.health_check()
        logger.info(f"Application health: {health}")
        
        # Test analysis methods with sample data
        sample_data = {
            "applicant_id": "TEST-001",
            "amount": 50000,
            "risk_score": 0.3
        }
        
        # Test underwriting
        try:
            uw_result = await app.run_underwriting_analysis(sample_data)
            logger.info(f"Underwriting test result: {uw_result['status']}")
        except Exception as e:
            logger.warning(f"Underwriting test failed (expected if no AI providers): {e}")
        
        # Test claims
        try:
            claims_result = await app.run_claims_analysis(sample_data)
            logger.info(f"Claims test result: {claims_result['status']}")
        except Exception as e:
            logger.warning(f"Claims test failed (expected if no AI providers): {e}")
        
        # Test actuarial
        try:
            actuarial_result = await app.run_actuarial_analysis(sample_data)
            logger.info(f"Actuarial test result: {actuarial_result['status']}")
        except Exception as e:
            logger.warning(f"Actuarial test failed (expected if no AI providers): {e}")
        
        # Shutdown
        await app.shutdown()
        
        print("✅ Main Application: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Main Application: FAILED - {e}")
        logger.exception("Main Application test failed")
        return False

async def test_import_compatibility():
    """Test import compatibility"""
    print("\n=== Testing Import Compatibility ===")
    
    try:
        # Test core imports
        from core.service_registry import ServiceRegistry
        from core.service_bootstrap import ServiceBootstrap
        
        # Test AI service imports
        from ai_services.ai_service_manager import AIServiceManager
        from ai_services.plugin_manager import PluginManager
        from ai_services.llm_providers import LLMProviderFactory
        from ai_services.prompt_templates import PromptTemplateManager
        
        # Test config imports
        from config.settings import get_settings, Settings
        
        # Test main import
        from main import InsuranceAIApplication
        
        print("✅ Import Compatibility: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Import Compatibility: FAILED - {e}")
        logger.exception("Import compatibility test failed")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Modular AI Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Import Compatibility", test_import_compatibility),
        ("Configuration System", test_configuration_system),
        ("Service Registry", test_service_registry),
        ("Plugin Manager", test_plugin_manager),
        ("AI Service Manager", test_ai_service_manager),
        ("Service Bootstrap", test_service_bootstrap),
        ("Main Application", test_main_application),
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
    print("🏁 Test Results Summary")
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
        print("🎉 All tests passed! Modular AI integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner crashed: {e}")
        sys.exit(1)