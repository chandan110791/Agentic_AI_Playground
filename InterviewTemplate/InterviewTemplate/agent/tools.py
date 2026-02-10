"""
Custom tools for the agent.

Tools are functions that the agent can call to perform specific tasks.
Each tool should be decorated with @adk.tool and use Pydantic models
for input and output to ensure type safety.

The LLM uses the function docstring and parameter descriptions to decide
when and how to call each tool.

Example:
    @adk.tool
    def my_tool(request: MyToolInput) -> MyToolOutput:
        '''Description of what this tool does.'''
        # Implementation
        return MyToolOutput(result="...")
"""

from google.generativeai import adk

# Define your tools here
from google.adk.tool_context import ToolContext

POSITIVE_PATTERN = ["yes","positive","proceed"]
NEGATIVE_PATTERN = ["no","negative","dont proceed"]


def process_user_request(text:str,tool_context:ToolContext)->dict:
    """
        - Understand a user’s travel request (destination, dates, budget, preferences).
        - Ask clarifying questions if required information is missing.
        Args:
            text: user input
            toolcontext to get the state 
        Returns  dictionary with parsed results
    """
    try:
        if tool_context and tool_context.state:
            destination = tool_context.get("destination","destination_is_null")
            dates = tool_context.get("dates","dates_is_null")
            budget = tool_context.get("budget","budget_is_null")
            preferences = tool_context.get("preferences","preferences_is_null")

            return {"validation_message":f" after parsing , we have values of slots as destination:{destination} \
                    dates:{dates} budget:{budget} preferences:{preferences} "}
    except Exception as e:
        print("exception caught in request as {e} ")
        return None


def confirm_travel_plan(text:str,tool_context:ToolContext)->dict:
    """
        - confirm a travel travel plan including flights, accommodation, and a simple itinerary.
        - Adapt recommendations when the user changes constraints.
        
        Args:
            text from LLM to parse
            tool context containing shared state variables
    """
    try:
            if tool_context and tool_context.state:
                user_response = tool_context.get("user_response","user_response_is_null")
                if user_response in POSITIVE_PATTERN:
                    return {"confirmation_message":f" after parsing , we have recieved user input as confirmation to procced , user_response:{user_response} "}
                elif user_response in NEGATIVE_PATTERN:
                    return {"confirmation_message":f" after parsing , we have recieved user input as deniel or not to proceed adapt reponse as per his recommendation, user_response:{user_response}. "}
                else:
                    return {"confirmation_message":f" we are not able to parse user response please ask user to answer in yes or no.If not the direction of improvement, user_response:{user_response}.U "}
    except Exception as e:
            print("exception caught in request as {e} ")
            return None