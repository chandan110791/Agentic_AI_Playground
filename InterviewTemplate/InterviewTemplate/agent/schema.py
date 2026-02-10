"""
Pydantic schemas for agent tools.

Define your tool input and output models here for type safety and validation.
The LLM uses field descriptions to understand what each parameter does.

Example:
    class MyToolInput(BaseModel):
        param: str = Field(..., description="What this parameter does")
    
    class MyToolOutput(BaseModel):
        result: str
"""

from pydantic import BaseModel, Field

# Define your tool schemas here

