#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ           routers/interpretus.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Actio Interpretus endpoints.

POST   /interpretus         — trigger pass manually
GET    /interpretus/status  — last run + pending count
"""

from fastapi import APIRouter, BackgroundTasks
from interpretus import run_interpretus, get_interpretus_status

router = APIRouter(tags=["interpretus"])


@router.post("/interpretus", status_code=202)
async def trigger_interpretus(background_tasks: BackgroundTasks):
    """Manually trigger an Actio Interpretus pass. Runs as background task."""
    background_tasks.add_task(run_interpretus)
    return {"status": "accepted", "message": "Actio Interpretus invoked"}


@router.get("/interpretus/status")
async def interpretus_status():
    return get_interpretus_status()
