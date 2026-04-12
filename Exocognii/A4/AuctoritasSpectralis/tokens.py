"""
AUCTORITAS SPECTRALIS — v1.0.0
tokens.py — ModusArcanus Design Token Constants

Single source of truth for all colour and typography constants.
All feature files import from here. No hex values hardcoded elsewhere.

Bureau I is the sole writer of theme.json.
These constants are the Nox Aurum baseline.
"""

# ── Background surfaces ───────────────────────────────────────────────────

C_BG        = "#050507"   # Void — primary window background
C_PANEL     = "#0a0a12"   # Obsidian — panel / card / sidebar surface
C_SUBTLE    = "#080810"   # Umbra — recessed / hover surface

# ── Gold family ───────────────────────────────────────────────────────────

C_GOLD      = "#d4af37"   # Aurum — primary accent, active states, headings
C_GOLD_DIM  = "#7a6a2a"   # Aurum Dimmus — secondary text, inactive labels
C_GOLD_DARK = "#3a2e10"   # Aurum Nox — borders, dividers, deep accents

# ── Text ──────────────────────────────────────────────────────────────────

C_TEXT      = "#c8b88a"   # Parchment — primary readable body text
C_WHITE     = "#e8e0cc"   # Vellum — emphasis text, selected labels

# ── Accent pair ───────────────────────────────────────────────────────────

C_CRIMSON   = "#8b1a1a"   # Sanguis — error / warning / danger
C_TEAL      = "#1a5a5a"   # Viridis — success / confirm / info

# ── Semantic extras (derived from above, used in QSS) ────────────────────

C_CRIMSON_BRIGHT = "#e08080"   # Sanguis text on dark background
C_TEAL_BRIGHT    = "#a0d0c0"   # Viridis text on dark background
C_WARN           = "#c87941"   # Amber — harmonic conflict warning

# ── Token registry ────────────────────────────────────────────────────────

DEFAULTS: dict[str, str] = {
    "c_bg":        C_BG,
    "c_panel":     C_PANEL,
    "c_subtle":    C_SUBTLE,
    "c_gold":      C_GOLD,
    "c_gold_dim":  C_GOLD_DIM,
    "c_gold_dark": C_GOLD_DARK,
    "c_text":      C_TEXT,
    "c_white":     C_WHITE,
    "c_crimson":   C_CRIMSON,
    "c_teal":      C_TEAL,
}

# ── Typography ────────────────────────────────────────────────────────────

# Display / headings — classical Roman proportions
FONT_DISPLAY = "'Cinzel', 'Georgia', serif"

# Body / labels — humanist old-style, warm and legible
FONT_SERIF   = "'IM Fell English', 'Georgia', serif"

# Monospace / data / code
FONT_MONO    = "'Share Tech Mono', 'Courier New', monospace"

# ── Sizing constants ──────────────────────────────────────────────────────

TITULUM_W  = 220    # px — left column fixed width
FASCIA_H   = 52     # px — toolbar strip height
STATUS_H   = 26     # px — status bar height
BORDER_W   = 1      # px — standard border width
RADIUS     = 0      # px — no border radius (flat aesthetic)
