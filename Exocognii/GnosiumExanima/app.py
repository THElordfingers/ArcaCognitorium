# GNOSIUM EXANIMA — app.py
# v1.0.0
"""Application boot — QApplication and MainWindow construction."""

from __future__ import annotations

import logging
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMessageBox

from .config import GnosiumConfig
from .constants import APP_NAME, APP_SUBTITLE, APP_VERSION, FONT_STACK
from .ui.main_window import MainWindow


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )


def run() -> int:
    _configure_logging()

    try:
        config = GnosiumConfig()
    except Exception as exc:
        # Config failures are fatal — can't locate the repo
        _fatal(f"Configuus failed: {exc}")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setApplicationDisplayName(f"{APP_NAME} — {APP_SUBTITLE}")
    app.setFont(QFont("Georgia", 10))

    window = MainWindow(config)
    window.show()
    return app.exec()


def _fatal(message: str) -> None:
    # Use a message box if we have a display, otherwise stderr
    try:
        _stub_app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, f"{APP_NAME} — fatal", message)
    except Exception:
        print(f"FATAL: {message}", file=sys.stderr)
