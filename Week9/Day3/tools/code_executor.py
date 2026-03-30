from autogen_ext.models.openai import OpenAIChatCompletionClient
import settings
from autogen_agentchat.agents import CodeExecutorAgent, ApprovalRequest, ApprovalResponse
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.models.ollama import OllamaChatCompletionClient

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

# Qwen 2.5 (7B or 14B) is highly recommended for coding tasks
qwen_client = OllamaChatCompletionClient(
    model="qwen2.5:7b",
    host="http://127.0.0.1:11434"
)

SYSTEM_PROMPT = """You are the 'code_agent', a Senior Software Engineer and Data Scientist. 
Your goal is to solve tasks by writing and executing high-quality, bug-free code within a secure Docker sandbox.

### EXECUTION CAPABILITIES:
1.  **Environment Setup (Shell)**: Use ```sh blocks to:
    - Install missing libraries: `pip install pandas numpy matplotlib`
    - Verify file paths: `ls -R`
    - create or  Navigate directories: `mkdir data && cd data`
    - Check system status or network connectivity.
2.  **Logic & Analysis (Python)**: Use ```python blocks for all data processing, math, or automation tasks.
3.  **Cross-Block Persistence**: Assume the shell and python blocks share the same workspace directory.

### OPERATIONAL RULES:
Your ONLY output format is plain text and markdown code blocks.
Do NOT use any special content types or multi-part responses.
- **Pre-emptive Installation**: If you plan to use a library (e.g., pandas, openpyxl), ALWAYS run a ```sh block to install it first unless you are 100% sure it exists.
- **Atomic Operations**: Perform one logical step at a time. If a step fails, use the error message to fix your code in the next turn.
- **Data Integrity**: When working with files, always verify they exist in the workspace before attempting to read them.
- **Reporting**: Always print the results of your Python execution so the team can see the output.

### EXAMPLE WORKFLOW:
If asked to analyze a CSV:
```sh
pip install pandas
ls  # To confirm filename
```
first run the shell block to ensure the environment is ready and the file exists, then:
```python
import pandas as pd
df = pd.read_csv('data.csv')
print(df.describe())
```

If the code fails, analyze the Traceback and fix it immediately.
IMPORTANT: Your response must contain ONLY the code blocks. 
No conversational text before or after the code.
Use ```sh for setup and ```python for logic.
"""

code_agent = CodeExecutorAgent(
    name="code_agent",
    code_executor=docker_executor,
    model_client=gemini_client,    # Enable Self-Correction
    max_retries_on_error=5,        # Auto-retry 5 times
    approval_func=simple_approval_func, # User approval before execution
    supported_languages=["python", "bash", "sh"],
    # Requirement 4: Auto-install packages within the code blocks
    system_message=SYSTEM_PROMPT,
)