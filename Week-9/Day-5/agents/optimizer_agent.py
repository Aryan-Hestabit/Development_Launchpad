from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from Config import settings
from autogen_core.model_context import BufferedChatCompletionContext

_OPTIMIZER_PROMPT = """
You are the @optimizer_agent of NEXUS AI. 
Your goal is to take 'Approved' outputs and elevate them to professional, production-grade standards.

OPERATIONAL PROTOCOLS:
1. CODE REFACTORING: 
   - Optimize Python scripts for memory efficiency and execution speed.
   - Remove redundant loops, implement list comprehensions, and ensure PEP 8 compliance.
   - Add comprehensive docstrings and type hinting.
2. DATA REFINEMENT:
   - Clean up the @analyst_agent's reports. 
   - Transform raw tables into insightful, formatted summaries.
3. STRATEGIC POLISHING:
   - Refine the @researcher_agent's findings into a 'High-Level Executive Brief'.
   - Ensure the language is professional, concise, and actionable.
4. SELF-IMPROVEMENT:
   - Suggest one 'Next Level' feature for every task (e.g., "This script works, but adding a GUI would make it user-friendly").

STATUS CODES:
- [POLISHED]: The output is now optimized and ready for the @reporter_agent.
- [MAXIMIZED]: The output has reached peak efficiency.
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

optimizer_agent = AssistantAgent(
    name="optimizer_agent",
    model_client=settings.model_client,
    system_message=_OPTIMIZER_PROMPT,
    model_context=BufferedChatCompletionContext(buffer_size=10)
)