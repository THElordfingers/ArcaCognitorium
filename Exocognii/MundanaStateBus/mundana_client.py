# ─────────────────────────────────────────────────────────────────────────────
# mundana_client.py
# Arca Cognitorium — Exocognii Infrastructure
# Mundana State Bus v1.0
# ─────────────────────────────────────────────────────────────────────────────
"""
MundanaClient — the sole interface Exocognii apps use to interact with the bus.

Usage pattern:
    client = MundanaClient()
    try:
        client.connect()
    except BusDaemonNotRunningError:
        # enter degraded mode — do not crash
        return

    client.subscribe("mundana.horologica", my_callback)
    client.publish("mundana.token_ledger", {"app": "dolium", "tokens": 120})
    client.disconnect()

Apps never import mundana_bus directly.
"""
import json
import logging
import socket
import threading
from collections.abc import Callable
from typing import Any

from .mundana_channels import BusChannelError, validate_channel

SOCKET_PATH = "/tmp/mundana.sock"
log = logging.getLogger("mundana.client")


class BusDaemonNotRunningError(Exception):
    """Raised when connect() cannot reach the bus daemon."""


class BusConnectionLostError(Exception):
    """Raised internally when an established connection drops."""


class MalformedPayloadError(Exception):
    """Raised when a received line cannot be parsed as JSON."""


class MundanaClient:
    """
    Connects to the Mundana State Bus daemon.
    Thread-safe. Runs a background reader thread after connect().
    """

    def __init__(self) -> None:
        self._sock: socket.socket | None = None
        self._callbacks: dict[str, list[Callable[[dict], None]]] = {}
        self._reader_thread: threading.Thread | None = None
        self._running = False
        self._lock = threading.Lock()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """
        Open Unix socket connection to the daemon.

        Raises BusDaemonNotRunningError if the socket is absent or refused.
        Starts the background reader thread.
        """
        try:
            self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._sock.connect(SOCKET_PATH)
        except (FileNotFoundError, ConnectionRefusedError) as e:
            self._sock = None
            raise BusDaemonNotRunningError(
                f"Mundana State Bus not running at {SOCKET_PATH}"
            ) from e

        self._running = True
        self._reader_thread = threading.Thread(
            target=self._reader_loop, daemon=True, name="mundana-reader"
        )
        self._reader_thread.start()

    def disconnect(self) -> None:
        """Stop the reader thread and close the socket."""
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    # ── Subscribe / Unsubscribe ───────────────────────────────────────────────

    def subscribe(self, channel: str, callback: Callable[[dict], None]) -> None:
        """
        Register callback for channel and send SUBSCRIBE to daemon.

        The callback fires on the reader thread. PyQt6 callers must use
        MundanaQtBridge instead of subscribing directly.

        Raises BusChannelError for unknown channel names.
        """
        validate_channel(channel)
        with self._lock:
            self._callbacks.setdefault(channel, []).append(callback)
        self._send({"type": "SUBSCRIBE", "channel": channel,
                    "client_id": str(id(self))})

    def unsubscribe(
        self,
        channel: str,
        callback: Callable[[dict], None] | None = None,
    ) -> None:
        """
        Remove callback (or all callbacks) for channel and notify daemon.

        Raises BusChannelError for unknown channel names.
        """
        validate_channel(channel)
        with self._lock:
            if callback is None:
                self._callbacks.pop(channel, None)
            else:
                cbs = self._callbacks.get(channel, [])
                try:
                    cbs.remove(callback)
                except ValueError:
                    pass
        self._send({"type": "UNSUBSCRIBE", "channel": channel,
                    "client_id": str(id(self))})

    # ── Publish ───────────────────────────────────────────────────────────────

    def publish(self, channel: str, payload: dict[str, Any]) -> None:
        """
        Publish payload dict to channel.

        Raises BusChannelError for unknown channel names.
        No-op if not connected.
        """
        validate_channel(channel)
        self._send({"type": "PUBLISH", "channel": channel, "payload": payload})

    # ── Reader loop ───────────────────────────────────────────────────────────

    def _reader_loop(self) -> None:
        """
        Background thread: read newline-delimited JSON from the daemon socket.
        Dispatches each parsed message to registered callbacks.
        """
        buf = ""
        try:
            while self._running:
                try:
                    chunk = self._sock.recv(4096)
                except OSError:
                    break
                if not chunk:
                    raise BusConnectionLostError("Socket closed by daemon")
                buf += chunk.decode("utf-8", errors="replace")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if line:
                        try:
                            self._dispatch(json.loads(line))
                        except json.JSONDecodeError as e:
                            log.warning("MalformedPayload from bus: %s — line: %.80s", e, line)
        except BusConnectionLostError as e:
            if self._running:
                log.warning("Bus connection lost: %s", e)

    # ── Dispatch ──────────────────────────────────────────────────────────────

    def _dispatch(self, msg: dict) -> None:
        """Route one parsed message to registered callbacks."""
        t = msg.get("type")

        if t in ("PUBLISH", "REPLAY"):
            ch = msg.get("channel", "")
            payload = msg.get("payload", {})
            with self._lock:
                cbs = list(self._callbacks.get(ch, []))
            for cb in cbs:
                try:
                    cb(payload)
                except Exception:
                    log.exception("Callback error on channel %s", ch)

        elif t == "SHUTDOWN":
            log.info("Bus shutdown broadcast received — disconnecting")
            self._running = False

        elif t == "ERROR":
            log.error(
                "Bus error [%s]: %s", msg.get("code"), msg.get("message")
            )

        elif t == "ACK":
            pass  # acknowledgements are informational; no action required

        else:
            log.debug("Unhandled message type from bus: %s", t)

    # ── Internal send ─────────────────────────────────────────────────────────

    def _send(self, msg: dict) -> None:
        """Serialize and send one JSON line. Silent no-op if not connected."""
        if self._sock is None:
            return
        try:
            self._sock.sendall((json.dumps(msg) + "\n").encode("utf-8"))
        except OSError as e:
            log.warning("Send failed: %s", e)
