import os
from typing import Sequence
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage

# 1. Import your Nexus Team from the agents folder
from agents.planner_agent import planner_agent
from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent
from agents.coder_agent import code_agent  # Your Docker CodeExecutorAgent
from agents.file_tools import file_agent # Day 3 Specialist
from agents.critique_agent import critique_agent
from agents.validator_agent import validator_agent
from agents.optimizer_agent import optimizer_agent
from agents.reporter_agent import reporter_agent

from Config import settings

# 2. Custom Selector Logic
def nexus_selector(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
    """
    State machine for NEXUS AI.
    Ensures the loop always starts with the Planner and ends with the Reporter.
    """
    if len(messages) == 1:
        return "planner_agent"
    
    last_message = messages[-1].content.upper()
    
    # If a specialist finishes without a mention, return to Planner for next step
    if "TERMINATE" not in last_message and "@" not in last_message:
        return "planner_agent"
        
    return None # Fallback to LLM Selector Prompt below

# 3. Enhanced Selector Prompt
# This teaches the "Brain" how to navigate the 8-agent team.
NEXUS_SELECTOR_PROMPT = """
You are the NEXUS Orchestrator. Your job is to select the most qualified agent for the next step.

HIERARCHY RULES:
1. START: Always start with @planner_agent to create the roadmap.
2. EXECUTION: Follow mentions (e.g., if Planner says @researcher_agent, pick them).
3. QUALITY: After @code_agent or @analyst_agent finish, prioritize @validator_agent and @critique_agent.
4. POLISH: Before finishing, ensure @optimizer_agent has refined the work.
5. FINAL: Use @reporter_agent to compile the FINAL-REPORT.md.
6. END: Only 'TERMINATE' when the @reporter_agent confirms the file is saved.

Participants: {participants}
History: {history}

Next Agent Handle:"""

# 4. Initialize the Nexus Team
nexus_team = SelectorGroupChat(
    participants=[
        planner_agent, research_agent, analyst_agent, 
        code_agent, file_agent, critique_agent, 
        validator_agent, optimizer_agent, reporter_agent
    ],
    model_client=settings.gemini_client, # High-reasoning model for orchestration
    termination_condition=TextMentionTermination("TERMINATE"),
    selector_prompt=NEXUS_SELECTOR_PROMPT,
    selector_func=nexus_selector,
    allow_repeated_speaker=True,
    max_turns=30 # Increased for multi-agent loops
)

async def run_nexus(user_query: str):
    """Entry point for the NEXUS system."""
    print(f"🚀 Initializing NEXUS AI for Task: {user_query}")
    
    # If using Docker, we must start it first
    # await code_agent.code_executor.start() 
    
    async for message in nexus_team.run_stream(task=user_query):
        if isinstance(message, BaseChatMessage):
            print(f"\n[{message.source}] -> {message.content}")
            
    # await code_agent.code_executor.stop()