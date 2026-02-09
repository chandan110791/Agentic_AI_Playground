"""
The agent shocases callabcks
"""

from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import  BaseTool
from datetime import datetime
from typing import Dict

# --- Define a Simple Tool Function ---
def get_capital_city(country: str) -> Dict[str, str]:
    """
    Retrieves the capital city of a given country.

    Args:
        country: Name of the country

    Returns:
        Dictionary with the capital city result
    """
    print(f"[TOOL] Executing get_capital_city tool with country: {country}")

    country_capitals = {
        "united states": "Washington, D.C.",
        "usa": "Washington, D.C.",
        "canada": "Ottawa",
        "france": "Paris",
        "germany": "Berlin",
        "japan": "Tokyo",
        "brazil": "Brasília",
        "australia": "Canberra",
        "india": "New Delhi",
    }

    # Use lowercase for comparison
    result = country_capitals.get(country.lower(), f"Capital not found for {country}")
    print(f"[TOOL] Result: {result}")
    print(f"[TOOL] Returning: {{'result': '{result}'}}")

    return {"result": result}

from typing import Any
def before_tool_callback(tool:BaseTool,args:Dict[str,Any],tool_context:ToolContext):
    """
     before_agent_callback called before exectuing the agent 
    
    Args:
        :param text: Description
        :type text: str
        :param callback_context: callback context to retrive vairables from state
    """
    try :
        timestart = datetime.now().strftime("%y-%m-%d %h-%s")
        if tool.name == "get_capital_city" and tool_context and tool_context.state:
            if (tool_context.state["country"]=="US"):
                tool_context.state["country"]=="America"
            return {"message":f"updated for US"}
        else: 
            return {"message":f" callback context is empty"}
    except Exception as e:
        print("exception as {e}")
    

def after_tool_callback(tool:BaseTool,args:Dict[str,Any],tool_context:ToolContext,tool_result:dict):
    """
     before_agent_callback called before exectuing the agent 
    
    Args:
        :param text: Description
        :type text: str
        :param callback_context: callback context to retrive vairables from state
    """
    try :
        timestart = datetime.now().strftime("%y-%m-%d %h-%s")
        if  tool.name == "get_capital_city" and tool_context and tool_context.state:
            if (tool_result["result"]=="USD"):
                tool_result["result"]=="Dollar"
            return {"message":f"updated for US"}
        else: 
            return {"message":f" callback context is empty"}
    except Exception as e:
        print("exception as {e}")


tool_callback_ex = LlmAgent(name="agentcallbacks",model="",instruction="You are a LLM.We are here to demonstrate agent callbacks. You have below tool available to calulcate the share the counter and ",
                                description="agent to demonstarte agent callback",before_tool_callback=[before_tool_callback],after_tool_callback=[after_tool_callback],tools=[get_capital_city])