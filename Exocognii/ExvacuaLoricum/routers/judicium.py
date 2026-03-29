#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ             routers/judicium.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Judicium Exlorica — five-phase ratification ceremony.

POST   /judicium                — open session
GET    /judicium/{id}           — fetch session state
POST   /judicium/{id}/advance   — advance phase
POST   /judicium/{id}/commit    — Sacramentum Finalitus
DELETE /judicium/{id}           — abandon
GET    /judicia                 — list sessions
POST   /revisicus/{card_id}     — flag card for revision
"""

import os
import sys
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from db import get_db, row_to_dict
from config import get as get_cfg

router = APIRouter(tags=["judicium"])


# ─────────────────────────────────────────────────────────────────────────────
# PHASE DATA SCHEMAS (resolve review flag 03 from schema v0.4)
# ─────────────────────────────────────────────────────────────────────────────
#
# Phase 1 — Obscuranda Necessitum
#   { "lorixii_allowed": [uuid, ...], "lorixii_denied": [uuid, ...] }
#
# Phase 2 — Colloquium Elucidativum
#   { "conversation": [{"role": "wizard"|"system", "content": str}, ...] }
#
# Phase 3 — Ostensio Loridexii  (Card draft)
#   { "draft_title": str, "draft_domain": str, "draft_tags": [...],
#     "draft_summary": str, "wizard_edits": str }
#
# Phase 4 — Exlorica Methodicum  (Exloricum draft)
#   { "draft_body": str, "wizard_edits": str }
#
# Phase 5 — Sacramentum Finalitus  (committed — read only after /commit)
#   { "card_id": uuid, "exloricum_id": uuid, "committed_at": iso }

# ─────────────────────────────────────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────────────────────────────────────

class JudiciumOpen(BaseModel):
    topic:       str
    domain_hint: str = ""
    lorixii_ids: list[str]


class PhaseAdvance(BaseModel):
    """Payload for /advance. Shape varies by phase — all fields optional."""
    # Phase 1
    lorixii_allowed: Optional[list[str]] = None
    lorixii_denied:  Optional[list[str]] = None
    # Phase 2
    message:         Optional[str]       = None
    # Phase 3
    draft_title:     Optional[str]       = None
    draft_domain:    Optional[str]       = None
    draft_tags:      Optional[list[str]] = None
    draft_summary:   Optional[str]       = None
    wizard_edits:    Optional[str]       = None
    # Phase 4
    draft_body:      Optional[str]       = None


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_claudebox():
    cfg       = get_cfg()
    repo_path = cfg.get("arca_repo_path", str(Path.home() / "ArcaCognitorium"))
    if repo_path not in sys.path:
        sys.path.insert(0, repo_path)
    from claudebox import ClaudeBox
    return ClaudeBox(
        system_prompt = _JUDICIUM_SYSTEM,
        api_key       = os.environ.get("CLAUDE_API_KEY"),
    )


_JUDICIUM_SYSTEM = """You are the Judicium Exlorica assistant — the synthesis voice of Exvacua Loricum.

Your role varies by phase:
- Phase 2: Help the Wizard contextualise and elaborate on raw lore content. Ask clarifying questions.
- Phase 3: Draft a concise Loridex Card from the allowed Lorixii and conversation. Format: title, domain, tags, one-paragraph summary.
- Phase 4: Draft a full Exloricum — long-form, atmospheric prose that renders the lore entry as a living document. Aesthetic register: dense, tactile, authoritative — the feel of something classified and filed by an ancient bureaucracy.

