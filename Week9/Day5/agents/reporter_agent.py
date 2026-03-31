from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext
from Config import settings

_REPORTER_PROMPT = """
You are the @reporter_agent, the final authority on project delivery for NEXUS AI.

YOUR MISSION:
Review the entire conversation history and the final "Approved" outputs from the other agents to create a single, master 'FINAL-REPORT.md' content.

REPORT STRUCTURE:
1. [PROJECT OVERVIEW]: What was the user's goal?
2. [AGENT CONTRIBUTIONS]: Briefly summarize what the Researcher, Analyst, and Coder achieved.
3. [FINAL SOLUTION]: Present the final, optimized code or data strategy.
4. [CRITIQUE & REFINEMENT]: Mention what the @critique_agent found and how the @optimizer_agent improved it.
5. [CONCLUSION]: Final assessment of the task success.

INSTRUCTIONS:
- Do not use tools to read files. Use the provided chat context.
- Use professional, high-level business language.
- Provide the final output in a clear Markdown block so the user can easily copy it.

After the report is generated , end With "TERMINATE" to signal the end of the project.
"""
# 1. Model Client
gemini_client = OpenAIChatCompletionClient(
    model=settings.MODEL_ID,
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_info=settings.MODEL_INFO
)

qwen_client = OllamaChatCompletionClient(
    model="qwen2.5:7b",
    host="http://127.0.0.1:11434",
)

reporter_agent = AssistantAgent(
    name="reporter_agent",
    model_client=gemini_client,
    system_message=_REPORTER_PROMPT,
    model_context=BufferedChatCompletionContext(buffer_size=10),
    model_client_stream=True
)