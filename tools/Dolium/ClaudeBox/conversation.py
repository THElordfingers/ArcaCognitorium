"""
claudebox.conversation
======================
Session creation, history management, and message assembly.

Manages one or many named sessions. Each session is an independent
conversation with its own history, config overrides, and token usage.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Optional, Union

from .config import Config
from .events import EventBus, EventName
from .exceptions import (
    HistoryTruncationError,
    InvalidMessageRoleError,
    SessionAlreadyExistsError,
    SessionNotFoundError,
)
from .models import ContentBlock, Message, Role, Session, TokenUsage

logger = logging.getLogger("claudebox.conversation")


class ConversationManager:
    """
    Manages all sessions and their histories.

    Thread-safe — separate sessions can be used concurrently from
    different threads or async tasks.
    """

    def __init__(self, config: Config, bus: EventBus):
        self._config = config
        self._bus = bus
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

        # Create the default session immediately
        default_id = config.conversation.get("default_session_id", "default")
        self._default_session_id = default_id
        self._create_session_internal(default_id)

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def create_session(
        self,
        session_id: str,
        *,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> Session:
        """
        Create a new session with an optional per-session config override.

        Args:
            session_id:    Unique identifier for this session.
            system_prompt: Override the global system prompt for this session only.
            model:         Override the global model for this session only.
            max_tokens:    Override max_tokens for this session only.
            temperature:   Override temperature for this session only.
            top_p:         Override top_p for this session only.
            top_k:         Override top_k for this session only.
            metadata:      Arbitrary metadata dict attached to the session.
            overwrite:     If True, silently replace an existing session.
                           If False (default), raise SessionAlreadyExistsError.

        Returns:
            The newly created Session object.
        """
        with self._lock:
            if session_id in self._sessions and not overwrite:
                raise SessionAlreadyExistsError(
                    f"Session '{session_id}' already exists. "
                    f"Use overwrite=True or delete it first.",
                    session_id=session_id,
                )
            session = self._create_session_internal(
                session_id,
                system_prompt=system_prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                metadata=metadata or {},
            )

        self._bus.emit(EventName.SESSION_CREATED, session)
        logger.debug(f"Session created: '{session_id}'")
        return session

    def _create_session_internal(
        self,
        session_id: str,
        **kwargs,
    ) -> Session:
        session = Session(id=session_id, **kwargs)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: Optional[str] = None) -> Session:
        """
        Retrieve a session by ID.
        If session_id is None, returns the default session.
        Raises SessionNotFoundError if the session does not exist.
        """
        sid = session_id or self._default_session_id

        # Auto-create default session if it was somehow removed
        if sid == self._default_session_id and sid not in self._sessions:
            self._create_session_internal(sid)

        multi_session = self._config.conversation.get("multi_session", True)
        if not multi_session:
            # In single-session mode, always return the default session
            return self._sessions[self._default_session_id]

        with self._lock:
            session = self._sessions.get(sid)
        if session is None:
            raise SessionNotFoundError(
                f"Session '{sid}' not found. Create it first with create_session().",
                session_id=sid,
            )
        return session

    def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        """Get a session by ID, creating it automatically if it doesn't exist."""
        sid = session_id or self._default_session_id
        with self._lock:
            if sid not in self._sessions:
                session = self._create_session_internal(sid)
                self._bus.emit(EventName.SESSION_CREATED, session)
                return session
            return self._sessions[sid]

    def delete_session(self, session_id: str) -> None:
        """
        Delete a session and its history.
        Cannot delete the default session — clear it instead.
        """
        if session_id == self._default_session_id:
            self.clear_history(session_id)
            return

        with self._lock:
            if session_id not in self._sessions:
                raise SessionNotFoundError(
                    f"Session '{session_id}' not found.",
                    session_id=session_id,
                )
            del self._sessions[session_id]

        self._bus.emit(EventName.SESSION_DELETED, session_id)
        logger.debug(f"Session deleted: '{session_id}'")

    def list_sessions(self) -> list[str]:
        """Return a list of all active session IDs."""
        with self._lock:
            return list(self._sessions.keys())

    def session_exists(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._sessions

    # ------------------------------------------------------------------
    # History management
    # ------------------------------------------------------------------

    def add_user_message(
        self,
        content: Union[str, list[ContentBlock]],
        session_id: Optional[str] = None,
    ) -> Message:
        """Add a user message to a session's history."""
        session = self.get_or_create_session(session_id)
        message = Message(role=Role.USER, content=content)
        self._append_message(session, message)
        return message

    def add_assistant_message(
        self,
        content: Union[str, list[ContentBlock]],
        session_id: Optional[str] = None,
    ) -> Message:
        """Add an assistant message to a session's history."""
        session = self.get_or_create_session(session_id)
        message = Message(role=Role.ASSISTANT, content=content)
        self._append_message(session, message)
        return message

    def add_message(
        self,
        role: Union[Role, str],
        content: Union[str, list[ContentBlock]],
        session_id: Optional[str] = None,
    ) -> Message:
        """Add any message with explicit role to a session's history."""
        if isinstance(role, str) and role not in (r.value for r in Role):
            raise InvalidMessageRoleError(
                f"Invalid message role: '{role}'. Must be 'user' or 'assistant'.",
                role=role,
            )
        session = self.get_or_create_session(session_id)
        message = Message(role=role, content=content)
        self._append_message(session, message)
        return message

    def _append_message(self, session: Session, message: Message) -> None:
        session.add_message(message)
        self._maybe_truncate(session)

    def clear_history(self, session_id: Optional[str] = None) -> None:
        """Clear all messages from a session's history."""
        session = self.get_or_create_session(session_id)
        session.clear_history()
        self._bus.emit(EventName.SESSION_CLEARED, session.id)
        logger.debug(f"History cleared for session '{session.id}'")

    def get_history(self, session_id: Optional[str] = None) -> list[Message]:
        """Return the current message history for a session."""
        session = self.get_or_create_session(session_id)
        return list(session.history)

    def get_history_as_dicts(self, session_id: Optional[str] = None) -> list[dict]:
        """Return history serialized as API-compatible dicts."""
        messages = self.get_history(session_id)
        return [m.to_api_dict() for m in messages]

    def replace_history(
        self,
        messages: list[Message],
        session_id: Optional[str] = None,
    ) -> None:
        """Replace a session's entire history with the provided messages."""
        session = self.get_or_create_session(session_id)
        session.history.clear()
        for msg in messages:
            session.add_message(msg)

    # ------------------------------------------------------------------
    # Truncation
    # ------------------------------------------------------------------

    def _maybe_truncate(self, session: Session) -> None:
        max_messages = self._config.conversation.get("max_history_messages")
        if max_messages is None:
            return

        if len(session.history) <= max_messages:
            return

        strategy = self._config.conversation.get("truncation_strategy", "drop_oldest")

        if strategy == "error":
            raise HistoryTruncationError(
                f"Session '{session.id}' has reached max_history_messages={max_messages}. "
                f"Clear history or increase the limit."
            )

        if strategy == "drop_oldest":
            # Drop oldest pairs (user + assistant) to get back under the limit
            while len(session.history) > max_messages:
                # Always drop in user+assistant pairs to maintain alternating structure
                removed = session.history.pop(0)
                logger.debug(f"Truncated oldest message from session '{session.id}': {removed.role}")
            self._bus.emit(EventName.HISTORY_TRUNCATED, {
                "session_id": session.id,
                "current_count": len(session.history),
                "max": max_messages,
            })

    # ------------------------------------------------------------------
    # Message assembly — builds the final messages list for an API call
    # ------------------------------------------------------------------

    def build_messages(
        self,
        session_id: Optional[str] = None,
        prefill: Optional[str] = None,
    ) -> list[dict]:
        """
        Build the final messages list to send to the API.

        Includes the full session history plus an optional assistant prefill.
        Returns a list of API-compatible message dicts.
        """
        history_dicts = self.get_history_as_dicts(session_id)

        if prefill is not None:
            history_dicts.append({"role": "assistant", "content": prefill})

        return history_dicts

    def build_system_prompt(self, session_id: Optional[str] = None) -> Optional[str]:
        """
        Resolve the effective system prompt for a session.

        Priority:
            1. Session-level override
            2. Config-level default
        """
        session = self.get_or_create_session(session_id)
        if session.system_prompt is not None:
            return session.system_prompt
        return self._config.system.get("prompt")

    # ------------------------------------------------------------------
    # Token usage recording
    # ------------------------------------------------------------------

    def record_usage(
        self,
        usage: TokenUsage,
        session_id: Optional[str] = None,
    ) -> None:
        """Record token usage for a session."""
        session = self.get_or_create_session(session_id)
        session.token_usage.record(usage)

    def get_usage(self, session_id: Optional[str] = None) -> TokenUsage:
        """Get cumulative token usage for a session."""
        session = self.get_or_create_session(session_id)
        return session.token_usage.total

    def get_all_usage(self) -> dict[str, TokenUsage]:
        """Get cumulative token usage for all sessions."""
        with self._lock:
            return {sid: s.token_usage.total for sid, s in self._sessions.items()}

    # ------------------------------------------------------------------
    # Session config resolution
    # ------------------------------------------------------------------

    def resolve_param(
        self,
        param_name: str,
        request_value: Any,
        session_id: Optional[str] = None,
    ) -> Any:
        """
        Resolve the effective value of a parameter using priority order:
            request > session > config > None

        Args:
            param_name:    The parameter name (e.g. 'model', 'temperature').
            request_value: The value passed in the request (may be None).
            session_id:    The session to check for session-level overrides.
        """
        if request_value is not None:
            return request_value

        try:
            session = self.get_session(session_id)
            session_val = getattr(session, param_name, None)
            if session_val is not None:
                return session_val
        except SessionNotFoundError:
            pass

        # Fall back to config
        return self._config.model.get(param_name)

    # ------------------------------------------------------------------
    # Auto-clear
    # ------------------------------------------------------------------

    def maybe_auto_clear(self, session_id: Optional[str] = None) -> None:
        """Clear history after a turn if auto_clear_after_turn is enabled."""
        if self._config.conversation.get("auto_clear_after_turn", False):
            self.clear_history(session_id)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        with self._lock:
            count = len(self._sessions)
        return f"ConversationManager(sessions={count}, default='{self._default_session_id}')"
