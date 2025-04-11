#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Model Integration

This module implements integration with Google's Gemini AI models.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
import os

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

from .base_model import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeminiModel(BaseModel):
    """
    Integration with Google's Gemini models.
    
    This class implements the BaseModel interface for Gemini models like
    Gemini Pro, Gemini Ultra, etc.
    """
    
    def __init__(self, 
                model_name: str = "gemini-pro", 
                api_key: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Gemini model integration.
        
        Args:
            model_name: The name of the model to use (e.g., "gemini-pro", "gemini-ultra").
            api_key: The Google API key. If None, it will be loaded from the GOOGLE_API_KEY
                    environment variable.
            config: Additional configuration parameters.
        
        Raises:
            ImportError: If the google.generativeai package is not installed.
            ValueError: If the API key is not provided and not found in the environment.
        """
        super().__init__(model_name, config)
        
        if not HAS_GEMINI:
            raise ImportError(
                "The 'google-generativeai' package is required for Gemini model integration. "
                "Please install it using 'pip install google-generativeai'."
            )
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key is required. Please provide it as an argument or "
                "set the GOOGLE_API_KEY environment variable."
            )
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Model configuration
        self.generation_config = {
            "temperature": config.get("temperature", 0.7),
            "top_p": config.get("top_p", 0.8),
            "top_k": config.get("top_k", 40),
            "max_output_tokens": config.get("max_tokens", 1024),
        }
        
        # Safety settings (default to medium)
        safety_settings = config.get("safety_settings", None)
        self.safety_settings = safety_settings
        
        logger.info(f"Gemini model {model_name} initialized")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on the provided prompt using a Gemini model.
        
        Args:
            prompt: The text prompt to generate from.
            **kwargs: Additional parameters to pass to the Gemini API.
            
        Returns:
            The generated text.
            
        Raises:
            Exception: If there's an error communicating with the Gemini API.
        """
        try:
            # Create a generative model instance
            model = genai.GenerativeModel(model_name=self.model_name)
            
            # Update generation config with any kwargs
            generation_config = {**self.generation_config, **kwargs}
            
            # Generate the response
            response = model.generate_content(
                contents=prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
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
            **kwargs: Additional parameters to pass to the Gemini API.
            
        Returns:
            A dictionary conforming to the provided JSON schema.
            
        Raises:
            Exception: If there's an error communicating with the Gemini API or
                      parsing the generated JSON.
        """
        try:
            # Create prompt that includes the JSON schema
            system_prompt = f"You must respond with valid JSON that conforms to this schema: {json.dumps(json_schema)}"
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Create a generative model instance
            model = genai.GenerativeModel(model_name=self.model_name)
            
            # Update generation config with any kwargs
            generation_config = {**self.generation_config, **kwargs}
            
            # Generate the response
            response = model.generate_content(
                contents=full_prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )
            
            # Extract JSON from text
            result_text = response.text.strip()
            
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
            logger.error(f"Error generating JSON with Gemini: {e}")
            raise
    
    def chat(self, 
            messages: List[Dict[str, str]], 
            **kwargs) -> str:
        """
        Generate a response in a chat context.
        
        Args:
            messages: A list of message dictionaries. Each message should have
                     'role' (system, user, assistant) and 'content' keys.
            **kwargs: Additional parameters to pass to the Gemini API.
            
        Returns:
            The model's response text.
            
        Raises:
            Exception: If there's an error communicating with the Gemini API.
        """
        try:
            # Create a chat model instance
            model = genai.GenerativeModel(model_name=self.model_name)
            
            # Update generation config with any kwargs
            generation_config = {**self.generation_config, **kwargs}
            
            # Convert OpenAI-style messages to Gemini chat format
            chat = model.start_chat(history=[])
            
            # Process system message if it exists and combine with first user message
            has_system = False
            system_content = ""
            
            if messages and messages[0]["role"] == "system":
                has_system = True
                system_content = messages[0]["content"]
            
            # Add messages to chat
            for i, message in enumerate(messages):
                # Skip system message as it's handled separately
                if i == 0 and message["role"] == "system":
                    continue
                    
                # For the first user message after a system message, combine them
                if has_system and i == 1 and message["role"] == "user":
                    content = f"{system_content}\n\n{message['content']}"
                    chat.send_message(content, generation_config=generation_config)
                    continue
                
                if message["role"] == "user":
                    chat.send_message(message["content"], generation_config=generation_config)
                elif message["role"] == "assistant":
                    # Add assistant messages to the history
                    chat._history.append({"role": "model", "parts": [message["content"]]})
            
            # Generate response based on chat history
            response = chat.send_message("", generation_config=generation_config)
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating chat response with Gemini: {e}")
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
            **kwargs: Additional parameters to pass to the Gemini API.
            
        Returns:
            A dictionary containing the response and/or function call information.
            
        Raises:
            Exception: If there's an error communicating with the Gemini API.
        """
        try:
            # Gemini doesn't directly support function calling like OpenAI,
            # so we'll implement a workaround by formatting the functions in the prompt
            
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
            
            # Check if the response contains a function call
            function_call = None
            
            # Extract function call from the response if it exists
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
            logger.error(f"Error generating function call with Gemini: {e}")
            raise
    
    def embed(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for the provided text.
        
        Args:
            text: The text or list of texts to generate embeddings for.
            **kwargs: Additional parameters to pass to the Gemini API.
            
        Returns:
            A list of embedding vectors (lists of floats).
            
        Raises:
            Exception: If there's an error communicating with the Gemini API.
        """
        try:
            if isinstance(text, str):
                text = [text]
            
            # Gemini's embedding model name
            embedding_model = "models/embedding-001"
            
            # Generate embeddings for each text
            embeddings = []
            for t in text:
                result = genai.embed_content(
                    model=embedding_model,
                    content=t,
                    task_type="semantic_similarity",
                    **kwargs
                )
                embeddings.append(result["embedding"])
            
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings with Gemini: {e}")
            raise 