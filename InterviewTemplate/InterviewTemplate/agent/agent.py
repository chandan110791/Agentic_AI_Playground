"""
Main agent definition.

This file defines the core agent using Google's ADK. The agent configuration
is loaded from config, which combines settings from .env and agent_config.yaml.

This agent definition is used by BOTH:
1. `adk web` (local debugging with chat UI)
2. `main.py` (production FastAPI server)
"""

import os

from google.generativeai import adk
from config import settings

# Set the API key from configuration
# This ensures both `adk web` and `main.py` have access to the key
os.environ["GEMINI_API_KEY"] = settings.env.gemini_api_key

# Load the system instruction from configuration
system_instruction = settings.yaml.prompts.system_instruction

# Define the root agent
# This is the single source of truth for the agent definition
root_agent = adk.Agent(
    model=settings.yaml.agent.model,
    system_instruction=system_instruction,
    description="root travel Agent that helps a user plan a trip based on natural language input"
    tools=[process_user_request,produce_travel_plan],  # Add your tools here
)


# Export as 'agent' for compatibility with main.py
agent = root_agent

