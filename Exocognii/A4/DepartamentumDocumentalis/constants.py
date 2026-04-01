# Departamentum Documentalis — constants.py
# v1.0.0
"""WizDoc style system, app chrome constants, template types."""

# ── WizDoc Style Guide Colors (for document content) ────────
# These are independent of Bureau I's theme — they are the
# fixed document aesthetic per wizdoc-style-guide.md.
WIZDOC_COLORS = {
    'body':       '#BDAB5D',
    'h1':         '#E8C96A',
    'h2':         '#7EC8C8',
    'h3':         '#A98FD4',
    'h4':         '#C87941',
    'h5':         '#8FAD8F',
    'h6':         '#8C7B5C',
    'title':      '#E8C96A',
    'link':       '#7EC8C8',
    'code_bg':    '#1A1040',
    'code_text':  '#7EC8C8',
    'tbl_header_fill': '#2A1A4A',
    'tbl_header_text': '#E8C96A',
    'tbl_border':      '#6B4E8A',
    'tbl_header_border': '#8B6914',
    'bg':         '#050507',
}

# WizDoc typography
WIZDOC_FONTS = {
    'title':  ('Ebon Sigil', 64, True),     # font, size_pt, bold
    'h1':     ('Varnyx Regular', 36, True),
    'h2':     ('Varnyx Regular', 28, True),
    'h3':     ('Varnyx Regular', 24, True),
    'h4':     ('Varnyx Regular', 22, False),  # italic
    'h5':     ('Runavess Demo', 20, False),
    'h6':     ('Runavess Demo', 20, False),
    'body':   ('VL Gothic', 10, False),
    'code':   ('Courier New', 10, False),
}

# ── GUI Chrome (from Bureau I theme.json or defaults) ────────
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

# ── Bureau Identity ──────────────────────────────────────────
APP_TITLE = '\u2726  DEPARTAMENTUM DOCUMENTALIS  \u2726'
APP_SUBTITLE = '\uff24\uff45\uff46\uff49\uff4e\uff45! \uff24\uff45\uff53\uff49\uff47\uff4e\uff41! \uff24\uff45\uff4e\uff4f\uff54\uff41! \uff24\uff49\uff53\uff43\uff45\uff44\uff45!'
BUREAU_FULL = 'The Department of Documented Design Definitives'
BUREAU_LATIN = 'Departamentum Documentalis'

# ── Template Types ───────────────────────────────────────────
TEMPLATE_TYPES = [
    'expositio', 'dux_tome', 'build_doc', 'palette_card', 'blank',
]

# ── Pipe-Tag Registry ────────────────────────────────────────
# Single-line tags (self-closing)
SINGLE_TAGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
               'bullet', 'break', 'note', 'quote'}

# Block tags (require |/tag| close)
BLOCK_TAGS = {'body', 'code', 'table'}
