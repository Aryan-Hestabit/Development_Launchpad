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

def create_worker(worker_id: int, specialty: str):
    return AssistantAgent(
        name=f"worker_{worker_id}",
        model_client=gemini_client,
        system_message=f"Role: Specialized Executor. Specialty: {specialty}. Task: Execute your assigned sub-task only.",
        model_client_stream=True
    )