from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000, description="Вопрос по курсу")
    session_id: str = Field(default="default", description="ID сессии для памяти")

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = Field(default_factory=list, description="Источники из KB")
    confidence: float = Field(ge=0.0, le=1.0, description="Уверенность агента")
    status: str
    topic: Optional[str] = None
    level: Optional[str] = None

class AgentStateData(BaseModel):
    query: str
    session_id: str
    topic: str = ""
    level: str = "beginner"
    language: str = "ru"
    context: List[dict] = Field(default_factory=list)
    draft: str = ""
    final_answer: str = ""
    confidence: float = 0.0
    status: str = "new"
    retry_count: int = 0
    clarification_question: Optional[str] = None