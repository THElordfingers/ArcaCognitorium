"""
claudebox.events
================
The event bus — every output port on the ClaudeBox surface.

Every significant thing that happens inside the box fires an event.
The outer machine subscribes to events it cares about. Everything else is ignored.

SUBSCRIBING:
    box.on("token", my_handler)          # subscribe
    box.on_token(my_handler)             # shorthand alias
    box.off("token", my_handler)         # unsubscribe
    box.once("response", my_handler)     # fire once then auto-unsubscribe

EMITTING (internal use):
    bus.emit("token", StreamToken(...))

HANDLER SIGNATURES:
    All handlers receive a single argument: the event payload dataclass.
    Handlers may be sync or async. Async handlers are awaited if a running
    event loop is detected, otherwise they are scheduled via threading.

EVENT CATALOGUE:
    See EventName enum below for every possible event name and its payload type.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Any, Callable, Optional

from .exceptions import EventHandlerError, UnknownEventError

logger = logging.getLogger("claudebox.events")


# ---------------------------------------------------------------------------
# Event names — canonical list of every event the bus can emit
# ---------------------------------------------------------------------------

class EventName(str, Enum):
    # --- Lifecycle ---
    BOX_INITIALIZED = "box_initialized"         # ClaudeBox fully initialized
    BOX_CLOSED = "box_closed"                   # ClaudeBox closed/cleaned up

    # --- Request lifecycle ---
    REQUEST_START = "request_start"             # About to send a request
    REQUEST_END = "request_end"                 # Request completed (success or error)

    # --- Response ---
    RESPONSE = "response"                       # Full ClaudeResponse received
    TEXT = "text"                               # Complete text of a response
    TOKEN = "token"                             # Single streaming token (StreamToken)
    THINKING_TOKEN = "thinking_token"           # Single thinking token (StreamThinkingToken)
    THINKING = "thinking"                       # Complete thinking block text

    # --- Streaming ---
    STREAM_START = "stream_start"               # Stream opened
    STREAM_END = "stream_end"                   # Stream closed (StreamComplete)
    STREAM_EVENT = "stream_event"               # Raw SSE event (StreamEvent) — if yield_raw_events
    STREAM_ERROR = "stream_error"               # Error during streaming

    # --- Tools ---
    TOOL_CALL = "tool_call"                     # Claude is calling a tool (ToolCall)
    TOOL_RESULT = "tool_result"                 # Tool execution result (ToolResult)
    TOOL_ERROR = "tool_error"                   # Tool execution failed
    TOOL_REGISTERED = "tool_registered"         # A tool was registered
    TOOL_UNREGISTERED = "tool_unregistered"     # A tool was unregistered

    # --- Sessions ---
    SESSION_CREATED = "session_created"         # New session created (Session)
    SESSION_CLEARED = "session_cleared"         # Session history cleared
    SESSION_DELETED = "session_deleted"         # Session deleted
    HISTORY_TRUNCATED = "history_truncated"     # History truncation occurred

    # --- Token usage ---
    TOKEN_USAGE = "token_usage"                 # Token usage after a request (TokenUsage)

    # --- Batches ---
    BATCH_CREATED = "batch_created"             # Batch submitted (BatchStatus)
    BATCH_COMPLETE = "batch_complete"           # Batch finished (BatchStatus)
    BATCH_RESULT = "batch_result"               # Individual batch result (BatchResult)
    BATCH_POLL = "batch_poll"                   # Batch poll tick (BatchStatus)

    # --- Files ---
    FILE_UPLOADED = "file_uploaded"             # File uploaded (UploadedFile)
    FILE_DELETED = "file_deleted"               # File deleted

    # --- Config ---
    CONFIG_LOADED = "config_loaded"             # Config loaded or reloaded
    CONFIG_RELOADED = "config_reloaded"         # Config hot-reloaded

    # --- Errors ---
    ERROR = "error"                             # Any ClaudeBoxError (catch-all)
    API_ERROR = "api_error"                     # API-specific errors
    RATE_LIMIT = "rate_limit"                   # Rate limit hit (with retry info)

    # --- Raw ---
    RAW_REQUEST = "raw_request"                 # Raw API request params (if log_requests)
    RAW_RESPONSE = "raw_response"               # Raw API response object (if log_responses)


# All known event name strings — for validation
_ALL_EVENT_NAMES = {e.value for e in EventName}


# ---------------------------------------------------------------------------
# Handler type
# ---------------------------------------------------------------------------

Handler = Callable[[Any], Any]


# ---------------------------------------------------------------------------
# Event Bus
# ---------------------------------------------------------------------------

class EventBus:
    """
    Central event dispatcher for a ClaudeBox instance.

    Thread-safe. Supports sync and async handlers.
    Supports one-shot (once) subscriptions.
    Supports wildcard subscription via EventName.ERROR as catch-all.
    """

    def __init__(
        self,
        enabled: bool = True,
        async_handlers: bool = False,
        thread_pool_size: int = 4,
        suppress_handler_errors: bool = True,
        allow_unknown_events: bool = False,
    ):
        self._enabled = enabled
        self._async_handlers = async_handlers
        self._suppress_handler_errors = suppress_handler_errors
        self._allow_unknown_events = allow_unknown_events

        # event_name -> list of (handler, is_once)
        self._handlers: dict[str, list[tuple[Handler, bool]]] = defaultdict(list)
        self._lock = threading.Lock()

        self._executor: Optional[ThreadPoolExecutor] = None
        if async_handlers:
            self._executor = ThreadPoolExecutor(
                max_workers=thread_pool_size,
                thread_name_prefix="claudebox-event",
            )

    # ------------------------------------------------------------------
    # Subscribe
    # ------------------------------------------------------------------

    def on(self, event: str, handler: Handler) -> "EventBus":
        """Subscribe a handler to an event. Returns self for chaining."""
        self._validate_event(event)
        with self._lock:
            self._handlers[event].append((handler, False))
        logger.debug(f"Handler registered for '{event}': {handler.__name__ if hasattr(handler, '__name__') else handler}")
        return self

    def once(self, event: str, handler: Handler) -> "EventBus":
        """Subscribe a handler that fires exactly once then auto-unsubscribes."""
        self._validate_event(event)
        with self._lock:
            self._handlers[event].append((handler, True))
        return self

    def off(self, event: str, handler: Handler) -> "EventBus":
        """Unsubscribe a handler from an event."""
        with self._lock:
            handlers = self._handlers.get(event, [])
            self._handlers[event] = [(h, o) for h, o in handlers if h is not handler]
        return self

    def off_all(self, event: Optional[str] = None) -> "EventBus":
        """Remove all handlers for an event, or all handlers for all events."""
        with self._lock:
            if event is not None:
                self._handlers[event] = []
            else:
                self._handlers.clear()
        return self

    def listeners(self, event: str) -> list[Handler]:
        """Return a list of all handlers currently subscribed to an event."""
        with self._lock:
            return [h for h, _ in self._handlers.get(event, [])]

    def event_names(self) -> list[str]:
        """Return all event names that have at least one subscriber."""
        with self._lock:
            return [name for name, handlers in self._handlers.items() if handlers]

    # ------------------------------------------------------------------
    # Emit
    # ------------------------------------------------------------------

    def emit(self, event: str, payload: Any = None) -> None:
        """
        Fire an event synchronously. All handlers are called in subscription order.
        One-shot handlers are removed after firing.
        """
        if not self._enabled:
            return

        self._validate_event(event)

        with self._lock:
            handlers = list(self._handlers.get(event, []))
            # Remove one-shot handlers
            self._handlers[event] = [(h, o) for h, o in handlers if not o]

        if not handlers:
            return

        logger.debug(f"Emitting '{event}' to {len(handlers)} handler(s)")

        for handler, _ in handlers:
            self._dispatch(event, handler, payload)

    async def emit_async(self, event: str, payload: Any = None) -> None:
        """
        Fire an event asynchronously. Awaits async handlers,
        calls sync handlers normally.
        """
        if not self._enabled:
            return

        self._validate_event(event)

        with self._lock:
            handlers = list(self._handlers.get(event, []))
            self._handlers[event] = [(h, o) for h, o in handlers if not o]

        if not handlers:
            return

        for handler, _ in handlers:
            await self._dispatch_async(event, handler, payload)

    # ------------------------------------------------------------------
    # Internal dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, event: str, handler: Handler, payload: Any) -> None:
        if self._async_handlers and self._executor:
            self._executor.submit(self._call_handler, event, handler, payload)
        else:
            self._call_handler(event, handler, payload)

    async def _dispatch_async(self, event: str, handler: Handler, payload: Any) -> None:
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(payload)
            else:
                handler(payload)
        except Exception as e:
            self._handle_handler_error(event, handler, e)

    def _call_handler(self, event: str, handler: Handler, payload: Any) -> None:
        try:
            if asyncio.iscoroutinefunction(handler):
                # Async handler called from sync context — schedule it
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(handler(payload), loop)
                    else:
                        loop.run_until_complete(handler(payload))
                except RuntimeError:
                    asyncio.run(handler(payload))
            else:
                handler(payload)
        except Exception as e:
            self._handle_handler_error(event, handler, e)

    def _handle_handler_error(self, event: str, handler: Handler, exc: Exception) -> None:
        handler_name = getattr(handler, "__name__", repr(handler))
        msg = f"Event handler error in '{event}' handler '{handler_name}': {exc}"
        if self._suppress_handler_errors:
            logger.error(msg, exc_info=exc)
        else:
            raise EventHandlerError(msg, event_name=event, cause=exc)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_event(self, event: str) -> None:
        if not self._allow_unknown_events and event not in _ALL_EVENT_NAMES:
            raise UnknownEventError(
                f"Unknown event name: '{event}'. "
                f"Set events.allow_unknown_events=true in config to allow custom events.",
                event_name=event,
            )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Shut down the event bus and thread pool."""
        if self._executor:
            self._executor.shutdown(wait=True)
        self.off_all()

    def __repr__(self) -> str:
        subscribed = len([n for n, h in self._handlers.items() if h])
        return f"EventBus(enabled={self._enabled}, subscribed_events={subscribed})"


