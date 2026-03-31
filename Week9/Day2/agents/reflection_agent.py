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
    model_client=gemini_client,
    system_message=REFLECTION_PROMPT,
    model_client_stream=True
)