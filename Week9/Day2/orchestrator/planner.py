import json
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient

model_client = OllamaChatCompletionClient(model="mistral")

PLANNER_PROMPT = """
Role: Strategic Planner.
Task: Break the user query into logical sub-tasks for the other agents to work on, Note that the subtasks count should not exceed 5.
Rules: 1. For Simple Tasks, create 1 sub-task. 
2. For Moderately Complex Tasks, create 2-3 sub-tasks. 
3. For Highly Complex Tasks, create 4-5 sub-tasks.
Output: You MUST respond ONLY with a JSON array of tasks.
Example: 
[
  {"id": 1, "specialty": "Economist", "task": "Analyze cost impact"},
  {"id": 2, "specialty": "Engineer", "task": "Analyze technical hurdles"}
]
"""

planner_agent = AssistantAgent(
    name="planner_agent",
    model_client=model_client,
    system_message=PLANNER_PROMPT
)