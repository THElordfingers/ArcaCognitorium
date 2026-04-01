# Departamentum Documentalis — emitter_md.py
# v1.0.0
"""Emit .md (Markdown) from a BureauDocument AST.

Follows the markdown-style-guide.md formatting conventions.
Box-drawing tables, 80-char width.
"""

from pathlib import Path
from .schema import BureauDocument, BureauNode, InlineSpan


def _render_inline_md(spans: list[InlineSpan]) -> str:
    """Render inline spans to Markdown."""
    parts = []
    for span in spans:
        if span.bold:
            parts.append(f'**{span.text}**')
        elif span.italic:
            parts.append(f'*{span.text}*')
        elif span.code:
            parts.append(f'`{span.text}`')
        elif span.color_token:
            # Markdown has no native color — render as bold
            parts.append(f'**{span.text}**')
        else:
            parts.append(span.text)
    return ''.join(parts)


def _wrap_text(text: str, width: int = 76) -> list[str]:
    """Word-wrap text to given width."""
    words = text.split()
    lines = []
    current = []
    current_len = 0
    for word in words:
        if current_len + len(word) + 1 > width and current:
            lines.append(' '.join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += len(word) + 1
    if current:
        lines.append(' '.join(current))
    return lines


def _render_table_md(node: BureauNode) -> list[str]:
    """Render a table node using box-drawing characters."""
    if not node.children:
        return []

    # Determine column widths
    all_rows = node.children
    max_cols = max(len(row.children) for row in all_rows)
    col_widths = [4] * max_cols
    for row in all_rows:
        for ci, cell in enumerate(row.children):
            col_widths[ci] = max(col_widths[ci], len(cell.content) + 2)

    def _hline(left, mid, right, fill):
        parts = [left]
        for i, w in enumerate(col_widths):
            parts.append(fill * (w + 2))
            parts.append(mid if i < len(col_widths) - 1 else right)
        return ''.join(parts)

    lines = [_hline('\u256d', '\u252c', '\u256e', '\u2500')]

    for ri, row in enumerate(all_rows):
        cells = []
        for ci in range(max_cols):
            if ci < len(row.children):
                content = row.children[ci].content
            else:
                content = ''
            padded = f' {content:<{col_widths[ci]}} '
            cells.append(padded)
        lines.append('\u2502' + '\u2502'.join(cells) + '\u2502')

        if ri == 0 and row.tag == 'th':
            lines.append(_hline('\u251c', '\u253c', '\u2524', '\u2504'))
        elif ri < len(all_rows) - 1:
            pass  # no separator between data rows

    lines.append(_hline('\u2570', '\u2534', '\u256f', '\u2500'))
    return lines


def emit_markdown(doc: BureauDocument) -> str:
    """Convert a BureauDocument AST to Markdown."""
    lines = []

    # Title
    if doc.header.title:
        lines.append(f'# {doc.header.title}')
        lines.append('')

    for node in doc.nodes:
        tag = node.tag

        if tag == 'h1':
            content = _render_inline_md(node.spans) if node.spans else node.content
            lines.append(f'## {content}')
            lines.append('')
        elif tag == 'h2':
            content = _render_inline_md(node.spans) if node.spans else node.content
            lines.append(f'### {content}')
            lines.append('')
        elif tag == 'h3':
            content = _render_inline_md(node.spans) if node.spans else node.content
            lines.append(f'#### {content}')
            lines.append('')
        elif tag in ('h4', 'h5', 'h6'):
            depth = int(tag[1]) + 1
            content = _render_inline_md(node.spans) if node.spans else node.content
            lines.append(f'{"#" * depth} {content}')
            lines.append('')
        elif tag == 'body':
            content = _render_inline_md(node.spans) if node.spans else node.content
            wrapped = _wrap_text(content)
            lines.extend(wrapped)
            lines.append('')
        elif tag == 'bullet':
            content = _render_inline_md(node.spans) if node.spans else node.content
            lines.append(f'- {content}')
        elif tag == 'note':
            content = _render_inline_md(node.spans) if node.spans else node.content
            lines.append(f'> {content}')
            lines.append('')
        elif tag == 'quote':
            content = _render_inline_md(node.spans) if node.spans else node.content
            lines.append(f'> *{content}*')
            lines.append('')
        elif tag == 'code':
            lang = node.meta.get('lang', '')
            lines.append(f'```{lang}')
            lines.append(node.content)
            lines.append('```')
            lines.append('')
        elif tag == 'table':
            lines.extend(_render_table_md(node))
            lines.append('')
        elif tag == 'break':
            lines.append('---')
            lines.append('')

    return '\n'.join(lines)


def emit_to_file(doc: BureauDocument, path: Path):
    """Write markdown to a file."""
    content = emit_markdown(doc)
    path.write_text(content, encoding='utf-8')
