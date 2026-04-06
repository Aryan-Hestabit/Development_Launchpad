# Agent Fundamentals - Day 1

## Overview
This document outlines the fundamentals of the multi-agent system implemented in Day 1. The system uses three specialized agents in a round-robin workflow, each focused on one stage of the pipeline:
- Research
- Summarization
- Final answer synthesis

## System Architecture

### Main Entry Point (`main.py`)
- **Framework**: AutoGen AgentChat (console-based)
- **Agents**: `research_agent`, `summarizer_agent`, `answer_agent`
- **Chat Coordinator**: `RoundRobinGroupChat`
- **Termination**: `TextMentionTermination("TERMINATE")` or `max_turns=3`
- **User loop**: interactive input (exit/quit to stop)

### Agent Implementation Details
All three agents are built with `AssistantAgent`.

#### 1. Research Agent (`agents/research_agent.py`)
- **Role**: Expert Senior Research Analyst
- **Prompt**: deep technical research (400-600 words), with historical context
- **Constraint**: no summarization
- **Memory**: `BufferedChatCompletionContext(buffer_size=10)`
- **Streaming**: true

#### 2. Summarizer Agent (`agents/summarizer_agent.py`)
- **Role**: Information Architect & Summarizer
- **Prompt**: condense research to bullet points, reduce word count by ~60%
- **Constraint**: preserve key facts, no new facts
- **Streaming**: true

#### 3. Answer Agent (`agents/answer_agent.py`)
- **Role**: Final Communications Lead
- **Prompt**: create final answer from summary, do not add new info
- **Constraint**: professional tone, end response with `TERMINATE`
- **Streaming**: true

## Agent Interaction Flow
1. User message enters `RoundRobinGroupChat`
2. Research agent responds first with full-domain details
3. Summarizer agent distills the research into concise bullets
4. Answer agent crafts the final user-facing answer and appends `TERMINATE`
5. Chat ends once the termination condition is triggered or max turns are reached
