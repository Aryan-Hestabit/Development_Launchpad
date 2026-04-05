import argparse
import json
import sys
from pathlib import Path
import time
import faiss
import numpy as np
import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor
import pytesseract
from google import genai
from langchain_core.prompts import PromptTemplate

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from embeddings.clip_embedder import CLIPEmbedder
from config.settings import (
    IMAGE_INDEX_FILE, IMAGE_FAISS_INDEX,
    TOP_K, BLIP_MODEL, GEMINI_API_KEY, GEMINI_MODEL,
)

if not GEMINI_API_KEY:
    sys.exit("GOOGLE_API_KEY not set in .env")
client = genai.Client(api_key=GEMINI_API_KEY)

# ── Prompt ─────────────────────────────────────────────────────────────────────
RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question", "query_caption"],
    template=(
        "You are an expert image analyst. Using the retrieved context and the Query Image context "
        "below from visually similar images, answer the user's question as accurately as possible.\n"
        "Query Image Caption: {query_caption},\n\n"
        "Retrieved Context:\n{context}\n\n"
        "Question: {question}\n\nAnswer:"
    )
)

# ── Lazy BLIP singleton ────────────────────────────────────────────────────────
_blip_processor = None
_blip_model     = None


def get_blip():
    global _blip_processor, _blip_model
    if _blip_model is None:
        _blip_processor = BlipProcessor.from_pretrained(BLIP_MODEL)
        _blip_model     = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL)
        _blip_model.eval()
    return _blip_processor, _blip_model


# ── Helpers ────────────────────────────────────────────────────────────────────
def caption(img: Image.Image) -> str:
    proc, model = get_blip()
    inputs = proc(images=img, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=80)
    return proc.decode(out[0], skip_special_tokens=True).strip()


def ocr(img: Image.Image) -> str:
    return pytesseract.image_to_string(img).strip()


def load_index():
    if not IMAGE_FAISS_INDEX.exists():
        sys.exit("Index not found — run image_ingest.py first.")
    return faiss.read_index(str(IMAGE_FAISS_INDEX)), json.loads(IMAGE_INDEX_FILE.read_text())


def retrieve(query_vec: np.ndarray, faiss_index, metadata: list, top_k: int) -> list:
    scores, indices = faiss_index.search(query_vec.reshape(1, -1), top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        r = dict(metadata[idx])
        r["score"] = float(score)
        results.append(r)
    return results


def preprocess_query_image(query_context: str, img: Image.Image, embedder: CLIPEmbedder) -> np.ndarray:
    return embedder.embed_fused(img, query_context.strip())


def build_context(results: list) -> str:
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(
            f"[{i}] Source: {r['source']}\n"
            f"     Caption: {r.get('caption', '')}\n"
            f"     OCR Text: {r.get('ocr_text', '') or 'None'}"
        )
    return "\n\n".join(lines)


def show(results, title):
    print(f"\n{'═'*65}\n  {title}\n{'═'*65}")
    for i, r in enumerate(results, 1):
        page = f"  (page {r['page']})" if r.get("page") else ""
        print(f"\n  [{i}] score={r['score']:.4f}")
        print(f"       src    : {r['source']}{page}")
        print(f"       caption: {r.get('caption', '')}")
        if r.get("ocr_text"):
            print(f"       ocr    : {r['ocr_text'][:120]}…")
    print()


# ── Modes ──────────────────────────────────────────────────────────────────────
def mode_text_to_image(faiss_index, metadata, embedder, top_k):
    query = input("\n  Describe what you're looking for: ").strip()
    if not query:
        return
    vec = embedder.embed_text(query)
    show(retrieve(vec, faiss_index, metadata, top_k), "TEXT → IMAGE")


def mode_image_to_image(faiss_index, metadata, embedder, top_k):
    path = input("\n  Query image path: ").strip().strip("\"'")
    if not Path(path).exists():
        print(f"  File not found: {path}")
        return

    img            = Image.open(path).convert("RGB")
    query_caption  = caption(img)
    query_ocr      = ocr(img)
    complete_query = f"query_caption:{query_caption}\nQuery_OCR:{query_ocr}".strip()
    query_vec      = preprocess_query_image(complete_query, img, embedder)
    show(retrieve(query_vec, faiss_index, metadata, top_k), "IMAGE → IMAGE")


def mode_image_to_text(faiss_index, metadata, embedder, top_k):
    path = input("\n  Query image path: ").strip().strip("\"'")
    if not Path(path).exists():
        print(f"  File not found: {path}")
        return
    question = input("  Your question: ").strip()
    if not question:
        return

    img            = Image.open(path).convert("RGB")
    query_caption  = caption(img)
    query_ocr      = ocr(img)
    complete_query = f"query_caption:{query_caption}\nQuery_OCR:{query_ocr}".strip()
    query_vec      = preprocess_query_image(complete_query, img, embedder)
    results        = retrieve(query_vec, faiss_index, metadata, top_k)
    show(results, "RETRIEVED CONTEXT")

    context = build_context(results)
    prompt  = RAG_PROMPT.format(query_caption=query_caption, context=context, question=question)
    answer  = client.models.generate_content(model=GEMINI_MODEL, contents=prompt).text

    print(f"{'═'*65}")
    print(f"  ❓ {question}")
    print(f"  💡 {answer}")
    print(f"{'═'*65}\n")


# ── Menu ───────────────────────────────────────────────────────────────────────
MENU = """
╔══════════════════════════════════════════╗
║          Multimodal-RAG Image Search     ║
╠══════════════════════════════════════════╣
║  1.  Text  → Image                       ║
║  2.  Image → Image                       ║
║  3.  Image → Text Answer (Gemini)        ║
║  q.  Quit                                ║
╚══════════════════════════════════════════╝
"""


def main(top_k: int = TOP_K):
    faiss_index, metadata = load_index()
    embedder = CLIPEmbedder()
    get_blip()   # load BLIP once before menu

    print(MENU)
    while True:
        choice = input("  Select [1/2/3/q]: ").strip().lower()
        if choice == "q":
            print("  Goodbye! 👋")
            break
        elif choice == "1":
            mode_text_to_image(faiss_index, metadata, embedder, top_k)
        elif choice == "2":
            mode_image_to_image(faiss_index, metadata, embedder, top_k)
        elif choice == "3":
            mode_image_to_text(faiss_index, metadata, embedder, top_k)
        else:
            print("  Invalid choice.")
        print(MENU)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top_k", type=int, default=TOP_K)
    main(parser.parse_args().top_k)