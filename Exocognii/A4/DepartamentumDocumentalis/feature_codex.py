# Departamentum Documentalis · feature_codex.py · v1.1
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

FEATURES = [
    ("forma_registry",   "Forma Registry"),
    ("forma_editor",     "Forma Editor"),
    ("scriptorium",      "Scriptorium"),
    ("document_archive", "Document Archive"),
    ("propagatio",       "Propagatio Engine"),
    ("mandate_bench",    "Mandate Bench"),
]

class FeatureCodex(QWidget):
    feature_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("left_rail")
        self._dirty: set = set()
        self._buttons: dict = {}
        self._dirty_labels: dict = {}
        self._current = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._build_titulum(layout)
        for key, label in FEATURES:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            btn = QPushButton(label)
            btn.setObjectName("nav_button")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, k=key: self._select(k))
            self._buttons[key] = btn
            dirty = QLabel("⬦")
            dirty.setObjectName("dirty_marker")
            dirty.setFixedWidth(16)
            dirty.setVisible(False)
            self._dirty_labels[key] = dirty
            row.addWidget(btn)
            row.addWidget(dirty)
            w = QWidget(); w.setLayout(row)
            layout.addWidget(w)
        layout.addStretch()

    def _build_titulum(self, layout):
        pane = QWidget(); pane.setObjectName("titulum")
        vl = QVBoxLayout(pane)
        vl.setContentsMargins(10, 12, 10, 12); vl.setSpacing(2)
        for text, obj in [
            ("DEPARTAMENTUM",                          "title_primary"),
            ("DOCUMENTALIS",                           "title_primary"),
            ("Dept. of Documented Design Definitives", "title_sub"),
            ("Define! Designa! Denota! Discede!",      "title_motto"),
        ]:
            lbl = QLabel(text); lbl.setObjectName(obj); lbl.setWordWrap(True)
            vl.addWidget(lbl)
        layout.addWidget(pane)

    def _select(self, key: str):
        if self._current and self._current in self._buttons:
            self._buttons[self._current].setChecked(False)
        self._current = key
        self._buttons[key].setChecked(True)
        self.feature_selected.emit(key)

    def set_dirty(self, key: str, dirty: bool):
        if dirty: self._dirty.add(key)
        else:     self._dirty.discard(key)
        if key in self._dirty_labels:
            self._dirty_labels[key].setVisible(dirty)

    def select_first(self):
        if FEATURES:
            self._select(FEATURES[0][0])
