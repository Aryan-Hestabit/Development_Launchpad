from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_ext.models.openai import OpenAIChatCompletionClient
import settings


# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

mistral_client = OllamaChatCompletionClient(
    model="mistral", 
    host="http://localhost:11434", 
    function_calling=False, 
    json_output=False
)

RESEARCH_PROMPT = """
Role: Expert Senior Research Analyst.
Task: Provide exhaustive, factual, and detailed information on the user's topic.
Constraint: Your output must be comprehensive (approx 400-600 words) Focus on technical specs, 
historical context, and current trends. Do not summarize; provide raw depth.
"""

research_agent = AssistantAgent(
    name="research_agent",
    model_client=gemini_client,
    system_message=RESEARCH_PROMPT,
    model_context=BufferedChatCompletionContext(buffer_size=10),
    model_client_stream=True
)