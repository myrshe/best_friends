import os
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from src.agents.state import AgentState
from src.agents.skills import execute_skill
from src.core.llm import call_llm, parse_json_response
from src.config import settings
from src.core.memory import get_session_context

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("course-ai-assistant.agents")


def load_prompt(filename: str) -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", filename)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def router_node(state: AgentState) -> dict:
    with tracer.start_as_current_span("router_node") as span:
        span.set_attribute("agent.step", "classify")
        span.set_attribute("input.query", state["query"])
        try:
            prompt_template = load_prompt("router.md")
            prompt = prompt_template.format(query=state["query"])
            resp = call_llm(prompt, json_mode=True, temperature=0.0)
            parsed = parse_json_response(resp)

            result = {
                "topic": parsed.get("topic", "other"),
                "level": parsed.get("level", "beginner"),
                "language": parsed.get("language", "ru"),
                "status": "routed"
            }
            span.set_attributes(result)
            span.set_status(Status(StatusCode.OK))
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error(f"Router failed: {e}")
            return {"status": "fallback", "topic": "unknown", "level": "unknown"}


def researcher_node(state: AgentState) -> dict:
    with tracer.start_as_current_span("researcher_node") as span:
        span.set_attribute("agent.step", "search")
        span.set_attribute("input.topic", state["topic"])
        span.set_attribute("input.level", state["level"])
        try:
            history = get_session_context(state["session_id"])
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-3:]])
            enhanced_query = f"Предыдущий контекст: {history_text}\nТекущий вопрос: {state['query']}"

            chunks_result = execute_skill(
                skill_name="search_knowledge_base",
                inputs={"query": enhanced_query, "topic": state["topic"], "level": state["level"]},
                config={
                    "qdrant_url": settings.QDRANT_URL,
                    "ollama_url": settings.OLLAMA_BASE_URL,
                    "embedding_model": settings.EMBEDDING_MODEL,
                    "collection": settings.QDRANT_COLLECTION,
                    "top_k": settings.SEARCH_TOP_K
                }
            )
            span.set_attribute("output.chunks_count", len(chunks_result.get("chunks", [])))
            span.set_status(Status(StatusCode.OK))
            return {"context": chunks_result.get("chunks", [])}
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            return {"context": []}


def check_context_node(state: AgentState) -> dict:
    with tracer.start_as_current_span("check_context_node") as span:
        span.set_attribute("agent.step", "evaluate")
        try:
            eval_result = execute_skill(
                skill_name="evaluate_context",
                inputs={"chunks": state["context"], "query": state["query"]},
                config={}
            )
            status = eval_result.get("status", "insufficient")
            avg_score = eval_result.get("avg_score", 0.0)

            span.set_attribute("output.status", status)
            span.set_attribute("output.avg_score", avg_score)

            if status == "sufficient":
                span.set_status(Status(StatusCode.OK))
                return {"status": "researched", "retry_count": state["retry_count"]}
            elif state["retry_count"] < 1:
                return {"status": "retry_search", "retry_count": state["retry_count"] + 1}
            else:
                span.set_status(Status(StatusCode.ERROR, "Context insufficient after retry"))
                return {"status": "fallback"}
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            return {"status": "fallback"}


def tutor_node(state: AgentState) -> dict:
    with tracer.start_as_current_span("tutor_node") as span:
        span.set_attribute("agent.step", "generate")
        try:
            context_text = "\n---\n".join([f"[{i + 1}] {c['text']}" for i, c in enumerate(state["context"])])
            prompt_template = load_prompt("tutor.md")
            prompt = prompt_template.format(
                context=context_text,
                query=state['query'],
                level=state['level']
            )
            resp = call_llm(prompt, json_mode=True, temperature=0.1)
            parsed = parse_json_response(resp)

            result = {
                "final_answer": parsed.get("answer", "Не удалось сформировать ответ."),
                "sources": parsed.get("sources", []),
                "confidence": parsed.get("confidence", 0.5),
                "status": "approved"
            }
            span.set_attribute("output.confidence", result["confidence"])
            span.set_attribute("output.sources_count", len(result["sources"]))
            span.set_status(Status(StatusCode.OK))
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            return {"final_answer": "Ошибка генерации ответа.", "sources": [], "confidence": 0.0, "status": "fallback"}


def fallback_node(state: AgentState) -> dict:
    with tracer.start_as_current_span("fallback_node") as span:
        span.set_attribute("agent.step", "fallback")
        span.set_status(Status(StatusCode.ERROR, "Fallback triggered"))
        return {
            "final_answer": "К сожалению, я не нашёл достаточной информации по вашему вопросу в базе знаний. Попробуйте переформулировать или уточнить тему.",
            "sources": [],
            "confidence": 0.0,
            "status": "fallback"
        }


def route_after_check(state: AgentState) -> str:
    if state["status"] == "researched":
        return "tutor"
    elif state["status"] == "retry_search":
        return "researcher"
    return "fallback"

workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("check_context", check_context_node)
workflow.add_node("tutor", tutor_node)
workflow.add_node("fallback", fallback_node)

workflow.set_entry_point("router")
workflow.add_edge("router", "researcher")
workflow.add_edge("researcher", "check_context")
workflow.add_conditional_edges(
    "check_context",
    route_after_check,
    {"tutor": "tutor", "researcher": "researcher", "fallback": "fallback"}
)
workflow.add_edge("tutor", END)
workflow.add_edge("fallback", END)

app_graph = workflow.compile()