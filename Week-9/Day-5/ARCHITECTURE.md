# Day 5 Architecture

## Overview
Day 5 implements a multi-agent NEXUS AI system built on `autogen_agentchat` and memory storage. The system is designed to handle complex user requests by decomposing them into a team workflow, executing code safely in Docker, analyzing data, validating outputs, and generating final reports.

## Key Components

### 1. Entry Point
- `main.py`
- Creates the session, logger, and memory layers.
- Initializes the Nexus team via `agents.orchestrator.create_nexus_team()`.
- Starts Docker code execution environment.
- Receives user queries in a loop.
- Stores user interaction history in short-term session memory and extracted facts in long-term FAISS memory.

### 2. Orchestrator / Team Selector
- `agents/orchestrator.py`
- Builds the `SelectorGroupChat` team with:
  - `planner_agent`
  - `research_agent`
  - `analyst_agent`
  - `code_agent`
  - `file_agent`
  - `critique_agent`
  - `validator_agent`
  - `optimizer_agent`
  - `reporter_agent`
- Uses both a custom `nexus_selector()` function and a selector prompt to enforce workflow rules.
- Ensures the system starts with `planner_agent` and ends with `reporter_agent`.
- Applies termination conditions: mention-based `TERMINATE` or maximum turns.

### 3. Planner Agent
- `agents/planner_agent.py`
- Acts as the strategic architect.
- Decomposes user requests into phases and assigns tasks to specialized agents.
- Has access to both session memory and FAISS long-term memory.
- Uses a buffered chat context to preserve recent history.

### 4. Specialized Agents

#### Research Agent
- `agents/research_agent.py` (not shown in full here but imported by orchestrator)
- Responsible for information gathering and context research.

#### Analyst Agent
- `agents/analyst_agent.py`
- Analyzes structured data.
- Provides tools for:
  - CSV to SQLite conversion
  - SQL query execution
- Produces tabular insights and strategic interpretation.

#### Coder Agent
- `agents/coder_agent.py`
- Writes and executes code in a Docker container.
- Uses `DockerCommandLineCodeExecutor` with a `python:3.12-slim` image.
- Supports Python, Bash, and SH.
- Has an approval function for user-approved execution.

#### File Agent
- `agents/file_tools.py`
- Handles workspace file operations:
  - `list_workspace_files`
  - `read_from_file`
  - `write_to_file`

#### Critique Agent
- `agents/critique_agent.py`
- Reviews outputs for flaws, security issues, and logical gaps.
- Returns structured feedback with strengths and required revisions.

#### Validator Agent
- `agents/validator_agent.py`
- Compares original requests against final outputs.
- Checks completeness, accuracy, and realism.

#### Optimizer Agent
- `agents/optimizer_agent.py` (not shown in read files but imported by orchestrator)
- Refines the final solution for performance, clarity, and polish.

#### Reporter Agent
- `agents/reporter_agent.py`
- Produces the final delivery report.
- Summarizes the project goal, agent contributions, final solution, critique, and optimizations.
- Outputs the final report in Markdown and terminates the session.

## Memory System
- `memory/session_memory.py`
  - Stores the running conversation history for short-term context.
- `memory/vector_store.py`
  - Uses `FAISSVectorMemory` to store extracted facts.
- `memory/fact_extractor.py`
  - Extracts structured facts from user queries and agent outputs.
- Data flow:
  1. User query enters system.
  2. Session memory logs the query and response.
  3. Fact extractor derives new facts.
  4. FAISS memory stores facts as long-term knowledge.

## Configuration
- `Config/settings.py`
- Defines model settings, API keys, and workspace path.
- Uses `OpenAIChatCompletionClient` for the main model.
- Defines `WORKSPACE_DIR` as the host folder accessible to Docker: `Day5/nexus_workspace`.

## Execution Workflow
1. Start the system.
2. User enters a query.
3. Orchestrator starts with `planner_agent`.
4. Planner delegates subtasks to specialized agents.
5. Agents may research, analyze, code, read/write files, critique, validate, and optimize.
6. `reporter_agent` compiles the final result.
7. System logs outcomes and stores memory.
8. User may request stored facts with the `facts` command.

## Docker + Code Execution
- Docker is started in `main.py` through `coder_agent.docker_executor.start()`.
- All code execution is sandboxed within `WORKSPACE_DIR`.
- The code agent requires manual approval before executing generated code.

## Design Principles
- Modular agent specialization for clarity and accountability.
- Responsible orchestration with a planner and selector logic.
- Dual memory architecture for short-term context and long-term facts.
- Secure execution through Docker and explicit approval.
- Final report generation as a dedicated end-stage responsibility.

## Notes
- `main.py` is the user-facing runtime loop.
- The system is built for iterative, task-driven workflows rather than single-turn chat.
- `TERMINATE` signals end-of-task and closes the agent loop cleanly.
