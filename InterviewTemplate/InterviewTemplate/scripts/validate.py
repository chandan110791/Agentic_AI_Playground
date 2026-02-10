#!/usr/bin/env python3
"""
Template Validation Script

Checks if the Google ADK Agent Template has been properly customized.
Run with: just validate
"""

import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def check_env_file() -> tuple[bool, str]:
    """Check if .env file exists and has been configured."""
    env_path = Path(".env")
    
    if not env_path.exists():
        return False, ".env file does not exist (copy from .env.example)"
    
    with open(env_path, "r") as f:
        content = f.read()
        
    if "your-api-key-here" in content:
        return False, "GEMINI_API_KEY still has placeholder value"
    
    if "GEMINI_API_KEY" not in content:
        return False, "GEMINI_API_KEY not found in .env"
    
    return True, ".env configured with API key"


def check_agent_config() -> tuple[bool, str]:
    """Check if agent configuration has been customized."""
    config_path = Path("config/agent_config.yaml")
    
    if not config_path.exists():
        return False, "config/agent_config.yaml not found"
    
    with open(config_path, "r") as f:
        content = f.read()
    
    issues = []
    
    if 'name: "my_agent"' in content:
        issues.append("agent name still 'my_agent'")
    
    if "My Agent" in content:
        issues.append("display_name still 'My Agent'")
    
    if issues:
        return False, f"Agent config needs customization: {', '.join(issues)}"
    
    return True, "Agent configuration customized"


def check_agent_json() -> tuple[bool, str]:
    """Check if A2A agent card has been updated."""
    agent_json_path = Path("static/.well-known/agent.json")
    
    if not agent_json_path.exists():
        return False, "agent.json not found"
    
    with open(agent_json_path, "r") as f:
        content = f.read()
    
    issues = []
    
    if "<TODO_YOUR_AGENT_NAME>" in content or "my_agent" in content:
        issues.append("agent name needs updating")
    
    if "My Agent" in content:
        issues.append("displayName needs updating")
    
    if issues:
        return False, f"agent.json needs updates: {', '.join(issues)}"
    
    return True, "A2A agent card updated"


def check_tools_customized() -> tuple[bool, str]:
    """Check if custom tools have been implemented."""
    tools_path = Path("agent/tools.py")
    
    if not tools_path.exists():
        return False, "agent/tools.py not found"
    
    with open(tools_path, "r") as f:
        content = f.read()
    
    # Check if tools have been added (file should have @adk.tool decorators)
    if content.count("@adk.tool") == 0:
        return (
            False,
            "No tools implemented yet (add your custom tools)",
        )
    
    return True, "Custom tools implemented"


def check_readme_updated() -> tuple[bool, str]:
    """Check if README has been customized."""
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        return False, "README.md not found"
    
    with open(readme_path, "r") as f:
        content = f.read()
    
    if "Google ADK Agent Template" in content and "Example Agent" in content:
        return False, "README.md still has template title/content"
    
    return True, "README.md customized"


def main() -> int:
    """Run all validation checks."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}  🔍 Google ADK Template Validation{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    checks = [
        ("Environment Configuration", check_env_file),
        ("Agent Configuration", check_agent_config),
        ("A2A Agent Card", check_agent_json),
        ("Custom Tools", check_tools_customized),
        ("README Customization", check_readme_updated),
    ]
    
    results = []
    all_passed = True
    
    for name, check_func in checks:
        passed, message = check_func()
        results.append((name, passed, message))
        
        if passed:
            print(f"  {GREEN}✓{RESET} {name:<30} {GREEN}{message}{RESET}")
        else:
            print(f"  {RED}✗{RESET} {name:<30} {YELLOW}{message}{RESET}")
            all_passed = False
    
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    if all_passed:
        print(f"{BOLD}{GREEN}✅ All checks passed! Template is properly customized.{RESET}\n")
        return 0
    else:
        print(f"{BOLD}{YELLOW}⚠️  Some checks failed. Please customize the template:{RESET}")
        print(f"\n{BOLD}Customization Checklist:{RESET}")
        print(f"  1. Copy .env.example to .env and add your GEMINI_API_KEY")
        print(f"  2. Update config/agent_config.yaml with your agent details")
        print(f"  3. Update static/.well-known/agent.json with your agent info")
        print(f"  4. Implement your custom tools in agent/tools.py")
        print(f"  5. Customize README.md with your project information")
        print(f"\n{BOLD}See DOCS.md for detailed customization guide.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

