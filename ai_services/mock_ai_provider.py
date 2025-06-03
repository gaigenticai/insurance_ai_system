"""
Mock AI Provider for demonstration and testing purposes.

This provider simulates AI responses for insurance domain tasks
when real AI providers are not available.
"""

import json
import random
import logging
from typing import Dict, Any, List
from datetime import datetime
import asyncio

from .llm_providers import BaseLLMProvider, AIResponse

logger = logging.getLogger(__name__)

class MockAIProvider(BaseLLMProvider):
    """Mock AI provider that generates realistic insurance-domain responses."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = "mock-insurance-ai-v1"
        self.response_delay = config.get('response_delay', 0.5)  # Simulate processing time
        
    async def generate_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate a mock response based on the prompt content."""
        # Simulate processing time
        await asyncio.sleep(self.response_delay)
        
        try:
            # Analyze prompt to determine response type
            response_content = self._generate_contextual_response(prompt)
            confidence = random.uniform(0.75, 0.95)
            
            return AIResponse(
                content=response_content,
                model=self.model,
                confidence=confidence,
                usage={
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response_content.split()),
                    "total_tokens": len(prompt.split()) + len(response_content.split())
                },
                metadata={
                    "provider": "mock",
                    "timestamp": datetime.utcnow().isoformat(),
                    "mock_mode": True
                }
            )
            
        except Exception as e:
            logger.error(f"Mock AI provider error: {e}")
            return AIResponse(
                content="",
                model=self.model,
                error=f"Mock provider error: {str(e)}"
            )
    
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> AIResponse:
        """Generate a structured mock response following the provided schema."""
        await asyncio.sleep(self.response_delay)
        
        try:
            # Generate structured response based on schema
            structured_data = self._generate_structured_data(prompt, schema)
            
            return AIResponse(
                content=json.dumps(structured_data, indent=2),
                model=self.model,
                confidence=random.uniform(0.80, 0.95),
                usage={
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": 150,
                    "total_tokens": len(prompt.split()) + 150
                },
                metadata={
                    "provider": "mock",
                    "structured": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Mock structured response error: {e}")
            return AIResponse(
                content="",
                model=self.model,
                error=f"Mock structured response error: {str(e)}"
            )
    
    def _generate_contextual_response(self, prompt: str) -> str:
        """Generate contextual response based on prompt content."""
        prompt_lower = prompt.lower()
        
        # Underwriting responses
        if any(word in prompt_lower for word in ['underwriting', 'risk assessment', 'application', 'applicant']):
            return self._generate_underwriting_response(prompt)
        
        # Claims responses
        elif any(word in prompt_lower for word in ['claim', 'fraud', 'incident', 'damage']):
            return self._generate_claims_response(prompt)
        
        # Actuarial responses
        elif any(word in prompt_lower for word in ['actuarial', 'trend', 'analysis', 'premium', 'pricing']):
            return self._generate_actuarial_response(prompt)
        
        # General insurance response
        else:
            return self._generate_general_response(prompt)
    
    def _generate_underwriting_response(self, prompt: str) -> str:
        """Generate underwriting-specific response."""
        risk_factors = [
            "credit score analysis",
            "income verification",
            "employment stability",
            "debt-to-income ratio",
            "property value assessment",
            "geographic risk factors"
        ]
        
        decisions = ["Approve", "Approve with conditions", "Refer for manual review", "Deny"]
        decision = random.choice(decisions)
        
        selected_factors = random.sample(risk_factors, random.randint(2, 4))
        
        response = f"""Based on the underwriting analysis, I recommend to **{decision}** this application.

**Key Risk Factors Analyzed:**
{chr(10).join(f'• {factor}' for factor in selected_factors)}

**Risk Assessment:**
- Overall risk score: {random.randint(15, 85)}/100
- Primary concerns: {random.choice(['None identified', 'Minor credit history gaps', 'High debt-to-income ratio', 'Property location risk'])}
- Strengths: {random.choice(['Strong credit profile', 'Stable employment', 'Low debt burden', 'Excellent payment history'])}

**Recommendation Details:**
{self._get_decision_details(decision)}

**Confidence Level:** {random.randint(85, 95)}%"""
        
        return response
    
    def _generate_claims_response(self, prompt: str) -> str:
        """Generate claims-specific response."""
        fraud_indicators = [
            "Timeline inconsistencies",
            "Unusual damage patterns",
            "Prior claims history",
            "Documentation quality",
            "Witness statements",
            "Police report verification"
        ]
        
        recommendations = ["Approve", "Investigate further", "Request additional documentation", "Deny"]
        recommendation = random.choice(recommendations)
        
        fraud_score = random.randint(5, 95)
        selected_indicators = random.sample(fraud_indicators, random.randint(2, 3))
        
        response = f"""**Claims Analysis Summary**

**Fraud Risk Assessment:**
- Fraud risk score: {fraud_score}/100
- Risk level: {self._get_risk_level(fraud_score)}

**Analysis Findings:**
{chr(10).join(f'• {indicator}: {"✓ Verified" if random.choice([True, False]) else "⚠ Requires attention"}' for indicator in selected_indicators)}

**Recommendation:** {recommendation}

**Supporting Evidence:**
- Incident description consistency: {random.choice(['High', 'Medium', 'Low'])}
- Documentation completeness: {random.choice(['Complete', 'Partial', 'Incomplete'])}
- Timeline verification: {random.choice(['Verified', 'Pending', 'Inconsistent'])}

**Next Steps:**
{self._get_claims_next_steps(recommendation)}

**Processing Priority:** {random.choice(['Standard', 'High', 'Urgent'])}"""
        
        return response
    
    def _generate_actuarial_response(self, prompt: str) -> str:
        """Generate actuarial-specific response."""
        trends = [
            "Claims frequency increasing",
            "Severity trends stable",
            "Geographic risk concentration",
            "Seasonal pattern variations",
            "Demographic shifts",
            "Economic impact factors"
        ]
        
        selected_trends = random.sample(trends, random.randint(2, 4))
        
        response = f"""**Actuarial Analysis Report**

**Key Trends Identified:**
{chr(10).join(f'• {trend}' for trend in selected_trends)}

**Statistical Summary:**
- Loss ratio: {random.uniform(0.55, 0.85):.2f}
- Frequency trend: {random.choice(['+2.3%', '-1.8%', '+0.5%', '-3.2%'])} YoY
- Severity trend: {random.choice(['+5.1%', '-2.4%', '+1.2%', '+7.8%'])} YoY

**Risk Indicators:**
- Market conditions: {random.choice(['Stable', 'Volatile', 'Improving', 'Deteriorating'])}
- Regulatory impact: {random.choice(['Minimal', 'Moderate', 'Significant'])}
- Competitive pressure: {random.choice(['Low', 'Medium', 'High'])}

**Pricing Recommendations:**
- Overall rate adjustment: {random.choice(['+3%', '+5%', '-2%', '+1%', '+7%'])}
- High-risk segments: {random.choice(['+8%', '+12%', '+15%'])}
- Preferred segments: {random.choice(['-1%', '+2%', 'No change'])}

**Confidence Interval:** {random.randint(88, 96)}%"""
        
        return response
    
    def _generate_general_response(self, prompt: str) -> str:
        """Generate general insurance-related response."""
        return f"""I've analyzed your request regarding insurance operations. Based on the available data and industry best practices, here are my findings:

**Analysis Summary:**
The information provided indicates standard insurance processing requirements with typical risk factors present.

**Key Observations:**
• Data quality appears sufficient for analysis
• Standard industry patterns observed
• No immediate red flags identified
• Recommendations align with regulatory guidelines

**Suggested Actions:**
1. Proceed with standard processing protocols
2. Monitor for any developing patterns
3. Ensure compliance with current regulations
4. Document findings for audit trail

**Confidence Level:** {random.randint(80, 92)}%

*Note: This analysis is generated by the mock AI provider for demonstration purposes.*"""
    
    def _get_decision_details(self, decision: str) -> str:
        """Get detailed explanation for underwriting decision."""
        details = {
            "Approve": "Application meets all standard criteria with acceptable risk profile.",
            "Approve with conditions": "Application acceptable with premium adjustment of +15% due to elevated risk factors.",
            "Refer for manual review": "Application requires human underwriter review due to complex risk factors.",
            "Deny": "Application does not meet minimum acceptance criteria."
        }
        return details.get(decision, "Standard processing recommended.")
    
    def _get_risk_level(self, score: int) -> str:
        """Convert fraud score to risk level."""
        if score < 30:
            return "Low"
        elif score < 60:
            return "Medium"
        elif score < 80:
            return "High"
        else:
            return "Very High"
    
    def _get_claims_next_steps(self, recommendation: str) -> str:
        """Get next steps for claims recommendation."""
        steps = {
            "Approve": "Process payment according to policy terms and conditions.",
            "Investigate further": "Assign to special investigation unit for detailed review.",
            "Request additional documentation": "Contact claimant for missing documentation before proceeding.",
            "Deny": "Issue denial letter with detailed explanation and appeal process."
        }
        return steps.get(recommendation, "Follow standard claims processing procedures.")
    
    def _generate_structured_data(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured data based on schema."""
        # This is a simplified implementation
        # In a real scenario, you'd parse the schema more thoroughly
        
        if "risk_score" in str(schema):
            return {
                "risk_score": random.randint(20, 85),
                "risk_factors": random.sample([
                    "Credit history", "Income stability", "Property location", 
                    "Debt ratio", "Employment history"
                ], 3),
                "decision": random.choice(["Approve", "Deny", "Refer"]),
                "conditions": ["Premium adjustment +10%"] if random.choice([True, False]) else [],
                "premium_adjustment": random.choice([0, 5, 10, 15]),
                "reasoning": "Comprehensive risk analysis completed with standard criteria applied."
            }
        
        elif "fraud" in str(schema):
            return {
                "fraud_risk_score": random.randint(10, 90),
                "fraud_indicators": [
                    {
                        "indicator": "Timeline analysis",
                        "severity": random.choice(["low", "medium", "high"]),
                        "evidence": "Incident timing appears consistent with reported facts"
                    }
                ],
                "recommendation": random.choice(["approve", "investigate", "deny"]),
                "investigation_priority": random.choice(["low", "medium", "high"]),
                "suggested_actions": ["Verify documentation", "Contact witnesses"],
                "reasoning": "Standard fraud detection protocols applied with no major red flags identified."
            }
        
        else:
            return {
                "analysis_complete": True,
                "confidence": random.uniform(0.8, 0.95),
                "recommendations": ["Follow standard procedures"],
                "timestamp": datetime.utcnow().isoformat()
            }

    async def health_check(self) -> bool:
        """Mock health check - always returns True."""
        return True