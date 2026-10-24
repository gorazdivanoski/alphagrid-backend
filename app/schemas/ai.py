# Pydantic schemas for AI chat requests and responses,
# including user questions, previous analysis, and generated answers.

from pydantic import BaseModel
from typing import Optional

class AIChatRequest(BaseModel):
    question: str
    previous_analysis: Optional[str] = None

class AIChatResponse(BaseModel):
    answer: str