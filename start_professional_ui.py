#!/usr/bin/env python3
"""
Startup script for the Professional Insurance AI System UI.
Launches the Streamlit application with proper configuration.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def setup_environment():
    """Setup environment variables for the application."""
    # Set default environment variables if not already set
    env_defaults = {
        'AI_PROVIDER': 'local',
        'AI_MODEL': 'gpt-3.5-turbo',
        'AI_TEMPERATURE': '0.7',
        'AI_MAX_TOKENS': '2000',
        'AI_ENABLE_FALLBACK': 'true',
        'AI_ENABLE_CACHING': 'true',
        'APP_ENVIRONMENT': 'development',
        'APP_DEBUG': 'false',
        'CACHE_ENABLED': 'false'
    }
    
    for key, value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = value
    
    print("🔧 Environment configured:")
    for key, value in env_defaults.items():
        current_value = os.environ.get(key, value)
        print(f"   {key}: {current_value}")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'streamlit',
        'pandas',
        'plotly',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        print("✅ All dependencies installed successfully!")
    else:
        print("✅ All dependencies are available")

def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(description='Start the Professional Insurance AI System UI')
    parser.add_argument('--port', type=int, default=8501, help='Port to run the application on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the application to')
    parser.add_argument('--ui', choices=['professional', 'standard'], default='professional', 
                       help='UI version to launch')
    parser.add_argument('--dev', action='store_true', help='Enable development mode')
    
    args = parser.parse_args()
    
    print("🚀 Starting Insurance AI System")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    print()
    
    # Check dependencies
    check_dependencies()
    print()
    
    # Determine UI file to launch
    if args.ui == 'professional':
        ui_file = 'ui/professional_app.py'
        print("🏢 Launching Professional UI...")
    else:
        ui_file = 'ui/streamlit_app.py'
        print("📊 Launching Standard UI...")
    
    # Check if UI file exists
    if not Path(ui_file).exists():
        print(f"❌ UI file not found: {ui_file}")
        sys.exit(1)
    
    # Prepare Streamlit command
    streamlit_args = [
        'streamlit', 'run', ui_file,
        '--server.port', str(args.port),
        '--server.address', args.host,
        '--server.allowRunOnSave', 'true' if args.dev else 'false',
        '--server.runOnSave', 'true' if args.dev else 'false',
        '--browser.gatherUsageStats', 'false',
        '--server.enableCORS', 'true',
        '--server.enableXsrfProtection', 'false'
    ]
    
    print(f"🌐 Starting server on http://{args.host}:{args.port}")
    print(f"📱 UI Mode: {args.ui.title()}")
    print(f"🔧 Development Mode: {'Enabled' if args.dev else 'Disabled'}")
    print()
    print("🎯 Access the application at:")
    print(f"   Local: http://localhost:{args.port}")
    if args.host != 'localhost':
        print(f"   Network: http://{args.host}:{args.port}")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run(streamlit_args)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()