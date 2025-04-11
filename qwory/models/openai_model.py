#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI Model Integration

This module implements integration with OpenAI's models like GPT-4.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
import os

try:
    import openai
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

from .base_model import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OpenAIModel(BaseModel):
    """
    Integration with OpenAI models.
    
    This class implements the BaseModel interface for OpenAI models like GPT-4, GPT-4o,
    GPT-3.5-turbo, etc.
    """
    
    def __init__(self, 
                model_name: str = "gpt-4o", 
                api_key: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OpenAI model integration.
        
        Args:
            model_name: The name of the model to use (e.g., "gpt-4o", "gpt-4", "gpt-3.5-turbo").
            api_key: The OpenAI API key. If None, it will be loaded from the OPENAI_API_KEY
                    environment variable.
            config: Additional configuration parameters.
        
        Raises:
            ImportError: If the openai package is not installed.
            ValueError: If the API key is not provided and not found in the environment.
        """
        super().__init__(model_name, config)
        
        if not HAS_OPENAI:
            raise ImportError(
                "The 'openai' package is required for OpenAI model integration. "
                "Please install it using 'pip install openai'."
            )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Please provide it as an argument or "
                "set the OPENAI_API_KEY environment variable."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"OpenAI model {model_name} initialized")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on the provided prompt using an OpenAI model.
        
        Args:
            prompt: The text prompt to generate from.
            **kwargs: Additional parameters to pass to the OpenAI API.
            
        Returns:
            The generated text.
            
        Raises:
            Exception: If there's an error communicating with the OpenAI API.
        """
        try:
            response = self.client.completions.create(
                model=self.model_name,
                prompt=prompt,
                **kwargs
            )
            return response.choices[0].text.strip()
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
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
            **kwargs: Additional parameters to pass to the OpenAI API.
            
        Returns:
            A dictionary conforming to the provided JSON schema.
            
        Raises:
            Exception: If there's an error communicating with the OpenAI API or
                      parsing the generated JSON.
        """
        try:
            messages = [
                {"role": "system", "content": f"You must respond with valid JSON that conforms to this schema: {json.dumps(json_schema)}"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                **kwargs
            )
            
            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating JSON with OpenAI: {e}")
            raise
    
    def chat(self, 
            messages: List[Dict[str, str]], 
            **kwargs) -> str:
        """
        Generate a response in a chat context.
        
        Args:
            messages: A list of message dictionaries. Each message should have
                     'role' (system, user, assistant) and 'content' keys.
            **kwargs: Additional parameters to pass to the OpenAI API.
            
        Returns:
            The model's response text.
            
        Raises:
            Exception: If there's an error communicating with the OpenAI API.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating chat response with OpenAI: {e}")
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
            **kwargs: Additional parameters to pass to the OpenAI API.
            
        Returns:
            A dictionary containing the response and/or function call information.
            
        Raises:
            Exception: If there's an error communicating with the OpenAI API.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=[{"type": "function", "function": func} for func in functions],
                **kwargs
            )
            
            message = response.choices[0].message
            
            result = {
                "content": message.content if message.content else None,
                "function_call": None
            }
            
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_call = {
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                }
                result["function_call"] = function_call
            
            return result
        except Exception as e:
            logger.error(f"Error generating function call with OpenAI: {e}")
            raise
    
    def embed(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for the provided text.
        
        Args:
            text: The text or list of texts to generate embeddings for.
            **kwargs: Additional parameters to pass to the OpenAI API.
            
        Returns:
            A list of embedding vectors (lists of floats).
            
        Raises:
            Exception: If there's an error communicating with the OpenAI API.
        """
        try:
            if isinstance(text, str):
                text = [text]
                
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # Default embedding model
                input=text,
                **kwargs
            )
            
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings with OpenAI: {e}")
            raise 