#!/usr/bin/env python3
"""
Simplified Railway.com Startup Script for Insurance AI System
This script provides a minimal startup with health check to debug Railway deployment issues.
"""

import os
import sys
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_minimal_app():
    """Create a minimal FastAPI app for debugging"""
    app = FastAPI(
        title="Insurance AI System - Debug Mode",
        description="Minimal app for Railway deployment debugging",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "Insurance AI System is running", "status": "ok"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "message": "Health check passed"}
    
    @app.get("/debug")
    async def debug():
        return {
            "environment_variables": {
                "PORT": os.getenv("PORT", "Not set"),
                "DATABASE_URL": "Set" if os.getenv("DATABASE_URL") else "Not set",
                "REDIS_URL": "Set" if os.getenv("REDIS_URL") else "Not set",
                "OPENAI_API_KEY": "Set" if os.getenv("OPENAI_API_KEY") else "Not set",
            },
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "python_path": sys.path[:3]  # First 3 entries
        }
    
    return app

def main():
    """Main entry point for Railway deployment"""
    port = int(os.getenv('PORT', 8080))
    
    logger.info(f"🚀 Starting minimal Insurance AI System on port {port}")
    
    # Create the minimal application
    app = create_minimal_app()
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
    )

if __name__ == "__main__":
    main()