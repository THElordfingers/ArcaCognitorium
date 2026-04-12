#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈                                                                                  ▍
🮈   P R A E S I D I U M                                                            ▍
🮈   Vigilia Perpetua                                                               ▍
🮈                                                                                  ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                        praesidium_app.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# PRAESIDIUM · praesidium_app.py
# QMainWindow — entry point; owns monitor assignment.
# version: 2.0.0
# v2 changes:
#   - NuntiusClient wired in __init__; _emit/_involucrum helpers.
#   - Emission sites: chat_complete, token_usage, git_status, widget_spawn,
#     widget_close. Fire-and-forget; silently degrades if NUNTIUS absent.
#   - Non-wrapping spawn counter (fix B5) with (400, 400) clamp.
#   - Order-independent post-load wiring pass for ChatWidget/TokenTracker (B4).
#   - _wire_app_signals stripped of in-loop class discovery; handles only
#     per-widget app signals + ServicesWidget connection.
#   - exo status slot renamed '● NUNTIUS: —', driven by ServicesWidget.
#   - ADD WIDGET picker includes ServicesWidget label.
# Prior (v1.1.0):
#   - _load_widgets() no longer re-connects visibility_changed / lock_changed
#     to layout_manager — those are wired canonically inside LayoutManager._wire_widget()

import sys
from datetime import datetime, timezone
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout,
    QApplication, QMenu,
)
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QScreen

from theme import (
    GLOBAL_STYLE, C_BG, C_PANEL, C_GOLD, C_GOLD_DIM, C_GOLD_DARK,
    C_STATUS_OK, C_STATUS_WARN, C_STATUS_ERROR, C_STATUS_IDLE, arcane_button,
)
from configuus import Configuus
from widget_registry import WidgetRegistry
from layout_manager import LayoutManager

TOPBAR_H    = 42
STATUSBAR_H = 28
CANVAS_W    = 1849
CANVAS_H    = 779

PRAESIDIUM_VERSION = "2.0.0"


