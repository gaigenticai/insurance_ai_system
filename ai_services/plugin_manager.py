"""
Plugin Manager for AI Services

This module provides a plugin architecture for dynamically loading
and managing AI service providers and extensions.
"""

import logging
import importlib
import inspect
from typing import Dict, Any, Type, List, Optional, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import json

from core.service_registry import ServiceInterface

logger = logging.getLogger(__name__)

class AIPlugin(Protocol):
    """Protocol for AI plugins"""
    
    @property
    def name(self) -> str:
        """Plugin name"""
        ...
    
    @property
    def version(self) -> str:
        """Plugin version"""
        ...
    
    @property
    def description(self) -> str:
        """Plugin description"""
        ...
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin"""
        ...
    
    async def shutdown(self) -> None:
        """Shutdown the plugin"""
        ...

@dataclass
class PluginMetadata:
    """Plugin metadata"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    entry_point: str
    config_schema: Optional[Dict[str, Any]] = None

class PluginRegistry:
    """Registry for managing plugins"""
    
    def __init__(self):
        self._plugins: Dict[str, AIPlugin] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}
    
    def register_plugin(self, plugin: AIPlugin, metadata: PluginMetadata, config: Optional[Dict[str, Any]] = None):
        """Register a plugin"""
        self._plugins[metadata.name] = plugin
        self._metadata[metadata.name] = metadata
        if config:
            self._plugin_configs[metadata.name] = config
        
        logger.info(f"Registered plugin: {metadata.name} v{metadata.version}")
    
    def get_plugin(self, name: str) -> Optional[AIPlugin]:
        """Get a plugin by name"""
        return self._plugins.get(name)
    
    def get_metadata(self, name: str) -> Optional[PluginMetadata]:
        """Get plugin metadata"""
        return self._metadata.get(name)
    
    def list_plugins(self) -> List[str]:
        """List all registered plugins"""
        return list(self._plugins.keys())
    
    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all plugins"""
        return {
            name: {
                "metadata": {
                    "version": meta.version,
                    "description": meta.description,
                    "author": meta.author,
                    "dependencies": meta.dependencies
                },
                "loaded": name in self._plugins,
                "config": self._plugin_configs.get(name, {})
            }
            for name, meta in self._metadata.items()
        }

class PluginManager(ServiceInterface):
    """
    Plugin manager for AI services
    
    Provides dynamic loading and management of AI plugins including:
    - Provider plugins
    - Analysis plugins
    - Utility plugins
    """
    
    def __init__(self):
        self.registry = PluginRegistry()
        self._plugin_directories: List[Path] = []
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize plugin manager"""
        if self._initialized:
            return
        
        try:
            # Add default plugin directories
            self._add_default_plugin_directories()
            
            # Load plugins from directories
            await self._load_plugins_from_directories()
            
            # Initialize loaded plugins
            await self._initialize_plugins()
            
            self._initialized = True
            logger.info("Plugin manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize plugin manager: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check plugin manager health"""
        return self._initialized
    
    async def shutdown(self) -> None:
        """Shutdown plugin manager"""
        logger.info("Shutting down plugin manager")
        
        # Shutdown all plugins
        for plugin_name, plugin in self.registry._plugins.items():
            try:
                await plugin.shutdown()
                logger.debug(f"Shutdown plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Error shutting down plugin {plugin_name}: {e}")
        
        self.registry._plugins.clear()
        self.registry._metadata.clear()
        self.registry._plugin_configs.clear()
        self._initialized = False
    
    def _add_default_plugin_directories(self):
        """Add default plugin directories"""
        # Current directory plugins
        current_dir = Path(__file__).parent
        self._plugin_directories.extend([
            current_dir / "plugins",
            current_dir / "providers",
            current_dir / "extensions"
        ])
        
        # System-wide plugins
        self._plugin_directories.extend([
            Path("/opt/insurance_ai/plugins"),
            Path.home() / ".insurance_ai" / "plugins"
        ])
    
    def add_plugin_directory(self, directory: Path):
        """Add a plugin directory"""
        if directory.exists() and directory.is_dir():
            self._plugin_directories.append(directory)
            logger.info(f"Added plugin directory: {directory}")
        else:
            logger.warning(f"Plugin directory does not exist: {directory}")
    
    async def _load_plugins_from_directories(self):
        """Load plugins from all configured directories"""
        for directory in self._plugin_directories:
            if directory.exists():
                await self._load_plugins_from_directory(directory)
    
    async def _load_plugins_from_directory(self, directory: Path):
        """Load plugins from a specific directory"""
        try:
            for plugin_path in directory.iterdir():
                if plugin_path.is_dir() and not plugin_path.name.startswith('.'):
                    await self._load_plugin_from_path(plugin_path)
                elif plugin_path.suffix == '.py' and not plugin_path.name.startswith('_'):
                    await self._load_plugin_from_file(plugin_path)
        except Exception as e:
            logger.error(f"Error loading plugins from {directory}: {e}")
    
    async def _load_plugin_from_path(self, plugin_path: Path):
        """Load a plugin from a directory path"""
        try:
            # Look for plugin.json metadata file
            metadata_file = plugin_path / "plugin.json"
            if not metadata_file.exists():
                logger.debug(f"No plugin.json found in {plugin_path}")
                return
            
            # Load metadata
            with open(metadata_file, 'r') as f:
                metadata_dict = json.load(f)
            
            metadata = PluginMetadata(**metadata_dict)
            
            # Load the plugin module
            module_path = plugin_path / f"{metadata.entry_point}.py"
            if not module_path.exists():
                logger.error(f"Entry point {metadata.entry_point}.py not found in {plugin_path}")
                return
            
            # Import the module
            spec = importlib.util.spec_from_file_location(metadata.name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the plugin class
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                logger.error(f"No plugin class found in {module_path}")
                return
            
            # Create plugin instance
            plugin = plugin_class()
            
            # Register the plugin
            self.registry.register_plugin(plugin, metadata)
            
            logger.info(f"Loaded plugin: {metadata.name} from {plugin_path}")
            
        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_path}: {e}")
    
    async def _load_plugin_from_file(self, plugin_file: Path):
        """Load a plugin from a single Python file"""
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the plugin class
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                logger.debug(f"No plugin class found in {plugin_file}")
                return
            
            # Create plugin instance
            plugin = plugin_class()
            
            # Create basic metadata
            metadata = PluginMetadata(
                name=plugin.name,
                version=plugin.version,
                description=plugin.description,
                author="Unknown",
                dependencies=[],
                entry_point=plugin_file.stem
            )
            
            # Register the plugin
            self.registry.register_plugin(plugin, metadata)
            
            logger.info(f"Loaded plugin: {metadata.name} from {plugin_file}")
            
        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_file}: {e}")
    
    def _find_plugin_class(self, module) -> Optional[Type]:
        """Find a plugin class in a module"""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                hasattr(obj, 'name') and 
                hasattr(obj, 'version') and 
                hasattr(obj, 'description')):
                return obj
        return None
    
    async def _initialize_plugins(self):
        """Initialize all loaded plugins"""
        for plugin_name, plugin in self.registry._plugins.items():
            try:
                config = self.registry._plugin_configs.get(plugin_name, {})
                await plugin.initialize(config)
                logger.debug(f"Initialized plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
    
    async def load_plugin_from_config(self, config: Dict[str, Any]):
        """Load a plugin from configuration"""
        try:
            plugin_type = config.get('type')
            plugin_config = config.get('config', {})
            
            if plugin_type == 'file':
                plugin_file = Path(config['path'])
                await self._load_plugin_from_file(plugin_file)
            elif plugin_type == 'directory':
                plugin_dir = Path(config['path'])
                await self._load_plugin_from_path(plugin_dir)
            elif plugin_type == 'module':
                await self._load_plugin_from_module(config['module'], plugin_config)
            else:
                logger.error(f"Unknown plugin type: {plugin_type}")
                
        except Exception as e:
            logger.error(f"Failed to load plugin from config: {e}")
    
    async def _load_plugin_from_module(self, module_name: str, config: Dict[str, Any]):
        """Load a plugin from a module name"""
        try:
            module = importlib.import_module(module_name)
            plugin_class = self._find_plugin_class(module)
            
            if not plugin_class:
                logger.error(f"No plugin class found in module {module_name}")
                return
            
            plugin = plugin_class()
            
            metadata = PluginMetadata(
                name=plugin.name,
                version=plugin.version,
                description=plugin.description,
                author="Unknown",
                dependencies=[],
                entry_point=module_name
            )
            
            self.registry.register_plugin(plugin, metadata, config)
            await plugin.initialize(config)
            
            logger.info(f"Loaded plugin: {metadata.name} from module {module_name}")
            
        except Exception as e:
            logger.error(f"Failed to load plugin from module {module_name}: {e}")
    
    def get_plugin(self, name: str) -> Optional[AIPlugin]:
        """Get a plugin by name"""
        return self.registry.get_plugin(name)
    
    def list_plugins(self) -> List[str]:
        """List all loaded plugins"""
        return self.registry.list_plugins()
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get information about all plugins"""
        return {
            "total_plugins": len(self.registry._plugins),
            "plugin_directories": [str(d) for d in self._plugin_directories],
            "plugins": self.registry.get_plugin_info()
        }

# Global plugin manager instance
_plugin_manager = PluginManager()

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager"""
    return _plugin_manager