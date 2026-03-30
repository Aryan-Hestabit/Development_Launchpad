from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from typing import Sequence
import settings
from tools.db_tools import db_agent
from tools.code_executor import code_agent
from tools.file_tools import file_agent

# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

from autogen_ext.models.ollama import OllamaChatCompletionClient

qwen_client = OllamaChatCompletionClient(
    model="qwen2.5:7b",
    # Point to the bridge we created above
    host="http://127.0.0.1:11434", 
)

# 2. The Team Participants
primary_agent = AssistantAgent(
    name="primary_agent",
    model_client=qwen_client,
    system_message="""You are part of a Agent Chatbot system and are the Team Lead (primary_agent). 
Your sole responsibility is to plan and delegate tasks. 
CONTEXT:
1. @db_agent can execute SQL queries and convert CSVs to SQL tables.
2. @file_agent can manage files in the workspace (list, read, write).
3. @code_agent can write and execute Python code and shell commands.

RULES:
1. NEVER write Python code or Shell commands yourself.
2. If this is the start of a task, generate a step-by-step PLAN first.
3. Call agents using the format: @agent_name. Call a Single Agent at a time Only.
4. Delegate to @file_agent for file management and @db_agent for SQL tasks don't call @code_agent unnecessarily.
5. Only call @code_agent for complex logic, math, or data visualization that cannot be done via SQL.
6. Review the output of agents. If incorrect, ask for a refinement. If complete, provide the final answer to the user and end with TERMINATE.
7. Don't call the Function of Other Agents Directly, always ask them to do it themselves by mentioning them in the message."""
)

# 3. Custom Selector Prompt as per your requirement
# We force the selection of primary_agent if history is empty.
CUSTOM_SELECTOR_PROMPT = """

You are the Orchestrator. Analyze the conversation history and select the NEXT agent to speak.

RULES:
1. If the last message contains an '@mention' (e.g., @db_agent), you MUST select that agent.
2. If the user just asked a question, select 'primary_agent' to create the plan.
3. If an agent just finished a task but didn't mention anyone, select 'primary_agent' to review the work.
4. If 'TERMINATE' is mentioned, the chat ends.
4. Only return the name of the next role from: {participants}.

Available Agents:
{roles}

History:
{history}

Next Role:"""

def custom_selector(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
    # 1. If it's the very first message (the user query), always pick primary_agent
    if len(messages) == 1:
        return "primary_agent"
    # 4. Default: Let the LLM (Gemini) decide for any other complex transitions
    return None

# 4. Define the Team
team = SelectorGroupChat(
    participants=[primary_agent, code_agent, db_agent,file_agent],
    model_client=gemini_client,
    termination_condition=TextMentionTermination("TERMINATE"),
    selector_prompt=CUSTOM_SELECTOR_PROMPT,
    selector_func=custom_selector,
    allow_repeated_speaker=True, # Crucial for the Refinement Loop
    max_turns=15
)