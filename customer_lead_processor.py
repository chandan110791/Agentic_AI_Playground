"""
Customer Lead Processor

- Uses a minimal deterministic pipeline in pure Python stdlib.
- Adds a Google ADK integration hook path (when google.adk is available).
- Keeps Agent vs Orchestrator boundaries explicit.
"""

from __future__ import annotations

import copy
import importlib
import inspect
import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple


class ToolRegistry:
    """Maps tool names to callables. Orchestrator executes them on behalf of agents."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., Dict[str, Any]]] = {}

    def register(self, name: str, fn: Callable[..., Dict[str, Any]]) -> None:
        self._tools[name] = fn

    def execute(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self._tools:
            return {"ok": False, "error": f"Unknown tool: {tool_name}"}
        try:
            return {"ok": True, "result": self._tools[tool_name](**args)}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}


def verify_email_format(email: str) -> Dict[str, Any]:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return {"email": email, "valid": bool(re.match(pattern, email or ""))}


def normalize_phone(phone: str) -> Dict[str, Any]:
    digits = re.sub(r"\D", "", phone or "")
    valid = 10 <= len(digits) <= 15
    return {"raw": phone, "normalized": digits, "valid": valid}


@dataclass
class Agent:
    name: str
    instructions: str
    output_key: str

    def render_instructions(self, state: Dict[str, Any]) -> str:
        class SafeDict(dict):
            def __missing__(self, key: str) -> str:
                return "{" + key + "}"

        safe_state = SafeDict()
        for key, value in state.items():
            safe_state[key] = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
        return self.instructions.format_map(safe_state)

    def run(self, state: Dict[str, Any], user_input: str, orchestrator: "SequentialAgent") -> Dict[str, Any]:
        raise NotImplementedError


class ValidatorAgent(Agent):
    def run(self, state: Dict[str, Any], user_input: str, orchestrator: "SequentialAgent") -> Dict[str, Any]:
        _ = self.render_instructions(state)
        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", user_input)
        phone_match = re.search(r"(?:\+?\d[\d\s().-]{8,}\d)", user_input)

        email = email_match.group(0) if email_match else None
        phone_raw = phone_match.group(0) if phone_match else None

        tool_results: Dict[str, Any] = {}
        if email:
            tool_results["email_check"] = orchestrator.execute_tool_request(
                {"tool": "verify_email_format", "args": {"email": email}}
            )
        if phone_raw:
            tool_results["phone_check"] = orchestrator.execute_tool_request(
                {"tool": "normalize_phone", "args": {"phone": phone_raw}}
            )

        email_valid = bool(tool_results.get("email_check", {}).get("ok")) and bool(
            tool_results.get("email_check", {}).get("result", {}).get("valid")
        )
        phone_valid = bool(tool_results.get("phone_check", {}).get("ok")) and bool(
            tool_results.get("phone_check", {}).get("result", {}).get("valid")
        )
        phone_normalized = tool_results.get("phone_check", {}).get("result", {}).get("normalized")

        lowered = user_input.lower()
        preferred_contact = (
            "email"
            if "email" in lowered
            else "phone"
            if ("call" in lowered or "phone" in lowered)
            else "email"
            if email_valid
            else "phone"
            if phone_valid
            else None
        )

        errors: List[str] = []
        if email and not email_valid:
            errors.append("Detected email appears invalid.")
        if phone_raw and not phone_valid:
            errors.append("Detected phone appears invalid.")
        if not email and not phone_raw:
            errors.append("No contact method detected.")

        return {
            "has_email": email is not None,
            "email": email,
            "email_valid": email_valid,
            "has_phone": phone_raw is not None,
            "phone": phone_normalized if phone_normalized else phone_raw,
            "phone_valid": phone_valid,
            "preferred_contact": preferred_contact,
            "errors": errors,
        }


class ScorerAgent(Agent):
    KEYWORDS = ("buy", "price", "demo", "quote", "urgent")

    def run(self, state: Dict[str, Any], user_input: str, orchestrator: "SequentialAgent") -> Dict[str, Any]:
        _ = self.render_instructions(state)
        lead_status = state.get("lead_status", {})
        text = user_input.lower()

        score = 5
        reasons: List[str] = []
        matches = [k for k in self.KEYWORDS if k in text]
        if matches:
            inc = min(4, len(matches))
            score += inc
            reasons.append(f"Intent keywords found: {', '.join(matches)} (+{inc}).")
        else:
            score -= 1
            reasons.append("No high-intent keywords (-1).")

        if lead_status.get("email_valid") or lead_status.get("phone_valid"):
            score += 2
            reasons.append("Valid contact method present (+2).")
        else:
            score -= 3
            reasons.append("No valid contact method (-3).")

        score = max(1, min(10, score))
        return {"lead_score": score, "score_rationale": " ".join(reasons)}


class EmailerAgent(Agent):
    def run(self, state: Dict[str, Any], user_input: str, orchestrator: "SequentialAgent") -> Dict[str, Any]:
        _ = self.render_instructions(state)
        score_blob = state.get("lead_score", {})
        status = state.get("lead_status", {})
        score = score_blob.get("lead_score") if isinstance(score_blob, dict) else None

        if score is None:
            return {"email_drafted": None, "reason": "Missing lead score."}
        if score <= 7:
            return {"email_drafted": None, "reason": f"Lead score {score} is not above threshold (7)."}

        name = _extract_name(user_input) or "there"
        preferred = status.get("preferred_contact") or "email"
        contact_hint = status.get("email") if preferred == "email" else status.get("phone")
        draft = (
            "Subject: Quick follow-up on your request\n\n"
            f"Hi {name},\n\n"
            "Thanks for reaching out. I saw your interest and wanted to help right away. "
            "Based on your message, we can share pricing details and schedule a short demo this week.\n\n"
            f"If helpful, reply here and we’ll send next steps. Preferred contact noted: {preferred} ({contact_hint}).\n\n"
            "Best,\nCustomer Lead Team"
        )
        return {"email_drafted": draft, "reason": "Lead is eligible for outreach."}


class SequentialAgent:
    """Local orchestrator.

    Also provides ADK hooks by exposing a tool protocol (`execute_tool_request`) and
    agent outputs by `output_key` in shared state.
    """

    def __init__(self, agents: List[Agent], tool_registry: Optional[ToolRegistry] = None) -> None:
        self.agents = agents
        self.tool_registry = tool_registry or ToolRegistry()

    def execute_tool_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        tool = request.get("tool")
        args = request.get("args", {})
        if not tool:
            return {"ok": False, "error": "Tool request missing 'tool' field."}
        return self.tool_registry.execute(tool, args)

    def run(self, user_input: str, initial_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        state: Dict[str, Any] = copy.deepcopy(initial_state or {})
        state["user_input"] = user_input
        for agent in self.agents:
            output = agent.run(state=state, user_input=user_input, orchestrator=self)
            state[agent.output_key] = output
            print(f"\n--- After {agent.name} ({agent.output_key}) ---")
            print(json.dumps(state, indent=2, ensure_ascii=False))
        return state


class GoogleADKToolkitBridge:
    """Bridge that tries to register local tools with google.adk when present.

    NOTE: this avoids hard-coding unknown ADK APIs. It discovers optional decorators
    and wrappers dynamically, and falls back to plain callables.
    """

    def __init__(self) -> None:
        self.module = self._import_google_adk()

    @staticmethod
    def _import_google_adk() -> Optional[Any]:
        try:
            return importlib.import_module("google.adk")
        except Exception:
            return None

    def is_available(self) -> bool:
        return self.module is not None

    def wrap_tool(self, fn: Callable[..., Dict[str, Any]]) -> Callable[..., Dict[str, Any]]:
        if not self.module:
            return fn
        decorator = getattr(self.module, "tool", None)
        if callable(decorator):
            try:
                return decorator(fn)
            except Exception:
                return fn
        return fn

    def summary(self) -> str:
        if not self.module:
            return "google.adk not available in environment; running stdlib fallback orchestrator."
        return "google.adk module detected; toolkit bridge enabled for available tool decorators."


def _extract_name(text: str) -> Optional[str]:
    m = re.search(r"\b(?:i\s*am|i'm)\s+([A-Za-z][A-Za-z'-]{1,30})\b", text, flags=re.IGNORECASE)
    return m.group(1).title() if m else None


def build_pipeline() -> Tuple[SequentialAgent, GoogleADKToolkitBridge]:
    adk_bridge = GoogleADKToolkitBridge()

    tools = ToolRegistry()
    tools.register("verify_email_format", adk_bridge.wrap_tool(verify_email_format))
    tools.register("normalize_phone", adk_bridge.wrap_tool(normalize_phone))

    agents: List[Agent] = [
        ValidatorAgent(
            name="ValidatorAgent",
            output_key="lead_status",
            instructions=(
                "Validate contact details from user input and store structured status. "
                "Current known state: {user_input}"
            ),
        ),
        ScorerAgent(
            name="ScorerAgent",
            output_key="lead_score",
            instructions=(
                "Read prior validation from {lead_status}. "
                "Score lead 1-10 using intent and contact validity."
            ),
        ),
        EmailerAgent(
            name="EmailerAgent",
            output_key="email_draft",
            instructions="Use {lead_score} and {lead_status}. Draft outreach only when lead score > 7.",
        ),
    ]
    return SequentialAgent(agents=agents, tool_registry=tools), adk_bridge


def main() -> None:
    pipeline, adk_bridge = build_pipeline()
    print(f"[Runtime] {adk_bridge.summary()}")

    scenarios = [
        (
            "Valid email + high intent",
            "Hi I'm Sam, my email is sam@example.com. I need a demo and price quote urgently.",
        ),
        (
            "Invalid email/phone + low intent",
            "hello just browsing, email me at not-an-email and call at 12-34",
        ),
        (
            "Phone only + medium intent",
            "Hi, call me at +1 (415) 555-2671. Interested in options.",
        ),
    ]

    for idx, (label, user_text) in enumerate(scenarios, start=1):
        print("\n" + "=" * 80)
        print(f"Run {idx}: {label}")
        print(f"Input: {user_text}")
        pipeline.run(user_text)


if __name__ == "__main__":
    main()
