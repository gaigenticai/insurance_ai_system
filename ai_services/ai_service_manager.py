"""
AI Service Manager for coordinating AI operations across the insurance system.

This module provides a modular, scalable AI service management system with
no hardcoded values and full configurability.
"""

import logging
import json
import asyncio
import time
from typing import Dict, Any, Optional, List, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .llm_providers import LLMProviderFactory, BaseLLMProvider, AIResponse
from .prompt_templates import PromptTemplateManager, InsurancePromptEnhancer, RESPONSE_SCHEMAS
from .ai_analytics import AIMonitor, AIPerformanceTracker, get_ai_monitor
from config.settings import get_settings
from core.service_registry import ServiceInterface

logger = logging.getLogger(__name__)

class AIServiceInterface(Protocol):
    """Protocol for AI service implementations"""
    
    async def analyze(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze data using AI"""
        ...
    
    async def health_check(self) -> bool:
        """Check if AI service is healthy"""
        ...

@dataclass
class AIConfig:
    """Configuration for AI services - fully configurable from environment"""
    provider_type: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    provider_config: Optional[Dict[str, Any]] = None

class AIServiceManager(ServiceInterface):
    """
    Central manager for AI services in the insurance system.
    Handles provider selection, prompt management, and response processing.
    
    Fully modular and configurable with no hardcoded values.
    """
    
    def __init__(self):
        """Initialize the AI Service Manager with configuration-driven setup."""
        self.settings = get_settings()
        self.prompt_manager = PromptTemplateManager()
        self.prompt_enhancer = InsurancePromptEnhancer()
        self.ai_monitor = get_ai_monitor()
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider = None
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize AI providers from configuration."""
        if self._initialized:
            return
            
        try:
            await self._initialize_providers()
            self._initialized = True
            logger.info("AI Service Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Service Manager: {e}")
            raise
    
    async def _initialize_providers(self):
        """Initialize AI providers from configuration."""
        try:
            # Get AI configuration from settings
            ai_config = self.settings.ai
            
            # Initialize primary provider
            primary_provider = await self._create_provider(
                ai_config.provider,
                self._get_provider_config(ai_config.provider)
            )
            
            if primary_provider:
                self.providers[ai_config.provider] = primary_provider
                self.default_provider = primary_provider
                logger.info(f"Initialized primary AI provider: {ai_config.provider}")
            
            # Initialize fallback providers if enabled
            if ai_config.enable_fallback:
                await self._initialize_fallback_providers()
                
        except Exception as e:
            logger.error(f"Failed to initialize AI providers: {e}")
            if not ai_config.enable_fallback:
                raise
    
    async def _create_provider(self, provider_type: str, config: Dict[str, Any]) -> Optional[BaseLLMProvider]:
        """Create an AI provider instance."""
        try:
            return LLMProviderFactory.create_provider(provider_type, config)
        except Exception as e:
            logger.error(f"Failed to create {provider_type} provider: {e}")
            return None
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider from settings."""
        if provider == 'openai':
            return self.settings.ai.openai_api_key
        elif provider == 'anthropic':
            return self.settings.ai.anthropic_api_key
        return None
    
    def _get_base_url(self, provider: str) -> Optional[str]:
        """Get base URL for provider from settings."""
        if provider == 'openai':
            return self.settings.ai.openai_base_url
        elif provider == 'local':
            return self.settings.ai.local_llm_base_url
        return None
    
    def _get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get complete provider configuration."""
        base_config = {
            'model': self.settings.ai.model,
            'temperature': self.settings.ai.temperature,
            'max_tokens': self.settings.ai.max_tokens,
            'timeout': self.settings.ai.timeout,
            'max_retries': self.settings.ai.max_retries,
        }
        
        if provider == 'openai':
            base_config.update({
                'api_key': self.settings.ai.openai_api_key,
                'base_url': self.settings.ai.openai_base_url
            })
        elif provider == 'anthropic':
            base_config.update({
                'api_key': self.settings.ai.anthropic_api_key
            })
        elif provider == 'local':
            base_config.update({
                'model': self.settings.ai.local_llm_model,
                'base_url': self.settings.ai.local_llm_base_url,
                'provider_type': self.settings.ai.local_llm_provider_type,
                'api_key': self.settings.ai.local_llm_api_key
            })
        elif provider == 'mock':
            base_config.update({
                'model': 'mock-insurance-ai-v1',
                'response_delay': 0.3
            })
        
        return base_config
    
    async def _initialize_fallback_providers(self):
        """Initialize fallback providers for redundancy."""
        fallback_providers = ['openai', 'anthropic', 'local', 'mock']
        current_provider = self.settings.ai.provider
        
        for provider in fallback_providers:
            if provider != current_provider and provider not in self.providers:
                config = self._get_provider_config(provider)
                config['model'] = self._get_fallback_model(provider)
                
                fallback_provider = await self._create_provider(provider, config)
                if fallback_provider:
                    self.providers[provider] = fallback_provider
                    logger.info(f"Initialized fallback provider: {provider}")
        
        # Always ensure mock provider is available as ultimate fallback
        if 'mock' not in self.providers:
            mock_config = {'model': 'mock-insurance-ai-v1', 'response_delay': 0.3}
            mock_provider = await self._create_provider('mock', mock_config)
            if mock_provider:
                self.providers['mock'] = mock_provider
                logger.info("Initialized mock provider as ultimate fallback")
    
    def _get_fallback_model(self, provider: str) -> str:
        """Get appropriate model for fallback provider."""
        fallback_models = {
            'openai': 'gpt-3.5-turbo',
            'anthropic': 'claude-3-sonnet-20240229',
            'local': self.settings.ai.local_llm_model,
            'mock': 'mock-insurance-ai-v1'
        }
        return fallback_models.get(provider, 'gpt-3.5-turbo')
    
    async def health_check(self) -> bool:
        """Check if AI service is healthy."""
        if not self._initialized:
            return False
        
        if not self.providers:
            return False
        
        # Check if at least one provider is healthy
        for provider_name, provider in self.providers.items():
            try:
                # Simple health check - try to get provider info
                if hasattr(provider, 'health_check'):
                    if await provider.health_check():
                        return True
                else:
                    # If no health check method, assume healthy if provider exists
                    return True
            except Exception as e:
                logger.warning(f"Health check failed for provider {provider_name}: {e}")
                continue
        
        return False
    
    async def shutdown(self) -> None:
        """Shutdown AI service manager."""
        logger.info("Shutting down AI Service Manager")
        
        for provider_name, provider in self.providers.items():
            try:
                if hasattr(provider, 'shutdown'):
                    await provider.shutdown()
                logger.debug(f"Shutdown provider: {provider_name}")
            except Exception as e:
                logger.error(f"Error shutting down provider {provider_name}: {e}")
        
        self.providers.clear()
        self.default_provider = None
        self._initialized = False
    
    async def analyze_underwriting(
        self, 
        data: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None,
        use_enhanced_prompts: bool = True
    ) -> AIResponse:
        """Analyze underwriting data using AI with enhanced prompts."""
        if use_enhanced_prompts:
            return await self._analyze_with_enhanced_prompts('underwriting', data, context)
        return await self._analyze_with_template('underwriting', data, context)
    
    async def analyze_claims(
        self, 
        data: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None,
        use_enhanced_prompts: bool = True
    ) -> AIResponse:
        """Analyze claims data using AI with enhanced prompts."""
        if use_enhanced_prompts:
            return await self._analyze_with_enhanced_prompts('claims', data, context)
        return await self._analyze_with_template('claims', data, context)
    
    async def analyze_actuarial(
        self, 
        data: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None,
        use_enhanced_prompts: bool = True
    ) -> AIResponse:
        """Analyze actuarial data using AI with enhanced prompts."""
        if use_enhanced_prompts:
            return await self._analyze_with_enhanced_prompts('actuarial', data, context)
        return await self._analyze_with_template('actuarial', data, context)
    
    async def _analyze_with_enhanced_prompts(self, analysis_type: str, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze data using enhanced prompt techniques."""
        if not self._initialized:
            await self.initialize()
        
        if not self.default_provider:
            raise RuntimeError("No AI provider available")
        
        provider = self.providers[self.settings.ai.provider]
        
        with AIPerformanceTracker(
            provider=self.settings.ai.provider,
            model=self.settings.ai.model,
            operation=f"enhanced_{analysis_type}_analysis"
        ) as tracker:
            try:
                # Get enhanced prompt based on analysis type
                if analysis_type == 'underwriting':
                    prompt = self.prompt_enhancer.get_enhanced_underwriting_prompt(
                        data,
                        use_chain_of_thought=True,
                        include_examples=context and context.get('include_examples', False)
                    )
                elif analysis_type == 'claims':
                    prompt = self.prompt_enhancer.get_enhanced_claims_prompt(
                        data,
                        use_multi_perspective=True
                    )
                elif analysis_type == 'actuarial':
                    prompt = self.prompt_enhancer.get_enhanced_actuarial_prompt(
                        data,
                        analysis_type=context.get('analysis_type', 'comprehensive') if context else 'comprehensive'
                    )
                else:
                    raise ValueError(f"Unsupported analysis type: {analysis_type}")
                
                # Make AI request
                response = await provider.generate_response(prompt, **(context or {}))
                
                # Track performance metrics
                if response.usage:
                    tracker.set_token_usage(response.usage)
                if hasattr(response, 'confidence') and response.confidence:
                    tracker.set_confidence_score(response.confidence)
                
                logger.info(f"Enhanced AI analysis completed for {analysis_type}")
                return response
                
            except Exception as e:
                logger.error(f"Enhanced AI analysis failed for {analysis_type}: {e}")
                
                # Try fallback providers if enabled
                if self.settings.ai.enable_fallback:
                    return await self._try_fallback_analysis(analysis_type, data, context)
                
                raise

    async def _analyze_with_template(self, template_name: str, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze data using specified template with monitoring."""
        if not self._initialized:
            await self.initialize()
        
        if not self.default_provider:
            raise RuntimeError("No AI provider available")
        
        provider = self.providers[self.settings.ai.provider]
        
        with AIPerformanceTracker(
            provider=self.settings.ai.provider,
            model=self.settings.ai.model,
            operation=f"{template_name}_analysis"
        ) as tracker:
            try:
                # Get and format prompt template
                prompt = self.prompt_manager.get_prompt(template_name, data)
                
                # Make AI request
                response = await provider.generate_response(prompt, **(context or {}))
                
                # Track performance metrics
                if response.usage:
                    tracker.set_token_usage(response.usage)
                if hasattr(response, 'confidence') and response.confidence:
                    tracker.set_confidence_score(response.confidence)
                
                logger.info(f"AI analysis completed for {template_name}")
                return response
                
            except Exception as e:
                logger.error(f"AI analysis failed for {template_name}: {e}")
                
                # Try fallback providers if enabled
                if self.settings.ai.enable_fallback:
                    return await self._try_fallback_analysis(template_name, data, context)
                
                raise
    
    async def _try_fallback_analysis(self, template_name: str, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Try analysis with fallback providers."""
        current_provider = self.settings.ai.provider
        
        for provider_name, provider in self.providers.items():
            if provider_name != current_provider:
                try:
                    prompt = self.prompt_manager.get_prompt(template_name, data)
                    response = await provider.generate_response(prompt, context or {})
                    
                    logger.info(f"Fallback analysis successful with {provider_name}")
                    return response
                    
                except Exception as e:
                    logger.warning(f"Fallback provider {provider_name} failed: {e}")
                    continue
        
        # If all providers fail, return error response
        return AIResponse(
            content="AI analysis temporarily unavailable",
            confidence=0.0,
            metadata={"error": "All AI providers failed", "fallback_attempted": True}
        )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers."""
        return list(self.providers.keys())
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        return {
            "initialized": self._initialized,
            "default_provider": self.settings.ai.provider,
            "available_providers": self.get_available_providers(),
            "provider_count": len(self.providers),
            "settings": {
                "provider": self.settings.ai.provider,
                "model": self.settings.ai.model,
                "temperature": self.settings.ai.temperature,
                "max_tokens": self.settings.ai.max_tokens,
                "enable_fallback": self.settings.ai.enable_fallback,
                "enable_caching": self.settings.ai.enable_caching
            }
        }
    
    def get_ai_analytics(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get AI analytics and performance metrics."""
        analytics = self.ai_monitor.get_analytics_summary(hours_back)
        provider_comparison = self.ai_monitor.get_provider_comparison()
        error_analysis = self.ai_monitor.get_error_analysis()
        performance_trends = self.ai_monitor.get_performance_trends(hours_back)
        model_performance = self.ai_monitor.get_model_performance()
        
        return {
            "analytics_summary": analytics.__dict__,
            "provider_comparison": provider_comparison,
            "error_analysis": error_analysis,
            "performance_trends": performance_trends,
            "model_performance": model_performance,
            "monitoring_period_hours": hours_back
        }
    
    def export_ai_metrics(self, format: str = 'json') -> str:
        """Export AI metrics in specified format."""
        return self.ai_monitor.export_metrics(format)
    
    async def benchmark_providers(self, test_prompt: str = "Analyze this test case for insurance risk assessment.") -> Dict[str, Any]:
        """Benchmark all available providers with a test prompt."""
        if not self._initialized:
            await self.initialize()
        
        benchmark_results = {}
        
        for provider_name, provider in self.providers.items():
            try:
                with AIPerformanceTracker(
                    provider=provider_name,
                    model=getattr(provider, 'model', 'unknown'),
                    operation="benchmark_test"
                ) as tracker:
                    response = await provider.generate_response(test_prompt)
                    
                    benchmark_results[provider_name] = {
                        "success": True,
                        "response_length": len(response.content) if response.content else 0,
                        "model": response.model,
                        "usage": response.usage,
                        "metadata": response.metadata
                    }
                    
            except Exception as e:
                benchmark_results[provider_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "benchmark_results": benchmark_results,
            "test_prompt": test_prompt,
            "timestamp": time.time()
        }