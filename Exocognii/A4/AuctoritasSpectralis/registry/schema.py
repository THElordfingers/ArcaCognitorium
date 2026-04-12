"""
AUCTORITAS SPECTRALIS — v1.0.0
registry/schema.py — Chromatic Registry SQLite schema

The Chromatic Registry is the permanent archive of all ratified palettes.
Nothing is ever deleted. Nothing is ever edited.
"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS chromatic_registry (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    designator    TEXT    NOT NULL,
    sealed_at     TEXT    NOT NULL,
    seal          TEXT    NOT NULL UNIQUE,
    tokens_json   TEXT    NOT NULL,
    nomina_json   TEXT    NOT NULL DEFAULT '{}',
    wcag_min      REAL    NOT NULL DEFAULT 0.0,
    apca_min      REAL    NOT NULL DEFAULT 0.0,
    aa_pass       INTEGER NOT NULL DEFAULT 0,
    aaa_pass      INTEGER NOT NULL DEFAULT 0,
    notes         TEXT    NOT NULL DEFAULT '',
    UNIQUE(seal)
);

CREATE INDEX IF NOT EXISTS idx_registry_sealed_at
    ON chromatic_registry(sealed_at DESC);

CREATE INDEX IF NOT EXISTS idx_registry_designator
    ON chromatic_registry(designator);
"""

SCHEMA_VERSION = 1
SCHEMA_VERSION_SQL = """
CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT OR IGNORE INTO schema_meta (key, value) VALUES ('schema_version', '1');
"""
