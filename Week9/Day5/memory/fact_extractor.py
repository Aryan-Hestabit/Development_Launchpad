import json
import re
from typing import List, Dict
from autogen_core.models import SystemMessage, UserMessage
from Config import settings
from autogen_ext.models.openai import OpenAIChatCompletionClient

_SYSTEM_PROMPT = """
You are a memory extraction assistant. 
Read the conversation and extract ONLY facts worth remembering.

Rules:
1. USER FACTS: Name, location, job, preferences, goals.
2. ENVIRONMENTAL FACTS: Specific file paths mentioned, database names used, or tool configurations established (e.g., "The data is in /workspace/data.csv").
3. PERMANENCE: Do NOT extract "Hello", "Thank you", or temporary step-by-step logic.
4. One fact per item, one sentence each.
5. Category: personal, preference, fact, topic, instruction, environment.

Respond ONLY with a valid JSON array:
[{"content": "<fact>", "category": "<category>"}, ...]
If nothing is worth storing, respond exactly with: []
"""
# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

async def extract_facts(user_message: str, agent_response: str, client = gemini_client) -> List[Dict[str, str]]:
    exchange = f"USER: {user_message.strip()}\nAGENT: {agent_response.strip()}"

    try:
        result = await client.create(
            messages=[
                SystemMessage(content=_SYSTEM_PROMPT),
                UserMessage(content=exchange, source="extractor"),
            ]
        )
        # Suggestion 2: Regex Cleaner for Markdown JSON blocks
        raw = result.content
        raw = re.sub(r"```json|```", "", raw).strip()

        if not raw or raw == "[]":
            return []

        parsed = json.loads(raw)
        allowed = {"personal", "preference", "fact", "topic", "instruction", "environment"}
        
        return [
            item for item in parsed 
            if isinstance(item, dict) 
            and item.get("category") in allowed 
            and len(item.get("content", "").strip()) > 5
        ]
    except Exception as e:
        print(f"[FactExtractor] Error: {e}")
        return []