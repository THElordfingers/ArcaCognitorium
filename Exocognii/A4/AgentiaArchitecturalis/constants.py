# Agentia Architecturalis — constants.py
# v1.0.0
"""Element registry, palette categories, and ModusArcanus defaults."""

MODUS_ARCANUS_DEFAULTS = {
    'c_bg': '#050507', 'c_panel': '#0a0a12', 'c_gold': '#d4af37',
    'c_gold_dim': '#7a6a2a', 'c_gold_dark': '#3a2e10',
    'c_crimson': '#8b1a1a', 'c_teal': '#1a5a5a',
    'c_text': '#c8b88a', 'c_subtle': '#3a3528', 'c_white': '#e8e0cc',
}

TOKEN_NAMES = [
    'c_bg', 'c_panel', 'c_gold', 'c_gold_dim', 'c_gold_dark',
    'c_crimson', 'c_teal', 'c_text', 'c_subtle', 'c_white',
]

FONT_STACK = 'Georgia, Constantia, serif'
FONT_STACK_MONO = 'excalib-nf, Courier New, monospace'

PALETTE_CATEGORIES = [
    {
        'id': 'receptacula', 'label': 'Receptacula',
        'description': 'Containers and structural elements',
        'elements': ['QFrame', 'QGroupBox', 'QSplitter', 'QTabWidget'],
    },
    {
        'id': 'ingressus', 'label': 'Ingressus',
        'description': 'Input and control elements',
        'elements': ['QLineEdit', 'QComboBox', 'QSlider', 'QSpinBox'],
    },
    {
        'id': 'ostensio', 'label': 'Ostensio',
        'description': 'Display and label elements',
        'elements': ['QLabel_gold', 'QLabel_dim', 'QLabel_micro', 'QProgressBar'],
    },
    {
        'id': 'actiones', 'label': 'Actiones',
        'description': 'Buttons and action triggers',
        'elements': ['ArcaneButton_gold', 'ArcaneButton_teal',
                     'ArcaneButton_crimson', 'ToggleButton'],
    },
    {
        'id': 'tabulae', 'label': 'Tabulae',
        'description': 'Tables and data grids',
        'elements': ['QTableView'],
    },
    {
        'id': 'ornamentum', 'label': 'Ornamentum',
        'description': 'Decorative and structural elements',
        'elements': ['Separator', 'Spacer', 'RuleLine'],
    },
    {
        'id': 'composita', 'label': 'Composita',
        'description': 'Pre-built ModusArcanus widget patterns',
        'elements': ['TopBar', 'StatusBar', 'ControlPanel',
                     'SectionHeader', 'SwatchStrip'],
    },
]

ELEMENT_DEFAULTS = {
    'container': {
        'bg_token': 'c_panel', 'border_token': 'c_gold_dark',
        'layout_type': 'vertical', 'spacing': 16, 'padding': 8,
        'border_width': 1, 'border_style': 'solid',
    },
    'input': {
        'bg_token': 'c_bg', 'text_token': 'c_text',
        'border_token': 'c_subtle', 'font_size': 11, 'padding': 6,
    },
    'display': {
        'text_token': 'c_text', 'font_size': 11, 'font_bold': False,
    },
    'button': {
        'bg_token': 'c_panel', 'text_token': 'c_gold',
        'border_token': 'c_gold_dark', 'font_size': 11,
        'letter_spacing': 1, 'padding': 6,
    },
    'decorative': {
        'border_token': 'c_gold_dark', 'border_width': 1,
    },
    'table': {
        'bg_token': 'c_bg', 'text_token': 'c_text',
        'border_token': 'c_subtle',
    },
}

# Maps element type strings to (category, display_name, description)
ELEMENT_REGISTRY = {
    'QFrame':      ('container', 'QFrame', 'Generic container frame'),
    'QGroupBox':   ('container', 'QGroupBox', 'Labeled group container'),
    'QSplitter':   ('container', 'QSplitter', 'Resizable split container'),
    'QTabWidget':  ('container', 'QTabWidget', 'Tabbed container'),
    'QLineEdit':   ('input', 'QLineEdit', 'Single-line text input'),
    'QComboBox':   ('input', 'QComboBox', 'Dropdown selector'),
    'QSlider':     ('input', 'QSlider', 'Horizontal slider'),
    'QSpinBox':    ('input', 'QSpinBox', 'Numeric spinner'),
    'QLabel_gold': ('display', 'QLabel (Gold)', 'Gold header label'),
    'QLabel_dim':  ('display', 'QLabel (Dim)', 'Dim hint label'),
    'QLabel_micro': ('display', 'QLabel (Micro)', 'Micro uppercase label'),
    'QProgressBar': ('display', 'QProgressBar', 'Progress indicator'),
    'ArcaneButton_gold': ('button', 'Button (Gold)', 'Primary arcane button'),
    'ArcaneButton_teal': ('button', 'Button (Teal)', 'Confirm/save button'),
    'ArcaneButton_crimson': ('button', 'Button (Crimson)', 'Destructive button'),
    'ToggleButton': ('button', 'Toggle', 'Checkable toggle button'),
    'QTableView':  ('table', 'QTableView', 'Data table'),
    'Separator':   ('decorative', 'Separator', 'Horizontal rule line'),
    'Spacer':      ('decorative', 'Spacer', 'Empty spacing element'),
    'RuleLine':    ('decorative', 'Rule Line', 'Decorative divider'),
    'TopBar':      ('composite', 'TopBar', 'ModusArcanus top bar'),
    'StatusBar':   ('composite', 'StatusBar', 'ModusArcanus status bar'),
    'ControlPanel': ('composite', 'ControlPanel', 'Slide-out control panel'),
    'SectionHeader': ('composite', 'SectionHeader', 'Gold section header'),
    'SwatchStrip': ('composite', 'SwatchStrip', 'Color swatch list'),
}

APP_TITLE = '\u2726  AGENTIA ARCHITECTURALIS  \u2726'
APP_SUBTITLE = 'In Linea, In Parallelo, In Perpetuum'
BUREAU_FULL = 'The Architectural Alignment Enforcement Agency'
BUREAU_LATIN = 'Agentia Architecturalis'
