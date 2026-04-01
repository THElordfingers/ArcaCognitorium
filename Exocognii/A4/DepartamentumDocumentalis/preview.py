# Departamentum Documentalis — preview.py
# v1.0.0
"""Live preview renderer — approximate wizdoc styling in QTextEdit."""

from PyQt6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QTextBlockFormat

from .schema import BureauDocument, BureauNode, InlineSpan
from .constants import WIZDOC_COLORS, WIZDOC_FONTS


class PreviewPanel(QWidget):
    """Approximate wizdoc-styled preview using QTextEdit rich text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel('SPECULARIUM')
        title.setProperty('role', 'micro')
        layout.addWidget(title)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setStyleSheet(
            f"QTextEdit {{ background: {WIZDOC_COLORS['bg']}; "
            f"color: {WIZDOC_COLORS['body']}; border: none; padding: 16px; }}"
        )
        layout.addWidget(self._preview)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self._rebuild)
        self._pending_doc = None

    def schedule_rebuild(self, doc: BureauDocument):
        self._pending_doc = doc
        self._timer.start()

    def _rebuild(self):
        if self._pending_doc is None:
            return
        self._preview.clear()
        cursor = self._preview.textCursor()

        # Title
        if self._pending_doc.header.title:
            self._insert_heading(cursor, self._pending_doc.header.title,
                                 'title', center=True)
            cursor.insertBlock()

        for node in self._pending_doc.nodes:
            self._render_node(cursor, node)

        self._preview.setTextCursor(cursor)
        self._preview.moveCursor(QTextCursor.MoveOperation.Start)

    def _render_node(self, cursor: QTextCursor, node: BureauNode):
        tag = node.tag

        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            text = node.content
            if tag == 'h1':
                text = text.upper()
            self._insert_heading(cursor, text, tag)
            cursor.insertBlock()

        elif tag == 'body':
            self._insert_inline(cursor, node.spans if node.spans else
                                [InlineSpan(text=node.content)])
            cursor.insertBlock()

        elif tag == 'bullet':
            fmt = self._make_format('body')
            cursor.insertText('  \u2022  ', fmt)
            self._insert_inline(cursor, node.spans if node.spans else
                                [InlineSpan(text=node.content)])
            cursor.insertBlock()

        elif tag == 'note':
            fmt = self._make_format('h5')
            fmt.setFontItalic(True)
            cursor.insertText(f'    {node.content}', fmt)
            cursor.insertBlock()

        elif tag == 'quote':
            fmt = self._make_format('h6')
            fmt.setFontItalic(True)
            cursor.insertText(f'    \u201c{node.content}\u201d', fmt)
            cursor.insertBlock()

        elif tag == 'code':
            code_fmt = QTextCharFormat()
            code_fmt.setForeground(QColor(WIZDOC_COLORS['code_text']))
            code_fmt.setBackground(QColor(WIZDOC_COLORS['code_bg']))
            code_fmt.setFont(QFont('Courier New', 9))
            for line in node.content.split('\n'):
                cursor.insertText(line, code_fmt)
                cursor.insertBlock()
            cursor.insertBlock()

        elif tag == 'table':
            self._render_table(cursor, node)

        elif tag == 'break':
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(WIZDOC_COLORS['h6']))
            cursor.insertText('\u2500' * 40, fmt)
            cursor.insertBlock()
            cursor.insertBlock()

    def _insert_heading(self, cursor: QTextCursor, text: str,
                        level: str, center: bool = False):
        fmt = self._make_format(level)
        if center:
            block_fmt = QTextBlockFormat()
            block_fmt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cursor.setBlockFormat(block_fmt)
        cursor.insertText(text, fmt)

    def _insert_inline(self, cursor: QTextCursor, spans: list[InlineSpan]):
        for span in spans:
            fmt = self._make_format('body')
            if span.bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            if span.italic:
                fmt.setFontItalic(True)
            if span.code:
                fmt.setForeground(QColor(WIZDOC_COLORS['code_text']))
                fmt.setBackground(QColor(WIZDOC_COLORS['code_bg']))
                fmt.setFont(QFont('Courier New', 9))
            if span.color_token:
                token_colors = {
                    'c_gold': WIZDOC_COLORS['h1'],
                    'c_teal': WIZDOC_COLORS['h2'],
                    'c_gold_dim': WIZDOC_COLORS['h6'],
                }
                color = token_colors.get(span.color_token, WIZDOC_COLORS['body'])
                fmt.setForeground(QColor(color))
            cursor.insertText(span.text, fmt)

    def _make_format(self, level: str) -> QTextCharFormat:
        fmt = QTextCharFormat()
        color = WIZDOC_COLORS.get(level, WIZDOC_COLORS['body'])
        fmt.setForeground(QColor(color))
        font_info = WIZDOC_FONTS.get(level, WIZDOC_FONTS['body'])
        font_name, size_pt, bold = font_info
        # Use Georgia as fallback for all custom fonts
        fmt.setFont(QFont('Georgia', max(8, size_pt // 3)))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        return fmt

    def _render_table(self, cursor: QTextCursor, node: BureauNode):
        # Simple text-based table rendering in preview
        if not node.children:
            return
        header_fmt = self._make_format('h1')
        header_fmt.setFontWeight(QFont.Weight.Bold)
        body_fmt = self._make_format('body')
        sep_fmt = QTextCharFormat()
        sep_fmt.setForeground(QColor(WIZDOC_COLORS['tbl_border']))

        for row in node.children:
            cells = [c.content for c in row.children]
            fmt = header_fmt if row.tag == 'th' else body_fmt
            cursor.insertText('  '.join(f'{c:<16}' for c in cells), fmt)
            cursor.insertBlock()
            if row.tag == 'th':
                cursor.insertText('\u2504' * 50, sep_fmt)
                cursor.insertBlock()

        cursor.insertBlock()
