from google.adk.agents import LlmAgent


generate_agent = LlmAgent(model="gemini-2.0-flash",name="generate_agent",description="Agent to generate review for linkedin post",
                            instructions="""
                                You are an expert in refining Linkedin posts.
                                Refine a linkedin post containing the course contents of course for AI from Mr.ABC.
                                Please consider below points while refining the content:
                                - Do keep and eye for tone and length

                                You have access to below information:
                                - current time {current_time}
                                - generated content  {generated_content}
                                - suggestions {suggestion}


""",output_key="refined_content")