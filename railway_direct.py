#!/usr/bin/env python3
"""
Direct Railway.com startup script that bypasses complex initialization
This script starts the API directly without migrations or complex setup
"""

import os
import sys
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_basic_environment():
    """Setup basic environment variables"""
    port = int(os.getenv('PORT', 8080))
    
    # Set basic defaults
    defaults = {
        'API_PORT': str(port),
        'ALLOWED_ORIGINS': '*',
        'AI_PROVIDER': 'openai',
        'AI_MODEL': 'gpt-3.5-turbo',
        'AI_TEMPERATURE': '0.7',
        'AI_MAX_TOKENS': '2000',
        'INSTITUTION_ID': 'default',
        'SECRET_KEY': os.urandom(32).hex(),
        'JWT_SECRET_KEY': os.urandom(32).hex(),
        'ENABLE_AUTO_MIGRATE': 'false',  # Disable auto-migration
    }
    
    for key, value in defaults.items():
        os.environ.setdefault(key, value)
    
    return port

def main():
    """Main entry point for direct Railway deployment"""
    port = setup_basic_environment()
    
    logger.info(f"🚀 Starting Insurance AI System directly on port {port}")
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Import the API directly
        from api import app
        logger.info("✅ API imported successfully")
        
        # Start uvicorn directly
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            proxy_headers=True,
            forwarded_allow_ips="*",
        )
        
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        logger.info("Starting minimal fallback server...")
        
        # Create minimal fallback
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(title="Insurance AI System - Emergency Mode")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        async def root():
            return {"message": "Insurance AI System - Emergency Mode", "status": "limited"}
        
        @app.get("/health")
        async def health():
            return {"status": "limited", "message": f"Emergency mode: {str(e)}"}
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
        )

if __name__ == "__main__":
    main()