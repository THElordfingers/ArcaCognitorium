# Departamentum Documentalis · scriptura_parser.py · v1.1
"""
Scriptura Ordinata pipe-tag grammar parser.
Tags: |FIELD:name|, |SECTION:name|, |END|, |FIXED:name|, |INJECT:zone|
Never raises. Returns ParseResult(ast, errors).
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TextNode:
    content: str

@dataclass
class FieldNode:
    name: str
    content: str
    fixed: bool = False

@dataclass
class InjectNode:
    zone: str
    children: list = field(default_factory=list)

@dataclass
class SectionNode:
    name: str
    children: list = field(default_factory=list)

@dataclass
class DocumentAST:
    children: list = field(default_factory=list)
    fields: dict = field(default_factory=dict)

@dataclass
class ParseError:
    line: int
    col: int
    message: str

@dataclass
class ParseResult:
    ast: Optional[DocumentAST]
    errors: list

    @property
    def ok(self):
        return len(self.errors) == 0

_TAG_RE = re.compile(r"\|([A-Z]+):?([^|]*)\|")

def _tokenise(text):
    tokens = []
    pos = 0
    for m in _TAG_RE.finditer(text):
        if m.start() > pos:
            tokens.append(("TEXT", text[pos:m.start()], 0, 0))
        line = text[:m.start()].count("\n") + 1
        col  = m.start() - text[:m.start()].rfind("\n")
        tokens.append((m.group(1), m.group(2).strip(), line, col))
        pos = m.end()
    if pos < len(text):
        tokens.append(("TEXT", text[pos:], 0, 0))
    return tokens

def parse(text: str) -> ParseResult:
    errors = []
    ast = DocumentAST()
    tokens = _tokenise(text)
    stack = [ast.children]
    field_accumulator = {}
    current_field = None
    current_fixed = False

    for kind, value, line, col in tokens:
        if kind == "TEXT":
            if current_field:
                field_accumulator[current_field] = \
                    field_accumulator.get(current_field, "") + value
            else:
                stack[-1].append(TextNode(content=value))
        elif kind == "FIELD":
            if not value:
                errors.append(ParseError(line, col, "FIELD tag missing name"))
            else:
                current_field = value
                current_fixed = False
                field_accumulator.setdefault(current_field, "")
        elif kind == "FIXED":
            if not value:
                errors.append(ParseError(line, col, "FIXED tag missing name"))
            else:
                current_field = value
                current_fixed = True
                field_accumulator.setdefault(current_field, "")
        elif kind == "END":
            if current_field:
                node = FieldNode(
                    name=current_field,
                    content=field_accumulator.get(current_field, "").strip(),
                    fixed=current_fixed)
                stack[-1].append(node)
                ast.fields[current_field] = node.content
                current_field = None
                current_fixed = False
            elif len(stack) > 1:
                stack.pop()
            else:
                errors.append(ParseError(line, col, "Unexpected |END|"))
        elif kind == "SECTION":
            if not value:
                errors.append(ParseError(line, col, "SECTION tag missing name"))
            else:
                node = SectionNode(name=value)
                stack[-1].append(node)
                stack.append(node.children)
        elif kind == "INJECT":
            node = InjectNode(zone=value or "DEFAULT")
            stack[-1].append(node)
            stack.append(node.children)
        else:
            errors.append(ParseError(line, col, f"Unknown tag: {kind}"))

    if len(stack) > 1:
        errors.append(ParseError(0, 0, "Unclosed block at end of document"))

    ast.fields = field_accumulator
    return ParseResult(ast=ast, errors=errors)
