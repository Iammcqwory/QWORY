#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenRouter Model Integration

This module implements integration with OpenRouter to support various models including 
Deepseek, Ollama models, and other open-source models through a unified API.
"""

import json
import logging
import os
import requests
from typing import Any, Dict, List, Optional, Union

from .base_model import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OpenRouterModel(BaseModel):
    """
    Integration with OpenRouter for accessing various AI models.
    
    This class implements the BaseModel interface for models available through OpenRouter,
    including Deepseek, Ollama-hosted models, and other providers.
    """
    
    # OpenRouter API base URL
    API_BASE = "https://openrouter.ai/api/v1"
    
    # Default models for different types
    DEFAULT_MODELS = {
        "deepseek": "deepseek/deepseek-chat",
        "ollama": "ollama/llama3",
        "mistral": "mistralai/mistral-medium",
        "claude": "anthropic/claude-3-opus",
        "mixtral": "mistralai/mixtral-8x7b",
        "yi": "01-ai/yi-large"
    }
    
    def __init__(self, 
                model_name: str = "deepseek/deepseek-chat", 
                api_key: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OpenRouter model integration.
        
        Args:
            model_name: The name of the model to use (provider/model format).
            api_key: The OpenRouter API key. If None, it will be loaded from the OPENROUTER_API_KEY
                    environment variable.
            config: Additional configuration parameters.
        
        Raises:
            ValueError: If the API key is not provided and not found in the environment.
        """
        super().__init__(model_name, config)
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Please provide it as an argument or "
                "set the OPENROUTER_API_KEY environment variable."
            )
        
        # Ensure config is not None
        if config is None:
            config = {}
            
        # Ensure config is not None
        if config is None:
            config = {}
            
        # Set up headers for OpenRouter API
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": config.get("http_referer", "https://github.com/yourusername/qwory"),  # Your site URL
            "X-Title": config.get("x_title", "Qwory Framework")  # Your site name
        }
        
        # Store additional configuration
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1024)
        
        logger.info(f"OpenRouter model {model_name} initialized")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on the provided prompt using an OpenRouter model.
        
        Args:
            prompt: The text prompt to generate from.
            **kwargs: Additional parameters to pass to the OpenRouter API.
            
        Returns:
            The generated text.
            
        Raises:
            Exception: If there's an error communicating with the OpenRouter API.
        """
        try:
            # Prepare the request payload
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }
            
            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            # Make the API request
            response = requests.post(
                f"{self.API_BASE}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating text with OpenRouter: {e}")
            raise
    
    def generate_with_json(self, 
                          prompt: str, 
                          json_schema: Dict[str, Any],
                          **kwargs) -> Dict[str, Any]:
        """
        Generate structured JSON output based on the provided prompt and schema.
        
        Args:
            prompt: The text prompt to generate from.
            json_schema: The JSON schema that defines the expected output format.
            **kwargs: Additional parameters to pass to the OpenRouter API.
            
        Returns:
            A dictionary conforming to the provided JSON schema.
            
        Raises:
            Exception: If there's an error communicating with the OpenRouter API or
                      parsing the generated JSON.
        """
        try:
            # Create system message with JSON instruction
            system_message = f"You must respond with valid JSON that conforms to this schema: {json.dumps(json_schema)}"
            
            # Prepare the request payload
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "response_format": {"type": "json_object"}
            }
            
            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            # Make the API request
            response = requests.post(
                f"{self.API_BASE}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            result_text = result["choices"][0]["message"]["content"].strip()
            
            # If the result is wrapped in triple backticks for code block, extract it
            if result_text.startswith("```json") and result_text.endswith("```"):
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif result_text.startswith("```") and result_text.endswith("```"):
                result_text = result_text[3:-3].strip()
            
            return json.loads(result_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.error(f"Raw response: {result_text}")
            raise
        except Exception as e:
            logger.error(f"Error generating JSON with OpenRouter: {e}")
            raise
    
    def chat(self, 
            messages: List[Dict[str, str]], 
            **kwargs) -> str:
        """
        Generate a response in a chat context.
        
        Args:
            messages: A list of message dictionaries. Each message should have
                     'role' (system, user, assistant) and 'content' keys.
            **kwargs: Additional parameters to pass to the OpenRouter API.
            
        Returns:
            The model's response text.
            
        Raises:
            Exception: If there's an error communicating with the OpenRouter API.
        """
        try:
            # Prepare the request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }
            
            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value
            
            # Make the API request
            response = requests.post(
                f"{self.API_BASE}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating chat response with OpenRouter: {e}")
            raise
    
    def chat_with_functions(self,
                           messages: List[Dict[str, str]],
                           functions: List[Dict[str, Any]],
                           **kwargs) -> Dict[str, Any]:
        """
        Generate a response in a chat context with function calling capabilities.
        
        Args:
            messages: A list of message dictionaries. Each message should have
                     'role' (system, user, assistant) and 'content' keys.
            functions: A list of function definitions that the model can call.
            **kwargs: Additional parameters to pass to the OpenRouter API.
            
        Returns:
            A dictionary containing the response and/or function call information.
            
        Raises:
            Exception: If there's an error communicating with the OpenRouter API.
        """
        try:
            # Check if the model supports tools/functions
            supports_tools = self._model_supports_tools()
            
            if supports_tools:
                # Use the native tools/function calling for supported models
                payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "tools": [{"type": "function", "function": func} for func in functions],
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                }
                
                # Add any additional parameters
                for key, value in kwargs.items():
                    if key not in payload:
                        payload[key] = value
                
                # Make the API request
                response = requests.post(
                    f"{self.API_BASE}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                message = result["choices"][0]["message"]
                
                # Extract function call if present
                function_call = None
                if "tool_calls" in message and message["tool_calls"]:
                    tool_call = message["tool_calls"][0]
                    function_call = {
                        "name": tool_call["function"]["name"],
                        "arguments": json.loads(tool_call["function"]["arguments"])
                    }
                
                return {
                    "content": message.get("content"),
                    "function_call": function_call
                }
            else:
                # Use a prompt-based approach for models without native function calling
                # Convert functions to a format the model can understand
                functions_str = json.dumps(functions, indent=2)
                
                # Create system prompt with function definitions
                system_prompt = (
                    "You have access to the following functions:\n\n"
                    f"{functions_str}\n\n"
                    "When you need to use a function, respond with JSON in this format:\n"
                    "```json\n"
                    "{\n"
                    '  "function_call": {\n'
                    '    "name": "function_name",\n'
                    '    "arguments": {\n'
                    '      "arg1": "value1",\n'
                    '      "arg2": "value2"\n'
                    '    }\n'
                    '  }\n'
                    "}\n"
                    "```\n"
                    "If you don't need to use a function, just respond normally."
                )
                
                # Add or update system message
                if messages and messages[0]["role"] == "system":
                    messages[0]["content"] += "\n\n" + system_prompt
                else:
                    messages.insert(0, {"role": "system", "content": system_prompt})
                
                # Get chat response
                response_text = self.chat(messages, **kwargs)
                
                # Extract function call from the response if it exists
                function_call = None
                try:
                    # First, try to find JSON block within markdown code blocks
                    if "```json" in response_text and "```" in response_text:
                        json_text = response_text.split("```json")[1].split("```")[0].strip()
                        parsed_response = json.loads(json_text)
                        if "function_call" in parsed_response:
                            function_call = parsed_response["function_call"]
                            # Set response content to None since it's a function call
                            response_text = None
                    # If no code block, try parsing the entire response as JSON
                    elif response_text.strip().startswith("{") and response_text.strip().endswith("}"):
                        parsed_response = json.loads(response_text)
                        if "function_call" in parsed_response:
                            function_call = parsed_response["function_call"]
                            # Set response content to None since it's a function call
                            response_text = None
                except (json.JSONDecodeError, IndexError):
                    # Not a function call, just use the text response
                    pass
                
                return {
                    "content": response_text,
                    "function_call": function_call
                }
        except Exception as e:
            logger.error(f"Error generating function call with OpenRouter: {e}")
            raise
    
    def embed(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for the provided text.
        
        Args:
            text: The text or list of texts to generate embeddings for.
            **kwargs: Additional parameters to pass to the OpenRouter API.
            
        Returns:
            A list of embedding vectors (lists of floats).
            
        Raises:
            Exception: If there's an error communicating with the OpenRouter API.
        """
        try:
            # Ensure text is a list
            if isinstance(text, str):
                text = [text]
            
            # Use OpenAI-compatible embeddings endpoint
            payload = {
                "model": kwargs.get("embedding_model", "openai/text-embedding-ada-002"),
                "input": text
            }
            
            # Make the API request
            response = requests.post(
                f"{self.API_BASE}/embeddings",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return [item["embedding"] for item in result["data"]]
        except Exception as e:
            logger.error(f"Error generating embeddings with OpenRouter: {e}")
            raise
    
    def _model_supports_tools(self) -> bool:
        """
        Check if the current model supports native function/tool calling.
        
        Returns:
            True if the model supports tools, False otherwise.
        """
        # Models known to support function/tool calling on OpenRouter
        tool_supporting_models = [
            "openai/",         # OpenAI models (GPT-4, etc.)
            "anthropic/claude-3",  # Claude 3 models
            "meta-llama/llama-3",  # Llama 3 models that support tool calling
            "groq/llama3"      # Groq's Llama 3 models
        ]
        
        return any(self.model_name.startswith(prefix) for prefix in tool_supporting_models)
    
    @classmethod
    def get_available_models(cls, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of available models from OpenRouter.
        
        Args:
            api_key: The OpenRouter API key. If None, it will be loaded from the OPENROUTER_API_KEY
                    environment variable.
            
        Returns:
            A list of dictionaries containing information about available models.
            
        Raises:
            Exception: If there's an error communicating with the OpenRouter API.
        """
        api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenRouter API key is required. Please provide it as an argument or "
                "set the OPENROUTER_API_KEY environment variable."
            )
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            response = requests.get(
                f"{cls.API_BASE}/models",
                headers=headers
            )
            response.raise_for_status()
            
            return response.json()["data"]
        except Exception as e:
            logger.error(f"Error fetching available models from OpenRouter: {e}")
            raise