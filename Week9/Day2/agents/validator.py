from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient

model_client = OllamaChatCompletionClient(model="mistral")

VALIDATOR_PROMPT = """
Role: Final Quality Validator.
Task: Review the outputs of all parallel workers.
Output: Consolidate the work into one perfect response. If any part is illogical, correct it.
Constraint: Your response is what the user sees. Make it professional.
"""

validator_agent = AssistantAgent(
    name="validator_agent",
    model_client=model_client,
    system_message=VALIDATOR_PROMPT,
    model_client_stream=True
)