# Agentia Architecturalis — library.py
# v1.0.0
"""SQLite CRUD for the Component Library."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS components (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    category        TEXT    NOT NULL,
    description     TEXT    DEFAULT '',
    design_json     TEXT    NOT NULL,
    thumbnail_png   BLOB    DEFAULT NULL,
    version         INTEGER NOT NULL DEFAULT 1,
    parent_id       INTEGER DEFAULT NULL REFERENCES components(id),
    theme_designator TEXT   DEFAULT NULL,
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL,
    tags            TEXT    DEFAULT '',
    is_archived     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS category_registry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    description     TEXT    DEFAULT '',
    sort_order      INTEGER NOT NULL DEFAULT 0
);

INSERT OR IGNORE INTO category_registry (name, description, sort_order) VALUES
    ('panel',     'Full panel compositions',        1),
    ('dialog',    'Modal and popup dialog layouts',  2),
    ('toolbar',   'TopBar, StatusBar assemblies',     3),
    ('card',      'Self-contained data display cards',4),
    ('composite', 'Reusable multi-element blocks',    5),
    ('fragment',  'Individual element configs',       6);

CREATE TABLE IF NOT EXISTS export_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id    INTEGER NOT NULL REFERENCES components(id),
    format          TEXT    NOT NULL,
    export_path     TEXT    DEFAULT NULL,
    exported_at     TEXT    NOT NULL
);
"""


class ComponentLibrary:
    """Manages saved component designs in SQLite."""

    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None
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
            self._conn = None
            return False

    @property
    def enabled(self) -> bool:
        return self._enabled and self._conn is not None

    def save(self, name: str, category: str, design_json: str,
             description: str = '', tags: str = '',
             thumbnail: bytes = None, theme_designator: str = None,
             component_id: int = None) -> int:
        """Save or update a component. Returns component id."""
        if not self.enabled:
            raise RuntimeError("Library is disabled")
        now = datetime.now(timezone.utc).isoformat()

        if component_id is not None:
            # Update existing — increment version
            row = self.load(component_id)
            if row:
                new_version = row.get('version', 0) + 1
                self._conn.execute(
                    """UPDATE components SET name=?, category=?, design_json=?,
                       description=?, tags=?, thumbnail_png=?, theme_designator=?,
                       version=?, updated_at=? WHERE id=?""",
                    (name, category, design_json, description, tags,
                     thumbnail, theme_designator, new_version, now, component_id)
                )
                self._conn.commit()
                return component_id

        cur = self._conn.execute(
            """INSERT INTO components
               (name, category, design_json, description, tags,
                thumbnail_png, theme_designator, version, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
            (name, category, design_json, description, tags,
             thumbnail, theme_designator, now, now)
        )
        self._conn.commit()
        return cur.lastrowid

    def fork(self, source_id: int, new_name: str) -> int:
        """Create a new component forked from source."""
        if not self.enabled:
            raise RuntimeError("Library is disabled")
        source = self.load(source_id)
        if source is None:
            raise ValueError(f"Source component {source_id} not found")
        now = datetime.now(timezone.utc).isoformat()
        cur = self._conn.execute(
            """INSERT INTO components
               (name, category, design_json, description, tags,
                thumbnail_png, theme_designator, version, parent_id,
                created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)""",
            (new_name, source['category'], source['design_json'],
             source['description'], source['tags'], source['thumbnail_png'],
             source['theme_designator'], source_id, now, now)
        )
        self._conn.commit()
        return cur.lastrowid

    def load(self, component_id: int) -> dict | None:
        if not self.enabled:
            return None
        cur = self._conn.execute(
            "SELECT * FROM components WHERE id = ?", (component_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def list_components(self, category: str = None,
                        archived: bool = False) -> list[dict]:
        if not self.enabled:
            return []
        query = "SELECT * FROM components WHERE is_archived = ?"
        params: list = [1 if archived else 0]
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY updated_at DESC"
        cur = self._conn.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def search(self, query: str) -> list[dict]:
        if not self.enabled:
            return []
        pattern = f'%{query}%'
        cur = self._conn.execute(
            """SELECT * FROM components WHERE is_archived = 0
               AND (name LIKE ? OR description LIKE ? OR tags LIKE ?)
               ORDER BY updated_at DESC""",
            (pattern, pattern, pattern)
        )
        return [dict(row) for row in cur.fetchall()]

    def archive(self, component_id: int):
        if not self.enabled:
            return
        self._conn.execute(
            "UPDATE components SET is_archived = 1 WHERE id = ?",
            (component_id,)
        )
        self._conn.commit()

    def log_export(self, component_id: int, fmt: str, path: str = None):
        if not self.enabled:
            return
        self._conn.execute(
            """INSERT INTO export_log (component_id, format, export_path, exported_at)
               VALUES (?, ?, ?, ?)""",
            (component_id, fmt, path, datetime.now(timezone.utc).isoformat())
        )
        self._conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
