from autogen_agentchat.agents import AssistantAgent
import settings


PLANNER_PROMPT = """
Role: Strategic Planner.
Task: Break the user query into logical sub-tasks for the other agents to work on, Note that the subtasks count should not exceed 5.

Rules:
- For Simple Tasks, create 1 sub-task. 
- For Moderately Complex Tasks, create 2-3 sub-tasks. 
- For Highly Complex Tasks, create 4-5 sub-tasks.
- Note that no other agent can handle code execution or any other tools.
- Do NOT answer the query yourself.
- Respond ONLY with a valid JSON array — nothing else

## OUTPUT FORMAT (strict):
Respond ONLY with this JSON array — no extra text before or after:

[
  {"id": 1, "Role": "<Specialist Role>", "task": "<Clear task 
   description>"},
  {"id": 2, "Role": "<Specialist Role>", "task": "<Clear task 
   description>"}
]
"""

planner_agent = AssistantAgent(
    name="planner_agent",
    model_client=settings.gemini_client,
    system_message=PLANNER_PROMPT
)

