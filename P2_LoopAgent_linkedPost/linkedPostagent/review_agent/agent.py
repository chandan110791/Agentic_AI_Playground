from google.adk.agents import LlmAgent

from datetime import datetime
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

def review_push_suggestions(text:str,tool_context:ToolContext)->dict:
    """
        Review the text generated and share the required suggestions back to state
        Args:
            toolcontext to get the generated content 
        
            Returns:
            dictionary with suggestions after parsing the text generated
        
    """
    text_generated = text
    len_generated  = 0
    diff = 0
    MAX_LENGTH = 1000
    MIN_LENGTH = 500
    try:
        if text_generated and len(text_generated)>0:
            len_generated = len(text_generated)
            if len_generated > MAX_LENGTH:
                diff = int(len_generated) - int(MAX_LENGTH)
                tool_context.state["review_status"]="Fail"
                return {"suggestion":f"text is long,decrease it by {diff} character to match maxlength of {MAX_LENGTH}"}
            elif len_generated < MIN_LENGTH:
                 tool_context.state["review_status"]="Fail"
                 diff = int(MIN_LENGTH) - int(len_generated)
                 return {"suggestion":f"text is short,increase it by {diff} character to match minlength of {MIN_LENGTH}"}
            else:
                  tool_context.state["review_status"]="Pass"
                  return {"suggestion":f"text is fine, no change in length required, its between   maxlength of {MAX_LENGTH} and minlength of {MIN_LENGTH}"}
        
    except Exception as e:
        print(f"error while accessing content generated{e}")


def exit_loop(tool_context: ToolContext) -> Dict[str, Any]:
    tool_context.actions.escalate = True
    return {}


review_agent = LlmAgent(model="gemini-2.0-flash",name="review_agent",description="Agent to generate review for linkedin post",
                            instruction="""
                            Generated content:
                            {generated_content}

                            Call `review_push_suggestions` with:
                            - text = the full generated content above

                            If the tool sets review_status to Pass, you MUST call `exit_loop` immediately.
                            If review_status is Fail, do NOT call exit_loop.

                            Return a short confirmation only.

""",tools=[review_push_suggestions,exit_loop],output_key="suggestion_to_refine")