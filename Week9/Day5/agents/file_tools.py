import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from Config import settings
from autogen_core.model_context import BufferedChatCompletionContext
# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

from autogen_ext.models.ollama import OllamaChatCompletionClient

# Qwen 2.5 (7B or 14B) is highly recommended for coding tasks
qwen_client = OllamaChatCompletionClient(
    model="qwen2.5:7b",
    host="http://127.0.0.1:11434",
)



def list_workspace_files() -> str:
    """Lists all files available in the restricted workspace."""
    files = os.listdir(settings.WORKSPACE_DIR)
    return f"Available files: {files}" if files else "The workspace is currently empty."

def write_to_file(filename: str, content: str) -> str:
    """Writes or overwrites a file in the workspace."""
    path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(filename))
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filename}."
    except Exception as e:
        return f"File Error: {str(e)}"

def read_from_file(filename: str) -> str:
    """Reads the content of a file from the workspace."""
    path = os.path.join(settings.WORKSPACE_DIR, os.path.basename(filename))
    if not os.path.exists(path):
        return f"Error: {filename} does not exist."
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Read Error: {str(e)}"
    
file_agent = AssistantAgent(
    name="file_agent",
    model_client=settings.model_client,
    tools=[ 
        list_workspace_files, 
        write_to_file, 
        read_from_file
    ],
    system_message="""You are the @file_agent.
    - Use 'list_workspace_files' to see the list of files in the directory.
    - Use 'read_from_file' in order to read file data.
    - Use 'write_to_file' if you need to create or add content to a file.
    - Provide a clear summary of the file contents.
    - After finishing, return control to @primary_agent.
    """,
    model_context=BufferedChatCompletionContext(buffer_size=10)
    )