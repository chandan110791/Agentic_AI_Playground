"""
Simple Before/After Model Callbacks (ADK) using regex + subn

Goal:
- before_model_callback: log the last user message + optionally block certain words
- after_model_callback: do simple word replacements using regex.subn (efficient + tells count)

NOTE:
- This uses `instruction=` (singular), which matches the ADK version you hit earlier
  (where `instructions=` caused a Pydantic "extra_forbidden" error).
"""

# --- Standard libs ---
import re  # regex support (compile/search/sub/subn)
import copy  # deep copy parts safely (avoid mutating original response object)
from datetime import datetime  # timestamps for logging
from typing import Optional  # return type can be LlmResponse or None

# --- ADK / Gemini types ---
from google.adk.agents import LlmAgent  # the ADK agent class
from google.adk.agents.callback_context import CallbackContext  # callback context (state, agent_name)
from google.adk.models import LlmRequest, LlmResponse  # request/response wrapper types
from google.genai import types  # Content / Part types


# -----------------------------
# 1) Regex replacement setup
# -----------------------------

REPLACEMENTS = {  # map of words you want to replace (keys must be lowercase)
    "problem": "challenge",
    "difficult": "complex",
}

# Build a word-boundary pattern like: r"\b(problem|difficult)\b" (case-insensitive)
_PATTERN = re.compile(  # compile once for efficiency
    r"\b(" + "|".join(map(re.escape, REPLACEMENTS.keys())) + r")\b",  # safe join of keys
    re.IGNORECASE,  # match any casing (Problem/PROBLEM/problem)
)


def _match_case(src: str, dst: str) -> str:
    """Match replacement casing to the original token (simple heuristics)."""
    if src.isupper():  # if original is ALL CAPS
        return dst.upper()  # make replacement ALL CAPS
    if src[:1].isupper():  # if original is Title Case (first letter uppercase)
        return dst.capitalize()  # make replacement Title Case
    return dst  # otherwise keep replacement lowercase


def _repl(m: re.Match) -> str:
    """Regex replacement function used by subn; preserves casing."""
    original = m.group(0)  # the exact matched text as it appears in the response
    base = REPLACEMENTS[original.lower()]  # lookup replacement using lowercase key
    return _match_case(original, base)  # adjust casing to match original


# -----------------------------
# 2) BEFORE callback (optional)
# -----------------------------

def before_model_callback(
    callback_context: CallbackContext,  # gives you .state and .agent_name
    llm_request: LlmRequest,            # request that will be sent to the model
) -> Optional[LlmResponse]:
    """
    Runs before the model call.

    - Logs last user message
    - Example: blocks if user message contains a prohibited word
    - Returns:
        None -> allow model call
        LlmResponse -> skip model call and use this response instead
    """
    state = callback_context.state  # persistent session state dict
    agent_name = callback_context.agent_name  # name of agent running the callback

    last_user_message = ""  # default if we can't find a user message

    # Walk the request contents from newest to oldest to find the last user text message
    if llm_request.contents:  # ensure list exists / not empty
        for content in reversed(llm_request.contents):  # search backwards for the latest user content
            if content.role == "user" and content.parts:  # must be user role and have parts
                # Find the first text part (don’t assume index 0 is always text)
                for part in content.parts:  # iterate parts safely
                    if hasattr(part, "text") and part.text:  # text part found
                        last_user_message = part.text  # capture it
                        break  # stop scanning parts
                if last_user_message:  # if we found a message, stop scanning contents
                    break

    # Log basic info
    print("=== MODEL REQUEST STARTED ===")  # marker
    print(f"Agent: {agent_name}")  # which agent is calling the model
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")  # timestamp

    if last_user_message:  # if we found a message
        print(f"User message: {last_user_message[:120]}")  # log truncated message
        state["last_user_message"] = last_user_message  # store it for later debugging
    else:
        print("User message: <empty>")  # no user message found

    # Example block: if message contains a prohibited word
    if last_user_message and "sucks" in last_user_message.lower():  # simple check
        print("=== INAPPROPRIATE CONTENT BLOCKED ===")  # marker
        return LlmResponse(  # return a response to bypass the model
            content=types.Content(  # build a Content object
                role="model",  # model role
                parts=[types.Part(text="Please rephrase without inappropriate language.")],  # text response
            )
        )

    # Record start time (optional)
    state["model_start_time"] = datetime.now()  # store start time in state
    print("[BEFORE MODEL] ✓ Request approved")  # marker

    return None  # allow normal model request


# -----------------------------
# 3) AFTER callback (subn-based)
# -----------------------------

def after_model_callback(
    callback_context: CallbackContext,  # context/state if you need it
    llm_response: LlmResponse,          # model response you can optionally modify
) -> Optional[LlmResponse]:
    """
    Runs after the model call.

    Uses regex.subn (ONE pass) to replace words + get replacement count.
    Returns:
      - LlmResponse with modified content (if changes were made)
      - None (if no changes, keep original response)
    """
    print("[AFTER MODEL] Processing response")  # marker

    # If response has no content/parts, nothing to do
    if not llm_response or not llm_response.content or not llm_response.content.parts:
        return None  # keep original (which is empty anyway)

    # Copy parts so we don't mutate the original response object
    modified_parts = [copy.deepcopy(p) for p in llm_response.content.parts]  # deep copy each part
    modified_any = False  # track if any part changed

    # Process each part independently (avoids breaking multi-part responses)
    for i, part in enumerate(modified_parts):  # loop through all parts with index
        # Only modify text parts that contain non-whitespace content
        if hasattr(part, "text") and part.text and not part.text.isspace():
            # ---- KEEP subn as-is (core requirement) ----
            new_text, n = _PATTERN.subn(_repl, part.text)  # do replacements + get count
            # -------------------------------------------

            if n > 0:  # if at least one replacement happened
                modified_parts[i].text = new_text  # write back modified text
                modified_any = True  # mark that we changed something

    if modified_any:  # only override response if changes were made
        print("[AFTER MODEL] ↺ Modified response text")  # marker
        return LlmResponse(  # return a new response object
            content=types.Content(  # create new content
                role="model",  # model role
                parts=modified_parts,  # updated parts
            )
        )

    return None  # no changes -> keep original response


# -----------------------------
# 4) Create the agent
# -----------------------------

root_agent = LlmAgent(
    name="content_filter_agent",  # agent name
    model="gemini-2.0-flash",  # model id
    description="Agent demonstrating before/after callbacks with regex.subn",  # description
    instruction=(  # ADK expects 'instruction' in your version (not 'instructions')
        "You are a helpful assistant.\n"
        "- Answer user questions concisely\n"
        "- Be factual\n"
        "- Be respectful\n"
    ),
    before_model_callback=before_model_callback,  # attach before callback
    after_model_callback=after_model_callback,  # attach after callback
)
