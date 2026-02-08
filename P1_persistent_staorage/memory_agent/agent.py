from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

def add_reminder(reminder:str,tool_context:ToolContext)->dict[str,any]:
    """
    add_reminder used to updated current reminder list and add new entries
    
    Args:
        :param reminder: new reminder to be added
        :param ToolSpecs: STate tool spec holding existing reminder

    Returns:
        A confirmation message
    """

    reminderList:list[str]=[]
    message:str=""
    try:
        if tool_context:
            reminderList=tool_context.state.get("reminders")
            reminderList.append(reminder)
            tool_context.state["reminders"]=reminderList
            message="reminder added"
        else:
            message="ToolSpecs empty"
        
        return {
            "reminder":tool_context.state["reminders"],
            "message":message
        }
    except Exception as e:
        print(f"error duing add_reminder:{e}")
        return {
             "message":f"error duing add_reminder:{e}"
        }

memory_agent=Agent(model="gemini-2.0-flash",
                   description="A smart agent with persistent memory",
                   instruction="""
                        You are a reminder assistant coach.
                        You need to perform below operations on reminder list.
                         - create or add reminders
                         - read reminders
                         - update reminders 
                         - delete a reminder using its index

                         You have access to below information:
                           - ReminderList : {reminders}
                           - User List : {user_name}

                        You have below tool availabe to make calls:
                            - add_reminder

                """,
                name="memory_agent",
                tools=[add_reminder],
                )

