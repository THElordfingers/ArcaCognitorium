# GNOSIUM EXANIMA — entity/portrait.py
# v1.0.0
"""Portrait loading and thumbnail caching for the entity panel."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap

from ..constants import C_GOLD_DIM, C_PANEL, PORTRAIT_THUMB_PX


class PortraitCache:
    """48x48 portrait cache with placeholder fallback."""

    def __init__(self, size: int = PORTRAIT_THUMB_PX):
        self._size = size
        self._cache: dict[str, QPixmap] = {}
        self._placeholder: Optional[QPixmap] = None

    def load(self, entity_id: str, portrait_path: Optional[Path]) -> QPixmap:
        if entity_id in self._cache:
            return self._cache[entity_id]

        pixmap: Optional[QPixmap] = None
        if portrait_path and portrait_path.exists():
            raw = QPixmap(str(portrait_path))
            if not raw.isNull():
                pixmap = raw.scaled(
                    self._size, self._size,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )

        if pixmap is None:
            pixmap = self._build_placeholder(entity_id)

        self._cache[entity_id] = pixmap
        return pixmap

    def _build_placeholder(self, entity_id: str) -> QPixmap:
        if self._placeholder is None:
            pm = QPixmap(self._size, self._size)
            pm.fill(QColor(C_PANEL))
            painter = QPainter(pm)
            pen = QPen(QColor(C_GOLD_DIM))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(0, 0, self._size - 1, self._size - 1)
            painter.drawLine(self._size // 3, self._size // 4,
                             2 * self._size // 3, self._size // 4)
            painter.drawLine(self._size // 4, self._size // 2,
                             3 * self._size // 4, self._size // 2)
            painter.end()
            self._placeholder = pm
        return self._placeholder
