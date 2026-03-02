from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever

from src.embeddings.embedder import Embedder
from src.retriever.reranker import Reranker
from src.config.settings import VECTORSTORE_PATH, TOP_K


# --------------------------------------------------
# Utility Functions
# --------------------------------------------------

def apply_filters(documents, filters):
    if not filters:
        return documents

    return [
        doc for doc in documents
        if all(doc.metadata.get(k) == v for k, v in filters.items())
    ]


def deduplicate(documents):
    seen = set()
    unique_docs = []

    for doc in documents:
        identifier = (
            doc.metadata.get("source"),
            doc.metadata.get("page"),
            doc.metadata.get("chunk_id"),
        )

        if identifier not in seen:
            unique_docs.append(doc)
            seen.add(identifier)

    return unique_docs


# --------------------------------------------------
# Hybrid Retriever Class (Load Once)
# --------------------------------------------------

class HybridRetriever:

    def __init__(self):

        print("Loading embedder...")
        self.embedder = Embedder()

        print("Loading FAISS vectorstore...")
        self.vectorstore = FAISS.load_local(
            folder_path=str(VECTORSTORE_PATH),
            embeddings=self.embedder,
            allow_dangerous_deserialization=True
        )

        print("Initializing semantic retriever (MMR)...")
        self.semantic_retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 10, "fetch_k": 20}
        )

        print("Building BM25 retriever...")
        all_docs = list(self.vectorstore.docstore._dict.values())
        self.bm25 = BM25Retriever.from_documents(all_docs)
        self.bm25.k = 5

        print("Loading reranker...")
        self.reranker = Reranker()

        print("Hybrid Retriever Ready.\n")

    # --------------------------------------------------
    # Retrieve Method
    # --------------------------------------------------

    def retrieve(self, query: str, top_k: int = TOP_K, filters: dict = None):

        # Semantic retrieval
        semantic_docs = self.semantic_retriever.invoke(query)

        # Keyword retrieval
        keyword_docs = self.bm25.invoke(query)

        # Merge
        merged_docs = semantic_docs + keyword_docs

        # Apply filters
        merged_docs = apply_filters(merged_docs, filters)

        # Deduplicate
        merged_docs = deduplicate(merged_docs)

        # Rerank
        reranked_docs = self.reranker.rerank(query, merged_docs)

        return reranked_docs[:top_k]