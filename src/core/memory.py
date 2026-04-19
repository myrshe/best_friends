import json
import redis
from datetime import datetime, timedelta
from typing import List, Optional
from src.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def save_session_message(session_id: str, role: str, content: str):
    key = f"session:{session_id}:messages"
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    redis_client.lpush(key, json.dumps(message))
    redis_client.ltrim(key, 0, 9)
    redis_client.expire(key, timedelta(hours=settings.SESSION_TTL_HOURS))

def get_session_context(session_id: str, last_n: int = 5) -> List[dict]:
    key = f"session:{session_id}:messages"
    messages = redis_client.lrange(key, 0, last_n - 1)
    return [json.loads(m) for m in reversed(messages)]

def clear_session(session_id: str):
    redis_client.delete(f"session:{session_id}:messages")