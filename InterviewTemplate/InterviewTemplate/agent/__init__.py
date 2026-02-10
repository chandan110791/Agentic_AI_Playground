"""
Google ADK Agent Package.

This package contains all the agent-specific logic:
- agent.py: Main agent definition
- tools.py: Custom tools/functions the agent can use
- schema.py: Pydantic models for type safety
"""

from agent.agent import agent, root_agent

__all__ = ["agent", "root_agent"]

