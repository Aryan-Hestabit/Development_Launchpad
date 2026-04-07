# NEXUS AI - Multi-Agent System

A sophisticated multi-agent AI system built on `autogen_agentchat` that decomposes complex user requests into specialized agent workflows, executes code safely in Docker, and stores findings in a dual-memory architecture.

## 🎯 Overview

NEXUS AI is designed to handle complex, multi-faceted user requests by leveraging a team of specialized agents that work together through an orchestrated workflow. The system combines strategic planning, research, analysis, coding, validation, and optimization—all with secure code execution and persistent memory.

**Key Features:**
- 🤖 Multi-agent orchestration with specialized roles
- 🐳 Sandboxed code execution via Docker
- 💾 Dual-memory architecture (session + long-term FAISS)
- ✅ Quality assurance through critique and validation agents
- 📊 Data analysis and SQL query capabilities
- 📝 Final report generation
- 🔐 Safe, approval-based code execution

## 📋 Table of Contents

- [Architecture](#architecture)
- [Components](#components)
- [Installation](#installation)
- [Usage](#usage)
- [Memory System](#memory-system)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Workflow](#workflow)
- [Docker Integration](#docker-integration)

## 🏗️ Architecture

NEXUS AI follows a team-based orchestration pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query Input                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌──────────────────────────────┐
         │   SelectorGroupChat Team     │
         │   (Orchestrator)             │
         └──────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Planner  │   │Research  │   │ Analyst  │
   │ Agent    │   │ Agent    │   │ Agent    │
   └──────────┘   └──────────┘   └──────────┘
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Coder    │   │File Mgmt │   │Critique  │
   │ Agent    │   │ Tools    │   │ Agent    │
   └──────────┘   └──────────┘   └──────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │Validator │   │Optimizer │   │Reporter  │
   │ Agent    │   │ Agent    │   │ Agent    │
   └──────────┘   └──────────┘   └──────────┘
                         │
                         ▼
          ┌──────────────────────────┐
          │   Final Report + Memory  │
          │   Storage                │
          └──────────────────────────┘
```

## 🧩 Components

### 1. **Orchestrator** (`agents/orchestrator.py`)
Central coordinator that manages the multi-agent team using `SelectorGroupChat`. Features:
- Enforces workflow rules (starts with Planner, ends with Reporter)
- Custom `nexus_selector()` function for intelligent agent routing
- Termination conditions (TERMINATE flag or max turns)
- Integrates all specialized agents

### 2. **Planner Agent** (`agents/planner_agent.py`)
Strategic architect that:
- Decomposes complex requests into phases
- Assigns tasks to specialized agents
- Accesses both session and long-term memory
- Maintains buffered chat context

### 3. **Specialized Agents**

#### Research Agent (`agents/research_agent.py`)
- Gathers information and context
- Provides background research for complex tasks

#### Analyst Agent (`agents/analyst_agent.py`)
- Analyzes structured data
- Converts CSV to SQLite
- Executes SQL queries
- Produces tabular insights

#### Coder Agent (`agents/coder_agent.py`)
- Writes and executes code in Docker containers
- Supports Python, Bash, and Shell scripts
- Requires manual approval before execution
- Provides `DockerCommandLineCodeExecutor` with `python:3.12-slim` image

#### File Tools (`agents/file_tools.py`)
- `list_workspace_files()` - Browse workspace
- `read_from_file()` - Read file contents
- `write_to_file()` - Create/modify files

#### Critique Agent (`agents/critique_agent.py`)
- Reviews outputs for flaws and security issues
- Provides structured feedback with strengths and revisions

#### Validator Agent (`agents/validator_agent.py`)
- Compares outputs against original requests
- Checks completeness, accuracy, and realism

#### Optimizer Agent (`agents/optimizer_agent.py`)
- Refines solutions for performance and clarity
- Polishes final outputs before reporting

#### Reporter Agent (`agents/reporter_agent.py`)
- Compiles final delivery report
- Summarizes project goals, agent contributions, and solutions
- Outputs final report in Markdown
- Terminates the agent loop

## 💾 Memory System

NEXUS uses a **dual-memory architecture** for context and learning:

### Session Memory (`memory/session_memory.py`)
- **Scope:** Current session only
- **Purpose:** Running conversation history
- **Use Case:** Short-term context for ongoing tasks
- **Storage:** In-memory buffer with async operations

### Vector Store Memory (`memory/vector_store.py`)
- **Scope:** Long-term persistence
- **Purpose:** Extracted facts and learnings
- **Implementation:** FAISS-based vector storage
- **File:** `faiss.index` (binary index)
- **Use Case:** Retrieving past knowledge across sessions

### Fact Extractor (`memory/fact_extractor.py`)
- Extracts structured facts from queries and responses
- Categorizes facts for semantic understanding
- Feeds facts into FAISS memory

**Data Flow:**
```
User Query → Session Memory → Fact Extraction → FAISS Vector Store
   ↓                                                    ↓
 Agent Response → Session Update              Long-term Knowledge
```

## ⚙️ Configuration

### Settings (`Config/settings.py`)
- Model configuration (OpenAI API)
- API key management
- Workspace path definition: `Day5/nexus_workspace`
- Docker image selection

### Environment Variables (`.env`)
Set the following in your `.env` file:
```
OPENAI_API_KEY=your_api_key_here
WORKSPACE_DIR=/path/to/nexus_workspace
```

## 📂 Project Structure

```
Day-5/
├── README.md                    # This file
├── ARCHITECTURE.md              # Detailed architecture documentation
├── main.py                      # Entry point & session loop
├── Config/
│   ├── settings.py              # Configuration management
│   └── .env                     # Environment variables
├── agents/
│   ├── orchestrator.py          # Team orchestration & routing
│   ├── planner_agent.py         # Strategic planning agent
│   ├── research_agent.py        # Information gathering
│   ├── analyst_agent.py         # Data analysis & SQL
│   ├── coder_agent.py           # Code execution in Docker
│   ├── file_tools.py            # File system operations
│   ├── critique_agent.py        # Quality review
│   ├── validator_agent.py       # Output validation
│   ├── optimizer_agent.py       # Solution refinement
│   └── reporter_agent.py        # Final report generation
├── memory/
│   ├── session_memory.py        # Short-term context storage
│   ├── vector_store.py          # FAISS-based long-term memory
│   ├── fact_extractor.py        # Fact extraction logic
│   ├── faiss.index              # FAISS vector database
│   └── logs/                    # Session logs
├── nexus_ai/
│   ├── config.py                # Additional configuration
│   └── main.py                  # Secondary entry point
├── nexus_workspace/             # Sandboxed execution directory
└── logs/                        # System logs
```

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Docker (for sandboxed code execution)
- OpenAI API key

### Setup

1. **Clone/Navigate to Project:**
   ```bash
   cd Day-5
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment:**
   - Copy `.env.example` to `.env` (if available)
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=sk-...
     ```

5. **Verify Docker:**
   ```bash
   docker --version
   ```

6. **Initialize FAISS Memory:**
   ```bash
   python -c "from memory.vector_store import FAISSVectorMemory; m = FAISSVectorMemory(); m.initialize()"
   ```

## 💻 Usage

### Starting the System

```bash
python main.py
```

You'll see:
```
 NEXUS ONLINE | Session: a1b2c3d4
Starting Docker Environment...
```

### User Interaction

**Interactive Query Loop:**
```
User: Analyze this CSV file and find trends

[System processes through agent team]
[Final report is generated]

User: facts

[All learned facts displayed]

User: exit
```

### Special Commands

| Command | Purpose |
|---------|---------|
| `facts` | Display all stored facts from current and past sessions |
| `exit` / `quit` | Cleanly shutdown the system |
| Regular query | Trigger the agent workflow |

### Example Workflows

**Example 1: Data Analysis**
```
User: Read data.csv, analyze trends, generate insights
→ File agent reads CSV
→ Analyst converts to SQLite  
→ Coder runs analysis scripts
→ Reporter summarizes findings
```

**Example 2: Code Generation**
```
User: Create a web scraper for news articles
→ Planner breaks down requirements
→ Coder generates Python script
→ Critique reviews security
→ Validator checks functionality
→ Optimizer improves performance
→ Reporter provides final solution
```

## 🔄 Workflow

The typical execution flow:

1. **Start:** System initializes with session ID and memory layers
2. **Input:** User enters a query
3. **Planning:** Planner decomposes request into subtasks
4. **Execution:** Specialized agents handle their domains
   - Research: Gathers context
   - Analyst: Processes data
   - Coder: Writes/executes code
   - File Tools: Manages files
5. **Quality Assurance:**
   - Critique: Reviews for issues
   - Validator: Checks completeness
   - Optimizer: Refines output
6. **Reporting:** Reporter compiles final results
7. **Memory:** Facts extracted and stored for future reference
8. **Loop:** System waits for next query or exit

## 🐳 Docker Integration

### Code Execution Environment

- **Image:** `python:3.12-slim`
- **Executor:** `DockerCommandLineCodeExecutor`
- **Supported Languages:** Python, Bash, Shell
- **Sandbox:** All code runs in isolated `nexus_workspace/` directory
- **Approval:** Manual approval required before execution

### Starting Docker

```python
await docker_executor.start()  # Starts in main.py
```

### Stopping Docker

```python
await docker_executor.stop()   # Called in finally block
```

### Security Features

- ✅ Code sandboxed in Docker container
- ✅ Manual approval before execution
- ✅ Workspace isolation
- ✅ Resource limits via Docker

## 🔐 Security Considerations

1. **API Key Management:**
   - Store `OPENAI_API_KEY` in `.env`, never commit
   - Use `.gitignore` to exclude sensitive files

2. **Code Execution:**
   - All code runs in Docker
   - Requires manual approval before running
   - Sandboxed to `nexus_workspace/`

3. **Memory Storage:**
   - Session logs stored in `memory/logs/`
   - FAISS index contains embeddings
   - No sensitive data should be in memory

## 📊 Logging

Session logs are automatically created:

```
memory/logs/nexus_xxxxxxxx.log
```

Log format:
```
2025-01-15 10:30:45,123 | INFO | --- SESSION START: a1b2c3d4-... ---
2025-01-15 10:30:46,456 | INFO | USER_QUERY: analyze data trends
2025-01-15 10:30:52,789 | INFO | FACTS_LEARNED: 3
2025-01-15 10:31:00,012 | INFO | --- SESSION END ---
```

## 🛠️ Development

### Adding a New Agent

1. Create file in `agents/` directory
2. Define agent class with appropriate tools
3. Register in `orchestrator.py`
4. Update routing logic in `nexus_selector()`

### Extending Memory

1. Modify `fact_extractor.py` for new fact formats
2. Update FAISS schema in `vector_store.py`
3. Retrain/reinitialize FAISS index

### Custom Tools

1. Create tool function with proper signatures
2. Register in corresponding agent's tool list
3. Document tool description for LLM context

## 📚 Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed technical architecture
- Individual agent files - Agent-specific implementation details
- `Config/settings.py` - Configuration reference

## 🤝 Contributing

To contribute improvements:

1. Follow the modular agent pattern
2. Add logging for debugging
3. Test in local environment first
4. Document changes in code comments
5. Update ARCHITECTURE.md if adding major components

## 📝 Notes

- **Iterative Workflows:** System designed for multi-turn, task-driven interactions, not single-turn chat
- **TERMINATE Signal:** Agents can signal end-of-task with `TERMINATE` to close workflow
- **Memory Persistence:** Facts persist across sessions; session memory is ephemeral
- **Async Operations:** All agent interactions are async; use `await` consistently

## ❓ Troubleshooting

### Docker Not Found
```bash
# Ensure Docker is installed and running
docker version
```

### FAISS Index Error
```bash
# Reinitialize memory
python -c "from memory.vector_store import FAISSVectorMemory; FAISSVectorMemory().initialize(force=True)"
```

### Agent Not Responding
- Check logs in `memory/logs/`
- Verify internet connection for API calls
- Ensure Docker container is running
