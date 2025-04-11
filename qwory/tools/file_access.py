#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Access Tool for the Qwory framework.

This module provides tools for safe file operations including reading, writing, and listing files.
It implements security measures to prevent unauthorized access to system directories.
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from .base_tool import BaseTool

logger = logging.getLogger(__name__)

# Define safe paths that agents are allowed to access by default
DEFAULT_SAFE_PATHS = [
    "./data",
    "./output",
    "./temp",
    "./documents",
]

class FileAccessTool(BaseTool):
    """
    A tool for safe file operations within the Qwory framework.
    
    This tool provides methods for reading, writing, and managing files with
    built-in safety mechanisms to prevent unauthorized file access.
    """
    
    def __init__(self, safe_paths: Optional[List[str]] = None, 
                 allow_system_access: bool = False,
                 working_directory: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the FileAccessTool.
        
        Args:
            safe_paths: List of directory paths that agents can access. If None, uses default paths.
            allow_system_access: Whether to allow access to system directories (use with caution).
            working_directory: The base working directory for file operations.
            name: A unique name for this tool.
            description: A description of what this tool does.
            config: Configuration dictionary for the tool.
        """
        super().__init__(name=name, description=description, config=config)
        self.safe_paths = safe_paths or DEFAULT_SAFE_PATHS
        self.allow_system_access = allow_system_access
        self.working_directory = working_directory or os.getcwd()
        
        # Resolve all safe paths to absolute paths
        self.safe_paths = [os.path.abspath(os.path.join(self.working_directory, path)) 
                           for path in self.safe_paths]
        
        # Create any missing safe directories
        for path in self.safe_paths:
            os.makedirs(path, exist_ok=True)
        
        logger.info(f"FileAccessTool initialized with safe paths: {self.safe_paths}")
        if self.allow_system_access:
            logger.warning("System directory access is enabled. Use with caution.")
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a file operation based on the specified action.
        
        Args:
            action: The file operation to perform (read, write, list, delete, copy, move, create_dir, get_info)
            **kwargs: Arguments specific to the operation
            
        Returns:
            Dictionary containing the result of the operation
            
        Raises:
            ValueError: If the action is invalid or arguments are missing
        """
        try:
            if action == 'read':
                content = self.read_file(**kwargs)
                return {
                    "success": True,
                    "action": "read",
                    "content": content,
                    "file_path": kwargs.get("file_path")
                }
            elif action == 'write':
                success = self.write_file(**kwargs)
                return {
                    "success": success,
                    "action": "write",
                    "file_path": kwargs.get("file_path")
                }
            elif action == 'list':
                files = self.list_files(**kwargs)
                return {
                    "success": True,
                    "action": "list",
                    "files": files,
                    "directory": kwargs.get("directory")
                }
            elif action == 'delete':
                success = self.delete_file(**kwargs)
                return {
                    "success": success,
                    "action": "delete",
                    "file_path": kwargs.get("file_path")
                }
            elif action == 'copy':
                success = self.copy_file(**kwargs)
                return {
                    "success": success,
                    "action": "copy",
                    "source_path": kwargs.get("source_path"),
                    "destination_path": kwargs.get("destination_path")
                }
            elif action == 'move':
                success = self.move_file(**kwargs)
                return {
                    "success": success,
                    "action": "move",
                    "source_path": kwargs.get("source_path"),
                    "destination_path": kwargs.get("destination_path")
                }
            elif action == 'create_dir':
                success = self.create_directory(**kwargs)
                return {
                    "success": success,
                    "action": "create_dir",
                    "directory_path": kwargs.get("directory_path")
                }
            elif action == 'get_info':
                info = self.get_file_info(**kwargs)
                return {
                    "success": True,
                    "action": "get_info",
                    "info": info,
                    "file_path": kwargs.get("file_path")
                }
            else:
                raise ValueError(f"Invalid action: {action}")
        except Exception as e:
            logger.error(f"Error executing file operation {action}: {str(e)}")
            return {
                "success": False,
                "action": action,
                "error": str(e)
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for this tool's parameters.
        
        Returns:
            A dictionary containing the JSON schema for this tool's parameters.
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The file operation to perform",
                    "enum": ["read", "write", "list", "delete", "copy", "move", "create_dir", "get_info"]
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file for operations that require it"
                },
                "directory": {
                    "type": "string",
                    "description": "Directory path for list operations"
                },
                "content": {
                    "type": ["string", "object", "array"],
                    "description": "Content to write to a file"
                },
                "source_path": {
                    "type": "string",
                    "description": "Source file path for copy/move operations"
                },
                "destination_path": {
                    "type": "string",
                    "description": "Destination file path for copy/move operations"
                },
                "directory_path": {
                    "type": "string",
                    "description": "Directory path to create"
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding",
                    "default": "utf-8"
                },
                "as_json": {
                    "type": "boolean",
                    "description": "Whether to parse/write content as JSON",
                    "default": False
                },
                "append": {
                    "type": "boolean",
                    "description": "Whether to append to the file instead of overwriting",
                    "default": False
                },
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern for filtering files"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to list files recursively",
                    "default": False
                }
            },
            "required": ["action"],
            "allOf": [
                {
                    "if": {
                        "properties": {"action": {"enum": ["read", "delete", "get_info"]}}
                    },
                    "then": {
                        "required": ["file_path"]
                    }
                },
                {
                    "if": {
                        "properties": {"action": {"enum": ["write"]}}
                    },
                    "then": {
                        "required": ["file_path", "content"]
                    }
                },
                {
                    "if": {
                        "properties": {"action": {"enum": ["list"]}}
                    },
                    "then": {
                        "required": ["directory"]
                    }
                },
                {
                    "if": {
                        "properties": {"action": {"enum": ["copy", "move"]}}
                    },
                    "then": {
                        "required": ["source_path", "destination_path"]
                    }
                },
                {
                    "if": {
                        "properties": {"action": {"enum": ["create_dir"]}}
                    },
                    "then": {
                        "required": ["directory_path"]
                    }
                }
            ]
        }
    
    def _is_path_safe(self, file_path: str) -> bool:
        """
        Check if a path is safe to access.
        
        Args:
            file_path: The path to check
            
        Returns:
            True if the path is safe to access, False otherwise
        """
        if self.allow_system_access:
            return True
            
        abs_path = os.path.abspath(file_path)
        
        # Check if the path is within any of the safe paths
        for safe_path in self.safe_paths:
            if abs_path.startswith(safe_path):
                return True
                
        return False
    
    def read_file(self, file_path: str, 
                  encoding: str = 'utf-8',
                  as_json: bool = False) -> Union[str, Dict[str, Any], List[Any]]:
        """
        Read a file safely.
        
        Args:
            file_path: Path to the file to read
            encoding: File encoding (default: utf-8)
            as_json: Whether to parse the file as JSON
            
        Returns:
            File contents as string or parsed JSON object
            
        Raises:
            ValueError: If the path is not safe or file not found
        """
        if not self._is_path_safe(file_path):
            logger.warning(f"Attempted to access unsafe path: {file_path}")
            raise ValueError(f"Access to path {file_path} is not allowed for security reasons.")
            
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            if as_json:
                return json.loads(content)
            return content
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise ValueError(f"Error reading file: {str(e)}")
    
    def write_file(self, file_path: str, 
                   content: Union[str, Dict[str, Any], List[Any]],
                   encoding: str = 'utf-8',
                   as_json: bool = False,
                   append: bool = False) -> bool:
        """
        Write content to a file safely.
        
        Args:
            file_path: Path to the file to write
            content: Content to write (string or JSON-serializable object)
            encoding: File encoding (default: utf-8)
            as_json: Whether to serialize the content as JSON
            append: Whether to append to the file instead of overwriting
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If the path is not safe
        """
        if not self._is_path_safe(file_path):
            logger.warning(f"Attempted to write to unsafe path: {file_path}")
            raise ValueError(f"Access to path {file_path} is not allowed for security reasons.")
            
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        mode = 'a' if append else 'w'
        
        try:
            with open(file_path, mode, encoding=encoding) as f:
                if as_json:
                    json.dump(content, f, indent=2, ensure_ascii=False)
                else:
                    f.write(content)
            logger.info(f"Successfully {'appended to' if append else 'wrote'} file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing to file {file_path}: {str(e)}")
            raise ValueError(f"Error writing to file: {str(e)}")
    
    def list_files(self, directory: str, 
                   pattern: Optional[str] = None, 
                   recursive: bool = False) -> List[str]:
        """
        List files in a directory safely.
        
        Args:
            directory: Directory to list files from
            pattern: Optional glob pattern to filter files
            recursive: Whether to list files recursively
            
        Returns:
            List of file paths
            
        Raises:
            ValueError: If the path is not safe
        """
        if not self._is_path_safe(directory):
            logger.warning(f"Attempted to list files in unsafe path: {directory}")
            raise ValueError(f"Access to path {directory} is not allowed for security reasons.")
            
        if not os.path.exists(directory):
            logger.error(f"Directory not found: {directory}")
            raise ValueError(f"Directory not found: {directory}")
            
        try:
            path_obj = Path(directory)
            
            if recursive:
                glob_pattern = f"**/{pattern or '*'}"
            else:
                glob_pattern = pattern or "*"
                
            files = [str(p) for p in path_obj.glob(glob_pattern) if p.is_file()]
            return files
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {str(e)}")
            raise ValueError(f"Error listing files: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file safely.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If the path is not safe or file not found
        """
        if not self._is_path_safe(file_path):
            logger.warning(f"Attempted to delete unsafe path: {file_path}")
            raise ValueError(f"Access to path {file_path} is not allowed for security reasons.")
            
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Successfully deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            raise ValueError(f"Error deleting file: {str(e)}")
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copy a file safely.
        
        Args:
            source_path: Path to the source file
            destination_path: Path to the destination file
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If either path is not safe or source file not found
        """
        if not self._is_path_safe(source_path) or not self._is_path_safe(destination_path):
            logger.warning(f"Attempted unsafe file copy: {source_path} -> {destination_path}")
            raise ValueError("Source or destination path is not allowed for security reasons.")
            
        try:
            if not os.path.exists(source_path):
                logger.error(f"Source file not found: {source_path}")
                raise ValueError(f"Source file not found: {source_path}")
                
            # Ensure the directory exists
            destination_dir = os.path.dirname(destination_path)
            if destination_dir and not os.path.exists(destination_dir):
                os.makedirs(destination_dir, exist_ok=True)
                
            shutil.copy2(source_path, destination_path)
            logger.info(f"Successfully copied file: {source_path} -> {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Error copying file {source_path} to {destination_path}: {str(e)}")
            raise ValueError(f"Error copying file: {str(e)}")
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Move a file safely.
        
        Args:
            source_path: Path to the source file
            destination_path: Path to the destination file
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If either path is not safe or source file not found
        """
        if not self._is_path_safe(source_path) or not self._is_path_safe(destination_path):
            logger.warning(f"Attempted unsafe file move: {source_path} -> {destination_path}")
            raise ValueError("Source or destination path is not allowed for security reasons.")
            
        try:
            if not os.path.exists(source_path):
                logger.error(f"Source file not found: {source_path}")
                raise ValueError(f"Source file not found: {source_path}")
                
            # Ensure the directory exists
            destination_dir = os.path.dirname(destination_path)
            if destination_dir and not os.path.exists(destination_dir):
                os.makedirs(destination_dir, exist_ok=True)
                
            shutil.move(source_path, destination_path)
            logger.info(f"Successfully moved file: {source_path} -> {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Error moving file {source_path} to {destination_path}: {str(e)}")
            raise ValueError(f"Error moving file: {str(e)}")
    
    def create_directory(self, directory_path: str) -> bool:
        """
        Create a directory safely.
        
        Args:
            directory_path: Path to the directory to create
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If the path is not safe
        """
        if not self._is_path_safe(directory_path):
            logger.warning(f"Attempted to create directory in unsafe path: {directory_path}")
            raise ValueError(f"Access to path {directory_path} is not allowed for security reasons.")
            
        try:
            os.makedirs(directory_path, exist_ok=True)
            logger.info(f"Successfully created directory: {directory_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory {directory_path}: {str(e)}")
            raise ValueError(f"Error creating directory: {str(e)}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information safely.
        
        Args:
            file_path: Path to the file to get information for
            
        Returns:
            Dictionary containing file information
            
        Raises:
            ValueError: If the path is not safe or file not found
        """
        if not self._is_path_safe(file_path):
            logger.warning(f"Attempted to access unsafe path for file info: {file_path}")
            raise ValueError(f"Access to path {file_path} is not allowed for security reasons.")
            
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                raise ValueError(f"File not found: {file_path}")
                
            stats = os.stat(file_path)
            
            return {
                "path": file_path,
                "size": stats.st_size,
                "creation_time": stats.st_ctime,
                "modification_time": stats.st_mtime,
                "access_time": stats.st_atime,
                "is_directory": os.path.isdir(file_path),
                "extension": os.path.splitext(file_path)[1] if os.path.isfile(file_path) else None
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            raise ValueError(f"Error getting file info: {str(e)}") 