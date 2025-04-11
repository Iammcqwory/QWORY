#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwory: Quantum Web Orchestration Research Yield
An open-source AI agent framework designed to revolutionize task automation.

This is the main entry point for the Qwory framework.
"""

import argparse
import sys
import os
import json
from typing import List, Optional

from qwory.agents import SingleAgent, HybridAgent
from qwory.tools import SearchTool, FileAccessTool
from qwory.models.openai_model import OpenAIModel
from qwory.models.gemini_model import GeminiModel
from qwory.models.openrouter_model import OpenRouterModel

__version__ = "0.1.0"


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Command line arguments. If None, sys.argv[1:] is used.
        
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Qwory: Quantum Web Orchestration Research Yield - AI agent framework",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Qwory {__version__}"
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a Qwory agent")
    run_parser.add_argument(
        "-m", "--mode",
        choices=["single", "multi", "hybrid"],
        default="hybrid",
        help="Agent operation mode"
    )
    run_parser.add_argument(
        "-t", "--task",
        required=True,
        help="Task description for the agent"
    )
    run_parser.add_argument(
        "--provider",
        choices=["openai", "gemini", "openrouter"],
        default="openai",
        help="AI provider to use"
    )
    run_parser.add_argument(
        "--model",
        default=None,
        help="Model to use (provider-specific, defaults to appropriate model for the chosen provider)"
    )
    run_parser.add_argument(
        "--openrouter-model-type",
        choices=["deepseek", "ollama", "mistral", "claude", "mixtral", "yi"],
        default="deepseek",
        help="When using OpenRouter, specify the model type to use"
    )
    run_parser.add_argument(
        "--api-key",
        default=None,
        help="API key for the model provider. If not provided, will look for environment variables."
    )
    run_parser.add_argument(
        "--enable-file-access",
        action="store_true",
        help="Enable local file system access for agents (use with caution)"
    )
    run_parser.add_argument(
        "--file-access-path",
        default="./data",
        help="Base path for file operations when file access is enabled"
    )
    
    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Start interactive mode")
    interactive_parser.add_argument(
        "-m", "--mode",
        choices=["single", "multi", "hybrid"],
        default="hybrid",
        help="Agent operation mode"
    )
    interactive_parser.add_argument(
        "--provider",
        choices=["openai", "gemini", "openrouter"],
        default="openai",
        help="AI provider to use"
    )
    interactive_parser.add_argument(
        "--model",
        default=None,
        help="Model to use (provider-specific, defaults to appropriate model for the chosen provider)"
    )
    interactive_parser.add_argument(
        "--openrouter-model-type",
        choices=["deepseek", "ollama", "mistral", "claude", "mixtral", "yi"],
        default="deepseek",
        help="When using OpenRouter, specify the model type to use"
    )
    interactive_parser.add_argument(
        "--api-key",
        default=None,
        help="API key for the model provider. If not provided, will look for environment variables."
    )
    interactive_parser.add_argument(
        "--enable-file-access",
        action="store_true",
        help="Enable local file system access for agents (use with caution)"
    )
    interactive_parser.add_argument(
        "--file-access-path",
        default="./data",
        help="Base path for file operations when file access is enabled"
    )
    
    # List models command (for OpenRouter)
    list_models_parser = subparsers.add_parser("list-models", help="List available models from a provider")
    list_models_parser.add_argument(
        "--provider",
        choices=["openrouter"],
        default="openrouter",
        help="Provider to list models from"
    )
    list_models_parser.add_argument(
        "--api-key",
        default=None,
        help="API key for the provider. If not provided, will look for environment variables."
    )
    
    return parser.parse_args(args)


def get_model(provider: str, model_name: Optional[str] = None, model_type: Optional[str] = None, api_key: Optional[str] = None):
    """
    Get the appropriate model based on the specified provider.
    
    Args:
        provider: The AI provider ("openai", "gemini", or "openrouter").
        model_name: The model to use. If None, a default model will be used.
        model_type: When using OpenRouter, the type of model to use (deepseek, ollama, etc.).
        api_key: API key for the model provider. If None, will look for environment variables.
        
    Returns:
        A model instance.
        
    Raises:
        ValueError: If an unsupported provider is specified.
    """
    if provider == "openai":
        default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        return OpenAIModel(
            model_name=model_name or default_model,
            api_key=api_key
        )
    elif provider == "gemini":
        default_model = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-pro")
        return GeminiModel(
            model_name=model_name or default_model,
            api_key=api_key
        )
    elif provider == "openrouter":
        # If model_name is provided directly, use it
        if model_name:
            return OpenRouterModel(
                model_name=model_name,
                api_key=api_key
            )
        
        # Otherwise, use the model type to determine the model
        if model_type:
            default_model = OpenRouterModel.DEFAULT_MODELS.get(
                model_type, 
                os.getenv("DEFAULT_OPENROUTER_MODEL", "deepseek/deepseek-chat")
            )
            return OpenRouterModel(
                model_name=default_model,
                api_key=api_key
            )
        
        # If no model_name or model_type, use the default from environment or fall back to deepseek
        default_model = os.getenv("DEFAULT_OPENROUTER_MODEL", "deepseek/deepseek-chat")
        return OpenRouterModel(
            model_name=default_model,
            api_key=api_key
        )
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


def get_agent(mode: str, provider: str, model_name: Optional[str] = None, model_type: Optional[str] = None, api_key: Optional[str] = None, 
              enable_file_access: bool = False, file_access_path: str = "./data"):
    """
    Get the appropriate agent based on the specified mode.
    
    Args:
        mode: The agent mode ("single", "multi", or "hybrid").
        provider: The AI provider to use.
        model_name: The model to use. If None, a default model will be used.
        model_type: When using OpenRouter, the type of model to use.
        api_key: API key for the model provider. If None, will look for environment variables.
        enable_file_access: Whether to enable local file system access for agents.
        file_access_path: Base path for file operations when file access is enabled.
        
    Returns:
        An agent instance.
        
    Raises:
        ValueError: If an unsupported mode is specified.
    """
    # Get the appropriate model
    model = get_model(provider, model_name, model_type, api_key)
    
    # Set up tools
    tools = [SearchTool()]
    
    # Add file access tool if enabled
    if enable_file_access:
        # Create safe paths based on the specified file access path
        safe_paths = [
            file_access_path,
            os.path.join(file_access_path, "documents"),
            os.path.join(file_access_path, "output"),
            os.path.join(file_access_path, "temp")
        ]
        
        # Add file access tool to the list of tools
        file_tool = FileAccessTool(safe_paths=safe_paths)
        tools.append(file_tool)
        print(f"File access enabled with safe paths: {safe_paths}")
    
    if mode == "single":
        return SingleAgent(model=model, tools=tools)
    elif mode == "hybrid":
        return HybridAgent(model=model, tools=tools)
    else:
        raise ValueError(f"Unsupported agent mode: {mode}")


def run_agent(args: argparse.Namespace):
    """
    Run an agent with the specified arguments.
    
    Args:
        args: Command line arguments.
    """
    # Get the agent
    agent = get_agent(
        mode=args.mode,
        provider=args.provider,
        model_name=args.model,
        model_type=args.openrouter_model_type if args.provider == "openrouter" else None,
        api_key=args.api_key,
        enable_file_access=args.enable_file_access,
        file_access_path=args.file_access_path
    )
    
    # Run the agent with the task
    result = agent.run(args.task)
    
    # Print the result
    print(f"\nAgent result: {result}")


def interactive_mode(args: argparse.Namespace):
    """
    Start interactive mode with the specified arguments.
    
    Args:
        args: Command line arguments.
    """
    # Get the agent
    agent = get_agent(
        mode=args.mode,
        provider=args.provider,
        model_name=args.model,
        model_type=args.openrouter_model_type if args.provider == "openrouter" else None,
        api_key=args.api_key,
        enable_file_access=args.enable_file_access,
        file_access_path=args.file_access_path
    )
    
    print(f"Starting Qwory interactive mode with {args.provider} provider")
    
    # Define formatting constants
    USER_PREFIX = "🧑 "
    AGENT_PREFIX = "🤖 "
    
    try:
        while True:
            # Get user input
            user_input = input(f"\n{USER_PREFIX}")
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting interactive mode.")
                break
            
            # Process the user input with the agent
            result = agent.run(user_input)
            
            # Print the result
            print(f"\n{AGENT_PREFIX}{result}")
    
    except KeyboardInterrupt:
        print("\nExiting interactive mode.")
    except Exception as e:
        print(f"Error in interactive mode: {e}")


def list_models(args: argparse.Namespace):
    """
    List available models from a provider.
    
    Args:
        args: Command line arguments.
    """
    if args.provider == "openrouter":
        model = OpenRouterModel(api_key=args.api_key)
        
        try:
            # Get available models
            available_models = model.get_available_models()
            
            # Print the available models
            print("\nAvailable models on OpenRouter:")
            print("-" * 80)
            
            for model_info in available_models:
                model_id = model_info.get("id", "Unknown")
                context_length = model_info.get("context_length", "Unknown")
                pricing = model_info.get("pricing", {})
                
                input_price = pricing.get("input", 0) * 1000000  # Convert to per million tokens
                output_price = pricing.get("output", 0) * 1000000  # Convert to per million tokens
                
                print(f"ID: {model_id}")
                print(f"Context Length: {context_length}")
                print(f"Pricing: ${input_price:.4f} per million input tokens, ${output_price:.4f} per million output tokens")
                print("-" * 80)
                
        except Exception as e:
            print(f"Error listing models: {e}")
    else:
        print(f"Listing models not supported for provider: {args.provider}")


def main(args: Optional[List[str]] = None):
    """
    Main entry point for the Qwory framework.
    
    Args:
        args: Command line arguments. If None, sys.argv[1:] is used.
    """
    # Parse arguments
    parsed_args = parse_arguments(args)
    
    # Load environment variables from .env file if it exists
    if os.path.exists(".env"):
        from dotenv import load_dotenv
        load_dotenv()
    
    # Handle different commands
    if parsed_args.command == "run":
        run_agent(parsed_args)
    elif parsed_args.command == "interactive":
        interactive_mode(parsed_args)
    elif parsed_args.command == "list-models":
        list_models(parsed_args)
    else:
        print("No command specified. Use 'run', 'interactive', or 'list-models'.")
        sys.exit(1)


if __name__ == "__main__":
    main()