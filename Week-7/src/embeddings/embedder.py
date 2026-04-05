from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings


class Embedder(Embeddings):
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-small-en")

    def embed_documents(self, texts):
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings.tolist()

    def embed_query(self, text):
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embedding.tolist()