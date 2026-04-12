# Departamentum Documentalis · md_renderer.py · v1.1
from DepartamentumDocumentalis.scriptura_parser import (
    DocumentAST, TextNode, FieldNode, SectionNode, InjectNode)

def render(ast: DocumentAST, forma_fields: list, fixed_values: dict) -> str:
    lines = []
    _render_children(ast.children, lines, forma_fields, fixed_values)
    return "\n".join(lines)

def _render_children(nodes, lines, forma_fields, fixed_values):
    for node in nodes:
        if isinstance(node, TextNode):
            t = node.content.strip()
            if t:
                lines.append(t)
        elif isinstance(node, FieldNode):
            value = fixed_values.get(node.name, node.content) if node.fixed else node.content
            label = _lbl(node.name, forma_fields)
            lines.append(f"**{label}:** {value}")
        elif isinstance(node, SectionNode):
            lines.append(f"\n## {node.name}\n")
            _render_children(node.children, lines, forma_fields, fixed_values)
        elif isinstance(node, InjectNode):
            lines.append(f"\n<!-- ZONA INIECTIONIS: {node.zone} -->\n")
            _render_children(node.children, lines, forma_fields, fixed_values)

def _lbl(name, forma_fields):
    for f in forma_fields:
        if f["name"] == name:
            return f["label"]
    return name
