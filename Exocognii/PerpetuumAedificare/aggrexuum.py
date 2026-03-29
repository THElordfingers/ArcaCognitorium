#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                          aggrexuum.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Actio Aggrexuum — build capture aggregation engine.

Reads pending Acquiuum Chronex captures. Uses Claude to:
  - Infer which Nodus Momentuum each capture belongs to (or create a new one)
  - Update the Nodifex (current state description) of touched nodes
  - Infer relationships between nodes

Also runs Driftuum Sentifex — drift scoring for dormant nodes.
"""

import os
import sys
import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

from db import get_db, row_to_dict
from config import get as get_cfg

log = logging.getLogger("aggrexuum")


# ─────────────────────────────────────────────────────────────────────────────
# CLAUDEBOX
# ─────────────────────────────────────────────────────────────────────────────

def _get_claudebox():
    cfg       = get_cfg()
    repo_path = cfg.get("arca_repo_path", str(Path.home() / "ArcaCognitorium"))
    if repo_path not in sys.path:
        sys.path.insert(0, repo_path)
    from claudebox import ClaudeBox
    return ClaudeBox(
        system_prompt = _SYSTEM_PROMPT,
        api_key       = os.environ.get("CLAUDE_API_KEY"),
    )


_SYSTEM_PROMPT = """You are Actio Aggrexuum — the build memory aggregation engine of the Arca Cognitorium.

Your job: read raw build captures and map them to work nodes (Nodi Momentuum).

A Nodus Momentuum represents a unit of ongoing work — an app, a feature, a concept, a question, a decision, an artefact, or a session.

You will be given:
- A raw capture (text from a build app, a note, a file)
- The current list of active Nodi (titles and current state)

Respond ONLY with JSON — no preamble, no markdown fences.

Response schema:
{
  "action": "map_existing" | "create_new" | "dismiss",
  "node_id": "existing node id if map_existing, else null",
  "new_title": "title for new node if create_new, else null",
  "new_nodicum": "nodicum type if create_new — one of: system, feature, concept, question, decision, artefact, session",
  "nodifex_update": "one or two sentences describing the current state after this capture",
  "confidence": "inferred"
}

Dismiss if the capture contains no build-relevant information (greetings, system noise, empty content).
Map to existing if the capture clearly relates to a named active node.
Create new only if the capture introduces a genuinely new work unit not represented in the active list."""

_USER_TEMPLATE = """CAPTURE:
Source: {source_type} / {source_ref}
Content: {content}

ACTIVE NODI ({count} nodes):
{nodi_summary}"""


# ─────────────────────────────────────────────────────────────────────────────
# AGGREGATION
# ─────────────────────────────────────────────────────────────────────────────

def _nodi_summary(nodi: list[dict]) -> str:
    if not nodi:
        return "(none)"
    lines = []
    for n in nodi[:30]:   # cap context at 30 nodes
        lines.append(f"  [{n['id'][:8]}] {n['title']} ({n['nodicum']}) — {n['nodifex'][:80]}")
    return "\n".join(lines)


def _classify_capture(box, capture: dict, active_nodi: list[dict]) -> dict:
    prompt = _USER_TEMPLATE.format(
        source_type   = capture["source_type"],
        source_ref    = capture.get("source_ref", ""),
        content       = capture["raw_content"][:3000],
        count         = len(active_nodi),
        nodi_summary  = _nodi_summary(active_nodi),
    )
    try:
        response = box.send(prompt)
        text = response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        result = json.loads(text)
        for key in ("action",):
            if key not in result:
                raise ValueError(f"Missing key: {key}")
        return result
    except Exception as e:
        log.warning(f"Aggrexuum classification failed for {capture['id']}: {e}")
        return {"action": "dismiss", "node_id": None,
                "new_title": None, "new_nodicum": "concept",
                "nodifex_update": "", "confidence": "inferred"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# DRIFTUUM SENTIFEX
# ─────────────────────────────────────────────────────────────────────────────

def _compute_drift(node: dict, active_nodi: list[dict],
                   exnodica: list[dict], threshold: float) -> float:
    """
    Driftuum Metrica — how stale is this node relative to its connected nodes?
    Returns 0.0–1.0. Threshold defined in Configuus.
    """
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    try:
        last = datetime.fromisoformat(node["last_touched_at"])
    except Exception:
        last = now

    staleness_days = (now - last).total_seconds() / 86400

    # Base drift from staleness — 0.0 at 0 days, 1.0 at 30 days
    base = min(1.0, staleness_days / 30)

    # Connected nodes touched recently amplify drift
    connected_ids = {
        e["to_node"] for e in exnodica if e["from_node"] == node["id"]
    } | {
        e["from_node"] for e in exnodica if e["to_node"] == node["id"]
    }

    recently_active = 0
    for n in active_nodi:
        if n["id"] in connected_ids:
            try:
                t = datetime.fromisoformat(n["last_touched_at"])
                if (now - t).total_seconds() < 86400 * 3:
                    recently_active += 1
            except Exception:
                pass

    # Each recently active connected node adds 0.1 to drift score
    drift = min(1.0, base + recently_active * 0.10)
    return round(drift, 3)


def _run_driftuum(conn, threshold: float):
    """Score drift for all active nodes. Flag those above threshold."""
    now  = _now()
    nodi = [row_to_dict(r) for r in conn.execute("""
        SELECT * FROM nodus_momentuum WHERE status = 'active'
    """).fetchall()]
    exnodica = [dict(r) for r in conn.execute(
        "SELECT from_node, to_node FROM exnodica"
    ).fetchall()]

    for node in nodi:
        score = _compute_drift(node, nodi, exnodica, threshold)
        should_flag = (score >= threshold) and not node["driftuum_attentio"]

        conn.execute("""
            UPDATE nodus_momentuum SET driftuum_metrica = ? WHERE id = ?
        """, (score, node["id"]))

        if should_flag:
            conn.execute("""
                UPDATE nodus_momentuum SET driftuum_attentio = 1 WHERE id = ?
            """, (node["id"],))

            # Find trigger nodes (connected + recently active)
            trigger_ids = []
            for ex in exnodica:
                connected_id = (ex["to_node"] if ex["from_node"] == node["id"]
                                else ex["from_node"] if ex["to_node"] == node["id"]
                                else None)
                if connected_id:
                    trigger_ids.append(connected_id)

            conn.execute("""
                INSERT INTO driftuum_log(id, node_id, driftuum_metrica,
                                         flagged_at, trigger_nodes)
                VALUES (?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), node["id"], score, now,
                  json.dumps(trigger_ids)))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PASS
