# GNOSIUM EXANIMA — session/store.py
# v1.0.0
"""
SQLite store for sessions, messages, distillations, and entity_state.

All schemas are created on first connection via CREATE TABLE IF NOT EXISTS.
Writes are serialised through a per-instance threading lock so the store
is safe to call from both the main Qt thread and background workers.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..constants import MODE_CHAMBER, MODE_SOLO


# ─── Row dataclasses ───────────────────────────────────────────────
@dataclass
class SessionRow:
    id: str
    mode: str
    title: Optional[str]
    created_at: str
    updated_at: str
    active_entities: list[str] = field(default_factory=list)
    is_current: bool = False


@dataclass
class MessageRow:
    id: str
    session_id: str
    role: str              # 'wizard' or 'entity'
    entity_id: Optional[str]
    content: str
    timestamp: str


@dataclass
class DistillationRow:
    id: str
    session_id: str
    summary: str
    from_message_id: str
    to_message_id: str
    created_at: str
    token_estimate: Optional[int] = None


# ─── Schema ────────────────────────────────────────────────────────
_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id              TEXT PRIMARY KEY,
    mode            TEXT NOT NULL,
    title           TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    active_entities TEXT NOT NULL,
    is_current      INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_sessions_mode_current
    ON sessions(mode, is_current);

CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL,
    entity_id   TEXT,
    content     TEXT NOT NULL,
    timestamp   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_messages_session
    ON messages(session_id, timestamp);

CREATE TABLE IF NOT EXISTS distillations (
    id               TEXT PRIMARY KEY,
    session_id       TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    summary          TEXT NOT NULL,
    from_message_id  TEXT NOT NULL,
    to_message_id    TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    token_estimate   INTEGER
);

CREATE INDEX IF NOT EXISTS ix_distillations_session
    ON distillations(session_id, created_at);

CREATE TABLE IF NOT EXISTS entity_state (
    entity_id       TEXT PRIMARY KEY,
    last_loaded_at  TEXT,
    notes           TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


# ─── Store ─────────────────────────────────────────────────────────
class SessionStore:
    """Thread-safe SQLite persistence layer."""

    def __init__(self, db_path: Path):
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            str(self._path),
            check_same_thread=False,
            isolation_level=None,  # autocommit
        )
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.executescript(_SCHEMA)

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # ── Sessions ─────────────────────────────────────────────────
    def create_session(
        self,
        mode: str,
        entity_ids: list[str],
        title: Optional[str] = None,
    ) -> SessionRow:
        if mode not in (MODE_CHAMBER, MODE_SOLO):
            raise ValueError(f"invalid mode: {mode!r}")
        row = SessionRow(
            id=_new_id(),
            mode=mode,
            title=title,
            created_at=_now(),
            updated_at=_now(),
            active_entities=list(entity_ids),
            is_current=True,
        )
        with self._lock:
            self._conn.execute(
                "UPDATE sessions SET is_current = 0 WHERE mode = ?", (mode,)
            )
            self._conn.execute(
                "INSERT INTO sessions "
                "(id, mode, title, created_at, updated_at, active_entities, is_current) "
                "VALUES (?, ?, ?, ?, ?, ?, 1)",
                (row.id, row.mode, row.title, row.created_at,
                 row.updated_at, json.dumps(row.active_entities)),
            )
        return row

    def update_session(
        self,
        session_id: str,
        *,
        title: Optional[str] = None,
        active_entities: Optional[list[str]] = None,
    ) -> None:
        sets: list[str] = ["updated_at = ?"]
        params: list = [_now()]
        if title is not None:
            sets.append("title = ?")
            params.append(title)
        if active_entities is not None:
            sets.append("active_entities = ?")
            params.append(json.dumps(active_entities))
        params.append(session_id)
        with self._lock:
            self._conn.execute(
                f"UPDATE sessions SET {', '.join(sets)} WHERE id = ?", params
            )

    def set_current_session(self, session_id: str, mode: str) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE sessions SET is_current = 0 WHERE mode = ?", (mode,)
            )
            self._conn.execute(
                "UPDATE sessions SET is_current = 1 WHERE id = ?", (session_id,)
            )

    def delete_session(self, session_id: str) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

    def get_session(self, session_id: str) -> Optional[SessionRow]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            )
            row = cur.fetchone()
        return _row_to_session(row) if row else None

    def current_session(self, mode: str) -> Optional[SessionRow]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM sessions WHERE mode = ? AND is_current = 1 "
                "ORDER BY updated_at DESC LIMIT 1",
                (mode,),
            )
            row = cur.fetchone()
        return _row_to_session(row) if row else None

    def list_sessions(self, mode: Optional[str] = None) -> list[SessionRow]:
        with self._lock:
            if mode:
                cur = self._conn.execute(
                    "SELECT * FROM sessions WHERE mode = ? ORDER BY updated_at DESC",
                    (mode,),
                )
            else:
                cur = self._conn.execute(
                    "SELECT * FROM sessions ORDER BY updated_at DESC"
                )
            rows = cur.fetchall()
        return [_row_to_session(r) for r in rows]

    # ── Messages ─────────────────────────────────────────────────
    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        entity_id: Optional[str] = None,
    ) -> MessageRow:
        if role not in ("wizard", "entity"):
            raise ValueError(f"invalid role: {role!r}")
        row = MessageRow(
            id=_new_id(),
            session_id=session_id,
            role=role,
            entity_id=entity_id,
            content=content,
            timestamp=_now(),
        )
        with self._lock:
            self._conn.execute(
                "INSERT INTO messages (id, session_id, role, entity_id, content, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (row.id, row.session_id, row.role, row.entity_id,
                 row.content, row.timestamp),
            )
            self._conn.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (row.timestamp, session_id),
            )
        return row

    def load_messages(self, session_id: str) -> list[MessageRow]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp",
                (session_id,),
            )
            rows = cur.fetchall()
        return [
            MessageRow(
                id=r["id"], session_id=r["session_id"], role=r["role"],
                entity_id=r["entity_id"], content=r["content"],
                timestamp=r["timestamp"],
            ) for r in rows
        ]

    def message_count(self, session_id: str) -> int:
        with self._lock:
            cur = self._conn.execute(
                "SELECT COUNT(*) FROM messages WHERE session_id = ?", (session_id,)
            )
            return int(cur.fetchone()[0])

    # ── Distillations ────────────────────────────────────────────
    def write_distillation(
        self,
        session_id: str,
        summary: str,
        from_message_id: str,
        to_message_id: str,
        token_estimate: Optional[int] = None,
    ) -> DistillationRow:
        row = DistillationRow(
            id=_new_id(),
            session_id=session_id,
            summary=summary,
            from_message_id=from_message_id,
            to_message_id=to_message_id,
            created_at=_now(),
            token_estimate=token_estimate,
        )
        with self._lock:
            self._conn.execute(
                "INSERT INTO distillations "
                "(id, session_id, summary, from_message_id, to_message_id, "
                " created_at, token_estimate) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (row.id, row.session_id, row.summary, row.from_message_id,
                 row.to_message_id, row.created_at, row.token_estimate),
            )
        return row

    def load_distillations(self, session_id: str) -> list[DistillationRow]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM distillations WHERE session_id = ? "
                "ORDER BY created_at",
                (session_id,),
            )
            rows = cur.fetchall()
        return [
            DistillationRow(
                id=r["id"], session_id=r["session_id"], summary=r["summary"],
                from_message_id=r["from_message_id"],
                to_message_id=r["to_message_id"],
                created_at=r["created_at"],
                token_estimate=r["token_estimate"],
            ) for r in rows
        ]

    # ── Entity state ─────────────────────────────────────────────
    def touch_entity(self, entity_id: str) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO entity_state (entity_id, last_loaded_at) VALUES (?, ?) "
                "ON CONFLICT(entity_id) DO UPDATE SET last_loaded_at = excluded.last_loaded_at",
                (entity_id, _now()),
            )


def _row_to_session(row) -> SessionRow:
    return SessionRow(
        id=row["id"],
        mode=row["mode"],
        title=row["title"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        active_entities=json.loads(row["active_entities"] or "[]"),
        is_current=bool(row["is_current"]),
    )
