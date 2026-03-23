#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / app.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import os
import sys
from pathlib import Path

from textual.app import App

import prompts as _prompts
from store import IdeaStore
from ui.layout import ChainScreen

# Absolute path — works regardless of working directory
_HERE = Path(__file__).parent.resolve()


class DoliumApp(App):
    """
    The Dolium — Idea Fruition Chain.
    No custom __init__ — reads all config from environment variables
    in on_mount to avoid Textual version compatibility issues.

    Environment variables:
        CLAUDE_API_KEY   — API key for ClaudeBox
        DOLIUM_CONTEXT_FILE — path to live CONTEXT.md from AC repo
        DOLIUM_STORAGE_DIR  — override default storage/ directory
        DOLIUM_REPO_PATH    — path to AC repo root for /attach commands
    """

    CSS_PATH = str(_HERE / "dolium.tcss")

    def on_mount(self) -> None:
        api_key     = os.environ.get("CLAUDE_API_KEY", "")
        storage_dir = Path(
            os.environ.get("DOLIUM_STORAGE_DIR", "")
            or _HERE / "storage"
        )
        repo_path = os.environ.get("DOLIUM_REPO_PATH", "")
        context   = self._load_context(os.environ.get("DOLIUM_CONTEXT_FILE"))

        if context:
            _prompts.set_context(context)

        store = IdeaStore(storage_dir)
        box   = self._build_box(api_key)
        self.push_screen(ChainScreen(
            store     = store,
            box       = box,
            repo_path = repo_path or None,
        ))

    # ── Private ───────────────────────────────────────────────────────────────

    def _build_box(self, api_key: str) -> object:
        try:
            from claudebox import ClaudeBox
            box = ClaudeBox(api_key=api_key)
            print(f"[dolium] ClaudeBox initialised OK", file=sys.stderr)
            return box
        except ImportError as e:
            print(f"[dolium] ClaudeBox import failed: {e}", file=sys.stderr)
            return _StubBox()
        except Exception as e:
            print(f"[dolium] ClaudeBox init failed: {type(e).__name__}: {e}", file=sys.stderr)
            return _StubBox()

    @staticmethod
    def _load_context(path_str: str | None) -> str | None:
        if not path_str:
            return None
        path = Path(path_str).expanduser().resolve()
        if not path.exists():
            print(
                f"[dolium] Warning: DOLIUM_CONTEXT_FILE={path_str!r} not found. "
                f"Using static context.",
                file=sys.stderr,
            )
            return None
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                print(f"[dolium] Context loaded from {path}", file=sys.stderr)
            return text or None
        except Exception as e:
            print(f"[dolium] Warning: could not read context file: {e}", file=sys.stderr)
            return None


# ── StubBox ───────────────────────────────────────────────────────────────────

class _StubBox:
    """Fallback when claudebox is not installed or API key is absent."""

    def stream_response_text(self, messages: list, system: str = "", **kwargs) -> str:
        return (
            "ClaudeBox is not available. "
            "Install the claudebox package and set CLAUDE_API_KEY "
            "to enable conversation."
        )
