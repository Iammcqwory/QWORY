from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Qwory API", description="API for Qwory AI Agent Framework")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from .routers import chat, models, tools, files
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

@app.get("/")
async def root():
    return {"message": "Welcome to Qwory API", "status": "operational"}

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"}
    )

@app.get("/api/models")
async def list_models():
    """
    Temporary endpoint to list models until the full router is implemented.
    """
    return {
        "models": {
            "ollama": [
                {"id": "llama3", "name": "Llama 3"},
                {"id": "llama3:8b", "name": "Llama 3 (8B)"},
                {"id": "mistral", "name": "Mistral"},
                {"id": "codellama", "name": "Code Llama"}
            ],
            "openrouter": [
                {"id": "deepseek/deepseek-chat", "name": "DeepSeek Chat"},
                {"id": "mistralai/mistral-medium", "name": "Mistral Medium"}
            ],
            "gemini": [
                {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"}
            ],
            "openai": [
                {"id": "gpt-4o", "name": "GPT-4o"}
            ]
        }
    }

@app.post("/api/chat")
async def chat():
    """
    Temporary endpoint for chat until the full router is implemented.
    """
    return {
        "message": {
            "role": "assistant",
            "content": "This is a placeholder response. The actual API implementation will connect to the Qwory framework and use Ollama for local model execution."
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 