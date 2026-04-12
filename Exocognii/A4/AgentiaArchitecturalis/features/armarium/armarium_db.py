"""
Armarium Database — SQLite component library.

Schema includes schema_version from day one (constraint #8).
Seal/Load/Fork/Export operations with thumbnail capture and parent_id lineage.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "storage" / "armarium.db"


@dataclass
class ComponentRecord:
    id: int
    name: str
    category: str
    version: int
    theme_designator: str
    design_json: str
    thumbnail_png: Optional[bytes]
    parent_id: Optional[int]
    created_at: str
    source_app: str
    source_version: str
    involucrum_id: Optional[str]


class ArmariumDB:
    """SQLite-backed component library."""

    def __init__(self) -> None:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(_DB_PATH))
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS schema_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            INSERT OR IGNORE INTO schema_meta (key, value) VALUES ('schema_version', '1.0');

            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'uncategorized',
                version INTEGER NOT NULL DEFAULT 1,
                theme_designator TEXT NOT NULL DEFAULT 'Nox Aurum',
                design_json TEXT NOT NULL,
                thumbnail_png BLOB,
                parent_id INTEGER,
                created_at TEXT NOT NULL,
                source_app TEXT NOT NULL DEFAULT 'AgentiaArchitecturalis',
                source_version TEXT NOT NULL DEFAULT '1.0',
                involucrum_id TEXT,
                archived INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (parent_id) REFERENCES components(id)
            );

            CREATE TABLE IF NOT EXISTS category_registry (
                name TEXT PRIMARY KEY
            );
            INSERT OR IGNORE INTO category_registry (name) VALUES ('panel');
            INSERT OR IGNORE INTO category_registry (name) VALUES ('dialog');
            INSERT OR IGNORE INTO category_registry (name) VALUES ('toolbar');
            INSERT OR IGNORE INTO category_registry (name) VALUES ('card');

            CREATE TABLE IF NOT EXISTS export_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_id INTEGER NOT NULL,
                exported_at TEXT NOT NULL,
                export_type TEXT NOT NULL DEFAULT 'clipboard',
                FOREIGN KEY (component_id) REFERENCES components(id)
            );
        """)
        self._conn.commit()

    def seal(
        self,
        name: str,
        category: str,
        design_json: str,
        theme_designator: str = "Nox Aurum",
        thumbnail_png: Optional[bytes] = None,
    ) -> int:
        """Seal a new component. Returns the component id."""
        cursor = self._conn.execute(
            """INSERT INTO components (name, category, version, theme_designator,
               design_json, thumbnail_png, created_at)
               VALUES (?, ?, 1, ?, ?, ?, ?)""",
            (name, category, theme_designator, design_json, thumbnail_png,
             datetime.utcnow().isoformat()),
        )
        self._conn.commit()
        # Ensure category exists
        self._conn.execute(
            "INSERT OR IGNORE INTO category_registry (name) VALUES (?)", (category,)
        )
        self._conn.commit()
        return cursor.lastrowid

    def load(self, component_id: int) -> Optional[ComponentRecord]:
        """Load a component by ID."""
        row = self._conn.execute(
            "SELECT * FROM components WHERE id = ? AND archived = 0", (component_id,)
        ).fetchone()
        if not row:
            return None
        return self._row_to_record(row)

    def fork(self, component_id: int) -> Optional[int]:
        """Fork a component. Returns new ID with parent_id = original."""
        original = self.load(component_id)
        if not original:
            return None
        cursor = self._conn.execute(
            """INSERT INTO components (name, category, version, theme_designator,
               design_json, thumbnail_png, parent_id, created_at, source_app, source_version)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (original.name, original.category, original.version + 1,
             original.theme_designator, original.design_json, original.thumbnail_png,
             original.id, datetime.utcnow().isoformat(),
             original.source_app, original.source_version),
        )
        self._conn.commit()
        return cursor.lastrowid

    def list_all(
        self,
        category: str = "",
        theme: str = "",
        search: str = "",
    ) -> list[ComponentRecord]:
        """List components with optional filters."""
        query = "SELECT * FROM components WHERE archived = 0"
        params: list = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if theme:
            query += " AND theme_designator = ?"
            params.append(theme)
        if search:
            query += " AND name LIKE ?"
            params.append(f"%{search}%")
        query += " ORDER BY created_at DESC"
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_record(r) for r in rows]

    def categories(self) -> list[str]:
        """List all registered categories."""
        rows = self._conn.execute("SELECT name FROM category_registry ORDER BY name").fetchall()
        return [r["name"] for r in rows]

    def log_export(self, component_id: int, export_type: str = "clipboard") -> None:
        self._conn.execute(
            "INSERT INTO export_log (component_id, exported_at, export_type) VALUES (?, ?, ?)",
            (component_id, datetime.utcnow().isoformat(), export_type),
        )
        self._conn.commit()

    def archive(self, component_id: int) -> None:
        self._conn.execute("UPDATE components SET archived = 1 WHERE id = ?", (component_id,))
        self._conn.commit()

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) FROM components WHERE archived = 0").fetchone()
        return row[0] if row else 0

    def _row_to_record(self, row: sqlite3.Row) -> ComponentRecord:
        return ComponentRecord(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            version=row["version"],
            theme_designator=row["theme_designator"],
            design_json=row["design_json"],
            thumbnail_png=row["thumbnail_png"],
            parent_id=row["parent_id"],
            created_at=row["created_at"],
            source_app=row["source_app"],
            source_version=row["source_version"],
            involucrum_id=row["involucrum_id"],
        )

    def close(self) -> None:
        self._conn.close()
