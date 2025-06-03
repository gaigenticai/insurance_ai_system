"""
Prompt templates for insurance domain-specific AI tasks.
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    """A prompt template with variables and formatting."""
    name: str
    template: str
    variables: List[str]
    description: str
    category: str

class PromptTemplateManager:
    """Manages prompt templates for different insurance AI tasks."""
    
    def __init__(self):
        self.templates = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize all prompt templates."""
        
        # Underwriting Templates
        self.templates.update({
            'risk_assessment': PromptTemplate(
                name='risk_assessment',
                template="""
You are an expert insurance underwriter. Analyze the following application data and provide a comprehensive risk assessment.

Application Data:
{application_data}

Institution Guidelines:
{guidelines}

Please provide:
1. Overall risk score (1-100, where 100 is highest risk)
2. Key risk factors identified
3. Recommended decision (Approve/Deny/Refer for manual review)
4. Specific conditions or premium adjustments if applicable
5. Detailed reasoning for your assessment

Format your response as JSON with the following structure:
{{
    "risk_score": <number>,
    "risk_factors": ["factor1", "factor2", ...],
    "decision": "Approve|Deny|Refer",
    "conditions": ["condition1", "condition2", ...],
    "premium_adjustment": <percentage>,
    "reasoning": "detailed explanation"
}}
""",
                variables=['application_data', 'guidelines'],
                description='Comprehensive risk assessment for underwriting',
                category='underwriting'
            ),
            
            'document_analysis': PromptTemplate(
                name='document_analysis',
                template="""
You are an expert document analyst for insurance applications. Analyze the following document text and extract relevant information.

Document Text:
{document_text}

Document Type: {document_type}

Please extract and structure the following information:
1. Personal information (name, address, date of birth, etc.)
2. Financial information (income, assets, debts, etc.)
3. Insurance-relevant details
4. Any red flags or inconsistencies
5. Missing information that should be requested

Format your response as JSON:
{{
    "extracted_data": {{
        "personal_info": {{}},
        "financial_info": {{}},
        "insurance_details": {{}},
        "other_relevant_data": {{}}
    }},
    "red_flags": ["flag1", "flag2", ...],
    "missing_information": ["item1", "item2", ...],
    "confidence_score": <0-1>,
    "notes": "additional observations"
}}
""",
                variables=['document_text', 'document_type'],
                description='Extract and analyze information from insurance documents',
                category='underwriting'
            ),
            
            'adaptive_questioning': PromptTemplate(
                name='adaptive_questioning',
                template="""
You are an intelligent insurance application assistant. Based on the current application data, generate relevant follow-up questions to complete the risk assessment.

Current Application Data:
{current_data}

Missing Required Fields:
{missing_fields}

Institution Requirements:
{requirements}

Generate 3-5 intelligent follow-up questions that will help complete the application and improve risk assessment accuracy. Consider:
1. Critical missing information
2. Potential risk factors that need clarification
3. Regulatory requirements
4. Questions that could reveal additional risks or benefits

Format your response as JSON:
{{
    "questions": [
        {{
            "question": "question text",
            "field_name": "corresponding_field",
            "priority": "high|medium|low",
            "reasoning": "why this question is important"
        }}
    ],
    "completion_percentage": <0-100>,
    "next_steps": "recommended next actions"
}}
""",
                variables=['current_data', 'missing_fields', 'requirements'],
                description='Generate adaptive questions for incomplete applications',
                category='underwriting'
            )
        })
        
        # Claims Templates
        self.templates.update({
            'fraud_detection': PromptTemplate(
                name='fraud_detection',
                template="""
You are an expert insurance fraud investigator. Analyze the following claim for potential fraud indicators.

Claim Data:
{claim_data}

Historical Claims for Policy:
{claim_history}

Fraud Detection Rules:
{fraud_rules}

Analyze the claim for:
1. Suspicious patterns or inconsistencies
2. Timeline anomalies
3. Amount discrepancies
4. Description analysis for fraud indicators
5. Historical pattern analysis

Provide a fraud risk assessment with specific indicators found.

Format your response as JSON:
{{
    "fraud_risk_score": <0-100>,
    "fraud_indicators": [
        {{
            "indicator": "description",
            "severity": "low|medium|high",
            "evidence": "specific evidence found"
        }}
    ],
    "recommendation": "approve|investigate|deny",
    "investigation_priority": "low|medium|high|urgent",
    "suggested_actions": ["action1", "action2", ...],
    "reasoning": "detailed analysis"
}}
""",
                variables=['claim_data', 'claim_history', 'fraud_rules'],
                description='Analyze claims for fraud indicators',
                category='claims'
            ),
            
            'claim_triage': PromptTemplate(
                name='claim_triage',
                template="""
You are an expert claims processor. Analyze the following claim and determine the appropriate triage category and processing path.

Claim Information:
{claim_data}

Policy Information:
{policy_data}

Triage Rules:
{triage_rules}

Categorize this claim based on:
1. Complexity level
2. Required expertise
3. Processing priority
4. Estimated processing time
5. Special handling requirements

Format your response as JSON:
{{
    "triage_category": "simple|standard|complex|specialist",
    "priority": "low|medium|high|urgent",
    "estimated_processing_time": "time estimate",
    "required_expertise": ["expertise1", "expertise2", ...],
    "special_handling": ["requirement1", "requirement2", ...],
    "auto_approval_eligible": true/false,
    "reasoning": "detailed explanation"
}}
""",
                variables=['claim_data', 'policy_data', 'triage_rules'],
                description='Triage claims for appropriate processing',
                category='claims'
            ),
            
            'claim_settlement': PromptTemplate(
                name='claim_settlement',
                template="""
You are an expert claims adjuster. Analyze the following claim and provide a settlement recommendation.

Claim Details:
{claim_data}

Policy Coverage:
{policy_coverage}

Investigation Results:
{investigation_results}

Settlement Guidelines:
{settlement_guidelines}

Provide a comprehensive settlement analysis including:
1. Coverage determination
2. Settlement amount calculation
3. Deductible application
4. Any exclusions or limitations
5. Payment recommendations

Format your response as JSON:
{{
    "coverage_determination": "covered|not_covered|partially_covered",
    "settlement_amount": <amount>,
    "deductible_applied": <amount>,
    "exclusions_applied": ["exclusion1", "exclusion2", ...],
    "payment_method": "direct|vendor|reimbursement",
    "conditions": ["condition1", "condition2", ...],
    "reasoning": "detailed explanation"
}}
""",
                variables=['claim_data', 'policy_coverage', 'investigation_results', 'settlement_guidelines'],
                description='Determine claim settlement amounts and conditions',
                category='claims'
            )
        })
        
        # Actuarial Templates
        self.templates.update({
            'risk_modeling': PromptTemplate(
                name='risk_modeling',
                template="""
You are an expert actuary. Analyze the following data and provide insights for risk modeling and pricing.

Historical Data:
{historical_data}

Market Conditions:
{market_conditions}

Regulatory Environment:
{regulatory_info}

Provide analysis on:
1. Risk trends and patterns
2. Pricing recommendations
3. Reserve adequacy
4. Emerging risks
5. Competitive positioning

Format your response as JSON:
{{
    "risk_trends": [
        {{
            "trend": "description",
            "impact": "positive|negative|neutral",
            "confidence": <0-1>,
            "timeframe": "short|medium|long term"
        }}
    ],
    "pricing_recommendations": {{
        "overall_adjustment": <percentage>,
        "segment_adjustments": {{}},
        "reasoning": "explanation"
    }},
    "reserve_adequacy": {{
        "current_level": "adequate|inadequate|excessive",
        "recommended_adjustment": <percentage>,
        "reasoning": "explanation"
    }},
    "emerging_risks": ["risk1", "risk2", ...],
    "market_position": "competitive analysis"
}}
""",
                variables=['historical_data', 'market_conditions', 'regulatory_info'],
                description='Analyze data for actuarial risk modeling',
                category='actuarial'
            ),
            
            'trend_analysis': PromptTemplate(
                name='trend_analysis',
                template="""
You are an expert data analyst specializing in insurance trends. Analyze the following data and identify significant trends and patterns.

Data Set:
{data_set}

Time Period: {time_period}

Analysis Focus: {analysis_focus}

Provide comprehensive trend analysis including:
1. Statistical trends and patterns
2. Seasonal variations
3. Anomaly detection
4. Predictive insights
5. Business implications

Format your response as JSON:
{{
    "trends_identified": [
        {{
            "trend_name": "name",
            "description": "detailed description",
            "statistical_significance": <0-1>,
            "direction": "increasing|decreasing|stable|cyclical",
            "magnitude": "low|medium|high",
            "timeframe": "period"
        }}
    ],
    "seasonal_patterns": {{}},
    "anomalies": [
        {{
            "date": "date",
            "description": "anomaly description",
            "potential_causes": ["cause1", "cause2", ...]
        }}
    ],
    "predictions": {{
        "short_term": "3-6 months",
        "medium_term": "6-12 months",
        "long_term": "1+ years"
    }},
    "business_implications": ["implication1", "implication2", ...],
    "recommendations": ["recommendation1", "recommendation2", ...]
}}
""",
                variables=['data_set', 'time_period', 'analysis_focus'],
                description='Analyze trends in actuarial data',
                category='actuarial'
            ),
            
            'report_generation': PromptTemplate(
                name='report_generation',
                template="""
You are an expert insurance analyst. Generate a comprehensive report based on the following analysis results.

Analysis Results:
{analysis_results}

Report Type: {report_type}

Target Audience: {target_audience}

Key Metrics:
{key_metrics}

Generate a professional report that includes:
1. Executive summary
2. Key findings
3. Detailed analysis
4. Recommendations
5. Supporting data and charts description

Format your response as a structured report in markdown format with clear sections and professional language appropriate for {target_audience}.

Include specific recommendations for:
- Risk management
- Pricing strategies
- Operational improvements
- Regulatory compliance
- Market opportunities
""",
                variables=['analysis_results', 'report_type', 'target_audience', 'key_metrics'],
                description='Generate comprehensive insurance reports',
                category='actuarial'
            )
        })
    
    def get_template(self, name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
        return self.templates[name]
    
    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """Get all templates for a specific category."""
        return [template for template in self.templates.values() if template.category == category]
    
    def get_prompt(self, template_name: str, **kwargs) -> str:
        """Get a formatted prompt template with provided variables."""
        return self.format_prompt(template_name, **kwargs)
    
    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with provided variables."""
        template = self.get_template(template_name)
        
        # Check if all required variables are provided
        missing_vars = [var for var in template.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables for template '{template_name}': {missing_vars}")
        
        # Format the template
        return template.template.format(**kwargs)
    
    def list_templates(self) -> Dict[str, List[str]]:
        """List all available templates by category."""
        categories = {}
        for template in self.templates.values():
            if template.category not in categories:
                categories[template.category] = []
            categories[template.category].append(template.name)
        return categories

# JSON Schema definitions for structured responses
RESPONSE_SCHEMAS = {
    'risk_assessment': {
        "type": "object",
        "properties": {
            "risk_score": {"type": "number", "minimum": 1, "maximum": 100},
            "risk_factors": {"type": "array", "items": {"type": "string"}},
            "decision": {"type": "string", "enum": ["Approve", "Deny", "Refer"]},
            "conditions": {"type": "array", "items": {"type": "string"}},
            "premium_adjustment": {"type": "number"},
            "reasoning": {"type": "string"}
        },
        "required": ["risk_score", "risk_factors", "decision", "reasoning"]
    },
    
    'fraud_detection': {
        "type": "object",
        "properties": {
            "fraud_risk_score": {"type": "number", "minimum": 0, "maximum": 100},
            "fraud_indicators": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "indicator": {"type": "string"},
                        "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                        "evidence": {"type": "string"}
                    }
                }
            },
            "recommendation": {"type": "string", "enum": ["approve", "investigate", "deny"]},
            "investigation_priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
            "suggested_actions": {"type": "array", "items": {"type": "string"}},
            "reasoning": {"type": "string"}
        },
        "required": ["fraud_risk_score", "fraud_indicators", "recommendation", "reasoning"]
    },
    
    'trend_analysis': {
        "type": "object",
        "properties": {
            "trends_identified": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "trend_name": {"type": "string"},
                        "description": {"type": "string"},
                        "statistical_significance": {"type": "number", "minimum": 0, "maximum": 1},
                        "direction": {"type": "string", "enum": ["increasing", "decreasing", "stable", "cyclical"]},
                        "magnitude": {"type": "string", "enum": ["low", "medium", "high"]},
                        "timeframe": {"type": "string"}
                    }
                }
            },
            "business_implications": {"type": "array", "items": {"type": "string"}},
            "recommendations": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["trends_identified", "business_implications", "recommendations"]
    }
}