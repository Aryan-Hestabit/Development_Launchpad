from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext

ANSWER_PROMPT = """
Role: Final Communications Lead.
Task: Take a summarized technical report and turn it into a direct answer for the user.
Constraint: Do not add new information. Keep the tone professional and helpful. 
The answer should be the 'Final Answer' that solves the initial user query perfectly.
"""

answer_agent = AssistantAgent(
    name="answer_agent",
    model_client=OllamaChatCompletionClient(model="mistral", host="http://localhost:11434", function_calling=True, json_output=False),
    system_message=ANSWER_PROMPT,
    model_context=BufferedChatCompletionContext(buffer_size=10),
    model_client_stream=True
)