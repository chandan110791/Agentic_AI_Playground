from google.adk.agents import LlmAgent

from datetime import datetime
from google.adk.tools.tool_context import ToolContext

def review_push_suggestions(toolcontext:ToolContext)->dict:
    """
        Review the text generated and share the required suggestions back to state
        Args:
            toolcontext to get the generated content 
        
            Returns:
            dictionary with suggestions after parsing the text generated
        
    """
    text_generated = toolcontext.state["generated_content"]
    len_generated  = 0
    diff = 0
    MAX_LENGTH = 1000
    MIN_LENGTH = 500
    try:
        if text_generated and len(text_generated)>0:
            len_generated = len(text_generated)
            if len_generated > MAX_LENGTH:
                diff = int(len_generated) - int(MAX_LENGTH)
                return {"suggestion":f"text is long,decrease it by {diff} character to match maxlength of {MAX_LENGTH}"}
            elif len_generated < MIN_LENGTH:
                diff = int(MIN_LENGTH) - int(len_generated)
                return {"suggestion":f"text is short,increase it by {diff} character to match minlength of {MIN_LENGTH}"}
            else:
                return {"suggestion":f"text is fine, no change in length required, its between   maxlength of {MAX_LENGTH} and minlength of {MIN_LENGTH}"}
        
    except Exception as e:
        print(f"error while accessing content generated{e}")


review_agent = LlmAgent(model="gemini-2.0-flash",name="review_agent",description="Agent to generate review for linkedin post",
                            instructions="""
                                You are an expert in reviwing Linkedin posts.
                                Review a linkedin post containing the course contents of course for AI from Mr.ABC.
                                Please consider below points while reviwing the content:
                                - Do keep and eye for tone and length

                                You have access to below information:
                                - generated content {generated_content}

                                You have access to below tool for validating content size:
                                - review_push_suggestions 

""",tool=[review_push_suggestions],output_key="suggestion")