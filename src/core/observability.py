import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("agent_observability")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_DIR / "agent.log", encoding="utf-8", mode="a")
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)

def log_request(session_id: str, query: str, metadata: Optional[Dict[str, Any]] = None):
    entry = {
        "type": "request",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "query": query,
        "metadata": metadata or {}
    }
    logger.info(json.dumps(entry, ensure_ascii=False))

def log_response(session_id: str, answer: str, sources: list, confidence: float, latency_ms: float):
    entry = {
        "type": "response",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "answer_preview": answer[:200] + "..." if len(answer) > 200 else answer,
        "sources": sources,
        "confidence": confidence,
        "latency_ms": round(latency_ms, 2)
    }
    logger.info(json.dumps(entry, ensure_ascii=False))

def log_agent_step(step_name: str, state: Dict[str, Any]):
    entry = {
        "type": "agent_step",
        "timestamp": datetime.now().isoformat(),
        "step": step_name,
        "state_summary": {k: v for k, v in state.items() if k in ["query", "topic", "status", "retry_count"]}
    }
    logger.debug(json.dumps(entry, ensure_ascii=False))

_metrics = {
    "requests_total": 0,
    "responses_total": 0,
    "fallbacks_total": 0,
    "avg_latency_ms": 0.0,
    "_count": 0
}

def inc_metric(name: str, value: float = 1.0):
    if name in _metrics:
        _metrics[name] += value
        if name == "latency_ms":
            _metrics["_count"] += 1
            _metrics["avg_latency_ms"] = (
                _metrics["avg_latency_ms"] * (_metrics["_count"] - 1) + value
            ) / _metrics["_count"]

def get_metrics() -> Dict[str, Any]:
    return {k: v for k, v in _metrics.items() if not k.startswith("_")}