#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                   routers/arca.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Arca Absoluticum — Tower reference layer.
Read-only Tower references attached to Nodi. Never writes to Tower storage.

POST   /nodus/{id}/arca           — attach reference
DELETE /nodus/{id}/arca/{ref_id}  — detach reference
"""

import json
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import get_db, row_to_dict

router = APIRouter(tags=["arca"])


class ArcaRef(BaseModel):
    type: str   # "FOLIUM" | "FILUM" | "grimoire_snapshot"
    id:   str


@router.post("/nodus/{node_id}/arca", status_code=201)
async def attach_arca(node_id: str, payload: ArcaRef):
    with get_db() as conn:
        row = conn.execute(
            "SELECT arca_absoluta FROM nodus_momentuum WHERE id = ?", (node_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Node not found")
        refs = json.loads(row["arca_absoluta"] or "[]")
        ref_id = str(uuid.uuid4())
        refs.append({"ref_id": ref_id, "type": payload.type, "id": payload.id})
        conn.execute(
            "UPDATE nodus_momentuum SET arca_absoluta = ? WHERE id = ?",
            (json.dumps(refs), node_id)
        )
    return {"node_id": node_id, "ref_id": ref_id, "type": payload.type}


@router.delete("/nodus/{node_id}/arca/{ref_id}")
async def detach_arca(node_id: str, ref_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT arca_absoluta FROM nodus_momentuum WHERE id = ?", (node_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Node not found")
        refs = json.loads(row["arca_absoluta"] or "[]")
        new_refs = [r for r in refs if r.get("ref_id") != ref_id]
        if len(new_refs) == len(refs):
            raise HTTPException(status_code=404, detail="Reference not found")
        conn.execute(
            "UPDATE nodus_momentuum SET arca_absoluta = ? WHERE id = ?",
            (json.dumps(new_refs), node_id)
        )
    return {"node_id": node_id, "ref_id": ref_id, "detached": True}
