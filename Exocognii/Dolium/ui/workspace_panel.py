"""
ui/workspace_panel.py — Dolium v2
WorkspacePanel: centre panel with chamber-gated ArcaneField surfaces.
QTimer debounce triggers ambient whispers after 1500ms typing inactivity.
Gate bar at bottom with advance / return / cull.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QStackedWidget, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import style
from models import Idea, CHAMBER_NAMES
from store import IdeaStore
from chambers import GateEngine
from ui.widgets import ArcaneField, GateBar


# ── Field definitions per chamber ─────────────────────────────────────────────

CHAMBER_FIELDS = {
    1: [
        dict(field_name="title",      label="TITLE",      placeholder="Name this idea.",      min_height=44,  required=True),
        dict(field_name="body",       label="BODY",       placeholder="What is it?",          min_height=120, required=True),
        dict(field_name="motivation", label="MOTIVATION", placeholder="Why does it matter?",  min_height=80,  required=True),
    ],
    2: [
        dict(field_name="elaboration", label="ELABORATION", placeholder="Say more than you did in the Fomentary.", min_height=140, required=True),
        dict(field_name="obstacles",   label="OBSTACLES",   placeholder="What stands in the way? Be honest.",     min_height=80,  required=True),
        dict(field_name="first_step",  label="FIRST STEP",  placeholder="One specific executable act.",           min_height=60,  required=True),
    ],
    3: [
        dict(field_name="refined_form",  label="REFINED FORM",  placeholder="State what this would be if finished.",     min_height=120, required=True),
        dict(field_name="open_problems", label="OPEN PROBLEMS", placeholder="What is genuinely unresolved?",             min_height=80,  required=True),
        dict(field_name="next_actions",  label="NEXT ACTIONS",  placeholder="Concrete steps beyond the first.",          min_height=80,  required=True),
    ],
    4: [
        dict(field_name="declaration", label="DECLARATION", placeholder="State it plainly, as if to a stranger.", min_height=100, required=True),
        dict(field_name="summary",     label="SUMMARY",     placeholder="One to three sentences.",                min_height=70,  required=True),
        dict(field_name="tags",        label="TAGS",        placeholder="space-separated tags",                   min_height=40,  required=False),
    ],
}


class WorkspacePanel(QWidget):

    field_changed     = pyqtSignal(str, str)         # (field_name, text)
    whisper_requested = pyqtSignal(str, str, object) # (field_name, text, idea)
    advance_requested = pyqtSignal()
    return_requested  = pyqtSignal()
    cull_requested    = pyqtSignal()

    def __init__(self, store: IdeaStore, parent=None):
        super().__init__(parent)
        self._store       = store
        self._idea: Idea | None = None
        self._fields: dict[str, ArcaneField] = {}
        self._pending_field = ""
        self._pending_text  = ""

        # Debounce timer — created on main thread, lives here permanently
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(1500)
        self._debounce.timeout.connect(self._on_debounce_fire)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Chamber header ────────────────────────────────────────────────────
        self._chamber_header = QWidget()
        self._chamber_header.setStyleSheet(f"""
            background-color: {style.C_PANEL};
            border-bottom: 1px solid {style.C_BORDER};
        """)
        ch_layout = QHBoxLayout(self._chamber_header)
        ch_layout.setContentsMargins(12, 8, 12, 8)

        self._chamber_label = QLabel("—")
        self._chamber_label.setStyleSheet(f"""
            QLabel {{
                color: {style.C_GOLD};
                font-family: Georgia, Constantia, serif;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        self._idea_title_label = style.dim_label("", size=10)

        ch_layout.addWidget(self._chamber_label)
        ch_layout.addSpacing(10)
        ch_layout.addWidget(self._idea_title_label)
        ch_layout.addStretch()
        layout.addWidget(self._chamber_header)

        # ── Scrollable field area ─────────────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(self._scroll.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(f"background-color: {style.C_BG};")

        self._field_container = QWidget()
        self._field_container.setStyleSheet(f"background-color: {style.C_BG};")
        self._field_layout = QVBoxLayout(self._field_container)
        self._field_layout.setContentsMargins(14, 12, 14, 12)
        self._field_layout.setSpacing(14)

        self._empty_label = style.dim_label("Select or create an idea to begin.", size=11)
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._field_layout.addWidget(self._empty_label)
        self._field_layout.addStretch()

        self._scroll.setWidget(self._field_container)
        layout.addWidget(self._scroll, stretch=1)

        # ── Gate bar ──────────────────────────────────────────────────────────
        self._gate_bar = GateBar()
        self._gate_bar.setVisible(False)
        self._gate_bar.advance_requested.connect(self.advance_requested)
        self._gate_bar.return_requested.connect(self.return_requested)
        self._gate_bar.cull_requested.connect(self.cull_requested)
        layout.addWidget(self._gate_bar)

    # ── Public API ────────────────────────────────────────────────────────────

    def load_idea(self, idea: Idea) -> None:
        """Load an idea into the workspace. Rebuilds field set for the chamber."""
        self._idea = idea
        self._rebuild_fields()
        self._populate_fields()
        self._refresh_gate()
        self._gate_bar.setVisible(True)
        self._chamber_label.setText(f"▸  {idea.chamber_name()}")
        self._idea_title_label.setText(idea.title or "(untitled)")

    def clear(self) -> None:
        """Reset to empty state."""
        self._idea = None
        self._clear_fields()
        self._gate_bar.setVisible(False)
        self._chamber_label.setText("—")
        self._idea_title_label.setText("")

    def refresh_gate(self) -> None:
        self._refresh_gate()

    def get_field_text(self, field_name: str) -> str:
        f = self._fields.get(field_name)
        return f.get_text() if f else ""

    # ── Field management ──────────────────────────────────────────────────────

    def _rebuild_fields(self) -> None:
        if not self._idea:
            return

        self._clear_fields()
        self._empty_label.setVisible(False)

        chamber_def = CHAMBER_FIELDS.get(self._idea.chamber, CHAMBER_FIELDS[1])
        for kwargs in chamber_def:
            field = ArcaneField(**kwargs)
            field.text_changed.connect(self._on_field_changed)
            self._fields[kwargs["field_name"]] = field
            self._field_layout.insertWidget(self._field_layout.count() - 1, field)

    def _clear_fields(self) -> None:
        for field in self._fields.values():
            self._field_layout.removeWidget(field)
            field.deleteLater()
        self._fields.clear()
        self._empty_label.setVisible(True)

    def _populate_fields(self) -> None:
        if not self._idea:
            return
        for field_name, field_widget in self._fields.items():
            # Tags field: join list to space-separated string
            if field_name == "tags":
                value = " ".join(self._idea.tags)
            else:
                value = getattr(self._idea, field_name, "")
            field_widget.set_text(value)

    def _refresh_gate(self) -> None:
        if not self._idea:
            return
        result = GateEngine.gate_for_current_chamber(self._idea)
        self._gate_bar.update_gate(result, self._idea.chamber)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_field_changed(self, field_name: str, text: str) -> None:
        if not self._idea:
            return

        # Update in-memory idea attribute
        if field_name == "tags":
            self._idea.tags = [t.strip() for t in text.split() if t.strip()]
        else:
            setattr(self._idea, field_name, text)

        # Persist
        self._store.update(self._idea)

        # Refresh gate
        self._refresh_gate()

        # Update header title if title field changed
        if field_name == "title":
            self._idea_title_label.setText(text or "(untitled)")

        # Signal up to main window (for pipeline refresh etc.)
        self.field_changed.emit(field_name, text)

        # Reset debounce — only for meaningful text fields
        if field_name not in ("tags",) and len(text.strip()) >= 60:
            self._pending_field = field_name
            self._pending_text  = text
            self._debounce.start()

    def _on_debounce_fire(self) -> None:
        if self._idea and self._pending_field and self._pending_text:
            self.whisper_requested.emit(
                self._pending_field,
                self._pending_text,
                self._idea,
            )
