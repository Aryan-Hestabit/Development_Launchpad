# DEPLOYMENT NOTES — RAG Capstone (Day 5)

## Stack Overview

| Component        | Technology                          |
|------------------|-------------------------------------|
| UI               | Streamlit                           |
| LLM              | Gemini 2.5 Flash (google-genai)     |
| Memory           | Redis (per-endpoint, last 5 turns)  |
| Text RAG         | HybridRetriever (FAISS + BM25 + Reranker) |
| Image RAG        | CLIP + BLIP + FAISS (fused embeddings) |
| SQL QA           | SQLite + Gemini (generate → validate → execute → summarize) |
| Evaluation       | Keyword overlap confidence + Gemini self-critique |
| Logs             | CHAT-LOGS.json (auto-appended)      |

---

## Project Structure

``` bash
src/
├── config/
│   └── settings.py                  ← all paths, model names, API keys
├── memory/
│   └── memory_store.py              ← Redis memory (get/add/clear/format)
├── evaluation/
│   └── rag_eval.py                  ← confidence, hallucination, refinement, logging
├── deployment/
│   └── app.py                       ← Streamlit UI (all 3 endpoints)
├── retriever/
│   ├── hybrid_retriever.py          ← FAISS + BM25 + Reranker (/ask)
│   └── image_search.py              ← CLIP FAISS search (/ask-image)
├── embeddings/
│   ├── embedder.py                  ← text embedder for hybrid retriever
│   └── clip_embedder.py             ← CLIP image+text fused embedder
├── pipelines/
│   ├── image_ingest.py              ← BLIP + OCR + CLIP → FAISS index
│   └── sql_pipeline.py              ← execute_sql + summarize
├── generator/
│   └── sql_generator.py             ← Gemini SQL generation + 3-layer validation
├── utils/
│   └── schema_loader.py             ← SQLite schema auto-discovery
├── context_builder.py               ← formats retrieved docs → context string
└── data/
    ├── images/                      ← images/PDFs for ingestion
    ├── tables/                      ← .db or .csv files for SQL QA
    └── vectorstore/                 ← FAISS index files

CHAT-LOGS.json                       ← auto-generated trace log
```

---

## Installation

``` bash
pip install streamlit redis pandas google-genai langchain-core \
            langchain-community sentence-transformers faiss-cpu \
            transformers Pillow pytesseract sqlparse pdf2image \
            python-dotenv --break-system-packages
```

### System Dependencies
```bash
# Tesseract OCR
sudo apt-get install tesseract-ocr

# Poppler (PDF → image conversion)
sudo apt-get install pdf2image

# Redis
sudo apt-get install redis-server
sudo service redis-server start

# Verify Redis
redis-cli ping   # should return PONG
```

---

## Environment Setup

Create a `.env` file at the project root:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get your Gemini API key at: https://aistudio.google.com

## Run

```bash
# From project root
streamlit run src/deployment/app.py
```


## Endpoints

### 💬 /ask — Text RAG

**Flow:**
```
User question
    → HybridRetriever.retrieve(query, top_k=5)
        ├── Semantic search (FAISS MMR)
        ├── Keyword search (BM25)
        ├── Merge + Deduplicate
        └── Rerank
    → build_context(docs)          ← formatted source blocks
    → format_history("ask")        ← last 5 turns from Redis
    → Gemini generates answer
    → run_eval_and_display()
```

**Session state:** `HybridRetriever` cached in `st.session_state["ask_retriever"]` — loads once per session.

---

### 🖼️ /ask-image — Multimodal RAG

**Two modes:**

**Image → Image**
```
Upload query image
    → BLIP caption(img)            ← query_caption
    → Tesseract ocr(img)           ← query_ocr
    → combined = "query_caption:... Query_OCR:..."
    → CLIPEmbedder.embed_fused(img, combined)   ← fused 512-d vec
    → FAISS IndexFlatIP.search(query_vec, top_k)
    → Display retrieved images in 3-column grid (no LLM)
```

**Image → Text Answer**
```
Upload query image + question
    → BLIP caption + Tesseract OCR → combined
    → embed_fused → FAISS retrieve → build_context
    → format_history("ask-image")
    → RAG_PROMPT(query_caption, context, history+question)
    → Gemini generates answer
    → run_eval_and_display()
```

