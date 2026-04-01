# Departamentum Documentalis — library.py
# v1.0.0
"""SQLite registry of produced documents."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT    NOT NULL,
    doc_type        TEXT    NOT NULL,
    source_path     TEXT    DEFAULT '',
    wiz_path        TEXT    DEFAULT '',
    md_path         TEXT    DEFAULT '',
    bureau_json     TEXT    DEFAULT '',
    version         TEXT    DEFAULT '1.0',
    author          TEXT    DEFAULT '',
    theme           TEXT    DEFAULT 'wizdoc',
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL,
    is_archived     INTEGER NOT NULL DEFAULT 0
);
"""


class DocumentLibrary:
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._conn = None
        self._enabled = True

    def initialize(self) -> bool:
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.executescript(_SCHEMA_SQL)
            self._conn.commit()
            return True
        except (sqlite3.Error, OSError):
            self._enabled = False
            return False

    @property
    def enabled(self) -> bool:
        return self._enabled and self._conn is not None

    def record(self, title: str, doc_type: str, source_path: str = '',
               wiz_path: str = '', md_path: str = '',
               bureau_json: str = '', version: str = '1.0',
               author: str = '', theme: str = 'wizdoc') -> int:
        if not self.enabled:
            raise RuntimeError("Library disabled")
        now = datetime.now(timezone.utc).isoformat()
        cur = self._conn.execute(
            """INSERT INTO documents
               (title, doc_type, source_path, wiz_path, md_path,
                bureau_json, version, author, theme, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, doc_type, source_path, wiz_path, md_path,
             bureau_json, version, author, theme, now, now)
        )
        self._conn.commit()
        return cur.lastrowid

    def list_documents(self, doc_type: str = None) -> list[dict]:
        if not self.enabled:
            return []
        q = "SELECT * FROM documents WHERE is_archived = 0"
        params = []
        if doc_type:
            q += " AND doc_type = ?"
            params.append(doc_type)
        q += " ORDER BY updated_at DESC"
        return [dict(r) for r in self._conn.execute(q, params).fetchall()]

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