class PraesidiumApp(QMainWindow):
    """
    Main window. Owns:
      - TopBar (42px)
      - Canvas (free-floating widget layer)
      - StatusBar (28px)
      - LayoutManager + WidgetRegistry
      - NuntiusClient (optional, fire-and-forget)
    """

    def __init__(self, configuus: Configuus, storage_path: Path):
        super().__init__()
        self._cfg  = configuus
        self._stor = storage_path

        self.setWindowTitle("PRAESIDIUM")
        self.setMinimumSize(800, 480)

        # Spawn counter — never wraps, keeps ADD WIDGET offsets sane (fix B5)
        self._spawn_count: int = 0

        # NUNTIUS client (optional, graceful degradation)
        self._init_nuntius()

        self._build_ui()
        self._init_managers()
        self._assign_monitor()
        # Defer widget load until after the event loop starts so the canvas
        # has resolved its geometry before move() / resize() are called.
        # 150ms: gives X11 time to assign a native window handle to the canvas
        # before widgets are parented and shown.
        QTimer.singleShot(150, self._load_widgets)

    # ------------------------------------------------------------------
    # NUNTIUS client
    # ------------------------------------------------------------------

    def _init_nuntius(self) -> None:
        """Instantiate NuntiusClient. Silently degrades if unreachable/misconfigured."""
        self._nuntius = None
        self._NuntiusDaemonNotRunningError = Exception
        try:
            exocognii_dir = str(self._cfg.arca_repo_path / "Exocognii")
            if exocognii_dir not in sys.path:
                sys.path.insert(0, exocognii_dir)
            from Nuntius.nuntius_client import (  # type: ignore
                NuntiusClient, NuntiusDaemonNotRunningError,
            )
            self._nuntius = NuntiusClient()
            self._NuntiusDaemonNotRunningError = NuntiusDaemonNotRunningError
            print("[PRAESIDIUM] NuntiusClient initialised.")
        except Exception as e:
            print(f"[PRAESIDIUM] NuntiusClient unavailable: {e}")
            self._nuntius = None

    def _involucrum(self, hint: str, body: dict) -> dict:
        """Wrap a body dict with source/timestamp metadata for NUNTIUS /emit."""
        return {
            "source_app":     "Praesidium",
            "source_version": PRAESIDIUM_VERSION,
            "timestamp":      datetime.now(timezone.utc).isoformat(),
            "hint":           hint,
            "body":           body,
        }

    def _emit(self, payload: dict) -> None:
        """Fire-and-forget Involucrum emission. Silently degrades if NUNTIUS absent."""
        if self._nuntius is None:
            return
        try:
            self._nuntius.emit(payload)
        except self._NuntiusDaemonNotRunningError:
            pass  # NUNTIUS not running — observation dropped silently
        except Exception as e:
            print(f"[PRAESIDIUM] NUNTIUS emit error: {e}")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root.setStyleSheet(f"background: {C_BG};")

        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self._topbar = self._build_topbar()
        vbox.addWidget(self._topbar)

        self._canvas = QWidget()
        self._canvas.setObjectName("canvas")
        self._canvas.setStyleSheet(f"QWidget#canvas {{ background: {C_BG}; }}")
        vbox.addWidget(self._canvas, 1)

        self._statusbar_frame = self._build_statusbar()
        vbox.addWidget(self._statusbar_frame)

    def _build_topbar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(TOPBAR_H)
        bar.setStyleSheet(
            f"QFrame {{ background: {C_PANEL}; border-bottom: 1px solid {C_GOLD_DARK}; }}"
        )

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 10, 0)
        layout.setSpacing(10)

        title = QLabel("PRAESIDIUM")
        title.setStyleSheet(
            f"color: {C_GOLD}; font-family: Georgia, serif; "
            "font-size: 16px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(title)

        sub = QLabel("✦  Vigilia Perpetua  ✦")
        sub.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
            "font-size: 10px; letter-spacing: 2px; background: transparent;"
        )
        layout.addWidget(sub)
        layout.addStretch()

        self._btn_add    = arcane_button("⊞  ADD WIDGET")
        btn_save_default = arcane_button("⊙  SAVE DEFAULT")
        btn_config       = arcane_button("⚙  CONFIG")
        self._btn_add.clicked.connect(self._show_widget_picker)
        btn_save_default.clicked.connect(self._save_default_layout)
        layout.addWidget(self._btn_add)
        layout.addWidget(btn_save_default)
        layout.addWidget(btn_config)

        return bar

    def _show_widget_picker(self) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {C_PANEL};
                color: {C_GOLD};
                border: 1px solid {C_GOLD_DARK};
                font-family: Georgia, serif;
                font-size: 11px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 18px;
                letter-spacing: 1px;
            }}
            QMenu::item:selected {{
                background: {C_GOLD_DARK};
                color: {C_GOLD};
            }}
        """)

        labels = {
            "GitWidget":            "⎇  Git",
            "ChatWidget":           "⚗  Chat",
            "TokenTracker":         "◈  Token Tracker",
            "TodoBoard":            "☐  Todo Board",
            "AppLauncher":          "⊞  App Launcher",
            "StyleReference":       "■  Style Reference",
            "StatusLegend":         "●  Status Legend",
            "DisplayPanel":         "⊟  Display Panel",
            "DiffViewer":           "⎇  Diff Viewer",
            "RepoActivity":         "⚡  Repo Activity",
            "QuickFileDrop":        "⬇  Quick File Drop",
            "ReferentiaAggregator": "⚙  Referentia",
            "ServicesWidget":         "⚙  Services",
            "MundanaAmbientWidget":   "☽  Mundana Ambient",
            "AppStatusWidget":        "●  App Status",
            "ActivityFeedWidget":     "⚡  Activity Feed",
        }

        for cls_name in self._registry.available_classes():
            label = labels.get(cls_name, cls_name)
            action = menu.addAction(label)
            action.setData(cls_name)

        btn_geo = self._btn_add.mapToGlobal(self._btn_add.rect().bottomLeft())
        chosen  = menu.exec(btn_geo)
        if chosen:
            self._spawn_widget(chosen.data())

    def _spawn_widget(self, cls_name: str) -> None:
        import uuid
        widget_id = f"{cls_name.lower()}_{uuid.uuid4().hex[:6]}"

        w = self._registry.instantiate(
            cls_name, widget_id, extra={}, parent=self._canvas
        )
        if w is None:
            return

        # Non-wrapping offset, clamped to stay on-canvas (fix B5)
        offset = self._spawn_count * 24
        self._spawn_count += 1
        x = min(40 + offset, 400)
        y = min(40 + offset, 400)
        w.move(x, y)
        w.resize(300, 260)
        w.show()
        self._widgets.append(w)

        # App-level signal wiring (non-layout)
        self._wire_app_signals(w)

        # Layout manager handles persistence + layout signal wiring
        self._layout_mgr.register_widget(w, cls_name)

        # NUNTIUS emission — widget_spawn
        self._emit(self._involucrum("widget_spawn", {
            "widget_id": widget_id,
            "cls":       cls_name,
        }))

    def _build_statusbar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(STATUSBAR_H)
        bar.setStyleSheet(
            f"QFrame {{ background: {C_PANEL}; border-top: 1px solid {C_GOLD_DARK}; }}"
        )

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(16)

        self._status_labels: dict[str, QLabel] = {}

        for slot_id, initial_text in (
            ("git",   "● GIT: Initialising"),
            ("chat",  "● CHAT: —"),
            ("token", "● TOKEN: —"),
            ("exo",   "● NUNTIUS: —"),
        ):
            lbl = QLabel(initial_text)
            lbl.setStyleSheet(
                f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
                "font-size: 10px; background: transparent;"
            )
            self._status_labels[slot_id] = lbl
            layout.addWidget(lbl)

        layout.addStretch()
        return bar

    # ------------------------------------------------------------------
    # Managers
    # ------------------------------------------------------------------

    def _init_managers(self) -> None:
        self._registry   = WidgetRegistry(self._cfg)
        self._layout_mgr = LayoutManager(
            storage_path=self._stor,
            registry=self._registry,
            canvas_parent=self._canvas,
        )

    def _load_widgets(self) -> None:
        # layout_manager.load() handles:
        #   - reading layout.json (or DEFAULT_LAYOUT on corrupt/empty)
        #   - instantiating widgets with correct parent
        #   - restoring geometry, visibility, lock, font size
        #   - purging stale entries and DEDUPLICATING (v2)
        #   - wiring ALL layout signals (position, size, visibility, lock, font)
        #   - synchronous clean write of layout.json after load
        self._widgets = self._layout_mgr.load()

        self._chat_widget   = None
        self._token_tracker = None
        self._status_legend = None

        for w in self._widgets:
            # Re-assert parent on X11: setParent() enforces embedding after
            # the window has a native handle. Geometry is re-applied after.
            if w.parent() is not self._canvas:
                w.setParent(self._canvas)
                w.move(w.x(), w.y())
            w.show()
            w.raise_()
            self._wire_app_signals(w)

        # ------------------------------------------------------------------
        # Post-load wiring pass — order-independent (fix B4).
        # Discover ChatWidget and TokenTracker by class name after every
        # widget has been loaded. Do not rely on iteration order.
        # ------------------------------------------------------------------
        chat  = next((w for w in self._widgets if type(w).__name__ == "ChatWidget"), None)
        token = next((w for w in self._widgets if type(w).__name__ == "TokenTracker"), None)
        legend = next((w for w in self._widgets if type(w).__name__ == "StatusLegend"), None)

        if chat and token:
            try:
                chat.token_used.connect(token.record_usage)
            except (RuntimeError, TypeError):
                pass  # already connected / signal missing — guard

        if token:
            try:
                token.usage_recorded.connect(self._on_token_usage)
            except (RuntimeError, TypeError):
                pass

        self._chat_widget   = chat
        self._token_tracker = token
        self._status_legend = legend

    def _wire_app_signals(self, w) -> None:
        """
        Wire application-level signals (git status, widget status, visibility,
        nuntius status from ServicesWidget).
        Layout signals (position, size, lock) are wired exclusively by
        LayoutManager._wire_widget() and must NOT be connected here.
        Inter-widget wiring (Chat ↔ Token) is done in _load_widgets() in an
        order-independent post-load pass — do not duplicate it here.
        """
        if hasattr(w, "git_status_updated"):
            try:
                w.git_status_updated.connect(self._on_git_status)
            except (RuntimeError, TypeError):
                pass
        if hasattr(w, "status_changed"):
            try:
                w.status_changed.connect(self._on_widget_status)
            except (RuntimeError, TypeError):
                pass
        if hasattr(w, "visibility_changed"):
            try:
                w.visibility_changed.connect(self._on_widget_visibility)
            except (RuntimeError, TypeError):
                pass

        # ServicesWidget drives the exo/NUNTIUS status slot
        if type(w).__name__ == "ServicesWidget" and hasattr(w, "nuntius_status_changed"):
            try:
                w.nuntius_status_changed.connect(self._on_nuntius_status)
            except (RuntimeError, TypeError):
                pass

    # ------------------------------------------------------------------
    # Status bar updates
    # ------------------------------------------------------------------

    def _on_git_status(self, widget_id: str, status: str) -> None:
        lbl = self._status_labels.get("git")
        if lbl is None:
            return
        text_map = {
            "ok":    ("● GIT: Clean",    C_STATUS_OK),
            "warn":  ("● GIT: Modified", C_STATUS_WARN),
            "error": ("● GIT: Error",    C_STATUS_ERROR),
        }
        text, colour = text_map.get(status, ("● GIT: —", C_STATUS_IDLE))
        lbl.setText(text)
        lbl.setStyleSheet(
            f"color: {colour}; font-family: Georgia, serif; "
            "font-size: 10px; background: transparent;"
        )

        # NUNTIUS emission — git_status
        self._emit(self._involucrum("git_status", {
            "widget_id": widget_id,
            "status":    status,
        }))

    def _on_widget_status(self, widget_id: str, status: str, message: str) -> None:
        if self._status_legend:
            slot = None
            if widget_id.startswith("git"):   slot = "git"
            elif widget_id.startswith("chat"): slot = "chat"
            elif widget_id.startswith("token"): slot = "token"
            if slot:
                self._status_legend.update_slot(slot, status, message)

        if widget_id.startswith("chat"):
            lbl = self._status_labels.get("chat")
            if lbl:
                colour_map = {
                    "ok":    C_STATUS_OK,
                    "warn":  C_STATUS_WARN,
                    "error": C_STATUS_ERROR,
                    "idle":  C_STATUS_IDLE,
                }
                label_map = {
                    "ok":    "● CHAT: Ready",
                    "warn":  "● CHAT: Streaming",
                    "error": "● CHAT: Error",
                    "idle":  "● CHAT: Idle",
                }
                colour = colour_map.get(status, C_STATUS_IDLE)
                lbl.setText(label_map.get(status, "● CHAT: —"))
                lbl.setStyleSheet(
                    f"color: {colour}; font-family: Georgia, serif; "
                    "font-size: 10px; background: transparent;"
                )

            # NUNTIUS emission — chat_complete on successful response
            if status == "ok":
                self._emit(self._involucrum("chat_complete", {
                    "widget_id": widget_id,
                    "event":     "response_complete",
                }))

    def _on_token_usage(self, model: str, input_tokens: int, output_tokens: int, session_id: str) -> None:
        lbl = self._status_labels.get("token")
        if lbl:
            total = input_tokens + output_tokens
            lbl.setText(f"● TOKEN: {total:,}")
            lbl.setStyleSheet(
                f"color: {C_STATUS_OK}; font-family: Georgia, serif; "
                "font-size: 10px; background: transparent;"
            )

        # NUNTIUS emission — token_usage
        self._emit(self._involucrum("token_usage", {
            "model":         model,
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "session_id":    session_id,
            "total":         input_tokens + output_tokens,
        }))

    def _on_widget_visibility(self, widget_id: str, visible: bool) -> None:
        """Emit widget_close observation when a widget is hidden via ✕."""
        if visible:
            return
        self._emit(self._involucrum("widget_close", {
            "widget_id": widget_id,
        }))

    def _on_nuntius_status(self, status: str, summary: str) -> None:
        """Update the exo/NUNTIUS status bar slot from ServicesWidget signal."""
        lbl = self._status_labels.get("exo")
        if lbl is None:
            return
        colour_map = {
            "running":  C_STATUS_OK,
            "offline":  C_STATUS_ERROR,
            "starting": C_STATUS_WARN,
            "unknown":  C_STATUS_IDLE,
        }
        text_map = {
            "running":  f"● NUNTIUS: {summary}",
            "starting": f"● NUNTIUS: {summary}",
            "offline":  "● NUNTIUS: Offline",
            "unknown":  "● NUNTIUS: —",
        }
        lbl.setText(text_map.get(status, "● NUNTIUS: —"))
        lbl.setStyleSheet(
            f"color: {colour_map.get(status, C_STATUS_IDLE)}; "
            "font-family: Georgia, serif; font-size: 10px; background: transparent;"
        )

    # ------------------------------------------------------------------
    # Save default / monitor assignment
    # ------------------------------------------------------------------

    def _save_default_layout(self) -> None:
        self._layout_mgr.save_as_default()
        lbl = self._status_labels.get("git")
        if lbl:
            orig_text, orig_style = lbl.text(), lbl.styleSheet()
            lbl.setText("✦ Default layout saved")
            QTimer.singleShot(2000, lambda: (
                lbl.setText(orig_text),
                lbl.setStyleSheet(orig_style),
            ))

    def _assign_monitor(self) -> None:
        screens = QApplication.screens()
        primary: QScreen = QApplication.primaryScreen()

        target: QScreen = primary
        for s in screens:
            if s is not primary:
                target = s
                break

        geo: QRect = target.geometry()
        self.setGeometry(
            geo.x(),
            geo.y(),
            CANVAS_W,
            CANVAS_H + TOPBAR_H + STATUSBAR_H,
        )
