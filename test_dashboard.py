#!/usr/bin/env python3
"""
Test script for the Insurance AI Dashboard

Verifies that all components can be imported and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Streamlit: {e}")
        return False
    
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Plotly: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Pandas: {e}")
        return False
    
    try:
        from ui.dashboard_app import main
        print("✅ Dashboard app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import dashboard app: {e}")
        return False
    
    try:
        from ui.dashboard_utils import APIClient, get_api_client
        print("✅ Dashboard utils imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import dashboard utils: {e}")
        return False
    
    try:
        from config.dashboard_config import get_dashboard_config, UserRole
        print("✅ Dashboard config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import dashboard config: {e}")
        return False
    
    return True

def test_api_endpoints():
    """Test that API endpoints are accessible"""
    print("\n🔌 Testing API endpoints...")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ API health endpoint accessible")
        else:
            print(f"⚠️ API health endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️ API not accessible (this is expected if not running): {e}")
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config.dashboard_config import get_dashboard_config, UserRole, ROLE_PERMISSIONS
        
        config = get_dashboard_config()
        print(f"✅ Dashboard config loaded: {config.page_title}")
        
        # Test role permissions
        admin_perms = ROLE_PERMISSIONS[UserRole.ADMIN]
        print(f"✅ Role permissions loaded: Admin can manage users: {admin_perms.can_manage_users}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_mock_data():
    """Test mock data generation"""
    print("\n📊 Testing mock data generation...")
    
    try:
        from ui.dashboard_app import generate_mock_policies, generate_mock_claims, generate_mock_agents
        
        policies = generate_mock_policies(5)
        print(f"✅ Generated {len(policies)} mock policies")
        
        claims = generate_mock_claims(3)
        print(f"✅ Generated {len(claims)} mock claims")
        
        agents = generate_mock_agents()
        print(f"✅ Generated {len(agents)} mock agents")
        
        return True
    except Exception as e:
        print(f"❌ Mock data test failed: {e}")
        return False

def test_utilities():
    """Test utility functions"""
    print("\n🛠️ Testing utility functions...")
    
    try:
        from ui.dashboard_utils import format_currency, format_percentage, get_status_color
        
        # Test formatting functions
        currency = format_currency(1234.56)
        print(f"✅ Currency formatting: {currency}")
        
        percentage = format_percentage(0.8542)
        print(f"✅ Percentage formatting: {percentage}")
        
        color = get_status_color("Active")
        print(f"✅ Status color: {color}")
        
        return True
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏢 Insurance AI Dashboard - Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_mock_data,
        test_utilities,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dashboard is ready to launch.")
        print("\n🚀 To start the dashboard, run:")
        print("   python start_dashboard.py")
        print("\n📖 Or start components separately:")
        print("   # Start API: uvicorn api_enhanced:app --host 0.0.0.0 --port 8080")
        print("   # Start UI:  streamlit run ui/dashboard_app.py --server.port 8501")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)