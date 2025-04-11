# Qwory Web UI

Modern web interface for the Qwory AI agent framework, designed to run completely with local models via Ollama without requiring any external API keys.

## 🌟 Features

- **Chat Interface**: Modern chat UI with message history
- **Streaming Responses**: Real-time streaming via WebSockets
- **Local Model Execution**: Run models locally with Ollama (no API keys needed)
- **Dark/Light Theme**: Responsive design that works on all devices
- **Model Selection**: Support for multiple model providers
- **Docker Integration**: Easy setup with Docker Compose

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Setup and Run

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/qwory.git
   cd qwory
   ```

2. Start the application with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the web interface:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000

4. The system will automatically download and setup Llama 3 model on first run.

## 🔧 Local Development

### Frontend (React)

1. Navigate to the frontend directory:
   ```bash
   cd qwory-ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Backend (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd qwory-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## 🧠 Local Models with Ollama

Qwory Web UI uses [Ollama](https://ollama.ai/) to run AI models locally without requiring any API keys. Here are the available models:

### Available Models

- **General Purpose**:
  - Llama 3 (`llama3`)
  - Llama 3 8B (`llama3:8b`)
  - Mistral (`mistral`)

- **Code Specialized**:
  - DeepSeek Coder (`deepseek-coder`)
  - Code Llama (`codellama`)
  - Wizard Coder (`wizard-coder`)

- **Smaller Models**:
  - Phi-3 Mini (`phi3:mini`)
  - Mistral 7B (`mistral:7b`)

### Using a Specific Model

To use a specific model, select it from the dropdown in the settings page of the web UI, or specify it when starting Qwory from the command line.

## 📁 Project Structure

```
qwory/
├── docker-compose.yml       # Docker Compose configuration
├── qwory-ui/                # Frontend application
│   ├── src/                 # React source code
│   ├── Dockerfile           # Frontend Docker configuration
│   └── nginx.conf           # Nginx configuration
├── qwory-api/               # Backend application
│   ├── app/                 # FastAPI application code
│   ├── Dockerfile           # Backend Docker configuration
│   └── requirements.txt     # Python dependencies
└── data/                    # Shared data volume
```

## 🔄 API Endpoints

- `GET /api/models` - List available models
- `POST /api/chat` - Send a message to the agent
- `WS /ws/chat` - WebSocket endpoint for streaming responses

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Ollama](https://ollama.ai/) for making local models easily accessible
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [React](https://reactjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling
