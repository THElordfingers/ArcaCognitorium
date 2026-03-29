#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ              routers/loricuum.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Arx Loricuum — taxonomy register.

GET    /loricuum            — full register
POST   /loricuum/domain     — propose domain
POST   /loricuum/tag        — propose tag
PUT    /loricuum/{id}       — approve/reject/rename
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import get_db, row_to_dict

router = APIRouter(tags=["loricuum"])


class DomainProposal(BaseModel):
    name:        str
    proposed_by: str = "wizard"


class TagProposal(BaseModel):
    name:          str
    parent_domain: str
    proposed_by:   str = "wizard"


class TaxonomyUpdate(BaseModel):
    status: Optional[str] = None
    name:   Optional[str] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/loricuum")
async def get_loricuum():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM arx_loricuum ORDER BY type DESC, name ASC
        """).fetchall()
    return {"entries": [row_to_dict(r) for r in rows]}


@router.post("/loricuum/domain", status_code=201)
async def propose_domain(payload: DomainProposal):
    entry_id = str(uuid.uuid4())
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM arx_loricuum WHERE name = ?", (payload.name,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Domain already exists")
        conn.execute("""
            INSERT INTO arx_loricuum(id, name, type, status, proposed_by, created_at)
            VALUES (?, ?, 'domain', 'proposed', ?, ?)
        """, (entry_id, payload.name, payload.proposed_by, _now()))
    return {"id": entry_id, "name": payload.name, "status": "proposed"}


@router.post("/loricuum/tag", status_code=201)
async def propose_tag(payload: TagProposal):
    entry_id = str(uuid.uuid4())
    with get_db() as conn:
        # Resolve parent domain id
        parent = conn.execute(
            "SELECT id FROM arx_loricuum WHERE name = ? AND type = 'domain'",
            (payload.parent_domain,)
        ).fetchone()
        if not parent:
            raise HTTPException(
                status_code=404, detail=f"Parent domain '{payload.parent_domain}' not found"
            )
        conn.execute("""
            INSERT INTO arx_loricuum(id, name, type, parent_domain, status, proposed_by, created_at)
            VALUES (?, ?, 'tag', ?, 'proposed', ?, ?)
        """, (entry_id, payload.name, parent["id"], payload.proposed_by, _now()))
    return {"id": entry_id, "name": payload.name, "status": "proposed"}


@router.put("/loricuum/{entry_id}")
async def update_taxonomy(entry_id: str, payload: TaxonomyUpdate):
    valid_statuses = {"seeded", "ratified", "proposed", "rejected"}
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM arx_loricuum WHERE id = ?", (entry_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Taxonomy entry not found")

        updates = []
        params  = []
        if payload.status:
            if payload.status not in valid_statuses:
                raise HTTPException(status_code=422, detail=f"Invalid status: {payload.status}")
            updates.append("status = ?"); params.append(payload.status)
        if payload.name:
            updates.append("name = ?"); params.append(payload.name)

        if not updates:
            raise HTTPException(status_code=422, detail="Nothing to update")

        params.append(entry_id)
        conn.execute(
            f"UPDATE arx_loricuum SET {', '.join(updates)} WHERE id = ?", params
        )
    return {"id": entry_id, "updated": True}
