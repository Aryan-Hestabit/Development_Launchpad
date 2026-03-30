import asyncio
import logging
import os
import uuid

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient
from Config import settings
from memory.session_memory import build_session_memory, add_to_session 
from memory.vector_store import FAISSVectorMemory 
from memory.fact_extractor import extract_facts

# =============================================================================
# CONFIG
# =============================================================================

MAIN_MODEL      = "gpt-4.1"
DB_PATH         = os.path.join(os.path.dirname(__file__), "memory", "long_term.db")
LOGS_DIR        = os.path.join(os.path.dirname(__file__), "memory", "logs")

SYSTEM_PROMPT = """
You are a helpful, context-aware AI assistant with persistent memory.

Before each response you receive two memory injections:
1. Session turns tagged [USER] / [AGENT] — this conversation so far.
2. [LONG-TERM MEMORY] — facts recalled from past sessions relevant to your query.

Use both naturally. When recalling long-term facts say:
"Based on what I know about you…" or "Since you prefer…"
"""

# =============================================================================
# LOGGING — file only, conversation turns + facts, nothing else
# =============================================================================

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


# =============================================================================
# MAIN
# =============================================================================

async def main() -> None:

    # --- Logging + session ID ------------------------------------------------
    session_id = str(uuid.uuid4())
    logger     = setup_logging(session_id)
    logger.info(f"SESSION START | id={session_id}")

    print(f"\n  DAY 4 — AutoGen Memory Systems | Session: {session_id[:8]}…\n")

    # --- Memory initialisation -----------------------------------------------
    session_memory = build_session_memory()

    faiss_memory = FAISSVectorMemory(db_path=DB_PATH, top_k=5, score_threshold=0.4)
    faiss_memory.initialize()

    # --- Agent ---------------------------------------------------------------
    # BufferedChatCompletionContext(buffer_size=10):
    #   Limits raw LLM message window to last 10 messages.
    #   Ref: autogen docs — "Using Model Context" in Agents tutorial.
    #
    # memory=[session_memory, faiss_memory]:
    #   AutoGen calls update_context() on both before every LLM invocation.
    agent = AssistantAgent(
        name="MemoryAgent",
        model_client=settings.gemini_client,
        system_message=SYSTEM_PROMPT,
        model_context=BufferedChatCompletionContext(buffer_size=10),
        memory=[session_memory, faiss_memory],
        model_client_stream=True,
    )

    print(f"  Long-term facts loaded: {faiss_memory.fact_count}")
    print("  Commands: 'facts' | 'quit'\n")

    turn = 0

    # --- Chat loop -----------------------------------------------------------
    while True:

        try:
            user_input = input("🧑 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Bye.")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "facts":
            faiss_memory.display_all()
            continue

        turn += 1

        # Log user turn + add to session memory
        logger.info(f"[TURN {turn:03d}] [USER] {user_input}")
        await add_to_session(session_memory, "USER", user_input)

        # Run agent
        # AutoGen internally calls before the LLM:
        #   session_memory.update_context() → injects session turns as SystemMessage
        #   faiss_memory.update_context()   → FAISS search, injects top-k facts
        #   BufferedChatCompletionContext   → provides last 10 raw LLM messages
        print("\n🤖 Agent: ", end="", flush=True)
        try:
            response = await agent.on_messages(
                [TextMessage(content=user_input, source="user")],
                CancellationToken(),
            )
            agent_response: str = response.chat_message.content
            print(agent_response)
        except Exception as e:
            print(f"\n[Error: {e}]")
            continue

        # Log agent turn + add to session memory
        logger.info(f"[TURN {turn:03d}] [AGENT] {agent_response}")
        await add_to_session(session_memory, "AGENT", agent_response)

        # Extract facts → store to SQLite + FAISS simultaneously via store_facts()
        facts = await extract_facts(user_input, agent_response)
        if facts:
            await faiss_memory.store_facts(facts, session_id, turn)
            for fact in facts:
                logger.info(f"[TURN {turn:03d}] [FACT] [{fact['category']}] {fact['content']}")
            print(f"\n  💾 {len(facts)} fact(s) stored → {[f['category'] for f in facts]}")

        print()

    # --- Cleanup -------------------------------------------------------------
    logger.info(f"SESSION END | id={session_id} | turns={turn}")
    await faiss_memory.close()
    print(f"\n✅ Done | Turns: {turn} | Log: memory/logs/session_{session_id}.log\n")


if __name__ == "__main__":
    asyncio.run(main())