# Day 2: Multi-Agent Orchestration Flow

This document outlines the hierarchical architecture and task-delegation logic of our autonomous system.

## 1. System Architecture (DAG)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER QUERY                                         │
│            "Switch city bus fleet to Hydrogen or Electric?"                 │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PLANNER AGENT                                           │
│              (orchestrator/planner.py)                                      │
│    Decompose query into JSON sub-tasks (max 5)                              │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                    ┌────────┴───────┐
                    │ Parsed JSON    │
                    │   Task List    │
                    └────────┬───────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Worker 1    │  │  Worker 2    │  │  Worker N    │
    │ (Specialty A)│  │ (Specialty B)│  │(Specialty C) │
    └──────────────┘  └──────────────┘  └──────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼───────┐
                    │  RESULT        │
                    │  AGGREGATOR    │
                    │  (Combined     │
                    │   Reports)     │
                    └────────┬───────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              REFLECTION AGENT                                               │
│         (agents/reflection_agent.py)                                        │
│    Critique worker outputs for contradictions & gaps                        │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                    ┌────────▼───────┐
                    │  Critique      │
                    │  Output        │
                    └────────┬───────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              VALIDATOR AGENT                                                │
│         (agents/validator.py)                                               │
│    Synthesize final professional response                                   │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FINAL ANSWER                                            │
│                  (to User)                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Implemented Behavior from Code (Day2)
- `planner_agent` is in `orchestrator/planner.py`:
  - role: break query into tasks (max 5)
  - output must be JSON array of tasks
- `worker_agent.create_worker` builds `AssistantAgent` with an on-the-fly Role message
- All workers run in parallel using `asyncio.gather`
- Reflection is performed by `reflection_agent`
- Final synthesis by `validator_agent`

## 3. Important Runtime Notes
- `main.py` uses safe JSON fallback when planner output is invalid.
- Task creation is dynamic by extraction of `id` and `Role`.
- Combine worker results into one report string before reflection and validation.
