# Agentia Architecturalis — elements/factory.py
# v1.0.0
"""Element factory — maps type strings to CanvasElement instances."""

from .base import CanvasElement
from .containers import FrameElement, GroupBoxElement, SplitterElement, TabWidgetElement
from .displays import LabelElement, ProgressBarElement
from .inputs import LineEditElement, ComboBoxElement, SliderElement, SpinBoxElement
from .buttons import ArcaneButtonElement, ToggleButtonElement
from .tables import TableViewElement
from .text import TextEditElement
from .decorative import SeparatorElement, SpacerElement, RuleLineElement
from .composite import (
    TopBarElement, StatusBarElement, ControlPanelElement,
    SectionHeaderElement, SwatchStripElement,
)


_FACTORY_MAP = {
    'QFrame': FrameElement,
    'QGroupBox': GroupBoxElement,
    'QSplitter': SplitterElement,
    'QTabWidget': TabWidgetElement,
    'QLabel_gold': lambda: LabelElement('QLabel_gold'),
    'QLabel_dim': lambda: LabelElement('QLabel_dim'),
    'QLabel_micro': lambda: LabelElement('QLabel_micro'),
    'QProgressBar': ProgressBarElement,
    'QLineEdit': LineEditElement,
    'QComboBox': ComboBoxElement,
    'QSlider': SliderElement,
    'QSpinBox': SpinBoxElement,
    'QTextEdit': TextEditElement,
    'ArcaneButton_gold': lambda: ArcaneButtonElement('ArcaneButton_gold'),
    'ArcaneButton_teal': lambda: ArcaneButtonElement('ArcaneButton_teal'),
    'ArcaneButton_crimson': lambda: ArcaneButtonElement('ArcaneButton_crimson'),
    'ToggleButton': ToggleButtonElement,
    'QTableView': TableViewElement,
    'Separator': SeparatorElement,
    'Spacer': SpacerElement,
    'RuleLine': RuleLineElement,
    'TopBar': TopBarElement,
    'StatusBar': StatusBarElement,
    'ControlPanel': ControlPanelElement,
    'SectionHeader': SectionHeaderElement,
    'SwatchStrip': SwatchStripElement,
}


def create_element(element_type: str) -> CanvasElement:
    """Create a CanvasElement instance by type string.

    Raises KeyError if type is not registered.
    """
    factory = _FACTORY_MAP.get(element_type)
    if factory is None:
        raise KeyError(f"Unknown element type: {element_type}")
    if callable(factory) and not isinstance(factory, type):
        return factory()
    return factory()


def deserialize_element(node: dict) -> CanvasElement:
    """Reconstruct a CanvasElement from a serialized ElementNode dict."""
    element_type = node.get('element_type', 'QFrame')
    try:
        element = create_element(element_type)
    except KeyError:
        # Placeholder for unknown types
        element = FrameElement()
        element.properties['variable_name'] = f'unknown_{element_type}'
        element.properties['label_text'] = f'\u2334 Unknown: {element_type}'

    element.id = node.get('id', element.id)
    element.properties.update(node.get('properties', {}))

    for child_node in node.get('children', []):
        child = deserialize_element(child_node)
        element.children.append(child)

    return element


def list_element_types() -> list[str]:
    """Return all registered element type strings."""
    return list(_FACTORY_MAP.keys())
