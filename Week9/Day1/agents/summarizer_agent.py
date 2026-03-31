from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
import settings


# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

# Qwen 2.5 (7B or 14B) is highly recommended for coding tasks
mistral_client = OllamaChatCompletionClient(
    model="mistral", 
    host="http://localhost:11434", 
    function_calling=False, 
    json_output=False
)
SUMMARIZER_PROMPT = """
Role: Information Architect & Summarizer.
Task: Receive long-form research and distill it into a structured summary.
Constraint: Maintain all key technical facts but reduce the word count by 60%.
Don't add any facts from your own knowledge. 
Use bullet points for readability. Ensure the output is concise enough to allow 
the next agent to process the full history.
"""

summarizer_agent = AssistantAgent(
    name="summarizer_agent",
    model_client=gemini_client,
    system_message=SUMMARIZER_PROMPT,
    model_client_stream=True
)