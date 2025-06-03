#!/usr/bin/env python3
"""
Railway-compatible launcher for Insurance AI Dashboard

This script launches the dashboard in a way that's compatible with Railway deployment.
It starts the API backend and provides access to the Streamlit UI.
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# Set environment variables for Railway
os.environ.setdefault("PORT", "8080")
os.environ.setdefault("HOST", "0.0.0.0")

# Get project root
PROJECT_ROOT = Path(__file__).parent

def start_api():
    """Start the API server"""
    port = os.environ.get("PORT", "8080")
    host = os.environ.get("HOST", "0.0.0.0")
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "api_enhanced:app",
        "--host", host,
        "--port", port,
        "--workers", "1"
    ]
    
    print(f"🚀 Starting API on {host}:{port}")
    
    # Change to project directory
    os.chdir(PROJECT_ROOT)
    
    # Start the API
    subprocess.run(cmd)

def main():
    """Main launcher"""
    print("🏢 Insurance AI System - Railway Launcher")
    print("=" * 50)
    
    # Set Python path
    os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))
    
    # For Railway, we primarily run the API
    # The dashboard UI can be accessed via the API docs or separate deployment
    
    print("🔧 Starting API server...")
    start_api()

if __name__ == "__main__":
    main()