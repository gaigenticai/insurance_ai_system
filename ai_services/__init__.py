"""
AI Services module for the Insurance AI System.
Provides AI-powered capabilities for underwriting, claims, and actuarial analysis.
"""

from .ai_service_manager import AIServiceManager
from .llm_providers import OpenAIProvider, LocalLLMProvider
from .prompt_templates import PromptTemplateManager
from .ai_agents import (
    AIUnderwritingAgent,
    AIClaimsAgent, 
    AIActuarialAgent
)

__all__ = [
    'AIServiceManager',
    'OpenAIProvider',
    'LocalLLMProvider', 
    'PromptTemplateManager',
    'AIUnderwritingAgent',
    'AIClaimsAgent',
    'AIActuarialAgent'
]