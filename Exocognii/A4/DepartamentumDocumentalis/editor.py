# Departamentum Documentalis — editor.py
# v1.0.0
"""Syntax-highlighted QPlainTextEdit for .bureau pipe-tag content."""

import re

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont,
)

from .constants import WIZDOC_COLORS


class BureauHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for .bureau pipe-tag format."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        # YAML front matter
        fmt_yaml = QTextCharFormat()
        fmt_yaml.setForeground(QColor(WIZDOC_COLORS['h5']))
        self._rules.append((re.compile(r'^---\s*$'), fmt_yaml))
        self._rules.append((re.compile(r'^\w+:.*$'), fmt_yaml))

        # Tag pipes |tag|
        fmt_tag = QTextCharFormat()
        fmt_tag.setForeground(QColor(WIZDOC_COLORS['h2']))
        fmt_tag.setFontWeight(QFont.Weight.Bold)
        self._rules.append((re.compile(r'\|/?(?:h[1-6]|body|bullet|code|table|th|tr|break|note|quote)\|'), fmt_tag))

        # Heading content after |h1|
        fmt_heading = QTextCharFormat()
        fmt_heading.setForeground(QColor(WIZDOC_COLORS['h1']))
        fmt_heading.setFontWeight(QFont.Weight.Bold)
        self._rules.append((re.compile(r'\|h[1-2]\|(.+?)\|'), fmt_heading))

        # Bold **text**
        fmt_bold = QTextCharFormat()
        fmt_bold.setForeground(QColor(WIZDOC_COLORS['title']))
        fmt_bold.setFontWeight(QFont.Weight.Bold)
        self._rules.append((re.compile(r'\*\*.+?\*\*'), fmt_bold))

        # Italic *text*
        fmt_italic = QTextCharFormat()
        fmt_italic.setForeground(QColor(WIZDOC_COLORS['body']))
        fmt_italic.setFontItalic(True)
        self._rules.append((re.compile(r'(?<!\*)\*(?!\*).+?(?<!\*)\*(?!\*)'), fmt_italic))

        # Inline code `text`
        fmt_code = QTextCharFormat()
        fmt_code.setForeground(QColor(WIZDOC_COLORS['code_text']))
        fmt_code.setBackground(QColor(WIZDOC_COLORS['code_bg']))
        fmt_code.setFontFamily('Courier New')
        self._rules.append((re.compile(r'`[^`]+`'), fmt_code))

        # Color spans {{token|text}}
        fmt_color = QTextCharFormat()
        fmt_color.setForeground(QColor(WIZDOC_COLORS['h3']))
        self._rules.append((re.compile(r'\{\{.+?\}\}'), fmt_color))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class BureauEditor(QWidget):
    """Complete .bureau editor panel with title and syntax highlighting."""

    content_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel('COMPOSITIO')
        title.setProperty('role', 'micro')
        layout.addWidget(title)

        self._editor = QPlainTextEdit()
        self._editor.setTabStopDistance(28)
        self._editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self._highlighter = BureauHighlighter(self._editor.document())
        self._editor.textChanged.connect(self.content_changed.emit)
        layout.addWidget(self._editor)

    def get_text(self) -> str:
        return self._editor.toPlainText()

    def set_text(self, text: str):
        self._editor.setPlainText(text)

    def clear(self):
        self._editor.clear()
