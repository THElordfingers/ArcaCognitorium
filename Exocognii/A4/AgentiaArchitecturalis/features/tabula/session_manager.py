"""
Session Manager — named canvas sessions to storage/canvases/*.json.

Tracks dirty state. Provides save/discard/cancel guard dialog.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QMessageBox, QInputDialog, QWidget

from ...models import DesignDocument, ElementNode

_CANVASES_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "canvases"


class SessionManager:
    """Manages canvas session persistence."""

    def __init__(self) -> None:
        _CANVASES_DIR.mkdir(parents=True, exist_ok=True)
        self._current_name: str = ""
        self._current_path: Optional[Path] = None
        self._dirty: bool = False

    @property
    def current_name(self) -> str:
        return self._current_name

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    def mark_dirty(self) -> None:
        self._dirty = True

    def mark_clean(self) -> None:
        self._dirty = False

    def save(self, elements: list[ElementNode], parent_widget: QWidget | None = None) -> bool:
        """Save current canvas. Prompts for name if unnamed."""
        if not self._current_name:
            return self.save_as(elements, parent_widget)
        doc = DesignDocument(name=self._current_name, elements=elements)
        path = _CANVASES_DIR / f"{self._current_name}.json"
        doc.save(path)
        self._current_path = path
        self._dirty = False
        return True

    def save_as(self, elements: list[ElementNode], parent_widget: QWidget | None = None) -> bool:
        """Save canvas with a new name."""
        name, ok = QInputDialog.getText(
            parent_widget, "Sigilla Ut", "Canvas name:",
        )
        if not ok or not name.strip():
            return False
        name = name.strip().replace(" ", "_")
        self._current_name = name
        return self.save(elements, parent_widget)

    def load(self, parent_widget: QWidget | None = None) -> Optional[DesignDocument]:
        """Show available canvases and load one."""
        canvases = sorted(_CANVASES_DIR.glob("*.json"))
        if not canvases:
            QMessageBox.information(parent_widget, "Armarium", "No saved canvases found.")
            return None
        names = [p.stem for p in canvases]
        name, ok = QInputDialog.getItem(
            parent_widget, "Aperi Canvam", "Select canvas:", names, 0, False,
        )
        if not ok:
            return None
        path = _CANVASES_DIR / f"{name}.json"
        doc = DesignDocument.load(path)
        self._current_name = doc.name
        self._current_path = path
        self._dirty = False
        return doc

    def new_canvas(self, parent_widget: QWidget | None = None) -> bool:
        """Start a new canvas. Returns False if user cancels dirty guard."""
        if self._dirty:
            if not self._dirty_guard(parent_widget):
                return False
        self._current_name = ""
        self._current_path = None
        self._dirty = False
        return True

    def _dirty_guard(self, parent_widget: QWidget | None = None) -> bool:
        """Show save/discard/cancel dialog. Returns True if safe to proceed."""
        reply = QMessageBox.question(
            parent_widget,
            "Unsaved Changes",
            f"Canvas '{self._current_name or 'untitled'}' has unsaved changes.\n"
            "Save before continuing?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        if reply == QMessageBox.StandardButton.Save:
            # Caller must handle actual save
            return True
        return True  # Discard

    def check_dirty_guard(self, parent_widget: QWidget | None = None) -> bool:
        """Check if it's safe to proceed (no unsaved changes or user confirmed)."""
        if not self._dirty:
            return True
        return self._dirty_guard(parent_widget)

    def list_canvases(self) -> list[str]:
        """List all saved canvas names."""
        return sorted(p.stem for p in _CANVASES_DIR.glob("*.json"))
