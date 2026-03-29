#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                 routers/nodi.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Nodus Momentuum endpoints.

POST   /nodus                    — create manually
GET    /nodi                     — list, filterable
GET    /nodus/{id}               — fetch single
PUT    /nodus/{id}               — update nodifex, nodicum, status, questions
DELETE /nodus/{id}               — mark abandoned
GET    /nodus/{id}/acquiuum      — fetch associated captures
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from db import get_db, row_to_dict

router = APIRouter(tags=["nodi"])


class NodeCreate(BaseModel):
    title:          str
    nodicum:        str  = "concept"
    nodifex:        str  = ""
    open_questions: list = []


class NodeUpdate(BaseModel):
    nodifex:        Optional[str]  = None
    nodicum:        Optional[str]  = None
    status:         Optional[str]  = None
    open_questions: Optional[list] = None
    decisions:      Optional[list] = None
    nodicum_confidence: Optional[str] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/nodus", status_code=201)
async def create_nodus(payload: NodeCreate):
    node_id = str(uuid.uuid4())
    now     = _now()
    with get_db() as conn:
        conn.execute("""
            INSERT INTO nodus_momentuum
                (id, title, nodicum, nodicum_confidence, nodifex,
                 created_at, last_touched_at, open_questions)
            VALUES (?, ?, ?, 'wizard_set', ?, ?, ?, ?)
        """, (node_id, payload.title, payload.nodicum, payload.nodifex,
              now, now, json.dumps(payload.open_questions)))
    return {"id": node_id, "title": payload.title, "status": "active"}


@router.get("/nodi")
async def list_nodi(
    nodicum: Optional[str] = Query(None),
    status:  Optional[str] = Query(None),
    limit:   int           = Query(50, ge=1, le=200),
    offset:  int           = Query(0, ge=0),
):
    clauses, params = [], []
    if nodicum:
        clauses.append("nodicum = ?"); params.append(nodicum)
    if status:
        clauses.append("status = ?");  params.append(status)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    with get_db() as conn:
        rows = conn.execute(f"""
            SELECT * FROM nodus_momentuum {where}
            ORDER BY last_touched_at DESC LIMIT ? OFFSET ?
        """, params + [limit, offset]).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) FROM nodus_momentuum {where}", params
        ).fetchone()[0]
    return {"total": total, "limit": limit, "offset": offset,
            "results": [row_to_dict(r) for r in rows]}


@router.get("/nodus/{node_id}")
async def get_nodus(node_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM nodus_momentuum WHERE id = ?", (node_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Node not found")
        exnodica = conn.execute("""
            SELECT * FROM exnodica WHERE from_node = ? OR to_node = ?
        """, (node_id, node_id)).fetchall()
    result = row_to_dict(row)
    result["exnodica"] = [dict(e) for e in exnodica]
    return result


@router.put("/nodus/{node_id}")
async def update_nodus(node_id: str, payload: NodeUpdate):
    valid_statuses = {"active", "dormant", "resolved", "abandoned"}
    now = _now()
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM nodus_momentuum WHERE id = ?", (node_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Node not found")

        updates, params = ["last_touched_at = ?"], [now]
        if payload.nodifex is not None:
            updates.append("nodifex = ?");  params.append(payload.nodifex)
        if payload.nodicum is not None:
            updates.append("nodicum = ?");  params.append(payload.nodicum)
            updates.append("nodicum_confidence = 'wizard_set'")
        if payload.status is not None:
            if payload.status not in valid_statuses:
                raise HTTPException(status_code=422, detail=f"Invalid status: {payload.status}")
            updates.append("status = ?");   params.append(payload.status)
        if payload.open_questions is not None:
            updates.append("open_questions = ?")
            params.append(json.dumps(payload.open_questions))
        if payload.decisions is not None:
            existing = json.loads(row["decisions"] or "[]")
            existing.extend(payload.decisions)
            updates.append("decisions = ?"); params.append(json.dumps(existing))

        params.append(node_id)
        conn.execute(
            f"UPDATE nodus_momentuum SET {', '.join(updates)} WHERE id = ?", params
        )
    return {"id": node_id, "updated_at": now}


@router.delete("/nodus/{node_id}")
async def abandon_nodus(node_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM nodus_momentuum WHERE id = ?", (node_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Node not found")
        conn.execute(
            "UPDATE nodus_momentuum SET status = 'abandoned' WHERE id = ?", (node_id,)
        )
    return {"id": node_id, "status": "abandoned"}


@router.get("/nodus/{node_id}/acquiuum")
async def get_node_captures(node_id: str, limit: int = Query(50, ge=1, le=200)):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM acquiuum_chronex
            WHERE inferred_node_id = ?
            ORDER BY captured_at DESC LIMIT ?
        """, (node_id, limit)).fetchall()
    return {"node_id": node_id, "results": [row_to_dict(r) for r in rows]}