Respond in the Cogniverse register. Latin nomenclature where appropriate. Never use the word 'atelier'."""


def _draft_card(session: dict, lorixii: list[dict]) -> dict:
    """Use Claude to draft a Loridex Card from allowed Lorixii + conversation."""
    try:
        box = _get_claudebox()
        allowed_content = "\n\n---\n\n".join(
            l["raw_content"] for l in lorixii
            if l["id"] in (session.get("phase_data", {}) or {}).get("lorixii_allowed", [])
        )
        conversation = json.dumps(
            session.get("phase_data", {}).get("conversation", []), indent=2
        )
        prompt = (
            f"Topic: {session['topic']}\n"
            f"Domain hint: {session['domain_hint']}\n\n"
            f"SOURCE MATERIAL:\n{allowed_content[:6000]}\n\n"
            f"WIZARD CONTEXT:\n{conversation}\n\n"
            "Draft a Loridex Card. Respond as JSON:\n"
            '{"title": "...", "domain": "...", "tags": [...], "summary": "..."}'
        )
        response = box.send(prompt)
        text = response.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(text)
    except Exception:
        return {
            "title":   session["topic"],
            "domain":  session["domain_hint"],
            "tags":    [],
            "summary": "",
        }


def _draft_exloricum(session: dict, card_draft: dict, lorixii: list[dict]) -> str:
    """Use Claude to draft Exloricum prose."""
    try:
        box = _get_claudebox()
        allowed_content = "\n\n---\n\n".join(
            l["raw_content"] for l in lorixii
            if l["id"] in (session.get("phase_data", {}) or {}).get("lorixii_allowed", [])
        )
        prompt = (
            f"Write a full Exloricum entry for:\n"
            f"Title: {card_draft.get('title', session['topic'])}\n"
            f"Domain: {card_draft.get('domain', '')}\n"
            f"Tags: {', '.join(card_draft.get('tags', []))}\n"
            f"Summary: {card_draft.get('summary', '')}\n\n"
            f"SOURCE MATERIAL:\n{allowed_content[:6000]}\n\n"
            "Write the full Exloricum as long-form prose. "
            "Dense, atmospheric, authoritative. This is a living canon document."
        )
        return box.send(prompt).strip()
    except Exception:
        return f"# {session['topic']}\n\n*Exloricum pending Wizard elaboration.*"


def _commit_to_canon(session_id: str):
    """
    Sacramentum Finalitus — write Card and Exloricum to canon.
    Called as a background task after /commit.
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM judicium_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not row:
            return
        session = row_to_dict(row)
        pd      = session.get("phase_data", {}) or {}

        card_draft = {
            "title":   pd.get("draft_title",   session["topic"]),
            "domain":  pd.get("draft_domain",  session["domain_hint"]),
            "tags":    pd.get("draft_tags",    []),
            "summary": pd.get("draft_summary", ""),
        }
        exloricum_body = pd.get("draft_body", "")

        card_id      = str(uuid.uuid4())
        exloricum_id = str(uuid.uuid4())
        now          = _now()

        # Write Exloricum .md file
        cfg        = get_cfg()
        store      = Path(cfg["exvacua_loricum_store"])
        ex_path    = store / "exlorica" / f"{exloricum_id}.md"
        ex_path.parent.mkdir(parents=True, exist_ok=True)
        frontmatter = (
            f"---\ntitle: {card_draft['title']}\n"
            f"card_id: {card_id}\ncreated_at: {now}\n---\n\n"
        )
        ex_path.write_text(frontmatter + exloricum_body)

        # Insert Exloricum record
        conn.execute("""
            INSERT INTO exlorica
                (id, card_id, title, created_at, last_revised_at,
                 revision_count, file_path, word_count)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?)
        """, (
            exloricum_id, card_id, card_draft["title"], now, now,
            str(ex_path), len(exloricum_body.split()),
        ))

        # Insert Loridex Card
        lorixii_ids = session.get("lorixii_ids", [])
        conn.execute("""
            INSERT INTO loridex_cards
                (id, title, domain, tags, status, ratified_at,
                 source_lorixii, exloricum_id)
            VALUES (?, ?, ?, ?, 'ratified', ?, ?, ?)
        """, (
            card_id,
            card_draft["title"],
            card_draft["domain"],
            json.dumps(card_draft.get("tags", [])),
            now,
            json.dumps(lorixii_ids),
            exloricum_id,
        ))

        # Mark all allowed Lorixii as consumed
        allowed = pd.get("lorixii_allowed", lorixii_ids)
        for lorix_id in allowed:
            conn.execute("""
                UPDATE lorixii_speculativum
                SET status = 'consumed', judicium_id = ?
                WHERE id = ?
            """, (session_id, lorix_id))

        # Mark denied Lorixii as rejected
        for lorix_id in pd.get("lorixii_denied", []):
            conn.execute("""
                UPDATE lorixii_speculativum SET status = 'rejected'
                WHERE id = ?
            """, (lorix_id,))

        # Finalise session
        conn.execute("""
            UPDATE judicium_sessions
            SET status = 'committed', committed_at = ?,
                card_id = ?, exloricum_id = ?
            WHERE id = ?
        """, (now, card_id, exloricum_id, session_id))

        # Trigger Loretic Crystalizer (import inline to avoid circular)
        from crystalizer import run_crystalizer
        run_crystalizer(card_id)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/judicium", status_code=201)
