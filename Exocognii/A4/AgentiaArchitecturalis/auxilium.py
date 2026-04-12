"""
Auxilium — Per-Feature Contextual Help.

Non-modal. F1 opens for the currently active feature.
Content keyed to active feature — switching features updates content.
HELP button is the sole persistent Fascia element, always rightmost.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
)

from . import tokens


# ── Help Content per Feature ────────────────────────────────────

HELP_CONTENT = {
    "tabula": {
        "title": "Tabula Designandi",
        "overview": (
            "The Tabula Designandi is the primary design surface. Elements are dragged "
            "from the Elementarium and placed spatially on the canvas. Containers accept "
            "children dropped within their visible bounds \u2014 the child is reparented in "
            "the scene graph and constrained within the parent rect. The Inspector governs "
            "properties; the Specularium shows the rendered truth."
        ),
        "sections": [
            ("Fascia Controls", [
                ("Novum / Ctrl+N",        "Nova Tabula",     "New canvas. Prompts if unsaved changes detected."),
                ("Aperi / Ctrl+O",        "Aperi Canvam",    "Open named canvas session from disk."),
                ("Sigilla / Ctrl+S",      "Sigilla",         "Save canvas by name. Prompts for name if unsaved."),
                ("Sig. Ut / Ctrl+Shift+S","Sigilla Ut",      "Save canvas as new named session."),
                ("\u21a9 / Ctrl+Z",       "Revertere",       "Undo. 50-step stack."),
                ("\u21aa / Ctrl+Shift+Z", "Repete",          "Redo."),
                ("Dele / Del",            "Dele",            "Delete selected element."),
                ("Duplica / Ctrl+D",      "Duplica",         "Duplicate selected element."),
                ("Congrega / Ctrl+G",     "Congrega",        "Group selected element into a new QFrame container."),
            ]),
            ("Canvas Navigation", [
                ("Middle drag",          "Pan",              "Pan the canvas view over the scene."),
                ("Ctrl+Scroll",          "Zoom",             "Scale canvas 0.25\u00d7 \u2013 4\u00d7."),
                ("Drag from Elementarium","Place element",   "Drops onto a container to nest; onto canvas background for root placement."),
            ]),
        ],
    },
    "armarium": {
        "title": "Armarium Componentium",
        "overview": (
            "The bureau\u2019s institutional memory. Every sealed composition lives here, "
            "versioned, forkable, and exportable. Search, filter, load, or fork any saved component."
        ),
        "sections": [
            ("Operations", [
                ("Sigilla Canvas",   "Seal",    "Save current canvas as a library component."),
                ("Furca",            "Fork",    "Create a versioned duplicate with lineage preserved."),
                ("Exporta",          "Export",  "Generate and copy code for the selected component."),
            ]),
        ],
    },
    "specularium": {
        "title": "Specularium Vivum",
        "overview": (
            "Live preview of the current canvas design rendered as real PyQt6 widgets. "
            "Two renderer instances share a single data model. The floating window "
            "(Ctrl+P or Fenestra button) provides a detached view."
        ),
        "sections": [
            ("Controls", [
                ("Reconstruc",       "Rebuild",       "Force a full preview rebuild."),
                ("Cape Imaginem",    "Capture",       "Save a thumbnail of the current preview."),
                ("Fenestra / Ctrl+P","Float Window",  "Toggle the detached preview window."),
            ]),
        ],
    },
    "codex": {
        "title": "Codex Exportum",
        "overview": (
            "Canvas tree \u2192 validated PyQt6 code using token constants only (never raw hex). "
            "AST parse validates before delivery. Choose clipboard or file export."
        ),
        "sections": [
            ("Controls", [
                ("In Clipboard",    "Copy",     "Copy generated code to clipboard."),
                ("In Fasciculum",   "Save",     "Save generated code to a .py file."),
                ("Valida",          "Validate", "Run ast.parse() validation on generated code."),
            ]),
        ],
    },
    "thema": {
        "title": "Thema",
        "overview": (
            "A full browse surface for the active theme\u2019s token registry. All ten tokens, "
            "their values, and live swatches visible simultaneously. Bureau I is the sole writer "
            "of theme.json. Bureau II reads only."
        ),
        "sections": [
            ("Controls", [
                ("Onus theme.json",     "Load",     "Load a theme file from disk."),
                ("Applica & Repinge",   "Apply",    "Apply theme and repaint all canvas elements."),
                ("Reset",               "Reset",    "Reset to ModusArcanus defaults (Nox Aurum)."),
            ]),
        ],
    },
    "auxilium": {
        "title": "Auxilium",
        "overview": (
            "You are reading the help system. Press F1 or click the HELP button from any feature "
            "to see contextual help. Press Escape or click Dimitte to close."
        ),
        "sections": [],
    },
}


class AuxiliumFeature(QWidget):
    """Auxilium help content page."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_feature = "tabula"
        self._build_ui()
        self.set_feature("tabula")

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(16, 16, 16, 16)
        self._content_layout.setSpacing(8)

        scroll.setWidget(self._content)
        outer.addWidget(scroll)

    def set_feature(self, feature_key: str) -> None:
        """Update help content for the given feature."""
        self._current_feature = feature_key
        self._rebuild_content()

    def _rebuild_content(self) -> None:
        # Clear old content
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        data = HELP_CONTENT.get(self._current_feature, HELP_CONTENT["tabula"])

        # Overview
        head = QLabel("Overview")
        head.setStyleSheet(
            f"font-size: 8px; letter-spacing: 2px; color: {tokens.C_GOLD}; "
            f"text-transform: uppercase; border-bottom: 1px solid {tokens.C_GOLD_DARK}; "
            f"padding-bottom: 3px;"
        )
        self._content_layout.addWidget(head)

        overview = QLabel(data["overview"])
        overview.setWordWrap(True)
        overview.setStyleSheet(
            f"font-size: 10.5px; color: {tokens.C_TEXT}; font-style: italic; line-height: 1.7;"
        )
        self._content_layout.addWidget(overview)

        # Sections
        for sec_title, rows in data.get("sections", []):
            sec_head = QLabel(sec_title)
            sec_head.setStyleSheet(
                f"font-size: 8px; letter-spacing: 2px; color: {tokens.C_GOLD}; "
                f"text-transform: uppercase; border-bottom: 1px solid {tokens.C_GOLD_DARK}; "
                f"padding-bottom: 3px; margin-top: 10px;"
            )
            self._content_layout.addWidget(sec_head)

            for shortcut, action, desc in rows:
                row = QWidget()
                from PyQt6.QtWidgets import QHBoxLayout
                rl = QHBoxLayout(row)
                rl.setContentsMargins(0, 2, 0, 2)
                rl.setSpacing(12)

                sc = QLabel(shortcut)
                sc.setStyleSheet(f"color: {tokens.C_GOLD}; font-family: {tokens.FONT_MONO}; font-size: 9px; min-width: 130px;")
                sc.setFixedWidth(150)
                rl.addWidget(sc)

                act = QLabel(action)
                act.setStyleSheet(f"color: {tokens.C_TEXT}; font-family: {tokens.FONT_MONO}; font-size: 9px; min-width: 100px;")
                act.setFixedWidth(100)
                rl.addWidget(act)

                d = QLabel(desc)
                d.setWordWrap(True)
                d.setStyleSheet(f"color: {tokens.C_GOLD_DIM}; font-family: {tokens.FONT_MONO}; font-size: 9px; font-style: italic;")
                rl.addWidget(d, 1)

                self._content_layout.addWidget(row)

        self._content_layout.addStretch()
