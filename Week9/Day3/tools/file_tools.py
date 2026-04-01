import os
from autogen_agentchat.agents import AssistantAgent
import settings
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated

def list_workspace_files() -> str:
    """Lists all files available in the restricted workspace."""
    files = os.listdir(settings.WORKSPACE_DIR)
    return f"Available files: {files}" if files else "The workspace is currently empty."

def write_to_file(
        filename: Annotated[str, "The name of the file to write to"],
        content: Annotated[str, "The content to write to the file"]
    ) -> str:
    """Writes or overwrites a file in the workspace."""
    path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(filename))
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filename}."
    except Exception as e:
        return f"File Error: {str(e)}"

def read_from_file(filename: Annotated[str, "The name of the file to read from"]) -> str:
    """Reads the content of a file from the workspace."""
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
    description="Lists all files available in the restricted workspace."
)
write_to_file_tool = FunctionTool(
    write_to_file,
    description="Writes or overwrites a file in the workspace, files can be txt or csv. Args: filename, content"
)
read_from_file_tool = FunctionTool(
    read_from_file,
    description="Reads the content of a file from the workspace, files can be txt or csv.. Args: filename"
)

file_agent = AssistantAgent(
    name="file_agent",
    description=("Workspace file specialist. Three tools: "
        "list_workspace_files() to see available files, "
        "read_from_file(filename) to read file content,it can read both csv and txt files  "
        "write_to_file(filename, content) to save content. "
        "Use for all file read, write, and list operations exclusively."),
    model_client=settings.model_client,
    tools=[ 
        list_workspace_files_tool, 
        write_to_file_tool, 
        read_from_file_tool
    ],
    max_tool_iterations=3,
    reflect_on_tool_use=True,
    system_message="""You are part of an Agent AI team and You are @file_agent — a specialist in file management.

    CAPABILITIES: 
    - Can read files (plain text or CSV) and return their content as strings through read_from_file_tool(filename).
    - Can write strings to files (plain text or CSV) using write_to_file_tool(filename, content).
    - Can list all files in the workspace with list_workspace_files_tool().
    - Can call multiple tools in squence to accomplish complex file-related tasks.

    RULES:
    - Always uses the exact filename when reading or writing. Never assumes a file exists without checking first.
    - Cannot execute code, manipulate databases, or perform any operations beyond file management.
    - Always run the list_workspace_files_tool() first before running any other tool.
    - If a file does not exist when trying to read, report the error and wait for new instructions.Do not attempt to create or modify files unless explicitly instructed by the primary agent.

    CRITICAL:
    - Never reply with an empty string. If you have no data to return, please return "No data to return." instead of an empty string.
    """
)