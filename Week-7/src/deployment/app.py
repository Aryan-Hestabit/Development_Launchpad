"""
Run: streamlit run src/deployment/app.py
"""

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.config.settings import (
    GEMINI_API_KEY, GEMINI_MODEL, TOP_K
)
from src.retriever.image_search import (
    caption, ocr, load_index,
    retrieve, preprocess_query_image,
    build_context as img_build_context,
    get_blip, RAG_PROMPT,
)
from src.embeddings.clip_embedder import CLIPEmbedder
from PIL import Image as PILImage
from src.memory.memory_store import get_memory, add_message, format_history, clear_memory
from src.evaluation.rag_eval import confidence_score, hallucination_detected, refinement_loop, log_trace
from src.retriever.hybrid_retriever import HybridRetriever
from src.pipelines.context_builder import build_context
from src.utils.schema_loader import load_schema, get_schema_metadata
from src.generator.sql_generator import generate_sql
from src.pipelines.sql_pipeline import execute_sql, summarize
from google import genai
from langchain_core.prompts import PromptTemplate

client = genai.Client(api_key=GEMINI_API_KEY)

import uuid

# Session State for Memory
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

SESSION_ID = st.session_state.session_id

# Cached model loaders
@st.cache_resource
def load_retriever():
    return HybridRetriever()

@st.cache_resource
def load_image_models():
    faiss_index, metadata = load_index()
    get_blip()
    return faiss_index, metadata, CLIPEmbedder()

# Page config
st.set_page_config(page_title="RAG Capstone", page_icon="🧠", layout="wide")

# Sidebar 
with st.sidebar:
    st.title("RAG Capstone")
    mode = st.radio(
        "Select Mode",
        ["Ask", "Ask Image", "Ask SQL"],
        index=0,
    )
    st.divider()
    st.caption("Memory: last 5 turns per mode (Redis)")
    if st.button("🗑️ Clear Memory"):
        endpoint_map = {"Ask": "ask", "Ask Image": "ask-image", "Ask SQL": "ask-sql"}
        clear_memory(SESSION_ID,endpoint_map[mode])
        st.success("Memory cleared.")

# Shared eval helper
def run_eval_and_display(endpoint, question, context, raw_answer):
    embedder     = load_retriever().embedder
    score        = confidence_score(raw_answer, context, embedder) if embedder else 0.0
    hallucinated = hallucination_detected(score)
    final_answer, was_rewritten = refinement_loop(question, context, raw_answer)

    log_trace(
        endpoint, question, context,
        raw_answer, final_answer, was_rewritten,
        score, hallucinated,
    )

    add_message(SESSION_ID,endpoint, "user", question)
    add_message(SESSION_ID, endpoint, "assistant", final_answer)

    st.markdown("### Answer")
    st.write(final_answer)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Confidence Score", f"{score:.2f}")
    with col2:
        if hallucinated:
            st.error("Possible hallucination detected")
        else:
            st.success("Answer grounded in context")

    if was_rewritten:
        st.info("Answer was refined by self-critique loop.")

    with st.expander("Retrieved Context"):
        st.text(context[:2000])

    with st.expander("Conversation Memory"):
        for m in get_memory(SESSION_ID,endpoint):
            role = "User" if m["role"] == "user" else "Assistant"
            st.markdown(f"**{role}:** {m['content']}")


# Shared image results display 
def display_image_results(results: list):
    st.markdown(f"### Top {len(results)} Similar Images")
    cols = st.columns(min(len(results), 3))
    for i, r in enumerate(results):
        with cols[i % 3]:
            src     = r.get("source", "")
            score   = r.get("score", 0.0)
            cap     = r.get("caption", "") or "—"
            ocr_txt = r.get("ocr_text", "") or "None"

            try:
                st.image(src, width=300)
            except Exception:
                st.warning(f"Could not load image: {src}")

            st.metric("Score", f"{score:.4f}")
            st.caption(f"Caption: {cap}")
            st.caption(f"OCR: {ocr_txt[:120]}")


