# Departamentum Documentalis · main_window.py · v1.1
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStackedWidget, QPushButton)
from PyQt6.QtCore import Qt
from DepartamentumDocumentalis.feature_codex    import FeatureCodex
from DepartamentumDocumentalis.forma_registry   import FormaRegistry
from DepartamentumDocumentalis.forma_editor     import FormaEditor
from DepartamentumDocumentalis.scriptorium      import Scriptorium
from DepartamentumDocumentalis.document_archive import DocumentArchive
from DepartamentumDocumentalis.propagatio_engine import PropagatiEngine
from DepartamentumDocumentalis.mandate_bench    import MandateBench

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Departamentum Documentalis")
        self.setMinimumSize(1100, 700)
        self._build_ui()

    def _build_ui(self):
        root = QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)

        fascia = QWidget(); fascia.setObjectName("fascia"); fascia.setFixedHeight(52)
        fl = QHBoxLayout(fascia); fl.setContentsMargins(8,0,8,0); fl.setSpacing(6)
        fl.addStretch()
        help_btn = QPushButton("HELP"); help_btn.setObjectName("fascia_button_help")
        fl.addWidget(help_btn)
        outer.addWidget(fascia)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._codex = FeatureCodex(); self._codex.setFixedWidth(220)
        self._codex.feature_selected.connect(self._switch)

        self._stack = QStackedWidget(); self._stack.setObjectName("canvas")
        self._feats = {}

        fr = FormaRegistry(); fe = FormaEditor(); sc = Scriptorium()
        da = DocumentArchive(); pe = PropagatiEngine(); mb = MandateBench()

        for key, w in [("forma_registry",fr),("forma_editor",fe),("scriptorium",sc),
                        ("document_archive",da),("propagatio",pe),("mandate_bench",mb)]:
            self._feats[key] = w; self._stack.addWidget(w)

        fe.dirty_changed.connect(lambda d: self._codex.set_dirty("forma_editor", d))
        sc.dirty_changed.connect(lambda d: self._codex.set_dirty("scriptorium", d))
        fr.forma_selected.connect(self._open_in_editor)
        fr.new_forma_requested.connect(lambda: self._switch("forma_editor"))

        splitter.addWidget(self._codex); splitter.addWidget(self._stack)
        splitter.setCollapsible(0, False); splitter.setCollapsible(1, False)
        outer.addWidget(splitter)
        self._codex.select_first()

    def _switch(self, key):
        w = self._feats.get(key)
        if w: self._stack.setCurrentWidget(w)

    def _open_in_editor(self, forma_id):
        self._switch("forma_editor")
        self._codex._select("forma_editor")
        self._feats["forma_editor"].load_forma(forma_id)
