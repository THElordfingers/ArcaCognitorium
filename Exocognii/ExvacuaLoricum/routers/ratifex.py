#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ               routers/ratifex.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Loricum Ratifex endpoints.

GET    /ratifex                    — fetch full compendium
GET    /ratifex/section/{domain}   — fetch single domain section
PUT    /ratifex/section/{domain}   — Wizard edits section directly
"""

import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import get_db, row_to_dict
from config import get as get_cfg

router = APIRouter(tags=["ratifex"])


class SectionEdit(BaseModel):
    body: str


def _ratifex_path() -> Path:
    cfg = get_cfg()
    store = Path(cfg["exvacua_loricum_store"])
    return store / "loricum_ratifex.md"


def _read_ratifex() -> str:
    p = _ratifex_path()
    return p.read_text() if p.exists() else ""


def _write_ratifex(content: str):
    p = _ratifex_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


@router.get("/ratifex")
async def get_ratifex():
    with get_db() as conn:
        row = conn.execute("SELECT * FROM loricum_ratifex WHERE id = 1").fetchone()
    meta = row_to_dict(row) if row else {}
    meta["body"] = _read_ratifex()
    return meta


@router.get("/ratifex/section/{domain}")
async def get_ratifex_section(domain: str):
    body = _read_ratifex()
    section = _extract_section(body, domain)
    if section is None:
        raise HTTPException(status_code=404, detail=f"Section '{domain}' not found in Ratifex")
    return {"domain": domain, "body": section}


@router.put("/ratifex/section/{domain}")
async def edit_ratifex_section(domain: str, payload: SectionEdit):
    """Wizard directly edits a domain section. Marks with wizard provenance comment."""
    now  = datetime.now(timezone.utc).isoformat()
    body = _read_ratifex()

    # Annotate with wizard provenance
    annotated = f"<!-- wizard: {now[:10]} -->\n{payload.body}"
    new_body   = _replace_or_append_section(body, domain, annotated)
    _write_ratifex(new_body)

    with get_db() as conn:
        conn.execute("""
            UPDATE loricum_ratifex
            SET last_wizard_edit_at = ?, version = version + 1 WHERE id = 1
        """, (now,))

    return {"domain": domain, "updated_at": now}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _extract_section(body: str, domain: str) -> str | None:
    pattern = re.compile(
        r'^# ' + re.escape(domain.upper()) + r'\s*\n(.*?)(?=^# |\Z)',
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    m = pattern.search(body)
    return m.group(1).strip() if m else None


def _replace_or_append_section(body: str, domain: str, new_content: str) -> str:
    header  = f"# {domain.upper()}\n"
    pattern = re.compile(
        r'^# ' + re.escape(domain.upper()) + r'\s*\n(.*?)(?=^# |\Z)',
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    replacement = header + new_content + "\n\n"
    if pattern.search(body):
        return pattern.sub(replacement, body)
    return body.rstrip() + "\n\n" + replacement
