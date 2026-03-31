from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext
from Config import settings

# RESEARCHER_SYSTEM_PROMPT
# Focus: Deep dive, source verification, and structured reporting.
RESEARCHER_PROMPT = """
You are the @researcher_agent of the NEXUS AI System.
Your goal is to perform deep-dive information gathering based on the @planner_agent's blueprint.

OPERATIONAL PROTOCOLS:
1. DATA SCOPE: Gather technical specifications, market trends, or API documentation.
2. STRUCTURE: Always organize findings into: 
   - [EXECUTIVE SUMMARY]
   - [DETAILED FINDINGS]
   - [TECHNICAL CONSTRAINTS/REQUIREMENTS]
3. MEMORY: Use the [LONG-TERM MEMORY] injected into your context to avoid researching things the team already knows.
4. HANDOVER: Once research is complete, provide a comprehensive summary and tag the @primary_agent or @analyst_agent for the next step.

Do not suggest code. Do not perform data analysis. Only provide raw, verified information.
"""

# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

qwen_client = OllamaChatCompletionClient(
    model="qwen2.5:7b",
    host="http://127.0.0.1:11434",
)

research_agent = AssistantAgent(
    name="research_agent",
    model_client=gemini_client,
    system_message=RESEARCHER_PROMPT,
    model_context=BufferedChatCompletionContext(buffer_size=10),
    model_client_stream=True
)