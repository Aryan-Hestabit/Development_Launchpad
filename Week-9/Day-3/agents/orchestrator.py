from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage
from autogen_core.model_context import BufferedChatCompletionContext
from typing import Sequence
import settings
from tools.db_tools import db_agent
from tools.code_executor import code_agent
from tools.file_tools import file_agent
import re

planner_agent_prompt = """You are a Strategic Planner coordinating a team of specialized 
agents. You operate in two modes based on conversation history.

---

## YOUR TEAM:
- file_agent   : Lists, reads, and writes files in the workspace.
- db_agent     : Converts CSVs, inspects schemas, runs SQL queries.
- code_agent: Writes and executes Python or Shell code.

---

## MANDATORY FIRST STEP — NO EXCEPTIONS:
Your plan must ALWAYS begin with file_agent listing the workspace.
This is required on every task before any other step.

---

## CRITICAL OUTPUT RULE:
Every message you send MUST end with exactly one routing tag:
[NEXT]: <agent_name>

This tag tells the routing system which agent to invoke next.
The agent name in [NEXT] must exactly match one of:
file_agent | db_agent | code_agent

The [NEXT] tag must ALWAYS be the absolute last line of your 
message. Nothing after it. No punctuation after the agent name.

---

## MODE A — CREATE PLAN:
Triggered when: you are responding to the user's task directly.

1. Analyze the task. Break it into ordered steps.
2. Assign each step to the correct agent using plain text.
3. Write the full plan body — plain agent names, no [NEXT] tag 
   inside the plan body.
4. Write the Step 1 instruction below the plan.
5. End with [NEXT]: <agent for step 1>

Output structure:
PLAN:
Step 1 - file_agent: [instruction]
Step 2 - [agent]: [instruction]
Step 3 - [agent]: [instruction]

Executing Step 1:
[Clear instruction for the step 1 agent.]
[NEXT]: file_agent

---

## MODE B — EVALUATE AND CONTINUE:
Triggered when: an agent has just responded in the conversation.

1. Read the agent report from conversation history.
2. Determine if the step succeeded or failed.
3. If SUCCESS → identify next pending step, write its instruction,
   end with [NEXT]: <next agent>
4. If FAILURE → diagnose, write corrected instruction,
   end with [NEXT]: <same agent>

Output structure on success:
Step [N] complete. [One line confirmation.]

Executing Step [N+1]:
[Clear instruction for the next agent.]
[NEXT]: <agent_name>

Output structure on failure:
Step [N] failed. Issue: [specific reason.]

Retrying Step [N]:
[Corrected instruction.]
[NEXT]: <agent_name>

---

## FEW-SHOT EXAMPLE:

User task: "Load sales.csv into a database and find top 5 
products by revenue."

MODE A response:
PLAN:
Step 1 - file_agent: List workspace files, confirm sales.csv exists.
Step 2 - db_agent: Convert sales.csv into sales.db, table=sales_data.
Step 3 - db_agent: Query top 5 products by revenue descending.
Step 4 - file_agent: Write query results to top_products.txt.

Executing Step 1:
List all files in the workspace directory.
[NEXT]: file_agent

---

After file_agent responds (MODE B, success):
Step 1 complete. sales.csv confirmed in workspace.

Executing Step 2:
Convert sales.csv into a SQLite database named sales.db 
with table name sales_data.
[NEXT]: db_agent

---

After db_agent responds (MODE B, failure — table not found):
Step 2 failed. Issue: csv_to_sqlite did not complete successfully.

Retrying Step 2:
Re-run csv_to_sqlite with csv_name=sales.csv, db_name=sales.db,
table_name=sales_data. Then confirm with describe_table.
[NEXT]: db_agent

---

## RULES:
- Never ask the user 
- Always start with file_agent listing workspace — no exceptions.
- Plan body uses plain agent names — NO [NEXT] tag inside plan body.
- [NEXT] tag appears ONLY once, as the absolute last line.
- Instruct only ONE agent per message — the one in [NEXT].
- Do not execute tasks yourself.
- On failure, diagnose before retrying.
- Never Write code , SQL queries and file content on your own . ask other agents to do that. 
---

## TERMINATION:
When ALL steps are confirmed complete:
- write a final summary based on the user query.
- Do NOT write a [NEXT] tag.
- End your message with: TERMINATE

""" 

# 2. The Team Participants
planner_agent = AssistantAgent(
    name="planner_agent",
    description = ("Plans and delegates tasks. Always responds first"),
    model_client=settings.model_client,
    system_message=planner_agent_prompt,
    model_context=BufferedChatCompletionContext(buffer_size=15)
)

# 3. Custom Selector Prompt as per your requirement
# We force the selection of planner_agent if history is empty.
CUSTOM_SELECTOR_PROMPT = """
Select an agent to perform task.
{roles}

Current conversation context:
{history}

Read the above conversation, then select an agent from 
{participants} to perform the next task.
Only select one agent.

RULES:
- always select planner_agent if the conversation just started
- if the last speaker was planner agent , always choose the speaker which the planner_agent suggested in the [NEXT]: """


def custom_selector(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
    if len(messages) == 1:
        return "planner_agent"

    last = messages[-1]
    if last.source == "user":
        return "planner_agent"

    # Rule 2 — Any worker just responded → back to planner
    if last.source in ("file_agent", "db_agent", "code_agent"):
        return "planner_agent"

    # Rule 3 — Planner just responded → read ONLY the [NEXT]: tag
    if last.source == "planner_agent":
        content = last.content

        # Extract [NEXT]: <agent_name> — ignore everything else
        match = re.search(r'\[NEXT\]:\s*(\w+)', content)
        if match:
            next_agent = match.group(1).strip()
            # Validate it is an actual participant
            if next_agent in ("file_agent", "db_agent", "code_agent"):
                return next_agent

        # No [NEXT] tag found — TERMINATE condition or end of plan
        return None

    return None

# 4. Define the Team
team = SelectorGroupChat(
    participants=[planner_agent, code_agent, db_agent, file_agent],
    model_client=settings.model_client,
    termination_condition=TextMentionTermination("TERMINATE") | MaxMessageTermination(15),
    selector_prompt=CUSTOM_SELECTOR_PROMPT,
    selector_func=custom_selector,
)