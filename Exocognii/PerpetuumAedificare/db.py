#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                                db.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from config import get as get_cfg

_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── Acquiuum Chronex — capture surface ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS acquiuum_chronex (
    id               TEXT PRIMARY KEY,
    source_type      TEXT NOT NULL
                          CHECK(source_type IN
                          ('indicatum_machina','nota_brevis',
                           'oratio_extracticum','file_drop')),
    source_ref       TEXT NOT NULL DEFAULT '',
    raw_content      TEXT NOT NULL DEFAULT '',
    captured_at      TEXT NOT NULL,
    inferred_node_id TEXT,
    node_confidence  TEXT NOT NULL DEFAULT 'inferred'
                          CHECK(node_confidence IN ('inferred','wizard_set')),
    status           TEXT NOT NULL DEFAULT 'pending'
                          CHECK(status IN ('pending','aggregated','dismissed'))
);

CREATE INDEX IF NOT EXISTS idx_acq_status   ON acquiuum_chronex(status);
CREATE INDEX IF NOT EXISTS idx_acq_captured ON acquiuum_chronex(captured_at);
CREATE INDEX IF NOT EXISTS idx_acq_node     ON acquiuum_chronex(inferred_node_id);

-- ── Nodus Momentuum — atomic work unit ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS nodus_momentuum (
    id                  TEXT PRIMARY KEY,
    title               TEXT NOT NULL,
    nodicum             TEXT NOT NULL DEFAULT 'concept',
    nodicum_confidence  TEXT NOT NULL DEFAULT 'inferred'
                             CHECK(nodicum_confidence IN ('inferred','wizard_set')),
    nodifex             TEXT NOT NULL DEFAULT '',
    created_at          TEXT NOT NULL,
    last_touched_at     TEXT NOT NULL,
    open_questions      TEXT NOT NULL DEFAULT '[]',
    decisions           TEXT NOT NULL DEFAULT '[]',
    arca_absoluta       TEXT NOT NULL DEFAULT '[]',
    driftuum_metrica    REAL NOT NULL DEFAULT 0.0,
    driftuum_attentio   INTEGER NOT NULL DEFAULT 0,
    status              TEXT NOT NULL DEFAULT 'active'
                             CHECK(status IN ('active','dormant','resolved','abandoned'))
);

CREATE INDEX IF NOT EXISTS idx_nodus_status  ON nodus_momentuum(status);
CREATE INDEX IF NOT EXISTS idx_nodus_touched ON nodus_momentuum(last_touched_at);
CREATE INDEX IF NOT EXISTS idx_nodus_nodicum ON nodus_momentuum(nodicum);

-- ── Exnodica — relationship graph ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS exnodica (
    id                       TEXT PRIMARY KEY,
    from_node                TEXT NOT NULL REFERENCES nodus_momentuum(id),
    to_node                  TEXT NOT NULL REFERENCES nodus_momentuum(id),
    relationship             TEXT NOT NULL DEFAULT 'informs',
    relationship_confidence  TEXT NOT NULL DEFAULT 'inferred'
                                  CHECK(relationship_confidence IN ('inferred','wizard_set')),
    created_at               TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_exnodica_from ON exnodica(from_node);
CREATE INDEX IF NOT EXISTS idx_exnodica_to   ON exnodica(to_node);

-- ── Nodicum register — seeded and emergent types ──────────────────────────────
CREATE TABLE IF NOT EXISTS nodicum_register (
    name        TEXT PRIMARY KEY,
    description TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL DEFAULT 'seeded'
                     CHECK(status IN ('seeded','proposed','ratified','rejected')),
    created_at  TEXT NOT NULL
);

-- ── Aggrexuum log ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS aggrexuum_log (
    id               TEXT PRIMARY KEY,
    started_at       TEXT NOT NULL,
    completed_at     TEXT,
    captures_processed INTEGER NOT NULL DEFAULT 0,
    nodes_created    INTEGER NOT NULL DEFAULT 0,
    nodes_updated    INTEGER NOT NULL DEFAULT 0,
    error            TEXT
);

-- ── Driftuum log ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS driftuum_log (
    id              TEXT PRIMARY KEY,
    node_id         TEXT NOT NULL REFERENCES nodus_momentuum(id),
    driftuum_metrica REAL NOT NULL,
    flagged_at      TEXT NOT NULL,
    resolved_at     TEXT,
    trigger_nodes   TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_drift_node     ON driftuum_log(node_id);
CREATE INDEX IF NOT EXISTS idx_drift_resolved ON driftuum_log(resolved_at);
"""

_SEEDED_NODICA = [
    ("system",    "A full application or major architectural system"),
    ("feature",   "A discrete capability within a system"),
    ("concept",   "An idea, principle, or design pattern"),
    ("question",  "An open question requiring resolution"),
    ("decision",  "A resolved choice — closed, but preserved"),
    ("artefact",  "A produced output — doc, file, schema, component"),
    ("session",   "A working context — intent-bounded, not time-bounded"),
]


def _seed_nodica(conn: sqlite3.Connection):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    for name, desc in _SEEDED_NODICA:
        conn.execute("""
            INSERT OR IGNORE INTO nodicum_register(name, description, status, created_at)
            VALUES (?, ?, 'seeded', ?)
        """, (name, desc, now))


def _db_path() -> str:
    return get_cfg()["perpetuum_aedificare_db"]


def init_db():
    Path(_db_path()).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_db_path())
    conn.executescript(_SCHEMA)
    _seed_nodica(conn)
    conn.commit()
    conn.close()


@contextmanager
def get_db():
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


_JSON_FIELDS = {
    "open_questions", "decisions", "arca_absoluta",
    "trigger_nodes",
}


def row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for field in _JSON_FIELDS:
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    # Boolean coercion for SQLite integers
    if "driftuum_attentio" in d:
        d["driftuum_attentio"] = bool(d["driftuum_attentio"])
    return d
