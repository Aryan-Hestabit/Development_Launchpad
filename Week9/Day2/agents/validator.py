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

mistral = OllamaChatCompletionClient(
    model="mistral", 
    host="http://localhost:11434", 
    function_calling=False, 
    json_output=False
)

VALIDATOR_PROMPT = """
Role: Final Quality Validator.
Task: Review the outputs of all parallel workers.
Output: Consolidate the work into one perfect response. If any part is illogical, correct it.
Constraint: Your response is what the user sees. Make it professional.
"""

validator_agent = AssistantAgent(
    name="validator_agent",
    model_client=gemini_client,
    system_message=VALIDATOR_PROMPT,
    model_client_stream=True
)