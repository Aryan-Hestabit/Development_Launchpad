from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from Config import settings

VALIDATOR_PROMPT = """
You are the @validator_agent. 
Your ONLY job is to compare the original Request and the planner task assigned to the @coder_agent with the final Output from the @code_agent.

CRITERIA:
1. COMPLETENESS: Did the agent provide all requested parts?
2. ACCURACY: Is the data format correct (CSV, Markdown, etc.)?
3. SANITY CHECK: Does the output look realistic, or did the agent hallucinate a success?

RESPONSE FORMAT:
- STATUS: [PASS] or [FAIL]
- FEEDBACK: If FAIL, specify exactly what is missing.
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

validator_agent = AssistantAgent(
    name="validator_agent",
    model_client=settings.gemini_client,
    system_message=VALIDATOR_PROMPT
)