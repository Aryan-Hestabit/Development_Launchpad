# Retrieval Strategies and Pipeline Overview 📚

This document analyzes how the components of the repository work together to support content retrieval, reranking, and context building. It serves as both a reference for developers and a guide for qualitatively understanding the system.

---

## 1. Core Components 🧩

| Component | Location | Responsibility |
|-----------|----------|----------------|
| **Embedder** | `src/embeddings/embedder.py` | Converts text into dense vectors using SentenceTransformers. Implements `embed_documents` and `embed_query` for use in semantic search. |
| **HybridRetriever** | `src/retriever/hybrid_retriever.py` | Orchestrates retrieval combining semantic (FAISS) and keyword (BM25) methods, applies filters, deduplicates, and triggers reranking. |
| **Reranker** | `src/retriever/reranker.py` | Scores document-query pairs with a CrossEncoder and sorts results by relevance. |
| **Context Builder** | `src/pipelines/context_builder.py` | Formats retrieved documents into a concatenated text block for downstream consumption (e.g. LLM prompts). |
| **Settings** | `src/config/settings.py` | Defines global constants (paths, chunk settings, TOP_K). |

---

## 2. Hybrid Retrieval Strategy 🔍

Hybrid retrieval leverages both semantic and keyword approaches to maximize recall and precision.

1. **Initialization**
   - Load the `Embedder` (BGE model by default).
   - Load a FAISS vectorstore from disk (`VECTORSTORE_PATH`).
   - Configure the semantic retriever using Maximal Marginal Relevance (MMR) with `k=10` and `fetch_k=30` to reduce redundancy.
   - Build a BM25 retriever over all stored documents for keyword-based matching (also limited to `k=10`).
   - Instantiate the `Reranker`.

2. **Retrieval Flow** (`HybridRetriever.retrieve`):
   - **Semantic step**: Query FAISS via MMR to obtain semantically similar documents.
   - **Keyword step**: Query BM25 to capture term-based hits often missed by embeddings.
   - **Merge**: Combine the two result lists.
   - **Filtering**: Optionally apply metadata filters (e.g. year, source).
   - **Deduplication**: Remove duplicates based on `(source, page, chunk_id)` tuple to avoid repeated passages.
   - **Reranking**: Pass merged documents to `Reranker` for final relevance ordering.
   - **Truncation**: Return the top-`K` documents as defined by `TOP_K`.

3. **Utility Functions**
   - `apply_filters`: Generic metadata filter.
   - `deduplicate`: Ensures unique context pieces.

> ⚠️ The retriever is intended to be loaded once (heavy initialization) and reused across queries.

---

## 3. Reranking ⬆️

Reranking happens after initial retrieval to refine result order using interaction-aware scoring.

- **Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2` via `sentence_transformers.CrossEncoder`.
- **Process**:
  1. Create `(query, document_text)` pairs for all candidates.
  2. Predict a relevance score for each pair.
  3. Sort documents in descending score order.
  4. Return the reordered list.

This step adds a deep semantic understanding of query–document interplay beyond independent embeddings.

---

## 4. Context Builder 🏗️

Located in `src/pipelines/context_builder.py`, its purpose is to prepare retrieved documents for use in prompt assembly.

- **build_context(documents)**:
  - Iterates through documents, numbering sources.
  - Inserts metadata (source file, page) and the actual text.
  - Joins blocks with double newlines.

- **main loop**:
  - Accepts user queries interactively.
  - Optionally applies filters.
  - Retrieves documents via `HybridRetriever`.
  - Builds and prints the final context for inspection or further use.

The context can then be passed to an LLM or other reasoning module.

---

## 5. Pipeline Summary 🛠️

1. **Data Ingestion & Chunking** (not covered here but implied by settings): large documents are split into chunks and stored with metadata.
2. **Embedding & Indexing**: `Embedder` generates vectors; FAISS stores them.
3. **Retrieval**: `HybridRetriever` fetches relevant chunks via semantic and keyword searches.
4. **Reranking**: `Reranker` reorders candidates for maximum relevance.
5. **Context Construction**: `build_context` formats results into text blocks ready for consumption.
6. **Downstream Use**: The generated context can be fed to a generative model, evaluation module, or user interface.

> 📌 **Settings** control behavior (e.g., `TOP_K`, chunk sizes) and should be tuned per dataset.

---

## 6. Extension Points & Notes ✨

- Filters rely on consistent metadata; any new field must be added during ingestion.
- Reranker model can be swapped via configuration for custom scoring.
- Logging paths and vectorstore locations are defined in settings for portability.

---
