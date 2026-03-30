# Day 2: Multi-Agent Orchestration Flow

This document outlines the hierarchical architecture and task-delegation logic of our autonomous system.

## 1. System Architecture (DAG)

``` mermaid
graph TD
    User([User Query]) --> Planner{Orchestrator/Planner}
    
    subgraph Parallel_Execution [Worker Phase]
        Planner -->|Task 1| W1[Worker 1: Specialty A]
        Planner -->|Task 2| W2[Worker 2: Specialty B]
        Planner -->|Task 3| W3[Worker 3: Specialty C]
    end
    
    W1 --> Aggregator[Result Aggregator]
    W2 --> Aggregator
    W3 --> Aggregator
    
    Aggregator --> Critic[Reflection Agent]
    
    subgraph Feedback_Loop [Quality Gate]
        Critic -->|Critique| Validator{Validator Agent}
        Validator -- FAIL: Incomplete --> Planner
        Validator -- PASS: Accurate --> Final[Final Consolidated Answer]
    end
    
    Final --> User
```