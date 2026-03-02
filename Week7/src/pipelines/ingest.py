import os
import json
from pathlib import Path
import re

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
)
from langchain_community.docstore import InMemoryDocstore
import numpy as np
import faiss
from langchain_text_splitters import TokenTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import faiss
from src.embeddings.embedder import Embedder
from src.config.settings import (
    RAW_DATA_PATH,
    CHUNK_OUTPUT_PATH,
    VECTORSTORE_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


CHUNK_FILE = os.path.join(CHUNK_OUTPUT_PATH, "chunks.json")


# ==============================
# DOCUMENT LOADING
# ==============================

def load_documents_from_directory(directory: str):
    documents = []

    for file_path in Path(directory).rglob("*"):
        if file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif file_path.suffix.lower() == ".txt":
            loader = TextLoader(str(file_path))
        elif file_path.suffix.lower() == ".csv":
            loader = CSVLoader(str(file_path))
        elif file_path.suffix.lower() == ".docx":
            loader = Docx2txtLoader(str(file_path))
        else:
            continue

        docs = loader.load()

        for doc in docs:
            doc.metadata["source"] = file_path.name

        documents.extend(docs)

    return documents


# ==============================
# TEXT CLEANING
# ==============================

def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


# ==============================
# CHUNKING
# ==============================

def chunk_documents(documents):
    splitter = TokenTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunked_docs = []

    for doc in documents:
        cleaned_text = clean_text(doc.page_content)
        chunks = splitter.split_text(cleaned_text)

        for i, chunk in enumerate(chunks):
            metadata = dict(doc.metadata)
            metadata["chunk_id"] = i

            chunked_docs.append(
                Document(page_content=chunk, metadata=metadata)
            )

    return chunked_docs


# ==============================
# SAVE CHUNKS (Optional Debug)
# ==============================

def save_chunks(chunked_docs):
    os.makedirs(CHUNK_OUTPUT_PATH, exist_ok=True)

    serializable = [
        {"text": doc.page_content, "metadata": doc.metadata}
        for doc in chunked_docs
    ]

    with open(CHUNK_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)

    print(f"Saved chunks to {CHUNK_FILE}")


# ==============================
# MAIN INGEST FUNCTION
# ==============================

def run_ingestion():

    print("Loading documents...")
    documents = load_documents_from_directory(RAW_DATA_PATH)
    print(f"Loaded {len(documents)} documents.")

    print("Chunking documents...")
    chunked_docs = chunk_documents(documents)
    print(f"Created {len(chunked_docs)} chunks.")

    save_chunks(chunked_docs)

    print("Loading embedder...")
    embedder = Embedder()

    print("Generating embeddings...")
    texts = [doc.page_content for doc in chunked_docs]
    embeddings = embedder.embed_documents(texts)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    print("Building FAISS IndexFlatIP...")
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    vectorstore = FAISS(
        embedding_function=embedder,
        index=index,
        docstore=None,
        index_to_docstore_id=None,
    )

    # Manually assign docstore

    docstore = InMemoryDocstore(
        {str(i): doc for i, doc in enumerate(chunked_docs)}
    )

    vectorstore.docstore = docstore
    vectorstore.index_to_docstore_id = {
        i: str(i) for i in range(len(chunked_docs))
    }

    os.makedirs(VECTORSTORE_PATH, exist_ok=True)

    print("Saving vectorstore...")
    vectorstore.save_local(VECTORSTORE_PATH)

    print("Ingestion completed successfully.")

if __name__ == "__main__":
    run_ingestion()