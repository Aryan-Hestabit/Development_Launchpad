from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, ToolCallSummaryMessage
from typing import Sequence
import settings
from tools.db_tools import db_agent
from tools.code_executor import code_agent
from tools.file_tools import file_agent

planner_agent_prompt = """
ROLE: You are Planner, the strategic planner and delegator of a multi-agent system.

TEAM:
1. code_agent: Generates and executes Python and Shell codes. Use for any Tasks which require code execution, heavy data_preprocessing, or complex calculations.
2. db_agent: Converts CSV files to SQLite tables , describes table schemas, and executes SQL queries. Use for all database-related operations exclusively.
3. file_agent: Manages files in the workspace. Use for reading, writing, and listing files.
4. reporter_agent: reviews the final outputs from all agents and crafts a clear, concise summary of the complete process and results in plain language.

TASKS:
- Break down the user's request into sequential steps.
- Delegate each step to the most appropriate agent, one at a time.
- if the response if from other agents review them and then assign the next step to the right agent according to the task requirements.

RULES:
- Always include exact filenames, table names, and query details in your delegations.
- At the end of each message, clearly specify which agent should act next using the @mention format (e.g., @code_agent: write a python file to plot graph between sales and revence column from the sales.csv file).
- Never Generate any code  yourself, assign the task to code_agent.
- Never write content for the file yourself, assign the task to file_agent.
- Never write any SQL query yourself, assign the task to db_agent.
- You can mention multiple agents in a single message, but add the "@" symbol for only the agent that should act next.
for example, if you want to assign a task to code_agent and then ask db_agent to prepare a database for a file, you can say 
"@code_agent: create a user.csv file and fill it with random 1000 rows of data , the columns are name, email, age . after that db_agent: prepare the sales.db database with a table called sales_data using the sales.csv file".
CRITICAL:
- Always use a single @mention at the end of your message to indicate which agent should act next. Do not mention multiple agents in the same message.
- Never reply with an empty string. If you have no Tasks to assign, respond with 
"@reporter_agent : All tasks completed. Please review the results and provide a summary." instead of an empty response.

"""

reporter_agent_prompt = """You are ReporterAgent — the summarization specialist of this multi-agent system.
Your ONLY responsibility is to review the final outputs from all agents and craft a clear, concise summary.

RULES:
- After report , Always print "TERMINATE" at the end of your summary to signal the end of the process.
- Your summary should be comprehensive and user friendly, explaining the complete process and results in plain language.
- Do not suggest any next steps or actions. Your role is purely to report on what was done and what the results were.
- If the output is Not as desired or contains errors, report that clearly in the summary. Do not attempt to fix or correct it — just report the facts.
- Never reply with an empty string. If you have no data to return, just print "TERMINATE" to end the conversation. Do not write anything else."""

# 2. The Team Participants
planner_agent = AssistantAgent(
    name="planner_agent",
    description = ("Strategic planner and delegator."
        "Breaks tasks into sequential steps and assigns them one at a time to "
        "CoderAgent, DBAgent, or FileAgent. Reviews each result before assigning "
        "the next step. Ends the conversation with TERMINATE when done."),
    model_client=settings.model_client,
    system_message=planner_agent_prompt)

reporter_agent = AssistantAgent(
    name="reporter_agent",
    description = ("Specialist in summarizing and reporting results."""
    "After all tasks are completed, this agent reviews the final outputs and crafts a clear, concise summary of the complete process and results. It ensures the final report is comprehensive and user-friendly."),
    model_client=settings.model_client,
    system_message=reporter_agent_prompt)

# 3. Custom Selector Prompt as per your requirement
# We force the selection of planner_agent if history is empty.
CUSTOM_SELECTOR_PROMPT = """

You are the routing layer of a 5-agent system. Pick the single best agent to act next.
 
AGENT ROLES :
{roles}
 
CONVERSATION HISTORY :
{history}
 
ROUTING RULES :
- review the end of the previous message to see if there is a @mention of a specific agent. If there is, route to that agent.
- New task from user return "planner_agent"
- If there are multiple @mentions in the last message , pick the agent that is mentioned at the top of the message.
- Planner_agent just assigned a task to @coder_agent return "coder_agent"
- Planner_agent just assigned a task to @db_agent return "db_agent"
- Planner_agent just assigned a task to @file_agent return "file_agent"
- Planner_agent just assigned a tasks to @reporter_agent return "reporter_agent"
- A specialist just finished reporting a result return "planner_agent"
- all tasks are completed  then return "reporter_agent" to generate the final report.
- Whenever in doubt, pick planner_agent to review and assign the next step.
- Never route to the same specialist twice without Planner_agent reviewing in between.

CRITICAL :
- Only return role .
 
=== AVAILABLE AGENTS ===
{participants}
 
Respond with ONLY the exact agent name. No punctuation, no explanation."""

SPECIALIST_AGENTS = {"CoderAgent", "DBAgent", "FileAgent"}
def custom_selector(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
    # 1. If it's the very first message (the user query), always pick primary_agent
    if len(messages) == 1:
        return "planner_agent"
    
    # Fallback 
    return None

# 4. Define the Team
team = SelectorGroupChat(
    participants=[planner_agent, code_agent, db_agent,file_agent, reporter_agent],
    model_client=settings.model_client,
    termination_condition=TextMentionTermination("TERMINATE"),
    selector_prompt=CUSTOM_SELECTOR_PROMPT,
    selector_func=custom_selector,
    max_turns=15,
    allow_repeated_speaker=False, # Crucial for the Refinement Loop
)