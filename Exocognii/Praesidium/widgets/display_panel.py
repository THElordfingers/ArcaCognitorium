#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widgets/display_panel.py                                       ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/display_panel.py
# Universal renderer — plain, markdown, diff, image.
# Multi-instance. Accepts drag-and-drop file drops.
# version: 1.0.0

from pathlib import Path

from PyQt6.QtWidgets import (
    QTextEdit, QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QComboBox, QSizePolicy, QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QDragEnterEvent, QDropEvent

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_PANEL,
    C_TEAL, C_CRIMSON,
    arcane_button, micro_label,
)

RENDER_MODES = ("plain", "markdown", "diff", "image")


class DisplayPanel(ArcaneWidget):
    """
    Universal renderer. Multi-instance capable.
    Modes: plain | markdown | diff | image
    Accepts file drops — infers mode from extension.
    """

    content_set = pyqtSignal(str, str)   # panel_id, summary

    def __init__(self, widget_id: str, parent=None):
        super().__init__(widget_id, "Display Panel", parent)
        self._mode = "plain"
        self._build_body()
        self.setAcceptDrops(True)
        self.set_status("idle", "Drop a file or call set_content()")

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Mode + controls row
        row = QHBoxLayout()
        row.setSpacing(6)
        row.addWidget(micro_label("mode"))

        self._mode_combo = QComboBox()
        self._mode_combo.addItems([m.upper() for m in RENDER_MODES])
        self._mode_combo.setStyleSheet(
            f"QComboBox {{ background: {C_BG}; color: {C_GOLD};"
            f"  border: 1px solid {C_GOLD_DARK}; font-family: Georgia, serif;"
            f"  font-size: 10px; padding: 2px 6px; }}"
            f"QComboBox QAbstractItemView {{"
            f"  background: {C_PANEL}; color: {C_TEXT};"
            f"  selection-background-color: {C_GOLD_DARK}; }}"
        )
        self._mode_combo.currentTextChanged.connect(
            lambda t: self._set_mode(t.lower())
        )
        row.addWidget(self._mode_combo)

        btn_clear = arcane_button("✕ CLEAR")
        btn_clear.setFixedHeight(22)
        btn_clear.clicked.connect(self.clear)
        row.addWidget(btn_clear)
        row.addStretch()
        L.addLayout(row)
        L.addWidget(self._sep())

        # Text area (plain / markdown / diff)
        self._text_area = QTextEdit()
        self._text_area.setReadOnly(True)
        self._text_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._text_area.setStyleSheet(
            f"QTextEdit {{ background: {C_BG}; color: {C_TEXT};"
            f"  border: none; font-family: Georgia, Constantia, serif;"
            f"  font-size: 11px; padding: 6px; }}"
        )
        L.addWidget(self._text_area, 1)

        # Image area (hidden by default)
        self._image_scroll = QScrollArea()
        self._image_scroll.setWidgetResizable(True)
        self._image_scroll.setVisible(False)
        self._image_scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: {C_BG}; }}"
        )
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setStyleSheet(f"background: {C_BG};")
        self._image_scroll.setWidget(self._image_label)
        L.addWidget(self._image_scroll, 1)

        # Drop hint
        self._drop_hint = QLabel("✦  Drop a file here")
        self._drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_hint.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
            "font-size: 10px; font-style: italic;"
        )
        L.addWidget(self._drop_hint)

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_content(self, content: str, mode: str = "plain") -> None:
        self._drop_hint.hide()
        # Block combo signal to avoid double-render
        self._mode_combo.blockSignals(True)
        self._mode_combo.setCurrentText(mode.upper())
        self._mode_combo.blockSignals(False)
        self._set_mode(mode)
        if mode == "plain":
            self._render_plain(content)
        elif mode == "markdown":
            self._render_markdown(content)
        elif mode == "diff":
            self._render_diff(content)
        else:
            self._render_plain(content)
        self.set_status("ok", f"{len(content):,} chars")
        self.content_set.emit(self.widget_id, content[:80])

    def set_image(self, path: str) -> None:
        self._set_mode("image")
        self._mode_combo.setCurrentText("IMAGE")
        self._render_image(path)

    def clear(self) -> None:
        self._text_area.clear()
        self._image_label.clear()
        self._drop_hint.show()
        self.set_status("idle", "")

    # ------------------------------------------------------------------
    # Mode switching
    # ------------------------------------------------------------------

    def _set_mode(self, mode: str) -> None:
        self._mode = mode
        is_image = (mode == "image")
        self._text_area.setVisible(not is_image)
        self._image_scroll.setVisible(is_image)

        if mode == "diff":
            self._text_area.setFont(QFont("Courier New", 10))
        else:
            self._text_area.setFont(QFont("Georgia", 11))

    # ------------------------------------------------------------------
    # Renderers
    # ------------------------------------------------------------------

    def _render_plain(self, content: str) -> None:
        # setPlainText preserves all whitespace, tabs, newlines exactly
        self._text_area.setFont(__import__('PyQt6.QtGui', fromlist=['QFont']).QFont("Courier New", 10))
        self._text_area.setPlainText(content)

    def _render_markdown(self, content: str) -> None:
        # Basic markdown → HTML without external deps
        import re
        html = content
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3 style="color:#7a4a9a">\1</h3>', html, flags=re.M)
        html = re.sub(r'^## (.+)$',  r'<h2 style="color:#1a5a5a">\1</h2>', html, flags=re.M)
        html = re.sub(r'^# (.+)$',   r'<h1 style="color:#d4af37">\1</h1>', html, flags=re.M)
        # Bold / italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)
        html = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', html)
        # Code inline
        html = re.sub(r'`(.+?)`', r'<code style="background:#1A1040;color:#7EC8C8;padding:1px 4px">\1</code>', html)
        # Line breaks
        html = html.replace('\n', '<br>')
        self._text_area.setHtml(
            f'<div style="color:{C_TEXT};font-family:Georgia,serif;font-size:11px">{html}</div>'
        )

    def _render_diff(self, content: str) -> None:
        html_lines = []
        for line in content.splitlines():
            if line.startswith('+') and not line.startswith('+++'):
                colour = "#1a6a1a"
            elif line.startswith('-') and not line.startswith('---'):
                colour = "#6a1a1a"
            elif line.startswith('@@'):
                colour = "#1a5a5a"
            elif line.startswith('diff ') or line.startswith('index '):
                colour = "#7a6a2a"
            else:
                colour = C_GOLD_DIM
            escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_lines.append(
                f'<div style="color:{colour};font-family:Courier New,monospace;font-size:10px">{escaped}</div>'
            )
        self._text_area.setHtml("".join(html_lines))

    def _render_image(self, path: str) -> None:
        px = QPixmap(path)
        if px.isNull():
            self._image_label.setText(f"✕  Could not load: {path}")
            self.set_status("error", "Image load failed")
            return
        scaled = px.scaled(
            self._image_scroll.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)
        self.set_status("ok", Path(path).name)

    # ------------------------------------------------------------------
    # Drag and drop
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        ext  = Path(path).suffix.lower()

        if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"):
            self.set_image(path)
        elif ext in (".diff", ".patch"):
            self.set_content(Path(path).read_text(errors="replace"), mode="diff")
        elif ext in (".md", ".markdown"):
            self.set_content(Path(path).read_text(errors="replace"), mode="markdown")
        else:
            try:
                self.set_content(Path(path).read_text(errors="replace"), mode="plain")
            except Exception as e:
                self.set_status("error", str(e)[:60])
