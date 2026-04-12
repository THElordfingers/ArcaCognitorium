#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ARX AEDIFICARIX                                                             ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                                 __main__.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import logging
import os
import sys
from pathlib import Path

# Ensure ArcaCognitorium root is on sys.path for claudebox and token_logger
_ARCA_ROOT = Path("~/ArcaCognitorium").expanduser()
if str(_ARCA_ROOT) not in sys.path:
    sys.path.insert(0, str(_ARCA_ROOT))

# Ensure ArxAedificarix package dir is on sys.path for core/ui/bridge subpackages
_ARX_DIR = Path(__file__).parent.resolve()
if str(_ARX_DIR) not in sys.path:
    sys.path.insert(0, str(_ARX_DIR))

from PyQt6.QtWidgets import QApplication, QMessageBox

from core.config_loader import ConfigLoader
from core.database import DatabaseManager
from core.session_store import SessionStore


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )
    logger = logging.getLogger("arx")

    app = QApplication(sys.argv)
    app.setApplicationName("ArxAedificarix")
    app.setOrganizationName("Cogniverse")

    # --- Config ---
    ConfigLoader.load()
    api_key = ConfigLoader.api_key()
    if not api_key:
        QMessageBox.critical(
            None,
            "Arx Aedificarix — Initialisation Failed",
            "CLAUDE_API_KEY not found.\n\n"
            "Set the environment variable or add 'api_key' to ~/.arca/config.json.",
        )
        sys.exit(1)

    # --- Database ---
    try:
        DatabaseManager.initialise(db_path=ConfigLoader.db_path())
    except RuntimeError as exc:
        QMessageBox.critical(
            None,
            "Arx Aedificarix — Database Error",
            f"Could not initialise database:\n\n{exc}",
        )
        sys.exit(1)

    store = SessionStore()

    # --- ClaudeBox ---
    try:
        from claudebox import ClaudeBox
        box = ClaudeBox(
            system_prompt="",   # system_block assembled per-send by ContextEngine
            api_key=os.environ.get("CLAUDE_API_KEY"),
        )
        comp_box = ClaudeBox(
            system_prompt="You are a concise summariser. Output only the summary.",
            api_key=os.environ.get("CLAUDE_API_KEY"),
        )
    except Exception as exc:
        QMessageBox.critical(
            None,
            "Arx Aedificarix — ClaudeBox Error",
            f"Could not initialise ClaudeBox:\n\n{exc}",
        )
        sys.exit(1)

    # --- Main Window ---
    from ui.main_window import MainWindow
    window = MainWindow(store, box, comp_box)
    window.show()

    exit_code = app.exec()
    DatabaseManager.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
