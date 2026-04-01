#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗██╗███╗   ██╗ ██████╗   ▍
🮈  ██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██║████╗  ██║██╔════╝   ▍
🮈  ██║     █████╗  ███████║██████╔╝██╔██╗ ██║██║██╔██╗ ██║██║  ███╗  ▍
🮈  ██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██║██║╚██╗██║██║   ██║  ▍
🮈  ███████╗███████╗██║  ██║██║  ██║██║ ╚████║██║██║ ╚████║╚██████╔╝  ▍
🮈  ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝   ▍
🮈                   E N G I N E  —  L E A R N I N G                  ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                     ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                    learning_engine.py   ⯩
# ⯨                                                                     ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
#
# EntitexRefined — Learning Engine
# Tracks archetype/axis/role combo weights and Analytica weakness frequency.
# Quality signal: score = max(0, 10 - len(flags)) — simple proxy.
# Written after package staging only. Non-fatal on all failures.
# ─────────────────────────────────────────────────────────────────────────────

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

DB_PATH = Path.home() / '.arca' / 'entitex_refined.db'

_SCHEMA = """
CREATE TABLE IF NOT EXISTS combo_scores (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    item        TEXT NOT NULL UNIQUE,
    total_score REAL DEFAULT 0.0,
    count       INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS weakness_freq (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    tag       TEXT NOT NULL UNIQUE,
    frequency INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS generation_log (
    id              TEXT PRIMARY KEY,
    generated_at    TEXT NOT NULL,
    archetype       TEXT,
    cognitive_axis  TEXT,
    role            TEXT,
    ratified_name   TEXT,
    weakness_tags   TEXT,
    analytica_flags INTEGER DEFAULT 0
);
"""


# ─────────────────────────────────────────────────────────────────────────────
# Connection
# ─────────────────────────────────────────────────────────────────────────────

def _conn() -> sqlite3.Connection:
    """Open connection; create tables on first use."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def record(entity_data: dict, flags: list[str]) -> None:
    """
    Record a completed generation.

    Quality signal: score = max(0, 10 - len(flags)).
    Updates combo_scores for archetype, cognitive_axis, and role.
    Increments weakness_freq for each flag tag.
    Inserts a generation_log row.
    Non-fatal — logs errors and returns.
    """
    try:
        score = max(0.0, 10.0 - float(len(flags)))
        archetype      = entity_data.get('archetype', '')
        cognitive_axis = entity_data.get('cognitive_axis', '')
        role           = entity_data.get('role', '')
        ratified_name  = entity_data.get('display_name', '')
        gen_id         = entity_data.get('_generation_id', 'unknown')

        combo_items = [x for x in [archetype, cognitive_axis, role] if x]

        conn = _conn()
        try:
            # Upsert combo_scores
            for item in combo_items:
                conn.execute("""
                    INSERT INTO combo_scores (item, total_score, count)
                    VALUES (?, ?, 1)
                    ON CONFLICT(item) DO UPDATE SET
                        total_score = total_score + excluded.total_score,
                        count       = count + 1
                """, (item, score))

            # Increment weakness_freq
            for tag in flags:
                if tag:
                    conn.execute("""
                        INSERT INTO weakness_freq (tag, frequency)
                        VALUES (?, 1)
                        ON CONFLICT(tag) DO UPDATE SET frequency = frequency + 1
                    """, (tag,))

            # Insert generation_log
            conn.execute("""
                INSERT OR REPLACE INTO generation_log
                    (id, generated_at, archetype, cognitive_axis, role,
                     ratified_name, weakness_tags, analytica_flags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gen_id,
                datetime.now().isoformat(),
                archetype,
                cognitive_axis,
                role,
                ratified_name,
                json.dumps(flags),
                len(flags),
            ))

            conn.commit()
        finally:
            conn.close()

    except Exception as e:
        log.error(f"learning_engine.record() failed: {e}", exc_info=True)


def get_combo_weights() -> dict[str, float]:
    """Return {item: avg_score} for all items with count >= 2."""
    try:
        conn = _conn()
        try:
            rows = conn.execute("""
                SELECT item, total_score / count AS avg
                FROM combo_scores
                WHERE count >= 2
                ORDER BY avg DESC
            """).fetchall()
            return {row[0]: round(row[1], 3) for row in rows}
        finally:
            conn.close()
    except Exception as e:
        log.error(f"learning_engine.get_combo_weights() failed: {e}")
        return {}


def get_weakness_stats(limit: int = 20) -> list[tuple[str, int]]:
    """Return [(tag, frequency)] sorted by frequency descending."""
    try:
        conn = _conn()
        try:
            rows = conn.execute("""
                SELECT tag, frequency
                FROM weakness_freq
                ORDER BY frequency DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [(row[0], row[1]) for row in rows]
        finally:
            conn.close()
    except Exception as e:
        log.error(f"learning_engine.get_weakness_stats() failed: {e}")
        return []


def get_generation_count() -> int:
    """Return total number of completed generations recorded."""
    try:
        conn = _conn()
        try:
            row = conn.execute("SELECT COUNT(*) FROM generation_log").fetchone()
            return row[0] if row else 0
        finally:
            conn.close()
    except Exception:
        return 0
