# Auctoritas Spectralis — constants.py
# v1.0.0
"""ModusArcanus canonical defaults and token names."""

# Default palette — the canonical ModusArcanus dark theme
MODUS_ARCANUS_DEFAULTS = {
    'c_bg':        '#050507',
    'c_panel':     '#0a0a12',
    'c_gold':      '#d4af37',
    'c_gold_dim':  '#7a6a2a',
    'c_gold_dark': '#3a2e10',
    'c_crimson':   '#8b1a1a',
    'c_teal':      '#1a5a5a',
    'c_text':      '#c8b88a',
    'c_subtle':    '#3a3528',
    'c_white':     '#e8e0cc',
}

DEFAULT_BG = '#050507'
DEFAULT_FG = '#d4af37'

TOKEN_NAMES = [
    'c_bg', 'c_panel', 'c_gold', 'c_gold_dim', 'c_gold_dark',
    'c_crimson', 'c_teal', 'c_text', 'c_subtle', 'c_white',
]

TOKEN_LABELS = {
    'c_bg':        'Void',
    'c_panel':     'Obsidian',
    'c_gold':      'Aurum',
    'c_gold_dim':  'Aurum Dimmus',
    'c_gold_dark': 'Aurum Nox',
    'c_crimson':   'Sanguis',
    'c_teal':      'Viridis',
    'c_text':      'Parchment',
    'c_subtle':    'Umbra',
    'c_white':     'Vellum',
}

# Foreground tokens — those intended to appear as text/icons on backgrounds
FG_TOKENS = ['c_gold', 'c_gold_dim', 'c_text', 'c_white', 'c_crimson', 'c_teal']

# Background tokens — those intended as surfaces behind foreground tokens
BG_TOKENS = ['c_bg', 'c_panel', 'c_subtle', 'c_gold_dark']

FONT_STACK = 'Georgia, Constantia, serif'
FONT_STACK_MONO = 'excalib-nf, Courier New, monospace'

APP_TITLE = '\u2726  CODEXIUM CHROMATICUS  \u2726'
APP_SUBTITLE = 'Sequentiae Umbrarum'
BUREAU_FULL = 'The Spectral Compliance Authority'
BUREAU_LATIN = 'Auctoritas Spectralis'
