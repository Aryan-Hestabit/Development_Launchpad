import openai
import asyncio
from agents.orchestrator import team
from tools.code_executor import docker_executor
from autogen_agentchat.ui import Console

async def run_system():
    # 1. Start the executor
    print("Starting Docker Container...")
    await docker_executor.start()
    
    try:
        while True:
                user_query = input("USER: ")
                if user_query == "":
                    continue
                elif user_query.lower() in ["exit", "quit"]:
                    break
                else:# 2. Run the team
                    result = await Console(team.run_stream(task=user_query))
    except Exception as e:
        print(f"\n ERROR: \n {str(e)}") 
    finally:        # 3. CRITICAL: Stop the executor BEFORE exiting the async function
        print("Shutting down Docker...")
        await docker_executor.stop()   

if __name__ == "__main__":
    # Use only one asyncio.run call for the entire lifecycle
    asyncio.run(run_system())