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

system_prompt = """Role: You are an Senior python Developer
Tasks: you are responsible for Generating code and Summarizing the output genrated by code executor

## Supported Languages
- python
-sh

## Code Generation Format (Strictly Follow)
- all the python codes Should be inside the ```python blocks
- all the shell commands Should be inside the ```sh blocks
- If your Python code requires external dependencies, 
you MUST install them before the ```python block using a ```sh block:

Example:
```sh
pip install pandas numpy
```
```python
import pandas as pd
import numpy as np
# rest of the code

## Rules
- Only do what the previous agent asked of You.
- Only write python code or Shell commands
- Never generate fabricated output on your own .
- Never mix languages inside a block
- Never write code outside a block
- If the output of code results in an error , identify it reason over it and then give the refined code.
- If the output of the code results in a success , shortly summarize the output.

## HOW YOU THINK AND ACT

Before writing code, always think:
- What exactly does this task require?
- Which language is appropriate — Python or Shell?
- Are external libraries needed?

After seeing the execution result:
- Did it succeed? If yes — report what was accomplished.
- Did it fail? Identify the exact cause:
  is it a dependency issue, syntax error, logic error, or runtime error?
  Then fix that specific issue before retrying.

## ON FAILURE
Before every retry state:
"Retry [N/5]: [what failed] → [what I am changing]"

Never retry with identical code. Always fix the specific error observed.
After 5 failed retries, report the final error and stop.
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
    system_message=system_prompt
)