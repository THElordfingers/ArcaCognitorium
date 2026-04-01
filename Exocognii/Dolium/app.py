"""
app.py — Dolium v2
Application bootstrap. Resolves storage directory, applies global style,
launches DoliumWindow.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

import style
from store import IdeaStore
from ui.main_window import DoliumWindow


def run() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("The Dolium")
    app.setStyleSheet(style.GLOBAL_STYLE)

    # Storage directory resolution — default to app-local storage/
    storage_dir = Path(os.environ.get("DOLIUM_STORAGE", Path(__file__).parent / "storage"))
    storage_dir.mkdir(parents=True, exist_ok=True)

    store  = IdeaStore(storage_dir)
    window = DoliumWindow(store, storage_dir)
    window.show()

    sys.exit(app.exec())
