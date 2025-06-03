#!/usr/bin/env python3
"""
Insurance AI System Dashboard Launcher

Starts both the enhanced API backend and the Streamlit dashboard UI.
Provides a complete control tower interface for insurance operations.
"""

import subprocess
import sys
import os
import time
import threading
import signal
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent

def start_api_server():
    """Start the enhanced API server"""
    print("🚀 Starting Enhanced API Server...")
    
    # Change to project directory
    os.chdir(PROJECT_ROOT)
    
    # Start the API server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "api_enhanced:app",
        "--host", "0.0.0.0",
        "--port", "8080",
        "--reload"
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Monitor output
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[API] {line.strip()}")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("🎯 Starting Dashboard UI...")
    
    # Change to project directory
    os.chdir(PROJECT_ROOT)
    
    # Start the dashboard
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "ui/dashboard_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Monitor output
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[UI] {line.strip()}")
        
        return process
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return None

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "streamlit",
        "fastapi", 
        "uvicorn",
        "plotly",
        "pandas"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def main():
    """Main launcher function"""
    print("🏢 Insurance AI System - Dashboard Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing packages manually.")
        sys.exit(1)
    
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT))
    
    # Start API server in a separate thread
    print("\n🔧 Starting services...")
    
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Wait a moment for API to start
    print("⏳ Waiting for API server to initialize...")
    time.sleep(5)
    
    # Start dashboard
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Wait a moment for dashboard to start
    print("⏳ Waiting for dashboard to initialize...")
    time.sleep(3)
    
    print("\n" + "=" * 50)
    print("🎉 Insurance AI System Dashboard is starting!")
    print("=" * 50)
    print()
    print("📊 Dashboard UI:")
    print("   Local:    http://localhost:8501")
    print("   Network:  http://0.0.0.0:8501")
    print()
    print("🔌 Enhanced API:")
    print("   Local:    http://localhost:8080")
    print("   Network:  http://0.0.0.0:8080")
    print("   Docs:     http://localhost:8080/docs")
    print()
    print("🎯 Features Available:")
    print("   • 🏠 Dashboard Control Tower")
    print("   • 📋 Policy & Underwriting Management")
    print("   • ⚖️ Claims Processing Center")
    print("   • 📊 Actuarial & Risk Analytics")
    print("   • 🕵️ Fraud & Ethics Monitoring")
    print("   • 📚 Knowledge Base & Model Feedback")
    print("   • ⚙️ System Configuration")
    print("   • 📩 Notifications & Logging")
    print("   • 👤 User Management & Access Control")
    print("   • 📞 Human Escalation & AI Co-Pilot")
    print()
    print("💡 Tips:")
    print("   • Use the sidebar to navigate between sections")
    print("   • All data is connected to the backend API")
    print("   • AI features require API keys (OpenAI/Anthropic)")
    print("   • Press Ctrl+C to stop all services")
    print()
    print("=" * 50)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        print("👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()