# Enterprise RAG Architecture – Day 1 Implementation

## 1. Overview

This system implements a Retrieval-Augmented Generation (RAG) architecture designed for enterprise-grade document intelligence.

The objective is to:

- Ingest structured and unstructured documents
- Convert text into semantic embeddings
- Store embeddings in a vector database
- Retrieve the most relevant chunks for a given query
- Provide traceable, non-hallucinated context to an LLM

---

## 2. System Components

### 2.1 Document Ingestion

Supported Formats:
- PDF
- TXT
- CSV
- DOCX

Documents are loaded using `langchain_community` loaders.

Metadata captured:
- source (filename)
- page (if available)
- chunk_id (added during chunking)

---

### 2.2 Text Cleaning

Cleaning ensures:

- Normalized newline formatting
- Collapsed excessive whitespace
- Preserved paragraph boundaries

This improves chunk coherence and embedding quality.

### 2.3 Token-Based Chunking

We use:

TokenTextSplitter

Configuration:
- chunk_size: 600 tokens
- chunk_overlap: 100 tokens

Rationale:
- Aligns with LLM token processing
- Avoids character-based fragmentation
- Preserves semantic structure

### 2.4 Embedding Model

Model:
BAAI/bge-small-en

Properties:
- 384-dimensional vectors
- Optimized for retrieval
- CPU-friendly
- Strong semantic ranking performance

Embeddings are L2-normalized before indexing.

## 3. Similarity Computation

We use cosine similarity:

cos(θ) = (A · B) / (||A|| ||B||)

Since embeddings are normalized:

||A|| = 1  
||B|| = 1  

Cosine similarity becomes:

A · B

This allows use of FAISS IndexFlatIP for efficient retrieval.

## 4. Vector Store

Vector database:
FAISS (IndexFlatIP)

Why Flat Index?

- Exact nearest neighbor search
- No approximation errors
- Suitable for moderate dataset size
- Simpler debugging and evaluation

Stored Artifacts:

- index.faiss → embedding vectors
- metadata.pkl → metadata mapping
- chunks.json → raw chunk text + metadata

## 5. Retrieval Flow

Query → Embed → Normalize → FAISS Search → Top 5 Results

Steps:

1. Query converted to embedding
2. Embedding normalized
3. FAISS retrieves top-k most similar vectors
4. Scores represent cosine similarity
5. Corresponding chunks are returned

## 6. Score Interpretation

The retrieval score is cosine similarity.

Score Range:

- 0.80+ → Very strong semantic match
- 0.65–0.80 → Relevant match
- < 0.50 → Weak relation

The score is NOT a probability.  
It is a geometric similarity measure in embedding space.

## 7. Design Principles

- Modular architecture (embedder, ingestion, retriever separated)
- Model-agnostic embedding layer
- Exact similarity search for reliability
- Token-aware chunking
- Metadata traceability for enterprise auditing
- Future-ready for hybrid retrieval and reranking

## 8. Future Extensions (Day 2+)

- Hybrid search (BM25 + embeddings)
- Cross-encoder reranking
- Metadata filtering
- MMR-based diversification
- Hallucination detection
- Faithfulness scoring
- Conversational memory