**Session state:** FAISS index, metadata, CLIPEmbedder, BLIP all cached in `st.session_state` — load once per session.

**Ingest pipeline** (run before using /ask-image):
```bash
python src/pipelines/image_ingest.py --images_dir src/data/images
```

---

### 🗄️ /ask-sql — Natural Language to SQL

**Database input options:**
- Upload a `.db` SQLite file directly
- Upload one or more `.csv` files → auto-converted to temporary SQLite DB

**Flow:**
```
Upload .db / .csv  →  db_path (temp SQLite)
    → load_schema(db_path)         ← table names, columns, sample rows
    → get_schema_metadata(db_path) ← {table: [columns]} for validation
    → format_history("ask-sql")    ← last 5 turns from Redis
    → generate_sql(enriched_question, schema, schema_meta)
        ├── Gemini generates SQL
        ├── Validation Layer 1: Guard rail (blocks DROP/DELETE/UPDATE/ALTER etc.)
        ├── Validation Layer 2: Syntax check (sqlparse)
        ├── Validation Layer 3: Schema check (tables + columns exist)
        └── Auto-correction loop (up to 3 retries on failure)
    → execute_sql(db_path, sql)    ← safe SQLite execution
    → st.dataframe(rows)           ← tabular display
    → summarize(question, sql, rows) ← Gemini natural language summary
    → run_eval_and_display()
```

---

## Evaluation Pipeline

Runs after every answer across all three endpoints:

```
raw_answer + context
    ↓
confidence_score()
    → keyword overlap (answer words ∩ context words) / answer words
    → stopwords removed
    → returns float 0.0 – 1.0

hallucination_detected()
    → True if confidence < HALLUCINATION_THRESHOLD (default: 0.4)

refinement_loop()
    → Gemini self-critiques: KEEP or REWRITE
    → returns (final_answer, was_rewritten)

log_trace()
    → appends full trace entry to CHAT-LOGS.json
```

**UI output:**
- Confidence score metric
- ✅ Grounded / ⚠️ Hallucination badge
- 🔄 Refined badge (if rewritten)
- Retrieved context expander
- Conversation memory expander

---

## Memory (Redis)

| Key | Endpoint | Contents |
|-----|----------|----------|
| `memory:ask` | /ask | last 10 messages (5 turns) |
| `memory:ask-image` | /ask-image | last 10 messages (5 turns) |
| `memory:ask-sql` | /ask-sql | last 10 messages (5 turns) |

Message format:
```json
{"role": "user", "content": "..."}
{"role": "assistant", "content": "..."}
```

Memory is injected into every LLM prompt via `format_history(endpoint)`.
Clear memory per-mode using the **🗑️ Clear Memory** button in the sidebar.

---

## CHAT-LOGS.json Schema

Auto-appended after every query across all endpoints:

```json
[
  {
    "timestamp":      "2025-01-01T12:00:00",
    "endpoint":       "ask",
    "question":       "What is RAG?",
    "context":        "...(first 500 chars of retrieved context)...",
    "answer":         "RAG stands for Retrieval-Augmented Generation...",
    "refined_answer": "RAG (Retrieval-Augmented Generation) is a technique...",
    "was_rewritten":  true,
    "confidence":     0.73,
    "hallucination":  false
  }
]
```

---

## Settings Reference

```python
# Gemini
GEMINI_API_KEY   = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL     = "gemini-2.5-flash"
GEMINI_MODEL_SQL = "gemini-2.5-flash"

# Redis
REDIS_HOST          = "localhost"
REDIS_PORT          = 6379
REDIS_DB            = 0
MEMORY_MAX_MESSAGES = 10   # 5 user + 5 assistant

# Paths
VECTORSTORE_PATH      = src/vectorstore/
IMAGE_FAISS_INDEX     = src/vectorstore/image.index
IMAGE_INDEX_FILE      = src/vectorstore/image_index.json
IMAGES_DIR            = src/data/images/
DB_DIR                = src/data/tables/
CHAT_LOGS_PATH        = CHAT-LOGS.json

# Evaluation
HALLUCINATION_THRESHOLD = 0.4

# CLIP fusion weights
IMAGE_WEIGHT = 0.5
TEXT_WEIGHT  = 0.5

# Models
CLIP_MODEL     = "openai/clip-vit-base-patch32"
BLIP_MODEL     = "Salesforce/blip-image-captioning-base"
TOP_K          = 5
```