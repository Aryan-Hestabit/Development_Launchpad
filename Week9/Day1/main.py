import asyncio
from agents.research_agent import research_agent
from agents.summarizer_agent import summarizer_agent
from agents.answer_agent import answer_agent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination

async def main():
    print("Day 1: Multi-Agent System Active (Mistral)")
    print("Memory Window: 10 | Type 'exit' to quit.\n")

    while True:
        user_query = input("USER: ")
        if user_query == "":
            continue
        elif user_query.lower() in ["exit", "quit"]:
            break
        else:
            team = RoundRobinGroupChat(
                [research_agent, summarizer_agent, answer_agent],
                termination_condition=TextMentionTermination("TERMINATE"),
                max_turns = 3
                )
            
            await Console(team.run_stream(task=user_query))
if __name__ == "__main__":
    asyncio.run(main())