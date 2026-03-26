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
    {"label": "✦ ARCA COGNITORIUM ✦",    "cmd": "bash ArcaCognitorium.sh",       "cwd": "~/ArcaCognitorium/"},
    {"label": "✦ DOLIUM ✦",   "cmd": "bash ~/ArcaCognitorium/tools/Dolium/main.py",       "cwd": "~/ArcaCognitorium/tools/Dolium/"},
    {"label": "✦ VIGILARUM ✦","cmd": "bash ~/ArcaCognitorium/Exocognii/Vigilarum/Vigilarum.sh", "cwd": "~/ArcaCognitorium/Exocognii/Vigilarum/"},
    {"label": "✦ MYTHOTEX ✦", "cmd": "bash ~/ArcaCognitorium/Exocognii/Mythotex/Mythotex-FP.sh",  "cwd": "~/ArcaCognitorium/Exocognii/Mythotex/"},
    {"label": "✦ ENTITEX ✦", "cmd": "bash ~/ArcaCognitorium/Exocognii/Entitex/Entitex.sh",  "cwd": "~/ArcaCognitorium/Exocognii/Entitex/"},
    {"label": "✦ Lexiferium ✦", "cmd": "bash ~/ArcaCognitorium/Exocognii/Lexiferium/Lexifer.sh", "cwd": "~/ArcaCognitorium/Exocognii/Lexiferium",},
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

