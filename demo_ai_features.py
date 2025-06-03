#!/usr/bin/env python3
"""
Demo script showing AI features in the insurance system.
This script demonstrates the key AI capabilities without requiring full infrastructure.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set demo environment variables
os.environ.setdefault("OPENAI_API_KEY", "demo-key-openai")
os.environ.setdefault("ANTHROPIC_API_KEY", "demo-key-anthropic")
os.environ.setdefault("AI_PROVIDER", "openai")
os.environ.setdefault("AI_MODEL", "gpt-3.5-turbo")

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🤖 {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section header."""
    print(f"\n📋 {title}")
    print("-" * 40)

async def demo_prompt_templates():
    """Demonstrate prompt template functionality."""
    print_header("AI Prompt Templates Demo")
    
    from ai_services.prompt_templates import PromptTemplateManager
    
    template_manager = PromptTemplateManager()
    
    # List available templates
    templates = template_manager.list_templates()
    print("Available AI Templates by Category:")
    for category, template_names in templates.items():
        print(f"  📁 {category.title()}:")
        for name in template_names:
            print(f"    • {name}")
    
    print_section("Underwriting Risk Assessment Template")
    
    # Demo underwriting template
    underwriting_data = {
        "application_data": {
            "applicant_name": "Sarah Johnson",
            "age": 28,
            "occupation": "Data Scientist",
            "annual_income": 95000,
            "credit_score": 780,
            "driving_record": "Clean - no violations",
            "insurance_history": "5 years with previous carrier"
        },
        "guidelines": """
        Standard Underwriting Guidelines:
        - Age 25-65: Standard rates
        - Income >$50k: Preferred rates
        - Credit score >750: Excellent tier
        - Clean driving record: No surcharge
        """
    }
    
    prompt = template_manager.format_prompt("risk_assessment", **underwriting_data)
    print("Generated Prompt Preview:")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    
    print_section("Claims Fraud Detection Template")
    
    # Demo claims template
    claims_data = {
        "claim_data": {
            "claim_id": "CLM-2024-001",
            "policy_id": "POL-AUTO-12345",
            "claimed_amount": 8500,
            "claim_description": "Rear-end collision at intersection, significant damage to rear bumper and trunk",
            "incident_date": "2024-01-15",
            "reported_date": "2024-01-16",
            "location": "Main St & Oak Ave, Downtown"
        },
        "claim_history": [
            {
                "claim_id": "CLM-2023-045",
                "amount": 1200,
                "date": "2023-08-10",
                "type": "Minor fender bender"
            }
        ],
        "fraud_rules": [
            "Claims over $5000 require additional verification",
            "Multiple claims within 12 months trigger investigation",
            "Late reporting (>48 hours) increases fraud risk",
            "High-value claims in accident-prone areas need review"
        ]
    }
    
    fraud_prompt = template_manager.format_prompt("fraud_detection", **claims_data)
    print("Generated Fraud Detection Prompt Preview:")
    print(fraud_prompt[:500] + "..." if len(fraud_prompt) > 500 else fraud_prompt)

async def demo_ai_providers():
    """Demonstrate AI provider functionality."""
    print_header("AI Provider System Demo")
    
    from ai_services.llm_providers import LLMProviderFactory
    
    print_section("Available AI Providers")
    
    # Demo provider creation
    providers_config = {
        "openai": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "api_key": "demo-key"
        },
        "anthropic": {
            "model": "claude-3-sonnet-20240229",
            "temperature": 0.7,
            "api_key": "demo-key"
        },
        "local": {
            "model": "llama2-7b",
            "base_url": "http://localhost:11434",
            "temperature": 0.7
        }
    }
    
    for provider_name, config in providers_config.items():
        try:
            provider = LLMProviderFactory.create_provider(provider_name, config)
            print(f"✅ {provider_name.title()} Provider: {provider.model}")
        except Exception as e:
            print(f"❌ {provider_name.title()} Provider: {str(e)}")

