# Auctoritas Spectralis — registry.py
# v1.0.0
"""SQLite operations for the Chromatic Registry."""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS chromatic_registry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    designator      TEXT    NOT NULL,
    seal_hash       TEXT    NOT NULL UNIQUE,
    created_at      TEXT    NOT NULL,
    c_bg            TEXT    NOT NULL,
    c_panel         TEXT    NOT NULL,
    c_gold          TEXT    NOT NULL,
    c_gold_dim      TEXT    NOT NULL,
    c_gold_dark     TEXT    NOT NULL,
    c_crimson       TEXT    NOT NULL,
    c_teal          TEXT    NOT NULL,
    c_text          TEXT    NOT NULL,
    c_subtle        TEXT    NOT NULL,
    c_white         TEXT    NOT NULL,
    oklab_bg_l      REAL    NOT NULL,
    oklab_bg_a      REAL    NOT NULL,
    oklab_bg_b      REAL    NOT NULL,
    oklab_fg_l      REAL    NOT NULL,
    oklab_fg_a      REAL    NOT NULL,
    oklab_fg_b      REAL    NOT NULL,
    wcag_min_ratio  REAL    NOT NULL,
    apca_min_lc     REAL    NOT NULL,
    passes_aa       INTEGER NOT NULL DEFAULT 0,
    passes_aaa      INTEGER NOT NULL DEFAULT 0,
    notes           TEXT    DEFAULT ''
);

CREATE TABLE IF NOT EXISTS seal_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    registry_id     INTEGER NOT NULL REFERENCES chromatic_registry(id),
    seal_hash       TEXT    NOT NULL,
    sealed_at       TEXT    NOT NULL,
    canonical_json  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS export_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    registry_id     INTEGER NOT NULL REFERENCES chromatic_registry(id),
    format          TEXT    NOT NULL,
    export_path     TEXT    NOT NULL,
    exported_at     TEXT    NOT NULL,
    success         INTEGER NOT NULL DEFAULT 1
);
"""


class ChromaticRegistry:
    """Manages the SQLite chromatic registry database."""

    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._conn = None
        self._enabled = True

    def connect(self) -> bool:
        """Open DB connection, create schema if needed.

        Returns True if successful, False if registry is disabled.
        """
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.executescript(_SCHEMA_SQL)
            self._conn.commit()
            return True
        except (sqlite3.Error, OSError) as e:
            self._enabled = False
            self._conn = None
            return False

    @property
    def enabled(self) -> bool:
        return self._enabled and self._conn is not None

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def insert_palette(self, designator: str, seal_hash: str,
                       tokens: dict, oklab_bg: dict, oklab_fg: dict,
                       wcag_min: float, apca_min: float,
                       passes_aa: bool, passes_aaa: bool,
                       canonical_json: str, sealed_at: str,
                       notes: str = '') -> int:
        """Insert a ratified palette into the registry. Returns the row id."""
        if not self.enabled:
            raise RuntimeError("Registry is disabled")

        cur = self._conn.execute(
            """INSERT INTO chromatic_registry
               (designator, seal_hash, created_at,
                c_bg, c_panel, c_gold, c_gold_dim, c_gold_dark,
                c_crimson, c_teal, c_text, c_subtle, c_white,
                oklab_bg_l, oklab_bg_a, oklab_bg_b,
                oklab_fg_l, oklab_fg_a, oklab_fg_b,
                wcag_min_ratio, apca_min_lc, passes_aa, passes_aaa, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                       ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (designator, seal_hash, sealed_at,
             tokens['c_bg'], tokens['c_panel'], tokens['c_gold'],
             tokens['c_gold_dim'], tokens['c_gold_dark'],
             tokens['c_crimson'], tokens['c_teal'], tokens['c_text'],
             tokens['c_subtle'], tokens['c_white'],
             oklab_bg['l'], oklab_bg['a'], oklab_bg['b'],
             oklab_fg['l'], oklab_fg['a'], oklab_fg['b'],
             wcag_min, apca_min,
             1 if passes_aa else 0, 1 if passes_aaa else 0, notes)
        )

        registry_id = cur.lastrowid

        # Also write to seal_log
        self._conn.execute(
            """INSERT INTO seal_log (registry_id, seal_hash, sealed_at, canonical_json)
               VALUES (?, ?, ?, ?)""",
            (registry_id, seal_hash, sealed_at, canonical_json)
        )

        self._conn.commit()
        return registry_id

    def list_palettes(self) -> list[dict]:
        """Return all registry entries, most recent first."""
        if not self.enabled:
            return []
        cur = self._conn.execute(
            "SELECT * FROM chromatic_registry ORDER BY id DESC"
        )
        return [dict(row) for row in cur.fetchall()]

    def get_palette(self, registry_id: int) -> dict | None:
        """Fetch a single palette by id."""
        if not self.enabled:
            return None
        cur = self._conn.execute(
            "SELECT * FROM chromatic_registry WHERE id = ?", (registry_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def get_tokens_from_row(self, row: dict) -> dict:
        """Extract token dict from a registry row."""
        return {
            'c_bg': row['c_bg'], 'c_panel': row['c_panel'],
            'c_gold': row['c_gold'], 'c_gold_dim': row['c_gold_dim'],
            'c_gold_dark': row['c_gold_dark'], 'c_crimson': row['c_crimson'],
            'c_teal': row['c_teal'], 'c_text': row['c_text'],
            'c_subtle': row['c_subtle'], 'c_white': row['c_white'],
        }

    def log_export(self, registry_id: int, fmt: str, path: str,
                   success: bool = True):
        """Log an export event."""
        if not self.enabled:
            return
        self._conn.execute(
            """INSERT INTO export_log (registry_id, format, export_path, exported_at, success)
               VALUES (?, ?, ?, ?, ?)""",
            (registry_id, fmt, path,
             datetime.now(timezone.utc).isoformat(),
             1 if success else 0)
        )
        self._conn.commit()
