#╔═══════════════════════   
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨    
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨     
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨       
#║ ⛨        
#║ ⛨    gpt-client/memory/file_ingest.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════════════


from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from client.config import AppConfig
from memory.vector_store import VectorStore


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == s[-1]) and s[0] in ("'", '"')):
        return s[1:-1]
    return s


def _abs(p: str) -> str:
    return os.path.abspath(os.path.expanduser(p))


def _is_under_roots(path: str, roots: List[str]) -> bool:
    path_abs = _abs(path)
    root_abs = [_abs(r) for r in roots] if roots else []
    if not root_abs:
        return True
    for r in root_abs:
        try:
            if os.path.commonpath([path_abs, r]) == r:
                return True
        except Exception:
            continue
    return False


def _chunk_text(text: str, chunk_chars: int, overlap_chars: int) -> List[Tuple[int, int, str]]:
    t = (text or "").strip()
    if not t:
        return []

    chunk_chars = max(200, int(chunk_chars))
    overlap_chars = max(0, min(int(overlap_chars), chunk_chars - 1))

    out: List[Tuple[int, int, str]] = []
    start = 0
    n = len(t)

    while start < n:
        end = min(n, start + chunk_chars)
        chunk = t[start:end].strip()
        if chunk:
            out.append((start, end, chunk))
        if end >= n:
            break
        start = max(0, end - overlap_chars)

    return out


@dataclass
class IngestResult:
    path: str
    bytes_read: int
    chunks_added: int


class TextFileIngestor:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg

    def ingest_file(self, path: str, vectors: VectorStore, *, tag: str = "file") -> IngestResult:
        mem = self.cfg.memory
        ingest_cfg = mem.ingest

        raw_path = _strip_quotes(path)
        full_path = _abs(raw_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")
        if not os.path.isfile(full_path):
            raise ValueError(f"Not a file: {full_path}")

        allowed_roots = list(ingest_cfg.allowed_roots or [])
        if not _is_under_roots(full_path, allowed_roots):
            raise PermissionError(
                f"Refusing to ingest outside allowed_roots. File: {full_path} | allowed_roots={allowed_roots}"
            )

        max_bytes = int(ingest_cfg.max_file_bytes)
        size = os.path.getsize(full_path)
        if size > max_bytes:
            raise ValueError(f"File too large ({size} bytes). max_file_bytes={max_bytes}")

        with open(full_path, "rb") as f:
            data = f.read()

        # Decode as utf-8 with replacement to avoid crashes on odd bytes.
        text = data.decode("utf-8", errors="replace")
        text = text.replace("\x00", "")

        chunk_chars = int(ingest_cfg.chunk_chars)
        overlap = int(ingest_cfg.chunk_overlap_chars)
        chunks = _chunk_text(text, chunk_chars=chunk_chars, overlap_chars=overlap)

        st = os.stat(full_path)
        mtime = datetime.fromtimestamp(st.st_mtime).isoformat()

        added = 0
        for idx, (start, end, chunk) in enumerate(chunks):
            vectors.add(
                chunk,
                metadata={
                    "type": "file_chunk",
                    "tag": tag,
                    "source_path": full_path,
                    "source_name": os.path.basename(full_path),
                    "chunk_index": idx,
                    "chunk_start": start,
                    "chunk_end": end,
                    "file_mtime": mtime,
                    "file_bytes": size,
                },
            )
            added += 1

        return IngestResult(path=full_path, bytes_read=size, chunks_added=added)

    def ingest_dir(self, dir_path: str, vectors: VectorStore, *, tag: str = "dir") -> List[IngestResult]:
        mem = self.cfg.memory
        ingest_cfg = mem.ingest

        raw_dir = _strip_quotes(dir_path)
        full_dir = _abs(raw_dir)

        if not os.path.exists(full_dir):
            raise FileNotFoundError(f"Directory not found: {full_dir}")
        if not os.path.isdir(full_dir):
            raise ValueError(f"Not a directory: {full_dir}")

        allowed_roots = list(ingest_cfg.allowed_roots or [])
        if not _is_under_roots(full_dir, allowed_roots):
            raise PermissionError(
                f"Refusing to ingest outside allowed_roots. Dir: {full_dir} | allowed_roots={allowed_roots}"
            )

        exts = set([e.lower() for e in (ingest_cfg.allowed_extensions or [])])
        results: List[IngestResult] = []

        for root, _, files in os.walk(full_dir):
            for name in files:
                _, ext = os.path.splitext(name)
                if exts and ext.lower() not in exts:
                    continue
                p = os.path.join(root, name)
                try:
                    results.append(self.ingest_file(p, vectors, tag=tag))
                except Exception:
                    # Keep directory ingestion robust; skip files that fail.
                    continue

        return results
