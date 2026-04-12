# Departamentum Documentalis · db.py · v1.1
"""Thread-safe SQLite WAL wrapper. All queries live here."""
import sqlite3
import threading
from pathlib import Path
from DepartamentumDocumentalis.config import CFG

_local = threading.local()

def get_conn() -> sqlite3.Connection:
    if not hasattr(_local, "conn"):
        db_path = Path(CFG["db_path"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
    return _local.conn

def init_schema():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS formae (
            forma_id         TEXT PRIMARY KEY,
            name             TEXT NOT NULL,
            doc_type         TEXT NOT NULL,
            description      TEXT,
            output_targets   TEXT NOT NULL DEFAULT '["md"]',
            chromaticum_name TEXT,
            status           TEXT NOT NULL DEFAULT 'DRAFT',
            version          INTEGER NOT NULL DEFAULT 1,
            created_at       TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS forma_fields (
            field_id    TEXT PRIMARY KEY,
            forma_id    TEXT NOT NULL REFERENCES formae(forma_id),
            name        TEXT NOT NULL,
            label       TEXT NOT NULL,
            field_type  TEXT NOT NULL DEFAULT 'PERMISSIVE',
            required    INTEGER NOT NULL DEFAULT 0,
            fixed_value TEXT,
            position    INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS documents (
            doc_id      TEXT PRIMARY KEY,
            forma_id    TEXT NOT NULL REFERENCES formae(forma_id),
            title       TEXT NOT NULL,
            source_text TEXT NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS archive (
            archive_id       TEXT PRIMARY KEY,
            doc_id           TEXT NOT NULL,
            forma_id         TEXT NOT NULL,
            forma_version    INTEGER NOT NULL,
            status           TEXT NOT NULL DEFAULT 'CURRENT',
            bureau_marker    TEXT NOT NULL DEFAULT 'III-DD',
            chromaticum_name TEXT,
            theme_snapshot   TEXT,
            output_paths     TEXT,
            orphaned_corpus  TEXT,
            emitted_at       TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS mandate_bench (
            doc_type TEXT PRIMARY KEY,
            forma_id TEXT NOT NULL REFERENCES formae(forma_id),
            set_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS mandate_history (
            history_id TEXT PRIMARY KEY,
            doc_type   TEXT NOT NULL,
            forma_id   TEXT NOT NULL,
            set_at     TEXT NOT NULL DEFAULT (datetime('now')),
            set_by     TEXT NOT NULL DEFAULT 'WIZARD'
        );
        CREATE TABLE IF NOT EXISTS propagatio_queue (
            queue_id        TEXT PRIMARY KEY,
            archive_id      TEXT NOT NULL REFERENCES archive(archive_id),
            target_forma_id TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'PENDING',
            error_msg       TEXT,
            queued_at       TEXT NOT NULL DEFAULT (datetime('now')),
            processed_at    TEXT
        );
        CREATE TABLE IF NOT EXISTS emission_log (
            log_id     TEXT PRIMARY KEY,
            archive_id TEXT NOT NULL,
            event      TEXT NOT NULL,
            detail     TEXT,
            logged_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()

def fetch_all(sql, params=()):
    return get_conn().execute(sql, params).fetchall()

def fetch_one(sql, params=()):
    return get_conn().execute(sql, params).fetchone()

def execute(sql, params=()):
    conn = get_conn()
    cur = conn.execute(sql, params)
    conn.commit()
    return cur

def get_all_formae():
    return fetch_all("SELECT * FROM formae ORDER BY updated_at DESC")

def get_forma(forma_id):
    return fetch_one("SELECT * FROM formae WHERE forma_id = ?", (forma_id,))

def get_forma_fields(forma_id):
    return fetch_all(
        "SELECT * FROM forma_fields WHERE forma_id = ? ORDER BY position", (forma_id,))

def get_mandated_forma(doc_type):
    return fetch_one(
        "SELECT f.* FROM mandate_bench mb JOIN formae f ON f.forma_id = mb.forma_id "
        "WHERE mb.doc_type = ?", (doc_type,))

def get_archive(limit=100):
    return fetch_all("SELECT * FROM archive ORDER BY emitted_at DESC LIMIT ?", (limit,))

def get_propagatio_queue(status="PENDING"):
    return fetch_all(
        "SELECT * FROM propagatio_queue WHERE status = ? ORDER BY queued_at", (status,))

def get_mandate_bench():
    return fetch_all(
        "SELECT mb.*, f.name AS forma_name FROM mandate_bench mb "
        "JOIN formae f ON f.forma_id = mb.forma_id ORDER BY mb.doc_type")

def get_mandate_history(doc_type):
    return fetch_all(
        "SELECT * FROM mandate_history WHERE doc_type = ? ORDER BY set_at DESC", (doc_type,))
