"""
Centralized configuration management.

This module is CRITICAL to the dual-mode architecture.
It loads configuration from two sources:
1. .env file (or environment variables) for secrets
2. config/agent_config.yaml for static settings

Both `adk web` and `main.py` import from this file, ensuring
consistent configuration across debug and production modes.

The configuration is loaded once when the module is imported,
and any errors will halt the application with a clear message.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for resolving relative paths (project root, not config dir)
BASE_DIR = Path(__file__).resolve().parent.parent


# --- YAML Configuration (Static Settings) ---


class AgentConfig(BaseModel):
    """Agent metadata and model settings."""

    name: str = Field(..., description="Internal agent name (snake_case)")
    display_name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="Agent description for A2A discovery")
    model: str = Field(..., description="Gemini model to use")


class PromptsConfig(BaseModel):
    """Prompt templates and system instructions."""

    system_instruction: str = Field(
        ..., description="The system prompt that defines the agent's behavior"
        instruction="""You are a expert Travel Agent that helps a user plan a trip 
                    based on his request.
                    Understand and extract below entities to plan an intenary:
                     - destination
                     - dates
                     - budget
                     - preferences

                     You can make use of below tool to validate if information is recieved:
                     - process_user_request

                     If any information is missing , ask clarifying questions if required information is missing.
                     
                     Once the information is recieved , we plan the itenary for user.

                     After planning we confirm , if the user is okay with the itenary.
                     You can make use of below tool to validate if user is okay with the intenary and get user input for improvement :                     
                     -confirm_travel_plan
                    """

    )


class YamlSettings(BaseModel):
    """Container for all YAML-based configuration."""

    agent: AgentConfig
    prompts: PromptsConfig


def load_yaml_config() -> YamlSettings:
    """
    Load configuration from YAML file.

    Returns:
        YamlSettings: Validated configuration object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValidationError: If config file is invalid
    """
    yaml_file = BASE_DIR / "config" / "agent_config.yaml"

    if not yaml_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found at: {yaml_file}\n"
            f"Please ensure config/agent_config.yaml exists in the project root."
        )

    with open(yaml_file, "r") as f:
        config_data: dict[str, Any] = yaml.safe_load(f)

    return YamlSettings(**config_data)


# --- Environment Configuration (Secrets) ---


class EnvSettings(BaseSettings):
    """
    Environment-based configuration for secrets.

    Values are loaded from .env file or environment variables.
    In production, set these as secure environment variables.
    """

    gemini_api_key: str = Field(
        ...,
        alias="GEMINI_API_KEY",
        description="Google Gemini API key",
    )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars
        case_sensitive=False,
    )


# --- Combined Settings (Single Source of Truth) ---


class Settings(BaseModel):
    """
    The single source of truth for all application settings.

    Combines environment-based secrets and YAML-based configuration
    into a single, type-safe object.
    """

    env: EnvSettings
    yaml: YamlSettings


# Load settings once when the module is imported
# Any errors will halt the application with a helpful message
try:
    settings = Settings(
        env=EnvSettings(),
        yaml=load_yaml_config(),
    )
except Exception as e:
    print("\n" + "=" * 70)
    print("FATAL ERROR: Could not load configuration")
    print("=" * 70)
    print("\nPlease check:")
    print("  1. .env file exists (copy from .env.example)")
    print("  2. GEMINI_API_KEY is set in .env")
    print("  3. config/agent_config.yaml exists and is valid")
    print("\nError details:")
    print(f"  {type(e).__name__}: {e}")
    print("=" * 70 + "\n")
    raise

