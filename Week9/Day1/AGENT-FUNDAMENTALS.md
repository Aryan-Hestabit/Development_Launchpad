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

### Shared Settings (`settings.py`)
- `GEMINI_API_KEY` from environment or default placeholder
- `MODEL_ID` = `gemini-3.1-flash-lite-preview`
- `MODEL_INFO` includes vision, function_calling=false, json_output=true, structured_output=true

### Agent Implementation Details
All three agents are built with `AssistantAgent` and default to Gemini API client (`OpenAIChatCompletionClient`) from `autogen_ext.models.openai`.

#### 1. Research Agent (`agents/research_agent.py`)
- **Role**: Expert Senior Research Analyst
- **Prompt**: deep technical research (400-600 words), with historical context
- **Constraint**: no summarization
- **Model client**: `gemini_client` (OpenAIChatCompletionClient, `model=settings.MODEL_ID`)
- **Memory**: `BufferedChatCompletionContext(buffer_size=10)`
- **Streaming**: true
- **Unused client**: `mistral_client` is defined but not used

#### 2. Summarizer Agent (`agents/summarizer_agent.py`)
- **Role**: Information Architect & Summarizer
- **Prompt**: condense research to bullet points, reduce word count by ~60%
- **Constraint**: preserve key facts, no new facts
- **Model client**: `gemini_client` (OpenAIChatCompletionClient)
- **Streaming**: true
- **Unused client**: `mistral_client` is defined but not used

#### 3. Answer Agent (`agents/answer_agent.py`)
- **Role**: Final Communications Lead
- **Prompt**: create final answer from summary, do not add new info
- **Constraint**: professional tone, end response with `TERMINATE`
- **Model client**: `gemini_client` (OpenAIChatCompletionClient)
- **Streaming**: true
- **Unused client**: `mistral` is defined but not used

## Agent Interaction Flow
1. User message enters `RoundRobinGroupChat`
2. Research agent responds first with full-domain details
3. Summarizer agent distills the research into concise bullets
4. Answer agent crafts the final user-facing answer and appends `TERMINATE`
5. Chat ends once the termination condition is triggered or max turns are reached

## Notes
- There is a slight mismatch in comments vs implementation: `main.py` says Mistral via Ollama, but each agent uses Gemini via OpenAI API in code.
- `mistral_client` instances are created in each agent file but not tied into any `AssistantAgent` constructor.
- `TextMentionTermination("TERMINATE")` is used to explicitly close the group chat once the final answer includes the keyword.
- This module is good for proving a multi-agent chain-of-thought pipeline with separate responsibilities.