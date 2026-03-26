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
🮈      PRAESIDIUM · layout_manager.py                                              ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                        layout_manager.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# PRAESIDIUM · layout_manager.py
# Widget geometry persistence and default layout.
# version: 1.0.0
"""

import json
import tempfile
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, QObject, QTimer

from widget_base import ArcaneWidget
from widget_registry import WidgetRegistry
from configuus import Configuus

SCHEMA_VERSION = 1

# Default layout for 1849×779px canvas.
# All positions/sizes are in canvas-relative pixels.
DEFAULT_LAYOUT: dict = {
    "version": SCHEMA_VERSION,
    "widgets": {
        "git_main": {
            "cls": "GitWidget",
            "x": 8, "y": 8, "w": 280, "h": 240,
            "visible": True,
            "docked": False,
            "extra": {},   # repo_path falls back to configuus.arca_repo_path
        },
    },
    "docked_widgets": [],
}


class LayoutManager(QObject):
    """
    Persists and restores widget geometry and dock state.

    Interacts with WidgetRegistry to instantiate widgets at stored positions.
    layout.json is written atomically (tmp → rename) to avoid corruption.

    Signals:
        layout_changed()  — debounced; fires 500ms after last geometry change
    """

    layout_changed = pyqtSignal()

    def __init__(
        self,
        storage_path: Path,
        registry: WidgetRegistry,
        canvas_parent=None,
    ):
        super().__init__()
        self._path     = storage_path / "layout.json"
        self._registry = registry
        self._parent   = canvas_parent

        # In-memory geometry record: widget_id → {x,y,w,h,visible,docked,cls,extra}
        self._layout: dict = {}

        # Debounce timer — save 500ms after last move/resize
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self.save)

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> list[ArcaneWidget]:
        """
        Read layout.json; instantiate widgets via registry; set geometry.
        Falls back to default_layout() if layout.json absent or corrupt.
        Returns list of instantiated widgets in z-order (index 0 = bottom).
        """
        raw = self._read_layout_file()
        if raw is None:
            raw = DEFAULT_LAYOUT

        self._layout = raw.get("widgets", {})
        widgets: list[ArcaneWidget] = []

        for widget_id, record in self._layout.items():
            cls_name = record.get("cls")
            if not cls_name:
                continue

            extra = record.get("extra", {})

            # Inject repo_path from configuus if GitWidget and not overridden
            w = self._registry.instantiate(
                cls_name, widget_id, extra, parent=self._parent
            )
            if w is None:
                continue

            # Apply stored geometry
            w.move(record.get("x", 0), record.get("y", 0))
            w.resize(record.get("w", 280), record.get("h", 200))
            if not record.get("visible", True):
                w.hide()

            # Wire geometry signals → manager
            w.position_changed.connect(self.on_widget_moved)
            w.size_changed.connect(self.on_widget_resized)

            widgets.append(w)

        return widgets

    def _read_layout_file(self) -> dict | None:
        if not self._path.exists():
            return None
        try:
            data = json.loads(self._path.read_text())
            if data.get("version") != SCHEMA_VERSION:
                print("[LayoutManager] layout.json version mismatch — falling back to default")
                return None
            return data
        except (json.JSONDecodeError, OSError) as e:
            print(f"[LayoutManager] Failed to read layout.json: {e} — falling back to default")
            return None

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Serialise current geometry to layout.json atomically."""
        payload = {
            "version": SCHEMA_VERSION,
            "widgets": self._layout,
            "docked_widgets": [],
        }
        try:
            tmp_path = self._path.parent / (self._path.name + ".tmp")
            tmp_path.write_text(json.dumps(payload, indent=2))
            tmp_path.replace(self._path)
        except OSError as e:
            print(f"[LayoutManager] Save failed: {e}")

    def _schedule_save(self) -> None:
        """Restart debounce timer."""
        self._save_timer.start()

    # ------------------------------------------------------------------
    # Geometry event handlers (connected to widget signals)
    # ------------------------------------------------------------------

    def on_widget_moved(self, widget_id: str, x: int, y: int) -> None:
        if widget_id in self._layout:
            self._layout[widget_id]["x"] = x
            self._layout[widget_id]["y"] = y
        else:
            self._layout[widget_id] = {"x": x, "y": y}
        self._schedule_save()

    def on_widget_resized(self, widget_id: str, w: int, h: int) -> None:
        if widget_id in self._layout:
            self._layout[widget_id]["w"] = w
            self._layout[widget_id]["h"] = h
        else:
            self._layout[widget_id] = {"w": w, "h": h}
        self._schedule_save()

    def on_widget_visibility_changed(self, widget_id: str, visible: bool) -> None:
        if widget_id in self._layout:
            self._layout[widget_id]["visible"] = visible
        self._schedule_save()

