# 🧠 MEMORY-SYSTEM.md

## 1. Overview
The Day 4 Memory System implements a sophisticated, persistent "brain" for AutoGen agents. It moves beyond simple chat history by creating a dedicated Long-Term Memory (LTM) system that survives script restarts and builds a unique profile for the user over time.

## 2. Tech Stack
- **Orchestration:** autogen-core & autogen-agentchat.
- **Vector Engine:** FAISS (Facebook AI Similarity Search) using IndexFlatIP for Cosine Similarity.
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2) — 384-dimensional vectors.
- **Relational Logging:** SQLite3 for durable fact auditing.
- **Short-Term Logic:** ListMemory with a Sliding Window (20 messages).
- **Context Management:** BufferedChatCompletionContext for raw LLM windowing.

## 3. Architecture & Memory Layers

### 🟢 Short-Term: ListMemory
We utilize autogen_core.memory.ListMemory to store the literal "Transcript" of the current session.
- **Implementation:** A custom sliding window limits this to the 20 most recent messages.
- **Purpose:** To provide immediate conversational flow, ensuring the agent understands pronouns (e.g., "it", "that") and the immediate sequence of events.

### 🔵 Long-Term: FAISSVectorMemory (The Base Class approach)
We implemented our FAISS logic by inheriting from the Memory base class in autogen_core.
- **Why the Base Class?** By using the official Memory protocol, we tap into the update_context hook. This allows the AssistantAgent to automatically trigger a vector search and "inject" relevant facts into the system prompt without manual intervention in main.py.
- **Persistence:** Unlike standard RAM-only FAISS, our system writes to faiss.index on disk, allowing for true multi-session intelligence.

### 🟡 Auditing & Logging: SQLite
- **Component:** long_term.db
- **Role:** This file is used strictly for auditing and manual logging. While FAISS handles the "thinking" (retrieval), SQLite ensures we have a human-readable record of every fact extracted. It acts as the "Source of Truth" to rebuild the vector index if it is ever corrupted.

## 4. Key Technical Distinctions
A common point of confusion in Day 4 is the difference between the Context and the Memory. Here is how we have separated them:

| Feature |BufferedChatCompletionContext |ListMemory |
| --- | --- | --- |
|Primary Role|LLM Windowing|Short-Term Storage |
|Logic|Strictly limits the raw message count (e.g., 10) sent to the API to save tokens.|A persistent list of messages within the Python session.|
|Visibility|It is the "eye" of the LLM; it sees only what is inside the buffer.| It is the "working memory"; it holds the history that update_context can pull from.|
|Implementation | Part of the model_context parameter. | Part of the memory parameter list. | 

## 5. The Retrieval & Extraction Flow

1. **Semantic Search:** User query $\rightarrow$ FAISS $\rightarrow$ Top 5 relevant facts $\rightarrow$ Injected into System Prompt.
2. **Synchronous Extraction:** After the Agent speaks, fact_extractor.py parses the exchange.
3. **Self-Deduplication:** The FAISSVectorMemory.add() method runs a similarity check (Threshold: 0.9). If the fact is already "known," it is discarded to prevent redundancy.
4. **Durable Save:** New facts are committed to faiss.index (for future retrieval) and long_term.db (for auditing).