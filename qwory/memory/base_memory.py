#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Memory Implementation

This module contains the base memory classes for the Qwory framework.
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Union
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseMemory(ABC):
    """
    Abstract base class for all memory implementations in the Qwory framework.
    
    This class defines the interface that all memory implementations must follow.
    It provides common functionality and enforces a consistent API across
    different memory types.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new memory instance.
        
        Args:
            config: Configuration dictionary for the memory.
        """
        self.config = config or {}
        self.items = []
        logger.debug(f"{self.__class__.__name__} initialized")
    
    @abstractmethod
    def add(self, item: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an item to memory.
        
        Args:
            item: The item to add to memory.
            metadata: Additional metadata to store with the item.
            
        Returns:
            A unique identifier for the stored item.
        """
        pass
    
    @abstractmethod
    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item from memory by its ID.
        
        Args:
            item_id: The ID of the item to retrieve.
            
        Returns:
            The item and its metadata, or None if no item with the given ID exists.
        """
        pass
    
    @abstractmethod
    def search(self, query: Any) -> List[Dict[str, Any]]:
        """
        Search for items in memory that match the query.
        
        Args:
            query: The query to search for.
            
        Returns:
            A list of matching items and their metadata.
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Clear all items from memory.
        """
        pass


class ShortTermMemory(BaseMemory):
    """
    Short-term memory implementation for the Qwory framework.
    
    Short-term memory is designed to store recent information that is frequently
    accessed but may be forgotten after a certain period or when capacity is reached.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new short-term memory instance.
        
        Args:
            config: Configuration dictionary for the memory.
        """
        super().__init__(config)
        self.max_items = self.config.get("max_items", 100)
        self.ttl = self.config.get("ttl", 3600)  # Time-to-live in seconds (default: 1 hour)
        logger.info(f"ShortTermMemory initialized with max_items={self.max_items}, ttl={self.ttl}")
    
    def add(self, item: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an item to short-term memory.
        
        If the memory is at capacity, the oldest item will be removed.
        
        Args:
            item: The item to add to memory.
            metadata: Additional metadata to store with the item.
            
        Returns:
            A unique identifier for the stored item.
        """
        # Clean up expired items
        self._cleanup_expired()
        
        # Generate a unique ID for the item
        item_id = f"stm-{int(time.time())}-{len(self.items)}"
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Create memory entry
        entry = {
            "id": item_id,
            "item": item,
            "metadata": metadata,
            "created_at": time.time(),
            "expires_at": time.time() + self.ttl
        }
        
        # Add to memory
        self.items.append(entry)
        logger.debug(f"Item added to short-term memory with ID {item_id}")
        
        # If we're over capacity, remove the oldest item
        if len(self.items) > self.max_items:
            oldest = self.items.pop(0)
            logger.debug(f"Removed oldest item from short-term memory with ID {oldest['id']}")
        
        return item_id
    
    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item from short-term memory by its ID.
        
        Args:
            item_id: The ID of the item to retrieve.
            
        Returns:
            The item and its metadata, or None if no item with the given ID exists or has expired.
        """
        # Clean up expired items
        self._cleanup_expired()
        
        # Find the item
        for entry in self.items:
            if entry["id"] == item_id:
                # Check if the item has expired
                if time.time() > entry["expires_at"]:
                    logger.debug(f"Item with ID {item_id} has expired")
                    return None
                
                # Update the expiration time (reset TTL)
                entry["expires_at"] = time.time() + self.ttl
                logger.debug(f"Retrieved item from short-term memory with ID {item_id}")
                
                return {
                    "id": entry["id"],
                    "item": entry["item"],
                    "metadata": entry["metadata"],
                    "created_at": entry["created_at"]
                }
        
        logger.debug(f"No item found in short-term memory with ID {item_id}")
        return None
    
    def search(self, query: Any) -> List[Dict[str, Any]]:
        """
        Search for items in short-term memory that match the query.
        
        This is a simple implementation that checks if the query is contained
        in the string representation of the item.
        
        Args:
            query: The query to search for.
            
        Returns:
            A list of matching items and their metadata.
        """
        # Clean up expired items
        self._cleanup_expired()
        
        results = []
        query_str = str(query).lower()
        
        for entry in self.items:
            # Check if the item has expired
            if time.time() > entry["expires_at"]:
                continue
            
            # Simple string matching (could be more sophisticated)
            item_str = str(entry["item"]).lower()
            if query_str in item_str:
                # Update the expiration time (reset TTL)
                entry["expires_at"] = time.time() + self.ttl
                
                results.append({
                    "id": entry["id"],
                    "item": entry["item"],
                    "metadata": entry["metadata"],
                    "created_at": entry["created_at"]
                })
        
        logger.debug(f"Found {len(results)} matching items in short-term memory for query '{query}'")
        return results
    
    def clear(self) -> None:
        """
        Clear all items from short-term memory.
        """
        count = len(self.items)
        self.items = []
        logger.info(f"Cleared {count} items from short-term memory")
    
    def _cleanup_expired(self) -> None:
        """
        Remove expired items from memory.
        """
        now = time.time()
        original_count = len(self.items)
        
        self.items = [entry for entry in self.items if entry["expires_at"] > now]
        
        removed_count = original_count - len(self.items)
        if removed_count > 0:
            logger.debug(f"Removed {removed_count} expired items from short-term memory")


class LongTermMemory(BaseMemory):
    """
    Long-term memory implementation for the Qwory framework.
    
    Long-term memory is designed to store information that needs to be retained
    for extended periods or indefinitely. It may use persistent storage to ensure
    data is not lost between sessions.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new long-term memory instance.
        
        Args:
            config: Configuration dictionary for the memory.
        """
        super().__init__(config)
        self.persistence_enabled = self.config.get("persistence_enabled", False)
        self.persistence_path = self.config.get("persistence_path", "./memory.json")
        
        # Load persisted data if enabled
        if self.persistence_enabled:
            self._load_from_disk()
        
        logger.info(f"LongTermMemory initialized with persistence_enabled={self.persistence_enabled}")
    
    def add(self, item: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an item to long-term memory.
        
        Args:
            item: The item to add to memory.
            metadata: Additional metadata to store with the item.
            
        Returns:
            A unique identifier for the stored item.
        """
        # Generate a unique ID for the item
        item_id = f"ltm-{int(time.time())}-{len(self.items)}"
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Create memory entry
        entry = {
            "id": item_id,
            "item": item,
            "metadata": metadata,
            "created_at": time.time(),
            "importance": metadata.get("importance", 0.5)  # Default importance is medium (0.5)
        }
        
        # Add to memory
        self.items.append(entry)
        logger.debug(f"Item added to long-term memory with ID {item_id}")
        
        # Persist to disk if enabled
        if self.persistence_enabled:
            self._save_to_disk()
        
        return item_id
    
    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item from long-term memory by its ID.
        
        Args:
            item_id: The ID of the item to retrieve.
            
        Returns:
            The item and its metadata, or None if no item with the given ID exists.
        """
        for entry in self.items:
            if entry["id"] == item_id:
                logger.debug(f"Retrieved item from long-term memory with ID {item_id}")
                
                return {
                    "id": entry["id"],
                    "item": entry["item"],
                    "metadata": entry["metadata"],
                    "created_at": entry["created_at"],
                    "importance": entry["importance"]
                }
        
        logger.debug(f"No item found in long-term memory with ID {item_id}")
        return None
    
    def search(self, query: Any) -> List[Dict[str, Any]]:
        """
        Search for items in long-term memory that match the query.
        
        This is a simple implementation that checks if the query is contained
        in the string representation of the item.
        
        Args:
            query: The query to search for.
            
        Returns:
            A list of matching items and their metadata.
        """
        results = []
        query_str = str(query).lower()
        
        for entry in self.items:
            # Simple string matching (could be more sophisticated)
            item_str = str(entry["item"]).lower()
            if query_str in item_str:
                results.append({
                    "id": entry["id"],
                    "item": entry["item"],
                    "metadata": entry["metadata"],
                    "created_at": entry["created_at"],
                    "importance": entry["importance"]
                })
        
        # Sort results by importance (most important first)
        results.sort(key=lambda x: x["importance"], reverse=True)
        
        logger.debug(f"Found {len(results)} matching items in long-term memory for query '{query}'")
        return results
    
    def clear(self) -> None:
        """
        Clear all items from long-term memory.
        """
        count = len(self.items)
        self.items = []
        logger.info(f"Cleared {count} items from long-term memory")
        
        # Persist empty state to disk if enabled
        if self.persistence_enabled:
            self._save_to_disk()
    
    def _save_to_disk(self) -> None:
        """
        Save memory contents to disk.
        
        This is a placeholder implementation. In a real implementation, this would
        serialize the memory contents to a file or database.
        """
        logger.debug(f"Saving long-term memory to disk at {self.persistence_path}")
        # TODO: Implement actual persistence
        # For now, just log that we would save to disk
    
    def _load_from_disk(self) -> None:
        """
        Load memory contents from disk.
        
        This is a placeholder implementation. In a real implementation, this would
        deserialize the memory contents from a file or database.
        """
        logger.debug(f"Loading long-term memory from disk at {self.persistence_path}")
        # TODO: Implement actual persistence
        # For now, just log that we would load from disk