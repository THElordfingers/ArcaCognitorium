"""
ModusArcanus Design Token Constants — Bureau II Canonical Set

Ten ratified colour tokens from the v1.1 wireframe package.
Bureau I is the sole writer of theme.json; Bureau II reads only.
These defaults are the Nox Aurum baseline.
"""

# ── Background & Panel ──────────────────────────────────────────
C_BG        = "#050507"
C_PANEL     = "#0a0a12"

# ── Gold Family ─────────────────────────────────────────────────
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"

# ── Accent Colours ──────────────────────────────────────────────
C_CRIMSON   = "#8b1a1a"
C_TEAL      = "#1a5a5a"

# ── Text ────────────────────────────────────────────────────────
C_TEXT      = "#c8b88a"
C_SUBTLE    = "#3a3528"
C_WHITE     = "#e8e0cc"

# ── Token Registry ──────────────────────────────────────────────
TOKEN_NAMES = [
    "C_BG", "C_PANEL", "C_GOLD", "C_GOLD_DIM", "C_GOLD_DARK",
    "C_CRIMSON", "C_TEAL", "C_TEXT", "C_SUBTLE", "C_WHITE",
]

DEFAULTS = {
    "C_BG":        C_BG,
    "C_PANEL":     C_PANEL,
    "C_GOLD":      C_GOLD,
    "C_GOLD_DIM":  C_GOLD_DIM,
    "C_GOLD_DARK": C_GOLD_DARK,
    "C_CRIMSON":   C_CRIMSON,
    "C_TEAL":      C_TEAL,
    "C_TEXT":       C_TEXT,
    "C_SUBTLE":    C_SUBTLE,
    "C_WHITE":     C_WHITE,
}

# ── Font Stack ──────────────────────────────────────────────────
FONT_SERIF = "Georgia, Constantia, serif"
FONT_MONO  = "Courier Prime, Courier New, monospace"
