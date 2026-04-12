"""
Data models for Agentia Architecturalis.

ElementNode — serialisable tree node for canvas elements.
PropertySet — typed property dictionary for inspector editing.
DesignDocument — top-level canvas session file format.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, TypedDict


class PropertySet(TypedDict, total=False):
    """Configurable element properties exposed in the Inspector."""
    var_name: str
    width: int
    height: int
    x: int
    y: int
    bg_token: str
    border_token: str
    fg_token: str
    text_content: str
    font_size: int
    layout_type: str       # "vertical" | "horizontal" | "none"
    spacing: int
    padding: int
    border_radius: int
    placeholder: str
    min_val: int
    max_val: int
    columns: int
    orientation: str       # "horizontal" | "vertical"


@dataclass
class ElementNode:
    """A serialisable node in the design tree."""
    element_type: str
    var_name: str
    category: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    children: list[ElementNode] = field(default_factory=list)
    x: int = 0
    y: int = 0

    def to_dict(self) -> dict:
        d = {
            "element_type": self.element_type,
            "var_name": self.var_name,
            "category": self.category,
            "properties": dict(self.properties),
            "x": self.x,
            "y": self.y,
        }
        if self.children:
            d["children"] = [c.to_dict() for c in self.children]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> ElementNode:
        children = [cls.from_dict(c) for c in d.get("children", [])]
        return cls(
            element_type=d["element_type"],
            var_name=d["var_name"],
            category=d.get("category", ""),
            properties=d.get("properties", {}),
            children=children,
            x=d.get("x", 0),
            y=d.get("y", 0),
        )


@dataclass
class DesignDocument:
    """Top-level canvas session format."""
    name: str
    elements: list[ElementNode] = field(default_factory=list)
    theme_designator: str = "Nox Aurum"
    version: int = 1

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name,
            "theme_designator": self.theme_designator,
            "version": self.version,
            "elements": [e.to_dict() for e in self.elements],
        }, indent=2)

    @classmethod
    def from_json(cls, raw: str) -> DesignDocument:
        d = json.loads(raw)
        return cls(
            name=d["name"],
            theme_designator=d.get("theme_designator", "Nox Aurum"),
            version=d.get("version", 1),
            elements=[ElementNode.from_dict(e) for e in d.get("elements", [])],
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> DesignDocument:
        return cls.from_json(path.read_text(encoding="utf-8"))
