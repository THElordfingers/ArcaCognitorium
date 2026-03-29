#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ              routers/exnodica.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Exnodica — relationship graph.

POST   /exnodica            — create relationship
GET    /nodus/{id}/exnodica — all relationships for a node
PUT    /exnodica/{id}       — update relationship
DELETE /exnodica/{id}       — remove relationship
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import get_db

router = APIRouter(tags=["exnodica"])


class ExnodicaCreate(BaseModel):
    from_node:    str
    to_node:      str
    relationship: str = "informs"


class ExnodicaUpdate(BaseModel):
    relationship:            Optional[str] = None
    relationship_confidence: Optional[str] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/exnodica", status_code=201)
async def create_exnodica(payload: ExnodicaCreate):
    edge_id = str(uuid.uuid4())
    with get_db() as conn:
        for node_id in (payload.from_node, payload.to_node):
            if not conn.execute(
                "SELECT id FROM nodus_momentuum WHERE id = ?", (node_id,)
            ).fetchone():
                raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
        conn.execute("""
            INSERT INTO exnodica(id, from_node, to_node, relationship, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (edge_id, payload.from_node, payload.to_node, payload.relationship, _now()))
    return {"id": edge_id, "relationship": payload.relationship}


@router.get("/nodus/{node_id}/exnodica")
async def get_node_exnodica(node_id: str):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM exnodica WHERE from_node = ? OR to_node = ?
        """, (node_id, node_id)).fetchall()
    return {"node_id": node_id, "results": [dict(r) for r in rows]}


@router.put("/exnodica/{edge_id}")
async def update_exnodica(edge_id: str, payload: ExnodicaUpdate):
    with get_db() as conn:
        if not conn.execute("SELECT id FROM exnodica WHERE id = ?", (edge_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Edge not found")
        updates, params = [], []
        if payload.relationship:
            updates.append("relationship = ?"); params.append(payload.relationship)
        if payload.relationship_confidence:
            updates.append("relationship_confidence = ?")
            params.append(payload.relationship_confidence)
        if not updates:
            raise HTTPException(status_code=422, detail="Nothing to update")
        params.append(edge_id)
        conn.execute(f"UPDATE exnodica SET {', '.join(updates)} WHERE id = ?", params)
    return {"id": edge_id, "updated": True}


@router.delete("/exnodica/{edge_id}")
async def delete_exnodica(edge_id: str):
    with get_db() as conn:
        if not conn.execute("SELECT id FROM exnodica WHERE id = ?", (edge_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Edge not found")
        conn.execute("DELETE FROM exnodica WHERE id = ?", (edge_id,))
    return {"id": edge_id, "deleted": True}
