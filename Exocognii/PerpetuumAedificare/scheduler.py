#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                         scheduler.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import asyncio
import logging
from aggrexuum import run_aggrexuum, get_aggrexuum_status

log      = logging.getLogger("scheduler")
_task    = None
_running = False


async def _loop(interval: int, threshold: int):
    global _running
    _running = True
    log.info(f"Aggrexuum scheduler started — interval:{interval}s threshold:{threshold}")
    elapsed = 0
    while _running:
        await asyncio.sleep(1)
        elapsed += 1
        if elapsed % 30 == 0:
            status = get_aggrexuum_status()
            if status["pending_count"] >= threshold:
                log.info(f"Threshold reached ({status['pending_count']}) — firing Aggrexuum")
                result = await run_aggrexuum()
                log.info(f"Aggrexuum complete: {result}")
                elapsed = 0
                continue
        if elapsed >= interval:
            status = get_aggrexuum_status()
            if status["pending_count"] > 0:
                log.info(f"Scheduled Aggrexuum — {status['pending_count']} pending")
                result = await run_aggrexuum()
                log.info(f"Aggrexuum complete: {result}")
            elapsed = 0


async def start_scheduler(cfg: dict):
    global _task
    sub       = cfg.get("perpetuum_aedificare", {})
    interval  = int(sub.get("aggrexuum_interval",  300))
    threshold = int(sub.get("aggrexuum_threshold", 10))
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
