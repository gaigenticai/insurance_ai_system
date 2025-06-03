"""
Core Infrastructure for Insurance AI System

This package provides the foundational infrastructure components
for building a scalable, modular insurance AI system.
"""

from .service_registry import (
    ServiceRegistry,
    ServiceInterface,
    ServiceLifecycle,
    get_registry,
    register_singleton,
    register_transient,
    register_instance,
    get_service
)

__all__ = [
    'ServiceRegistry',
    'ServiceInterface', 
    'ServiceLifecycle',
    'get_registry',
    'register_singleton',
    'register_transient',
    'register_instance',
    'get_service'
]