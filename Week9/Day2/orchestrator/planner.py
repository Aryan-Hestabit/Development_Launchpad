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
    function_calling=False
)

PLANNER_PROMPT = """
Role: Strategic Planner.
Task: Break the user query into logical sub-tasks for the other agents to work on, Note that the subtasks count should not exceed 5.
Rules:
1. For Simple Tasks, create 1 sub-task. 
2. For Moderately Complex Tasks, create 2-3 sub-tasks. 
3. For Highly Complex Tasks, create 4-5 sub-tasks.
4. Note that no other agent can handle code execution or any other tools.
Output: You MUST respond ONLY with a JSON array of tasks.
Example: 
[
  {"id": 1, "specialty": "Economist", "task": "Analyze cost impact"},
  {"id": 2, "specialty": "Engineer", "task": "Analyze technical hurdles"}
]
"""

planner_agent = AssistantAgent(
    name="planner_agent",
    model_client=gemini_client,
    system_message=PLANNER_PROMPT
)