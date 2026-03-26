"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ███████ ████████  █████  ████████ ██    ██ ███████         ██      ███████  ██████  ███████ ███    ██ ██████  ▍
🮈  ██         ██    ██   ██    ██    ██    ██ ██              ██      ██      ██       ██      ████   ██ ██   ██ ▍
🮈  ███████    ██    ███████    ██    ██    ██ ███████         ██      █████   ██   ███ █████   ██ ██  ██ ██   ██ ▍
🮈       ██    ██    ██   ██    ██    ██    ██      ██         ██      ██      ██    ██ ██      ██  ██ ██ ██   ██ ▍
🮈  ███████    ██    ██   ██    ██     ██████  ███████ ███████ ███████ ███████  ██████  ███████ ██   ████ ██████  ▍
🮈                                                                                                                ▍
🮈                                                                                                                ▍
🮈                                                 Python Script                                                 ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# PRAESIDIUM · widgets/status_legend.py
# Aggregated status display. Receives updates via update_slot().
# version: 1.0.0
"""


from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT,
    C_STATUS_OK, C_STATUS_WARN, C_STATUS_ERROR, C_STATUS_IDLE,
    micro_label,
)

SLOTS = [
    ("git",    "GIT"),
    ("chat",   "CHAT"),
    ("token",  "TOKEN"),
    ("exo",    "EXOCOGNII"),
]

_COLOUR = {
    "ok":    C_STATUS_OK,
    "warn":  C_STATUS_WARN,
    "error": C_STATUS_ERROR,
    "idle":  C_STATUS_IDLE,
}


class StatusLegend(ArcaneWidget):
    """
    Compact aggregated status widget.
    Each slot shows a coloured dot + label + optional message.
    Call update_slot(slot_id, status, message) from anywhere.
    """

    def __init__(self, widget_id: str, parent=None):
        super().__init__(widget_id, "Status Legend", parent)
        self._rows: dict[str, tuple[QLabel, QLabel]] = {}
        self._build_body()
        self.set_status("idle", "")

    def _build_body(self) -> None:
        L = self._body_layout
        for slot_id, label in SLOTS:
            row = QHBoxLayout()
            row.setSpacing(8)

            dot = QLabel("●")
            dot.setStyleSheet(
                f"color: {C_STATUS_IDLE}; font-size: 10px; font-family: Georgia, serif;"
            )
            row.addWidget(dot)

            name = QLabel(label)
            name.setStyleSheet(
                f"color: {C_GOLD_DIM}; font-size: 9px; font-family: Georgia, serif; letter-spacing: 2px;"
            )
            row.addWidget(name)

            msg = QLabel("—")
            msg.setStyleSheet(
                f"color: {C_TEXT}; font-size: 10px; font-family: Georgia, serif;"
            )
            row.addWidget(msg, 1)
            L.addLayout(row)

            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
            L.addWidget(sep)

            self._rows[slot_id] = (dot, msg)

        L.addStretch()

    def update_slot(self, slot_id: str, status: str, message: str = "") -> None:
        """Update a named slot. status: ok | warn | error | idle"""
        if slot_id not in self._rows:
            return
        dot, msg = self._rows[slot_id]
        colour = _COLOUR.get(status, C_STATUS_IDLE)
        dot.setStyleSheet(
            f"color: {colour}; font-size: 10px; font-family: Georgia, serif;"
        )
        msg.setText(message or "—")

