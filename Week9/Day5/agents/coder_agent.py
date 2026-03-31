from autogen_agentchat.agents import CodeExecutorAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.agents import CodeExecutorAgent, ApprovalRequest, ApprovalResponse
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from Config import settings
from autogen_core.model_context import BufferedChatCompletionContext

# 1. Define the Docker Executor
# We specify the work_dir (Volume Mapping) and the base image
docker_executor = DockerCommandLineCodeExecutor(
    work_dir=settings.WORKSPACE_DIR,
    image="python:3.12-slim",
    timeout=30  # seconds
)

def simple_approval_func(request: ApprovalRequest) -> ApprovalResponse:
    forbidden_keywords = ["os.remove", "shutil.rmtree", "os.rmdir", "chmod"]
    for keyword in forbidden_keywords:
        if keyword in request.code:
            return ApprovalResponse(approved=False, reason=f"Security Violation: '{keyword}' is forbidden.")
    """Simple approval function that requests user input for code execution approval."""
    print("Code execution approval requested:")
    print("=" * 50)
    print(request.code)
    print("=" * 50)

    while True:
        user_input = input("Do you want to execute this code? (y/n): ").strip().lower()
        if user_input in ['y', 'yes']:
            return ApprovalResponse(approved=True, reason='Approved by user')
        elif user_input in ['n', 'no']:
            return ApprovalResponse(approved=False, reason='Denied by user')
        else:
            print("Please enter 'y' for yes or 'n' for no.")
# Note: In your main entry point, you must call:
# await docker_executor.start()

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
    host="http://127.0.0.1:11434"
)

CODER_PROMPT = """
You are the @coder_agent of NEXUS AI.
Your goal is to solve technical tasks by writing and executing code.

CAPABILITIES:
- Languages: python, bash, sh.
- Lifecycle: You write code, run it, and if it fails, you analyze the output and fix it.
- Approval: You must present your code clearly before execution.

INSTRUCTIONS:
1. Always use print() to output results so you can see them.
2. Always install packages which are needed to run the python script by using ```sh pip install <package> ```.
3. If your code fails, analyze the error message and fix it in the next turn.
4. Verify your work by running a final test script.
"""

code_agent = CodeExecutorAgent(
    name="code_agent",
    code_executor=docker_executor,
    model_client=gemini_client,    # Enable Self-Correction
    max_retries_on_error=5,        # Auto-retry 5 times
    approval_func=simple_approval_func, # User approval before execution
    supported_languages=["python", "bash", "sh"],
    # Requirement 4: Auto-install packages within the code blocks
    system_message=CODER_PROMPT,
    model_context=BufferedChatCompletionContext(buffer_size=10),
    model_client_stream=True
)