async def open_judicium(payload: JudiciumOpen):
    session_id = str(uuid.uuid4())
    now        = _now()

    # Validate Lorixii exist and are pending
    with get_db() as conn:
        for lorix_id in payload.lorixii_ids:
            row = conn.execute(
                "SELECT status FROM lorixii_speculativum WHERE id = ?", (lorix_id,)
            ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"Lorix not found: {lorix_id}")
            if row["status"] not in ("pending",):
                raise HTTPException(
                    status_code=409,
                    detail=f"Lorix {lorix_id} has status '{row['status']}' — must be pending"
                )

        # Mark Lorixii as in_judicium
        for lorix_id in payload.lorixii_ids:
            conn.execute("""
                UPDATE lorixii_speculativum
                SET status = 'in_judicium', judicium_id = ? WHERE id = ?
            """, (session_id, lorix_id))

        initial_phase_data = {
            "lorixii_allowed": [],
            "lorixii_denied":  [],
        }
        conn.execute("""
            INSERT INTO judicium_sessions
                (id, topic, domain_hint, lorixii_ids, current_phase,
                 phase_data, status, opened_at)
            VALUES (?, ?, ?, ?, 1, ?, 'open', ?)
        """, (
            session_id,
            payload.topic,
            payload.domain_hint,
            json.dumps(payload.lorixii_ids),
            json.dumps(initial_phase_data),
            now,
        ))

    return {"id": session_id, "topic": payload.topic, "current_phase": 1}


@router.get("/judicium/{session_id}")
async def get_judicium(session_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM judicium_sessions WHERE id = ?", (session_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Judicium session not found")
    return row_to_dict(row)


