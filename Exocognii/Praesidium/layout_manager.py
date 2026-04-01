#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · layout_manager.py                                              ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · layout_manager.py
# Widget geometry persistence and default layout.
# version: 1.2.0
# Changes:
#   - _loading guard: suppresses save() during load() to prevent partial writes
#   - purge_stale: removes layout entries for widgets that fail to instantiate
#   - corrupt/empty layout.json detected and replaced with DEFAULT_LAYOUT
#   - _wire_widget(): single canonical signal-wiring method — no double-connections
#   - blockSignals during geometry restore prevents mid-load save triggers
#   - synchronous clean write after load() completes

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
        self._path         = storage_path / "layout.json"
        self._default_path = storage_path / "layout_default.json"
        self._registry     = registry
        self._parent       = canvas_parent
        self._layout: dict = {}
        self._loading      = False  # guard: suppresses save() during load()

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self.save)

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> list[ArcaneWidget]:
        self._loading = True
        try:
            return self._load_inner()
        finally:
            self._loading = False

    def _load_inner(self) -> list[ArcaneWidget]:
        raw = self._read_layout_file()
        if raw is None:
            raw = self._read_default_file() or DEFAULT_LAYOUT

        source_widgets = raw.get("widgets", {})

        # Treat empty widgets dict as corrupt — fall back to DEFAULT_LAYOUT
        if not source_widgets:
            print("[LayoutManager] layout.json has empty widgets dict — using DEFAULT_LAYOUT")
            raw = DEFAULT_LAYOUT
            source_widgets = raw["widgets"]

        # Build a clean layout dict; purge entries that fail to instantiate
        self._layout = {}
        widgets: list[ArcaneWidget] = []
        failed_ids: list[str] = []

        for widget_id, record in source_widgets.items():
            cls_name = record.get("cls")
            if not cls_name:
                print(f"[LayoutManager] Skipping {widget_id!r}: missing cls key")
                failed_ids.append(widget_id)
                continue

            w = self._registry.instantiate(
                cls_name, widget_id, record.get("extra", {}),
                parent=self._parent,
            )
            if w is None:
                print(f"[LayoutManager] Purging stale entry {widget_id!r} ({cls_name})")
                failed_ids.append(widget_id)
                continue

            # Block signals during geometry restore.
            # resizeEvent emits size_changed — without this guard that fires
            # _schedule_save with a partially-populated _layout dict.
            w.blockSignals(True)
            w.move(record.get("x", 0), record.get("y", 0))
            w.resize(record.get("w", 280), record.get("h", 200))
            w.blockSignals(False)

            if not record.get("visible", True):
                w.hide()

            if record.get("locked", False):
                w.set_locked(True)

            if record.get("font_size"):
                if hasattr(w, "set_font_size"):
                    w.set_font_size(record["font_size"])

            # Write the verified record into the clean layout dict
            entry: dict = {
                "cls":     cls_name,
                "x":       w.x(),
                "y":       w.y(),
                "w":       w.width(),
                "h":       w.height(),
                "visible": record.get("visible", True),
                "locked":  record.get("locked", False),
                "docked":  record.get("docked", False),
                "extra":   record.get("extra", {}),
            }
            if record.get("font_size"):
                entry["font_size"] = record["font_size"]
            self._layout[widget_id] = entry

            # Wire signals after layout entry is committed
            self._wire_widget(w)
            widgets.append(w)

        if failed_ids:
            print(f"[LayoutManager] Purged {len(failed_ids)} stale entr(ies): {failed_ids}")

        # Synchronous clean write — persists the purged layout immediately.
        # This ensures layout.json is always in a valid state after load,
        # even if the process is killed before the debounce timer fires.
        self._write_json(self._path, {
            "version": SCHEMA_VERSION,
            "widgets": self._layout,
            "docked_widgets": [],
        })

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
                print(
                    f"[LayoutManager] {path.name}: version mismatch "
                    f"(got {data.get('version')!r}, expected {SCHEMA_VERSION}) — ignoring"
                )
                return None
            return data
        except (json.JSONDecodeError, OSError) as e:
            print(f"[LayoutManager] Failed to read {path.name}: {e}")
            return None

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self) -> None:
        if self._loading:
            return
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
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.parent / (path.name + ".tmp")
            tmp.write_text(json.dumps(payload, indent=2))
            tmp.replace(path)
        except OSError as e:
            print(f"[LayoutManager] Save failed ({path.name}): {e}")

    def _schedule_save(self) -> None:
        if self._loading:
            return
        self._save_timer.start()

    # ------------------------------------------------------------------
    # Signal wiring — single canonical method, no double-connections
    # ------------------------------------------------------------------

    def _wire_widget(self, w: ArcaneWidget) -> None:
        """
        Connect all layout-relevant signals from a widget to this manager.
        Called exactly once per widget lifetime — by load() or register_widget().
        praesidium_app must NOT re-connect these signals after calling load().
        """
        w.position_changed.connect(self.on_widget_moved)
        w.size_changed.connect(self.on_widget_resized)
        w.visibility_changed.connect(self.on_widget_visibility_changed)
        w.lock_changed.connect(self.on_widget_lock_changed)
        if hasattr(w, "font_size_changed"):
            w.font_size_changed.connect(self.on_widget_font_size_changed)

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
        self._wire_widget(widget)
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

    def on_widget_font_size_changed(self, widget_id: str, size: int) -> None:
        if widget_id in self._layout:
            self._layout[widget_id]["font_size"] = size
        self._schedule_save()
