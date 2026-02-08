"""
Main Class to run the agent with persistent storage
"""

import time
import asyncio
import uuid
import os
from dotenv import load_dotenv
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Verify API credentials are set
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ ERROR: GOOGLE_API_KEY environment variable not set!")
    print("Please create a .env file or set GOOGLE_API_KEY")
    exit(1)

print("✅ API credentials loaded")

# Fast imports - these don't cause slowness
_sessions_loaded = False
_agent_loaded = False
_runner_loaded = False
DatabaseSessionService = None
memory_agent = None
Runner = None

def _ensure_sessions_loaded():
    """Lazy load google.adk.sessions on first use"""
    global _sessions_loaded, DatabaseSessionService
    if not _sessions_loaded:
        load_start = time.time()
        from google.adk.sessions import DatabaseSessionService as _DB
        DatabaseSessionService = _DB
        _sessions_loaded = True
        print(f"[LAZY LOAD] Sessions imported in {time.time() - load_start:.2f}s")
    return DatabaseSessionService

def _ensure_agent_loaded():
    """Lazy load memory_agent on first use"""
    global _agent_loaded, memory_agent
    if not _agent_loaded:
        from memory_agent.agent import memory_agent as _agent
        memory_agent = _agent
        _agent_loaded = True
    return memory_agent

def _ensure_runner_loaded():
    """Lazy load Runner on first use"""
    global _runner_loaded, Runner
    if not _runner_loaded:
        from google.adk.runners import Runner as _Runner
        Runner = _Runner
        _runner_loaded = True
    return Runner

#load_dotenv()
db_url = "sqlite:///./my_agent_data.db"

# Defer session service creation until needed
session_service = None

app_name="MemoerTes"
initial_state={
    "user_name":"Tummy",
    "favouritelist":"Likes to eat , sleep and code",
    "reminders" : []
}

user_id = "Chands"

from google.genai import types 

async def call_asynch_message_process(runner,sessionid,usermessage:str,user_id:str):
        """
        Docstring for call_asynch_message_process
        
        :param runner: Description
        :param sessionid: Description
        :param usermessage: Description
        :type usermessage: str
        """
        try:
            start_time = time.time()
            Content = types.Content(parts=[types.Part(text=usermessage)],role="user")
            print(f"content {Content}")
            print(f"[TIMING] Starting run_async at {start_time}")

            response_start = time.time()
            async for event in runner.run_async(
                session_id=sessionid,new_message=Content,user_id=user_id):
                await display(event)
        except Exception as e:
             print(f"error during req :: {e}")




async def display_state(session_service,app_name,user_id,session_id):
    """
    Display the current state of the session for the given app and user.
    Args:
        session_service: The session service to retrieve the session from
        app_name: The name of the application
        user_id: The ID of the user
    Returns:
        None
    """
    try:
        session = session_service.get_session(app_name=app_name,user_id=user_id,session_id=session_id)
        reminders = session.state.get("reminders",[])
        for idx,reminder in enumerate(reminders):
            print(f"{idx+1}::{reminder}")
    except Exception as e:
         print(f"error :: {e} ")


                

async def display(event):
    """
        Display the content of an event, including text, tool responses, and code execution results.

        Args:
            event: The event object to display content from.
        Returns:
            None

    """
    try :
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part,"executable_code") and part.executable_code:
                        print(f"executable_code Instructions: {part.executable_code}")
                elif hasattr(part,"code_execution_result") and part.code_execution_result:
                        print(f"executable_code Instructions: {part.code_execution_result.output}")
                elif hasattr(part,"tool_response") and part.tool_response:
                        print(f"🔧 Tool response: {part.tool_response.output}")
                elif hasattr(part,"function_call") and part.function_call:
                        # Handle function/tool calls
                        print(f"🔧 Calling tool: {part.function_call.name}")
                        if hasattr(part.function_call, "args"):
                            print(f"   Args: {part.function_call.args}")
                elif hasattr(part,"text") and part.text:
                        print(f"💬 Text: {part.text.strip()}") 

            if event.is_final_response():
                if event.content and event.content.parts and hasattr(event.content.parts[0],"text") and event.content.parts[0].text:
                        print(f"Final response: {event.content.parts[0].text}")

    except Exception as e:
         print(f" exception as {e}")


async def main():
    global session_service
    
    print("[TIMING] Starting main()")
    print("[LAZY LOAD] Loading dependencies on first use...")
    
    # Load sessions service (this triggers the slow import)
    session_start = time.time()
    DB_Service = _ensure_sessions_loaded()
    session_service = DB_Service(db_url=db_url)
    print(f"[TIMING] Session service initialized in {time.time() - session_start:.2f}s")
    
    query_start = time.time()
    sessions = session_service.list_sessions(app_name=app_name,user_id=user_id)
    print(f"[TIMING] list_sessions query took {time.time() - query_start:.2f}s")

    if sessions and len(sessions.sessions) > 0:
        session_id = sessions.sessions[0].id
        print(f"[TIMING] Using existing session{session_id}")
    else:
        create_start = time.time()
        session_id = session_service.create_session(app_name=app_name,user_id=user_id,state=initial_state)
        print(f"[TIMING] create_session took {time.time() - create_start:.2f}s")


    runner_start = time.time()
    RunnerClass = _ensure_runner_loaded()
    agent = _ensure_agent_loaded()
    Runner = RunnerClass(agent=agent,app_name=app_name,session_service=session_service)
    print(f"[TIMING] Runner initialization took {time.time() - runner_start:.2f}s")
    
    while True:

        usermessage = input("Type here: ")
        if usermessage.lower() in ["end","exit"]:
            print("Good bye")
            break
        await display_state(session_service,app_name,user_id,session_id)
        await call_asynch_message_process(Runner,session_id,usermessage,user_id)
        await display_state(session_service,app_name,user_id,session_id)



if __name__== "__main__":
    asyncio.run(main())