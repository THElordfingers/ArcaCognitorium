#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                 routers/canon.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Canon endpoints — Loridex Cards and Exlorica.

GET    /cards                  — list cards
GET    /card/{id}              — fetch card
GET    /card/{id}/exloricum    — fetch bound exloricum
GET    /exlorica               — list all exlorica
GET    /exloricum/{id}         — fetch single exloricum
PUT    /exloricum/{id}         — Wizard edits prose body directly
"""

import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from db import get_db, row_to_dict

router = APIRouter(tags=["canon"])


class ExloricumEdit(BaseModel):
    body: str   # full prose body replacement


@router.get("/cards")
async def list_cards(
    domain: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tags:   Optional[str] = Query(None, description="Comma-separated tag filter"),
    limit:  int           = Query(50, ge=1, le=200),
    offset: int           = Query(0, ge=0),
):
    """List Loridex Cards, filterable by domain, status, and tags."""
    clauses = []
    params  = []
    if domain:
        clauses.append("domain = ?");  params.append(domain)
    if status:
        clauses.append("status = ?");  params.append(status)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    params_q = params + [limit, offset]

    with get_db() as conn:
        rows = conn.execute(f"""
            SELECT * FROM loridex_cards
            {where}
            ORDER BY ratified_at DESC
            LIMIT ? OFFSET ?
        """, params_q).fetchall()

        total = conn.execute(
            f"SELECT COUNT(*) FROM loridex_cards {where}", params
        ).fetchone()[0]

    results = [row_to_dict(r) for r in rows]

    # Tag filter applied in Python (JSON array stored in SQLite)
    if tags:
        tag_set = {t.strip().lower() for t in tags.split(",")}
        results = [
            r for r in results
            if tag_set.intersection({t.lower() for t in (r.get("tags") or [])})
        ]

    return {"total": total, "limit": limit, "offset": offset, "results": results}


@router.get("/card/{card_id}")
async def get_card(card_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM loridex_cards WHERE id = ?", (card_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Card not found")
    return row_to_dict(row)


@router.get("/card/{card_id}/exloricum")
async def get_card_exloricum(card_id: str):
    with get_db() as conn:
        card = conn.execute(
            "SELECT exloricum_id FROM loridex_cards WHERE id = ?", (card_id,)
        ).fetchone()
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        if not card["exloricum_id"]:
            raise HTTPException(status_code=404, detail="No exloricum bound to this card")
        row = conn.execute(
            "SELECT * FROM exlorica WHERE id = ?", (card["exloricum_id"],)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Exloricum not found")
    return _exloricum_with_body(row_to_dict(row))


@router.get("/exlorica")
async def list_exlorica(
    limit:  int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM exlorica ORDER BY created_at DESC LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM exlorica").fetchone()[0]
    return {
        "total":   total,
        "limit":   limit,
        "offset":  offset,
        "results": [row_to_dict(r) for r in rows],
    }


@router.get("/exloricum/{exloricum_id}")
async def get_exloricum(exloricum_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM exlorica WHERE id = ?", (exloricum_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Exloricum not found")
    return _exloricum_with_body(row_to_dict(row))


@router.put("/exloricum/{exloricum_id}")
async def edit_exloricum(exloricum_id: str, payload: ExloricumEdit):
    """Wizard directly edits the prose body of an Exloricum."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM exlorica WHERE id = ?", (exloricum_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Exloricum not found")

        # Write updated .md file
        ex = row_to_dict(row)
        file_path = ex.get("file_path", "")
        if file_path:
            try:
                from pathlib import Path
                p = Path(file_path)
                p.parent.mkdir(parents=True, exist_ok=True)
                _write_exloricum_md(p, ex["title"], payload.body, now)
            except Exception:
                pass   # prose still updated in DB regardless

        conn.execute("""
            UPDATE exlorica
            SET last_revised_at = ?, revision_count = revision_count + 1,
                word_count = ?
            WHERE id = ?
        """, (now, len(payload.body.split()), exloricum_id))

        # Flag card for revision awareness
        conn.execute("""
            UPDATE loridex_cards SET status = 'flagged_for_revision'
            WHERE exloricum_id = ? AND status = 'ratified'
        """, (exloricum_id,))

        # Update ratifex last_wizard_edit
        conn.execute("""
            UPDATE loricum_ratifex SET last_wizard_edit_at = ?,
            version = version + 1 WHERE id = 1
        """, (now,))

    return {"id": exloricum_id, "revised_at": now}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _exloricum_with_body(ex: dict) -> dict:
    """Attach prose body from .md file if it exists."""
    file_path = ex.get("file_path", "")
    if file_path:
        from pathlib import Path
        p = Path(file_path)
        if p.exists():
            try:
                raw  = p.read_text()
                # Strip YAML frontmatter if present
                if raw.startswith("---"):
                    parts = raw.split("---", 2)
                    body  = parts[2].strip() if len(parts) >= 3 else raw
                else:
                    body = raw
                ex["body"] = body
            except Exception:
                ex["body"] = ""
        else:
            ex["body"] = ""
    else:
        ex["body"] = ""
    return ex


def _write_exloricum_md(path, title: str, body: str, revised_at: str):
    from pathlib import Path
    frontmatter = f"---\ntitle: {title}\nrevised_at: {revised_at}\n---\n\n"
    Path(path).write_text(frontmatter + body)
