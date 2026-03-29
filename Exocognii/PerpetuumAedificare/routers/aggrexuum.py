#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ              routers/aggrexuum.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Actio Aggrexuum endpoints.

POST   /aggrexuum         — trigger manually
GET    /aggrexuum/status  — last run + pending count
"""

from fastapi import APIRouter, BackgroundTasks
from aggrexuum import run_aggrexuum, get_aggrexuum_status

router = APIRouter(tags=["aggrexuum"])


@router.post("/aggrexuum", status_code=202)
async def trigger_aggrexuum(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_aggrexuum)
    return {"status": "accepted", "message": "Actio Aggrexuum invoked"}


@router.get("/aggrexuum/status")
async def aggrexuum_status():
    return get_aggrexuum_status()
