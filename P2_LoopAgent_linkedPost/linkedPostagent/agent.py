from google.adk.agents import SequentialAgent,LoopAgent
from .generate_agent import generate_agent
from .review_agent import review_agent
from .refine_agent import refine_agent


review_refine_agent=LoopAgent(name="review_refine_agent",description="loop agent to review and refine the reviews " \
                                    "untill acceptable conditions ar met" ,sub_agents= [review_agent,refine_agent])

root_agent_sequential=SequentialAgent(name="root_agent_workflow",description="this is a root agent ,it directs the workflow to generate a review," \
                                        "review the generated review and refine it untill conditions are met",
                                      sub_agents=[generate_agent,review_refine_agent])