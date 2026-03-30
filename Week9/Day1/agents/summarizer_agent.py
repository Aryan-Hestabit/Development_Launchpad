from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext

SUMMARIZER_PROMPT = """
Role: Information Architect & Summarizer.
Task: Receive long-form research and distill it into a structured summary.
Constraint: Maintain all key technical facts but reduce the word count by 60%.
Don't add any facts from your own knowledge. 
Use bullet points for readability. Ensure the output is concise enough to allow 
the next agent to process the full history.
"""

summarizer_agent = AssistantAgent(
    name="summarizer_agent",
    model_client=OllamaChatCompletionClient(model="mistral", host="http://localhost:11434", function_calling=True, json_output=False),
    system_message=SUMMARIZER_PROMPT,
    model_context=BufferedChatCompletionContext(buffer_size=10)
)