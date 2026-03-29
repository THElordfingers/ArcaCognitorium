#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                              main.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
PERPETUUM AEDIFICARE — main.py
Build continuity memory service. FastAPI. Port 8732.

    python3 main.py
    uvicorn main:app --host 127.0.0.1 --port 8732 --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db        import init_db
from config    import load_config
from scheduler import start_scheduler, stop_scheduler
from routers   import acquiuum, nodi, exnodica, arca, aggrexuum

cfg = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await start_scheduler(cfg)
    yield
    await stop_scheduler()


app = FastAPI(
    title       = "Perpetuum Aedificare",
    description = "Build continuity memory service — Arca Cognitorium",
    version     = "1.0.0",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost", "http://127.0.0.1"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.include_router(acquiuum.router)
app.include_router(nodi.router)
app.include_router(exnodica.router)
app.include_router(arca.router)
app.include_router(aggrexuum.router)


@app.get("/health")
async def health():
    return {"service": "perpetuum_aedificare", "status": "running", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=cfg.get("port", 8732), reload=False)
