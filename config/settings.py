"""
Modular Configuration System for Insurance AI System

This module provides a comprehensive, environment-based configuration system
with no hardcoded values, supporting multiple deployment environments.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path
import secrets

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = field(default_factory=lambda: os.getenv('POSTGRES_HOST', 'localhost'))
    port: int = field(default_factory=lambda: int(os.getenv('POSTGRES_PORT', '5432')))
    database: str = field(default_factory=lambda: os.getenv('POSTGRES_DB', 'insurance_ai'))
    username: str = field(default_factory=lambda: os.getenv('POSTGRES_USER', 'postgres'))
    password: str = field(default_factory=lambda: os.getenv('POSTGRES_PASSWORD', ''))
    schema: str = field(default_factory=lambda: os.getenv('DB_SCHEMA', 'insurance_ai'))
    pool_size: int = field(default_factory=lambda: int(os.getenv('DB_POOL_SIZE', '10')))
    max_overflow: int = field(default_factory=lambda: int(os.getenv('DB_MAX_OVERFLOW', '20')))
    pool_timeout: int = field(default_factory=lambda: int(os.getenv('DB_POOL_TIMEOUT', '30')))
    
    @property
    def url(self) -> str:
        """Get database URL"""
        # Check for Railway-style DATABASE_URL first
        if url := os.getenv('DATABASE_URL'):
            return url
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = field(default_factory=lambda: os.getenv('REDIS_HOST', 'localhost'))
    port: int = field(default_factory=lambda: int(os.getenv('REDIS_PORT', '6379')))
    password: str = field(default_factory=lambda: os.getenv('REDIS_PASSWORD', ''))
    database: int = field(default_factory=lambda: int(os.getenv('REDIS_DB', '0')))
    max_connections: int = field(default_factory=lambda: int(os.getenv('REDIS_MAX_CONNECTIONS', '50')))
    
    @property
    def url(self) -> str:
        """Get Redis URL"""
        # Check for Railway-style REDIS_URL first
        if url := os.getenv('REDIS_URL'):
            return url
        
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.database}"

@dataclass
class AIConfig:
    """AI service configuration"""
    enabled: bool = field(default_factory=lambda: os.getenv('AI_ENABLED', 'true').lower() == 'true')
    provider: str = field(default_factory=lambda: os.getenv('AI_PROVIDER', 'openai'))
    model: str = field(default_factory=lambda: os.getenv('AI_MODEL', 'gpt-3.5-turbo'))
    temperature: float = field(default_factory=lambda: float(os.getenv('AI_TEMPERATURE', '0.7')))
    max_tokens: int = field(default_factory=lambda: int(os.getenv('AI_MAX_TOKENS', '2000')))
    timeout: int = field(default_factory=lambda: int(os.getenv('AI_TIMEOUT', '30')))
    max_retries: int = field(default_factory=lambda: int(os.getenv('AI_MAX_RETRIES', '3')))
    
    # Provider-specific configurations
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv('OPENAI_API_KEY'))
    openai_base_url: Optional[str] = field(default_factory=lambda: os.getenv('OPENAI_BASE_URL'))
    
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.getenv('ANTHROPIC_API_KEY'))
    
    local_llm_base_url: str = field(default_factory=lambda: os.getenv('LOCAL_LLM_BASE_URL', 'http://localhost:11434'))
    local_llm_model: str = field(default_factory=lambda: os.getenv('LOCAL_LLM_MODEL', 'llama2-7b'))
    
    # Feature flags
    enable_caching: bool = field(default_factory=lambda: os.getenv('AI_ENABLE_CACHING', 'true').lower() == 'true')
    enable_fallback: bool = field(default_factory=lambda: os.getenv('AI_ENABLE_FALLBACK', 'true').lower() == 'true')
    enable_metrics: bool = field(default_factory=lambda: os.getenv('AI_ENABLE_METRICS', 'true').lower() == 'true')

@dataclass
class AppConfig:
    """Application configuration"""
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'development'))
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'false').lower() == 'true')
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    demo_mode: bool = field(default_factory=lambda: os.getenv('DEMO_MODE', 'false').lower() == 'true')
    
    # Feature flags
    enable_plugins: bool = field(default_factory=lambda: os.getenv('ENABLE_PLUGINS', 'true').lower() == 'true')
    enable_monitoring: bool = field(default_factory=lambda: os.getenv('ENABLE_MONITORING', 'true').lower() == 'true')
    
    # Timeouts
    startup_timeout: int = field(default_factory=lambda: int(os.getenv('STARTUP_TIMEOUT', '30')))
    shutdown_timeout: int = field(default_factory=lambda: int(os.getenv('SHUTDOWN_TIMEOUT', '10')))

@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = field(default_factory=lambda: os.getenv('CACHE_ENABLED', 'true').lower() == 'true')
    backend: str = field(default_factory=lambda: os.getenv('CACHE_BACKEND', 'memory'))
    ttl: int = field(default_factory=lambda: int(os.getenv('CACHE_TTL', '3600')))
    max_size: int = field(default_factory=lambda: int(os.getenv('CACHE_MAX_SIZE', '1000')))
    
    # Redis-specific (if backend is redis)
    redis_enabled: bool = field(default_factory=lambda: os.getenv('CACHE_BACKEND', 'memory') == 'redis')

@dataclass
class APIConfig:
    """API server configuration"""
    host: str = field(default_factory=lambda: os.getenv('API_HOST', '0.0.0.0'))
    port: int = field(default_factory=lambda: int(os.getenv('PORT', os.getenv('API_PORT', '8080'))))
    workers: int = field(default_factory=lambda: int(os.getenv('WORKERS', '1')))
    reload: bool = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'production') != 'production')
    
    # CORS configuration
    allowed_origins: List[str] = field(default_factory=lambda: 
        os.getenv('ALLOWED_ORIGINS', '*').split(',') if os.getenv('ALLOWED_ORIGINS') != '*' 
        else ['*'])
    allowed_methods: List[str] = field(default_factory=lambda: 
        os.getenv('ALLOWED_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(','))
    allowed_headers: List[str] = field(default_factory=lambda: 
        os.getenv('ALLOWED_HEADERS', '*').split(',') if os.getenv('ALLOWED_HEADERS') != '*' 
        else ['*'])
    
    # Security
    secret_key: str = field(default_factory=lambda: 
        os.getenv('SECRET_KEY') or secrets.token_urlsafe(32))
    jwt_secret_key: str = field(default_factory=lambda: 
        os.getenv('JWT_SECRET_KEY') or secrets.token_urlsafe(32))
    jwt_algorithm: str = field(default_factory=lambda: os.getenv('JWT_ALGORITHM', 'HS256'))
    jwt_expiration: int = field(default_factory=lambda: int(os.getenv('JWT_EXPIRATION', '3600')))

@dataclass
class CeleryConfig:
    """Celery configuration"""
    broker_url: str = field(default_factory=lambda: 
        os.getenv('CELERY_BROKER_URL') or RedisConfig().url)
    result_backend: str = field(default_factory=lambda: 
        os.getenv('CELERY_RESULT_BACKEND') or RedisConfig().url)
    task_serializer: str = field(default_factory=lambda: os.getenv('CELERY_TASK_SERIALIZER', 'json'))
    result_serializer: str = field(default_factory=lambda: os.getenv('CELERY_RESULT_SERIALIZER', 'json'))
    accept_content: List[str] = field(default_factory=lambda: 
        os.getenv('CELERY_ACCEPT_CONTENT', 'json').split(','))
    timezone: str = field(default_factory=lambda: os.getenv('CELERY_TIMEZONE', 'UTC'))
    enable_utc: bool = field(default_factory=lambda: 
        os.getenv('CELERY_ENABLE_UTC', 'true').lower() == 'true')

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    format: str = field(default_factory=lambda: 
        os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file: Optional[str] = field(default_factory=lambda: os.getenv('LOG_FILE'))
    max_bytes: int = field(default_factory=lambda: int(os.getenv('LOG_MAX_BYTES', '10485760')))  # 10MB
    backup_count: int = field(default_factory=lambda: int(os.getenv('LOG_BACKUP_COUNT', '5')))

@dataclass
class InstitutionConfig:
    """Institution-specific configuration"""
    id: str = field(default_factory=lambda: os.getenv('INSTITUTION_ID', 'default'))
    name: str = field(default_factory=lambda: os.getenv('INSTITUTION_NAME', 'Default Institution'))
    config_path: str = field(default_factory=lambda: 
        os.getenv('INSTITUTION_CONFIG_PATH', 'config/institutions'))
    
    def get_config_file(self) -> Path:
        """Get institution-specific config file path"""
        return Path(self.config_path) / f"{self.id}.json"

@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling functionality"""
    enable_ai_features: bool = field(default_factory=lambda: 
        os.getenv('ENABLE_AI_FEATURES', 'true').lower() == 'true')
    enable_caching: bool = field(default_factory=lambda: 
        os.getenv('ENABLE_CACHING', 'true').lower() == 'true')
    enable_metrics: bool = field(default_factory=lambda: 
        os.getenv('ENABLE_METRICS', 'true').lower() == 'true')
    enable_auto_migrate: bool = field(default_factory=lambda: 
        os.getenv('ENABLE_AUTO_MIGRATE', 'true').lower() == 'true')
    enable_background_tasks: bool = field(default_factory=lambda: 
        os.getenv('ENABLE_BACKGROUND_TASKS', 'true').lower() == 'true')