# ---------------------------------------------------------------------------
# Shorthand method mixin — generates on_<event> methods for all EventNames
# ---------------------------------------------------------------------------

class EventMixin:
    """
    Mixin that generates on_<event_name>() shorthand subscription methods
    for every event in the EventName enum.

    Example:
        box.on_token(handler)     # same as box.on("token", handler)
        box.on_response(handler)  # same as box.on("response", handler)
    """

    _bus: EventBus  # must be set by the host class

    def on(self, event: str, handler: Handler) -> "EventMixin":
        self._bus.on(event, handler)
        return self

    def once(self, event: str, handler: Handler) -> "EventMixin":
        self._bus.once(event, handler)
        return self

    def off(self, event: str, handler: Handler) -> "EventMixin":
        self._bus.off(event, handler)
        return self

    def off_all(self, event: Optional[str] = None) -> "EventMixin":
        self._bus.off_all(event)
        return self

    def listeners(self, event: str) -> list[Handler]:
        return self._bus.listeners(event)

    def event_names(self) -> list[str]:
        return self._bus.event_names()


def _make_shorthand(event_name: str):
    """Factory for on_<event>, once_<event>, off_<event> methods."""
    def on_event(self, handler: Handler) -> "EventMixin":
        self._bus.on(event_name, handler)
        return self
    on_event.__name__ = f"on_{event_name}"
    on_event.__doc__ = f"Subscribe to the '{event_name}' event."

    def once_event(self, handler: Handler) -> "EventMixin":
        self._bus.once(event_name, handler)
        return self
    once_event.__name__ = f"once_{event_name}"

    def off_event(self, handler: Handler) -> "EventMixin":
        self._bus.off(event_name, handler)
        return self
    off_event.__name__ = f"off_{event_name}"

    return on_event, once_event, off_event


# Dynamically attach on_<event>, once_<event>, off_<event> for every EventName
for _en in EventName:
    _safe_name = _en.value.replace(".", "_")
    _on, _once, _off = _make_shorthand(_en.value)
    setattr(EventMixin, f"on_{_safe_name}", _on)
    setattr(EventMixin, f"once_{_safe_name}", _once)
    setattr(EventMixin, f"off_{_safe_name}", _off)
