#!/usr/bin/env python3
"""
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
⯨  ARCANUM BRIDGE  ⯩         𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
#
##  mcp_bridge_server.py
###
####  FastAPI server bridging Claude mobile → Anthropic API
#####   with MCP filesystem access to ~/ArcaCognitorium/
######
"""

import os
import json
import asyncio
import secrets
import subprocess
import tempfile
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import anthropic
import uvicorn

# ── Configuration ────────────────────────────────────────────────
ARCANUM_PATH   = str(Path.home() / "ArcaCognitorium")
BRIDGE_API_KEY = os.environ.get("BRIDGE_API_KEY", "")
CLAUDE_KEY  = os.environ.get("CLAUDE_API_KEY", "")
HOST           = "0.0.0.0"
PORT           = int(os.environ.get("BRIDGE_PORT", "7432"))
MODEL          = "claude-sonnet-4-20250514"

if not BRIDGE_API_KEY:
    raise RuntimeError("BRIDGE_API_KEY env var not set. Refusing to start unguarded.")
if not CLAUDE_KEY:
    raise RuntimeError("CLAUDE_API_KEY env var not set.")

# ── App ──────────────────────────────────────────────────────────
app = FastAPI(title="Arcanum Bridge", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-Bridge-Key", auto_error=False)

async def require_key(key: str = Depends(api_key_header)):
    if not key or not secrets.compare_digest(key, BRIDGE_API_KEY):
        raise HTTPException(status_code=401, detail="Nulla auctoritas.")
    return key

# ── Models ───────────────────────────────────────────────────────
class Message(BaseModel):
    role: str          # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    system: str | None = None
    stream: bool = True

# ── MCP server subprocess management ────────────────────────────
_mcp_proc: subprocess.Popen | None = None
_mcp_lock = asyncio.Lock()

def get_mcp_server_path() -> str | None:
    """Find npx or the MCP filesystem server."""
    for cmd in ["npx", "/usr/local/bin/npx", str(Path.home() / ".npm-global/bin/npx")]:
        if Path(cmd).exists() or cmd == "npx":
            return cmd
    return None

# ── MCP tool definitions (filesystem) ───────────────────────────
# We declare these manually so Anthropic API can call them;
# calls are forwarded to the MCP subprocess via JSON-RPC stdio.

MCP_TOOLS = [
    {
        "name": "filesystem_read_file",
        "description": "Read the complete contents of a file from ~/ArcaCognitorium/",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute or relative path to file"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "filesystem_write_file",
        "description": "Write content to a file in ~/ArcaCognitorium/",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "filesystem_list_directory",
        "description": "List contents of a directory under ~/ArcaCognitorium/",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "filesystem_search_files",
        "description": "Search for files matching a pattern under ~/ArcaCognitorium/",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "pattern": {"type": "string"}
            },
            "required": ["path", "pattern"]
        }
    },
    {
        "name": "filesystem_get_file_info",
        "description": "Get metadata (size, modified time, type) for a file or directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "filesystem_create_directory",
        "description": "Create a directory under ~/ArcaCognitorium/",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "filesystem_move_file",
        "description": "Move or rename a file/directory within ~/ArcaCognitorium/",
        "input_schema": {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "destination": {"type": "string"}
            },
            "required": ["source", "destination"]
        }
    },
    {
        "name": "filesystem_delete_file",
        "description": "Delete a file or empty directory within ~/ArcaCognitorium/",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
]

