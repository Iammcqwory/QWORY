#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Agent Implementation

This module contains the HybridAgent class, which can dynamically switch
between single-agent and multi-agent modes based on task complexity.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HybridAgent(BaseAgent):
    """
    A hybrid agent that can dynamically switch between single-agent and multi-agent modes.
    
    This agent analyzes task complexity and automatically determines whether to handle
    the task itself (single-agent mode) or delegate to specialized sub-agents (multi-agent mode).
    """
    
    def __init__(self, model, tools=None, config=None):
        """
        Initialize a HybridAgent.
        
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
        self.mode = "hybrid"  # Can be "single", "multi", or "hybrid"
        self.sub_agents = []
        self.complexity_threshold = self.config.get("complexity_threshold", 0.7)
        self.performance_metrics = {"single_mode": [], "multi_mode": []}
        logger.info(f"HybridAgent '{self.name}' initialized with complexity threshold {self.complexity_threshold}")
    
    def add_sub_agent(self, agent: BaseAgent) -> None:
        """
        Add a sub-agent to this hybrid agent.
        
        Args:
            agent: The agent to add as a sub-agent.
        """
        self.sub_agents.append(agent)
        logger.debug(f"Sub-agent '{agent.name}' added to hybrid agent '{self.name}'")
    
    def analyze_complexity(self, input_data: Union[str, Dict[str, Any]]) -> float:
        """
        Analyze the complexity of the input data to determine the appropriate mode.
        
        Args:
            input_data: The input data to analyze.
        
        Returns:
            A complexity score between 0 and 1, where higher values indicate greater complexity.
        """
        # TODO: Implement a more sophisticated complexity analysis algorithm
        # This is a placeholder implementation
        if isinstance(input_data, str):
            # Simple heuristic: longer inputs are considered more complex
            words = input_data.split()
            complexity = min(1.0, len(words) / 100)
            logger.debug(f"Complexity analysis for text input: {complexity:.2f}")
            return complexity
        elif isinstance(input_data, dict):
            # For dictionaries, consider the number of keys and nested structures
            complexity = min(1.0, len(input_data) / 10)
            logger.debug(f"Complexity analysis for structured input: {complexity:.2f}")
            return complexity
        else:
            logger.warning(f"Unsupported input type for complexity analysis: {type(input_data)}")
            return 0.5  # Default to medium complexity
    
    def select_mode(self, input_data: Union[str, Dict[str, Any]]) -> str:
        """
        Select the appropriate mode (single or multi) based on input complexity.
        
        Args:
            input_data: The input data to process.
        
        Returns:
            The selected mode ("single" or "multi").
        """
        if self.mode != "hybrid":
            # If mode is explicitly set to single or multi, respect that setting
            logger.debug(f"Using explicitly set mode: {self.mode}")
            return self.mode
        
        complexity = self.analyze_complexity(input_data)
        selected_mode = "multi" if complexity > self.complexity_threshold else "single"
        logger.info(f"Selected mode '{selected_mode}' based on complexity {complexity:.2f}")
        return selected_mode
    
    def process_single_mode(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process input data in single-agent mode.
        
        Args:
            input_data: The input data to process.
        
        Returns:
            A dictionary containing the agent's response.
        """
        # TODO: Implement single-agent processing logic
        logger.info(f"Processing input in single-agent mode")
        
        # Placeholder implementation
        if isinstance(input_data, str):
            response = {"result": f"Processed in single-agent mode: {input_data[:50]}...", "mode": "single"}
        else:
            response = {"result": "Processed structured input in single-agent mode", "mode": "single"}
        
        return response
    
    def process_multi_mode(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process input data in multi-agent mode by delegating to sub-agents.
        
        Args:
            input_data: The input data to process.
        
        Returns:
            A dictionary containing the combined response from sub-agents.
        """
        logger.info(f"Processing input in multi-agent mode with {len(self.sub_agents)} sub-agents")
        
        if not self.sub_agents:
            logger.warning("No sub-agents available for multi-agent processing")
            return {"error": "No sub-agents available", "mode": "multi"}
        
        # Collect responses from all sub-agents
        responses = []
        for agent in self.sub_agents:
            try:
                agent_response = agent.process(input_data)
                responses.append({"agent": agent.name, "response": agent_response})
                logger.debug(f"Received response from sub-agent '{agent.name}'")
            except Exception as e:
                logger.error(f"Error processing input with sub-agent '{agent.name}': {str(e)}")
                responses.append({"agent": agent.name, "error": str(e)})
        
        # Combine responses (this is a simple aggregation, could be more sophisticated)
        combined_response = {
            "results": responses,
            "mode": "multi",
            "sub_agent_count": len(self.sub_agents)
        }
        
        return combined_response
    
    def process(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process input data and generate a response, automatically selecting the appropriate mode.
        
        Args:
            input_data: The input data to process.
        
        Returns:
            A dictionary containing the agent's response.
        """
        mode = self.select_mode(input_data)
        
        if mode == "single":
            response = self.process_single_mode(input_data)
        else:  # mode == "multi"
            response = self.process_multi_mode(input_data)
        
        # Record performance metrics for future mode selection optimization
        # TODO: Implement more sophisticated performance tracking
        
        return response
    
    def set_mode(self, mode: str) -> None:
        """
        Explicitly set the agent's mode.
        
        Args:
            mode: The mode to set ("single", "multi", or "hybrid").
        """
        if mode not in ["single", "multi", "hybrid"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'single', 'multi', or 'hybrid'.")
        
        self.mode = mode
        logger.info(f"Mode for agent '{self.name}' explicitly set to '{mode}'")
    
    def update_complexity_threshold(self, threshold: float) -> None:
        """
        Update the complexity threshold used for mode selection.
        
        Args:
            threshold: The new complexity threshold (between 0 and 1).
        """
        if not 0 <= threshold <= 1:
            raise ValueError(f"Invalid complexity threshold: {threshold}. Must be between 0 and 1.")
        
        self.complexity_threshold = threshold
        logger.info(f"Complexity threshold for agent '{self.name}' updated to {threshold}")