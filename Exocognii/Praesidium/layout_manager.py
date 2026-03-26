"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈                  ██       █████  ██    ██  ██████  ██    ██ ████████      ███    ███  █████  ███    ██  █████   ██████  ███████ ██████  ▍
🮈                  ██      ██   ██  ██  ██  ██    ██ ██    ██    ██         ████  ████ ██   ██ ████   ██ ██   ██ ██       ██      ██   ██ ▍
🮈                  ██      ███████   ████   ██    ██ ██    ██    ██         ██ ████ ██ ███████ ██ ██  ██ ███████ ██   ███ █████   ██████  ▍
🮈                  ██      ██   ██    ██    ██    ██ ██    ██    ██         ██  ██  ██ ██   ██ ██  ██ ██ ██   ██ ██    ██ ██      ██   ██ ▍
🮈                  ███████ ██   ██    ██     ██████   ██████     ██ ███████ ██      ██ ██   ██ ██   ████ ██   ██  ██████  ███████ ██   ██ ▍
🮈                                                                                                                                         ▍
🮈                                                                                                                                         ▍
🮈           Python Script           ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃

🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · layout_manager.py      ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · layout_manager.py
# Widget geometry persistence and default layout.
# version: 1.1.0
# Changes: fix geometry restore order, lock persistence, register_widget(),
#          save_as_default(), visibility persisted on close

import json
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, QObject, QTimer

from widget_base import ArcaneWidget
from widget_registry import WidgetRegistry

SCHEMA_VERSION = 1

DEFAULT_LAYOUT: dict = {
    "version": SCHEMA_VERSION,
    "widgets": {
        "git_main": {
            "cls": "GitWidget",
            "x": 8, "y": 8, "w": 280, "h": 280,
            "visible": True, "locked": False, "docked": False, "extra": {},
        },
        "chat_main": {
            "cls": "ChatWidget",
            "x": 296, "y": 8, "w": 560, "h": 460,
            "visible": True, "locked": False, "docked": False, "extra": {},
        },
        "token_main": {
            "cls": "TokenTracker",
            "x": 864, "y": 8, "w": 280, "h": 260,
            "visible": True, "locked": False, "docked": False, "extra": {},
        },
        "todo_main": {
            "cls": "TodoBoard",
            "x": 8, "y": 296, "w": 280, "h": 300,
            "visible": True, "locked": False, "docked": False, "extra": {},
        },
        "launcher_main": {
            "cls": "AppLauncher",
            "x": 1152, "y": 8, "w": 200, "h": 200,
            "visible": True, "locked": False, "docked": False, "extra": {},
        },
        "style_main": {
            "cls": "StyleReference",
            "x": 864, "y": 276, "w": 280, "h": 260,
            "visible": True, "locked": False, "docked": False, "extra": {},
        },
        "status_main": {
            "cls": "StatusLegend",
            "x": 1152, "y": 216, "w": 200, "h": 180,
            "visible": True, "locked": False, "docked": False, "extra": {},
        },
    },
    "docked_widgets": [],
}


