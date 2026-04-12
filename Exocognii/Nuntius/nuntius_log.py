# NUNTIUS — nuntius_log.py
# v1.0
"""SQLite WAL-mode emission log. Ring buffer. Atomic writes. Per-consumer outcome rows."""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS emissions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp     TEXT    NOT NULL,
    source_app    TEXT    NOT NULL,
    payload       TEXT    NOT NULL,
    consumer_name TEXT    NOT NULL,
    consumer_url  TEXT    NOT NULL,
    outcome       TEXT    NOT NULL,
    status_code   INTEGER,
    error_detail  TEXT
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_emissions_consumer
    ON emissions (consumer_name, id DESC);
"""


@dataclass
class EmissionRecord:
    """One per-consumer row in the emission log."""
    timestamp: str
    source_app: str
    payload: str              # full Involucrum JSON verbatim
    consumer_name: str
    consumer_url: str
    outcome: str              # 'success' | 'timeout' | 'error'
    status_code: Optional[int]
    error_detail: Optional[str]


class EmissionLog:
    """SQLite WAL-mode ring buffer for emission records."""

    def __init__(self, db_path: Path, max_rows: int) -> None:
        """Open or create the emissions DB. Enable WAL. Create table and index."""
        self._db_path = db_path
        self._max_rows = max_rows
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            str(self._db_path),
            check_same_thread=False,
            isolation_level=None,   # autocommit — we manage transactions manually
        )
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(CREATE_TABLE_SQL)
            conn.execute(CREATE_INDEX_SQL)

    def record(self, entries: List[EmissionRecord]) -> None:
        """Write one or more emission records atomically. Purge if over max_rows."""
        if not entries:
            return
        try:
            with self._connect() as conn:
                conn.execute("BEGIN")
                conn.executemany(
                    """
                    INSERT INTO emissions
                        (timestamp, source_app, payload, consumer_name,
                         consumer_url, outcome, status_code, error_detail)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            e.timestamp,
                            e.source_app,
                            e.payload,
                            e.consumer_name,
                            e.consumer_url,
                            e.outcome,
                            e.status_code,
                            e.error_detail,
                        )
                        for e in entries
                    ],
                )
                # Ring buffer purge
                row = conn.execute("SELECT COUNT(*) FROM emissions").fetchone()
                count = row[0]
                if count > self._max_rows:
                    excess = count - self._max_rows
                    conn.execute(
                        """
                        DELETE FROM emissions WHERE id IN (
                            SELECT id FROM emissions ORDER BY id ASC LIMIT ?
                        )
                        """,
                        (excess,),
                    )
                conn.execute("COMMIT")
        except sqlite3.Error as exc:
            logger.error("EmissionLog write failure: %s", exc)
            # Do not re-raise — log failure must never gate fan-out

    def recent(self, page: int = 1, limit: int = 50) -> tuple[List[dict], int]:
        """Return paginated records ordered by id DESC. Payload excluded. Returns (rows, total)."""
        offset = (page - 1) * limit
        try:
            with self._connect() as conn:
                total = conn.execute("SELECT COUNT(*) FROM emissions").fetchone()[0]
                rows = conn.execute(
                    """
                    SELECT id, timestamp, source_app, consumer_name, consumer_url,
                           outcome, status_code, error_detail
                    FROM emissions
                    ORDER BY id DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                ).fetchall()
            return [dict(r) for r in rows], total
        except sqlite3.Error as exc:
            logger.error("EmissionLog read failure: %s", exc)
            return [], 0

    def last_per_consumer(self) -> List[dict]:
        """Return most recent outcome per consumer_name for /status."""
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT consumer_name, consumer_url,
                           MAX(timestamp) AS last_seen, outcome AS last_outcome
                    FROM emissions
                    GROUP BY consumer_name
                    """
                ).fetchall()
            return [dict(r) for r in rows]
        except sqlite3.Error as exc:
            logger.error("EmissionLog last_per_consumer failure: %s", exc)
            return []
