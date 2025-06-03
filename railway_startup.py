#!/usr/bin/env python3
"""
Railway.com Startup Script for Insurance AI System

This script handles the initialization and startup of the Insurance AI System
on Railway.com platform with proper environment configuration and health checks.
"""

import os
import sys
import time
import logging
import asyncio
from typing import Optional
import uvicorn
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayConfig:
    """Railway.com specific configuration management"""
    
    def __init__(self):
        self.port = int(os.getenv('PORT', 8080))
        self.host = '0.0.0.0'  # Railway requires binding to all interfaces
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.workers = int(os.getenv('WORKERS', 1))  # Railway handles scaling
        self.enable_auto_migrate = os.getenv('ENABLE_AUTO_MIGRATE', 'true').lower() == 'true'
        
    def get_database_url(self) -> Optional[str]:
        """Get database URL from Railway environment"""
        # Railway provides DATABASE_URL automatically
        return os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL from Railway environment"""
        # Railway provides REDIS_URL automatically
        return os.getenv('REDIS_URL')
    
    def setup_environment(self):
        """Setup environment variables for Railway deployment"""
        # Parse DATABASE_URL if provided by Railway
        db_url = self.get_database_url()
        if db_url:
            # Railway format: postgresql://user:pass@host:port/db
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(db_url)
            
            os.environ.setdefault('POSTGRES_HOST', parsed.hostname or 'localhost')
            os.environ.setdefault('POSTGRES_PORT', str(parsed.port or 5432))
            os.environ.setdefault('POSTGRES_DB', parsed.path.lstrip('/') if parsed.path else 'insurance_ai')
            os.environ.setdefault('POSTGRES_USER', parsed.username or 'postgres')
            os.environ.setdefault('POSTGRES_PASSWORD', parsed.password or '')
            os.environ.setdefault('DB_SCHEMA', 'insurance_ai')
        
        # Parse REDIS_URL if provided by Railway
        redis_url = self.get_redis_url()
        if redis_url:
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(redis_url)
            
            os.environ.setdefault('REDIS_HOST', parsed.hostname or 'localhost')
            os.environ.setdefault('REDIS_PORT', str(parsed.port or 6379))
            os.environ.setdefault('REDIS_PASSWORD', parsed.password or '')
            os.environ.setdefault('REDIS_DB', '0')
            os.environ.setdefault('CELERY_BROKER_URL', redis_url)
            os.environ.setdefault('CELERY_RESULT_BACKEND', redis_url)
        
        # Set default values for missing environment variables
        defaults = {
            'API_PORT': str(self.port),
            'ALLOWED_ORIGINS': '*',
            'AI_PROVIDER': 'openai',
            'AI_MODEL': 'gpt-3.5-turbo',
            'AI_TEMPERATURE': '0.7',
            'AI_MAX_TOKENS': '2000',
            'INSTITUTION_ID': 'default',
            'SECRET_KEY': os.urandom(32).hex(),
            'JWT_SECRET_KEY': os.urandom(32).hex(),
        }
        
        for key, value in defaults.items():
            os.environ.setdefault(key, value)

async def run_migrations():
    """Run database migrations if enabled"""
    config = RailwayConfig()
    
    if not config.enable_auto_migrate:
        logger.info("Auto-migration disabled, skipping...")
        return
    
    try:
        logger.info("Running database migrations...")
        
        # Import and run migrations
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Initialize database connection
        from db_connection import initialize_db_pool, close_db_pool
        await initialize_db_pool()
        
        # Run migrations
        import db_migrations
        await asyncio.to_thread(db_migrations.main)
        
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        # Don't fail startup if migrations fail - the app might still work
        # with existing schema

def setup_environment():
    """Setup environment without async operations"""
    logger.info("🚀 Setting up environment for Railway.com")
    
    config = RailwayConfig()
    config.setup_environment()
    
    logger.info(f"✅ Environment configured for port {config.port}")
    return config

def create_app():
    """Create and configure the FastAPI application"""
    # Import the main API application
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        logger.info("Attempting to import main API application...")
        from api import app
        
        # Add health check if not present
        @app.get("/health")
        async def health_check_override():
            return {"status": "healthy", "message": "Insurance AI System API is running"}
        
        logger.info("✅ Main API application loaded successfully")
        return app
        
    except ImportError as e:
        logger.error(f"Import error when creating app: {e}")
        logger.info("Creating fallback application...")
        return create_fallback_app(f"Import error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error when creating app: {e}")
        logger.info("Creating fallback application...")
        return create_fallback_app(f"Startup error: {str(e)}")

def create_fallback_app(error_message: str):
    """Create a minimal health check app if main app fails"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    fallback_app = FastAPI(title="Insurance AI System - Fallback Mode")
    
    # Add CORS middleware
    fallback_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @fallback_app.get("/")
    async def root():
        return {"message": "Insurance AI System - Fallback Mode", "status": "degraded"}
    
    @fallback_app.get("/health")
    async def health():
        return {"status": "degraded", "message": f"Main application failed: {error_message}"}
    
    @fallback_app.get("/debug")
    async def debug():
        return {
            "error": error_message,
            "environment": {
                "PORT": os.getenv("PORT", "Not set"),
                "DATABASE_URL": "Set" if os.getenv("DATABASE_URL") else "Not set",
                "REDIS_URL": "Set" if os.getenv("REDIS_URL") else "Not set",
            },
            "python_path": sys.path[:3]
        }
    
    return fallback_app

def main():
    """Main entry point for Railway deployment"""
    # Setup environment first
    config = setup_environment()
    
    logger.info(f"🚀 Starting Insurance AI System")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Port: {config.port}")
    logger.info(f"Workers: {config.workers}")
    
    # Create the application
    app = create_app()
    
    # Configure uvicorn for Railway
    uvicorn_config = {
        "app": app,
        "host": config.host,
        "port": config.port,
        "log_level": os.getenv('LOG_LEVEL', 'info').lower(),
        "access_log": True,
    }
    
    # Railway handles process management, so we use single worker
    if config.environment == 'production':
        uvicorn_config.update({
            "workers": 1,  # Railway handles scaling
            "proxy_headers": True,
            "forwarded_allow_ips": "*",
        })
    
    # Start the server
    uvicorn.run(**uvicorn_config)

if __name__ == "__main__":
    main()