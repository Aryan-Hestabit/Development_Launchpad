import asyncio
import uuid
import logging
import os
from autogen_agentchat.ui import Console
from autogen_core.memory import MemoryContent, MemoryMimeType

# NEXUS Imports
from agents.orchestrator import create_nexus_team # Factory function
from agents.coder_agent import docker_executor

# Memory & Fact Imports
from memory.session_memory import build_session_memory, add_to_session
from memory.vector_store import FAISSVectorMemory 
from memory.fact_extractor import extract_facts

# --- 📜 LOGGING SETUP ---
LOGS_DIR = os.path.join(os.path.dirname(__file__), "memory", "logs")

def setup_logger(session_id: str) -> logging.Logger:
    os.makedirs(LOGS_DIR, exist_ok=True)
    logger = logging.getLogger(session_id)
    logger.setLevel(logging.INFO)
    file_path = os.path.join(LOGS_DIR, f"nexus_{session_id[:8]}.log")
    handler = logging.FileHandler(file_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return logger

async def run_system():
    # 1. Setup Session & Logging
    session_id = str(uuid.uuid4())
    logger = setup_logger(session_id)
    logger.info(f"--- SESSION START: {session_id} ---")
   
    # 2. Initialize Memory Tiers
    session_memory = build_session_memory()
    faiss_memory = FAISSVectorMemory()
    faiss_memory.initialize()

    print(f"🚀 NEXUS ONLINE | Session: {session_id[:8]}")

    # 3. Create the Team (NATIVE MEMORY INJECTION)
    # This ensures the Planner gets the memory objects directly
    nexus_team = create_nexus_team(session_memory, faiss_memory)

    # 4. Start Docker
    print("🐳 Starting Docker Environment...")
    await docker_executor.start()
    
    try:
        while True:
            query = input("\n🧑 User: ").strip()
            if not query: continue
            if query.lower() in ["exit", "quit"]: break
            
            logger.info(f"USER_QUERY: {query}")
            final_output = ""
            # 1. Get the stream/result from the team
            response = await Console(nexus_team.run_stream(task=query))

            print(f"response: {response}")

            """# 2. Check if it's actually a stream (has __aiter__)
            if hasattr(result_stream, "__aiter__"):
                async for message in result_stream:
                    # SAFE ATTRIBUTE CHECK for events
                    if hasattr(message, 'content') and isinstance(message.content, str):
                        final_output = message.content
                    
                    # Render the UI
                    await Console(message)
            else:
                # If it returned a single TaskResult/TextMessage instead of a stream
                final_output = result_stream.content if hasattr(result_stream, 'content') else str(result_stream)
                await Console(result_stream)

            # --- 💾 POST-PROCESS & STORAGE ---
            if final_output:
                logger.info(f"NEXUS_RESPONSE: {len(final_output)} chars")
                
                # Update Short-term (Session)
                await add_to_session(session_memory, "USER", query)
                await add_to_session(session_memory, "AGENT", final_output)

                # Update Long-term (Facts)
                new_facts = await extract_facts(query, final_output)
                for f in new_facts:
                    await faiss_memory.add(MemoryContent(
                        content=f["content"], 
                        mime_type=MemoryMimeType.TEXT, 
                        metadata={"category": f["category"]}
                    ))
                print(f"\n✅ Learned {len(new_facts)} new facts.")
                logger.info(f"FACTS_LEARNED: {len(new_facts)}")
                """
    except Exception as e:
        logger.error(f"SYSTEM_ERROR: {str(e)}")
        print(f"❌ System Error: {e}")
    finally:
        print("🛑 Shutting down Docker...")
        await docker_executor.stop()
        logger.info("--- SESSION END ---")

if __name__ == "__main__":
    try:
        asyncio.run(run_system())
    except KeyboardInterrupt:
        print("\nGoodbye!")