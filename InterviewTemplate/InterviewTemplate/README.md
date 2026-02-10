# Google ADK Agent Template

Production-ready template for building AI agents with Google's Agent Development Kit. Supports dual-mode operation: local debugging + production deployment.

## Quick Start

```bash
# 1. Setup
just setup

# 2. Configure
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# 3. Develop
just web    # Chat UI at http://127.0.0.1:8000

# 4. Deploy
just prod   # API at http://127.0.0.1:8080
```

## Project Structure

```
.
├── agent/                      # Your agent implementation
│   ├── agent.py               # Main agent definition
│   ├── tools.py               # Custom tools (ADD YOUR TOOLS HERE)
│   └── schema.py              # Pydantic models for tools
│
├── config/                     # Configuration
│   ├── __init__.py            # Loads .env + agent_config.yaml
│   └── agent_config.yaml      # Agent settings & prompts
│
├── static/.well-known/
│   └── agent.json             # A2A protocol card
│
├── .env                       # Secrets (GEMINI_API_KEY)
├── main.py                    # Production FastAPI server
└── justfile                   # Commands
```

## Building Your Agent

### 1. Define Tool Schemas (`agent/schema.py`)

```python
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    query: str = Field(..., description="User's query")

class MyToolOutput(BaseModel):
    result: str
```

### 2. Implement Tools (`agent/tools.py`)

```python
from google.generativeai import adk
from agent.schema import MyToolInput, MyToolOutput

@adk.tool
def my_tool(request: MyToolInput) -> MyToolOutput:
    """What this tool does - the LLM reads this."""
    # Your implementation
    return MyToolOutput(result="...")
```

### 3. Register Tools (`agent/agent.py`)

```python
from agent.tools import my_tool

root_agent = adk.Agent(
    model=settings.yaml.agent.model,
    system_instruction=settings.yaml.prompts.system_instruction,
    tools=[my_tool],  # Add your tools here
)
```

### 4. Configure Agent (`config/agent_config.yaml`)

```yaml
agent:
  name: "your_agent"
  display_name: "Your Agent"
  description: "What your agent does"
  model: "gemini-2.0-flash-exp"

prompts:
  system_instruction: |
    You are an AI agent that...
    
    Your tools:
    - my_tool: When to use it
```

## Commands

```bash
# Development
just web        # Chat UI (debug mode)
just chat       # CLI chat (debug mode)
just prod       # Production server

# Code Quality
just lint       # Check style
just format     # Format code
just typecheck  # Type check
just test       # Run tests
just check      # All checks

# Other
just validate   # Check customization
just sync       # Sync dependencies
just clean      # Clean cache
```

## Dual-Mode Architecture

**Development Mode** (`just web`)
- Interactive chat UI
- Live tool execution
- Fast iteration
- Port 8000

**Production Mode** (`just prod`)
- RESTful API
- A2A protocol compliant
- Health checks
- Port 8080

Same agent code runs in both modes.

## API Endpoints (Production)

- `GET /` - Health & metadata
- `GET /health` - Health check
- `POST /run` - Execute agent (A2A)
- `GET /docs` - OpenAPI docs
- `GET /.well-known/agent.json` - A2A card

## Configuration

### Environment (`.env`)
```env
GEMINI_API_KEY="your-api-key"
```

### Agent Config (`config/agent_config.yaml`)
```yaml
agent:
  name: "agent_name"           # Internal name
  display_name: "Agent Name"   # UI display name
  description: "What it does"  # Description
  model: "gemini-2.0-flash-exp" # Model choice

prompts:
  system_instruction: |
    Your system prompt...
```

### Models Available
- `gemini-2.0-flash-exp` - Fast, experimental ✅
- `gemini-1.5-flash` - Fast, stable
- `gemini-1.5-pro` - Slower, more capable

## Tech Stack

- **Python 3.11+** - Language
- **Google ADK** - Agent framework
- **FastAPI** - Production API
- **Pydantic** - Type safety
- **UV** - Package manager (fast)
- **Just** - Command runner
- **MyPy** - Type checking
- **Ruff** - Linting

## Deployment

### Docker
```bash
just docker-build
just docker-run
```

### Cloud Run (GCP)
```bash
gcloud run deploy my-agent \
  --source . \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=your-key
```

### Kubernetes
Use the Dockerfile in `docker/Dockerfile`. Set `GEMINI_API_KEY` as a secret.

## A2A Protocol

This template is A2A (Agent-to-Agent) compliant:
- Service discovery via `/.well-known/agent.json`
- Standard `/run` endpoint
- OpenAPI documentation

Update `static/.well-known/agent.json` with your agent details.

## Development Workflow

1. Start: `just web`
2. Edit: `config/agent_config.yaml`, `agent/tools.py`, `agent/schema.py`
3. Test: Refresh chat UI
4. Quality: `just check`
5. Deploy: `just prod` → Docker → Cloud

## Code Quality

This template enforces:
- File length ≤ 300 lines
- Function length ≤ 40 lines
- Type hints everywhere
- MyPy strict mode
- Google-style docstrings

## Troubleshooting

**"GEMINI_API_KEY not found"**
→ Copy `.env.example` to `.env` and add your key

**Agent doesn't call tools**
→ Improve tool docstrings and system prompt

**Port in use**
→ `PORT=9000 just prod`

**Config errors**
→ Check `.env` and `config/agent_config.yaml` syntax

## Documentation

**[DOCS.md](DOCS.md)** - Complete guide (architecture, deployment, advanced usage)

## Resources

- [Google ADK Docs](https://google.github.io/adk-docs/)
- [A2A Protocol](https://agentstoaccess.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)

## License

Proprietary - See [LICENSE](LICENSE)

---

**Get your API key:** [Google AI Studio](https://aistudio.google.com/app/apikey)

**Status:** Production ready • A2A compliant • Type safe
