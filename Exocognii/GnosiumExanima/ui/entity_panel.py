# GNOSIUM EXANIMA — ui/entity_panel.py
# v1.0.0
"""Entity roster panel — portraits, name, toggles, mode switch."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QButtonGroup, QCheckBox, QFrame, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QScrollArea, QVBoxLayout, QWidget,
)

from ..constants import (
    C_BG, C_GOLD, C_GOLD_DARK, C_GOLD_DIM, C_PANEL, C_TEXT,
    ENTITY_PANEL_WIDTH, FONT_STACK, FONT_STACK_HEAD,
    MODE_CHAMBER, MODE_SOLO, PORTRAIT_THUMB_PX,
)
from ..entity.models import EntityPackage
from ..entity.portrait import PortraitCache


class EntityPanel(QWidget):
    """
    Left-side roster. Emits:
      - mode_changed(str)               — when the Wizard flips modes
      - selection_changed(list[str])    — when the active-entity set changes
    """

    mode_changed = pyqtSignal(str)
    selection_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = MODE_CHAMBER
        self._entities: list[EntityPackage] = []
        self._portraits = PortraitCache()
        self._chamber_boxes: dict[str, QCheckBox] = {}
        self._solo_radios: dict[str, QRadioButton] = {}
        self._solo_group = QButtonGroup(self)
        self._solo_group.setExclusive(True)
        self._rows: dict[str, _EntityRow] = {}
        self._setup_ui()

    # ── Construction ─────────────────────────────────────────────
    def _setup_ui(self) -> None:
        self.setFixedWidth(ENTITY_PANEL_WIDTH)
        self.setStyleSheet(f"background: {C_BG};")

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # Header
        self._header = QLabel("CHAMBER")
        self._header.setFont(QFont("Cinzel", 11, QFont.Weight.Bold))
        self._header.setStyleSheet(
            f"color: {C_GOLD}; letter-spacing: 3px; border-bottom: 1px solid {C_GOLD_DARK}; padding-bottom: 6px;"
        )
        self._header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._header)

        # Mode toggle row
        mode_row = QHBoxLayout()
        mode_row.setSpacing(4)
        self._btn_chamber = self._mode_button("Chamber", True)
        self._btn_solo = self._mode_button("Solo", False)
        self._btn_chamber.clicked.connect(lambda: self._set_mode(MODE_CHAMBER))
        self._btn_solo.clicked.connect(lambda: self._set_mode(MODE_SOLO))
        mode_row.addWidget(self._btn_chamber)
        mode_row.addWidget(self._btn_solo)
        root.addLayout(mode_row)

        # Scroll area for entity list
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ background: {C_BG}; border: none; }}"
            f"QScrollBar:vertical {{ background: {C_PANEL}; width: 8px; }}"
            f"QScrollBar::handle:vertical {{ background: {C_GOLD_DARK}; min-height: 24px; }}"
        )
        self._list_host = QWidget()
        self._list_host.setStyleSheet(f"background: {C_BG};")
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 4, 0, 4)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch(1)
        self._scroll.setWidget(self._list_host)
        root.addWidget(self._scroll, 1)

    def _mode_button(self, text: str, active: bool) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setFont(QFont("Georgia", 9))
        btn.setStyleSheet(
            f"QPushButton {{ background: {C_PANEL}; color: {C_GOLD_DIM}; "
            f"border: 1px solid {C_GOLD_DARK}; padding: 4px 8px; }}"
            f"QPushButton:checked {{ color: {C_GOLD}; border-color: {C_GOLD}; }}"
        )
        return btn

    # ── Public API ───────────────────────────────────────────────
    def set_entities(self, entities: list[EntityPackage]) -> None:
        self._entities = list(entities)
        self._rebuild_list()

    def set_mode(self, mode: str) -> None:
        self._set_mode(mode, emit=False)

    def set_active(self, entity_ids: list[str]) -> None:
        active = set(entity_ids)
        for eid, box in self._chamber_boxes.items():
            box.blockSignals(True)
            box.setChecked(eid in active)
            box.blockSignals(False)
        for eid, radio in self._solo_radios.items():
            radio.blockSignals(True)
            radio.setChecked(eid in active)
            radio.blockSignals(False)
        self._restyle_rows()

    def active_entity_ids(self) -> list[str]:
        if self._mode == MODE_CHAMBER:
            return [eid for eid, box in self._chamber_boxes.items() if box.isChecked()]
        return [eid for eid, radio in self._solo_radios.items() if radio.isChecked()]

    # ── Internals ────────────────────────────────────────────────
    def _set_mode(self, mode: str, *, emit: bool = True) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        self._header.setText("CHAMBER" if mode == MODE_CHAMBER else "SOLO")
        self._btn_chamber.setChecked(mode == MODE_CHAMBER)
        self._btn_solo.setChecked(mode == MODE_SOLO)
        self._rebuild_list()
        if emit:
            self.mode_changed.emit(mode)

    def _rebuild_list(self) -> None:
        # Clear existing
        while self._list_layout.count() > 0:
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._chamber_boxes.clear()
        self._solo_radios.clear()
        for btn in list(self._solo_group.buttons()):
            self._solo_group.removeButton(btn)
        self._rows.clear()

        for entity in self._entities:
            row = _EntityRow(
                entity,
                mode=self._mode,
                portrait_cache=self._portraits,
                solo_group=self._solo_group,
            )
            self._list_layout.addWidget(row)
            self._rows[entity.entity_id] = row
            if self._mode == MODE_CHAMBER:
                self._chamber_boxes[entity.entity_id] = row.chamber_box
                row.chamber_box.stateChanged.connect(self._emit_selection)
            else:
                self._solo_radios[entity.entity_id] = row.solo_radio
                row.solo_radio.toggled.connect(self._emit_selection)

        self._list_layout.addStretch(1)
        self._restyle_rows()

    def _emit_selection(self, *_args) -> None:
        self._restyle_rows()
        self.selection_changed.emit(self.active_entity_ids())

    def _restyle_rows(self) -> None:
        active = set(self.active_entity_ids())
        for eid, row in self._rows.items():
            row.set_active(eid in active)


class _EntityRow(QFrame):
    """Single entity line: portrait + name + toggle."""

    def __init__(
        self,
        entity: EntityPackage,
        *,
        mode: str,
        portrait_cache: PortraitCache,
        solo_group: QButtonGroup,
    ):
        super().__init__()
        self.entity = entity
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(
            f"background: {C_PANEL}; border: 1px solid {C_GOLD_DARK};"
        )
        self.setFixedHeight(PORTRAIT_THUMB_PX + 12)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 6, 4)
        layout.setSpacing(6)

        # Portrait
        self.portrait_label = QLabel()
        self.portrait_label.setFixedSize(PORTRAIT_THUMB_PX, PORTRAIT_THUMB_PX)
        self.portrait_label.setPixmap(
            portrait_cache.load(entity.entity_id, entity.portrait_path)
        )
        self.portrait_label.setStyleSheet(
            f"background: {C_BG}; border: 1px solid {C_GOLD_DARK};"
        )
        layout.addWidget(self.portrait_label)

        # Name
        self.name_label = QLabel(entity.display_name)
        self.name_label.setFont(QFont("Georgia", 9))
        self.name_label.setStyleSheet(f"color: {C_TEXT};")
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label, 1)

        # Toggle
        if mode == MODE_CHAMBER:
            self.chamber_box = QCheckBox()
            self.chamber_box.setStyleSheet(
                f"QCheckBox::indicator {{ width: 14px; height: 14px; "
                f"border: 1px solid {C_GOLD_DIM}; background: {C_BG}; }}"
                f"QCheckBox::indicator:checked {{ background: {C_GOLD}; }}"
            )
            layout.addWidget(self.chamber_box)
            self.solo_radio = None
        else:
            self.solo_radio = QRadioButton()
            self.solo_radio.setStyleSheet(
                f"QRadioButton::indicator {{ width: 14px; height: 14px; "
                f"border: 1px solid {C_GOLD_DIM}; border-radius: 7px; "
                f"background: {C_BG}; }}"
                f"QRadioButton::indicator:checked {{ background: {C_GOLD}; }}"
            )
            solo_group.addButton(self.solo_radio)
            layout.addWidget(self.solo_radio)
            self.chamber_box = None

    def set_active(self, active: bool) -> None:
        border = C_GOLD if active else C_GOLD_DARK
        self.portrait_label.setStyleSheet(
            f"background: {C_BG}; border: 1px solid {border};"
        )
        self.setStyleSheet(
            f"background: {C_PANEL}; border: 1px solid {border};"
        )