def _safe_path(raw: str) -> Path:
    """Resolve and jail path to ARCANUM_PATH."""
    base = Path(ARCANUM_PATH).resolve()
    target = (base / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
    if not str(target).startswith(str(base)):
        raise PermissionError(f"Path escape attempt: {raw}")
    return target

def execute_fs_tool(name: str, args: dict) -> str:
    """Execute filesystem tool calls directly (no subprocess needed)."""
    try:
        if name == "filesystem_read_file":
            p = _safe_path(args["path"])
            return p.read_text(encoding="utf-8", errors="replace")

        elif name == "filesystem_write_file":
            p = _safe_path(args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"], encoding="utf-8")
            return f"Written: {p}"

        elif name == "filesystem_list_directory":
            p = _safe_path(args["path"])
            entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
            lines = []
            for e in entries:
                icon = "📁" if e.is_dir() else "📄"
                lines.append(f"{icon} {e.name}")
            return "\n".join(lines) if lines else "(empty)"

        elif name == "filesystem_search_files":
            base = _safe_path(args["path"])
            pattern = args["pattern"]
            matches = list(base.rglob(pattern))
            return "\n".join(str(m.relative_to(Path(ARCANUM_PATH))) for m in matches[:100])

        elif name == "filesystem_get_file_info":
            p = _safe_path(args["path"])
            stat = p.stat()
            import datetime
            return json.dumps({
                "path": str(p),
                "type": "directory" if p.is_dir() else "file",
                "size_bytes": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }, indent=2)

        elif name == "filesystem_create_directory":
            p = _safe_path(args["path"])
            p.mkdir(parents=True, exist_ok=True)
            return f"Created: {p}"

        elif name == "filesystem_move_file":
            src = _safe_path(args["source"])
            dst = _safe_path(args["destination"])
            src.rename(dst)
            return f"Moved: {src} → {dst}"

        elif name == "filesystem_delete_file":
            p = _safe_path(args["path"])
            if p.is_dir():
                p.rmdir()
            else:
                p.unlink()
            return f"Deleted: {p}"

        else:
            return f"Unknown tool: {name}"

    except PermissionError as e:
        return f"⛔ Forbidden: {e}"
    except Exception as e:
        return f"⚠ Error: {e}"

# ── Core agentic chat loop ────────────────────────────────────────
async def run_agentic_chat(
    messages: list[dict],
    system: str | None,
) -> AsyncGenerator[str, None]:
    """
    Agentic loop: keep calling Claude until no more tool_use blocks.
    Yields SSE-formatted strings.
    """
    client = anthropic.Anthropic(api_key=CLAUDE_KEY)

    sys_prompt = system or (
        f"You are the Arcanum Bridge — Claude operating with filesystem access "
        f"to the ArcaCognitorium project vault at {ARCANUM_PATH}. "
        f"You can read, write, list, search, and manage files there. "
        f"Be precise, thorough, and speak with the gravity befitting a grimoire-keeper."
    )

    loop_messages = list(messages)

    while True:
        # Streaming call
        full_text = ""
        tool_uses = []
        stop_reason = None

        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            system=sys_prompt,
            messages=loop_messages,
            tools=MCP_TOOLS,
        ) as stream:
            for event in stream:
                if hasattr(event, "type"):
                    if event.type == "content_block_delta":
                        delta = event.delta
                        if hasattr(delta, "text"):
                            full_text += delta.text
                            yield f"data: {json.dumps({'type': 'text', 'text': delta.text})}\n\n"
                    elif event.type == "message_delta":
                        if hasattr(event.delta, "stop_reason"):
                            stop_reason = event.delta.stop_reason

            # Collect tool use blocks from the final message
            final_msg = stream.get_final_message()
            stop_reason = final_msg.stop_reason
            for block in final_msg.content:
                if block.type == "tool_use":
                    tool_uses.append(block)

        if stop_reason != "tool_use" or not tool_uses:
            break

        # Execute tools and loop back
        assistant_content = []
        if full_text:
            assistant_content.append({"type": "text", "text": full_text})
        for tu in tool_uses:
            assistant_content.append({
                "type": "tool_use",
                "id": tu.id,
                "name": tu.name,
                "input": tu.input,
            })

        loop_messages.append({"role": "assistant", "content": assistant_content})

        tool_results = []
        for tu in tool_uses:
            yield f"data: {json.dumps({'type': 'tool_call', 'name': tu.name, 'input': tu.input})}\n\n"
            result = execute_fs_tool(tu.name, tu.input)
            yield f"data: {json.dumps({'type': 'tool_result', 'name': tu.name, 'result': result[:500]})}\n\n"
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result,
            })

        loop_messages.append({"role": "user", "content": tool_results})

    yield f"data: {json.dumps({'type': 'done'})}\n\n"

# ── Routes ───────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h2>⯨ Arcanum Bridge ⯩</h2><p>Porta aperta.</p>"

@app.get("/status", dependencies=[Depends(require_key)])
async def status():
    arcanum_exists = Path(ARCANUM_PATH).exists()
    return {
        "status": "operans",
        "arcanum_path": ARCANUM_PATH,
        "arcanum_accessible": arcanum_exists,
        "model": MODEL,
    }

@app.post("/chat", dependencies=[Depends(require_key)])
async def chat(req: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    if req.stream:
        return StreamingResponse(
            run_agentic_chat(messages, req.system),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    else:
        # Collect full response non-streaming
        chunks = []
        async for chunk in run_agentic_chat(messages, req.system):
            if chunk.startswith("data: "):
                data = json.loads(chunk[6:])
                if data.get("type") == "text":
                    chunks.append(data["text"])
        return {"response": "".join(chunks)}

# ── Entry ────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"""
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
⯨  ARCANUM BRIDGE  ⯩         𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
  Vault  : {ARCANUM_PATH}
  Listen : {HOST}:{PORT}
  Model  : {MODEL}
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
""")
    uvicorn.run(app, host=HOST, port=PORT)
