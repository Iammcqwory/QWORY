#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the FileAccessTool.

This script demonstrates and verifies the functionality of the FileAccessTool.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to sys.path to import the qwory package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qwory.tools.file_access import FileAccessTool

def main():
    """Test the FileAccessTool functionality."""
    print("Testing FileAccessTool...")
    
    # Create a test directory structure
    test_dir = Path("./test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Initialize the tool with our test directory
    file_tool = FileAccessTool(safe_paths=["./test_data"])
    
    print(f"Safe paths: {file_tool.safe_paths}")
    
    # Test writing a file
    test_content = "This is a test file.\nIt has multiple lines.\n"
    test_file_path = "./test_data/test_file.txt"
    
    print(f"Writing text file to {test_file_path}...")
    file_tool.write_file(test_file_path, test_content)
    
    # Test reading the file
    print(f"Reading from {test_file_path}...")
    content = file_tool.read_file(test_file_path)
    print(f"Content: {content}")
    
    # Test writing JSON
    test_json = {
        "name": "Test JSON",
        "values": [1, 2, 3, 4, 5],
        "nested": {
            "key": "value"
        }
    }
    json_file_path = "./test_data/test_file.json"
    
    print(f"Writing JSON file to {json_file_path}...")
    file_tool.write_file(json_file_path, test_json, as_json=True)
    
    # Test reading JSON
    print(f"Reading JSON from {json_file_path}...")
    json_content = file_tool.read_file(json_file_path, as_json=True)
    print(f"JSON content: {json_content}")
    
    # Test listing files
    print("Listing files in test directory...")
    files = file_tool.list_files("./test_data")
    print(f"Files: {files}")
    
    # Test creating a subdirectory
    subdir_path = "./test_data/subdir"
    print(f"Creating subdirectory: {subdir_path}...")
    file_tool.create_directory(subdir_path)
    
    # Test writing a file in the subdirectory
    subdir_file_path = "./test_data/subdir/test_file.txt"
    print(f"Writing file in subdirectory: {subdir_file_path}...")
    file_tool.write_file(subdir_file_path, "This is a file in the subdirectory.")
    
    # Test listing files recursively
    print("Listing all files recursively...")
    all_files = file_tool.list_files("./test_data", recursive=True)
    print(f"All files: {all_files}")
    
    # Test copying a file
    copy_path = "./test_data/test_file_copy.txt"
    print(f"Copying file from {test_file_path} to {copy_path}...")
    file_tool.copy_file(test_file_path, copy_path)
    
    # Test moving a file
    move_path = "./test_data/test_file_moved.txt"
    print(f"Moving file from {copy_path} to {move_path}...")
    file_tool.move_file(copy_path, move_path)
    
    # Test file info
    print(f"Getting file info for {move_path}...")
    file_info = file_tool.get_file_info(move_path)
    print(f"File info: {file_info}")
    
    # Test deleting files
    print(f"Deleting file: {move_path}...")
    file_tool.delete_file(move_path)
    
    # Test safety mechanisms
    try:
        print("Testing safety mechanism by accessing a file outside safe paths...")
        file_tool.read_file("/etc/passwd")
    except ValueError as e:
        print(f"Safety mechanism worked: {e}")
    
    print("FileAccessTool tests completed successfully!")

if __name__ == "__main__":
    main() 