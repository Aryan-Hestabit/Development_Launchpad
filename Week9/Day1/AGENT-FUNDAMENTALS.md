# Agent Fundamentals - Day 1

## Overview
This document outlines the fundamentals of the multi-agent system implemented in Day 1. The system consists of three specialized agents working together in a round-robin group chat to process user queries through research, summarization, and final answer generation.

## System Architecture

### Main Entry Point (`main.py`)
- **Framework**: Uses AutoGen AgentChat library
- **Model**: Mistral via Ollama (localhost:11434)
- **Chat Type**: RoundRobinGroupChat with 3 agents
- **Termination**: TextMentionTermination("TERMINATE") with max_turns=3
- **Interface**: Console-based interactive loop

### Agents Overview

#### 1. Research Agent (`research_agent.py`)
- **Role**: Expert Senior Research Analyst
- **Task**: Provide exhaustive, factual, and detailed information (400-600 words)
- **Focus**: Technical specifications, historical context, current trends
- **Constraint**: No summarization - provide raw depth
- **Memory**: BufferedChatCompletionContext with buffer_size=10
- **Model**: Mistral (streaming enabled)

#### 2. Summarizer Agent (`summarizer_agent.py`)
- **Role**: Information Architect & Summarizer
- **Task**: Distill long-form research into structured summaries
- **Format**: Bullet points for readability
- **Constraint**: Reduce word count by 60%, maintain all key facts, no external knowledge
- **Model**: Mistral (streaming enabled)

#### 3. Answer Agent (`answer_agent.py`)
- **Role**: Final Communications Lead
- **Task**: Convert summarized reports into direct user answers
- **Constraint**: Professional tone, no new information, end with "TERMINATE"
- **Model**: Mistral (streaming enabled)

## Agent Interaction Flow
1. **User Query** → Research Agent (gathers comprehensive information)
2. **Research Output** → Summarizer Agent (condenses into bullet points)
3. **Summary** → Answer Agent (formats final response + "TERMINATE")

## Key Features
- **Streaming**: All agents use streaming model clients for real-time output
- **Memory Management**: Research agent maintains context buffer (10 messages)
- **Termination Control**: Automatic termination on "TERMINATE" keyword or max 3 turns
- **Local AI**: Uses Ollama for local Mistral model execution
- **Function Calling**: Disabled (json_output=False)

## Configuration Notes
- All agents use the same Ollama endpoint: `http://localhost:11434`
- No JSON output mode enabled
- Round-robin ensures each agent gets a turn in sequence
- System designed for technical research and Q&A workflows