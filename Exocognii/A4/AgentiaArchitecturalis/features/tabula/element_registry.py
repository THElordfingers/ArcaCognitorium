"""
Element Registry — 28 element types across 7 categories.

Each entry defines: display_name, element_type key, category, default width/height,
and whether the element accepts children (is a container).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ElementDef:
    """Definition of a palette element type."""
    display_name: str
    element_type: str
    category: str
    default_width: int
    default_height: int
    accepts_children: bool = False


# ── Receptacula (Containers) ────────────────────────────────────
RECEPTACULA = [
    ElementDef("QFrame",      "QFrame",      "Receptacula", 300, 200, True),
    ElementDef("QGroupBox",   "QGroupBox",   "Receptacula", 280, 180, True),
    ElementDef("QSplitter",   "QSplitter",   "Receptacula", 400, 200, True),
    ElementDef("QTabWidget",  "QTabWidget",  "Receptacula", 350, 220, True),
]

# ── Ingressus (Inputs) ─────────────────────────────────────────
INGRESSUS = [
    ElementDef("QLineEdit",   "QLineEdit",   "Ingressus",  220, 32,  False),
    ElementDef("QComboBox",   "QComboBox",   "Ingressus",  180, 32,  False),
    ElementDef("QSlider",     "QSlider",     "Ingressus",  200, 24,  False),
    ElementDef("QSpinBox",    "QSpinBox",    "Ingressus",  100, 32,  False),
    ElementDef("QTextEdit",   "QTextEdit",   "Ingressus",  260, 120, False),
    ElementDef("QCheckBox",   "QCheckBox",   "Ingressus",  160, 24,  False),
    ElementDef("QRadioButton","QRadioButton","Ingressus",  160, 24,  False),
]

# ── Ostensio (Display) ─────────────────────────────────────────
OSTENSIO = [
    ElementDef("Label (Gold)",  "QLabel_gold",  "Ostensio", 200, 28, False),
    ElementDef("Label (Dim)",   "QLabel_dim",   "Ostensio", 200, 28, False),
    ElementDef("Label (Micro)", "QLabel_micro", "Ostensio", 150, 20, False),
    ElementDef("QProgressBar",  "QProgressBar", "Ostensio", 220, 22, False),
]

# ── Actiones (Buttons) ─────────────────────────────────────────
ACTIONES = [
    ElementDef("Btn (Gold)",    "ArcaneButton_gold",    "Actiones", 140, 34, False),
    ElementDef("Btn (Teal)",    "ArcaneButton_teal",    "Actiones", 140, 34, False),
    ElementDef("Btn (Crimson)", "ArcaneButton_crimson", "Actiones", 140, 34, False),
    ElementDef("ToggleButton",  "ToggleButton",         "Actiones", 140, 34, False),
]

# ── Tabulae (Tables) ───────────────────────────────────────────
TABULAE = [
    ElementDef("QTableView",  "QTableView",  "Tabulae", 460, 260, False),
]

# ── Composita (Pre-built patterns) ─────────────────────────────
COMPOSITA = [
    ElementDef("TopBar",         "TopBar",         "Composita", 500, 48,  True),
    ElementDef("StatusBar",      "StatusBar",      "Composita", 500, 26,  False),
    ElementDef("ControlPanel",   "ControlPanel",   "Composita", 220, 400, True),
    ElementDef("SectionHeader",  "SectionHeader",  "Composita", 300, 32,  False),
    ElementDef("SwatchStrip",    "SwatchStrip",    "Composita", 400, 24,  False),
]

# ── Ornamentum (Decorative) ────────────────────────────────────
ORNAMENTUM = [
    ElementDef("Separator",  "Separator",  "Ornamentum", 300, 2,  False),
    ElementDef("Spacer",     "Spacer",     "Ornamentum", 100, 40, False),
    ElementDef("RuleLine",   "RuleLine",   "Ornamentum", 300, 2,  False),
]

# ── All categories in palette order ─────────────────────────────
CATEGORIES = [
    ("Receptacula", RECEPTACULA),
    ("Ingressus",   INGRESSUS),
    ("Ostensio",    OSTENSIO),
    ("Actiones",    ACTIONES),
    ("Tabulae",     TABULAE),
    ("Composita",   COMPOSITA),
    ("Ornamentum",  ORNAMENTUM),
]

# ── Flat registry lookup ────────────────────────────────────────
ALL_ELEMENTS: list[ElementDef] = []
ELEMENT_MAP: dict[str, ElementDef] = {}

for _cat_name, _cat_list in CATEGORIES:
    for edef in _cat_list:
        ALL_ELEMENTS.append(edef)
        ELEMENT_MAP[edef.element_type] = edef


def get_element_def(element_type: str) -> ElementDef | None:
    """Look up an element definition by type key."""
    return ELEMENT_MAP.get(element_type)
