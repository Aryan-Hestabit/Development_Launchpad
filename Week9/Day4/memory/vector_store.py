import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

import numpy as np

from autogen_core.memory import Memory, MemoryContent, MemoryMimeType, MemoryQueryResult
from autogen_core.model_context import ChatCompletionContext
from autogen_core.models import SystemMessage
import faiss
from sentence_transformers import SentenceTransformer
logger = logging.getLogger(__name__)

DB_PATH         = os.path.join(os.path.dirname(__file__), "long_term.db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM   = 384

class FAISSVectorMemory(Memory):
    """
    Long-term persistent memory: SQLite (durable) + FAISS (vector search).
    Implements the AutoGen Memory protocol.
    """

    def __init__(self, db_path: str = DB_PATH, top_k: int = 3, score_threshold: float = 0.28) -> None:
        self.db_path         = db_path
        self.top_k           = top_k
        self.score_threshold = score_threshold
        self._encoder        = SentenceTransformer(EMBEDDING_MODEL)
        self._index          = faiss.IndexFlatIP(EMBEDDING_DIM)
        self._fact_ids: List[int] = []
        self._conn: Optional[sqlite3.Connection] = None
        self._ready          = False

    def initialize(self) -> None:
        if self._ready:
            return

        # SQLite — create DB and table if they don't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                content  TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'fact',
                source   TEXT NOT NULL DEFAULT 'llm_extractor',
                ts       TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}'
            )
        """)
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_cat ON facts (category)")
        self._conn.commit()

        # Rebuild FAISS from all persisted facts in SQLite
        rows = self._conn.execute("SELECT id, content FROM facts ORDER BY id").fetchall()
        if rows:
            vecs = self._encode_batch([r["content"] for r in rows])
            self._index.add(vecs)
            self._fact_ids = [r["id"] for r in rows]

        self._ready = True

    def _encode(self, text: str) -> np.ndarray:
        """Encode one string → L2-normalised float32 (1, DIM)."""
        vec = self._encoder.encode([text], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(vec)
        return vec

    def _encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode list of strings → L2-normalised float32 (N, DIM)."""
        vecs = self._encoder.encode(texts, convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(vecs)
        return vecs

    async def add(self, content: MemoryContent, cancellation_token=None) -> None:
        """
        Write fact to SQLite AND FAISS simultaneously.
        SQLite committed first (durable), then FAISS updated (searchable).
        """
        text     = str(content.content)
        meta     = content.metadata or {}
        category = meta.get("category", "fact")
        source   = meta.get("source", "llm_extractor")
        ts       = datetime.now(timezone.utc).isoformat()
        extra    = {k: v for k, v in meta.items() if k not in ("category", "source")}

        cursor = self._conn.execute(
            "INSERT INTO facts (content, category, source, ts, metadata) VALUES (?, ?, ?, ?, ?)",
            (text, category, source, ts, json.dumps(extra)),
        )
        self._conn.commit()

        self._index.add(self._encode(text))
        self._fact_ids.append(cursor.lastrowid)

    async def store_facts(self, facts: List[dict], session_id: str, turn: int) -> None:
        for fact in facts:
            await self.add(MemoryContent(
                content=fact["content"],
                mime_type=MemoryMimeType.TEXT,
                metadata={
                    "category"  : fact["category"],
                    "source"    : "llm_extractor",
                    "session_id": session_id,
                    "turn"      : turn,
                },
            ))

    async def query(self, query: str, cancellation_token=None, **kwargs) -> MemoryQueryResult:
        """Cosine similarity search — returns top-k most relevant facts."""
        if self._index.ntotal == 0:
            return MemoryQueryResult(results=[])

        k = min(self.top_k, self._index.ntotal)
        scores, indices = self._index.search(self._encode(query), k)

        results: List[MemoryContent] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or float(score) < self.score_threshold:
                continue
            row = self._conn.execute(
                "SELECT content, category, ts FROM facts WHERE id = ?",
                (self._fact_ids[idx],),
            ).fetchone()
            if row:
                results.append(MemoryContent(
                    content=row["content"],
                    mime_type=MemoryMimeType.TEXT,
                    metadata={"category": row["category"], "ts": row["ts"], "score": round(float(score), 4)},
                ))

        return MemoryQueryResult(results=results)

    async def update_context(self, model_context: ChatCompletionContext) -> None:
        if self._index.ntotal == 0:
            return

        messages = await model_context.get_messages()
        last_user: Optional[str] = next(
            (str(m.content) for m in reversed(messages) if getattr(m, "source", None) == "user"),
            None,
        )
        if not last_user:
            return

        result = await self.query(last_user)
        if not result.results:
            return

        lines = [f"\n[LONG-TERM MEMORY — {len(result.results)} fact(s) recalled]"]
        for i, item in enumerate(result.results, 1):
            m = item.metadata or {}
            lines.append(f"  [{i}] ({m.get('category', 'fact')}, score={m.get('score', '?')}) {item.content}")
        lines.append("[END LONG-TERM MEMORY]")

        await model_context.add_message(SystemMessage(content="\n".join(lines)))

    async def clear(self) -> None:
        self._conn.execute("DELETE FROM facts")
        self._conn.commit()
        self._index.reset()
        self._fact_ids.clear()

    async def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def fact_count(self) -> int:
        if not self._conn:
            return 0
        return self._conn.execute("SELECT COUNT(*) AS n FROM facts").fetchone()["n"]

    def display_all(self) -> None:
        """Print all stored facts to stdout."""
        rows = self._conn.execute("SELECT id, category, content FROM facts ORDER BY id").fetchall()
        print(f"\n{'='*65}")
        print(f"  LONG-TERM MEMORY — {len(rows)} facts | {self.db_path}")
        print(f"{'='*65}")
        for r in rows:
            print(f"  [{r['id']:03d}] [{r['category']:12s}] {r['content'][:70]}")
        print(f"{'='*65}\n")