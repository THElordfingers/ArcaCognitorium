#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/memory/chronicle.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════
from __future__ import annotations

import os
import pickle
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
from math import sqrt

from client.config import AppConfig


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    return dot / (na * nb + 1e-10)


@dataclass
class VectorItem:
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]


class Chronicle:

    EMBED_MODEL = "all-MiniLM-L6-v2"

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.path = cfg.storage.vectors_path
        self.items: List[VectorItem] = []
        self._embedder = None
        self._load()

    def _get_embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(self.EMBED_MODEL)
        return self._embedder

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                raw = pickle.load(f)
            self.items = [VectorItem(**x) if isinstance(x, dict) else x for x in raw]

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "wb") as f:
            pickle.dump(
                [{"text": it.text, "embedding": it.embedding, "metadata": it.metadata}
                 for it in self.items],
                f,
            )

    def embed(self, text: str) -> List[float]:
        return self._get_embedder().encode(text, convert_to_numpy=True).tolist()

    def add(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        metadata = metadata or {}
        emb = self.embed(text)
        self.items.append(VectorItem(text=text, embedding=emb, metadata=metadata))
        self._save()

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        *,
        conversation_ids: Optional[Iterable[str]] = None,
        thread_by_conversation: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        if not self.items:
            return []

        allow_cids: Optional[set] = None
        if conversation_ids is not None:
            allow_cids = {str(x) for x in conversation_ids}

        tmap: Optional[Dict[str, str]] = None
        if thread_by_conversation is not None:
            tmap = {str(k): str(v or "main") for k, v in thread_by_conversation.items()}

        q = self.embed(query_text)
        scored: List[Tuple[float, VectorItem]] = []

        for it in self.items:
            meta = it.metadata or {}
            cid = meta.get("conversation_id", None)
            if allow_cids is not None:
                if cid is None or str(cid) not in allow_cids:
                    continue
            if tmap is not None:
                if cid is None:
                    continue
                want_tid = tmap.get(str(cid), "main")
                have_tid = str(meta.get("thread_id", "main") or "main")
                if have_tid != want_tid:
                    continue
            scored.append((_cosine(q, it.embedding), it))

        scored.sort(key=lambda x: x[0], reverse=True)
        min_score = float(self.cfg.memory.min_relevance_score)
        out = []
        for score, it in scored[:top_k]:
            if score < min_score:
                continue
            out.append({"score": score, "text": it.text, "metadata": it.metadata})
        return out

    def stats(self) -> Dict[str, Any]:
        return {
            "count": len(self.items),
            "path": self.path,
            "embedding_model": self.EMBED_MODEL,
        }

    def add_from_distillation(self, text: str, metadata: dict | None = None) -> None:
        from datetime import datetime, timezone
        meta = metadata or {}
        meta["source"] = "distillation"
        meta["extracted_at"] = datetime.now(timezone.utc).isoformat()
        self.add(text, metadata=meta)
