# Departamentum Documentalis · wiz_renderer.py · v1.1
import json, subprocess, tempfile, os
from pathlib import Path
from DepartamentumDocumentalis.scriptura_parser import (
    DocumentAST, TextNode, FieldNode, SectionNode)
from DepartamentumDocumentalis.config import CFG

class WizRenderError(Exception):
    pass

def render(ast: DocumentAST, forma_fields: list, fixed_values: dict, output_path: str) -> str:
    blocks = _ast_to_blocks(ast, forma_fields, fixed_values)
    node_script = CFG["node_script_path"]
    if not Path(node_script).exists():
        raise WizRenderError(f"Node.js emit script not found: {node_script}")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"doc": blocks, "output": output_path}, f)
        tmp = f.name
    try:
        r = subprocess.run(["node", node_script, tmp],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            raise WizRenderError(f"Node.js error: {r.stderr.strip()}")
        return output_path
    finally:
        os.unlink(tmp)

def _ast_to_blocks(ast, forma_fields, fixed_values):
    blocks = []
    for node in ast.children:
        if isinstance(node, TextNode) and node.content.strip():
            blocks.append({"type": "paragraph", "text": node.content.strip()})
        elif isinstance(node, FieldNode):
            val = fixed_values.get(node.name, node.content) if node.fixed else node.content
            blocks.append({"type": "field", "label": _lbl(node.name, forma_fields), "value": val})
        elif isinstance(node, SectionNode):
            blocks.append({"type": "heading", "text": node.name})
            sub = type("_", (), {"children": node.children})()
            blocks.extend(_ast_to_blocks(sub, forma_fields, fixed_values))
    return blocks

def _lbl(name, forma_fields):
    for f in forma_fields:
        if f["name"] == name:
            return f["label"]
    return name
