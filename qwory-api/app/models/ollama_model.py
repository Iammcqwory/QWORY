import aiohttp
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import json

from .base_model import BaseModel

logger = logging.getLogger(__name__)

class OllamaModel(BaseModel):
    """
    Implementation of BaseModel for Ollama local models.
    This model connects to a local Ollama server to generate text and embeddings.
    """
    
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama model.
        
        Args:
            model_name: Name of the Ollama model to use
            base_url: URL of the Ollama server
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        
        # Validate parameters
        if not model_name:
            raise ValueError("Model name cannot be empty")
        
        logger.info(f"Initialized OllamaModel with model={model_name}, url={base_url}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using Ollama.
        
        Args:
            prompt: The input prompt to generate a response for
            **kwargs: Additional parameters to pass to Ollama API
            
        Returns:
            Generated response as a string
        """
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        # Generate the response
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {error_text}")
                        raise Exception(f"Ollama API error: {response.status} - {error_text}")
                    
                    result = await response.json()
                    return result.get("response", "")
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {str(e)}")
            raise
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a response from Ollama.
        
        Args:
            prompt: The input prompt to generate a response for
            **kwargs: Additional parameters to pass to Ollama API
            
        Yields:
            Chunks of the generated response as they become available
        """
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {error_text}")
                        raise Exception(f"Ollama API error: {response.status} - {error_text}")
                    
                    # Process the streaming response
                    async for line in response.content:
                        if not line:
                            continue
                        
                        try:
                            line_text = line.decode('utf-8').strip()
                            if not line_text:
                                continue
                                
                            data = json.loads(line_text)
                            if "response" in data:
                                yield data["response"]
                                
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON from Ollama: {line}")
                        except Exception as e:
                            logger.error(f"Error processing streaming response: {str(e)}")
                            raise
        except Exception as e:
            logger.error(f"Error streaming response from Ollama: {str(e)}")
            raise
    
    async def get_embeddings(self, text: str, **kwargs) -> List[float]:
        """
        Generate embeddings using Ollama.
        
        Args:
            text: The input text to generate embeddings for
            **kwargs: Additional parameters to pass to Ollama API
            
        Returns:
            A list of floats representing the embedding vector
        """
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "prompt": text,
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/embeddings", json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {error_text}")
                        raise Exception(f"Ollama API error: {response.status} - {error_text}")
                    
                    result = await response.json()
                    return result.get("embedding", [])
        except Exception as e:
            logger.error(f"Error generating embeddings with Ollama: {str(e)}")
            raise 