class Settings:
    """Main settings class that aggregates all configuration"""
    
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.debug = self.environment != 'production'
        
        # Initialize all configuration sections
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.ai = AIConfig()
        self.app = AppConfig()
        self.cache = CacheConfig()
        self.api = APIConfig()
        self.celery = CeleryConfig()
        self.logging = LoggingConfig()
        self.institution = InstitutionConfig()
        self.features = FeatureFlags()
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate configuration settings"""
        errors = []
        
        # Validate AI configuration
        if self.ai.enabled:
            if self.ai.provider == 'openai' and not self.ai.openai_api_key:
                errors.append("OPENAI_API_KEY is required when AI_PROVIDER=openai")
            elif self.ai.provider == 'anthropic' and not self.ai.anthropic_api_key:
                errors.append("ANTHROPIC_API_KEY is required when AI_PROVIDER=anthropic")
        
        # Validate database configuration
        if not self.database.host:
            errors.append("POSTGRES_HOST is required")
        
        if errors:
            logger.warning(f"Configuration validation warnings: {errors}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)"""
        return {
            'environment': self.environment,
            'debug': self.debug,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'schema': self.database.schema,
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'database': self.redis.database,
            },
            'ai': {
                'provider': self.ai.provider,
                'model': self.ai.model,
                'temperature': self.ai.temperature,
                'max_tokens': self.ai.max_tokens,
                'enable_caching': self.ai.enable_caching,
                'enable_fallback': self.ai.enable_fallback,
            },
            'api': {
                'host': self.api.host,
                'port': self.api.port,
                'workers': self.api.workers,
            },
            'features': {
                'enable_ai_features': self.features.enable_ai_features,
                'enable_caching': self.features.enable_caching,
                'enable_metrics': self.features.enable_metrics,
            }
        }
    
    @classmethod
    def load_from_file(cls, config_file: Union[str, Path]) -> 'Settings':
        """Load settings from JSON file (overrides environment variables)"""
        config_path = Path(config_file)
        if not config_path.exists():
            logger.warning(f"Config file {config_path} not found, using environment variables")
            return cls()
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Set environment variables from config file
            for key, value in config_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        env_key = f"{key.upper()}_{sub_key.upper()}"
                        os.environ.setdefault(env_key, str(sub_value))
                else:
                    os.environ.setdefault(key.upper(), str(value))
            
            return cls()
        
        except Exception as e:
            logger.error(f"Failed to load config file {config_path}: {e}")
            return cls()

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings

def reload_settings():
    """Reload settings from environment variables"""
    global settings
    settings = Settings()
    return settings