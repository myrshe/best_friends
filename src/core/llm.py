import json
import re
import httpx
import logging
from typing import Optional
from src.config import settings

logger = logging.getLogger(__name__)


def call_llm(
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.1,
        timeout: float = 90.0
) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "options": {
            "temperature": temperature,
            "num_predict": 512,
            "keep_alive": "10m"
        },
        "stream": False
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
        raise RuntimeError(f"Ollama HTTP {e.response.status_code}") from e
    except Exception as e:
        logger.error(f"Ollama request failed: {e}")
        raise RuntimeError(f"Ollama error: {e}") from e


def parse_json_response(text: str) -> dict:
    try:
        clean = text.strip()
        clean = re.sub(r'^```(?:json)?\s*', '', clean)
        clean = re.sub(r'\s*```$', '', clean).strip()
        return json.loads(clean)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except:
                pass
        raise ValueError(f"Failed to parse JSON: {text[:300]}...")