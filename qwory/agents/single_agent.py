#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single Agent Implementation

This module contains the SingleAgent class, a concrete implementation
of the BaseAgent that uses a single model for all operations.
"""

import logging
from typing import Any, Dict, List, Optional, Union
import json

from .base_agent import BaseAgent
from ..models.base_model import BaseModel
from ..models.openai_model import OpenAIModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SingleAgent(BaseAgent):
    """
    A concrete implementation of BaseAgent that uses a single model.
    
    This agent uses a single model (by default OpenAI) to perform all operations.
    It supports basic task processing, memory management, and tool usage.
    """
    
    def __init__(self, model, tools=None, config=None):
        """
        Initialize a SingleAgent.
        
        Args:
            model: The LLM model to use for this agent.
            tools: List of tools available to this agent.
            config: Configuration dictionary.
        """
        super().__init__(config)
        self.model = model
        self.tools = {}
        
        # Add any provided tools
        if tools:
            for tool in tools:
                self.add_tool(tool)
        
        # Initialize the model if not provided
        self.model = model or OpenAIModel(
            model_name=config.get("model_name", "gpt-4o"),
            api_key=config.get("api_key", None),
        )
        
        # Set up system prompt
        self.system_prompt = config.get("system_prompt", (
            "You are a helpful AI assistant that helps users accomplish tasks. "
            "You have access to various tools and can use them to help the user. "
            "Always think step by step and explain your reasoning."
        ))
        
        logger.info(f"SingleAgent '{self.name}' initialized with model {self.model.model_name}")
    
    def process(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process input data and generate a response.
        
        Args:
            input_data: The input data to process. This could be a string (e.g., a user query)
                       or a structured dictionary containing multiple fields.
        
        Returns:
            A dictionary containing the agent's response and any additional information.
        """
        logger.info(f"Processing input for agent '{self.name}'")
        
        # Convert input to string if it's a dictionary
        if isinstance(input_data, dict):
            if "query" in input_data:
                query = input_data["query"]
            else:
                query = json.dumps(input_data)
        else:
            query = input_data
        
        # Add to short-term memory
        self.add_to_memory({"role": "user", "content": query})
        
        # Prepare messages for the model
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add memory context (last 10 interactions)
        short_term_memory = self.get_from_memory("short_term")[-10:]
        messages.extend(short_term_memory)
        
        # Generate response
        try:
            if self.tools and len(self.tools) > 0:
                # If we have tools, use function calling
                functions = [self._convert_tool_to_function(tool) for tool in self.tools]
                response_dict = self.model.chat_with_functions(
                    messages=messages,
                    functions=functions
                )
                
                # Process function call if present
                if response_dict["function_call"]:
                    function_call = response_dict["function_call"]
                    tool_name = function_call["name"]
                    args = function_call["arguments"]
                    
                    # Find the tool and execute it
                    for tool in self.tools:
                        if tool.__class__.__name__ == tool_name:
                            try:
                                tool_result = tool.execute(**args)
                                
                                # Add the function call and result to memory
                                self.add_to_memory({
                                    "role": "assistant",
                                    "content": None,
                                    "function_call": {
                                        "name": tool_name,
                                        "arguments": json.dumps(args)
                                    }
                                })
                                
                                self.add_to_memory({
                                    "role": "function",
                                    "name": tool_name,
                                    "content": json.dumps(tool_result)
                                })
                                
                                # Generate a new response incorporating the function result
                                messages.extend([
                                    {
                                        "role": "assistant",
                                        "content": None,
                                        "function_call": {
                                            "name": tool_name,
                                            "arguments": json.dumps(args)
                                        }
                                    },
                                    {
                                        "role": "function",
                                        "name": tool_name,
                                        "content": json.dumps(tool_result)
                                    }
                                ])
                                
                                # Get the final response
                                final_response = self.model.chat(messages=messages)
                                self.add_to_memory({"role": "assistant", "content": final_response})
                                
                                return {
                                    "response": final_response,
                                    "tool_used": tool_name,
                                    "tool_result": tool_result
                                }
                            except Exception as e:
                                logger.error(f"Error executing tool {tool_name}: {e}")
                                error_message = f"Error executing tool {tool_name}: {str(e)}"
                                self.add_to_memory({"role": "system", "content": error_message})
                                return {"response": error_message, "error": str(e)}
                
                # If no function call or no matching tool, just return the response
                response = response_dict["content"] or "I don't know how to respond to that."
                self.add_to_memory({"role": "assistant", "content": response})
                return {"response": response}
            else:
                # No tools, just generate a simple response
                response = self.model.chat(messages=messages)
                self.add_to_memory({"role": "assistant", "content": response})
                return {"response": response}
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return {"response": f"An error occurred: {str(e)}", "error": str(e)}
    
    def _convert_tool_to_function(self, tool: Any) -> Dict[str, Any]:
        """
        Convert a tool to a function definition for the model.
        
        Args:
            tool: The tool to convert.
            
        Returns:
            A function definition dictionary.
        """
        return {
            "name": tool.__class__.__name__,
            "description": tool.__doc__ or f"Execute the {tool.__class__.__name__} tool",
            "parameters": tool.get_schema() if hasattr(tool, "get_schema") else {"type": "object", "properties": {}}
        } 