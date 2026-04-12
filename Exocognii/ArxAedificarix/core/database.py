#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                              core/database.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging
import sqlite3
import time
from pathlib import Path

logger = logging.getLogger("arx.database")

DB_PATH = Path("~/ArcaCognitorium/Exocognii/ArxAedificarix/arx.db").expanduser()

_SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS projects (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    shared_instructions TEXT NOT NULL DEFAULT '',
    created_at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id              TEXT PRIMARY KEY,
    project_id      TEXT REFERENCES projects(id) ON DELETE SET NULL,
    title           TEXT NOT NULL,
    builder_prompt  TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL,
    last_active_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id                   TEXT PRIMARY KEY,
    conversation_id      TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role                 TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content              TEXT NOT NULL,
    compressed           INTEGER NOT NULL DEFAULT 0,
    compression_group_id TEXT,
    token_count          INTEGER NOT NULL DEFAULT 0,
    created_at           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS compression_archive (
    id                   TEXT PRIMARY KEY,
    compression_group_id TEXT NOT NULL,
    original_messages    TEXT NOT NULL,
    summary              TEXT NOT NULL,
    compressed_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attachments (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id) ON DELETE CASCADE,
    project_id      TEXT REFERENCES projects(id) ON DELETE CASCADE,
    scope           TEXT NOT NULL CHECK(scope IN ('conversation', 'project')),
    filename        TEXT NOT NULL,
    full_content    TEXT NOT NULL,
    summary_cache   TEXT,
    attached_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS output_files (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    filename        TEXT NOT NULL,
    language        TEXT NOT NULL DEFAULT 'plain',
    content         TEXT NOT NULL,
    description     TEXT NOT NULL DEFAULT '',
    export_status   TEXT NOT NULL DEFAULT 'pending'
                    CHECK(export_status IN ('pending', 'exported')),
    created_at      TEXT NOT NULL
);
"""


class DatabaseManager:
    """
    Owns the single SQLite connection for the lifetime of the process.
    Singleton by class variable. Call initialise() once at startup.
    All subsequent access via connection().
    """

    _conn: sqlite3.Connection | None = None

    @classmethod
    def initialise(cls, db_path: Path = DB_PATH) -> None:
        """
        Create database and all tables if not exist; enable WAL mode.
        Raises RuntimeError on critical failure — caller should exit.
        """
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            cls._conn = sqlite3.connect(
                str(db_path),
                check_same_thread=False,
            )
            cls._conn.row_factory = sqlite3.Row
            cls._run_schema()
            cls._conn.commit()
            logger.info("DatabaseManager initialised at %s", db_path)
        except Exception as exc:
            logger.critical("DatabaseManager.initialise failed: %s", exc)
            raise RuntimeError(f"Database initialisation failed: {exc}") from exc

    @classmethod
    def _run_schema(cls) -> None:
        """Execute full schema DDL. Idempotent — uses CREATE IF NOT EXISTS."""
        assert cls._conn is not None
        # Execute statement by statement to allow WAL pragma to land first.
        for statement in _SCHEMA.strip().split(";"):
            stmt = statement.strip()
            if stmt:
                cls._conn.execute(stmt)

    @classmethod
    def connection(cls) -> sqlite3.Connection:
        """
        Return the active connection.
        Raises RuntimeError if initialise() has not been called.
        """
        if cls._conn is None:
            raise RuntimeError(
                "DatabaseManager has not been initialised. "
                "Call DatabaseManager.initialise() at application startup."
            )
        return cls._conn

    @classmethod
    def execute_with_retry(
        cls,
        sql: str,
        params: tuple = (),
        retries: int = 1,
        delay: float = 0.2,
    ) -> sqlite3.Cursor:
        """
        Execute with one retry on OperationalError (e.g. brief lock).
        Used by SessionStore for write operations.
        """
        conn = cls.connection()
        for attempt in range(retries + 1):
            try:
                return conn.execute(sql, params)
            except sqlite3.OperationalError as exc:
                if attempt < retries:
                    logger.warning(
                        "SQLite OperationalError (attempt %d): %s — retrying in %.1fs",
                        attempt + 1, exc, delay,
                    )
                    time.sleep(delay)
                else:
                    raise

    @classmethod
    def close(cls) -> None:
        """Close connection gracefully. Called on application exit."""
        if cls._conn is not None:
            cls._conn.close()
            cls._conn = None
            logger.info("DatabaseManager connection closed.")
