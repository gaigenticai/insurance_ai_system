"""
AI-enhanced agents for underwriting, claims, and actuarial analysis.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from agents.base.base_agent import BaseAgent
from .ai_service_manager import AIServiceManager

logger = logging.getLogger(__name__)

class AIUnderwritingAgent(BaseAgent):
    """AI-enhanced underwriting agent using LLMs for risk assessment."""
    
    def __init__(self, config_agent):
        super().__init__(agent_name="AIUnderwritingAgent", config_agent=config_agent)
        self.ai_manager = AIServiceManager(config_agent)
    
    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """
        Execute AI-enhanced underwriting analysis.
        
        Args:
            data: Application data including applicant information
            institution_id: Institution identifier
            
        Returns:
            Enhanced underwriting decision with AI insights
        """
        try:
            application_data = data.get('application_data', data)
            applicant_id = application_data.get('applicant_id', 'unknown')
            
            self.logger.info(f"Starting AI underwriting analysis for applicant {applicant_id}")
            
            # Get institution guidelines
            guidelines = self._get_underwriting_guidelines(institution_id)
            
            # Perform AI risk assessment
            ai_assessment = self._perform_ai_risk_assessment(application_data, guidelines, institution_id)
            
            # Analyze documents if available
            document_analysis = self._analyze_documents(application_data, institution_id)
            
            # Generate adaptive questions for incomplete applications
            adaptive_questions = self._generate_adaptive_questions(application_data, institution_id)
            
            # Combine AI insights with traditional rule-based assessment
            final_decision = self._combine_assessments(
                ai_assessment, document_analysis, adaptive_questions, application_data, institution_id
            )
            
            # Log audit event
            self.log_audit(
                institution_id=institution_id,
                event_type="AI_UNDERWRITING_COMPLETED",
                details={
                    "applicant_id": applicant_id,
                    "ai_risk_score": ai_assessment.get('risk_score'),
                    "ai_decision": ai_assessment.get('decision'),
                    "final_decision": final_decision.get('decision')
                }
            )
            
            return final_decision
            
        except Exception as e:
            return self.handle_error(e, {"applicant_id": applicant_id}, institution_id)
    
    def _get_underwriting_guidelines(self, institution_id: str) -> str:
        """Get underwriting guidelines for the institution."""
        try:
            config = self.config_agent.get_module_configuration('underwriting')
            guidelines = []
            
            # Format guidelines as text
            if 'risk_factors' in config:
                guidelines.append("Risk Factors:")
                for factor, rules in config['risk_factors'].items():
                    guidelines.append(f"- {factor}: {json.dumps(rules)}")
            
            if 'decision_thresholds' in config:
                guidelines.append("\nDecision Thresholds:")
                for threshold, value in config['decision_thresholds'].items():
                    guidelines.append(f"- {threshold}: {value}")
            
            return "\n".join(guidelines)
            
        except Exception as e:
            self.logger.warning(f"Could not get guidelines for {institution_id}: {str(e)}")
            return "Standard underwriting guidelines apply."
    
    async def _perform_ai_risk_assessment(self, application_data: Dict[str, Any], guidelines: str, institution_id: str) -> Dict[str, Any]:
        """Perform AI-powered risk assessment."""
        try:
            response = await self.ai_manager.generate_structured_response(
                template_name='risk_assessment',
                template_variables={
                    'application_data': json.dumps(application_data, indent=2),
                    'guidelines': guidelines
                }
            )
            
            if response.error:
                self.logger.error(f"AI risk assessment failed: {response.error}")
                return self._fallback_risk_assessment(application_data)
            
            return self.ai_manager.parse_structured_response(response)
            
        except Exception as e:
            self.logger.error(f"Error in AI risk assessment: {str(e)}")
            return self._fallback_risk_assessment(application_data)
    
    async def _analyze_documents(self, application_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Analyze documents using AI."""
        document_text = application_data.get('document_text', '')
        if not document_text:
            return {"status": "no_documents", "extracted_data": {}}
        
        try:
            response = await self.ai_manager.generate_structured_response(
                template_name='document_analysis',
                template_variables={
                    'document_text': document_text,
                    'document_type': application_data.get('document_type', 'application')
                }
            )
            
            if response.error:
                self.logger.error(f"Document analysis failed: {response.error}")
                return {"status": "analysis_failed", "extracted_data": {}}
            
            result = self.ai_manager.parse_structured_response(response)
            result["status"] = "analyzed"
            return result
            
        except Exception as e:
            self.logger.error(f"Error in document analysis: {str(e)}")
            return {"status": "analysis_error", "extracted_data": {}}
    
    async def _generate_adaptive_questions(self, application_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Generate adaptive questions for incomplete applications."""
        try:
            # Identify missing fields
            required_fields = ['full_name', 'date_of_birth', 'income', 'credit_score', 'address']
            missing_fields = [field for field in required_fields if not application_data.get(field)]
            
            if not missing_fields:
                return {"status": "complete", "questions": []}
            
            requirements = self._get_underwriting_guidelines(institution_id)
            
            response = await self.ai_manager.generate_structured_response(
                template_name='adaptive_questioning',
                template_variables={
                    'current_data': json.dumps(application_data, indent=2),
                    'missing_fields': json.dumps(missing_fields),
                    'requirements': requirements
                }
            )
            
            if response.error:
                self.logger.error(f"Adaptive questioning failed: {response.error}")
                return {"status": "generation_failed", "questions": []}
            
            result = self.ai_manager.parse_structured_response(response)
            result["status"] = "generated"
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating adaptive questions: {str(e)}")
            return {"status": "generation_error", "questions": []}
    
    def _combine_assessments(self, ai_assessment: Dict[str, Any], document_analysis: Dict[str, Any], 
                           adaptive_questions: Dict[str, Any], application_data: Dict[str, Any], 
                           institution_id: str) -> Dict[str, Any]:
        """Combine AI and traditional assessments."""
        
        # Start with AI assessment
        final_decision = {
            "ai_assessment": ai_assessment,
            "document_analysis": document_analysis,
            "adaptive_questions": adaptive_questions,
            "decision": ai_assessment.get('decision', 'Refer'),
            "risk_score": ai_assessment.get('risk_score', 50),
            "reasoning": ai_assessment.get('reasoning', 'AI assessment completed'),
            "conditions": ai_assessment.get('conditions', []),
            "premium_adjustment": ai_assessment.get('premium_adjustment', 0)
        }
        
        # Adjust based on document analysis
        if document_analysis.get('red_flags'):
            final_decision['risk_score'] = min(100, final_decision['risk_score'] + 10)
            final_decision['conditions'].extend([f"Review: {flag}" for flag in document_analysis['red_flags']])
        
        # Add missing information requirements
        if adaptive_questions.get('questions'):
            final_decision['missing_information'] = adaptive_questions['questions']
            if final_decision['decision'] == 'Approve':
                final_decision['decision'] = 'Refer'
                final_decision['reasoning'] += " - Additional information required"
        
        return final_decision
    
    def _fallback_risk_assessment(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback risk assessment when AI is unavailable."""
        # Simple rule-based assessment
        risk_score = 50
        risk_factors = []
        
        # Check credit score
        credit_score = application_data.get('credit_score')
        if credit_score:
            try:
                score = int(credit_score)
                if score < 600:
                    risk_score += 20
                    risk_factors.append("Low credit score")
                elif score > 750:
                    risk_score -= 10
                    risk_factors.append("Excellent credit score")
            except (ValueError, TypeError):
                risk_factors.append("Invalid credit score format")
        
        # Check income
        income = application_data.get('income')
        if income:
            try:
                if float(income) < 30000:
                    risk_score += 15
                    risk_factors.append("Low income")
            except (ValueError, TypeError):
                risk_factors.append("Invalid income format")
        
        # Determine decision
        if risk_score <= 30:
            decision = "Approve"
        elif risk_score >= 70:
            decision = "Deny"
        else:
            decision = "Refer"
        
        return {
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "decision": decision,
            "reasoning": "Fallback rule-based assessment (AI unavailable)",
            "conditions": [],
            "premium_adjustment": 0
        }

class AIClaimsAgent(BaseAgent):
    """AI-enhanced claims processing agent."""
    
    def __init__(self, config_agent):
        super().__init__(agent_name="AIClaimsAgent", config_agent=config_agent)
        self.ai_manager = AIServiceManager(config_agent)
    
    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """
        Execute AI-enhanced claims processing.
        
        Args:
            data: Claim data
            institution_id: Institution identifier
            
        Returns:
            Enhanced claims processing result
        """
        try:
            claim_id = data.get('claim_id', 'unknown')
            self.logger.info(f"Starting AI claims processing for claim {claim_id}")
            
            # Perform AI fraud detection
            fraud_analysis = self._perform_ai_fraud_detection(data, institution_id)
            
            # Perform AI claim triage
            triage_analysis = self._perform_ai_triage(data, institution_id)
            
            # Perform settlement analysis if appropriate
            settlement_analysis = self._perform_ai_settlement_analysis(data, institution_id)
            
            # Combine analyses
            final_result = self._combine_claims_analyses(
                fraud_analysis, triage_analysis, settlement_analysis, data, institution_id
            )
            
            # Log audit event
            self.log_audit(
                institution_id=institution_id,
                event_type="AI_CLAIMS_COMPLETED",
                details={
                    "claim_id": claim_id,
                    "fraud_risk_score": fraud_analysis.get('fraud_risk_score'),
                    "triage_category": triage_analysis.get('triage_category'),
                    "final_recommendation": final_result.get('recommendation')
                }
            )
            
            return final_result
            
        except Exception as e:
            return self.handle_error(e, {"claim_id": claim_id}, institution_id)
    
    async def _perform_ai_fraud_detection(self, claim_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Perform AI-powered fraud detection."""
        try:
            # Get claim history (mock for now)
            claim_history = self._get_claim_history(claim_data.get('policy_id', ''))
            
            # Get fraud rules
            fraud_rules = self._get_fraud_rules(institution_id)
            
            response = await self.ai_manager.generate_structured_response(
                template_name='fraud_detection',
                template_variables={
                    'claim_data': json.dumps(claim_data, indent=2),
                    'claim_history': json.dumps(claim_history, indent=2),
                    'fraud_rules': json.dumps(fraud_rules, indent=2)
                }
            )
            
            if response.error:
                self.logger.error(f"AI fraud detection failed: {response.error}")
                return self._fallback_fraud_detection(claim_data)
            
            return self.ai_manager.parse_structured_response(response)
            
        except Exception as e:
            self.logger.error(f"Error in AI fraud detection: {str(e)}")
            return self._fallback_fraud_detection(claim_data)
    
    async def _perform_ai_triage(self, claim_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Perform AI-powered claim triage."""
        try:
            # Get policy data (mock for now)
            policy_data = self._get_policy_data(claim_data.get('policy_id', ''))
            
            # Get triage rules
            triage_rules = self._get_triage_rules(institution_id)
            
            response = await self.ai_manager.generate_structured_response(
                template_name='claim_triage',
                template_variables={
                    'claim_data': json.dumps(claim_data, indent=2),
                    'policy_data': json.dumps(policy_data, indent=2),
                    'triage_rules': json.dumps(triage_rules, indent=2)
                }
            )
            
            if response.error:
                self.logger.error(f"AI triage failed: {response.error}")
                return self._fallback_triage(claim_data)
            
            return self.ai_manager.parse_structured_response(response)
            
        except Exception as e:
            self.logger.error(f"Error in AI triage: {str(e)}")
            return self._fallback_triage(claim_data)
    
    async def _perform_ai_settlement_analysis(self, claim_data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Perform AI-powered settlement analysis."""
        try:
            # Get policy coverage
            policy_coverage = self._get_policy_coverage(claim_data.get('policy_id', ''))
            
            # Get investigation results (mock for now)
            investigation_results = {"status": "preliminary", "findings": []}
            
            # Get settlement guidelines
            settlement_guidelines = self._get_settlement_guidelines(institution_id)
            
            response = await self.ai_manager.generate_structured_response(
                template_name='claim_settlement',
                template_variables={
                    'claim_data': json.dumps(claim_data, indent=2),
                    'policy_coverage': json.dumps(policy_coverage, indent=2),
                    'investigation_results': json.dumps(investigation_results, indent=2),
                    'settlement_guidelines': json.dumps(settlement_guidelines, indent=2)
                }
            )
            
            if response.error:
                self.logger.error(f"AI settlement analysis failed: {response.error}")
                return self._fallback_settlement_analysis(claim_data)
            
            return self.ai_manager.parse_structured_response(response)
            
        except Exception as e:
            self.logger.error(f"Error in AI settlement analysis: {str(e)}")
            return self._fallback_settlement_analysis(claim_data)
    
    def _combine_claims_analyses(self, fraud_analysis: Dict[str, Any], triage_analysis: Dict[str, Any],
                               settlement_analysis: Dict[str, Any], claim_data: Dict[str, Any],
                               institution_id: str) -> Dict[str, Any]:
        """Combine all claims analyses into final result."""
        
        # Determine overall recommendation
        fraud_score = fraud_analysis.get('fraud_risk_score', 0)
        fraud_recommendation = fraud_analysis.get('recommendation', 'approve')
        triage_category = triage_analysis.get('triage_category', 'standard')
        
        if fraud_score > 70 or fraud_recommendation == 'deny':
            final_recommendation = 'deny'
        elif fraud_score > 40 or fraud_recommendation == 'investigate':
            final_recommendation = 'investigate'
        elif triage_category in ['complex', 'specialist']:
            final_recommendation = 'manual_review'
        else:
            final_recommendation = 'approve'
        
        return {
            "claim_id": claim_data.get('claim_id'),
            "recommendation": final_recommendation,
            "fraud_analysis": fraud_analysis,
            "triage_analysis": triage_analysis,
            "settlement_analysis": settlement_analysis,
            "processing_notes": f"AI analysis completed. Fraud risk: {fraud_score}/100, Category: {triage_category}"
        }
    
    def _get_claim_history(self, policy_id: str) -> List[Dict[str, Any]]:
        """Get claim history for policy (mock implementation)."""
        return [
            {"claim_id": "PREV001", "date": "2023-01-15", "amount": 1500, "status": "closed"},
            {"claim_id": "PREV002", "date": "2023-06-20", "amount": 800, "status": "closed"}
        ]
    
    def _get_fraud_rules(self, institution_id: str) -> Dict[str, Any]:
        """Get fraud detection rules."""
        try:
            config = self.config_agent.get_claims_rules(institution_id)
            return config.get('fraud_rules', {})
        except:
            return {"multiple_claims_threshold": 3, "amount_threshold": 10000}
    
    def _get_triage_rules(self, institution_id: str) -> Dict[str, Any]:
        """Get triage rules."""
        return {
            "simple_threshold": 1000,
            "complex_threshold": 10000,
            "specialist_keywords": ["fire", "flood", "structural"]
        }
    
    def _get_policy_data(self, policy_id: str) -> Dict[str, Any]:
        """Get policy data (mock implementation)."""
        return {
            "policy_id": policy_id,
            "status": "active",
            "coverage_limit": 100000,
            "deductible": 500
        }
    
    def _get_policy_coverage(self, policy_id: str) -> Dict[str, Any]:
        """Get policy coverage details."""
        return {
            "property_damage": 100000,
            "liability": 300000,
            "deductible": 500
        }
    
    def _get_settlement_guidelines(self, institution_id: str) -> Dict[str, Any]:
        """Get settlement guidelines."""
        return {
            "auto_approve_limit": 5000,
            "depreciation_rate": 0.1,
            "labor_rate": 75
        }
    
    def _fallback_fraud_detection(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback fraud detection."""
        amount = claim_data.get('claim_amount', 0)
        fraud_score = 10 if amount > 10000 else 5
        
        return {
            "fraud_risk_score": fraud_score,
            "fraud_indicators": [],
            "recommendation": "approve",
            "reasoning": "Fallback fraud detection (AI unavailable)"
        }
    
    def _fallback_triage(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback triage."""
        amount = claim_data.get('claim_amount', 0)
        category = "complex" if amount > 10000 else "simple"
        
        return {
            "triage_category": category,
            "priority": "medium",
            "reasoning": "Fallback triage (AI unavailable)"
        }
    
    def _fallback_settlement_analysis(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback settlement analysis."""
        amount = claim_data.get('claim_amount', 0)
        
        return {
            "coverage_determination": "covered",
            "settlement_amount": amount,
            "reasoning": "Fallback settlement analysis (AI unavailable)"
        }

class AIActuarialAgent(BaseAgent):
    """AI-enhanced actuarial analysis agent."""
    
    def __init__(self, config_agent):
        super().__init__(agent_name="AIActuarialAgent", config_agent=config_agent)
        self.ai_manager = AIServiceManager(config_agent)
    
    def execute(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """
        Execute AI-enhanced actuarial analysis.
        
        Args:
            data: Analysis data
            institution_id: Institution identifier
            
        Returns:
            Enhanced actuarial analysis result
        """
        try:
            analysis_id = data.get('analysis_id', 'unknown')
            self.logger.info(f"Starting AI actuarial analysis {analysis_id}")
            
            # Perform AI risk modeling
            risk_modeling = self._perform_ai_risk_modeling(data, institution_id)
            
            # Perform AI trend analysis
            trend_analysis = self._perform_ai_trend_analysis(data, institution_id)
            
            # Generate AI report
            ai_report = self._generate_ai_report(risk_modeling, trend_analysis, data, institution_id)
            
            # Combine analyses
            final_result = self._combine_actuarial_analyses(
                risk_modeling, trend_analysis, ai_report, data, institution_id
            )
            
            # Log audit event
            self.log_audit(
                institution_id=institution_id,
                event_type="AI_ACTUARIAL_COMPLETED",
                details={
                    "analysis_id": analysis_id,
                    "trends_identified": len(trend_analysis.get('trends_identified', [])),
                    "report_generated": bool(ai_report.get('content'))
                }
            )
            
            return final_result
            
        except Exception as e:
            return self.handle_error(e, {"analysis_id": analysis_id}, institution_id)
    
    async def _perform_ai_risk_modeling(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Perform AI-powered risk modeling."""
        try:
            # Get historical data
            historical_data = data.get('historical_data', data.get('raw_data', []))
            
            # Get market conditions (mock for now)
            market_conditions = self._get_market_conditions()
            
            # Get regulatory info
            regulatory_info = self._get_regulatory_info(institution_id)
            
            response = await self.ai_manager.generate_structured_response(
                template_name='risk_modeling',
                template_variables={
                    'historical_data': json.dumps(historical_data, indent=2),
                    'market_conditions': json.dumps(market_conditions, indent=2),
                    'regulatory_info': json.dumps(regulatory_info, indent=2)
                }
            )
            
            if response.error:
                self.logger.error(f"AI risk modeling failed: {response.error}")
                return self._fallback_risk_modeling(data)
            
            return self.ai_manager.parse_structured_response(response)
            
        except Exception as e:
            self.logger.error(f"Error in AI risk modeling: {str(e)}")
            return self._fallback_risk_modeling(data)
    
    async def _perform_ai_trend_analysis(self, data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Perform AI-powered trend analysis."""
        try:
            dataset = data.get('raw_data', data.get('historical_data', []))
            time_period = data.get('time_period', '2023-2024')
            analysis_focus = data.get('analysis_focus', 'general trends')
            
            response = await self.ai_manager.generate_structured_response(
                template_name='trend_analysis',
                template_variables={
                    'data_set': json.dumps(dataset, indent=2),
                    'time_period': time_period,
                    'analysis_focus': analysis_focus
                }
            )
            
            if response.error:
                self.logger.error(f"AI trend analysis failed: {response.error}")
                return self._fallback_trend_analysis(data)
            
            return self.ai_manager.parse_structured_response(response)
            
        except Exception as e:
            self.logger.error(f"Error in AI trend analysis: {str(e)}")
            return self._fallback_trend_analysis(data)
    
    async def _generate_ai_report(self, risk_modeling: Dict[str, Any], trend_analysis: Dict[str, Any],
                                data: Dict[str, Any], institution_id: str) -> Dict[str, Any]:
        """Generate AI-powered actuarial report."""
        try:
            # Combine analysis results
            analysis_results = {
                "risk_modeling": risk_modeling,
                "trend_analysis": trend_analysis
            }
            
            # Get key metrics
            key_metrics = self._extract_key_metrics(risk_modeling, trend_analysis)
            
            response = await self.ai_manager.generate_response(
                template_name='report_generation',
                template_variables={
                    'analysis_results': json.dumps(analysis_results, indent=2),
                    'report_type': data.get('report_type', 'comprehensive'),
                    'target_audience': data.get('target_audience', 'management'),
                    'key_metrics': json.dumps(key_metrics, indent=2)
                }
            )
            
            if response.error:
                self.logger.error(f"AI report generation failed: {response.error}")
                return {"content": "Report generation failed", "error": response.error}
            
            return {"content": response.content, "format": "markdown"}
            
        except Exception as e:
            self.logger.error(f"Error generating AI report: {str(e)}")
            return {"content": "Report generation error", "error": str(e)}
    
    def _combine_actuarial_analyses(self, risk_modeling: Dict[str, Any], trend_analysis: Dict[str, Any],
                                  ai_report: Dict[str, Any], data: Dict[str, Any],
                                  institution_id: str) -> Dict[str, Any]:
        """Combine all actuarial analyses."""
        
        return {
            "analysis_id": data.get('analysis_id'),
            "status": "completed",
            "risk_modeling": risk_modeling,
            "trend_analysis": trend_analysis,
            "ai_report": ai_report,
            "summary": {
                "trends_count": len(trend_analysis.get('trends_identified', [])),
                "risk_factors": len(risk_modeling.get('emerging_risks', [])),
                "recommendations": len(trend_analysis.get('recommendations', []))
            }
        }
    
    def _get_market_conditions(self) -> Dict[str, Any]:
        """Get current market conditions (mock implementation)."""
        return {
            "interest_rates": 5.25,
            "inflation_rate": 3.2,
            "market_volatility": "moderate",
            "economic_outlook": "stable"
        }
    
    def _get_regulatory_info(self, institution_id: str) -> Dict[str, Any]:
        """Get regulatory information."""
        return {
            "solvency_requirements": "Solvency II",
            "capital_requirements": "150% minimum",
            "reporting_frequency": "quarterly"
        }
    
    def _extract_key_metrics(self, risk_modeling: Dict[str, Any], trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from analyses."""
        return {
            "risk_trends": len(trend_analysis.get('trends_identified', [])),
            "emerging_risks": len(risk_modeling.get('emerging_risks', [])),
            "pricing_adjustment": risk_modeling.get('pricing_recommendations', {}).get('overall_adjustment', 0)
        }
    
    def _fallback_risk_modeling(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback risk modeling."""
        return {
            "risk_trends": [{"trend": "stable", "impact": "neutral"}],
            "pricing_recommendations": {"overall_adjustment": 0},
            "emerging_risks": [],
            "reasoning": "Fallback risk modeling (AI unavailable)"
        }
    
    def _fallback_trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback trend analysis."""
        return {
            "trends_identified": [{"trend_name": "stable", "direction": "stable"}],
            "business_implications": ["No significant changes identified"],
            "recommendations": ["Continue monitoring"],
            "reasoning": "Fallback trend analysis (AI unavailable)"
        }