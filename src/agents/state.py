from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    query: str
    session_id: str
    topic: str
    level: str
    language: str
    context: List[Dict[str, Any]]
    draft: str
    final_answer: str
    confidence: float
    status: str
    retry_count: int
    clarification_question: Optional[str]
    sources: List[str]