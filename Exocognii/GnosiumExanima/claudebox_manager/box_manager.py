# GNOSIUM EXANIMA — claudebox_manager/box_manager.py
# v1.0.0
"""
ClaudeBoxManager — lifecycle + streaming for the conversation instance.

The v5 rule: a ClaudeBox instance is tied to exactly one system prompt.
Any event that changes the active prompt — entity toggle in Chamber,
entity switch in Solo, mode switch, session switch — destroys the
current instance and constructs a fresh one, then reloads history via
ConversationManager.replace_history().

Streaming uses send_threaded with on_token/on_complete/on_error
callbacks. ClaudeBox itself registers on_token as a `bus.once()`
handler per call, which matches the project's established rule.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Callable, Optional

from ..session.store import MessageRow

logger = logging.getLogger("gnosium.claudebox")

# Canonical ClaudeBox import: the module lives at
# ~/ArcaCognitorium/claudebox/. Importers inject that directory onto
# sys.path at app startup via Configuus.
try:
    from claudebox import ClaudeBox, Message, Role
except ImportError:  # pragma: no cover — exercised only in broken installs
    ClaudeBox = None  # type: ignore
    Message = None    # type: ignore
    Role = None       # type: ignore


SESSION_ID = "gnosium_primary"   # internal ClaudeBox session key


def ensure_claudebox_on_path(arca_repo_path: Path) -> None:
    """Prepend the Arca repo path to sys.path so `import claudebox` resolves."""
    p = str(arca_repo_path)
    if p not in sys.path:
        sys.path.insert(0, p)


class ClaudeBoxUnavailable(RuntimeError):
    """Raised when ClaudeBox cannot be imported or constructed."""


class ClaudeBoxManager:
    """
    Owns the current ClaudeBox instance for a conversation.

    rebuild() is the only method that instantiates a new ClaudeBox. All
    other callers use send() against whichever instance is current.
    """

    def __init__(
        self,
        arca_repo_path: Path,
        *,
        api_key_env: str = "CLAUDE_API_KEY",
    ):
        ensure_claudebox_on_path(arca_repo_path)
        # Re-import after path mutation in case initial import failed
        global ClaudeBox, Message, Role
        if ClaudeBox is None:
            try:
                from claudebox import ClaudeBox as _CB, Message as _Msg, Role as _Role
                ClaudeBox, Message, Role = _CB, _Msg, _Role
            except ImportError as exc:
                raise ClaudeBoxUnavailable(
                    f"Cannot import claudebox from {arca_repo_path}: {exc}"
                ) from exc

        self._api_key_env = api_key_env
        self._box: Optional[ClaudeBox] = None
        self._system_prompt: Optional[str] = None

    # ── Lifecycle ────────────────────────────────────────────────
    def rebuild(
        self,
        system_prompt: str,
        history: Optional[list[MessageRow]] = None,
    ) -> None:
        """
        Destroy the current ClaudeBox (if any) and create a new one
        with the given system prompt. Reload history via
        conversation.replace_history().
        """
        self.teardown()

        api_key = os.environ.get(self._api_key_env)
        if not api_key:
            logger.warning(
                "%s not set — ClaudeBox will fail on send",
                self._api_key_env,
            )

        self._box = ClaudeBox(
            api_key=api_key,
            system_prompt=system_prompt,
        )
        self._system_prompt = system_prompt

        if history:
            messages = [_messagerow_to_claudebox(m) for m in history]
            self._box._conversation.replace_history(messages, session_id=SESSION_ID)

    def teardown(self) -> None:
        self._box = None
        self._system_prompt = None

    @property
    def system_prompt(self) -> Optional[str]:
        return self._system_prompt

    @property
    def is_ready(self) -> bool:
        return self._box is not None

    # ── Send ─────────────────────────────────────────────────────
    def send(
        self,
        text: str,
        *,
        on_token: Callable[[object], None],
        on_complete: Callable[[object], None],
        on_error: Callable[[Exception], None],
    ) -> None:
        """
        Send a wizard message. Streams tokens via on_token callback,
        delivers the final ClaudeResponse via on_complete, or forwards
        the exception via on_error.

        Non-blocking — returns immediately after spawning a thread.
        """
        if self._box is None:
            on_error(ClaudeBoxUnavailable("ClaudeBox has not been built"))
            return

        self._box.send_threaded(
            text,
            session_id=SESSION_ID,
            on_token=on_token,
            on_complete=on_complete,
            on_error=on_error,
        )


def _messagerow_to_claudebox(row: MessageRow) -> "Message":
    """
    Map our wire-level MessageRow to a ClaudeBox Message.

    Wizard rows -> USER. Entity rows -> ASSISTANT, with the entity
    display prefix re-embedded so the model sees the same structure
    it produced originally.
    """
    assert Message is not None and Role is not None
    if row.role == "wizard":
        return Message(role=Role.USER, content=row.content)
    return Message(role=Role.ASSISTANT, content=row.content)
