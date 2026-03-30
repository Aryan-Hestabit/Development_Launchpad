import asyncio
from agents.research_agent import research_agent
from agents.summarizer_agent import summarizer_agent
from agents.answer_agent import answer_agent
from autogen_agentchat.messages import TextMessage

async def main():
    print("🚀 Day 1: Multi-Agent System Active (Mistral)")
    print("Memory Window: 10 | Type 'exit' to quit.\n")

    while True:
        user_query = input("USER: ")
        if user_query.lower() in ["exit", "quit"]:
            break

        # 1. User -> Research Agent (Wait for full info)
        print("\n[1/3] Researching...")
        res_research = await research_agent.on_messages([TextMessage(content=user_query, source="user")], None)
        print(f"Research Output \n {res_research.chat_message.content}\n")
        
        # 2. Research -> Summarizer Agent (Wait for summary)
        print("[2/3] Summarizing...")
        res_summary = await summarizer_agent.on_messages([res_research.chat_message], None)
        print(f"Summary Output \n {res_summary.chat_message.content}\n")

        # 3. Summarizer -> Answer Agent (STREAMING)
        print("[3/3] Final Answer: ", end="", flush=True)
        
        # We use run_stream to get the generator
        # Note: In AutoGen v0.4+, we wrap the message in a list for the stream
        res_answer = await answer_agent.on_messages([res_summary.chat_message], None)
        print(f"\n{res_answer.chat_message.content}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSystem offline.")