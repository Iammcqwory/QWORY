#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Model Interface

This module defines the base interface for all model integrations in Qwory.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

class BaseModel(ABC):
    """
    Abstract base class for all model integrations.
    
    This class defines the interface that all model implementations must follow.
    It provides common functionality and enforces a consistent API across
    different model types and providers.
    """
    
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a model integration.
        
        Args:
            model_name: The name of the model to use.
            config: Configuration dictionary for the model.
        """
        self.model_name = model_name
        self.config = config or {}
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text based on the provided prompt.
        
        Args:
            prompt: The text prompt to generate from.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            The generated text.
        """
        pass
    
    @abstractmethod
    def generate_with_json(self, 
                          prompt: str, 
                          json_schema: Dict[str, Any],
                          **kwargs) -> Dict[str, Any]:
        """
        Generate structured JSON output based on the provided prompt and schema.
        
        Args:
            prompt: The text prompt to generate from.
            json_schema: The JSON schema that defines the expected output format.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A dictionary conforming to the provided JSON schema.
        """
        pass
    
    @abstractmethod
    def chat(self, 
            messages: List[Dict[str, str]], 
            **kwargs) -> str:
        """
        Generate a response in a chat context.
        
        Args:
            messages: A list of message dictionaries. Each message should have
                     'role' (system, user, assistant) and 'content' keys.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            The model's response text.
        """
        pass
    
    @abstractmethod
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
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A dictionary containing the response and/or function call information.
        """
        pass
    
    @abstractmethod
    def embed(self, text: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for the provided text.
        
        Args:
            text: The text or list of texts to generate embeddings for.
            **kwargs: Additional model-specific parameters.
            
        Returns:
            A list of embedding vectors (lists of floats).
        """
        pass 