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
# version: 1.1.0
# Changes:
#   - _load_widgets() no longer re-connects visibility_changed / lock_changed
#     to layout_manager — those are wired canonically inside LayoutManager._wire_widget()
#   - Only app-level signals (git_status_updated, status_changed, token_used)
#     are wired here; layout signals are layout_manager's responsibility

from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout,
    QApplication, QMenu,
)
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QScreen

from theme import (
    GLOBAL_STYLE, C_BG, C_PANEL, C_GOLD, C_GOLD_DIM, C_GOLD_DARK,
    C_STATUS_OK, C_STATUS_IDLE, arcane_button,
)
from configuus import Configuus
from widget_registry import WidgetRegistry
from layout_manager import LayoutManager

TOPBAR_H    = 42
STATUSBAR_H = 28
CANVAS_W    = 1849
CANVAS_H    = 779


class PraesidiumApp(QMainWindow):
    """
    Main window. Owns:
      - TopBar (42px)
      - Canvas (free-floating widget layer)
      - StatusBar (28px)
      - LayoutManager + WidgetRegistry
    """

    def __init__(self, configuus: Configuus, storage_path: Path):
        super().__init__()
        self._cfg  = configuus
        self._stor = storage_path

        self.setWindowTitle("PRAESIDIUM")
        self.setMinimumSize(800, 480)

        self._build_ui()
        self._init_managers()
        self._assign_monitor()
        # Defer widget load until after the event loop starts so the canvas
        # has resolved its geometry before move() / resize() are called.
        # 150ms: gives X11 time to assign a native window handle to the canvas
        # before widgets are parented and shown. singleShot(0) fires before the
        # window has a real handle on X11, causing children to go top-level.
        QTimer.singleShot(150, self._load_widgets)

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

        offset = (len(self._widgets) % 8) * 24
        w.move(40 + offset, 40 + offset)
        w.resize(300, 260)
        w.show()
        self._widgets.append(w)

        # App-level signal wiring (non-layout)
        self._wire_app_signals(w)

        # Layout manager handles persistence + layout signal wiring
        self._layout_mgr.register_widget(w, cls_name)

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
            ("exo",   "● EXOCOGNII: —"),
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
        #   - purging stale entries
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

        if self._chat_widget and self._token_tracker:
            self._chat_widget.token_used.connect(self._token_tracker.record_usage)

        if self._token_tracker:
            self._token_tracker.usage_recorded.connect(self._on_token_usage)

    def _wire_app_signals(self, w) -> None:
        """
        Wire application-level signals (git status, widget status, token usage).
        Layout signals (position, size, visibility, lock) are wired exclusively
        by LayoutManager._wire_widget() and must NOT be connected here.
        """
        cls = type(w).__name__

        if hasattr(w, "git_status_updated"):
            w.git_status_updated.connect(self._on_git_status)
        if hasattr(w, "status_changed"):
            w.status_changed.connect(self._on_widget_status)

        if cls == "ChatWidget":
            self._chat_widget = w
            if self._token_tracker:
                w.token_used.connect(self._token_tracker.record_usage)
        elif cls == "TokenTracker":
            self._token_tracker = w
            if self._chat_widget:
                self._chat_widget.token_used.connect(w.record_usage)
            w.usage_recorded.connect(self._on_token_usage)
        elif cls == "StatusLegend":
            self._status_legend = w

    # ------------------------------------------------------------------
    # Status bar updates
    # ------------------------------------------------------------------

    def _on_git_status(self, widget_id: str, status: str) -> None:
        lbl = self._status_labels.get("git")
        if lbl is None:
            return
        text_map = {
            "ok":    ("● GIT: Clean",    C_STATUS_OK),
            "warn":  ("● GIT: Modified", "#d4af37"),
            "error": ("● GIT: Error",    "#8b1a1a"),
        }
        text, colour = text_map.get(status, ("● GIT: —", C_STATUS_IDLE))
        lbl.setText(text)
        lbl.setStyleSheet(
            f"color: {colour}; font-family: Georgia, serif; "
            "font-size: 10px; background: transparent;"
        )

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
                    "warn":  "#d4af37",
                    "error": "#8b1a1a",
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

    def _on_token_usage(self, model: str, input_tokens: int, output_tokens: int, session_id: str) -> None:
        lbl = self._status_labels.get("token")
        if lbl:
            total = input_tokens + output_tokens
            lbl.setText(f"● TOKEN: {total:,}")
            lbl.setStyleSheet(
                f"color: {C_STATUS_OK}; font-family: Georgia, serif; "
                "font-size: 10px; background: transparent;"
            )

    # ------------------------------------------------------------------
    # Monitor assignment
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
