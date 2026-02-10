# Google ADK Agent Template - Documentation

## Overview

This template provides a production-ready foundation for building AI agents with Google's Agent Development Kit (ADK). It supports **dual-mode operation**: local debugging with a chat UI and production deployment as an A2A-compliant API.

## Quick Start

```bash
# 1. Install dependencies
just setup

# 2. Configure environment
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# 3. Start developing
just web    # Chat UI at http://127.0.0.1:8000
just prod   # API at http://127.0.0.1:8080
```

## Project Structure

```
.
├── agent/                      # Agent implementation
│   ├── agent.py               # Core agent definition
│   ├── schema.py              # Pydantic models for tools
│   └── tools.py               # Custom tool implementations
├── config/                     # Configuration
│   ├── __init__.py            # Config loader (loads .env + YAML)
│   └── agent_config.yaml      # Static settings (prompts, model)
├── static/.well-known/
│   └── agent.json             # A2A protocol discovery card
├── .env                       # Secrets (GEMINI_API_KEY)
├── main.py                    # Production FastAPI server
└── justfile                   # Command runner
```

## Core Concepts

### Dual-Mode Architecture

The same agent code runs in two modes:

**Development Mode** (`just web`)
- Interactive chat UI
- Live tool execution visibility
- Fast iteration
- Uses `adk web` command

**Production Mode** (`just prod`)
- RESTful API server
- A2A protocol compliant
- Health checks and monitoring
- Uses FastAPI + uvicorn

### Configuration Management

Configuration comes from two sources:

1. **`.env`** - Secrets (never commit)
   - `GEMINI_API_KEY` - Your API key

2. **`config/agent_config.yaml`** - Static settings (committed)
   - Agent name and description
   - Model selection
   - System prompt

Both are loaded by `config/__init__.py` and merged into a single `settings` object.

### Agent Definition

`agent/agent.py` defines the agent:

```python
root_agent = adk.Agent(
    model=settings.yaml.agent.model,
    system_instruction=settings.yaml.prompts.system_instruction,
    tools=[],  # Add your tools here
)
```

This agent is used by both debug and production modes.

## Building Your Agent

### 1. Define Tool Schemas

Create Pydantic models in `agent/schema.py`:

```python
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param: str = Field(..., description="What this does")

class MyToolOutput(BaseModel):
    result: str
```

### 2. Implement Tools

Add tools in `agent/tools.py`:

```python
from google.generativeai import adk
from agent.schema import MyToolInput, MyToolOutput

@adk.tool
def my_tool(request: MyToolInput) -> MyToolOutput:
    """Clear description of what this tool does."""
    # Implementation
    result = do_something(request.param)
    return MyToolOutput(result=result)
```

### 3. Register Tools

Add to `agent/agent.py`:

```python
from agent.tools import my_tool

root_agent = adk.Agent(
    model=settings.yaml.agent.model,
    system_instruction=settings.yaml.prompts.system_instruction,
    tools=[my_tool],  # Register here
)
```

### 4. Update System Prompt

Edit `config/agent_config.yaml`:

```yaml
prompts:
  system_instruction: |
    You are an AI agent that...
    
    Your tools:
    - my_tool: Description of when to use it
    
    Always explain your reasoning.
```

## Commands

```bash
# Development
just setup      # Install dependencies
just web        # Start chat UI (debug mode)
just chat       # Start CLI chat (debug mode)
just prod       # Start production server

# Code Quality
just lint       # Check code style
just format     # Format code
just typecheck  # Run MyPy
just test       # Run tests
just check      # Run all quality checks

# Docker
just docker-build   # Build container
just docker-run     # Run container

# Utilities
just sync       # Sync dependencies
just validate   # Validate template customization
just info       # Show project info
```

## API Endpoints (Production Mode)

When running `just prod`:

- `GET /` - Health check and metadata
- `GET /health` - Simple health check
- `POST /run` - Main agent execution (A2A protocol)
- `GET /docs` - OpenAPI documentation
- `GET /.well-known/agent.json` - A2A discovery card

## A2A Protocol

The template is A2A (Agent-to-Agent) compliant, enabling:
- Service discovery via `/.well-known/agent.json`
- Standard communication protocol
- Agent composition and orchestration

Update `static/.well-known/agent.json` with your agent details.

## Configuration Reference

### Environment Variables (`.env`)

```env
GEMINI_API_KEY="your-api-key"
```

### Agent Config (`config/agent_config.yaml`)

```yaml
agent:
  name: "my_agent"              # Internal name (snake_case)
  display_name: "My Agent"      # Human-readable name
  description: "What it does"   # Agent description
  model: "gemini-2.0-flash-exp" # Model selection

prompts:
  system_instruction: |
    Your system prompt here...
```

### Available Models

- `gemini-2.0-flash-exp` - Fast, experimental (recommended)
- `gemini-1.5-flash` - Fast, stable
- `gemini-1.5-pro` - Slower, more capable

## Development Workflow

1. **Start debug mode**: `just web`
2. **Edit configuration**: `config/agent_config.yaml`
3. **Add tools**: `agent/tools.py` and `agent/schema.py`
4. **Register tools**: `agent/agent.py`
5. **Test changes**: Restart debug mode
6. **Run quality checks**: `just check`
7. **Test production mode**: `just prod`

## Deployment

### Docker

```bash
# Build
just docker-build

# Run locally
just docker-run

# Push to registry
docker tag my-agent:latest registry.com/my-agent:latest
docker push registry.com/my-agent:latest
```

### Cloud Run (GCP)

```bash
gcloud run deploy my-agent \
  --source . \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=your-key
```

### Environment Variables for Production

Set these in your deployment environment:
- `GEMINI_API_KEY` - Required
- `PORT` - Optional (default: 8080)
- `LOG_LEVEL` - Optional (default: INFO)

## Code Quality Standards

- **File length**: ≤ 300 lines
- **Function length**: ≤ 40 lines
- **Cyclomatic complexity**: ≤ 10
- **Type hints**: Required everywhere (pass `mypy --strict`)
- **Docstrings**: Google-style for all public APIs

## Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure `.env` exists with your API key
- Check `.env` is in project root

### Agent doesn't call tools
- Improve tool docstrings (be specific)
- Update system prompt with examples
- Simplify tool names

### Config loading errors
- Verify `.env` exists and has valid values
- Check `config/agent_config.yaml` is valid YAML
- Run: `uv run python -c "from config import settings; print(settings)"`

### Port already in use
- Change port: `PORT=9000 just prod`
- Stop other services using the port

## Tech Stack

- **Python 3.11+** - Language
- **Google ADK** - Agent framework
- **FastAPI** - Production server
- **Pydantic** - Type-safe config & schemas
- **UV** - Package manager (10-100x faster than pip)
- **Just** - Command runner
- **MyPy** - Type checking
- **Ruff** - Linting and formatting

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol](https://agentstoaccess.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

**Need help?** Run `just info` to see project details or `just validate` to check your setup.
