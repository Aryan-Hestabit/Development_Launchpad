import os
from autogen_ext.models.openai import OpenAIChatCompletionClient

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC0KGYhoID8Sc7tb3F6B-dTIxK4Ypsg3rs")
MODEL_ID = "gemini-3.1-flash-lite-preview"

# New requirement: Model Info for non-OpenAI models
MODEL_INFO = {
    "vision": True,
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "family": "unknown",
    "multiple_system_messages": True,
}

# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=MODEL_ID,
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=MODEL_INFO
)
