# Multimodal RAG — Day 3

This document summarizes the Day 3 multimodal retrieval-augmented generation (RAG) pipeline, including image embedding, ingestion, and retrieval/search components.

## Overview

The Day 3 folder implements a multimodal RAG flow that combines image and text embeddings for visual search and question answering over image content.

Key ideas:
- Use CLIP to embed both images and text into a shared vector space.
- Extract image captions and OCR text from visual content using BLIP and Tesseract.
- Fuse image and text embeddings into a single multimodal representation.
- Store fused embeddings in a FAISS index for similarity search.
- Support text-to-image retrieval, image-to-image retrieval, and image-to-text Q&A.

## Files

- `embeddings/clip_embedder.py`
  - Defines `CLIPEmbedder` for computing image, text, and fused embeddings.
  - Uses `transformers` CLIP model and processor.
  - Combines image and text vectors with `IMAGE_WEIGHT` and `TEXT_WEIGHT`.

- `pipelines/image_ingest.py`
  - Ingests images and PDF pages from `IMAGES_DIR`.
  - Generates captions via BLIP and OCR text via Tesseract.
  - Creates LangChain `Document` objects for downstream context.
  - Computes fused embeddings and saves them into a FAISS index.
  - Writes ingestion metadata to `IMAGE_INDEX_FILE`.

- `retriever/image_search.py`
  - Loads the FAISS index and metadata.
  - Provides search modes:
    - `Text → Image`
    - `Image → Image`
    - `Image → Text` with Gemini answer generation
  - Uses BLIP to caption and OCR query images.
  - Builds a retrieval prompt and sends it to Google Gemini for natural-language answers.

## Pipeline

1. `image_ingest.py` collects image files and PDF pages.
2. For each visual input:
   - Caption is generated with BLIP.
   - OCR text is extracted with Tesseract.
   - Combined text is formed from caption + OCR.
   - Fused embedding is created from image and combined text.
3. Embeddings are indexed in FAISS and metadata is saved.
4. `image_search.py` loads the index and uses CLIP embeddings for retrieval.

## Search Modes

### Text → Image
- User enters a text query.
- The query is embedded with CLIP text encoder.
- FAISS returns the top visually relevant images.

### Image → Image
- User provides a query image path.
- The query image is captioned and OCRed.
- A fused query embedding is computed and used for similarity search.

### Image → Text
- User provides a query image and a question.
- The system retrieves similar indexed images.
- It formats retrieved context and the query image caption into a RAG prompt.
- Answer generation is performed using Google Gemini.

## Configuration

The implementation relies on `config.settings` for constants such as:
- `CLIP_MODEL`
- `BLIP_MODEL`
- `IMAGE_WEIGHT`
- `TEXT_WEIGHT`
- `IMAGES_DIR`
- `VECTORSTORE_PATH`
- `IMAGE_INDEX_FILE`
- `IMAGE_FAISS_INDEX`
- `TOP_K`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`

## Running the pipeline

1. Ingest images and build the index:

```bash
python Day-3/pipelines/image_ingest.py
```

2. Run the interactive search app:

```bash
python Day-3/retriever/image_search.py
```

## Notes

- The `embed_fused` method normalizes the fused vector after combining image and text features.
- FAISS index uses `IndexFlatIP` on normalized vectors for cosine similarity.
- PDF pages are handled as separate image records with `page` metadata.
- The image search app has a simple terminal menu for user interaction.
