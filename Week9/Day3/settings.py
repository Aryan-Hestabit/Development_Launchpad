import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCQtlUs-hvBxWZiXYQjg54kuVL8cQd5kgU")
MODEL_ID = "gemini-3.1-flash-lite-preview"



# New requirement: Model Info for non-OpenAI models
MODEL_INFO = {
    "vision": True,
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "family": "unknown" 
}


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")