#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widgets/quick_file_drop.py                                     ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/quick_file_drop.py
# Drag-and-drop file ingest. Sends content to a DisplayPanel or clipboard.
# version: 1.0.0

import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QTextEdit, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG,
    C_TEAL, C_CRIMSON,
    arcane_button, micro_label,
)

MAX_PREVIEW_BYTES = 8_192


class QuickFileDrop(ArcaneWidget):
    """
    Drop zone for quick file inspection.
    - Text/code: previewed inline, copyable
    - Images: name + size shown, send to DisplayPanel
    - Any file: path shown, open-in-manager button

    Signals:
        file_dropped(path)   — emitted for every dropped file
        send_to_display(path, content, mode)  — route to DisplayPanel
    """

    file_dropped    = pyqtSignal(str)
    send_to_display = pyqtSignal(str, str, str)   # path, content, mode

    def __init__(self, widget_id: str, parent=None):
        super().__init__(widget_id, "Quick File Drop", parent)
        self._last_path: str | None = None
        self._build_body()
        self.setAcceptDrops(True)
        self.set_status("idle", "")

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Drop zone
        self._drop_zone = QFrame()
        self._drop_zone.setFixedHeight(60)
        self._drop_zone.setStyleSheet(
            f"QFrame {{ background: {C_BG}; border: 2px dashed {C_GOLD_DARK};"
            f"  border-radius: 4px; }}"
        )
        dz_layout = QVBoxLayout(self._drop_zone)
        self._drop_lbl = QLabel("✦  Drop a file here")
        self._drop_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_lbl.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
            "font-size: 10px; font-style: italic; border: none;"
        )
        dz_layout.addWidget(self._drop_lbl)
        L.addWidget(self._drop_zone)

        # File info row
        self._info_lbl = micro_label("")
        L.addWidget(self._info_lbl)

        # Action buttons (hidden until file dropped)
        self._btn_row = QHBoxLayout()
        self._btn_copy    = arcane_button("⎗ COPY PATH")
        self._btn_display = arcane_button("⊞ SEND TO DISPLAY")
        self._btn_open    = arcane_button("⊙ OPEN FOLDER")
        for btn in (self._btn_copy, self._btn_display, self._btn_open):
            btn.setFixedHeight(24)
            self._btn_row.addWidget(btn)
        self._btn_row.addStretch()
        L.addLayout(self._btn_row)
        self._set_btns_visible(False)

        L.addWidget(self._sep())

        # Preview
        L.addWidget(micro_label("preview"))
        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._preview.setFont(QFont("Courier New", 10))
        self._preview.setStyleSheet(
            f"QTextEdit {{ background: {C_BG}; color: {C_TEXT};"
            f"  border: 1px solid {C_GOLD_DARK}; font-size: 10px; padding: 4px; }}"
        )
        L.addWidget(self._preview, 1)

        # Wire buttons
        self._btn_copy.clicked.connect(self._copy_path)
        self._btn_display.clicked.connect(self._send_display)
        self._btn_open.clicked.connect(self._open_folder)

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    def _set_btns_visible(self, v: bool) -> None:
        for i in range(self._btn_row.count()):
            item = self._btn_row.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(v)

    # ------------------------------------------------------------------
    # Drop handling
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            self._drop_zone.setStyleSheet(
                f"QFrame {{ background: {C_BG}; border: 2px dashed {C_TEAL}; border-radius: 4px; }}"
            )
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:
        self._drop_zone.setStyleSheet(
            f"QFrame {{ background: {C_BG}; border: 2px dashed {C_GOLD_DARK}; border-radius: 4px; }}"
        )

    def dropEvent(self, event: QDropEvent) -> None:
        self._drop_zone.setStyleSheet(
            f"QFrame {{ background: {C_BG}; border: 2px dashed {C_GOLD_DARK}; border-radius: 4px; }}"
        )
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        self._ingest(path)

    # ------------------------------------------------------------------
    # Ingest
    # ------------------------------------------------------------------

    def _ingest(self, path: str) -> None:
        p = Path(path)
        self._last_path = path
        self.file_dropped.emit(path)

        size = p.stat().st_size if p.exists() else 0
        size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
        self._drop_lbl.setText(f"✦  {p.name}")
        self._info_lbl.setText(f"{p.suffix or 'file'}  ·  {size_str}  ·  {p.parent}")
        self._set_btns_visible(True)

        # Preview
        ext = p.suffix.lower()
        if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"):
            self._preview.setPlainText(f"[image: {p.name}  {size_str}]")
            self.set_status("ok", f"image: {p.name}")
        else:
            try:
                raw = p.read_bytes()[:MAX_PREVIEW_BYTES]
                try:
                    text = raw.decode("utf-8")
                    if len(raw) == MAX_PREVIEW_BYTES:
                        text += "\n\n… (truncated)"
                    self._preview.setPlainText(text)
                except UnicodeDecodeError:
                    self._preview.setPlainText(f"[binary file: {p.name}  {size_str}]")
                self.set_status("ok", p.name)
            except Exception as e:
                self._preview.setPlainText(f"✕  {e}")
                self.set_status("error", str(e)[:60])

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _copy_path(self) -> None:
        if not self._last_path:
            return
        try:
            subprocess.run(["xclip", "-selection", "clipboard"],
                           input=self._last_path, text=True, timeout=3)
            self.set_status("ok", "Path copied")
        except Exception:
            # fallback: Qt clipboard
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(self._last_path)
            self.set_status("ok", "Path copied")

    def _send_display(self) -> None:
        if not self._last_path:
            return
        p    = Path(self._last_path)
        ext  = p.suffix.lower()
        mode = "image" if ext in (".png",".jpg",".jpeg",".gif",".webp",".bmp") \
               else "diff" if ext in (".diff",".patch") \
               else "markdown" if ext in (".md",".markdown") \
               else "plain"
        try:
            content = p.read_text(errors="replace") if mode != "image" else self._last_path
            self.send_to_display.emit(self._last_path, content, mode)
            self.set_status("ok", "Sent to Display Panel")
        except Exception as e:
            self.set_status("error", str(e)[:60])

    def _open_folder(self) -> None:
        if not self._last_path:
            return
        folder = str(Path(self._last_path).parent)
        try:
            subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            self.set_status("error", str(e)[:60])
