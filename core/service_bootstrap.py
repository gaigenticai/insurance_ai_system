"""
Service Bootstrap for Insurance AI System

This module provides centralized service registration and bootstrapping
for the entire application with full modularity and configurability.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .service_registry import ServiceRegistry, ServiceInterface, register_singleton, register_transient
from config.settings import get_settings
from ai_services.ai_service_manager import AIServiceManager
from ai_services.plugin_manager import PluginManager

logger = logging.getLogger(__name__)

@dataclass
class BootstrapConfig:
    """Configuration for service bootstrap"""
    enable_ai_services: bool = True
    enable_plugins: bool = True
    enable_monitoring: bool = True
    enable_caching: bool = True
    startup_timeout: int = 30

class ServiceBootstrap:
    """
    Service bootstrap manager for the insurance AI system
    
    Provides centralized service registration, initialization, and lifecycle management
    with full configurability and no hardcoded values.
    """
    
    def __init__(self, config: Optional[BootstrapConfig] = None):
        self.config = config or BootstrapConfig()
        self.settings = get_settings()
        self.registry = ServiceRegistry()
        self._initialized = False
        self._services_registered = False
    
    async def initialize(self) -> None:
        """Initialize all services"""
        if self._initialized:
            return
        
        try:
            logger.info("Starting service bootstrap initialization")
            
            # Register all services
            await self._register_services()
            
            # Initialize core services
            await self._initialize_core_services()
            
            # Initialize AI services if enabled
            if self.config.enable_ai_services:
                await self._initialize_ai_services()
            
            # Initialize plugins if enabled
            if self.config.enable_plugins:
                await self._initialize_plugins()
            
            # Initialize monitoring if enabled
            if self.config.enable_monitoring:
                await self._initialize_monitoring()
            
            self._initialized = True
            logger.info("Service bootstrap initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Service bootstrap initialization failed: {e}")
            raise
    
    async def _register_services(self):
        """Register all services with the service registry"""
        if self._services_registered:
            return
        
        logger.info("Registering services...")
        
        # Register AI services
        if self.config.enable_ai_services:
            register_singleton(AIServiceManager, AIServiceManager)
            logger.debug("Registered AI Service Manager")
        
        # Register plugin manager
        if self.config.enable_plugins:
            register_singleton(PluginManager, PluginManager)
            logger.debug("Registered Plugin Manager")
        
        # Register database services
        await self._register_database_services()
        
        # Register API services
        await self._register_api_services()
        
        # Register monitoring services
        if self.config.enable_monitoring:
            await self._register_monitoring_services()
        
        # Register caching services
        if self.config.enable_caching:
            await self._register_caching_services()
        
        self._services_registered = True
        logger.info("Service registration completed")
    
    async def _register_database_services(self):
        """Register database-related services"""
        try:
            # Import database services dynamically
            from database.connection import DatabaseManager
            from database.models import PolicyModel, ClaimModel, CustomerModel
            
            register_singleton(DatabaseManager, DatabaseManager)
            logger.debug("Registered database services")
            
        except ImportError as e:
            logger.warning(f"Database services not available: {e}")
    
    async def _register_api_services(self):
        """Register API-related services"""
        try:
            # Check if database is available before loading API services
            from db_connection import get_db_connection
            
            # Test database connection
            with get_db_connection():
                pass
            
            # If we get here, database is available - import API services
            from api.underwriting import UnderwritingAPI
            from api.claims import ClaimsAPI
            from api.actuarial import ActuarialAPI
            
            register_transient(UnderwritingAPI, UnderwritingAPI)
            register_transient(ClaimsAPI, ClaimsAPI)
            register_transient(ActuarialAPI, ActuarialAPI)
            logger.debug("Registered API services")
            
        except (ImportError, ConnectionError) as e:
            logger.warning(f"API services not available (database required): {e}")
        except Exception as e:
            logger.warning(f"Failed to register API services: {e}")
    
    async def _register_monitoring_services(self):
        """Register monitoring and metrics services"""
        try:
            # Import monitoring services dynamically
            from monitoring.metrics import MetricsCollector
            from monitoring.health import HealthChecker
            
            register_singleton(MetricsCollector, MetricsCollector)
            register_singleton(HealthChecker, HealthChecker)
            logger.debug("Registered monitoring services")
            
        except ImportError as e:
            logger.warning(f"Monitoring services not available: {e}")
    
    async def _register_caching_services(self):
        """Register caching services"""
        try:
            # Import caching services dynamically
            from caching.redis_cache import RedisCache
            from caching.memory_cache import MemoryCache
            
            if self.settings.cache.redis_enabled:
                register_singleton(RedisCache, RedisCache)
            else:
                register_singleton(MemoryCache, MemoryCache)
            
            logger.debug("Registered caching services")
            
        except ImportError as e:
            logger.warning(f"Caching services not available: {e}")
    
    async def _initialize_core_services(self):
        """Initialize core services"""
        logger.info("Initializing core services...")
        
        # Initialize database if available
        try:
            from database.connection import DatabaseManager
            db_manager = await self.registry.get(DatabaseManager)
            logger.debug("Initialized database manager")
        except Exception as e:
            logger.warning(f"Database manager not available: {e}")
    
    async def _initialize_ai_services(self):
        """Initialize AI services"""
        logger.info("Initializing AI services...")
        
        try:
            ai_manager = await self.registry.get(AIServiceManager)
            logger.info("AI services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
            if not self.settings.ai.enable_fallback:
                raise
    
    async def _initialize_plugins(self):
        """Initialize plugin system"""
        logger.info("Initializing plugin system...")
        
        try:
            plugin_manager = await self.registry.get(PluginManager)
            logger.info("Plugin system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize plugin system: {e}")
    
    async def _initialize_monitoring(self):
        """Initialize monitoring services"""
        logger.info("Initializing monitoring services...")
        
        try:
            # Initialize metrics collector if available
            from monitoring.metrics import MetricsCollector
            metrics = await self.registry.get(MetricsCollector)
            logger.debug("Metrics collector initialized")
        except Exception as e:
            logger.warning(f"Metrics collector not available: {e}")
        
        try:
            # Initialize health checker if available
            from monitoring.health import HealthChecker
            health = await self.registry.get(HealthChecker)
            logger.debug("Health checker initialized")
        except Exception as e:
            logger.warning(f"Health checker not available: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        if not self._initialized:
            return {
                "status": "not_initialized",
                "services": {}
            }
        
        # Get health status from service registry
        registry_health = await self.registry.health_check()
        
        # Add bootstrap-specific information
        health_status = {
            "status": registry_health["overall"],
            "bootstrap": {
                "initialized": self._initialized,
                "services_registered": self._services_registered,
                "config": {
                    "ai_services_enabled": self.config.enable_ai_services,
                    "plugins_enabled": self.config.enable_plugins,
                    "monitoring_enabled": self.config.enable_monitoring,
                    "caching_enabled": self.config.enable_caching
                }
            },
            "services": registry_health["services"],
            "service_count": len(registry_health["services"])
        }
        
        return health_status
    
    async def shutdown(self):
        """Shutdown all services gracefully"""
        logger.info("Starting service bootstrap shutdown")
        
        try:
            await self.registry.shutdown()
            self._initialized = False
            self._services_registered = False
            logger.info("Service bootstrap shutdown completed")
        except Exception as e:
            logger.error(f"Error during service bootstrap shutdown: {e}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about all registered services"""
        return {
            "bootstrap_status": {
                "initialized": self._initialized,
                "services_registered": self._services_registered,
                "config": {
                    "ai_services_enabled": self.config.enable_ai_services,
                    "plugins_enabled": self.config.enable_plugins,
                    "monitoring_enabled": self.config.enable_monitoring,
                    "caching_enabled": self.config.enable_caching
                }
            },
            "registry_info": self.registry.get_service_info()
        }
    
    async def get_service(self, service_type):
        """Get a service instance"""
        return await self.registry.get(service_type)

# Global bootstrap instance
_bootstrap = None

def get_bootstrap() -> ServiceBootstrap:
    """Get the global service bootstrap instance"""
    global _bootstrap
    if _bootstrap is None:
        _bootstrap = ServiceBootstrap()
    return _bootstrap

async def initialize_services(config: Optional[BootstrapConfig] = None) -> ServiceBootstrap:
    """Initialize all services with optional configuration"""
    global _bootstrap
    if _bootstrap is None:
        _bootstrap = ServiceBootstrap(config)
    
    await _bootstrap.initialize()
    return _bootstrap

async def shutdown_services():
    """Shutdown all services"""
    global _bootstrap
    if _bootstrap:
        await _bootstrap.shutdown()
        _bootstrap = None