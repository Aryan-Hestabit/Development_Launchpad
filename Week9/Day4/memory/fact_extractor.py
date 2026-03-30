import json
import re
from typing import List, Dict

from autogen_core.models import SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from Config import settings 

_SYSTEM_PROMPT = """
You are a memory extraction assistant.
Read one conversation exchange and extract ONLY facts worth remembering long-term.

Rules:
- Personal info (name, location, job), preferences, topics being studied, explicit instructions.
- Do NOT extract transient or obvious conversational content.
- One fact per item, one sentence each.
- Category must be exactly one of: personal, preference, fact, topic, instruction.

Respond ONLY with a valid JSON array, no markdown, no explanation:
[{"content": "<fact>", "category": "<category>"}, ...]

If nothing worth storing: []
"""


async def extract_facts(user_message: str, agent_response: str, client: OpenAIChatCompletionClient = settings.gemini_client) -> List[Dict[str, str]]:
    exchange = f"USER: {user_message.strip()}\nAGENT: {agent_response.strip()}"

    try:
        result = await client.create(
            messages=[
                SystemMessage(content=_SYSTEM_PROMPT),
                UserMessage(content=exchange, source="extractor"),
            ]
        )
        raw = result.content

        if not raw or raw == "[]":
            return []

        allowed = {"personal", "preference", "fact", "topic", "instruction"}
        return [
            {"content": item["content"], "category": item["category"]}
            for item in json.loads(raw)
            if isinstance(item, dict)
            and item.get("category") in allowed
            and len(item.get("content", "").strip()) > 5
        ]

    except Exception as e:
        # Never crash the main chat loop
        print(f"[FactExtractor] Skipped: {e}")
        return []