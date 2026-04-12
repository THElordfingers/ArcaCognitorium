"""
Preview Data Model — single source of truth for both Specularium renderers.

Holds current_elements + current_tokens. Emits design_updated signal.
Two PreviewRenderer instances subscribe. No reparenting — this is constitutional.
"""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from ...models import ElementNode
from ... import tokens


class PreviewDataModel(QObject):
    """Shared data model for the dual Specularium instances."""

    design_updated = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._elements: list[ElementNode] = []
        self._tokens: dict[str, str] = dict(tokens.DEFAULTS)

    @property
    def current_elements(self) -> list[ElementNode]:
        return self._elements

    @property
    def current_tokens(self) -> dict[str, str]:
        return dict(self._tokens)

    def update_design(self, elements: list[ElementNode]) -> None:
        """Update the element tree and notify subscribers."""
        self._elements = elements
        self.design_updated.emit()

    def refresh_tokens(self, token_dict: dict[str, str]) -> None:
        """Update token values and notify subscribers."""
        self._tokens = dict(token_dict)
        self.design_updated.emit()
