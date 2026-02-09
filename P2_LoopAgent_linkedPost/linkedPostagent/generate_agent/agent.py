from google.adk.agents import LlmAgent

from datetime import datetime
# from google.adk.tools.tool_context import ToolContext

def generate_time()->dict:
    return {"current_time":datetime.now().strftime("%y-%m-%d %h:$m")}

generate_agent = LlmAgent(model="gemini-2.0-flash",name="generate_agent",description="Agent to generate review for linkedin post",
                            instructions="""
                                You are an expert in generating Linked in posts.
                                Generate a linkedin post for appreciating the course contents of course for AI from Mr.ABC.
                                Please consider below points while generating the content:
                                - Do not include any hate speech and critise any other person,content or company
                                - Do maintain a professional tone while generating reviews
                                - Do include current time while generating content

                                You have access to below information:
                                - current time {current_time}

""",tool=[generate_time],output_key="generated_content")