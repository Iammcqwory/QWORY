#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Tool Implementation

This module contains the BaseTool class, which serves as the foundation
for all tool implementations in the Qwory framework.
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Union
import time
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Abstract base class for all tools in the Qwory framework.
    
    This class defines the interface that all tool implementations must follow.
    It provides common functionality and enforces a consistent API across
    different tool types.
    """
    
    def __init__(self, name: Optional[str] = None, description: Optional[str] = None, 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new tool instance.
        
        Args:
            name: A unique name for this tool. If None, a name will be generated based on the class name.
            description: A description of what this tool does.
            config: Configuration dictionary for the tool.
        """
        self.id = str(uuid.uuid4())
        self.name = name or self.__class__.__name__.lower()
        self.description = description or "No description provided."
        self.config = config or {}
        self.execution_history = []
        logger.debug(f"Tool '{self.name}' initialized with ID {self.id}")
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the given arguments.
        
        This is the main method that should be implemented by all tool subclasses.
        It takes any number of positional and keyword arguments and returns a
        dictionary containing the result of the tool execution.
        
        Args:
            *args: Positional arguments for the tool execution.
            **kwargs: Keyword arguments for the tool execution.
        
        Returns:
            A dictionary containing the result of the tool execution and any additional information.
        """
        pass
    
    def validate_args(self, *args, **kwargs) -> bool:
        """
        Validate the arguments for the tool execution.
        
        This method should be overridden by subclasses to provide specific validation
        for their arguments. The default implementation always returns True.
        
        Args:
            *args: Positional arguments to validate.
            **kwargs: Keyword arguments to validate.
        
        Returns:
            True if the arguments are valid, False otherwise.
        """
        return True
    
    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the given arguments.
        
        This method provides a convenient way to execute the tool by calling the
        instance directly. It validates the arguments, executes the tool, and
        records the execution in the history.
        
        Args:
            *args: Positional arguments for the tool execution.
            **kwargs: Keyword arguments for the tool execution.
        
        Returns:
            A dictionary containing the result of the tool execution and any additional information.
        """
        # Validate arguments
        if not self.validate_args(*args, **kwargs):
            error_msg = f"Invalid arguments for tool '{self.name}'"
            logger.error(error_msg)
            return {"error": error_msg, "status": "failed"}
        
        # Record execution start
        execution_record = {
            "id": str(uuid.uuid4()),
            "tool_id": self.id,
            "tool_name": self.name,
            "args": args,
            "kwargs": kwargs,
            "started_at": time.time(),
            "status": "in_progress"
        }
        
        try:
            # Execute the tool
            logger.info(f"Executing tool '{self.name}'")
            result = self.execute(*args, **kwargs)
            
            # Update execution record
            execution_record["completed_at"] = time.time()
            execution_record["duration"] = execution_record["completed_at"] - execution_record["started_at"]
            execution_record["status"] = "completed"
            execution_record["result"] = result
            
            logger.info(f"Tool '{self.name}' executed successfully in {execution_record['duration']:.2f} seconds")
            
        except Exception as e:
            # Handle execution error
            error_msg = f"Error executing tool '{self.name}': {str(e)}"
            logger.error(error_msg)
            
            # Update execution record
            execution_record["completed_at"] = time.time()
            execution_record["duration"] = execution_record["completed_at"] - execution_record["started_at"]
            execution_record["status"] = "failed"
            execution_record["error"] = str(e)
            
            result = {"error": error_msg, "status": "failed"}
        
        # Add execution record to history
        self.execution_history.append(execution_record)
        
        return result
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get the execution history for this tool.
        
        Returns:
            A list of execution records.
        """
        return self.execution_history
    
    def clear_execution_history(self) -> None:
        """
        Clear the execution history for this tool.
        """
        count = len(self.execution_history)
        self.execution_history = []
        logger.debug(f"Cleared {count} execution records from tool '{self.name}'")
    
    def __str__(self) -> str:
        """
        Return a string representation of the tool.
        
        Returns:
            A string representation of the tool.
        """
        return f"{self.__class__.__name__}(name='{self.name}', id='{self.id}')"
    
    def __repr__(self) -> str:
        """
        Return a string representation of the tool.
        
        Returns:
            A string representation of the tool.
        """
        return self.__str__()