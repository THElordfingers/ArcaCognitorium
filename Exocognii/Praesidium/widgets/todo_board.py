"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ████████  ██████  ██████   ██████          ██████   ██████   █████  ██████  ██████  ▍
🮈     ██    ██    ██ ██   ██ ██    ██         ██   ██ ██    ██ ██   ██ ██   ██ ██   ██ ▍
🮈     ██    ██    ██ ██   ██ ██    ██         ██████  ██    ██ ███████ ██████  ██   ██ ▍
🮈     ██    ██    ██ ██   ██ ██    ██         ██   ██ ██    ██ ██   ██ ██   ██ ██   ██ ▍
🮈     ██     ██████  ██████   ██████  ███████ ██████   ██████  ██   ██ ██   ██ ██████  ▍
🮈                                                                                      ▍
🮈                                                                                      ▍
🮈                                    Python Script                                     ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# PRAESIDIUM · widgets/todo_board.py
# TODO / Notice board. JSON-backed persistence. Add, complete, delete items.
# version: 1.0.0
"""
import json
import uuid
from pathlib import Path

from PyQt6.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFrame, QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_PANEL,
    C_SUBTLE, C_TEAL, C_CRIMSON,
    arcane_button, micro_label,
)


class TodoBoard(ArcaneWidget):
    """
    Persistent notice board.
    Items stored at storage/widget_state/todo_board.json.
    Check to complete; ✕ to delete.
    """

    def __init__(self, widget_id: str, storage_path: Path, parent=None):
        super().__init__(widget_id, "Todo · Notice Board", parent)
        self._path  = Path(storage_path) / "widget_state" / "todo_board.json"
        self._items: list[dict] = []
        self._load()
        self._build_body()
        self.set_status("idle", "")

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(4)
        self._input = QLineEdit()
        self._input.setPlaceholderText("Add note…")
        self._input.setStyleSheet(
            f"QLineEdit {{"
            f"  background: {C_BG}; color: {C_TEXT};"
            f"  border: 1px solid {C_GOLD_DARK};"
            f"  font-family: Georgia, serif; font-size: 10px; padding: 3px 6px;"
            f"}}"
            f"QLineEdit:focus {{ border-color: {C_GOLD}; }}"
        )
        self._input.returnPressed.connect(self._add_item)
        input_row.addWidget(self._input)

        btn_add = arcane_button("+ ADD")
        btn_add.setFixedHeight(24)
        btn_add.clicked.connect(self._add_item)
        input_row.addWidget(btn_add)
        L.addLayout(input_row)

        L.addWidget(self._sep())

        # Scroll area for items
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: {C_BG}; }}"
        )
        self._list_widget = QWidget()
        self._list_widget.setStyleSheet(f"background: {C_BG};")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()
        self._scroll.setWidget(self._list_widget)
        L.addWidget(self._scroll)

        self._render_items()

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    # ------------------------------------------------------------------
    # Item rendering
    # ------------------------------------------------------------------

    def _render_items(self) -> None:
        # Clear existing rows (keep the stretch at end)
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for rec in self._items:
            row = self._make_row(rec)
            self._list_layout.insertWidget(self._list_layout.count() - 1, row)

        pending = sum(1 for r in self._items if not r.get("done"))
        self.set_status("ok" if pending == 0 else "warn", f"{pending} open")

    def _make_row(self, rec: dict) -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background: {C_BG};")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 2, 0, 2)
        row.setSpacing(6)

        done = rec.get("done", False)

        # Check toggle
        check = QPushButton("☑" if done else "☐")
        check.setFixedSize(20, 20)
        check.setStyleSheet(
            f"QPushButton {{ background: transparent; color: "
            f"{'#1a9a1a' if done else C_GOLD_DIM}; border: none; font-size: 12px; }}"
            f"QPushButton:hover {{ color: {C_TEAL}; }}"
        )
        item_id = rec["id"]
        check.clicked.connect(lambda _, i=item_id: self._toggle(i))
        row.addWidget(check)

        # Text
        text = QLabel(rec["text"])
        text.setWordWrap(True)
        colour = C_GOLD_DIM if done else C_TEXT
        strike = "text-decoration: line-through;" if done else ""
        text.setStyleSheet(
            f"color: {colour}; font-family: Georgia, serif; font-size: 10px; {strike}"
        )
        row.addWidget(text, 1)

        # Delete
        btn_del = QPushButton("✕")
        btn_del.setFixedSize(16, 16)
        btn_del.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {C_GOLD_DARK}; border: none; font-size: 9px; }}"
            f"QPushButton:hover {{ color: {C_CRIMSON}; }}"
        )
        btn_del.clicked.connect(lambda _, i=item_id: self._delete(i))
        row.addWidget(btn_del)

        return container

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _add_item(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._items.insert(0, {"id": str(uuid.uuid4()), "text": text, "done": False})
        self._input.clear()
        self._save()
        self._render_items()

    def _toggle(self, item_id: str) -> None:
        for rec in self._items:
            if rec["id"] == item_id:
                rec["done"] = not rec["done"]
                break
        self._save()
        self._render_items()

    def _delete(self, item_id: str) -> None:
        self._items = [r for r in self._items if r["id"] != item_id]
        self._save()
        self._render_items()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            self._items = json.loads(self._path.read_text())
        except Exception:
            self._items = []

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self._items, indent=2))
            tmp.replace(self._path)
        except Exception:
            pass