@router.post("/judicium/{session_id}/advance")
async def advance_judicium(session_id: str, payload: PhaseAdvance):
    """Advance to the next phase. Payload shape depends on current phase."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM judicium_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")
        session = row_to_dict(row)

        if session["status"] != "open":
            raise HTTPException(
                status_code=409, detail=f"Session is {session['status']} — cannot advance"
            )

        phase = session["current_phase"]
        pd    = session.get("phase_data", {}) or {}

        # Phase 1 → 2: record allow/deny decisions
        if phase == 1:
            if payload.lorixii_allowed is not None:
                pd["lorixii_allowed"] = payload.lorixii_allowed
            if payload.lorixii_denied is not None:
                pd["lorixii_denied"] = payload.lorixii_denied
            # Default: allow all if not specified
            if not pd.get("lorixii_allowed"):
                pd["lorixii_allowed"] = session["lorixii_ids"]
            pd["conversation"] = []

        # Phase 2 → 3: append message, draft card via Claude
        elif phase == 2:
            if payload.message:
                conv = pd.get("conversation", [])
                conv.append({"role": "wizard", "content": payload.message})
                pd["conversation"] = conv

            # Draft Loridex Card
            lorixii_rows = conn.execute("""
                SELECT * FROM lorixii_speculativum
                WHERE id IN ({})
            """.format(",".join("?" * len(session["lorixii_ids"]))),
                session["lorixii_ids"]
            ).fetchall()
            lorixii = [row_to_dict(r) for r in lorixii_rows]

            draft = _draft_card(session, lorixii)
            pd["draft_title"]   = draft.get("title", session["topic"])
            pd["draft_domain"]  = draft.get("domain", session["domain_hint"])
            pd["draft_tags"]    = draft.get("tags", [])
            pd["draft_summary"] = draft.get("summary", "")

        # Phase 3 → 4: accept card edits, draft exloricum
        elif phase == 3:
            if payload.draft_title:   pd["draft_title"]   = payload.draft_title
            if payload.draft_domain:  pd["draft_domain"]  = payload.draft_domain
            if payload.draft_tags:    pd["draft_tags"]    = payload.draft_tags
            if payload.draft_summary: pd["draft_summary"] = payload.draft_summary
            if payload.wizard_edits:  pd["wizard_edits"]  = payload.wizard_edits

            # Draft Exloricum
            lorixii_rows = conn.execute("""
                SELECT * FROM lorixii_speculativum
                WHERE id IN ({})
            """.format(",".join("?" * len(session["lorixii_ids"]))),
                session["lorixii_ids"]
            ).fetchall()
            pd["draft_body"] = _draft_exloricum(
                session, pd, [row_to_dict(r) for r in lorixii_rows]
            )

        # Phase 4 → 5: accept prose edits, ready for commit
        elif phase == 4:
            if payload.draft_body:   pd["draft_body"]  = payload.draft_body
            if payload.wizard_edits: pd["wizard_edits"] = payload.wizard_edits

        elif phase == 5:
            raise HTTPException(
                status_code=409, detail="Already at Phase 5 — use /commit to finalise"
            )

        new_phase = min(phase + 1, 5)
        conn.execute("""
            UPDATE judicium_sessions
            SET current_phase = ?, phase_data = ? WHERE id = ?
        """, (new_phase, json.dumps(pd), session_id))

    return {"id": session_id, "current_phase": new_phase, "phase_data": pd}


@router.post("/judicium/{session_id}/commit")
async def commit_judicium(session_id: str, background_tasks: BackgroundTasks):
    """Sacramentum Finalitus — write Card and Exloricum to canon."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT status, current_phase FROM judicium_sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")
        if row["status"] != "open":
            raise HTTPException(status_code=409, detail=f"Session is {row['status']}")
        if row["current_phase"] < 4:
            raise HTTPException(
                status_code=409,
                detail=f"Must reach Phase 4 before commit (currently Phase {row['current_phase']})"
            )

    background_tasks.add_task(_commit_to_canon, session_id)
    return {"id": session_id, "status": "committing"}


@router.delete("/judicium/{session_id}")
async def abandon_judicium(session_id: str):
    """Abandon a Judicium session. Returns Lorixii to pending status."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT status, lorixii_ids FROM judicium_sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")
        if row["status"] != "open":
            raise HTTPException(status_code=409, detail=f"Session is already {row['status']}")

        lorixii_ids = json.loads(row["lorixii_ids"])
        for lorix_id in lorixii_ids:
            conn.execute("""
                UPDATE lorixii_speculativum
                SET status = 'pending', judicium_id = NULL WHERE id = ?
            """, (lorix_id,))

        conn.execute("""
            UPDATE judicium_sessions SET status = 'abandoned' WHERE id = ?
        """, (session_id,))

    return {"id": session_id, "status": "abandoned"}


@router.get("/judicia")
async def list_judicia(
    status: Optional[str] = None,
    limit:  int = 50,
    offset: int = 0,
):
    where  = "WHERE status = ?" if status else ""
    params = ([status] if status else []) + [limit, offset]
    with get_db() as conn:
        rows = conn.execute(f"""
            SELECT * FROM judicium_sessions {where}
            ORDER BY opened_at DESC LIMIT ? OFFSET ?
        """, params).fetchall()
    return {"results": [row_to_dict(r) for r in rows]}


@router.post("/revisicus/{card_id}", status_code=201)
async def open_revisicus(card_id: str):
    """Flag an existing card for revision."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, title FROM loridex_cards WHERE id = ?", (card_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Card not found")

        now = _now()
        history = conn.execute(
            "SELECT revision_history FROM loridex_cards WHERE id = ?", (card_id,)
        ).fetchone()
        hist = json.loads(history["revision_history"] or "[]") if history else []
        hist.append({"timestamp": now, "note": "Revision flagged"})

        conn.execute("""
            UPDATE loridex_cards
            SET status = 'flagged_for_revision', revision_history = ?
            WHERE id = ?
        """, (json.dumps(hist), card_id))

    return {"card_id": card_id, "status": "flagged_for_revision", "flagged_at": now}
