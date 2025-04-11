from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging
import json
import asyncio
import uuid
import os
import aiohttp

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# --- Models ---
class Message(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    provider: Optional[str] = None
    stream: Optional[bool] = False
    
class ChatResponse(BaseModel):
    message: Message
    
# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
            
    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

# Create manager instance
manager = ConnectionManager()

# --- Mock streaming response generator ---
async def mock_streaming_response(prompt: str) -> AsyncGenerator[str, None]:
    """
    Generate a mock streaming response for testing purposes.
    This will be replaced by actual model streaming later.
    """
    # Split the prompt into words to create a contextual response
    words = prompt.split()
    response_parts = [
        "I am QWORY (Quantum Web Orchestration Research Yield), an AI agent framework designed for task automation. ",
        "I'm part of the Trinity System alongside MARA (strategic brain) and MQWR (personal clone). ",
        f"Regarding your question about {' '.join(words[:3])}... ",
        "I can integrate with multiple model providers including OpenRouter, OpenAI, Google Gemini, and locally hosted models through Ollama. ",
        "My capabilities include web search, file access, and soon will expand to web automation, document processing, and more advanced tools. ",
        "This is currently a simulated response, but the full implementation will connect to actual AI models with streaming capability."
    ]
    
    for part in response_parts:
        yield part
        await asyncio.sleep(0.2)  # Simulate typing delay

# --- OpenRouter Integration ---
async def stream_openrouter_response(prompt: str, model_name: str) -> AsyncGenerator[str, None]:
    """
    Stream a response from OpenRouter API.
    
    Args:
        prompt: The user's prompt
        model_name: The model to use on OpenRouter
        
    Yields:
        Chunks of the response text
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("No OpenRouter API key found. Using mock response instead.")
        async for chunk in mock_streaming_response(prompt):
            yield chunk
        return
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/Iammcqwory/QWORY",
        "X-Title": "QWORY Framework"
    }
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"OpenRouter API error: {error_text}")
                    async for chunk in mock_streaming_response(prompt):
                        yield chunk
                    return
                    
                # Process the streaming response
                async for line in response.content:
                    if not line:
                        continue
                        
                    line_text = line.decode('utf-8').strip()
                    if not line_text:
                        continue
                        
                    # Skip the "data: " prefix
                    if line_text.startswith("data: "):
                        line_text = line_text[6:]
                            
                    # "[DONE]" is the end of the stream
                    if line_text == "[DONE]":
                        break
                            
                    try:
                        data = json.loads(line_text)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON from OpenRouter: {line_text}")
                    except Exception as e:
                        logger.error(f"Error processing streaming response: {str(e)}")
                        
    except Exception as e:
        logger.error(f"Error streaming response from OpenRouter: {str(e)}")
        # Fall back to mock response on error
        logger.info("Using mock response as fallback")
        async for chunk in mock_streaming_response(prompt):
            yield chunk

# --- Endpoints ---
@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the AI agent and get a response.
    """
    try:
        # Get the last user message
        user_message = next((m for m in reversed(request.messages) if m.role == "user"), None)
        prompt = user_message.content if user_message else ""
        
        # TODO: Replace with actual agent call
        # For now, just return a simple response
        response_content = f"This is a non-streaming response to: '{prompt}'. When implemented, this will integrate with the Qwory agent framework."
        
        response_message = Message(
            role="assistant",
            content=response_content
        )
        
        return ChatResponse(message=response_message)
    except Exception as e:
        logger.error(f"Error in chat message endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request."
        )

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for streaming chat responses.
    """
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Log the received message
            logger.info(f"Received message from client {client_id}: {request_data}")
            
            # Extract messages from the request
            messages = request_data.get("messages", [])
            provider = request_data.get("provider", "openrouter")
            model = request_data.get("model", "deepseek/deepseek-chat")
            
            # Get the last user message
            user_message = next((m for m in reversed(messages) if m["role"] == "user"), None)
            prompt = user_message["content"] if user_message else ""
            
            logger.info(f"Processing request with provider={provider}, model={model}, prompt='{prompt[:50]}...'")
            
            # Generate streaming response - use OpenRouter instead of mock
            if provider == "openrouter":
                async for chunk in stream_openrouter_response(prompt, model):
                    logger.debug(f"Sending chunk: {chunk}")
                    await manager.send_message(chunk, client_id)
            else:
                # Fall back to mock for other providers until implemented
                logger.info(f"Provider {provider} not yet implemented, using mock response")
                async for chunk in mock_streaming_response(prompt):
                    logger.debug(f"Sending chunk: {chunk}")
                    await manager.send_message(chunk, client_id)
                
            # End of response marker
            await manager.send_message(" [END]", client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
        try:
            await manager.send_message(f"Error: {str(e)}", client_id)
        except:
            pass
        manager.disconnect(client_id) 