#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ               routers/lorixii.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Lorixii Speculativum endpoints.

POST   /lorix              — ingest from Involucrum envelope
POST   /lorix/drop         — ingest a file drop
POST   /extracticus        — invoke Lorixii Extractuum scour
GET    /lorixii            — list, filterable
GET    /lorix/{id}         — fetch single
DELETE /lorix/{id}         — reject (status → rejected)
"""

import uuid
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Any

from db import get_db, row_to_dict

router = APIRouter(tags=["lorixii"])


# ─────────────────────────────────────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────────────────────────────────────

class Involucrum(BaseModel):
    source_app:     str
    source_version: str = ""
    timestamp:      str = ""
    hint:           str = ""
    body:           Any = ""


class FileDropRequest(BaseModel):
    file_path: str
    hint:      str = ""


class ExtractRequest(BaseModel):
    source_paths: list[str]
    hint:         str = ""


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _insert_lorix(conn, source_type: str, source_ref: str,
                  raw_content: str) -> str:
    lorix_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO lorixii_speculativum
            (id, source_type, source_ref, ingested_at, raw_content)
        VALUES (?, ?, ?, ?, ?)
    """, (lorix_id, source_type, source_ref, _now(), raw_content))
    return lorix_id


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/lorix", status_code=201)
async def ingest_lorix(payload: Involucrum):
    """Ingest a single Lorix from an app Involucrum envelope."""
    content = json.dumps(payload.body) if isinstance(payload.body, (dict, list)) else str(payload.body)
    if payload.hint:
        content = f"[hint: {payload.hint}]\n\n{content}"

    with get_db() as conn:
        lorix_id = _insert_lorix(
            conn,
            source_type = "app_log",
            source_ref  = payload.source_app,
            raw_content = content,
        )

    return {"id": lorix_id, "status": "pending"}


@router.post("/lorix/drop", status_code=201)
async def ingest_file_drop(payload: FileDropRequest):
    """Ingest a file the Wizard has dropped at a designated path."""
    path = Path(payload.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    try:
        raw = path.read_text(errors="replace")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read file: {e}")

    content = raw
    if payload.hint:
        content = f"[hint: {payload.hint}]\n\n{raw}"

    with get_db() as conn:
        lorix_id = _insert_lorix(
            conn,
            source_type = "file_drop",
            source_ref  = str(path),
            raw_content = content,
        )

    return {"id": lorix_id, "status": "pending", "chars_ingested": len(raw)}


@router.post("/extracticus", status_code=202)
async def invoke_extracticus(
    payload: ExtractRequest,
    background_tasks: BackgroundTasks,
):
    """
    Invoke Lorixii Extractuum — crawl source paths and ingest lore-relevant content.
    Runs as a background task. Returns immediately.
    """
    background_tasks.add_task(_run_extracticus, payload.source_paths, payload.hint)
    return {"status": "accepted", "paths": payload.source_paths}


async def _run_extracticus(source_paths: list[str], hint: str):
    """Background task — read each path and ingest as actio_extracticus."""
    TEXT_EXTENSIONS = {
        ".md", ".txt", ".py", ".json", ".yaml", ".yml", ".wiz", ".rst"
    }
    for source_path in source_paths:
        p = Path(source_path)
        if not p.exists():
            continue
        files = [p] if p.is_file() else list(p.rglob("*"))
        for f in files:
            if f.is_file() and f.suffix.lower() in TEXT_EXTENSIONS:
                try:
                    raw = f.read_text(errors="replace")
                    if len(raw.strip()) < 50:
                        continue
                    content = raw
                    if hint:
                        content = f"[hint: {hint}]\n\n{raw}"
                    with get_db() as conn:
                        _insert_lorix(
                            conn,
                            source_type = "actio_extracticus",
                            source_ref  = str(f),
                            raw_content = content[:8000],
                        )
                except Exception:
                    pass


@router.get("/lorixii")
async def list_lorixii(
    status:     Optional[str] = Query(None),
    domain:     Optional[str] = Query(None),
    confidence: Optional[str] = Query(None),
    limit:      int           = Query(100, ge=1, le=500),
    offset:     int           = Query(0, ge=0),
):
    """List Lorixii with optional filtering."""
    clauses = []
    params  = []
    if status:
        clauses.append("status = ?");     params.append(status)
    if domain:
        clauses.append("inferred_domain = ?"); params.append(domain)
    if confidence:
        clauses.append("confidence = ?"); params.append(confidence)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    params += [limit, offset]

    with get_db() as conn:
        rows = conn.execute(f"""
            SELECT * FROM lorixii_speculativum
            {where}
            ORDER BY ingested_at DESC
            LIMIT ? OFFSET ?
        """, params).fetchall()

        total = conn.execute(f"""
            SELECT COUNT(*) FROM lorixii_speculativum {where}
        """, params[:-2]).fetchone()[0]

    return {
        "total":   total,
        "limit":   limit,
        "offset":  offset,
        "results": [row_to_dict(r) for r in rows],
    }


@router.get("/lorix/{lorix_id}")
async def get_lorix(lorix_id: str):
    """Fetch a single Lorix by ID."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM lorixii_speculativum WHERE id = ?", (lorix_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Lorix not found")
    return row_to_dict(row)


@router.delete("/lorix/{lorix_id}")
async def reject_lorix(lorix_id: str):
    """Reject a Lorix — sets status to rejected. Never deleted."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, status FROM lorixii_speculativum WHERE id = ?",
            (lorix_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Lorix not found")
        if row["status"] in ("consumed", "in_judicium"):
            raise HTTPException(
                status_code=409,
                detail=f"Cannot reject a Lorix with status: {row['status']}"
            )
        conn.execute(
            "UPDATE lorixii_speculativum SET status = 'rejected' WHERE id = ?",
            (lorix_id,)
        )
    return {"id": lorix_id, "status": "rejected"}
