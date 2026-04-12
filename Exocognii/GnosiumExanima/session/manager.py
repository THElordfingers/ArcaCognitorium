# GNOSIUM EXANIMA — session/manager.py
# v1.0.0
"""
Session manager — orchestrates the SessionStore with business rules.

One current session per mode. Switching destroys the ClaudeBox,
rebuilds it with the new session's prompt, and reloads history.
"""

from __future__ import annotations

from typing import Optional

from .store import SessionRow, SessionStore
from ..constants import MODE_CHAMBER, MODE_SOLO


TITLE_LIMIT = 60


class SessionManager:
    def __init__(self, store: SessionStore):
        self._store = store

    # ── Lifecycle ────────────────────────────────────────────────
    def get_or_create_current(
        self,
        mode: str,
        active_entities: list[str],
    ) -> SessionRow:
        current = self._store.current_session(mode)
        if current:
            # Update entity roster if caller changed it
            if current.active_entities != active_entities:
                self._store.update_session(
                    current.id, active_entities=active_entities,
                )
                current.active_entities = list(active_entities)
            return current
        return self._store.create_session(mode, active_entities)

    def new_session(self, mode: str, active_entities: list[str]) -> SessionRow:
        return self._store.create_session(mode, active_entities)

    def switch_to(self, session_id: str) -> Optional[SessionRow]:
        row = self._store.get_session(session_id)
        if row is None:
            return None
        self._store.set_current_session(session_id, row.mode)
        row.is_current = True
        return row

    def delete(self, session_id: str) -> None:
        self._store.delete_session(session_id)

    def list_for_mode(self, mode: str) -> list[SessionRow]:
        return self._store.list_sessions(mode)

    # ── Auto-titling ─────────────────────────────────────────────
    def apply_auto_title_if_needed(
        self,
        session: SessionRow,
        first_wizard_message: str,
    ) -> Optional[str]:
        """
        If the session has no title, set one from the first wizard
        message (first 60 chars). Returns the new title or None if
        a title was already present.
        """
        if session.title:
            return None
        snippet = first_wizard_message.strip().replace("\n", " ")
        if len(snippet) > TITLE_LIMIT:
            snippet = snippet[:TITLE_LIMIT - 1].rstrip() + "…"
        if not snippet:
            return None
        self._store.update_session(session.id, title=snippet)
        session.title = snippet
        return snippet
