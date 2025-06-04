#!/usr/bin/env python3
"""
AI Configuration Script for Insurance AI System

This script helps users configure AI providers (OpenAI, Local LLM, etc.)
and test the AI integration with the insurance system.
"""

import os
import sys
import json
import asyncio
import time
from typing import Dict, Any, Optional
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def print_banner():
    """Print configuration banner."""
    print("=" * 60)
    print("🤖 Insurance AI System - AI Configuration")
    print("=" * 60)
    print()

def configure_openai():
    """Configure OpenAI provider."""
    print("🔧 Configuring OpenAI Provider")
    print("-" * 30)
    
    api_key = input("Enter your OpenAI API Key: ").strip()
    if not api_key:
        print("❌ API key is required for OpenAI")
        return False
    
    model = input("Enter model name (default: gpt-3.5-turbo): ").strip() or "gpt-3.5-turbo"
    base_url = input("Enter base URL (optional, press Enter for default): ").strip()
    
    # Set environment variables
    os.environ['AI_PROVIDER'] = 'openai'
    os.environ['OPENAI_API_KEY'] = api_key
    os.environ['AI_MODEL'] = model
    if base_url:
        os.environ['OPENAI_BASE_URL'] = base_url
    
    print("✅ OpenAI configuration saved!")
    return True

def configure_local_llm():
    """Configure Local LLM provider."""
    print("🏠 Configuring Local LLM Provider")
    print("-" * 35)
    
    provider_type = input("Enter provider type (ollama/vllm/lmstudio): ").strip().lower()
    if provider_type not in ['ollama', 'vllm', 'lmstudio']:
        print("❌ Invalid provider type. Must be: ollama, vllm, or lmstudio")
        return False
    
    base_url = input(f"Enter base URL (default: http://localhost:11434): ").strip() or "http://localhost:11434"
    model = input("Enter model name (default: llama2:7b): ").strip() or "llama2:7b"
    api_key = input("Enter API key (optional): ").strip()
    
    # Set environment variables
    os.environ['AI_PROVIDER'] = 'local'
    os.environ['LOCAL_LLM_PROVIDER_TYPE'] = provider_type
    os.environ['LOCAL_LLM_BASE_URL'] = base_url
    os.environ['LOCAL_LLM_MODEL'] = model
    if api_key:
        os.environ['LOCAL_LLM_API_KEY'] = api_key
    
    print("✅ Local LLM configuration saved!")
    return True

def configure_anthropic():
    """Configure Anthropic provider."""
    print("🧠 Configuring Anthropic Provider")
    print("-" * 32)
    
    api_key = input("Enter your Anthropic API Key: ").strip()
    if not api_key:
        print("❌ API key is required for Anthropic")
        return False
    
    model = input("Enter model name (default: claude-3-sonnet-20240229): ").strip() or "claude-3-sonnet-20240229"
    
    # Set environment variables
    os.environ['AI_PROVIDER'] = 'anthropic'
    os.environ['ANTHROPIC_API_KEY'] = api_key
    os.environ['AI_MODEL'] = model
    
    print("✅ Anthropic configuration saved!")
    return True

def configure_mock():
    """Configure Mock provider for testing."""
    print("🎭 Configuring Mock Provider (for testing)")
    print("-" * 42)
    
    # Set environment variables
    os.environ['AI_PROVIDER'] = 'mock'
    os.environ['AI_MODEL'] = 'mock-insurance-ai-v1'
    
    print("✅ Mock provider configured!")
    print("💡 This provider generates realistic demo responses for testing")
    return True

def save_config_file():
    """Save configuration to file."""
    config = {
        'ai_provider': os.environ.get('AI_PROVIDER', 'mock'),
        'ai_model': os.environ.get('AI_MODEL', 'mock-insurance-ai-v1'),
        'ai_enabled': True,
        'ai_temperature': 0.7,
        'ai_max_tokens': 2000,
        'ai_timeout': 30,
        'ai_max_retries': 3,
        'ai_enable_fallback': True,
        'ai_enable_caching': True,
        'timestamp': str(time.time())
    }
    
    # Add provider-specific config
    if config['ai_provider'] == 'openai':
        config['openai_api_key'] = os.environ.get('OPENAI_API_KEY', '')
        config['openai_base_url'] = os.environ.get('OPENAI_BASE_URL', '')
    elif config['ai_provider'] == 'local':
        config['local_llm_provider_type'] = os.environ.get('LOCAL_LLM_PROVIDER_TYPE', 'ollama')
        config['local_llm_base_url'] = os.environ.get('LOCAL_LLM_BASE_URL', 'http://localhost:11434')
        config['local_llm_model'] = os.environ.get('LOCAL_LLM_MODEL', 'llama2:7b')
        config['local_llm_api_key'] = os.environ.get('LOCAL_LLM_API_KEY', '')
    elif config['ai_provider'] == 'anthropic':
        config['anthropic_api_key'] = os.environ.get('ANTHROPIC_API_KEY', '')
    
    config_file = os.path.join(project_root, 'ai_config.json')
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"💾 Configuration saved to: {config_file}")

