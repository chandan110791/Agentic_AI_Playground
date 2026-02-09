from google.adk.agents import LlmAgent

from datetime import datetime
from google.adk.tools.tool_context import ToolContext

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

from typing import Dict,Any
def exit_loop(tool_context:ToolContext) -> Dict[str,Any]:
    """
        Function to exit the loop
        args:
         Tool context with access to the state

        return : Empty Dictionary
    """
    print("Exiting")
    tool_context.actions.escalate = True
    return {"message":"Exiting"}


review_agent = LlmAgent(model="gemini-2.0-flash",name="review_agent",description="Agent to generate review for linkedin post",
                            instruction="""
                                You are an expert in reviwing Linkedin posts.
                                Review a linkedin post containing the course contents of course for AI from Mr.ABC.
                                Please consider below points while reviwing the content:
                                - Do keep and eye for tone and length

                                You have access to below information:
                                - generated content {generated_content}

                                You have access to below tool for validating content size:
                                - review_push_suggestions 

""",tools=[review_push_suggestions,exit_loop],output_key="suggestion")