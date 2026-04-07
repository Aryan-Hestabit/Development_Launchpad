import asyncio
import logging
import os
import uuid
from autogen_core.memory import MemoryMimeType
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient
from Config import settings
from memory.session_memory import build_session_memory, add_to_session
from memory.vector_store import FAISSVectorMemory 
from memory.fact_extractor import extract_facts
from autogen_core.memory import MemoryContent

# CONFIG
LOGS_DIR        = os.path.join(os.path.dirname(__file__), "memory", "logs")

SYSTEM_PROMPT = """
You are a helpful, context-aware AI assistant with persistent memory.

Before each response you receive two memory injections:
1. Session turns tagged [USER] / [AGENT] — this conversation so far.
2. [LONG-TERM MEMORY] — facts recalled from past sessions relevant to your query.

Use both naturally. When recalling long-term facts say:
"Based on what I know about you…" or "Since you prefer…"
"""

def setup_logging(session_id: str) -> logging.Logger:
    os.makedirs(LOGS_DIR, exist_ok=True)
    logger = logging.getLogger(session_id)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.FileHandler(
        os.path.join(LOGS_DIR, f"session_{session_id}.log"), encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    return logger

async def main():
    # --- Logging + session ID ------------------------------------------------
    session_id = str(uuid.uuid4())
    logger     = setup_logging(session_id)
    logger.info(f"SESSION START | id={session_id}")

    print(f"\n  DAY 4 — AutoGen Memory Systems | Session: {session_id[:8]}…\n")

    # --- Memory initialisation -----------------------------------------------
    session_memory = build_session_memory()

    faiss_memory = FAISSVectorMemory(top_k=5, score_threshold=0.2)
    faiss_memory.initialize()

    agent = AssistantAgent(
        name="MemoryAgent",
        model_client=settings.gemini_client,
        system_message=SYSTEM_PROMPT,
        model_context=BufferedChatCompletionContext(buffer_size=10),
        memory=[session_memory, faiss_memory],
        model_client_stream=True,
    )

    print("  Commands: 'facts' | 'quit'\n")

    turn = 0
    
    while True:
        user_input = input("User: ").strip()
        if not user_input: continue
        if user_input.lower() == "quit" or user_input.lower() == "exit": break
        
        # REQUIREMENT: 'facts' command retrieves all from SQLite
        if user_input.lower() == "facts":
            rows = faiss_memory.get_all_facts()
            print(f"\n--- ALL STORED FACTS ({len(rows)}) ---")
            for r in rows:
                print(f"[{r[0].upper()}] {r[1]} ({r[2][:10]})")
            print("-------------------------------\n")
            continue

        turn += 1
        logger.info(f"[TURN {turn:03d}] [USER] {user_input}")

        # 1. RUN AGENT 
        try:
            response = await agent.on_messages(
                [TextMessage(content=user_input, source="user")],
                CancellationToken(),
            )
            agent_res = response.chat_message.content
            print(f"\n Agent: {agent_res}\n")
        except Exception as e:
            print(f"Error: {e}")
            continue

        # 2. UPDATE SESSION MEMORY (Short-term)
        await add_to_session(session_memory, "USER", user_input)
        await add_to_session(session_memory, "AGENT", agent_res)
        logger.info(f"[TURN {turn:03d}] [AGENT] {agent_res}")

        new_facts = await extract_facts(user_input, agent_res)
        if new_facts:
            for f in new_facts:
                await faiss_memory.add(MemoryContent(
                    content=f["content"], 
                    mime_type=MemoryMimeType.TEXT, 
                    metadata={"category": f["category"]}
                ))
            print(f" {len(new_facts)} facts stored.")
        else:
            print(" No new facts found.")


if __name__ == "__main__":
    asyncio.run(main())