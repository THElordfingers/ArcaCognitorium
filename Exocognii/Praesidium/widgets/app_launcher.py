"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈   █████  ██████  ██████     ██       █████  ██    ██ ███    ██  ██████ ██   ██ ███████ ██████  ▍
🮈  ██   ██ ██   ██ ██   ██    ██      ██   ██ ██    ██ ████   ██ ██      ██   ██ ██      ██   ██ ▍
🮈  ███████ ██████  ██████     ██      ███████ ██    ██ ██ ██  ██ ██      ███████ █████   ██████  ▍
🮈  ██   ██ ██      ██         ██      ██   ██ ██    ██ ██  ██ ██ ██      ██   ██ ██      ██   ██ ▍
🮈  ██   ██ ██      ██ ███████ ███████ ██   ██  ██████  ██   ████  ██████ ██   ██ ███████ ██   ██ ▍
🮈                                                                                                ▍
🮈                                                                                                ▍
🮈                                         Python Script                                          ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# PRAESIDIUM · widgets/app_launcher.py
# Configurable application launch buttons.
# Apps defined in ~/.arca/config.json under "launcher_apps".
# version: 1.0.0
"""

import subprocess
from pathlib import Path

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal

from widget_base import ArcaneWidget
from theme import C_GOLD, C_GOLD_DIM, C_GOLD_DARK, arcane_button, micro_label

# Default apps if not configured
DEFAULT_APPS = [
    {"label": "⚗ Tower",    "cmd": "bash ArcaCognitorium.sh",       "cwd": "~/ArcaCognitorium"},
    {"label": "🜲 Dolium",   "cmd": "python run.py",       "cwd": "~/ArcaCognitorium/tools/Dolium"},
    {"label": "⚙ Vigilarum","cmd": "python Vigilarum.sh", "cwd": "~/ArcaCognitorium/tools/Vigilarum"},
    {"label": "✕ Mythotex", "cmd": "python mythotex.py",  "cwd": "~/ArcaCognitorium/tools/Mythotex"},
]


class AppLauncher(ArcaneWidget):
    """
    Launches configured apps via subprocess.
    Apps sourced from configuus.get('launcher_apps') or DEFAULT_APPS.
    Each button fires and forgets — no process tracking.
    """

    app_launched = pyqtSignal(str)   # label

    def __init__(self, widget_id: str, apps: list | None = None, parent=None):
        super().__init__(widget_id, "App Launcher", parent)
        self._apps = apps or DEFAULT_APPS
        self._build_body()
        self.set_status("idle", "")

    def _build_body(self) -> None:
        L = self._body_layout
        L.addWidget(micro_label("launch"))

        for app in self._apps:
            btn = arcane_button(app["label"])
            btn.setFixedHeight(28)
            label = app["label"]
            cmd   = app["cmd"]
            cwd   = str(Path(app.get("cwd", "~")).expanduser())
            btn.clicked.connect(lambda checked, c=cmd, d=cwd, lb=label: self._launch(c, d, lb))
            L.addWidget(btn)

        L.addStretch()

    def _launch(self, cmd: str, cwd: str, label: str) -> None:
        try:
            subprocess.Popen(
                cmd, shell=True, cwd=cwd,
                start_new_session=True,
            )
            self.set_status("ok", f"Launched: {label}")
            self.app_launched.emit(label)
        except Exception as e:
            self.set_status("error", str(e)[:60])

