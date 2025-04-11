#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Orchestrator Implementation

This module contains the AgentOrchestrator class, which is responsible for
coordinating agents and managing task execution in the Qwory framework.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from ..agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the execution of tasks by coordinating multiple agents.
    
    The AgentOrchestrator is responsible for:
    - Managing the lifecycle of agents
    - Routing tasks to appropriate agents
    - Handling inter-agent communication
    - Monitoring and reporting on task execution
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new orchestrator instance.
        
        Args:
            config: Configuration dictionary for the orchestrator.
        """
        self.config = config or {}
        self.agents = {}
        self.tasks = []
        self.execution_history = []
        self.start_time = time.time()
        logger.info("AgentOrchestrator initialized")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: The agent to register.
        """
        if agent.id in self.agents:
            logger.warning(f"Agent with ID {agent.id} already registered, replacing")
        
        self.agents[agent.id] = agent
        logger.info(f"Agent '{agent.name}' registered with orchestrator")
    
    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the orchestrator.
        
        Args:
            agent_id: The ID of the agent to unregister.
        """
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            logger.info(f"Agent '{agent.name}' unregistered from orchestrator")
        else:
            logger.warning(f"No agent with ID {agent_id} registered")
    
    def add_task(self, task: Dict[str, Any]) -> str:
        """
        Add a task to the orchestrator's task queue.
        
        Args:
            task: The task to add.
        
        Returns:
            The ID of the added task.
        """
        task_id = task.get("id", f"task-{len(self.tasks)}")
        task["id"] = task_id
        task["status"] = "pending"
        task["created_at"] = time.time()
        
        self.tasks.append(task)
        logger.info(f"Task '{task_id}' added to orchestrator")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task by its ID.
        
        Args:
            task_id: The ID of the task to get.
        
        Returns:
            The task, or None if no task with the given ID exists.
        """
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def execute_task(self, task_id: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using the specified agent or an automatically selected one.
        
        Args:
            task_id: The ID of the task to execute.
            agent_id: The ID of the agent to use. If None, an agent will be selected automatically.
        
        Returns:
            The result of the task execution.
        """
        task = self.get_task(task_id)
        if not task:
            error_msg = f"No task with ID {task_id} found"
            logger.error(error_msg)
            return {"error": error_msg}
        
        if task["status"] != "pending":
            logger.warning(f"Task '{task_id}' is not pending (status: {task['status']})")
        
        # Update task status
        task["status"] = "in_progress"
        task["started_at"] = time.time()
        
        # Select agent
        if agent_id:
            if agent_id not in self.agents:
                error_msg = f"No agent with ID {agent_id} registered"
                logger.error(error_msg)
                task["status"] = "failed"
                task["error"] = error_msg
                return {"error": error_msg}
            agent = self.agents[agent_id]
        else:
            # Simple agent selection strategy (could be more sophisticated)
            if not self.agents:
                error_msg = "No agents registered with orchestrator"
                logger.error(error_msg)
                task["status"] = "failed"
                task["error"] = error_msg
                return {"error": error_msg}
            agent = list(self.agents.values())[0]
        
        logger.info(f"Executing task '{task_id}' with agent '{agent.name}'")
        
        try:
            # Execute task
            result = agent.process(task["input"])
            
            # Update task status
            task["status"] = "completed"
            task["completed_at"] = time.time()
            task["result"] = result
            
            # Record execution in history
            execution_record = {
                "task_id": task_id,
                "agent_id": agent.id,
                "agent_name": agent.name,
                "started_at": task["started_at"],
                "completed_at": task["completed_at"],
                "duration": task["completed_at"] - task["started_at"],
                "success": True
            }
            self.execution_history.append(execution_record)
            
            logger.info(f"Task '{task_id}' completed successfully")
            return result
        
        except Exception as e:
            # Handle execution error
            error_msg = f"Error executing task '{task_id}': {str(e)}"
            logger.error(error_msg)
            
            # Update task status
            task["status"] = "failed"
            task["error"] = str(e)
            task["completed_at"] = time.time()
            
            # Record execution in history
            execution_record = {
                "task_id": task_id,
                "agent_id": agent.id,
                "agent_name": agent.name,
                "started_at": task["started_at"],
                "completed_at": task["completed_at"],
                "duration": task["completed_at"] - task["started_at"],
                "success": False,
                "error": str(e)
            }
            self.execution_history.append(execution_record)
            
            return {"error": error_msg}
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get the execution history.
        
        Returns:
            The execution history.
        """
        return self.execution_history
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the orchestrator.
        
        Returns:
            A dictionary containing the status of the orchestrator.
        """
        pending_tasks = sum(1 for task in self.tasks if task["status"] == "pending")
        in_progress_tasks = sum(1 for task in self.tasks if task["status"] == "in_progress")
        completed_tasks = sum(1 for task in self.tasks if task["status"] == "completed")
        failed_tasks = sum(1 for task in self.tasks if task["status"] == "failed")
        
        return {
            "uptime": time.time() - self.start_time,
            "agent_count": len(self.agents),
            "task_count": len(self.tasks),
            "task_status": {
                "pending": pending_tasks,
                "in_progress": in_progress_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks
            },
            "execution_history_count": len(self.execution_history)
        }