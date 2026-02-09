from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from typing import Optional
from google.genai import types
from datetime import datetime

def before_agent_callback(text:str,callback_context:CallbackContext)->Optional[types.Content]:
    """
     before_agent_callback called before exectuing the agent 
    
    Args:
        :param text: Description
        :type text: str
        :param callback_context: callback context to retrive vairables from state
    """
    try :
        timestart = datetime.now().strftime("%y-%m-%d %h-%s")
        if callback_context and callback_context.state:
            callback_context.state["timestart"]=timestart
            if callback_context.state["counter"]:
                currentcounter=callback_context.state["counter"]
                callback_context.state["counter"]= int(currentcounter)+1
            else:
                callback_context.state["counter"]= 1
            return {"message":f"set the counter to {callback_context.state["counter"]} and timestamp"}
        
        else: 
            return {"message":f" callback context is empty"}
    except Exception as e:
        print("exception as {e}")
    

def after_agent_callback(text:str,callback_context:CallbackContext)->Optional[types.Content]:
    """
     after agent callback called before exectuing the agent 
    
    Args:
        :param text: Description
        :type text: str
        :param callback_context: callback context to retrive vairables from state
    """
    try :
        end_timestart = datetime.now().strftime("%y-%m-%d %h-%s")
        diff = 0
        if callback_context and callback_context.state:
            if callback_context.state["timestart"]:
              diff = end_timestart - callback_context.state["timestart"]
            return {"message":f"set the counter to {callback_context.state["counter"]} and timestamp","timedifference":diff,"counter":{callback_context.state["counter"]}}
        else: 
            return {"message":f" callback context is empty"}
    except Exception as e:
        print("exception as {e}")
    



agent_callback_ex = LlmAgent(name="agentcallbacks",model="",instruction="You are a LLM.We are here to demonstrate agent callbacks. You have below tool available to calulcate the share the counter and ",
                                description="agent to demonstarte agent callback",before_agent_callback=[before_agent_callback],after_agent_callback=[after_agent_callback])