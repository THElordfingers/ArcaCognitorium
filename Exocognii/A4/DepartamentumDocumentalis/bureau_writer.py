# Departamentum Documentalis — bureau_writer.py
# v1.0.0
"""Write a BureauDocument AST back to .bureau pipe-tag format."""

from .schema import BureauDocument, BureauNode, InlineSpan


def _render_inline(spans: list[InlineSpan]) -> str:
    """Render inline spans back to pipe-tag markup."""
    parts = []
    for span in spans:
        if span.color_token:
            parts.append(f'{{{{{span.color_token}|{span.text}}}}}')
        elif span.bold:
            parts.append(f'**{span.text}**')
        elif span.italic:
            parts.append(f'*{span.text}*')
        elif span.code:
            parts.append(f'`{span.text}`')
        else:
            parts.append(span.text)
    return ''.join(parts)


def write_bureau(doc: BureauDocument) -> str:
    """Serialize a BureauDocument back to .bureau format."""
    lines = []

    # Header
    h = doc.header
    lines.append('---')
    lines.append(f'title: {h.title}')
    lines.append(f'type: {h.doc_type}')
    lines.append(f'version: {h.version}')
    if h.author:
        lines.append(f'author: {h.author}')
    lines.append(f'theme: {h.theme}')
    for k, v in h.extra.items():
        lines.append(f'{k}: {v}')
    lines.append('---')
    lines.append('')

    for node in doc.nodes:
        lines.extend(_render_node(node))
        lines.append('')

    return '\n'.join(lines)


def _render_node(node: BureauNode) -> list[str]:
    """Render a single AST node to .bureau lines."""
    tag = node.tag

    if tag == 'break':
        return ['|break|']

    if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'bullet', 'note', 'quote'):
        content = _render_inline(node.spans) if node.spans else node.content
        return [f'|{tag}|{content}|']

    if tag == 'body':
        content = _render_inline(node.spans) if node.spans else node.content
        return [f'|body|', content, '|/body|']

    if tag == 'code':
        lang = node.meta.get('lang', '')
        header = f'|code|{lang}|' if lang else '|code|'
        return [header, node.content, '|/code|']

    if tag == 'table':
        result = ['|table|']
        for row in node.children:
            cells = [c.content for c in row.children]
            result.append(f'|{row.tag}|' + '|'.join(cells) + '|')
        result.append('|/table|')
        return result

    # Fallback
    return [f'|{tag}|{node.content}|']