class LayoutManager(QObject):
    layout_changed = pyqtSignal()

    def __init__(self, storage_path: Path, registry: WidgetRegistry, canvas_parent=None):
        super().__init__()
        self._path     = storage_path / "layout.json"
        self._default_path = storage_path / "layout_default.json"
        self._registry = registry
        self._parent   = canvas_parent
        self._layout: dict = {}

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self.save)

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> list[ArcaneWidget]:
        raw = self._read_layout_file()
        if raw is None:
            raw = self._read_default_file() or DEFAULT_LAYOUT

        self._layout = raw.get("widgets", {})
        widgets: list[ArcaneWidget] = []

        for widget_id, record in self._layout.items():
            cls_name = record.get("cls")
            if not cls_name:
                continue

            w = self._registry.instantiate(
                cls_name, widget_id, record.get("extra", {}),
                parent=self._parent,
            )
            if w is None:
                continue

            # ── Geometry must be applied AFTER parent is set ──────────
            # setParent() resets geometry, so we apply here after
            # instantiate() has set the parent via constructor arg.
            w.move(record.get("x", 0), record.get("y", 0))
            w.resize(record.get("w", 280), record.get("h", 200))

            # Visibility
            if not record.get("visible", True):
                w.hide()

            # Lock state
            if record.get("locked", False):
                w.set_locked(True)

            # Wire geometry + state signals → manager
            w.position_changed.connect(self.on_widget_moved)
            w.size_changed.connect(self.on_widget_resized)
            w.visibility_changed.connect(self.on_widget_visibility_changed)
            w.lock_changed.connect(self.on_widget_lock_changed)

            widgets.append(w)

        return widgets

    def _read_layout_file(self) -> dict | None:
        return self._read_json(self._path)

    def _read_default_file(self) -> dict | None:
        return self._read_json(self._default_path)

    def _read_json(self, path: Path) -> dict | None:
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            if data.get("version") != SCHEMA_VERSION:
                print(f"[LayoutManager] {path.name} version mismatch — skipping")
                return None
            return data
        except (json.JSONDecodeError, OSError) as e:
            print(f"[LayoutManager] Failed to read {path.name}: {e}")
            return None

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self) -> None:
        self._write_json(self._path, {
            "version": SCHEMA_VERSION,
            "widgets": self._layout,
            "docked_widgets": [],
        })

    def save_as_default(self) -> None:
        """Overwrite the saved default layout with the current arrangement."""
        self._write_json(self._default_path, {
            "version": SCHEMA_VERSION,
            "widgets": self._layout,
            "docked_widgets": [],
        })
        print("[LayoutManager] Default layout saved.")

    def _write_json(self, path: Path, payload: dict) -> None:
        try:
            tmp = path.parent / (path.name + ".tmp")
            tmp.write_text(json.dumps(payload, indent=2))
            tmp.replace(path)
        except OSError as e:
            print(f"[LayoutManager] Save failed ({path.name}): {e}")

    def _schedule_save(self) -> None:
        self._save_timer.start()

    # ------------------------------------------------------------------
    # Public registration (for spawned widgets)
    # ------------------------------------------------------------------

    def register_widget(
        self,
        widget: ArcaneWidget,
        cls_name: str,
        extra: dict | None = None,
    ) -> None:
        """Register a newly spawned widget and wire its signals."""
        wid = widget.widget_id
        self._layout[wid] = {
            "cls":     cls_name,
            "x":       widget.x(),
            "y":       widget.y(),
            "w":       widget.width(),
            "h":       widget.height(),
            "visible": widget.isVisible(),
            "locked":  widget._locked,
            "docked":  False,
            "extra":   extra or {},
        }
        widget.position_changed.connect(self.on_widget_moved)
        widget.size_changed.connect(self.on_widget_resized)
        widget.visibility_changed.connect(self.on_widget_visibility_changed)
        widget.lock_changed.connect(self.on_widget_lock_changed)
        self.save()

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------

    def on_widget_moved(self, widget_id: str, x: int, y: int) -> None:
        if widget_id in self._layout:
            self._layout[widget_id]["x"] = x
            self._layout[widget_id]["y"] = y
        self._schedule_save()

    def on_widget_resized(self, widget_id: str, w: int, h: int) -> None:
        if widget_id in self._layout:
            self._layout[widget_id]["w"] = w
            self._layout[widget_id]["h"] = h
        self._schedule_save()

    def on_widget_visibility_changed(self, widget_id: str, visible: bool) -> None:
        if widget_id in self._layout:
            self._layout[widget_id]["visible"] = visible
        self._schedule_save()

    def on_widget_lock_changed(self, widget_id: str, locked: bool) -> None:
        if widget_id in self._layout:
            self._layout[widget_id]["locked"] = locked
        self._schedule_save()
