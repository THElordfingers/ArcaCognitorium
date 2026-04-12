#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ             routers/acquiuum.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Acquiuum Chronex endpoints.

POST   /acquiuum              — ingest Involucrum (app emission)
POST   /acquiuum/nota         — ingest Nota Brevis (quick note)
POST   /acquiuum/oratio       — invoke Oratio Extracticum (conversation scour)
GET    /acquiuum              — list captures, filterable
GET    /acquiuum/{id}         — fetch single
PUT    /acquiuum/{id}/node    — Wizard manually assigns to a node
DELETE /acquiuum/{id}         — dismiss
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Any

from db import get_db, row_to_dict

router = APIRouter(tags=["acquiuum"])


class Involucrum(BaseModel):
    source_app:     str
    source_version: str = ""
    timestamp:      str = ""
    hint:           str = ""
    body:           Any = ""


class NotaBrevis(BaseModel):
    note: str
    hint: str = ""


class OratioRequest(BaseModel):
    source_paths: list[str]
    hint:         str = ""


class NodeAssignment(BaseModel):
    node_id: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _insert(conn, source_type: str, source_ref: str, raw_content: str) -> str:
    cid = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO acquiuum_chronex
            (id, source_type, source_ref, raw_content, captured_at)
        VALUES (?, ?, ?, ?, ?)
    """, (cid, source_type, source_ref, raw_content, _now()))
    return cid


@router.post("/acquiuum", status_code=201)
async def ingest_acquiuum(payload: Involucrum):
    """Ingest an app emission via Involucrum envelope."""
    content = json.dumps(payload.body) if isinstance(payload.body, (dict, list)) else str(payload.body)
    if payload.hint:
        content = f"[hint: {payload.hint}]\n\n{content}"
    with get_db() as conn:
        cid = _insert(conn, "indicatum_machina", payload.source_app, content)
    return {"id": cid, "status": "pending"}


@router.post("/acquiuum/nota", status_code=201)
async def ingest_nota(payload: NotaBrevis):
    """Ingest a quick Wizard note."""
    content = payload.note
    if payload.hint:
        content = f"[hint: {payload.hint}]\n\n{content}"
    with get_db() as conn:
        cid = _insert(conn, "nota_brevis", "wizard", content)
    return {"id": cid, "status": "pending"}


@router.post("/acquiuum/oratio", status_code=202)
async def invoke_oratio(payload: OratioRequest, background_tasks: BackgroundTasks):
    """Invoke Oratio Extracticum — scour conversation exports or files."""
    background_tasks.add_task(_run_oratio, payload.source_paths, payload.hint)
    return {"status": "accepted", "paths": payload.source_paths}


async def _run_oratio(source_paths: list[str], hint: str):
    TEXT_EXT = {".md", ".txt", ".json", ".yaml", ".yml"}
    for source_path in source_paths:
        p = Path(source_path)
        if not p.exists():
            continue
        files = [p] if p.is_file() else list(p.rglob("*"))
        for f in files:
            if f.is_file() and f.suffix.lower() in TEXT_EXT:
                try:
                    raw = f.read_text(errors="replace")
                    if len(raw.strip()) < 30:
                        continue
                    content = f"[source: {f}]\n\n{raw[:6000]}"
                    if hint:
                        content = f"[hint: {hint}]\n\n{content}"
                    with get_db() as conn:
                        _insert(conn, "oratio_extracticum", str(f), content)
                except Exception:
                    pass


@router.get("/acquiuum")
async def list_acquiuum(
    status:      Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    limit:       int           = Query(100, ge=1, le=500),
    offset:      int           = Query(0, ge=0),
):
    clauses, params = [], []
    if status:
        clauses.append("status = ?");      params.append(status)
    if source_type:
        clauses.append("source_type = ?"); params.append(source_type)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    with get_db() as conn:
        rows = conn.execute(f"""
            SELECT * FROM acquiuum_chronex {where}
            ORDER BY captured_at DESC LIMIT ? OFFSET ?
        """, params + [limit, offset]).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) FROM acquiuum_chronex {where}", params
        ).fetchone()[0]
    return {"total": total, "limit": limit, "offset": offset,
            "results": [row_to_dict(r) for r in rows]}


@router.get("/acquiuum/{capture_id}")
async def get_acquiuum(capture_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM acquiuum_chronex WHERE id = ?", (capture_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Capture not found")
    return row_to_dict(row)


@router.put("/acquiuum/{capture_id}/node")
async def assign_node(capture_id: str, payload: NodeAssignment):
    """Wizard manually assigns a capture to a Nodus Momentuum."""
    with get_db() as conn:
        cap = conn.execute(
            "SELECT id FROM acquiuum_chronex WHERE id = ?", (capture_id,)
        ).fetchone()
        if not cap:
            raise HTTPException(status_code=404, detail="Capture not found")
        node = conn.execute(
            "SELECT id FROM nodus_momentuum WHERE id = ?", (payload.node_id,)
        ).fetchone()
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        conn.execute("""
            UPDATE acquiuum_chronex
            SET inferred_node_id = ?, node_confidence = 'wizard_set',
                status = 'aggregated'
            WHERE id = ?
        """, (payload.node_id, capture_id))
        conn.execute("""
            UPDATE nodus_momentuum SET last_touched_at = ? WHERE id = ?
        """, (datetime.now(timezone.utc).isoformat(), payload.node_id))
    return {"id": capture_id, "node_id": payload.node_id, "confidence": "wizard_set"}


@router.delete("/acquiuum/{capture_id}")
async def dismiss_capture(capture_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM acquiuum_chronex WHERE id = ?", (capture_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Capture not found")
        conn.execute(
            "UPDATE acquiuum_chronex SET status = 'dismissed' WHERE id = ?",
            (capture_id,)
        )
    return {"id": capture_id, "status": "dismissed"}
