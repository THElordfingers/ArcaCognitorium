#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                              main.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
EXVACUA LORICUM — main.py
Lore canon memory service. FastAPI. Port 8731.

    python3 main.py
    uvicorn main:app --host 127.0.0.1 --port 8731 --reload
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db       import init_db
from config   import load_config
from scheduler import start_scheduler, stop_scheduler
from routers  import lorixii, canon, ratifex, loricuum, judicium, interpretus

cfg = load_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await start_scheduler(cfg)
    yield
    await stop_scheduler()

app = FastAPI(
    title       = "Exvacua Loricum",
    description = "Lore canon memory service — Arca Cognitorium",
    version     = "1.0.0",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["http://localhost", "http://127.0.0.1"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

app.include_router(lorixii.router)
app.include_router(canon.router)
app.include_router(ratifex.router)
app.include_router(loricuum.router)
app.include_router(judicium.router)
app.include_router(interpretus.router)


@app.get("/health")
async def health():
    return {"service": "exvacua_loricum", "status": "running", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=cfg.get("port", 8731), reload=False)
