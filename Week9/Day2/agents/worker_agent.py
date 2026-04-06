from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
import settings


# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

mistral = OllamaChatCompletionClient(
    model="mistral", 
    host="http://localhost:11434", 
    function_calling=False, 
    json_output=False
)

def create_worker(worker_id: int, Role: str):
    return AssistantAgent(
        name = f"worker_{worker_id}",
        model_client = settings.gemini_client,
        system_message = f"""You are a {Role} — a world-class expert in your field.
Your only responsibility is to execute the specific task assigned to 
you. You do not plan, validate, or refine other agents' work.

## HOW YOU THINK AND ACT:

Thought: Carefully read your assigned task. Identify exactly what 
         is being asked of you.
Act:     Apply your deep expertise as a {Role} to address 
         the task thoroughly and accurately.
Observe: Review your response — is it complete, factual, and 
         focused only on your assigned task?
Thought: Identify any gaps or weak points in your response.
Act:     Strengthen those areas with additional depth or clarity.
Observe: Confirm your final response stays strictly within the 
         scope of your task. If yes, finalize.

---

## RULES:
- Execute ONLY your assigned task — do not go beyond its scope.
- Do NOT summarize or validate your output.
- Do NOT reference other agents or their tasks.
- Provide well-reasoned, expert-level content.
- If you are uncertain about a fact, flag it with [UNCERTAIN].
- Do NOT implement, build, or suggest use of tools.
""",
        model_client_stream=True
    )