# Departamentum Documentalis — schema.py
# v1.0.0
"""AST node types for parsed .bureau content."""

from typing import TypedDict, Optional
from dataclasses import dataclass, field


@dataclass
class InlineSpan:
    """An inline text span with optional formatting."""
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    color_token: str | None = None  # e.g. 'c_gold'


@dataclass
class BureauNode:
    """A single node in the document AST."""
    tag: str              # 'h1', 'h2', ..., 'body', 'bullet', 'code', etc.
    content: str = ''     # raw text content (before inline parse)
    spans: list[InlineSpan] = field(default_factory=list)  # parsed inline
    children: list['BureauNode'] = field(default_factory=list)  # table rows
    meta: dict = field(default_factory=dict)  # tag-specific metadata
    # meta keys by tag:
    #   code: {'lang': 'python'}
    #   table th/tr: stored as children of a table node


@dataclass
class DocumentHeader:
    """YAML front matter from a .bureau file."""
    title: str = ''
    doc_type: str = 'blank'
    version: str = '1.0'
    author: str = ''
    theme: str = 'wizdoc'
    extra: dict = field(default_factory=dict)


@dataclass
class BureauDocument:
    """Complete parsed .bureau file."""
    header: DocumentHeader = field(default_factory=DocumentHeader)
    nodes: list[BureauNode] = field(default_factory=list)
    source_path: str = ''


class CompanionJson(TypedDict):
    """The .bureau.json sidecar file."""
    source: str
    outputs: dict[str, str]
    template: str
    document_theme: str
    gui_theme_designator: str | None
    compiled_at: str
    version: str
    author: str
