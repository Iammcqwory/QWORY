from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
import requests

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# --- Models ---
class Model(BaseModel):
    id: str
    name: str
    
class ModelProvider(BaseModel):
    id: str
    name: str
    models: List[Model]
    status: str = "available"
    
class ModelConfig(BaseModel):
    provider: str
    model: str
    
# --- Helper Functions ---
async def get_ollama_models() -> List[Model]:
    """Get available models from local Ollama installation."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            return [Model(id=model["name"], name=model["name"]) for model in models_data]
        return [
            Model(id="llama3", name="Llama 3"),
            Model(id="llama3:8b", name="Llama 3 (8B)"),
            Model(id="mistral", name="Mistral"),
            Model(id="codellama", name="Code Llama")
        ]
    except Exception as e:
        logger.error(f"Error fetching Ollama models: {str(e)}")
        # Return default models if Ollama is not available
        return [
            Model(id="llama3", name="Llama 3"),
            Model(id="mistral", name="Mistral")
        ]

async def get_openrouter_models() -> List[Model]:
    """Get available models from OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        # Return default models if API key not available
        return [
            Model(id="deepseek/deepseek-chat", name="DeepSeek Chat"),
            Model(id="mistralai/mistral-medium", name="Mistral Medium")
        ]
        
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        if response.status_code == 200:
            models_data = response.json().get("data", [])
            return [Model(id=model["id"], name=model["name"]) for model in models_data]
        return [
            Model(id="deepseek/deepseek-chat", name="DeepSeek Chat"),
            Model(id="mistralai/mistral-medium", name="Mistral Medium")
        ]
    except Exception as e:
        logger.error(f"Error fetching OpenRouter models: {str(e)}")
        return [
            Model(id="deepseek/deepseek-chat", name="DeepSeek Chat"),
            Model(id="mistralai/mistral-medium", name="Mistral Medium")
        ]

async def check_provider_status(provider_id: str) -> str:
    """Check if a provider is available and functioning."""
    try:
        if provider_id == "ollama":
            try:
                response = requests.get("http://localhost:11434/api/version", timeout=2)
                return "available" if response.status_code == 200 else "unavailable"
            except requests.exceptions.RequestException:
                return "unavailable"  # Ollama server not running
        elif provider_id == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                return "no_api_key"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers, timeout=5)
            return "available" if response.status_code == 200 else "unavailable"
        elif provider_id == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            return "no_api_key" if not api_key else "available"
        elif provider_id == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            return "no_api_key" if not api_key else "available"
        else:
            return "unsupported_provider"
    except Exception as e:
        logger.error(f"Error checking provider status: {str(e)}")
        return "error"

# --- Endpoints ---
@router.get("/providers", response_model=List[ModelProvider])
async def list_providers():
    """List all available model providers."""
    providers = [
        {
            "id": "openrouter", 
            "name": "OpenRouter", 
            "status": await check_provider_status("openrouter")
        },
        {
            "id": "ollama", 
            "name": "Ollama (Local)", 
            "status": await check_provider_status("ollama")
        },
        {
            "id": "gemini", 
            "name": "Google Gemini", 
            "status": await check_provider_status("gemini")
        },
        {
            "id": "openai", 
            "name": "OpenAI", 
            "status": await check_provider_status("openai")
        }
    ]
    
    result = []
    for provider in providers:
        if provider["id"] == "ollama":
            models = await get_ollama_models()
        elif provider["id"] == "openrouter":
            models = await get_openrouter_models()
        elif provider["id"] == "gemini":
            models = [
                Model(id="gemini-1.5-pro", name="Gemini 1.5 Pro"),
                Model(id="gemini-1.5-flash", name="Gemini 1.5 Flash")
            ]
        elif provider["id"] == "openai":
            models = [
                Model(id="gpt-4o", name="GPT-4o"),
                Model(id="gpt-4-turbo", name="GPT-4 Turbo")
            ]
        else:
            models = []
            
        result.append(ModelProvider(
            id=provider["id"],
            name=provider["name"],
            models=models,
            status=provider["status"]
        ))
        
    return result

@router.get("/", response_model=Dict[str, List[Model]])
async def list_models():
    """List all available models grouped by provider."""
    ollama_models = await get_ollama_models()
    openrouter_models = await get_openrouter_models()
    
    return {
        "ollama": ollama_models,
        "openrouter": openrouter_models,
        "gemini": [
            Model(id="gemini-1.5-pro", name="Gemini 1.5 Pro"),
            Model(id="gemini-1.5-flash", name="Gemini 1.5 Flash")
        ],
        "openai": [
            Model(id="gpt-4o", name="GPT-4o"),
            Model(id="gpt-4-turbo", name="GPT-4 Turbo")
        ]
    }

@router.get("/{provider_id}", response_model=List[Model])
async def list_provider_models(provider_id: str):
    """List models for a specific provider."""
    if provider_id == "ollama":
        return await get_ollama_models()
    elif provider_id == "openrouter":
        return await get_openrouter_models()
    elif provider_id == "gemini":
        return [
            Model(id="gemini-1.5-pro", name="Gemini 1.5 Pro"),
            Model(id="gemini-1.5-flash", name="Gemini 1.5 Flash")
        ]
    elif provider_id == "openai":
        return [
            Model(id="gpt-4o", name="GPT-4o"),
            Model(id="gpt-4-turbo", name="GPT-4 Turbo")
        ]
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found"
        ) 