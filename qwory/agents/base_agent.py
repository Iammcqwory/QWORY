#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Agent Implementation

This module contains the BaseAgent class, which serves as the foundation
for all agent implementations in the Qwory framework.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Qwory framework.
    
    This class defines the interface that all agent implementations must follow.
    It provides common functionality and enforces a consistent API across
    different agent types.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, name: Optional[str] = None):
        """
        Initialize a new agent.
        
        Args:
            config: Configuration dictionary for the agent.
            name: A unique name for this agent instance. If None, a UUID will be generated.
        """
        self.config = config or {}
        self.name = name or f"agent-{str(uuid.uuid4())[:8]}"
        self.tools = {}
        self.memory = {"short_term": [], "long_term": []}
        self.state = "initialized"
        
        logger.info(f"Initialized agent: {self.name}")
    
    @abstractmethod
    def process(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process input data and generate a response.
        
        This is the main method that should be implemented by all agent subclasses.
        It takes input data (which could be a string or a structured dictionary)
        and returns a response dictionary.
        
        Args:
            input_data: The input data to process. This could be a string (e.g., a user query)
                       or a structured dictionary containing multiple fields.
        
        Returns:
            A dictionary containing the agent's response and any additional information.
        """
        pass
    
    def add_tool(self, tool: Any) -> None:
        """
        Add a tool to the agent's toolkit.
        
        Args:
            tool: The tool to add.
        """
        self.tools.append(tool)
        logger.debug(f"Tool '{tool.__class__.__name__}' added to agent '{self.name}'")
    
    def add_to_memory(self, item: Any, memory_type: str = "short_term") -> None:
        """
        Add an item to the agent's memory.
        
        Args:
            item: The item to add to memory.
            memory_type: The type of memory to add the item to ("short_term" or "long_term").
        """
        if memory_type not in ["short_term", "long_term"]:
            raise ValueError(f"Invalid memory type: {memory_type}. Must be 'short_term' or 'long_term'.")
        
        self.memory[memory_type].append(item)
        logger.debug(f"Item added to {memory_type} memory of agent '{self.name}'")
    
    def get_from_memory(self, memory_type: str = "short_term") -> List[Any]:
        """
        Retrieve items from the agent's memory.
        
        Args:
            memory_type: The type of memory to retrieve items from ("short_term" or "long_term").
        
        Returns:
            A list of items from the specified memory type.
        """
        if memory_type not in ["short_term", "long_term"]:
            raise ValueError(f"Invalid memory type: {memory_type}. Must be 'short_term' or 'long_term'.")
        
        return self.memory[memory_type]
    
    def clear_memory(self, memory_type: Optional[str] = None) -> None:
        """
        Clear the agent's memory.
        
        Args:
            memory_type: The type of memory to clear. If None, all memory types will be cleared.
        """
        if memory_type is None:
            self.memory = {"short_term": [], "long_term": []}
            logger.debug(f"All memory cleared for agent '{self.name}'")
        elif memory_type in ["short_term", "long_term"]:
            self.memory[memory_type] = []
            logger.debug(f"{memory_type.capitalize()} memory cleared for agent '{self.name}'")
        else:
            raise ValueError(f"Invalid memory type: {memory_type}. Must be 'short_term' or 'long_term'.")
    
    def __str__(self) -> str:
        """
        Return a string representation of the agent.
        
        Returns:
            A string representation of the agent.
        """
        return f"{self.__class__.__name__}(name='{self.name}', id='{self.id}')"
    
    def __repr__(self) -> str:
        """
        Return a string representation of the agent.
        
        Returns:
            A string representation of the agent.
        """
        return self.__str__()