import argparse
import json
import sys
import uuid
from pathlib import Path

import faiss
import numpy as np
import torch
from PIL import Image
from tqdm import tqdm
from transformers import BlipForConditionalGeneration, BlipProcessor
from pdf2image import convert_from_path
import pytesseract

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from embeddings.clip_embedder import CLIPEmbedder
from langchain_core.documents import Document
from config.settings import (
    IMAGES_DIR, VECTORSTORE_PATH, IMAGE_INDEX_FILE,
    IMAGE_FAISS_INDEX, IMG_EXTS, BLIP_MODEL,
)

blip_processor = BlipProcessor.from_pretrained(BLIP_MODEL)
blip_model     = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL)
blip_model.eval()


def caption(img: Image.Image) -> str:
    inputs = blip_processor(images=img, return_tensors="pt")
    with torch.no_grad():
        out = blip_model.generate(**inputs, max_new_tokens=80)
    return blip_processor.decode(out[0], skip_special_tokens=True).strip()


def ocr(img: Image.Image) -> str:
    return pytesseract.image_to_string(img).strip()


def collect_tasks(images_dir: Path) -> list:
    tasks = []
    for ext in IMG_EXTS:
        for p in images_dir.rglob(f"*{ext}"):
            tasks.append((Image.open(p).convert("RGB"), str(p), None))
    for p in images_dir.rglob("*.pdf"):
        for i, page_img in enumerate(convert_from_path(str(p), dpi=200)):
            tasks.append((page_img, f"{p}::page{i+1}", i + 1))
    return tasks


def run_ingestion(images_dir: Path = IMAGES_DIR):
    embedder = CLIPEmbedder()
    tasks    = collect_tasks(images_dir)

    if not tasks:
        print("No images found.")
        return

    records, fused_vecs = [], []

    for img, src, page in tqdm(tasks, desc="Ingesting"):
        cap          = caption(img)
        ocr_text     = ocr(img)
        combined     = f"{cap} {ocr_text}".strip()

        # LangChain Document — combined text as page_content for downstream use
        lc_doc = Document(
            page_content=combined,
            metadata={"source": src, "page": page, "caption": cap},
        )

        # Fused embedding: 0.5 * image_vec + 0.5 * text_vec, re-normalised
        fused = embedder.embed_fused(img, combined)

        records.append({
            "id":              str(uuid.uuid4()),
            "source":          src,
            "page":            page,
            "caption":         cap,
            "ocr_text":        ocr_text,
            "combined_text":   combined,
            "lc_page_content": lc_doc.page_content,
            "embedding_index": len(records),
        })
        fused_vecs.append(fused)

    # Build FAISS IndexFlatIP (exact cosine sim on L2-normalised vectors)
    dim          = fused_vecs[0].shape[0]   # 512
    faiss_index  = faiss.IndexFlatIP(dim)
    faiss_index.add(np.array(fused_vecs, dtype=np.float32))

    VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)
    faiss.write_index(faiss_index, str(IMAGE_FAISS_INDEX))
    IMAGE_INDEX_FILE.write_text(json.dumps(records, indent=2))

    print(f"✅  Done. Indexed: {len(records)} images → {IMAGE_FAISS_INDEX}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_dir", type=Path, default=IMAGES_DIR)
    args = parser.parse_args()
    run_ingestion(args.images_dir)