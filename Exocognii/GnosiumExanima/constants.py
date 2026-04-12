# GNOSIUM EXANIMA — constants.py
# v1.0.0
"""
ModusArcanus palette + app-local layout constants.

Inlined per Exocognii convention — no central ModusArcanus module exists yet.
Match values to AuctoritasSpectralis/constants.py and the Modus Arcanus dux
tome so the whole suite stays visually coherent.
"""

# ─── ModusArcanus palette ──────────────────────────────────────────────
C_BG        = "#050507"   # Void
C_PANEL     = "#0a0a12"   # Obsidian
C_GOLD      = "#d4af37"   # Aurum  (primary)
C_GOLD_DIM  = "#7a6a2a"   # Aurum Dimmus
C_GOLD_DARK = "#3a2e10"   # Aurum Nox
C_CRIMSON   = "#8b1a1a"   # Sanguis  (entity-name prefix, destructive)
C_TEAL      = "#1a5a5a"   # Viridis  (entity body text)
C_TEXT      = "#c8b88a"   # Parchment
C_SUBTLE    = "#3a3528"   # Umbra
C_WHITE     = "#e8e0cc"   # Vellum
C_WARN      = "#b8860b"   # dim gold for token warning bar

# ─── Typography ────────────────────────────────────────────────────────
FONT_STACK       = "Georgia, Constantia, serif"
FONT_STACK_HEAD  = "Cinzel, Georgia, serif"
FONT_STACK_MONO  = "excalib-nf, Courier New, monospace"

# ─── App identity ──────────────────────────────────────────────────────
APP_NAME      = "GNOSIUM EXANIMA"
APP_SUBTITLE  = "Overseer of the Unbreathing Tower"
APP_ID        = "gnosium_exanima"
APP_VERSION   = "1.0.0"

# ─── Geometry defaults ─────────────────────────────────────────────────
MIN_WINDOW_W        = 900
MIN_WINDOW_H        = 600
DEFAULT_WINDOW_W    = 1200
DEFAULT_WINDOW_H    = 800
ENTITY_PANEL_WIDTH  = 220
PORTRAIT_THUMB_PX   = 48

# ─── Operational defaults (overridable via ~/.arca/config.json) ───────
DEFAULT_DISTILLATION_THRESHOLD       = 40       # messages
DEFAULT_SYSTEM_PROMPT_TOKEN_CEILING  = 4000     # rough token estimate
DEFAULT_MUNDANA_POLL_SECONDS         = 30
RAW_TAIL_MESSAGES                    = 20       # messages kept raw after distillation

# ─── Conversation modes ────────────────────────────────────────────────
MODE_CHAMBER = "chamber"
MODE_SOLO    = "solo"

# ─── Entity package sentinels ──────────────────────────────────────────
VAULT_FORMAT_JSON = "json"   # EntitexRefined entity.json
VAULT_FORMAT_YAML = "yaml"   # legacy role.yaml + traits.yaml + lore.yaml
