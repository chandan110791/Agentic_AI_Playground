from google.adk.agents import LlmAgent
from google.adk.tools.callback_context import CallbackContext
from google.adk.models import LlmRequest,LlmResponse
from datetime import datetime

def before_model_callback(text:str,model_req:LlmRequest):
    """
     before_model_callback called before exectuing the agent 
    
    Args:
        :param text: Description
        :type text: str
        :param callback_context: callback context to retrive vairables from state
    """
    try :
        retricted_content= ["personal","profanity","fraud","account","sucks"]
        #get the content 
        if model_req and model_req.contents and model_req.content.parts:
            for content in reversed(model_req.content):
                for part in model_req.content.parts:
                    if hasattr(part,text) and hasattr.part[0].text:
                        if hasattr.part[0].text.lower() in retricted_content:
                            return {"message":"I cant serve with restrcited content.please refreame"}
        else:
            return None
    except Exception as e:
        print("exception as {e}")
    
import re
Replacement={"placement":"offer"}

def replacement(m:re.Match):
    """
        replacement function 
    """
    match = m.group(0)
    replace = Replacement.get(match.lower())
    if match.isupper():
        return replace.upper()
    elif match[:1].isupper() and match[1:].islower()
        return (replace[:1].upper() +""+ replace[1:].lowerpper()) 
    else:
        return replace
    
PATTERN = re.compile("\b("+"|".join(Replacement.keys()) +")\b")

import copy
from google.genai import types  # Content / Part types
def after_model_callback(text:str,model_res:LlmResponse):
    """
     after agent callback called before exectuing the agent 
    
    Args:
        :param text: Description
        :type text: str
        :param callback_context: callback context to retrive vairables from state
    """
    try :
        #get the content 
        if model_res and model_res.Content and model_res.Content.parts:
            modified_copy=copy.deepcopy(model_res.Content.parts)
            for idx,part in enumerate(modified_copy):
                    if hasattr(part,text) and part[0].text:  
                        new_text,n = PATTERN.subn(replacement,part[0].text.lower())
                        if n>0:
                            modified_copy[idx].text = new_text

            return{LlmResponse(content = types.Content(parts=modified_copy,role="model"))}
        else:
            return None
    except Exception as e:
        print("exception as {e}")
    
model_callback_ex = LlmAgent(name="agentcallbacks",model="",instruction="You are a LLM.We are here to demonstrate agent callbacks. You have below tool available to calulcate the share the counter and ",
                                description="agent to demonstarte agent callback",before_model_callback=[before_model_callback],after_model_callback=[after_model_callback])