from typing import List, Dict, Any, Optional, AsyncGenerator
from abc import ABC, abstractmethod

class BaseModel(ABC):
    """
    Base class for all model implementations.
    All specific model implementations should inherit from this class.
    """
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response to the given prompt.
        
        Args:
            prompt: The input prompt to generate a response for
            **kwargs: Additional model-specific parameters
            
        Returns:
            The generated response as a string
        """
        pass
    
    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a response to the given prompt.
        
        Args:
            prompt: The input prompt to generate a response for
            **kwargs: Additional model-specific parameters
            
        Yields:
            Chunks of the generated response as they become available
        """
        pass
    
    @abstractmethod
    async def get_embeddings(self, text: str, **kwargs) -> List[float]:
        """
        Generate embeddings for the given text.
        
        Args:
            text: The input text to generate embeddings for
            **kwargs: Additional model-specific parameters
            
        Returns:
            A list of floats representing the embedding vector
        """
        pass 