async def demo_mock_ai_analysis():
    """Demonstrate AI analysis with mock responses."""
    print_header("AI Analysis Demo (Mock Responses)")
    
    # Mock AI provider for demonstration
    class DemoAIProvider:
        def __init__(self, provider_name):
            self.provider_name = provider_name
            self.model = f"{provider_name}-demo-model"
        
        async def generate_response(self, prompt, **kwargs):
            from ai_services.llm_providers import AIResponse
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            # Generate realistic mock responses based on prompt content
            if "risk assessment" in prompt.lower() or "underwriting" in prompt.lower():
                mock_content = json.dumps({
                    "risk_score": 0.25,
                    "risk_factors": [
                        "Excellent credit score (780)",
                        "Stable high income ($95,000)",
                        "Clean driving record",
                        "Professional occupation"
                    ],
                    "decision": "Approve",
                    "conditions": [
                        "Standard coverage terms",
                        "Preferred rate tier"
                    ],
                    "premium_adjustment": 0.90,
                    "reasoning": "Low-risk applicant with excellent financial profile and clean driving history. Qualifies for preferred rates."
                }, indent=2)
                
            elif "fraud" in prompt.lower() or "claims" in prompt.lower():
                mock_content = json.dumps({
                    "fraud_risk_score": 25,
                    "fraud_indicators": [
                        {
                            "indicator": "Late reporting",
                            "severity": "low",
                            "evidence": "Claim reported 1 day after incident"
                        },
                        {
                            "indicator": "High claim amount",
                            "severity": "medium",
                            "evidence": "Claim amount $8,500 exceeds threshold"
                        }
                    ],
                    "recommendation": "investigate",
                    "investigation_priority": "medium",
                    "suggested_actions": [
                        "Request additional documentation",
                        "Schedule vehicle inspection",
                        "Verify incident details with police report"
                    ],
                    "reasoning": "Moderate fraud risk due to high claim amount and late reporting. Recommend standard investigation procedures."
                }, indent=2)
                
            elif "actuarial" in prompt.lower() or "risk modeling" in prompt.lower():
                mock_content = json.dumps({
                    "risk_trends": [
                        {
                            "trend": "Increasing claim frequency in urban areas",
                            "impact": "negative",
                            "confidence": 0.85,
                            "timeframe": "short term"
                        },
                        {
                            "trend": "Improved vehicle safety technology adoption",
                            "impact": "positive",
                            "confidence": 0.78,
                            "timeframe": "medium term"
                        }
                    ],
                    "pricing_recommendations": {
                        "overall_adjustment": 1.05,
                        "segment_adjustments": {
                            "urban_drivers": 1.08,
                            "rural_drivers": 0.98,
                            "young_drivers": 1.12
                        },
                        "reasoning": "Increase rates by 5% overall to maintain profitability, with higher adjustments for high-risk segments"
                    },
                    "reserve_adequacy": {
                        "current_level": "adequate",
                        "recommended_adjustment": 0.02,
                        "reasoning": "Reserves are adequate but recommend 2% increase due to emerging trends"
                    },
                    "emerging_risks": [
                        "Autonomous vehicle liability",
                        "Climate change impact on claims",
                        "Cyber security for connected vehicles"
                    ],
                    "market_position": "Competitive with opportunity for selective rate increases"
                }, indent=2)
            else:
                mock_content = "Demo AI response generated successfully"
            
            return AIResponse(
                content=mock_content,
                model=self.model,
                usage={"total_tokens": 150, "prompt_tokens": 100, "completion_tokens": 50},
                metadata={"provider": self.provider_name, "demo": True}
            )
    
    # Demo different AI analyses
    demo_provider = DemoAIProvider("openai")
    
    print_section("Underwriting Risk Assessment")
    underwriting_response = await demo_provider.generate_response(
        "Perform risk assessment for underwriting application"
    )
    
    print("AI Analysis Result:")
    result = json.loads(underwriting_response.content)
    print(f"  Risk Score: {result['risk_score']} (Low Risk)")
    print(f"  Decision: {result['decision']}")
    print(f"  Premium Adjustment: {result['premium_adjustment']} (10% discount)")
    print(f"  Key Factors: {', '.join(result['risk_factors'][:2])}")
    
    print_section("Claims Fraud Detection")
    claims_response = await demo_provider.generate_response(
        "Analyze claim for fraud indicators"
    )
    
    claims_result = json.loads(claims_response.content)
    print("AI Fraud Analysis Result:")
    print(f"  Fraud Risk Score: {claims_result['fraud_risk_score']}/100 (Low-Medium)")
    print(f"  Recommendation: {claims_result['recommendation'].title()}")
    print(f"  Priority: {claims_result['investigation_priority'].title()}")
    print(f"  Key Indicators: {len(claims_result['fraud_indicators'])} found")
    
    print_section("Actuarial Risk Modeling")
    actuarial_response = await demo_provider.generate_response(
        "Perform actuarial analysis and risk modeling"
    )
    
    actuarial_result = json.loads(actuarial_response.content)
    print("AI Actuarial Analysis Result:")
    print(f"  Overall Rate Adjustment: +{(actuarial_result['pricing_recommendations']['overall_adjustment'] - 1) * 100:.0f}%")
    print(f"  Reserve Status: {actuarial_result['reserve_adequacy']['current_level'].title()}")
    print(f"  Risk Trends Identified: {len(actuarial_result['risk_trends'])}")
    print(f"  Emerging Risks: {len(actuarial_result['emerging_risks'])} identified")

