# Departamentum Documentalis — bureau_parser.py
# v1.0.0
"""Parse .bureau pipe-tag format into a document AST."""

import re
from pathlib import Path

from .schema import BureauDocument, BureauNode, DocumentHeader, InlineSpan
from .constants import SINGLE_TAGS, BLOCK_TAGS


# ── Inline formatting patterns ──────────────────────────────
_INLINE_PATTERNS = [
    (re.compile(r'\*\*(.+?)\*\*'), 'bold'),
    (re.compile(r'\*(.+?)\*'), 'italic'),
    (re.compile(r'`(.+?)`'), 'code'),
    (re.compile(r'\{\{(\w+)\|(.+?)\}\}'), 'color'),  # {{c_gold|text}}
]


def parse_inline(text: str) -> list[InlineSpan]:
    """Parse inline formatting within a content string.

    Supports: **bold**, *italic*, `code`, {{token|colored}}.
    Returns a list of InlineSpan objects preserving order.
    """
    spans = []
    pos = 0

    # Build a merged list of all matches sorted by position
    matches = []
    for pattern, fmt_type in _INLINE_PATTERNS:
        for m in pattern.finditer(text):
            matches.append((m.start(), m.end(), fmt_type, m))
    matches.sort(key=lambda x: x[0])

    # Eliminate overlapping matches (first wins)
    used = []
    for start, end, fmt_type, m in matches:
        if any(start < u_end and end > u_start for u_start, u_end in used):
            continue
        used.append((start, end))

        # Plain text before this match
        if pos < start:
            plain = text[pos:start]
            if plain:
                spans.append(InlineSpan(text=plain))

        if fmt_type == 'bold':
            spans.append(InlineSpan(text=m.group(1), bold=True))
        elif fmt_type == 'italic':
            spans.append(InlineSpan(text=m.group(1), italic=True))
        elif fmt_type == 'code':
            spans.append(InlineSpan(text=m.group(1), code=True))
        elif fmt_type == 'color':
            spans.append(InlineSpan(text=m.group(2), color_token=m.group(1)))

        pos = end

    # Trailing plain text
    if pos < len(text):
        spans.append(InlineSpan(text=text[pos:]))

    # If no formatting found at all, return single plain span
    if not spans:
        spans.append(InlineSpan(text=text))

    return spans


def _parse_header(lines: list[str]) -> tuple[DocumentHeader, int]:
    """Parse YAML-style front matter between --- fences.

    Returns (header, index_of_first_content_line).
    """
    header = DocumentHeader()
    if not lines or lines[0].strip() != '---':
        return header, 0

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return header, 0

    for line in lines[1:end_idx]:
        line = line.strip()
        if ':' not in line:
            continue
        key, _, val = line.partition(':')
        key = key.strip().lower()
        val = val.strip()
        if key == 'title':
            header.title = val
        elif key == 'type':
            header.doc_type = val
        elif key == 'version':
            header.version = val
        elif key == 'author':
            header.author = val
        elif key == 'theme':
            header.theme = val
        else:
            header.extra[key] = val

    return header, end_idx + 1


def _parse_single_tag(line: str) -> BureauNode | None:
    """Parse a single-line tag: |tag|content|"""
    stripped = line.strip()
    if not stripped.startswith('|'):
        return None

    parts = stripped.split('|')
    # Filter empties from leading/trailing pipes
    parts = [p for p in parts if p != '']
    if not parts:
        return None

    tag = parts[0].strip().lower()
    content = '|'.join(parts[1:]) if len(parts) > 1 else ''

    if tag in SINGLE_TAGS or tag == 'break':
        node = BureauNode(tag=tag, content=content.strip())
        if content.strip():
            node.spans = parse_inline(content.strip())
        return node

    return None


def parse_bureau(text: str, source_path: str = '') -> BureauDocument:
    """Parse a complete .bureau file into a BureauDocument AST.

    Handles:
    - YAML front matter (--- fenced)
    - Single-line tags: |h1|content|, |bullet|content|, |break|
    - Block tags: |body| ... |/body|, |code|lang| ... |/code|
    - Table blocks: |table| |th|..| |tr|..| |/table|
    """
    lines = text.split('\n')
    header, start_idx = _parse_header(lines)
    doc = BureauDocument(header=header, nodes=[], source_path=source_path)

    i = start_idx
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Check for single-line tag
        if stripped.startswith('|'):
            parts = stripped.split('|')
            parts = [p for p in parts if p != '']
            if not parts:
                i += 1
                continue

            tag = parts[0].strip().lower()

            # ── Block: body ──
            if tag == 'body':
                content_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].strip() == '|/body|':
                        break
                    content_lines.append(lines[i])
                    i += 1
                content = '\n'.join(content_lines).strip()
                node = BureauNode(tag='body', content=content)
                node.spans = parse_inline(content)
                doc.nodes.append(node)
                i += 1  # skip |/body|
                continue

            # ── Block: code ──
            if tag == 'code':
                lang = parts[1].strip() if len(parts) > 1 else ''
                code_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].strip() == '|/code|':
                        break
                    code_lines.append(lines[i])
                    i += 1
                content = '\n'.join(code_lines)
                node = BureauNode(
                    tag='code', content=content,
                    meta={'lang': lang}
                )
                doc.nodes.append(node)
                i += 1  # skip |/code|
                continue

            # ── Block: table ──
            if tag == 'table':
                table_node = BureauNode(tag='table')
                i += 1
                while i < len(lines):
                    tline = lines[i].strip()
                    if tline == '|/table|':
                        break
                    if tline.startswith('|th|') or tline.startswith('|tr|'):
                        row_parts = tline.split('|')
                        row_parts = [p for p in row_parts if p != '']
                        row_tag = row_parts[0].strip().lower()
                        cells = [p.strip() for p in row_parts[1:]]
                        row_node = BureauNode(
                            tag=row_tag, content='',
                            children=[
                                BureauNode(tag='td', content=c,
                                           spans=parse_inline(c))
                                for c in cells
                            ]
                        )
                        table_node.children.append(row_node)
                    i += 1
                doc.nodes.append(table_node)
                i += 1  # skip |/table|
                continue

            # ── Single-line tags ──
            single = _parse_single_tag(stripped)
            if single:
                doc.nodes.append(single)
                i += 1
                continue

        # Bare text line (not inside a block) — treat as implicit body
        bare_lines = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if nxt.startswith('|') or nxt == '':
                break
            bare_lines.append(nxt)
            i += 1
        content = ' '.join(bare_lines)
        node = BureauNode(tag='body', content=content)
        node.spans = parse_inline(content)
        doc.nodes.append(node)

    return doc


def parse_file(path: Path) -> BureauDocument:
    """Parse a .bureau file from disk."""
    text = path.read_text(encoding='utf-8')
    return parse_bureau(text, source_path=str(path))
