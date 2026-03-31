from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient

model_client = OllamaChatCompletionClient(model="mistral")

def create_worker(worker_id: int, specialty: str):
    return AssistantAgent(
        name=f"worker_{worker_id}",
        model_client=model_client,
        system_message=f"Role: Specialized Executor. Specialty: {specialty}. Task: Execute your assigned sub-task only.",
        model_client_stream=True
    )