import os
from dotenv import load_dotenv
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "gemini-3.1-flash-lite-preview"

# New requirement: Model Info for non-OpenAI models
MODEL_INFO = {
    "vision": True,
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "family": "unknown" 
}

# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=MODEL_ID,
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=MODEL_INFO
)
GROQ_MODEL_INFO = ModelInfo(
    vision=False,            # Most Groq models don't support vision yet
    function_calling=True,   # Essential for your tools
    json_output=True,        # Great for structured reporting
    family="unknown",         # Prevents AutoGen from applying GPT-specific logic
    structured_output=True
)

groq_client = OpenAIChatCompletionClient(
    model="llama-3.3-70b-versatile", # Or "llama3-8b-8192"
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    model_info=GROQ_MODEL_INFO,
    include_name_in_message=False  
)
# Qwen 2.5 (7B or 14B) is highly recommended for coding tasks
qwen_client = OllamaChatCompletionClient(
    model="qwen2.5:7b",
    host="http://127.0.0.1:11434"
)

qwen_coder_client = OllamaChatCompletionClient(
    model="qwen2.5-coder:7b",
    host="http://127.0.0.1:11434"
)

model_client = qwen_client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")