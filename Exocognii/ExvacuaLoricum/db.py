#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                                db.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
SQLite database layer for Exvacua Loricum.
Single connection per request via get_db() context manager.
"""

import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from config import get as get_cfg

# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────────────────────────────────────

_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── Lorixii Speculativum — unratified accumulation layer ─────────────────────
CREATE TABLE IF NOT EXISTS lorixii_speculativum (
    id               TEXT PRIMARY KEY,
    source_type      TEXT NOT NULL CHECK(source_type IN ('app_log','file_drop','actio_extracticus')),
    source_ref       TEXT NOT NULL DEFAULT '',
    ingested_at      TEXT NOT NULL,
    raw_content      TEXT NOT NULL DEFAULT '',
    inferred_domain  TEXT NOT NULL DEFAULT '',
    inferred_tags    TEXT NOT NULL DEFAULT '[]',
    confidence       TEXT NOT NULL DEFAULT 'low' CHECK(confidence IN ('low','medium','high')),
    status           TEXT NOT NULL DEFAULT 'pending'
                          CHECK(status IN ('pending','in_judicium','consumed','rejected','ignored')),
    judicium_id      TEXT,
    related_lorixii  TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_lorix_status   ON lorixii_speculativum(status);
CREATE INDEX IF NOT EXISTS idx_lorix_domain   ON lorixii_speculativum(inferred_domain);
CREATE INDEX IF NOT EXISTS idx_lorix_ingested ON lorixii_speculativum(ingested_at);

-- ── Loridex Cards — structured canon index entries ───────────────────────────
CREATE TABLE IF NOT EXISTS loridex_cards (
    id               TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    domain           TEXT NOT NULL DEFAULT '',
    tags             TEXT NOT NULL DEFAULT '[]',
    status           TEXT NOT NULL DEFAULT 'ratified'
                          CHECK(status IN ('ratified','flagged_for_revision')),
    ratified_at      TEXT NOT NULL,
    source_lorixii   TEXT NOT NULL DEFAULT '[]',
    linked_cards     TEXT NOT NULL DEFAULT '[]',
    exloricum_id     TEXT,
    revision_history TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_card_domain ON loridex_cards(domain);
CREATE INDEX IF NOT EXISTS idx_card_status ON loridex_cards(status);

-- ── Exlorica — long-form prose canon documents ───────────────────────────────
CREATE TABLE IF NOT EXISTS exlorica (
    id               TEXT PRIMARY KEY,
    card_id          TEXT NOT NULL REFERENCES loridex_cards(id),
    title            TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    last_revised_at  TEXT NOT NULL,
    revision_count   INTEGER NOT NULL DEFAULT 0,
    file_path        TEXT NOT NULL DEFAULT '',
    wiz_path         TEXT NOT NULL DEFAULT '',
    aestheticum      TEXT NOT NULL DEFAULT 'default',
    word_count       INTEGER NOT NULL DEFAULT 0
);

-- ── Loricum Ratifex — master lore compendium (singleton) ─────────────────────
CREATE TABLE IF NOT EXISTS loricum_ratifex (
    id                   INTEGER PRIMARY KEY DEFAULT 1,
    last_crystalized_at  TEXT,
    last_wizard_edit_at  TEXT,
    version              INTEGER NOT NULL DEFAULT 0,
    file_path            TEXT NOT NULL DEFAULT '',
    wiz_path             TEXT NOT NULL DEFAULT '',
    aestheticum          TEXT NOT NULL DEFAULT 'default',
    CHECK(id = 1)
);

-- Seed the singleton row if absent
INSERT OR IGNORE INTO loricum_ratifex(id, version) VALUES (1, 0);

-- ── Arx Loricuum — taxonomy register ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS arx_loricuum (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    type          TEXT NOT NULL CHECK(type IN ('domain','tag')),
    parent_domain TEXT,
    status        TEXT NOT NULL DEFAULT 'seeded'
                       CHECK(status IN ('seeded','ratified','proposed','rejected')),
    proposed_by   TEXT NOT NULL DEFAULT 'system' CHECK(proposed_by IN ('system','wizard')),
    created_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_loricuum_type   ON arx_loricuum(type);
CREATE INDEX IF NOT EXISTS idx_loricuum_status ON arx_loricuum(status);

-- ── Judicium sessions — ratification ceremony ─────────────────────────────────
CREATE TABLE IF NOT EXISTS judicium_sessions (
    id            TEXT PRIMARY KEY,
    topic         TEXT NOT NULL,
    domain_hint   TEXT NOT NULL DEFAULT '',
    lorixii_ids   TEXT NOT NULL DEFAULT '[]',
    current_phase INTEGER NOT NULL DEFAULT 1,
    phase_data    TEXT NOT NULL DEFAULT '{}',
    status        TEXT NOT NULL DEFAULT 'open'
                       CHECK(status IN ('open','committed','abandoned')),
    opened_at     TEXT NOT NULL,
    committed_at  TEXT,
    card_id       TEXT,
    exloricum_id  TEXT
);

CREATE INDEX IF NOT EXISTS idx_judicium_status ON judicium_sessions(status);

-- ── Actio Interpretus log ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS interpretus_log (
    id           TEXT PRIMARY KEY,
    started_at   TEXT NOT NULL,
    completed_at TEXT,
    lorixii_processed INTEGER NOT NULL DEFAULT 0,
    lorixii_claimed   INTEGER NOT NULL DEFAULT 0,
    lorixii_ignored   INTEGER NOT NULL DEFAULT 0,
    error        TEXT
);
"""

# ─────────────────────────────────────────────────────────────────────────────
# SEEDED DOMAINS
# ─────────────────────────────────────────────────────────────────────────────

_SEEDED_DOMAINS = [
    "entities",
    "cosmology",
    "tower_mechanics",
    "history",
    "places",
    "artefacts",
    "rituals",
    "language",
    "factions",
    "wizard",
]


def _seed_domains(conn: sqlite3.Connection):
    """Insert seeded domains if not already present."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    import uuid
    for domain in _SEEDED_DOMAINS:
        conn.execute("""
            INSERT OR IGNORE INTO arx_loricuum(id, name, type, status, proposed_by, created_at)
            VALUES (?, ?, 'domain', 'seeded', 'system', ?)
        """, (str(uuid.uuid4()), domain, now))


# ─────────────────────────────────────────────────────────────────────────────
# CONNECTION
# ─────────────────────────────────────────────────────────────────────────────

def _db_path() -> str:
    return get_cfg()["exvacua_loricum_db"]


def init_db():
    """Create all tables and seed initial data. Safe to call multiple times."""
    Path(_db_path()).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_db_path())
    conn.executescript(_SCHEMA)
    _seed_domains(conn)
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    """
    Yields a sqlite3 connection with row_factory set to Row.
    Commits on clean exit, rolls back on exception.
    """
    conn = sqlite3.connect(_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dict, parsing JSON fields."""
    d = dict(row)
    _JSON_FIELDS = {
        "inferred_tags", "related_lorixii", "tags", "source_lorixii",
        "linked_cards", "revision_history", "lorixii_ids", "phase_data",
        "open_questions", "decisions", "arca_absoluta",
    }
    for field in _JSON_FIELDS:
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return d
