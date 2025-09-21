# SignGPT-Crew-Server

SignGPT Server powered by crewai - FastAPI REST API for processing ASL tokens

## Overview

This server provides a REST API interface for processing American Sign Language (ASL) tokens using AI agents powered by CrewAI. The system converts ASL token sequences into natural English sentences through multiple specialized agents.

## Features

- **FastAPI REST API** - Modern, fast web API with automatic documentation
- **ASL Token Processing** - Convert ASL tokens to natural English sentences
- **Multi-Agent Workflow** - Specialized agents for different processing steps
- **Token Validation** - Validate tokens against ASL vocabulary dataset
- **Health Monitoring** - Built-in health check endpoints

## Quick Start

### 1. Install Dependencies

```bash
# Install using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the Server

```bash
# Using the startup script (recommended)
python start_server.py

# Or directly with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Interactive Explorer**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### POST /process-tokens

Process ASL tokens through the AI agent workflow.

**Request Body:**

```json
{
  "words": ["YOU", "NAME", "WHAT"]
}
```

**Response:**

```json
{
  "result": "What is your name?"
}
```

### GET /asl-dataset

Get information about available ASL vocabulary.

### POST /validate-tokens

Validate if tokens exist in the ASL dataset.

### GET /health

Health check endpoint with system status.

## Example Usage

### Using curl

```bash
# Process ASL tokens
curl -X POST "http://localhost:8000/process-tokens" \
  -H "Content-Type: application/json" \
  -d '{"words": ["YOU", "NAME", "WHAT"]}'

# Check health
curl "http://localhost:8000/health"

# Validate tokens
curl -X POST "http://localhost:8000/validate-tokens" \
  -H "Content-Type: application/json" \
  -d '["YOU", "INVALID_TOKEN", "NAME"]'
```

### Using Python requests

```python
import requests

# Process tokens
response = requests.post(
    "http://localhost:8000/process-tokens",
    json={"words": ["TOMORROW", "SCHOOL", "GO", "I"]}
)
result = response.json()
print(f"Result: {result['result']}")
```

## Original CLI Usage

The original command-line interface is still available:

```bash
python main.py
```

## Architecture

- **FastAPI** - Modern Python web framework
- **CrewAI** - Multi-agent AI framework
- **Pydantic** - Data validation and serialization
- **OpenAI GPT-4** - Language model for AI agents

## Development

- Auto-reload enabled in development mode
- Comprehensive error handling and validation
- CORS enabled for web frontend integration
- Detailed logging and monitoring
