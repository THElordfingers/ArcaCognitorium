# Agentia Architecturalis — schema.py
# v1.0.0
"""Design document serialization schema for the Component Library."""

from typing import TypedDict, Optional


class PropertySet(TypedDict, total=False):
    """Configurable properties for a canvas element."""
    variable_name: str
    label_text: str
    width: Optional[int]
    height: Optional[int]
    min_width: Optional[int]
    min_height: Optional[int]
    bg_token: str
    text_token: str
    border_token: str
    accent_token: str
    font_size: int
    font_bold: bool
    font_italic: bool
    micro_label: bool
    letter_spacing: int
    layout_type: str
    spacing: int
    padding: int
    alignment: str
    margin_top: int
    margin_right: int
    margin_bottom: int
    margin_left: int
    border_width: int
    border_style: str
    placeholder_text: str
    read_only: bool
    button_accent: str


class ElementNode(TypedDict):
    """A single element in the design tree."""
    id: str
    element_type: str
    element_category: str
    properties: PropertySet
    children: list['ElementNode']
    x: float
    y: float


class DesignDocument(TypedDict):
    """Complete serialized design — stored in component_library.db."""
    schema_version: str
    canvas_width: int
    canvas_height: int
    root_elements: list[ElementNode]
    theme_designator: Optional[str]
    metadata: dict
