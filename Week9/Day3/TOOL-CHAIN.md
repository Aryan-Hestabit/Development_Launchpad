# Tool Chain Documentation - Day3

## Overview

The Day3 implementation features a multi-agent system built with AutoGen that provides a comprehensive tool chain for data processing, code execution, and file management tasks. The system uses specialized agents that work together through an orchestrator to handle complex workflows securely and efficiently.

## Architecture

The system consists of 4 agents organized in a SelectorGroupChat:

1. **Planner Agent** - Strategic coordinator and task delegator
2. **Code Agent** - Code execution specialist
3. **DB Agent** - Database management specialist
4. **File Agent** - File system management specialist

## Tool Chain Components

### 1. Code Execution Tool Chain

**Agent**: Code Agent (`code_agent`)
**Executor**: Docker-based Code Executor
**Capabilities**:

- Executes Python and Shell scripts in isolated Docker containers
- Supports `python` and `sh` code blocks
- Automatic dependency installation for Python packages
- Security approval system with forbidden keyword filtering
- Self-correction with up to 5 retries on errors

**Security Features**:

- User approval required for all code execution
- Forbidden operations: file deletion, permission changes
- Isolated execution environment (Python 3.12-slim Docker image)
- 300-second timeout per execution

**Tools**:

- `docker_executor`: DockerCommandLineCodeExecutor with workspace volume mapping

### 2. Database Tool Chain

**Agent**: DB Agent (`db_agent`)
**Capabilities**:

- CSV to SQLite conversion
- SQL query execution (SELECT and modifications)
- Table schema inspection
- Database structure analysis

**Tools**:

- `csv_to_sqlite(csv_name, db_name, table_name)`: Converts CSV files to SQLite tables
- `execute_sql(db_name, query)`: Runs SQL queries on SQLite databases
- `describe_table(db_name, table_name)`: Returns table structure, columns, foreign keys, and indexes

**Rules**:

- Always inspects table schema before executing queries
- Cannot convert databases back to CSV format

### 3. File Management Tool Chain

**Agent**: File Agent (`file_agent`)
**Capabilities**:

- Workspace file listing
- File reading (text and CSV)
- File writing/overwriting

**Tools**:

- `list_workspace_files()`: Lists all files in the restricted workspace
- `read_from_file(filename)`: Reads file content as string
- `write_to_file(filename, content)`: Writes string content to files

**Rules**:

- Always lists files before other operations
- Cannot perform operations outside the workspace directory
- Supports .txt and .csv file formats

## Orchestration Flow

### Task Processing Workflow

1. **User Query** → **Planner Agent**
2. **Planner Agent** analyzes request and breaks into sequential steps
3. **Planner Agent** delegates to appropriate specialist agent using @mentions
4. **Specialist Agent** executes task and reports results
5. **Planner Agent** reviews results and assigns next step
6. **Repeat** until all steps completed
7. **Planner Agent** calls **Reporter Agent** for final summary
8. **Reporter Agent** provides comprehensive summary and terminates

### Routing Logic

The system uses a custom selector function with these rules:

- New user tasks route to Planner Agent
- @mentions in messages determine next agent
- Specialists return to Planner for review after completion
- Completed workflows route to Reporter Agent

## Security and Safety

- **Code Execution**: Requires explicit user approval, runs in Docker isolation
- **File Operations**: Restricted to designated workspace directory
- **Database Operations**: Read-only inspection, controlled modifications
- **Error Handling**: Automatic retries, comprehensive error reporting

## Configuration

**Environment Requirements**:

- Docker for code execution
- Python 3.12+ image
- Workspace directory for file operations

**Settings** (from `settings.py`):

- Model client configuration
- Workspace directory path
- Docker image specifications

## Usage Examples

### Data Analysis Workflow

1. File Agent lists available CSV files
2. DB Agent converts CSV to SQLite database
3. DB Agent executes analytical queries
4. Code Agent generates visualization scripts
5. File Agent saves results
6. Reporter Agent summarizes findings

### Code Development Workflow

1. File Agent reads existing code files
2. Code Agent executes and tests modifications
3. File Agent writes updated code
4. DB Agent stores test results
5. Reporter Agent documents changes

## Termination Conditions

The system terminates when:

- Reporter Agent outputs "TERMINATE"
- Maximum turns (15) reached
- User exits the application
