"""
AUCTORITAS SPECTRALIS — v1.0.0
registry/db.py — Chromatic Registry database interface

The Chromatic Registry is permanent. Nothing is ever deleted.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any

import AuctoritasSpectralis.config as cfg
from AuctoritasSpectralis.registry.schema import SCHEMA_SQL, SCHEMA_VERSION_SQL


def _db_path() -> Path:
    path = Path(cfg.get("registry_db_path", str(Path.home() / ".arca" / "chromatic_registry.db")))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def initialise() -> None:
    """Create tables if they don't exist."""
    with _connect() as conn:
        conn.executescript(SCHEMA_SQL)
        conn.executescript(SCHEMA_VERSION_SQL)


def insert_palette(record: dict[str, Any]) -> int:
    """
    Insert a ratified palette record.
    Returns the new row id.
    Raises sqlite3.IntegrityError if the seal already exists.
    """
    initialise()
    sql = """
    INSERT INTO chromatic_registry
        (designator, sealed_at, seal, tokens_json, nomina_json,
         wcag_min, apca_min, aa_pass, aaa_pass, notes)
    VALUES
        (:designator, :sealed_at, :seal, :tokens_json, :nomina_json,
         :wcag_min, :apca_min, :aa_pass, :aaa_pass, :notes)
    """
    row = {
        "designator":  record["designator"],
        "sealed_at":   record["sealed_at"],
        "seal":        record["seal"],
        "tokens_json": json.dumps(record["tokens"], ensure_ascii=False),
        "nomina_json": json.dumps(record.get("nomina", {}), ensure_ascii=False),
        "wcag_min":    record.get("wcag_min", 0.0),
        "apca_min":    record.get("apca_min", 0.0),
        "aa_pass":     int(record.get("aa_pass", False)),
        "aaa_pass":    int(record.get("aaa_pass", False)),
        "notes":       record.get("notes", ""),
    }
    with _connect() as conn:
        cur = conn.execute(sql, row)
        return cur.lastrowid


def fetch_all() -> list[dict]:
    """Return all records, newest first."""
    initialise()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM chromatic_registry ORDER BY sealed_at DESC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def fetch_by_id(record_id: int) -> dict | None:
    initialise()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM chromatic_registry WHERE id = ?", (record_id,)
        ).fetchone()
    return _row_to_dict(row) if row else None


def fetch_by_seal(seal: str) -> dict | None:
    initialise()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM chromatic_registry WHERE seal = ?", (seal,)
        ).fetchone()
    return _row_to_dict(row) if row else None


def count() -> int:
    initialise()
    with _connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM chromatic_registry").fetchone()[0]


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["tokens"] = json.loads(d.pop("tokens_json", "{}"))
    d["nomina"]  = json.loads(d.pop("nomina_json", "{}"))
    d["aa_pass"]  = bool(d["aa_pass"])
    d["aaa_pass"] = bool(d["aaa_pass"])
    return d
