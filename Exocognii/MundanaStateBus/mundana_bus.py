# ─────────────────────────────────────────────────────────────────────────────
# mundana_bus.py
# Arca Cognitorium — Exocognii Infrastructure
# Mundana State Bus v1.0
# ─────────────────────────────────────────────────────────────────────────────
"""
Mundana State Bus daemon.

Listens on a Unix domain socket at /tmp/mundana.sock.
Accepts subscriber and publisher connections; routes newline-delimited
JSON messages between them; maintains last-state cache per channel for
late-joining subscribers.

Run via: python -m MundanaStateBus
Never imported by app code — apps use mundana_client.MundanaClient only.
"""
import json
import logging
import signal
import socket
import threading
from pathlib import Path
from typing import Any

from .mundana_channels import CHANNELS, BusChannelError, validate_channel

SOCKET_PATH = Path("/tmp/mundana.sock")
log = logging.getLogger("mundana.bus")


class MundanaBus:
    """Unix socket routing hub for the Exocognii publish/subscribe system."""

    def __init__(self) -> None:
        # channel → list of connected subscriber sockets
        self._subscriber_registry: dict[str, list[socket.socket]] = {
            ch: [] for ch in CHANNELS
        }
        # channel → last published payload (for late-join replay)
        self._last_state: dict[str, dict[str, Any]] = {}
        self._registry_lock = threading.Lock()
        self._running = False
        self._server_sock: socket.socket | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def install_signal_handlers(self) -> None:
        """Install SIGTERM/SIGINT handlers. Must be called from the main thread."""
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def start(self) -> None:
        """Bind socket and accept connections until stop() or signal."""
        SOCKET_PATH.unlink(missing_ok=True)
        self._server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_sock.bind(str(SOCKET_PATH))
        self._server_sock.listen(64)
        self._running = True
        log.info("Mundana State Bus listening on %s", SOCKET_PATH)

        while self._running:
            try:
                conn, _ = self._server_sock.accept()
            except OSError:
                break
            t = threading.Thread(
                target=self._handle_connection, args=(conn,), daemon=True
            )
            t.start()

    def stop(self) -> None:
        """Programmatic shutdown — safe to call from any thread."""
        self._handle_shutdown(0, None)

    # ── Connection handler ────────────────────────────────────────────────────

    def _handle_connection(self, conn: socket.socket) -> None:
        """Read newline-delimited JSON from one client until disconnect."""
        buf = ""
        try:
            while self._running:
                try:
                    chunk = conn.recv(4096)
                except OSError:
                    break
                if not chunk:
                    break
                buf += chunk.decode("utf-8", errors="replace")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if line:
                        self._dispatch(conn, line)
        finally:
            self._deregister_socket(conn)
            try:
                conn.close()
            except OSError:
                pass

    # ── Message dispatch ──────────────────────────────────────────────────────

    def _dispatch(self, conn: socket.socket, line: str) -> None:
        """Parse one JSON line and route to appropriate handler."""
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            self._send(conn, {
                "type": "ERROR", "code": "MALFORMED",
                "message": f"Invalid JSON: {e}"
            })
            return

        t = msg.get("type")
        if t == "PUBLISH":
            self._handle_publish(conn, msg)
        elif t == "SUBSCRIBE":
            self._handle_subscribe(conn, msg)
        elif t == "UNSUBSCRIBE":
            self._handle_unsubscribe(conn, msg)
        else:
            self._send(conn, {
                "type": "ERROR", "code": "UNKNOWN_TYPE",
                "message": f"Unknown message type: '{t}'"
            })

    # ── Publish ───────────────────────────────────────────────────────────────

    def _handle_publish(self, conn: socket.socket, msg: dict) -> None:
        """Validate channel, cache payload, route to all subscribers."""
        try:
            ch = validate_channel(msg.get("channel", ""))
        except BusChannelError as e:
            self._send(conn, {
                "type": "ERROR", "code": "UNKNOWN_CHANNEL", "message": str(e)
            })
            return

        payload = msg.get("payload", {})
        if not isinstance(payload, dict):
            self._send(conn, {
                "type": "ERROR", "code": "MALFORMED",
                "message": "payload must be a JSON object"
            })
            return

        with self._registry_lock:
            self._last_state[ch] = payload
            subscribers = list(self._subscriber_registry.get(ch, []))

        self._send(conn, {"type": "ACK", "ref": "PUBLISH", "channel": ch})
        self._route_message(ch, payload, subscribers)

    def _route_message(
        self,
        channel: str,
        payload: dict[str, Any],
        subscribers: list[socket.socket],
    ) -> None:
        """Deliver payload to all subscriber sockets; prune dead sockets."""
        envelope = (
            json.dumps({"type": "PUBLISH", "channel": channel, "payload": payload})
            + "\n"
        )
        encoded = envelope.encode("utf-8")
        dead: list[socket.socket] = []

        for sock in subscribers:
            try:
                sock.sendall(encoded)
            except (BrokenPipeError, OSError):
                dead.append(sock)

        if dead:
            with self._registry_lock:
                for sock in dead:
                    try:
                        self._subscriber_registry[channel].remove(sock)
                    except ValueError:
                        pass

    # ── Subscribe / Unsubscribe ───────────────────────────────────────────────

    def _handle_subscribe(self, conn: socket.socket, msg: dict) -> None:
        """Register socket; ACK; replay last state if cached."""
        try:
            ch = validate_channel(msg.get("channel", ""))
        except BusChannelError as e:
            self._send(conn, {
                "type": "ERROR", "code": "UNKNOWN_CHANNEL", "message": str(e)
            })
            return

        with self._registry_lock:
            if conn not in self._subscriber_registry[ch]:
                self._subscriber_registry[ch].append(conn)
            last = self._last_state.get(ch)

        self._send(conn, {"type": "ACK", "ref": "SUBSCRIBE", "channel": ch})

        if last is not None:
            self._send(conn, {
                "type": "REPLAY", "channel": ch, "payload": last
            })

    def _handle_unsubscribe(self, conn: socket.socket, msg: dict) -> None:
        """Remove socket from channel registry; ACK."""
        try:
            ch = validate_channel(msg.get("channel", ""))
        except BusChannelError as e:
            self._send(conn, {
                "type": "ERROR", "code": "UNKNOWN_CHANNEL", "message": str(e)
            })
            return

        with self._registry_lock:
            try:
                self._subscriber_registry[ch].remove(conn)
            except ValueError:
                pass

        self._send(conn, {"type": "ACK", "ref": "UNSUBSCRIBE", "channel": ch})

    # ── Deregister ────────────────────────────────────────────────────────────

    def _deregister_socket(self, conn: socket.socket) -> None:
        """Remove a socket from all channel registries on disconnect."""
        with self._registry_lock:
            for ch in self._subscriber_registry:
                try:
                    self._subscriber_registry[ch].remove(conn)
                except ValueError:
                    pass

    # ── Shutdown ──────────────────────────────────────────────────────────────

    def _handle_shutdown(self, signum: int, frame: Any) -> None:
        """Broadcast shutdown notice to all subscribers, then stop."""
        log.info("Signal %s received — broadcasting shutdown", signum)
        self._running = False

        shutdown_msg = (
            json.dumps({
                "type": "SHUTDOWN",
                "channel": "mundana.bus_control",
                "payload": {"reason": "daemon_exit"},
            })
            + "\n"
        ).encode("utf-8")

        with self._registry_lock:
            all_sockets: set[socket.socket] = set()
            for socks in self._subscriber_registry.values():
                all_sockets.update(socks)

        for sock in all_sockets:
            try:
                sock.sendall(shutdown_msg)
            except OSError:
                pass

        if self._server_sock:
            try:
                self._server_sock.close()
            except OSError:
                pass

        SOCKET_PATH.unlink(missing_ok=True)
        log.info("Mundana State Bus stopped")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _send(conn: socket.socket, msg: dict) -> None:
        """Serialize and send one JSON line to a single socket."""
        try:
            conn.sendall((json.dumps(msg) + "\n").encode("utf-8"))
        except OSError:
            pass
