from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext

RESEARCH_PROMPT = """
Role: Expert Senior Research Analyst.
Task: Provide exhaustive, factual, and detailed information on the user's topic.
Constraint: Your output must be comprehensive (approx 400-600 words) Focus on technical specs, 
historical context, and current trends. Do not summarize; provide raw depth.
"""

research_agent = AssistantAgent(
    name="research_agent",
    model_client=OllamaChatCompletionClient(model="mistral", host="http://localhost:11434", function_calling=True, json_output=False),
    system_message=RESEARCH_PROMPT,
    model_context=BufferedChatCompletionContext(buffer_size=10)
)