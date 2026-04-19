# src/main.py
import time
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.models import ChatRequest, ChatResponse
from src.agents.graph import app_graph
from src.agents.state import AgentState
from src.core.memory import save_session_message
from src.core.observability import log_request, log_response, inc_metric
from src.core.observability_ot import setup_observability
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Course AI Assistant", version="1.0")

setup_observability(app)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    start_time = time.time()
    log_request(req.session_id, req.query)

    try:
        initial_state: AgentState = {
            "query": req.query,
            "session_id": req.session_id,
            "topic": "", "level": "beginner", "language": "ru",
            "context": [], "draft": "", "final_answer": "",
            "confidence": 0.0, "status": "new", "retry_count": 0,
            "clarification_question": None, "sources": []
        }

        print(f"\nDEBUG: Запуск графа для: {req.query[:50]}...")
        result = app_graph.invoke(initial_state)

        def safe_get(data, keys, default=""):
            if not isinstance(data, dict): return default
            for k in keys if isinstance(keys, list) else [keys]:
                if k in data: return data[k]
            return default

        answer = safe_get(result, ["final_answer", "answer"], "Ошибка: пустой ответ")
        sources = safe_get(result, ["sources"], [])
        confidence = safe_get(result, ["confidence"], 0.0)
        status = safe_get(result, ["status"], "unknown")
        topic = safe_get(result, ["topic", "router_topic"], "unknown")
        level = safe_get(result, ["level", "router_level"], "beginner")

        try:
            confidence = float(confidence)
        except:
            confidence = 0.0
        if not isinstance(sources, list): sources = []

        latency = (time.time() - start_time) * 1000
        log_response(req.session_id, answer, sources, confidence, latency)
        inc_metric("requests_total")
        inc_metric("responses_total")
        inc_metric("latency_ms", latency)
        if status == "fallback": inc_metric("fallbacks_total")

        return ChatResponse(
            answer=answer, sources=sources, confidence=confidence,
            status=status, topic=topic, level=level
        )

    except Exception as e:
        logger.error(f"CRITICAL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
