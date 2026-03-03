"""
memory_store.py
Redis-backed per-endpoint conversation memory.
Stores last 5 messages per endpoint as a JSON list in Redis.

Keys:
    memory:ask
    memory:ask-image
    memory:ask-sql
"""

import json
import sys
from pathlib import Path

import redis

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB, MEMORY_MAX_MESSAGES

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

ENDPOINTS = {"ask", "ask-image", "ask-sql"}


def _key(endpoint: str) -> str:
    assert endpoint in ENDPOINTS, f"Unknown endpoint: {endpoint}"
    return f"memory:{endpoint}"


def get_memory(endpoint: str) -> list[dict]:
    """Return the last N messages for the given endpoint."""
    raw = r.get(_key(endpoint))
    return json.loads(raw) if raw else []


def add_message(endpoint: str, role: str, content: str):
    """
    Append a message and keep only the last MEMORY_MAX_MESSAGES.
    role: 'user' | 'assistant'
    """
    messages = get_memory(endpoint)
    messages.append({"role": role, "content": content})
    messages = messages[-MEMORY_MAX_MESSAGES:]
    r.set(_key(endpoint), json.dumps(messages))


def clear_memory(endpoint: str):
    r.delete(_key(endpoint))


def format_history(endpoint: str) -> str:
    """Return memory as a formatted string for LLM context injection."""
    messages = get_memory(endpoint)
    if not messages:
        return ""
    lines = ["Conversation history:"]
    for m in messages:
        prefix = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"  {prefix}: {m['content']}")
    return "\n".join(lines)