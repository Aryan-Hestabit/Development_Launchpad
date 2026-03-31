import os
from pathlib import Path

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCQtlUs-hvBxWZiXYQjg54kuVL8cQd5kgU")
MODEL_ID = "gemini-3.1-flash-lite-preview"

# New requirement: Model Info for non-OpenAI models
MODEL_INFO = {
    "vision": True,
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "family": "unknown",
}

# Base directory of your project
BASE_DIR = Path(__file__).resolve().parent.parent

# WORKSPACE_DIR: The physical folder on your HOST machine 
# that Docker will 'see' as its internal home.
WORKSPACE_DIR = str(BASE_DIR / "nexus_workspace")