async def demo_api_integration():
    """Demonstrate API integration concepts."""
    print_header("API Integration Demo")
    
    print_section("Available AI Endpoints")
    
    endpoints = [
        {
            "method": "POST",
            "path": "/ai/underwriting/analyze",
            "description": "AI-powered underwriting analysis",
            "example_request": {
                "application_data": {
                    "applicant_name": "John Doe",
                    "age": 35,
                    "occupation": "Software Engineer"
                },
                "use_ai_only": False
            }
        },
        {
            "method": "POST",
            "path": "/ai/claims/analyze",
            "description": "AI-enhanced claims processing",
            "example_request": {
                "claim_data": {
                    "claim_id": "CLM-001",
                    "claimed_amount": 2500
                },
                "use_ai_only": False
            }
        },
        {
            "method": "POST",
            "path": "/ai/actuarial/analyze",
            "description": "AI-driven actuarial analysis",
            "example_request": {
                "analysis_data": {
                    "claim_frequency": 0.15,
                    "loss_ratio": 0.65
                },
                "use_ai_only": False
            }
        },
        {
            "method": "GET",
            "path": "/ai/configuration",
            "description": "Get current AI configuration",
            "example_request": None
        },
        {
            "method": "GET",
            "path": "/ai/health",
            "description": "Check AI service health",
            "example_request": None
        }
    ]
    
    for endpoint in endpoints:
        print(f"  {endpoint['method']} {endpoint['path']}")
        print(f"    📝 {endpoint['description']}")
        if endpoint['example_request']:
            print(f"    📋 Example: {json.dumps(endpoint['example_request'], indent=6)}")
        print()

def demo_configuration():
    """Demonstrate configuration options."""
    print_header("AI Configuration Demo")
    
    print_section("Environment Variables")
    
    config_vars = [
        ("OPENAI_API_KEY", "Your OpenAI API key", "sk-..."),
        ("ANTHROPIC_API_KEY", "Your Anthropic API key", "sk-ant-..."),
        ("AI_PROVIDER", "Primary AI provider", "openai|anthropic|local"),
        ("AI_MODEL", "AI model to use", "gpt-3.5-turbo|claude-3-sonnet-20240229"),
        ("AI_TEMPERATURE", "Response creativity (0-1)", "0.7"),
        ("AI_MAX_TOKENS", "Maximum response length", "2000"),
        ("LOCAL_LLM_BASE_URL", "Local LLM server URL", "http://localhost:11434"),
    ]
    
    for var_name, description, example in config_vars:
        print(f"  {var_name}")
        print(f"    📝 {description}")
        print(f"    💡 Example: {example}")
        print()
    
    print_section("Provider Capabilities")
    
    capabilities = {
        "OpenAI": [
            "GPT-3.5 Turbo and GPT-4 models",
            "Structured JSON responses",
            "Function calling support",
            "High-quality reasoning"
        ],
        "Anthropic": [
            "Claude 3 Sonnet and Haiku models",
            "Advanced reasoning capabilities",
            "Long context windows",
            "Safety-focused responses"
        ],
        "Local LLM": [
            "Self-hosted models (Ollama, vLLM)",
            "Data privacy and control",
            "Cost-effective for high volume",
            "Customizable model selection"
        ]
    }
    
    for provider, features in capabilities.items():
        print(f"  🤖 {provider}:")
        for feature in features:
            print(f"    • {feature}")
        print()

async def main():
    """Run the AI features demo."""
    print("🚀 Insurance AI System - Features Demo")
    print("=" * 60)
    print("This demo showcases the AI capabilities integrated into the insurance system.")
    print("All examples use mock data and responses for demonstration purposes.")
    
    try:
        # Run demo sections
        await demo_prompt_templates()
        await demo_ai_providers()
        await demo_mock_ai_analysis()
        await demo_api_integration()
        demo_configuration()
        
        print_header("Demo Complete!")
        print("🎉 AI Features Successfully Demonstrated!")
        print("\n✨ Key Capabilities Shown:")
        print("  • Insurance-specific AI prompt templates")
        print("  • Multi-provider AI system (OpenAI, Anthropic, Local)")
        print("  • Realistic AI analysis for underwriting, claims, and actuarial")
        print("  • REST API integration for AI services")
        print("  • Flexible configuration options")
        
        print("\n🔧 Next Steps to Use AI Features:")
        print("  1. Set up your AI provider API keys")
        print("  2. Configure database and Redis")
        print("  3. Start the API server: python api.py")
        print("  4. Test with real data using the API endpoints")
        print("  5. Monitor AI performance and adjust settings")
        
        print("\n📚 Documentation:")
        print("  • AI_IMPLEMENTATION_SUMMARY.md - Complete implementation details")
        print("  • docs/AI_FEATURES.md - API documentation and examples")
        print("  • test_ai_simple.py - Integration tests")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)