async def test_ai_connection():
    """Test AI connection."""
    print("\n🧪 Testing AI Connection...")
    print("-" * 25)
    
    try:
        from ai_services.ai_service_manager import AIServiceManager
        
        ai_manager = AIServiceManager()
        await ai_manager.initialize()
        
        # Test health check
        health = await ai_manager.health_check()
        if health:
            print("✅ AI connection successful!")
            
            # Test a simple analysis
            print("🔍 Testing underwriting analysis...")
            test_data = {
                "applicant_name": "Test User",
                "age": 30,
                "income": 50000,
                "credit_score": 700,
                "property_value": 200000,
                "loan_amount": 160000
            }
            
            response = await ai_manager.analyze_underwriting(test_data)
            if response and not response.error:
                print("✅ Underwriting analysis test successful!")
                print(f"📝 Sample response: {response.content[:100]}...")
            else:
                print(f"⚠️  Underwriting test failed: {response.error if response else 'No response'}")
        else:
            print("❌ AI connection failed!")
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

def create_env_file():
    """Create .env file with current configuration."""
    env_vars = [
        'AI_PROVIDER',
        'AI_MODEL',
        'OPENAI_API_KEY',
        'OPENAI_BASE_URL',
        'ANTHROPIC_API_KEY',
        'LOCAL_LLM_PROVIDER_TYPE',
        'LOCAL_LLM_BASE_URL',
        'LOCAL_LLM_MODEL',
        'LOCAL_LLM_API_KEY'
    ]
    
    env_file = os.path.join(project_root, '.env')
    with open(env_file, 'w') as f:
        f.write("# AI Configuration for Insurance AI System\n")
        f.write("# Generated by configure_ai.py\n\n")
        
        for var in env_vars:
            value = os.environ.get(var, '')
            if value:
                f.write(f"{var}={value}\n")
        
        # Add other common settings
        f.write("\n# General AI Settings\n")
        f.write("AI_ENABLED=true\n")
        f.write("AI_TEMPERATURE=0.7\n")
        f.write("AI_MAX_TOKENS=2000\n")
        f.write("AI_TIMEOUT=30\n")
        f.write("AI_MAX_RETRIES=3\n")
        f.write("AI_ENABLE_FALLBACK=true\n")
        f.write("AI_ENABLE_CACHING=true\n")
    
    print(f"📄 Environment file created: {env_file}")

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🚀 CONFIGURATION COMPLETE!")
    print("=" * 60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. 🎯 Test the Dashboard:")
    print("   python launch_dashboard.py")
    print("   # Then visit: http://localhost:8501")
    print()
    print("2. 🔧 Test the API:")
    print("   python -m uvicorn api:app --host 0.0.0.0 --port 8080")
    print("   # Then visit: http://localhost:8080/docs")
    print()
    print("3. 🤖 Use AI Services:")
    print("   - Navigate to 'AI Services' in the dashboard")
    print("   - Try underwriting, claims, or actuarial analysis")
    print("   - Configure additional providers as needed")
    print()
    print("4. 📊 Monitor Performance:")
    print("   - Check AI Analytics tab for usage metrics")
    print("   - Review AI confidence scores")
    print("   - Adjust settings as needed")
    print()
    print("💡 TIP: You can reconfigure AI providers anytime by running this script again")
    print()

def main():
    """Main configuration function."""
    parser = argparse.ArgumentParser(description='Configure AI providers for Insurance AI System')
    parser.add_argument('--provider', choices=['openai', 'local', 'anthropic', 'mock'], 
                       help='AI provider to configure')
    parser.add_argument('--test', action='store_true', help='Test AI connection after configuration')
    parser.add_argument('--create-env', action='store_true', help='Create .env file with configuration')
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.provider:
        # Configure specific provider
        if args.provider == 'openai':
            success = configure_openai()
        elif args.provider == 'local':
            success = configure_local_llm()
        elif args.provider == 'anthropic':
            success = configure_anthropic()
        elif args.provider == 'mock':
            success = configure_mock()
        
        if not success:
            sys.exit(1)
    else:
        # Interactive configuration
        print("Select AI Provider to configure:")
        print("1. 🤖 OpenAI (GPT models)")
        print("2. 🏠 Local LLM (Ollama, vLLM, LM Studio)")
        print("3. 🧠 Anthropic (Claude models)")
        print("4. 🎭 Mock Provider (for testing)")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            success = configure_openai()
        elif choice == '2':
            success = configure_local_llm()
        elif choice == '3':
            success = configure_anthropic()
        elif choice == '4':
            success = configure_mock()
        else:
            print("❌ Invalid choice")
            sys.exit(1)
        
        if not success:
            sys.exit(1)
    
    # Save configuration
    save_config_file()
    
    if args.create_env:
        create_env_file()
    
    # Test connection if requested
    if args.test:
        asyncio.run(test_ai_connection())
    
    print_next_steps()

if __name__ == "__main__":
    main()