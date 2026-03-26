"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈    ██████  ██    ██ ███    ██      ▍
🮈    ██   ██ ██    ██ ████   ██      ▍
🮈    ██████  ██    ██ ██ ██  ██      ▍
🮈    ██   ██ ██    ██ ██  ██ ██      ▍
🮈    ██   ██  ██████  ██   ████      ▍
🮈                                    ▍
🮈                                    ▍
🮈           Python Script            ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                                   run.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# PRAESIDIUM · run.py
# Entry point. QApplication bootstrap + monitor assignment.
# version: 1.0.0
"""

import sys
from pathlib import Path

# Ensure praesidium package root is on sys.path when invoked directly
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from configuus import Configuus, ConfigError
from praesidium_app import PraesidiumApp
from theme import GLOBAL_STYLE

STORAGE_PATH = _HERE / "storage"


def main() -> int:
    # Hi-DPI — must be set before QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Praesidium")
    app.setStyleSheet(GLOBAL_STYLE)

    # Config
    try:
        cfg = Configuus()
    except ConfigError as e:
        print(f"[PRAESIDIUM] Configuration error: {e}")
        return 1

    # Storage dirs
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    (STORAGE_PATH / "widget_state").mkdir(exist_ok=True)

    # Main window
    window = PraesidiumApp(configuus=cfg, storage_path=STORAGE_PATH)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