# ─────────────────────────────────────────────────────────────────────────────

async def run_aggrexuum() -> dict:
    run_id     = str(uuid.uuid4())
    started_at = _now()
    processed = created = updated = 0
    error_msg = None

    cfg       = get_cfg()
    sub       = cfg.get("perpetuum_aedificare", {})
    threshold = float(sub.get("drift_threshold", 0.65))

    try:
        box = _get_claudebox()

        with get_db() as conn:
            captures = [row_to_dict(r) for r in conn.execute("""
                SELECT * FROM acquiuum_chronex
                WHERE status = 'pending' ORDER BY captured_at ASC
            """).fetchall()]

            active_nodi = [row_to_dict(r) for r in conn.execute("""
                SELECT * FROM nodus_momentuum
                WHERE status = 'active' ORDER BY last_touched_at DESC
            """).fetchall()]

            for capture in captures:
                result = _classify_capture(box, capture, active_nodi)
                action = result.get("action", "dismiss")
                now    = _now()
                processed += 1

                if action == "dismiss":
                    conn.execute("""
                        UPDATE acquiuum_chronex SET status = 'dismissed' WHERE id = ?
                    """, (capture["id"],))

                elif action == "map_existing":
                    node_id = result.get("node_id")
                    if not node_id:
                        conn.execute("""
                            UPDATE acquiuum_chronex SET status = 'dismissed' WHERE id = ?
                        """, (capture["id"],))
                        continue

                    nodifex = result.get("nodifex_update", "")
                    if nodifex:
                        conn.execute("""
                            UPDATE nodus_momentuum
                            SET last_touched_at = ?, nodifex = ?
                            WHERE id = ?
                        """, (now, nodifex, node_id))

                    conn.execute("""
                        UPDATE acquiuum_chronex
                        SET status = 'aggregated', inferred_node_id = ?,
                            node_confidence = ?
                        WHERE id = ?
                    """, (node_id, result.get("confidence", "inferred"), capture["id"]))

                    # Refresh active_nodi with updated nodifex
                    for n in active_nodi:
                        if n["id"] == node_id and nodifex:
                            n["nodifex"] = nodifex
                            n["last_touched_at"] = now
                    updated += 1

                elif action == "create_new":
                    node_id  = str(uuid.uuid4())
                    title    = result.get("new_title") or capture["source_ref"] or "Unnamed node"
                    nodicum  = result.get("new_nodicum", "concept")
                    nodifex  = result.get("nodifex_update", "")

                    conn.execute("""
                        INSERT INTO nodus_momentuum
                            (id, title, nodicum, nodicum_confidence, nodifex,
                             created_at, last_touched_at)
                        VALUES (?, ?, ?, 'inferred', ?, ?, ?)
                    """, (node_id, title, nodicum, nodifex, now, now))

                    conn.execute("""
                        UPDATE acquiuum_chronex
                        SET status = 'aggregated', inferred_node_id = ?,
                            node_confidence = 'inferred'
                        WHERE id = ?
                    """, (node_id, capture["id"]))

                    active_nodi.append({
                        "id": node_id, "title": title,
                        "nodicum": nodicum, "nodifex": nodifex,
                        "last_touched_at": now,
                    })
                    created += 1

            # Driftuum pass after aggregation
            _run_driftuum(conn, threshold)

            conn.execute("""
                INSERT INTO aggrexuum_log
                    (id, started_at, completed_at,
                     captures_processed, nodes_created, nodes_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (run_id, started_at, _now(), processed, created, updated))

    except Exception as e:
        error_msg = str(e)
        log.error(f"Actio Aggrexuum failed: {e}")
        with get_db() as conn:
            conn.execute("""
                INSERT INTO aggrexuum_log
                    (id, started_at, completed_at, captures_processed,
                     nodes_created, nodes_updated, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (run_id, started_at, _now(), processed, created, updated, error_msg))

    return {
        "run_id":    run_id,
        "processed": processed,
        "created":   created,
        "updated":   updated,
        "error":     error_msg,
    }


def get_aggrexuum_status() -> dict:
    with get_db() as conn:
        last = conn.execute("""
            SELECT * FROM aggrexuum_log ORDER BY started_at DESC LIMIT 1
        """).fetchone()
        pending = conn.execute("""
            SELECT COUNT(*) FROM acquiuum_chronex WHERE status = 'pending'
        """).fetchone()[0]
    return {
        "pending_count": pending,
        "last_run":      dict(last) if last else None,
    }
