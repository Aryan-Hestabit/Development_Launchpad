"""
app.py — Streamlit UI for the RAG Capstone
Sidebar modes: Ask | Ask Image | Ask SQL
Run: streamlit run src/deployment/app.py
"""

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

# ── Path setup — point to project root so all src.* imports resolve ───────────
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.config.settings import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_MODEL_SQL,
    IMAGE_FAISS_INDEX, IMAGE_INDEX_FILE, BLIP_MODEL,
    HALLUCINATION_THRESHOLD,
)
from src.memory.memory_store import get_memory, add_message, format_history, clear_memory
from src.evaluation.rag_eval import confidence_score, hallucination_detected, refinement_loop, log_trace

from google import genai
from langchain_core.prompts import PromptTemplate

client = genai.Client(api_key=GEMINI_API_KEY)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="RAG Capstone", page_icon="🧠", layout="wide")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 RAG Capstone")
    mode = st.radio(
        "Select Mode",
        ["💬 Ask", "🖼️ Ask Image", "🗄️ Ask SQL"],
        index=0,
    )
    st.divider()
    st.caption("Memory: last 5 turns per mode (Redis)")
    if st.button("🗑️ Clear Memory"):
        endpoint_map = {"💬 Ask": "ask", "🖼️ Ask Image": "ask-image", "🗄️ Ask SQL": "ask-sql"}
        clear_memory(endpoint_map[mode])
        st.success("Memory cleared.")

# ── Shared eval helper ────────────────────────────────────────────────────────
def run_eval_and_display(endpoint, question, context, raw_answer):
    score        = confidence_score(raw_answer, context)
    hallucinated = hallucination_detected(score)
    final_answer, was_rewritten = refinement_loop(question, context, raw_answer)

    log_trace(
        endpoint, question, context,
        raw_answer, final_answer, was_rewritten,
        score, hallucinated,
    )

    add_message(endpoint, "user", question)
    add_message(endpoint, "assistant", final_answer)

    st.markdown("### 💡 Answer")
    st.write(final_answer)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Confidence Score", f"{score:.2f}")
    with col2:
        if hallucinated:
            st.error("⚠️ Possible hallucination detected")
        else:
            st.success("✅ Answer grounded in context")

    if was_rewritten:
        st.info("🔄 Answer was refined by self-critique loop.")

    with st.expander("📚 Retrieved Context"):
        st.text(context[:2000])

    with st.expander("🕓 Conversation Memory"):
        for m in get_memory(endpoint):
            role = "🧑 User" if m["role"] == "user" else "🤖 Assistant"
            st.markdown(f"**{role}:** {m['content']}")


# ═══════════════════════════════════════════════════════════════
# MODE 1 — ASK (Text RAG)
# ═══════════════════════════════════════════════════════════════
if mode == "💬 Ask":
    st.header("💬 Ask — Text RAG")

    ASK_PROMPT = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=(
            "{history}\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer based only on the context above:"
        )
    )

    # Load HybridRetriever once per session
    if "ask_retriever" not in st.session_state:
        with st.spinner("Loading retriever (first time only)..."):
            from src.retriever.hybrid_retriever import HybridRetriever
            st.session_state["ask_retriever"] = HybridRetriever()

    retriever = st.session_state["ask_retriever"]

    question = st.text_input("Your question:", placeholder="What is retrieval-augmented generation?")

    if st.button("Ask", key="ask_btn") and question:
        with st.spinner("Retrieving and generating..."):
            from src.pipelines.context_builder import build_context

            docs    = retriever.retrieve(query=question, top_k=5)
            context = build_context(docs)
            history = format_history("ask")
            prompt  = ASK_PROMPT.format(history=history, context=context, question=question)
            answer  = client.models.generate_content(model=GEMINI_MODEL, contents=prompt).text.strip()

        run_eval_and_display("ask", question, context, answer)


