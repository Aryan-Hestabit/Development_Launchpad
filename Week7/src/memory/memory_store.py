import json
import sys
from pathlib import Path

import redis

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB, MEMORY_MAX_MESSAGES

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

ENDPOINTS = {"ask", "ask-image", "ask-sql"}


def _key(session_id: str, endpoint: str) -> str:
    assert endpoint in ENDPOINTS, f"Unknown endpoint: {endpoint}"
    return f"memory:{session_id}:{endpoint}"


def get_memory(session_id: str, endpoint: str) -> list[dict]:
    raw = r.get(_key(session_id, endpoint))
    return json.loads(raw) if raw else []


def add_message(session_id: str, endpoint: str, role: str, content: str):
    messages = get_memory(session_id, endpoint)
    messages.append({"role": role, "content": content})
    messages = messages[-MEMORY_MAX_MESSAGES:]
    r.set(_key(session_id, endpoint), json.dumps(messages))


def clear_memory(session_id: str, endpoint: str):
    r.delete(_key(session_id, endpoint))


def format_history(session_id: str, endpoint: str) -> str:
    messages = get_memory(session_id, endpoint)
    if not messages:
        return ""

    lines = ["Conversation history:"]
    for m in messages:
        prefix = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"  {prefix}: {m['content']}")
    return "\n".join(lines)