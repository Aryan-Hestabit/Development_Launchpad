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


ANSWER_PROMPT = """
Role: Final Communications Lead.
Task: Take a summarized technical report and turn it into a direct answer for the user.
Constraint: Do not add new information. Keep the tone professional and helpful. 
The answer should be the 'Final Answer' that solves the initial user query perfectly.
Also At the end of your Answer , Add "TERMINATE" to signal the end of the project.
"""

answer_agent = AssistantAgent(
    name="answer_agent",
    model_client=gemini_client,
    system_message=ANSWER_PROMPT,
    model_client_stream=True
)