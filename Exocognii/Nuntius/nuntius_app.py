# NUNTIUS — nuntius_app.py
# v1.0
"""FastAPI application. /emit, /status, /log routes. Fan-out logic."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .nuntius_config import NuntiusConfig
from .nuntius_log import EmissionLog, EmissionRecord
from .nuntius_registry import ConsumerRegistry

logger = logging.getLogger(__name__)

# Module-level singletons — injected by __main__ before uvicorn starts
registry: ConsumerRegistry = None
emission_log: EmissionLog = None
config: NuntiusConfig = None

_start_time: float = time.monotonic()

app = FastAPI(title="NUNTIUS", version="1.0.0")


# ---------------------------------------------------------------------------
# Involucrum model
# ---------------------------------------------------------------------------

class Involucrum(BaseModel):
    source_app: str
    source_version: str
    timestamp: str
    hint: Optional[str] = None
    body: dict


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/emit", status_code=202)
async def emit(payload: Involucrum, background_tasks: BackgroundTasks) -> JSONResponse:
    """Receive Involucrum payload. Log pending. Return 202. Schedule fan-out."""
    background_tasks.add_task(
        _fan_out,
        payload.model_dump(),
        emission_log,
        registry,
        config,
    )
    return JSONResponse(status_code=202, content={"status": "accepted"})


@app.get("/status")
async def status() -> dict:
    """Return NUNTIUS health and per-consumer last delivery state."""
    uptime = int(time.monotonic() - _start_time)
    consumer_states = {row["consumer_name"]: row for row in emission_log.last_per_consumer()}

    consumers_out = []
    for c in registry.consumers:
        state = consumer_states.get(c.name, {})
        consumers_out.append(
            {
                "name": c.name,
                "url": c.url,
                "last_seen": state.get("last_seen"),
                "last_outcome": state.get("last_outcome"),
            }
        )

    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "consumers": consumers_out,
    }


@app.get("/log")
async def log(page: int = 1, limit: int = 50) -> dict:
    """Return paginated emission records. Payload field excluded."""
    limit = min(max(limit, 1), 200)
    page = max(page, 1)
    records, total = emission_log.recent(page=page, limit=limit)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "records": records,
    }


# ---------------------------------------------------------------------------
# Fan-out
# ---------------------------------------------------------------------------

async def _fan_out(
    payload: dict,
    log: EmissionLog,
    reg: ConsumerRegistry,
    cfg: NuntiusConfig,
) -> None:
    """Fan payload out to all registered consumers in parallel. Log outcomes."""
    payload_json = json.dumps(payload)
    source_app = payload.get("source_app", "unknown")
    timestamp = payload.get("timestamp", datetime.now(timezone.utc).isoformat())

    tasks = [
        _post_to_consumer(consumer, payload, cfg.consumer_timeout_seconds)
        for consumer in reg.consumers
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    records = []
    for consumer, result in zip(reg.consumers, results):
        if isinstance(result, asyncio.TimeoutError):
            outcome, status_code, error_detail = "timeout", None, "consumer timeout"
            logger.warning("NUNTIUS: consumer '%s' timed out", consumer.name)
        elif isinstance(result, Exception):
            outcome, status_code, error_detail = "error", None, str(result)
            logger.warning("NUNTIUS: consumer '%s' error: %s", consumer.name, result)
        else:
            outcome = "success"
            status_code = result.status_code
            error_detail = None
            if status_code not in (200, 201, 202, 204):
                outcome = "error"
                error_detail = f"unexpected status {status_code}"
                logger.warning(
                    "NUNTIUS: consumer '%s' returned unexpected status %d",
                    consumer.name,
                    status_code,
                )

        records.append(
            EmissionRecord(
                timestamp=timestamp,
                source_app=source_app,
                payload=payload_json,
                consumer_name=consumer.name,
                consumer_url=consumer.url,
                outcome=outcome,
                status_code=status_code,
                error_detail=error_detail,
            )
        )

    log.record(records)


async def _post_to_consumer(
    consumer,
    payload: dict,
    timeout_seconds: float,
) -> httpx.Response:
    """POST payload to one consumer. Raises on timeout or connection error."""
    async with httpx.AsyncClient() as client:
        return await asyncio.wait_for(
            client.post(consumer.url, json=payload),
            timeout=timeout_seconds,
        )
