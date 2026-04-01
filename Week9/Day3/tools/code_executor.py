import settings
from autogen_agentchat.agents import CodeExecutorAgent, ApprovalRequest, ApprovalResponse
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

# 1. Define the Docker Executor
# We specify the work_dir (Volume Mapping) and the base image
docker_executor = DockerCommandLineCodeExecutor(
    work_dir=settings.WORKSPACE_DIR,
    image="python:3.12-slim",
    timeout=300  # seconds
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


SYSTEM_PROMPT = """
You are part of an Agent AI team and You are the @code_agent, a specialist in writing and executing Python and Shell codes.

ROLE: your only job is to write and run code , give ```sh blocks for shell commands and ```python blocks for python code.

RULES: 
- Only create ```sh blocks or ```python blocks of code , no other programming languages are allowed.
- Always use properly labeled markdown fenced code blocks. The executor reads these labels.
- If any python code requires external libraries, you must include the installation commands within a ```sh block before the corresponding ```python block. Do not rely on pre-installed packages.
- Always write clean, readable, well-commented code.
- Always print your results explicitly — never rely on implicit output.
- If code fails, read the full error, fix the root cause, and rewrite the code .
- Never omit the language label — unlabelled blocks will not be executed.
- After successful execution, summarize the output clearly in plain language.
- Only report what the code actually produced — never fabricate output.

CRITICAL:
- Never reply with an empty string. If you have no code to run, respond with "No code to execute." instead of an empty response.
"""

code_agent = CodeExecutorAgent(
    name="code_agent",
    description=( "Executes Python and Shell code blocks. Use for scripting, data processing, "
        "calculations, and any task that requires running code." ),
    code_executor=docker_executor,
    model_client=settings.gemini_client,    # Enable Self-Correction
    max_retries_on_error=5,        # Auto-retry 5 times
    approval_func=simple_approval_func, # User approval before execution
    supported_languages=["python", "sh"],
    system_message=SYSTEM_PROMPT,
)