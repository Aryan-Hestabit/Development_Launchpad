import os , sqlite3 , faiss, logging
import numpy as np
import logging
from datetime import datetime, timezone

from autogen_core.model_context import ChatCompletionContext
from autogen_core.models import SystemMessage
from sentence_transformers import SentenceTransformer
from autogen_core.memory import Memory, MemoryContent, MemoryQueryResult, MemoryMimeType
logger = logging.getLogger(__name__)

INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss.index")
DB_PATH    = os.path.join(os.path.dirname(__file__), "long_term.db")

class FAISSVectorMemory(Memory):
    def __init__(self, top_k=5, score_threshold=0.2):
        self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self._index = faiss.IndexFlatIP(384)
        self._fact_ids = []
        self.top_k = top_k
        self.score_threshold = score_threshold

    def initialize(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._conn.execute("CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY, content TEXT, category TEXT, ts TEXT)")
        self._conn.commit()

        if os.path.exists(INDEX_PATH):
            self._index = faiss.read_index(INDEX_PATH)
            self._fact_ids = [r[0] for r in self._conn.execute("SELECT id FROM facts ORDER BY id").fetchall()]
            print(f"  Long-term facts  previous loaded: {len(self._fact_ids)}")
        else:
            self._rebuild_index()
            print(f"  Long-term facts loaded: {len(self._fact_ids)}")

    def _rebuild_index(self):
        rows = self._conn.execute("SELECT id, content FROM facts ORDER BY id").fetchall()
        if rows:
            embeddings = self._encoder.encode([r[1] for r in rows])
            faiss.normalize_L2(embeddings)
            self._index.add(np.array(embeddings).astype('float32'))
            self._fact_ids = [r[0] for r in rows]

    async def is_duplicate(self, text: str, threshold: float = 0.9) -> bool:
        """Check if a similar fact already exists in the vector store."""
        if self._index.ntotal == 0: return False
        vec = self._encoder.encode([text])
        faiss.normalize_L2(vec)
        scores, _ = self._index.search(vec.astype('float32'), 1)
        return scores[0][0] > threshold

    async def add(self, content: MemoryContent, **kwargs) -> None:
        text = str(content.content)
        
        # Internal Deduplication Check
        if await self.is_duplicate(text):
            return 

        category = content.metadata.get("category", "fact")
        ts = datetime.now(timezone.utc).isoformat()

        cursor = self._conn.execute("INSERT INTO facts (content, category, ts) VALUES (?, ?, ?)", (text, category, ts))
        self._conn.commit()
        
        vec = self._encoder.encode([text])
        faiss.normalize_L2(vec)
        self._index.add(vec.astype('float32'))
        self._fact_ids.append(cursor.lastrowid)
        faiss.write_index(self._index, INDEX_PATH)

    # ... query, update_context, and get_all_facts remain as previously discussed ...

    async def query(self, query_text: str, **kwargs) -> MemoryQueryResult:
        if self._index.ntotal == 0:
            return MemoryQueryResult(results=[])

        vec = self._encoder.encode([query_text])
        faiss.normalize_L2(vec)
        scores, indices = self._index.search(vec.astype('float32'), self.top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            print(f"📊 Raw Score found: {score} for index {idx}")
            if idx != -1 and float(score) >= self.score_threshold:
                # Map FAISS index back to SQLite ID
                db_id = self._fact_ids[idx]
                row = self._conn.execute("SELECT content FROM facts WHERE id=?", (db_id,)).fetchone()
                if row:
                    results.append(MemoryContent(content=row[0], mime_type=MemoryMimeType.TEXT, metadata={"score": float(score)}))
        print(f"\n  [Memory Query] Retrieved {len(results)} relevant fact(s) for query: '{query_text}'")
        return MemoryQueryResult(results=results)

    async def update_context(self, model_context: ChatCompletionContext) -> None:
        """Standard AutoGen hook to inject facts into the prompt."""
        messages = await model_context.get_messages()
        last_user = next((str(m.content) for m in reversed(messages) if getattr(m, "source", None) == "user"), None)
        
        mem_results = await self.query(last_user)

        if not mem_results.results: 
            print(f"No relevant facts found for memory recall.")
            return

        context_str = "\n[LONG-TERM MEMORY RECALL]\n"
        context_str += "\n".join([f"- {res.content}" for res in mem_results.results])
        context_str += "\n[END MEMORY]\n"

        await model_context.add_message(SystemMessage(content=context_str))

    def get_all_facts(self):
        """Returns all facts for the 'facts' command."""
        return self._conn.execute("SELECT category, content, ts FROM facts ORDER BY ts DESC").fetchall()

    async def clear(self) -> None:
        self._conn.execute("DELETE FROM facts")
        self._conn.commit()
        self._index.reset()
        self._fact_ids.clear()
        if os.path.exists(INDEX_PATH): os.remove(INDEX_PATH)

    async def close(self) -> None:
        if self._conn: self._conn.close()