# ═══════════════════════════════════════════════════════════════
# MODE 2 — ASK IMAGE (Multimodal RAG)
# ═══════════════════════════════════════════════════════════════
elif mode == "🖼️ Ask Image":
    st.header("🖼️ Ask Image — Multimodal RAG")

    # Load all image models once per session
    if "img_faiss" not in st.session_state:
        with st.spinner("Loading image models (first time only)..."):
            from src.retriever.image_search import (
                caption, ocr, load_index,
                retrieve, preprocess_query_image,
                build_context as img_build_context,
                get_blip, RAG_PROMPT,
            )
            from src.embeddings.clip_embedder import CLIPEmbedder

            faiss_index, metadata = load_index()
            get_blip()   # warm up BLIP

            st.session_state["img_faiss"]    = faiss_index
            st.session_state["img_metadata"] = metadata
            st.session_state["img_embedder"] = CLIPEmbedder()
            # store the imported functions so we don't re-import on every rerun
            st.session_state["img_fns"] = {
                "caption":    caption,
                "ocr":        ocr,
                "retrieve":   retrieve,
                "preprocess": preprocess_query_image,
                "context":    img_build_context,
                "rag_prompt": RAG_PROMPT,
            }

    faiss_index = st.session_state["img_faiss"]
    metadata    = st.session_state["img_metadata"]
    embedder    = st.session_state["img_embedder"]
    fns         = st.session_state["img_fns"]

    uploaded    = st.file_uploader("Upload a query image", type=["png", "jpg", "jpeg", "webp"])
    search_mode = st.selectbox("Search mode", ["Image → Image", "Image → Text Answer"])

    # Only show question input in Text Answer mode
    question = None
    if search_mode == "Image → Text Answer":
        question = st.text_input("Your question:", placeholder="What components are shown?")

    if st.button("Search", key="img_btn") and uploaded:
        with st.spinner("Processing image..."):
            from PIL import Image as PILImage
            from src.config.settings import TOP_K

            img            = PILImage.open(uploaded).convert("RGB")
            query_caption  = fns["caption"](img)
            query_ocr      = fns["ocr"](img)
            complete_query = f"query_caption:{query_caption}\nQuery_OCR:{query_ocr}".strip()

            query_vec = fns["preprocess"](complete_query, img, embedder)
            results   = fns["retrieve"](query_vec, faiss_index, metadata, TOP_K)
            context   = fns["context"](results)

        st.image(img, caption=f"Query Image — {query_caption}", width=300)

        if search_mode == "Image → Image":
            st.markdown(f"### 🔍 Top {len(results)} Similar Images")
            cols = st.columns(min(len(results), 3))
            for i, r in enumerate(results):
                with cols[i % 3]:
                    src = r.get("source", "")
                    try:
                        st.image(src, use_column_width=True)
                    except Exception:
                        st.text(src)
                    st.caption(
                        f"Score: {r['score']:.4f}\n"
                        f"{r.get('caption', '')}\n"
                        f"OCR: {r.get('ocr_text', '')[:80] or 'None'}"
                    )

        else:
            if not question:
                st.warning("Please enter a question for Image → Text Answer mode.")
                st.stop()

            history = format_history("ask-image")
            prompt  = fns["rag_prompt"].format(
                query_caption=query_caption,
                context=context,
                question=f"{history}\n\n{question}" if history else question,
            )
            answer = client.models.generate_content(model=GEMINI_MODEL, contents=prompt).text.strip()
            run_eval_and_display("ask-image", question, context, answer)


# ═══════════════════════════════════════════════════════════════
# MODE 3 — ASK SQL
# ═══════════════════════════════════════════════════════════════
elif mode == "🗄️ Ask SQL":
    st.header("🗄️ Ask SQL — Natural Language to SQL")

    from src.utils.schema_loader import load_schema, get_schema_metadata
    from src.generator.sql_generator import generate_sql
    from src.pipelines.sql_pipeline import execute_sql, summarize

    db_source = st.radio("Database source", [".db file (SQLite)", ".csv file(s)"])
    db_path   = None

    if db_source == ".db file (SQLite)":
        uploaded_db = st.file_uploader("Upload your .db file", type=["db"])
        if uploaded_db:
            tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
            tmp.write(uploaded_db.read())
            tmp.flush()
            db_path = Path(tmp.name)

    else:
        uploaded_csvs = st.file_uploader("Upload CSV file(s)", type=["csv"], accept_multiple_files=True)
        if uploaded_csvs:
            tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
            conn   = sqlite3.connect(tmp_db.name)
            for csv_file in uploaded_csvs:
                df         = pd.read_csv(csv_file)
                table_name = Path(csv_file.name).stem
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                st.success(f"Loaded CSV → table `{table_name}`")
            conn.close()
            db_path = Path(tmp_db.name)

    question = st.text_input("Your question:", placeholder="Show total sales by artist for 2023.")

    if st.button("Run Query", key="sql_btn") and db_path and question:
        with st.spinner("Generating and executing SQL..."):
            schema      = load_schema(db_path)
            schema_meta = get_schema_metadata(db_path)
            history     = format_history("ask-sql")

            # Inject conversation history into the question
            enriched         = f"{history}\n\nQuestion: {question}" if history else question
            sql, is_valid, error = generate_sql(enriched, schema, schema_meta)

        st.code(sql, language="sql")

        if not is_valid:
            st.error(f"❌ Validation failed: {error}")
            st.stop()

        st.success("✅ SQL validated.")

        # Execute using sql_pipeline.execute_sql
        rows, exec_error = execute_sql(db_path, sql)
        if exec_error:
            st.error(f"❌ Execution failed: {exec_error}")
            st.stop()

        if rows:
            st.dataframe(pd.DataFrame(rows))
        else:
            st.info("Query returned no results.")

        # Summarize using sql_pipeline.summarize
        answer  = summarize(question, sql, rows)
        context = f"SQL: {sql}\nResults: {json.dumps(rows[:50], indent=2)[:1000]}"

        run_eval_and_display("ask-sql", question, context, answer)