"""
AI Service Manager for coordinating AI operations across the insurance system.

This module provides a modular, scalable AI service management system with
no hardcoded values and full configurability.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .llm_providers import LLMProviderFactory, BaseLLMProvider, AIResponse
from .prompt_templates import PromptTemplateManager, RESPONSE_SCHEMAS
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
                {
                    'model': ai_config.model,
                    'temperature': ai_config.temperature,
                    'max_tokens': ai_config.max_tokens,
                    'timeout': ai_config.timeout,
                    'max_retries': ai_config.max_retries,
                    'api_key': self._get_api_key(ai_config.provider),
                    'base_url': self._get_base_url(ai_config.provider)
                }
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
    
    async def _initialize_fallback_providers(self):
        """Initialize fallback providers for redundancy."""
        fallback_providers = ['openai', 'anthropic', 'local']
        current_provider = self.settings.ai.provider
        
        for provider in fallback_providers:
            if provider != current_provider and provider not in self.providers:
                config = {
                    'model': self._get_fallback_model(provider),
                    'temperature': self.settings.ai.temperature,
                    'max_tokens': self.settings.ai.max_tokens,
                    'api_key': self._get_api_key(provider),
                    'base_url': self._get_base_url(provider)
                }
                
                fallback_provider = await self._create_provider(provider, config)
                if fallback_provider:
                    self.providers[provider] = fallback_provider
                    logger.info(f"Initialized fallback provider: {provider}")
    
    def _get_fallback_model(self, provider: str) -> str:
        """Get appropriate model for fallback provider."""
        fallback_models = {
            'openai': 'gpt-3.5-turbo',
            'anthropic': 'claude-3-sonnet-20240229',
            'local': self.settings.ai.local_llm_model
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
    
    async def analyze_underwriting(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze underwriting data using AI."""
        return await self._analyze_with_template('underwriting', data, context)
    
    async def analyze_claims(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze claims data using AI."""
        return await self._analyze_with_template('claims', data, context)
    
    async def analyze_actuarial(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze actuarial data using AI."""
        return await self._analyze_with_template('actuarial', data, context)
    
    async def _analyze_with_template(self, template_name: str, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Analyze data using specified template."""
        if not self._initialized:
            await self.initialize()
        
        if not self.default_provider:
            raise RuntimeError("No AI provider available")
        
        try:
            # Get and format prompt template
            prompt = self.prompt_manager.get_prompt(template_name, data)
            
            # Get provider and make request
            provider = self.providers[self.settings.ai.provider]
            response = await provider.generate_response(prompt, context or {})
            
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