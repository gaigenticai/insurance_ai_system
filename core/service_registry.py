"""
Modular Service Registry for Insurance AI System

This module provides a dependency injection and service registry system
for building scalable, modular, and testable applications.
"""

import logging
import asyncio
from typing import Dict, Any, Type, TypeVar, Optional, Callable, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import inspect

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ServiceLifecycle(Enum):
    """Service lifecycle states"""
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

class ServiceStatus(Enum):
    """Service status"""
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class ServiceDefinition:
    """Service definition metadata"""
    service_type: Type
    implementation: Type
    lifecycle: ServiceLifecycle
    dependencies: List[Type]
    factory: Optional[Callable]
    status: ServiceStatus = ServiceStatus.REGISTERED
    instance: Optional[Any] = None
    error: Optional[Exception] = None

class ServiceInterface(ABC):
    """Base interface for all services"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if service is healthy"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the service"""
        pass

class ServiceRegistry:
    """
    Dependency injection container and service registry
    
    Provides:
    - Service registration and resolution
    - Dependency injection
    - Lifecycle management
    - Health monitoring
    - Graceful shutdown
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceDefinition] = {}
        self._instances: Dict[Type, Any] = {}
        self._initialization_lock = asyncio.Lock()
        self._shutdown_handlers: List[Callable] = []
    
    def register_singleton(
        self, 
        service_type: Type[T], 
        implementation: Type[T], 
        factory: Optional[Callable[[], T]] = None
    ) -> 'ServiceRegistry':
        """Register a singleton service"""
        return self._register_service(
            service_type, implementation, ServiceLifecycle.SINGLETON, factory
        )
    
    def register_transient(
        self, 
        service_type: Type[T], 
        implementation: Type[T], 
        factory: Optional[Callable[[], T]] = None
    ) -> 'ServiceRegistry':
        """Register a transient service (new instance each time)"""
        return self._register_service(
            service_type, implementation, ServiceLifecycle.TRANSIENT, factory
        )
    
    def register_scoped(
        self, 
        service_type: Type[T], 
        implementation: Type[T], 
        factory: Optional[Callable[[], T]] = None
    ) -> 'ServiceRegistry':
        """Register a scoped service (one instance per scope)"""
        return self._register_service(
            service_type, implementation, ServiceLifecycle.SCOPED, factory
        )
    
    def register_instance(self, service_type: Type[T], instance: T) -> 'ServiceRegistry':
        """Register a pre-created instance"""
        self._services[service_type] = ServiceDefinition(
            service_type=service_type,
            implementation=type(instance),
            lifecycle=ServiceLifecycle.SINGLETON,
            dependencies=[],
            factory=None,
            status=ServiceStatus.READY,
            instance=instance
        )
        self._instances[service_type] = instance
        return self
    
    def _register_service(
        self, 
        service_type: Type[T], 
        implementation: Type[T], 
        lifecycle: ServiceLifecycle,
        factory: Optional[Callable[[], T]] = None
    ) -> 'ServiceRegistry':
        """Internal service registration"""
        # Analyze dependencies
        dependencies = self._analyze_dependencies(implementation)
        
        self._services[service_type] = ServiceDefinition(
            service_type=service_type,
            implementation=implementation,
            lifecycle=lifecycle,
            dependencies=dependencies,
            factory=factory
        )
        
        logger.debug(f"Registered {lifecycle.value} service: {service_type.__name__}")
        return self
    
    def _analyze_dependencies(self, implementation: Type) -> List[Type]:
        """Analyze constructor dependencies"""
        try:
            signature = inspect.signature(implementation.__init__)
            dependencies = []
            
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    dependencies.append(param.annotation)
            
            return dependencies
        except Exception as e:
            logger.warning(f"Failed to analyze dependencies for {implementation}: {e}")
            return []
    
    async def get(self, service_type: Type[T]) -> T:
        """Get service instance"""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} not registered")
        
        service_def = self._services[service_type]
        
        # Handle singleton lifecycle
        if service_def.lifecycle == ServiceLifecycle.SINGLETON:
            if service_def.instance is not None:
                return service_def.instance
            
            async with self._initialization_lock:
                # Double-check after acquiring lock
                if service_def.instance is not None:
                    return service_def.instance
                
                instance = await self._create_instance(service_def)
                service_def.instance = instance
                self._instances[service_type] = instance
                return instance
        
        # Handle transient lifecycle
        elif service_def.lifecycle == ServiceLifecycle.TRANSIENT:
            return await self._create_instance(service_def)
        
        # Handle scoped lifecycle (simplified - same as singleton for now)
        else:
            return await self.get(service_type)
    
    async def _create_instance(self, service_def: ServiceDefinition) -> Any:
        """Create service instance with dependency injection"""
        try:
            service_def.status = ServiceStatus.INITIALIZING
            
            # Use factory if provided
            if service_def.factory:
                instance = service_def.factory()
            else:
                # Resolve dependencies
                dependencies = []
                for dep_type in service_def.dependencies:
                    dep_instance = await self.get(dep_type)
                    dependencies.append(dep_instance)
                
                # Create instance
                instance = service_def.implementation(*dependencies)
            
            # Initialize if it's a ServiceInterface
            if isinstance(instance, ServiceInterface):
                await instance.initialize()
            
            service_def.status = ServiceStatus.READY
            logger.debug(f"Created instance of {service_def.service_type.__name__}")
            
            return instance
        
        except Exception as e:
            service_def.status = ServiceStatus.ERROR
            service_def.error = e
            logger.error(f"Failed to create instance of {service_def.service_type.__name__}: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all services"""
        health_status = {
            "overall": "healthy",
            "services": {}
        }
        
        for service_type, service_def in self._services.items():
            service_name = service_type.__name__
            
            try:
                if service_def.status == ServiceStatus.READY and service_def.instance:
                    if isinstance(service_def.instance, ServiceInterface):
                        is_healthy = await service_def.instance.health_check()
                        health_status["services"][service_name] = {
                            "status": "healthy" if is_healthy else "unhealthy",
                            "lifecycle": service_def.lifecycle.value
                        }
                    else:
                        health_status["services"][service_name] = {
                            "status": "healthy",
                            "lifecycle": service_def.lifecycle.value
                        }
                else:
                    health_status["services"][service_name] = {
                        "status": service_def.status.value,
                        "lifecycle": service_def.lifecycle.value,
                        "error": str(service_def.error) if service_def.error else None
                    }
                    
                    if service_def.status == ServiceStatus.ERROR:
                        health_status["overall"] = "degraded"
            
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["overall"] = "degraded"
        
        return health_status
    
    async def shutdown(self):
        """Shutdown all services gracefully"""
        logger.info("Shutting down services...")
        
        # Run shutdown handlers
        for handler in self._shutdown_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error(f"Error in shutdown handler: {e}")
        
        # Shutdown services in reverse order of creation
        for service_type, instance in reversed(list(self._instances.items())):
            try:
                if isinstance(instance, ServiceInterface):
                    await instance.shutdown()
                
                service_def = self._services[service_type]
                service_def.status = ServiceStatus.STOPPED
                service_def.instance = None
                
                logger.debug(f"Shutdown service: {service_type.__name__}")
            
            except Exception as e:
                logger.error(f"Error shutting down {service_type.__name__}: {e}")
        
        self._instances.clear()
        logger.info("All services shutdown complete")
    
    def add_shutdown_handler(self, handler: Callable):
        """Add a shutdown handler"""
        self._shutdown_handlers.append(handler)
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about registered services"""
        return {
            service_type.__name__: {
                "implementation": service_def.implementation.__name__,
                "lifecycle": service_def.lifecycle.value,
                "status": service_def.status.value,
                "dependencies": [dep.__name__ for dep in service_def.dependencies],
                "has_instance": service_def.instance is not None
            }
            for service_type, service_def in self._services.items()
        }

# Global service registry instance
_registry = ServiceRegistry()

def get_registry() -> ServiceRegistry:
    """Get the global service registry"""
    return _registry

def register_singleton(service_type: Type[T], implementation: Type[T], factory: Optional[Callable[[], T]] = None):
    """Register a singleton service"""
    return _registry.register_singleton(service_type, implementation, factory)

def register_transient(service_type: Type[T], implementation: Type[T], factory: Optional[Callable[[], T]] = None):
    """Register a transient service"""
    return _registry.register_transient(service_type, implementation, factory)

def register_instance(service_type: Type[T], instance: T):
    """Register a service instance"""
    return _registry.register_instance(service_type, instance)

async def get_service(service_type: Type[T]) -> T:
    """Get a service instance"""
    return await _registry.get(service_type)