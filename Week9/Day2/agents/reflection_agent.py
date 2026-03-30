from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient

model_client = OllamaChatCompletionClient(model="mistral")

REFLECTION_PROMPT = """
Role: Senior Peer Reviewer & Critic.
Task: Critically evaluate the combined output of multiple specialized workers.
Check for:
1. Contradictions between workers.
2. Missing data points from the original plan.
3. Lack of depth or generic answers.
Output: Provide a 'Critique' list. If the work is excellent, state 'NO IMPROVEMENTS NEEDED'.
"""

reflection_agent = AssistantAgent(
    name="reflection_agent",
    model_client=model_client,
    system_message=REFLECTION_PROMPT
)