import openai
import asyncio
from agents.factory import team
from tools.code_executor import docker_executor
from autogen_agentchat.ui import Console

async def run_system():
    # 1. Start the executor
    print("🐳 Starting Docker Container...")
    await docker_executor.start()
    
    try:
        while True:
            user_query = input("USER: ")
            if user_query == "":
                continue
            if user_query.lower() in ["exit", "quit"]:
                break
            # 2. Run the team
            await Console(team.run_stream(task=user_query))
    except openai.RateLimitError:
        print("\n🛑 RATE LIMIT HIT. The Free Tier allows 15 requests/min.")
        print("Waiting 60 seconds before you can try again...")
    finally:
        # 3. CRITICAL: Stop the executor BEFORE exiting the async function
        print("🛑 Shutting down Docker...")
        await docker_executor.stop()

if __name__ == "__main__":
    # Use only one asyncio.run call for the entire lifecycle
    asyncio.run(run_system())