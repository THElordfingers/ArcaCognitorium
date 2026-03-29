#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                       interpretus.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Actio Interpretus — lore relevance inference engine.

Reads pending Lorixii from the database, calls Claude to classify each one,
and writes back inferred_domain, inferred_tags, confidence, and status.

Lore-irrelevant content is marked `ignored` — never deleted.
Lore-relevant content remains `pending` for Judicium.

Also handles clustering: groups related pending Lorixii by domain
and updates related_lorixii links.
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

log = logging.getLogger("interpretus")

# ─────────────────────────────────────────────────────────────────────────────
# CLAUDEBOX IMPORT
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


# ─────────────────────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are Actio Interpretus — the lore classification engine of the Arca Cognitorium.

Your job: read raw content captured from the Cogniverse and determine whether it contains lore-relevant material.

Lore is: world-building facts, entity history, cosmological principles, named places, artefacts, rituals, factions, language, and events that shape the Cogniverse.

Lore is NOT: code, build instructions, technical implementation notes, casual conversation, or operational task lists.

You will be given raw content. Respond ONLY with a JSON object — no preamble, no markdown, no explanation.

Response schema:
{
  "lore_relevant": true or false,
  "confidence": "low" | "medium" | "high",
  "domain": "one of the seeded domains or a new proposed domain",
  "tags": ["tag1", "tag2"],
  "summary": "one sentence describing the lore content, or empty string if not relevant"
}

Seeded domains: entities, cosmology, tower_mechanics, history, places, artefacts, rituals, language, factions, wizard

If content spans multiple domains, choose the primary one.
Tags should be specific — entity names, place names, mechanic names, not generic labels.
Confidence reflects how clearly lore-relevant the content is."""

_USER_TEMPLATE = """Classify this content for lore relevance:

SOURCE: {source_type} / {source_ref}

CONTENT:
{content}"""


# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def _classify_lorix(box, lorix: dict) -> dict:
    """
    Call Claude to classify a single Lorix.
    Returns classification dict or a safe fallback on error.
    """
    prompt = _USER_TEMPLATE.format(
        source_type = lorix["source_type"],
        source_ref  = lorix.get("source_ref", ""),
        content     = lorix["raw_content"][:4000],  # cap at 4k chars
    )
    try:
        response = box.send(prompt)
        # Strip any accidental markdown fences
        text = response.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
        # Validate required keys
        for key in ("lore_relevant", "confidence", "domain", "tags"):
            if key not in result:
                raise ValueError(f"Missing key: {key}")
        return result
    except Exception as e:
        log.warning(f"Classification failed for {lorix['id']}: {e}")
        return {
            "lore_relevant": False,
            "confidence":    "low",
            "domain":        "",
            "tags":          [],
            "summary":       "",
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLUSTERING
# ─────────────────────────────────────────────────────────────────────────────

def _cluster_pending(conn) -> None:
    """
    Group pending Lorixii by inferred_domain and link related ones.
    Two Lorixii are related if they share the same domain.
    Updates related_lorixii JSON array on each row.
    """
    rows = conn.execute("""
        SELECT id, inferred_domain FROM lorixii_speculativum
        WHERE status = 'pending' AND inferred_domain != ''
    """).fetchall()

    domain_map: dict[str, list] = {}
    for row in rows:
        d = row["inferred_domain"]
        domain_map.setdefault(d, []).append(row["id"])

    for domain, ids in domain_map.items():
        if len(ids) < 2:
            continue
        for lorix_id in ids:
            related = [i for i in ids if i != lorix_id]
            conn.execute("""
                UPDATE lorixii_speculativum
                SET related_lorixii = ?
                WHERE id = ?
            """, (json.dumps(related), lorix_id))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PASS
# ─────────────────────────────────────────────────────────────────────────────

async def run_interpretus() -> dict:
    """
    Full Actio Interpretus pass.
    Processes all pending Lorixii, classifies, updates, clusters.
    Returns a summary dict.
    """
    run_id     = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()
    processed = claimed = ignored = 0
    error_msg = None

    try:
        box = _get_claudebox()

        with get_db() as conn:
            rows = conn.execute("""
                SELECT * FROM lorixii_speculativum WHERE status = 'pending'
                ORDER BY ingested_at ASC
            """).fetchall()

            for row in rows:
                lorix = row_to_dict(row)
                result = _classify_lorix(box, lorix)
                processed += 1

                if result["lore_relevant"]:
                    conn.execute("""
                        UPDATE lorixii_speculativum
                        SET inferred_domain = ?,
                            inferred_tags   = ?,
                            confidence      = ?
                        WHERE id = ?
                    """, (
                        result["domain"],
                        json.dumps(result.get("tags", [])),
                        result["confidence"],
                        lorix["id"],
                    ))
                    claimed += 1
                else:
                    conn.execute("""
                        UPDATE lorixii_speculativum
                        SET status = 'ignored'
                        WHERE id = ?
                    """, (lorix["id"],))
                    ignored += 1

            # Cluster after all classifications
            _cluster_pending(conn)

            # Log the run
            conn.execute("""
                INSERT INTO interpretus_log
                    (id, started_at, completed_at,
                     lorixii_processed, lorixii_claimed, lorixii_ignored)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                run_id, started_at,
                datetime.now(timezone.utc).isoformat(),
                processed, claimed, ignored,
            ))

    except Exception as e:
        error_msg = str(e)
        log.error(f"Actio Interpretus failed: {e}")

        with get_db() as conn:
            conn.execute("""
                INSERT INTO interpretus_log
                    (id, started_at, completed_at, lorixii_processed,
                     lorixii_claimed, lorixii_ignored, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, started_at,
                datetime.now(timezone.utc).isoformat(),
                processed, claimed, ignored, error_msg,
            ))

    return {
        "run_id":    run_id,
        "processed": processed,
        "claimed":   claimed,
        "ignored":   ignored,
        "error":     error_msg,
    }


def get_interpretus_status() -> dict:
    """Last run info and current pending count."""
    with get_db() as conn:
        last = conn.execute("""
            SELECT * FROM interpretus_log
            ORDER BY started_at DESC LIMIT 1
        """).fetchone()

        pending_count = conn.execute("""
            SELECT COUNT(*) FROM lorixii_speculativum WHERE status = 'pending'
        """).fetchone()[0]

    return {
        "pending_count": pending_count,
        "last_run":      dict(last) if last else None,
    }