# MODE 1 — ASK (Text RAG)
if mode == "Ask":
    st.header("Ask — Text RAG")

    ASK_PROMPT = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=(
            "{history}\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer based only on the context above:"
        )
    )

    with st.spinner("Loading retriever (first time only)..."):
        retriever = load_retriever()

    question = st.text_input("Your question:", placeholder="What is retrieval-augmented generation?")

    if st.button("Ask", key="ask_btn") and question:
        with st.spinner("Retrieving and generating..."):
            docs    = retriever.retrieve(query=question, top_k=5)
            context = build_context(docs)
            history = format_history(SESSION_ID,"ask")
            prompt  = ASK_PROMPT.format(history=history, context=context, question=question)
            answer  = client.models.generate_content(model=GEMINI_MODEL, contents=prompt).text.strip()

        run_eval_and_display("ask", question, context, answer)


# MODE 2 — ASK IMAGE (Multimodal RAG)
elif mode == "Ask Image":
    st.header("Ask Image — Multimodal RAG")

    with st.spinner("Loading image models (first time only)..."):
        faiss_index, metadata, embedder = load_image_models()

    search_mode = st.selectbox(
        "Search mode",
        ["Text → Image", "Image → Image", "Image → Text Answer"]
    )

    # Text → Image 
    if search_mode == "Text → Image":
        text_query = st.text_input(
            "Describe what you are looking for:"
        )
        if st.button("Search", key="txt_img_btn") and text_query:
            with st.spinner("Searching..."):
                # CLIP text embedding only — no image, no BLIP, no OCR
                query_vec = embedder.embed_text(text_query)
                results   = retrieve(query_vec, faiss_index, metadata, TOP_K)
            display_image_results(results)

    # Image → Image 
    elif search_mode == "Image → Image":
        uploaded = st.file_uploader("Upload a query image", type=["png", "jpg", "jpeg", "webp"])
        if st.button("Search", key="img_img_btn") and uploaded:
            with st.spinner("Processing image..."):
                img            = PILImage.open(uploaded).convert("RGB")
                query_caption  = caption(img)
                query_ocr      = ocr(img)
                complete_query = f"query_caption:{query_caption}\nQuery_OCR:{query_ocr}".strip()
                query_vec      = preprocess_query_image(complete_query, img, embedder)
                results        = retrieve(query_vec, faiss_index, metadata, TOP_K)

            st.image(img, caption=f"Query Image — {query_caption}", width=300)
            display_image_results(results)

    # Image → Text Answer
    else:
        uploaded = st.file_uploader("Upload a query image", type=["png", "jpg", "jpeg", "webp"])
        question = st.text_input("Your question:", placeholder="What components are shown?")

        if st.button("Search", key="img_txt_btn") and uploaded:
            if not question:
                st.warning("Please enter a question for Image → Text Answer mode.")
                st.stop()

            with st.spinner("Processing image..."):
                img            = PILImage.open(uploaded).convert("RGB")
                query_caption  = caption(img)
                query_ocr      = ocr(img)
                complete_query = f"query_caption:{query_caption}\nQuery_OCR:{query_ocr}".strip()
                query_vec      = preprocess_query_image(complete_query, img, embedder)
                results        = retrieve(query_vec, faiss_index, metadata, TOP_K)
                context        = img_build_context(results)

            st.image(img, caption=f"Query Image — {query_caption}", width=300)

            history = format_history(SESSION_ID,"ask-image")
            prompt  = RAG_PROMPT.format(
                query_caption=query_caption,
                context=context,
                question=f"{history}\n\n{question}" if history else question,
            )
            answer = client.models.generate_content(model=GEMINI_MODEL, contents=prompt).text.strip()
            run_eval_and_display("ask-image", question, context, answer)


# MODE 3 — ASK SQL
elif mode == "Ask SQL":
    st.header("Ask SQL — Natural Language to SQL")

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
            history     = format_history(SESSION_ID, "ask-sql")
            enriched    = f"{history}\n\nQuestion: {question}" if history else question
            sql, is_valid, error = generate_sql(enriched, schema, schema_meta)

        st.code(sql, language="sql")

        if not is_valid:
            st.error(f"❌ Validation failed: {error}")
            st.stop()

        st.success("✅ SQL validated.")

        rows, exec_error = execute_sql(db_path, sql)
        if exec_error:
            st.error(f"❌ Execution failed: {exec_error}")
            st.stop()

        if rows:
            st.dataframe(pd.DataFrame(rows))
        else:
            st.info("Query returned no results.")

        answer  = summarize(question, sql, rows)
        context = f"SQL: {sql}\nResults: {json.dumps(rows[:50], indent=2)[:1000]}"

        run_eval_and_display("ask-sql", question, context, answer)