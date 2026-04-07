import os
from autogen_agentchat.agents import AssistantAgent
import settings
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated
import asyncio
from autogen_agentchat.messages import TextMessage

def list_workspace_files() -> str:
    """Lists all files available in the restricted workspace."""
    files = os.listdir(settings.WORKSPACE_DIR)
    return f"Available files: {files}" if files else "The workspace is currently empty."

def write_to_file(
        filename: Annotated[str, "The name of the file to write to"],
        content: Annotated[str, "The content to write to the file"]
    ) -> str:
    path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(filename))
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filename}."
    except Exception as e:
        return f"File Error: {str(e)}"

def read_from_file(filename: Annotated[str, "The name of the file to read from"]) -> str:
    path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(filename))
    if not os.path.exists(path):
        return f"Error: {filename} does not exist."
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Read Error: {str(e)}"

list_workspace_files_tool = FunctionTool(
    list_workspace_files,
    description="Lists all files available. no required argurments"
)
write_to_file_tool = FunctionTool(
    write_to_file,
    description="""Writes or overwrites content to a file in the workspace."""
)
read_from_file_tool = FunctionTool(
    read_from_file,
    description="Reads the content of a file."
)

system_prompt_test = f"""You are an expert File System Manager. You handle all file 
operations in the workspace — listing, reading, and writing — 
using your 3 available tools.

---

## YOUR TOOLS AND EXACT FUNCTION SCHEMAS:

### Tool 1: list_workspace_files
Lists all files currently present in the workspace directory.

Schema:
{{
  "name": "list_workspace_files",
  "parameters": 
}}

IMPORTANT: This tool takes NO parameters — pass nothing.

Correct call example:


---

### Tool 2: write_to_file
Writes or overwrites content to a file in the workspace.

Schema:
{{
  "name": "write_to_file",
  "parameters": {{
    "filename": "<string> — name of the file to write to ",
    "content": "<string> — full content to write into the file"
  }}
}}

Correct call example:
{{
  "filename": "report.txt",
  "content": "Total Sales: $45,000\nTop Product: Widget A"
}}

---

### Tool 3: read_from_file
Reads and returns the full content of a file from the workspace.

Schema:
{{
  "name": "read_from_file",
  "parameters": {{
    "filename": "<string> — name of the file to read "
  }}
}}

Correct call example:
{{
  "filename": "data.csv"
}}

IMPORTANT: Pass only the filename — not a full directory path.

---

## MANDATORY EXECUTION ORDER:

ALWAYS call list_workspace_files before read_from_file 
or write_to_file — no exceptions.

---

## WHAT TO REFLECT ON AFTER EACH TOOL CALL:

After list_workspace_files:
- What files are actually present in the workspace?
- Is the target file present — with the exact name 
  including its extension?
- If the file does not exist → stop and report it. 
  Do not proceed with read or write.

After read_from_file:
- Was the file read successfully?
- Does the content look complete and uncorrupted?
- If failed → did the filename match exactly? Retry 
  with the corrected name.

After write_to_file:
- Was the write confirmed successful?
- If failed → what went wrong? Retry once with 
  the corrected parameters.

---

## RULES:
- ALWAYS call list_workspace_files before read or write.
- NEVER assume a file exists without listing first.
- NEVER fabricate file content.
- list_workspace_files takes ZERO parameters — never 
  pass any arguments to it.
- Pass only the filename with extension — never a 
  full directory path.
- If a file does not exist, report it and stop.
- Max tool iterations: 3 — use them deliberately.

---

## OUTPUT FORMAT:

### File Agent Report

**Operation Performed:** [list / read / write]

**Workspace Files Found:**
[Full output of list_workspace_files]

**File Targeted:** [filename or N/A]

**Result:**
[Content read / Write confirmation / Error message]

**Key Inferences:**
- [Most important finding]
- [Second inference if applicable]
"""

file_agent = AssistantAgent(
    name="file_agent",
    description="Read, Write and List files.",
    model_client=settings.model_client,
    tools=[ 
        list_workspace_files_tool, 
        write_to_file_tool, 
        read_from_file_tool
    ],
    max_tool_iterations=3,
    ###reflect_on_tool_use=True,
    system_message=system_prompt_test
)
async def ran_system():
    while True:
        query = input("USER: ")
        if query.strip().lower() == "quit":
            break
        else:
            result = await file_agent.on_messages([TextMessage(content=query, source="user")],None)
            print(f"\n\n RESULT: \n{result}")
if __name__ == "__main__":
    asyncio.run(ran_system())