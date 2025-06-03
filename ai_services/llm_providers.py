"""
LLM Provider implementations for connecting to OpenAI and local LLMs.
"""

import os
import logging
import json
import httpx
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Standardized response from AI providers."""
    content: str
    model: str
    confidence: float = 0.0
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get('model', 'default')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 1000)
        
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> AIResponse:
        """Generate a structured response following a specific schema."""
        pass

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider for GPT models."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.getenv('OPENAI_API_KEY')
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
        self.model = config.get('model', 'gpt-4')
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
    
    async def generate_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate a response using OpenAI API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Merge kwargs with default parameters
            params = {
                'model': kwargs.get('model', self.model),
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': kwargs.get('temperature', self.temperature),
                'max_tokens': kwargs.get('max_tokens', self.max_tokens)
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=params,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return AIResponse(
                        content="",
                        model=self.model,
                        error=error_msg
                    )
                
                data = response.json()
                content = data['choices'][0]['message']['content']
                usage = data.get('usage', {})
                
                return AIResponse(
                    content=content,
                    model=data['model'],
                    usage=usage,
                    metadata={'provider': 'openai'}
                )
                
        except Exception as e:
            error_msg = f"Error calling OpenAI API: {str(e)}"
            logger.error(error_msg)
            return AIResponse(
                content="",
                model=self.model,
                error=error_msg
            )
    
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> AIResponse:
        """Generate a structured response using OpenAI function calling."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Create function definition from schema
            function_def = {
                'name': 'structured_response',
                'description': 'Generate a structured response',
                'parameters': schema
            }
            
            params = {
                'model': kwargs.get('model', self.model),
                'messages': [{'role': 'user', 'content': prompt}],
                'functions': [function_def],
                'function_call': {'name': 'structured_response'},
                'temperature': kwargs.get('temperature', self.temperature)
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=params,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return AIResponse(
                        content="",
                        model=self.model,
                        error=error_msg
                    )
                
                data = response.json()
                function_call = data['choices'][0]['message'].get('function_call')
                
                if function_call:
                    content = function_call['arguments']
                else:
                    content = data['choices'][0]['message']['content']
                
                usage = data.get('usage', {})
                
                return AIResponse(
                    content=content,
                    model=data['model'],
                    usage=usage,
                    metadata={'provider': 'openai', 'structured': True}
                )
                
        except Exception as e:
            error_msg = f"Error calling OpenAI API for structured response: {str(e)}"
            logger.error(error_msg)
            return AIResponse(
                content="",
                model=self.model,
                error=error_msg
            )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        # Import anthropic here to avoid dependency issues
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response using Anthropic Claude."""
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Make API call
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 2000)),
                temperature=kwargs.get('temperature', self.temperature),
                messages=messages
            )
            
            return AIResponse(
                content=response.content[0].text,
                model=self.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                metadata={"provider": "anthropic"}
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return AIResponse(
                content="",
                model=self.model,
                error=f"Anthropic API error: {str(e)}"
            )
    
    async def generate_structured_response(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate structured response using Anthropic Claude."""
        try:
            # Add schema instructions to the prompt
            schema_prompt = f"""
{prompt}

Please respond with a JSON object that follows this exact schema:
{json.dumps(response_schema, indent=2)}

Ensure your response is valid JSON and follows the schema exactly.
"""
            
            response = await self.generate_response(
                schema_prompt,
                system_prompt,
                **kwargs
            )
            
            if response.error:
                return response
            
            # Try to parse as JSON
            try:
                parsed_data = json.loads(response.content)
                return AIResponse(
                    content=json.dumps(parsed_data),
                    model=response.model,
                    usage=response.usage,
                    metadata={'provider': 'anthropic', 'structured': True}
                )
            except json.JSONDecodeError as e:
                return AIResponse(
                    content="",
                    model=self.model,
                    error=f"Failed to parse structured response: {str(e)}"
                )
                
        except Exception as e:
            error_msg = f"Error calling Anthropic API for structured response: {str(e)}"
            logger.error(error_msg)
            return AIResponse(
                content="",
                model=self.model,
                error=error_msg
            )


class LocalLLMProvider(BaseLLMProvider):
    """Local LLM provider for self-hosted models (Ollama, vLLM, LM Studio, etc.)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model = config.get('model', 'llama2')
        self.provider_type = config.get('provider_type', 'ollama')  # ollama, vllm, lmstudio, textgen, etc.
        self.api_key = config.get('api_key')  # Some local providers may require API keys
    
    async def generate_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate a response using local LLM."""
        try:
            if self.provider_type == 'ollama':
                return await self._call_ollama(prompt, **kwargs)
            elif self.provider_type == 'vllm':
                return await self._call_vllm(prompt, **kwargs)
            elif self.provider_type == 'lmstudio':
                return await self._call_lmstudio(prompt, **kwargs)
            elif self.provider_type == 'textgen':
                return await self._call_textgen(prompt, **kwargs)
            elif self.provider_type == 'llamacpp':
                return await self._call_llamacpp(prompt, **kwargs)
            else:
                return await self._call_generic_openai_compatible(prompt, **kwargs)
                
        except Exception as e:
            error_msg = f"Error calling local LLM: {str(e)}"
            logger.error(error_msg)
            return AIResponse(
                content="",
                model=self.model,
                error=error_msg
            )
    
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any], **kwargs) -> AIResponse:
        """Generate a structured response using local LLM."""
        # For local LLMs, we'll add schema instructions to the prompt
        schema_prompt = f"""
{prompt}

Please respond with a JSON object that follows this schema:
{json.dumps(schema, indent=2)}

Ensure your response is valid JSON and follows the schema exactly.
"""
        
        response = await self.generate_response(schema_prompt, **kwargs)
        if response.content and not response.error:
            response.metadata = {'provider': 'local', 'structured': True}
        
        return response
    
    async def _call_ollama(self, prompt: str, **kwargs) -> AIResponse:
        """Call Ollama API."""
        params = {
            'model': kwargs.get('model', self.model),
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': kwargs.get('temperature', self.temperature),
                'num_predict': kwargs.get('max_tokens', self.max_tokens)
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/api/generate',
                json=params,
                timeout=120.0
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return AIResponse(
                    content="",
                    model=self.model,
                    error=error_msg
                )
            
            data = response.json()
            content = data.get('response', '')
            
            return AIResponse(
                content=content,
                model=data.get('model', self.model),
                metadata={'provider': 'ollama'}
            )
    
    async def _call_vllm(self, prompt: str, **kwargs) -> AIResponse:
        """Call vLLM API (OpenAI-compatible)."""
        return await self._call_generic_openai_compatible(prompt, **kwargs)
    
    async def _call_lmstudio(self, prompt: str, **kwargs) -> AIResponse:
        """Call LM Studio API."""
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        params = {
            'model': kwargs.get('model', self.model),
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': kwargs.get('temperature', self.temperature),
            'max_tokens': kwargs.get('max_tokens', self.max_tokens)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/v1/chat/completions',
                headers=headers,
                json=params,
                timeout=120.0
            )
            
            if response.status_code != 200:
                error_msg = f"LM Studio API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return AIResponse(
                    content="",
                    model=self.model,
                    error=error_msg
                )
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            
            return AIResponse(
                content=content,
                model=data.get('model', self.model),
                usage=usage,
                metadata={'provider': 'lmstudio'}
            )
    
    async def _call_textgen(self, prompt: str, **kwargs) -> AIResponse:
        """Call Text Generation WebUI API."""
        params = {
            'prompt': prompt,
            'max_new_tokens': kwargs.get('max_tokens', self.max_tokens),
            'temperature': kwargs.get('temperature', self.temperature),
            'do_sample': True,
            'top_p': kwargs.get('top_p', 0.9),
            'typical_p': kwargs.get('typical_p', 1),
            'repetition_penalty': kwargs.get('repetition_penalty', 1.1),
            'encoder_repetition_penalty': kwargs.get('encoder_repetition_penalty', 1),
            'top_k': kwargs.get('top_k', 40),
            'min_length': kwargs.get('min_length', 0),
            'no_repeat_ngram_size': kwargs.get('no_repeat_ngram_size', 0),
            'num_beams': kwargs.get('num_beams', 1),
            'penalty_alpha': kwargs.get('penalty_alpha', 0),
            'length_penalty': kwargs.get('length_penalty', 1),
            'early_stopping': kwargs.get('early_stopping', False),
            'seed': kwargs.get('seed', -1),
            'add_bos_token': kwargs.get('add_bos_token', True),
            'truncation_length': kwargs.get('truncation_length', 2048),
            'ban_eos_token': kwargs.get('ban_eos_token', False),
            'skip_special_tokens': kwargs.get('skip_special_tokens', True),
            'stopping_strings': kwargs.get('stopping_strings', [])
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/api/v1/generate',
                json=params,
                timeout=120.0
            )
            
            if response.status_code != 200:
                error_msg = f"Text Generation WebUI API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return AIResponse(
                    content="",
                    model=self.model,
                    error=error_msg
                )
            
            data = response.json()
            content = data['results'][0]['text'] if data.get('results') else ""
            
            return AIResponse(
                content=content,
                model=self.model,
                metadata={'provider': 'textgen'}
            )
    
    async def _call_llamacpp(self, prompt: str, **kwargs) -> AIResponse:
        """Call llama.cpp server API."""
        params = {
            'prompt': prompt,
            'n_predict': kwargs.get('max_tokens', self.max_tokens),
            'temperature': kwargs.get('temperature', self.temperature),
            'top_k': kwargs.get('top_k', 40),
            'top_p': kwargs.get('top_p', 0.9),
            'repeat_penalty': kwargs.get('repeat_penalty', 1.1),
            'repeat_last_n': kwargs.get('repeat_last_n', 64),
            'penalize_nl': kwargs.get('penalize_nl', True),
            'presence_penalty': kwargs.get('presence_penalty', 0.0),
            'frequency_penalty': kwargs.get('frequency_penalty', 0.0),
            'mirostat': kwargs.get('mirostat', 0),
            'mirostat_tau': kwargs.get('mirostat_tau', 5.0),
            'mirostat_eta': kwargs.get('mirostat_eta', 0.1),
            'seed': kwargs.get('seed', -1),
            'ignore_eos': kwargs.get('ignore_eos', False),
            'stream': False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/completion',
                json=params,
                timeout=120.0
            )
            
            if response.status_code != 200:
                error_msg = f"llama.cpp API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return AIResponse(
                    content="",
                    model=self.model,
                    error=error_msg
                )
            
            data = response.json()
            content = data.get('content', '')
            
            return AIResponse(
                content=content,
                model=self.model,
                usage={
                    'prompt_tokens': data.get('tokens_evaluated', 0),
                    'completion_tokens': data.get('tokens_predicted', 0),
                    'total_tokens': data.get('tokens_evaluated', 0) + data.get('tokens_predicted', 0)
                },
                metadata={'provider': 'llamacpp'}
            )

    async def _call_generic_openai_compatible(self, prompt: str, **kwargs) -> AIResponse:
        """Call OpenAI-compatible API."""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        params = {
            'model': kwargs.get('model', self.model),
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': kwargs.get('temperature', self.temperature),
            'max_tokens': kwargs.get('max_tokens', self.max_tokens)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.base_url}/v1/chat/completions',
                headers=headers,
                json=params,
                timeout=120.0
            )
            
            if response.status_code != 200:
                error_msg = f"Local LLM API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return AIResponse(
                    content="",
                    model=self.model,
                    error=error_msg
                )
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
            
            return AIResponse(
                content=content,
                model=data.get('model', self.model),
                usage=usage,
                metadata={'provider': 'local'}
            )

class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    @staticmethod
    def create_provider(provider_type: str, config: Dict[str, Any]) -> BaseLLMProvider:
        """Create an LLM provider based on type."""
        if provider_type.lower() == 'openai':
            return OpenAIProvider(config)
        elif provider_type.lower() == 'anthropic':
            return AnthropicProvider(config)
        elif provider_type.lower() in ['local', 'ollama', 'vllm', 'lmstudio', 'textgen', 'llamacpp']:
            return LocalLLMProvider(config)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")