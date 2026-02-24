from pathlib import Path

from langchain_community.vectorstores import FAISS

from src.embeddings.embedder import Embedder
from src.config.settings import (
    VECTORSTORE_PATH,
    TOP_K
)

class QueryEngine:
    def __init__(self):
        print("Loading embedder...")
        self.embedder = Embedder()

        print("Loading FAISS vectorstore...")
        self.vectorstore = FAISS.load_local(
            folder_path=str(VECTORSTORE_PATH),
            embeddings=self.embedder,
            allow_dangerous_deserialization=True
        )

    def search(self, query: str, top_k: int = TOP_K):

        results = self.vectorstore.similarity_search_with_score(
            query,
            k=top_k
        )

        formatted_results = []

        for doc, score in results:
            formatted_results.append({
                "score": float(score),
                "metadata": doc.metadata,
                "preview": doc.page_content[:300]
            })

        return formatted_results


# ==============================
# TESTING
# ==============================

if __name__ == "__main__":
    engine = QueryEngine()

    while True:
        query = input("\nEnter your query (or type 'exit'): ")

        if query.lower() == "exit":
            break

        results = engine.search(query)

        print("\nTop Results:\n")

        for i, res in enumerate(results, 1):
            print(f"Result {i}")
            print(f"Score: {res['score']:.4f}")
            print(f"Metadata: {res['metadata']}")
            print(f"Preview: {res['preview'][:200]}")
            print("-" * 60)