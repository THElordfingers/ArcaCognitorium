#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                         scheduler.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Background scheduler for Actio Interpretus.
Runs on configurable heartbeat. Fires immediately when pending count
crosses the threshold. Both values live in Configuus.
"""

import asyncio
import logging
from datetime import datetime, timezone

from interpretus import run_interpretus, get_interpretus_status
from db import get_db

log = logging.getLogger("scheduler")

_task: asyncio.Task | None = None
_running = False


async def _loop(interval: int, threshold: int):
    global _running
    _running = True
    log.info(f"Actio Interpretus scheduler started — interval:{interval}s threshold:{threshold}")

    elapsed = 0
    while _running:
        await asyncio.sleep(1)
        elapsed += 1

        # Check threshold every 30s without waiting for full interval
        if elapsed % 30 == 0:
            status = get_interpretus_status()
            if status["pending_count"] >= threshold:
                log.info(f"Threshold reached ({status['pending_count']} pending) — firing Actio Interpretus")
                result = await run_interpretus()
                log.info(f"Interpretus complete: {result}")
                elapsed = 0
                continue

        if elapsed >= interval:
            status = get_interpretus_status()
            if status["pending_count"] > 0:
                log.info(f"Scheduled Actio Interpretus — {status['pending_count']} pending")
                result = await run_interpretus()
                log.info(f"Interpretus complete: {result}")
            elapsed = 0


async def start_scheduler(cfg: dict):
    global _task
    sub = cfg.get("exvacua_loricum", {})
    interval  = int(sub.get("interpretus_interval",  600))
    threshold = int(sub.get("interpretus_threshold", 20))
    _task = asyncio.create_task(_loop(interval, threshold))


async def stop_scheduler():
    global _running, _task
    _running = False
    if _task:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
