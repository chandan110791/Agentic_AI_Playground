from google.adk.agents import LlmAgent

from datetime import datetime
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

def review_push_suggestions(text:str,tool_context:ToolContext)->dict:
    """
        Review the text generated and update state with oberved suggestions.
        Args:
            toolcontext to get the generated content 
        
        Returns:
            dictionary with suggestions after parsing the text generated
        
    """
    len_generated  = 0
    diff = 0
    MAX_LENGTH = 1000
    MIN_LENGTH = 500
    try:
        text_generated = (text or "").strip()
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
        else:
            tool_context.state["review_status"]="Fail"
            return {"suggestion":"text is empty, please generate some content"}
    except Exception as e:
        print(f"error while accessing content generated{e}")


def exit_loop(tool_context: ToolContext) -> Dict[str, Any]:
    tool_context.actions.escalate = True
    return {}


review_agent = LlmAgent(model="gemini-2.0-flash",name="review_agent",description="Agent to generate review for linkedin post",
                            instruction="""
                            You are a LinkedIn Post Quality Reviewer.

    Your task is to evaluate the quality of a LinkedIn post about Agent Development Kit (ADK).
    
    ## EVALUATION PROCESS
    1. Use the count_characters tool to check the post's length.
       Pass the post text directly to the tool.
    
    2. If the length check fails (tool result is "fail"), provide specific feedback on what needs to be fixed.
       Use the tool's message as a guideline, but add your own professional critique.
    
    3. If length check passes, evaluate the post against these criteria:
       - REQUIRED ELEMENTS:
         1. Mentions @aiwithbrandon
         2. Lists multiple ADK capabilities (at least 4)
         3. Has a clear call-to-action
         4. Includes practical applications
         5. Shows genuine enthusiasm
       
       - STYLE REQUIREMENTS:
         1. NO emojis
         2. NO hashtags
         3. Professional tone
         4. Conversational style
         5. Clear and concise writing
    
    ## OUTPUT INSTRUCTIONS
    IF the post fails ANY of the checks above:
      - Return concise, specific feedback on what to improve
      
    ELSE IF the post meets ALL requirements:
      - Call the exit_loop function
      - Return "Post meets all requirements. Exiting the refinement loop."
      
    Do not embellish your response. Either provide feedback on what to improve OR call exit_loop and return the completion message.
    
    ## POST TO REVIEW
    {generated_content}""",
                            tools=[review_push_suggestions,exit_loop],output_key="suggestion_to_refine",)