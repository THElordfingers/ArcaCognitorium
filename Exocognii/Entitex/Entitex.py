
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ███████ ███    ██ ████████ ██ ████████ ███████ ██   ██  ▍
🮈  ██      ████   ██    ██    ██    ██    ██       ██ ██   ▍
🮈  █████   ██ ██  ██    ██    ██    ██    █████     ███    ▍
🮈  ██      ██  ██ ██    ██    ██    ██    ██       ██ ██   ▍
🮈  ███████ ██   ████    ██    ██    ██    ███████ ██   ██  ▍
🮈                                                          ▍
🮈                                                          ▍
🮈                      Python Script                       ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃

# ─────────────────────────────────────────────────────────────────────────────
# Entitex v0.1
# Arca Cognitorium — Entity Package Generator
# Generates: role.yaml, traits.yaml, lore.yaml, profiles fragment,
#            canon fragment, portrait image
# Output: Exocognii/Entitex/staged/{entity_id}/
# ─────────────────────────────────────────────────────────────────────────────
"""

import os, re, sys, json, time, base64, random, shutil, copy
import urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

import anthropic
import yaml

from PyQt6.QtCore import (
    Qt, QThread, QSize, pyqtSignal, QObject
)
from PyQt6.QtGui import (
    QPixmap, QFont, QFontDatabase, QColor
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel,
    QPushButton, QComboBox, QSlider, QScrollArea,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QTextEdit, QPlainTextEdit, QLineEdit, QDialog,
    QProgressBar, QSizePolicy, QSpacerItem, QSplitter,
    QTabWidget, QCheckBox, QMessageBox
)

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────

ARCA_DIR      = Path.home() / "ArcaCognitorium"
BASE_DIR      = ARCA_DIR / "Exocognii" / "Entitex"
STAGED_DIR    = BASE_DIR / "staged"
VAULT_DIR     = BASE_DIR / "vault"          # generated entity archive
LOG_PATH      = BASE_DIR / "entitex_log.json"
TEMP_DIR      = BASE_DIR / "temp_portraits"

# ArcaCognitorium entity paths (install targets)
ENTITY_ROLES_DIR   = ARCA_DIR / "entities" / "roles"
ENTITY_TRAITS_DIR  = ARCA_DIR / "entities" / "traits"
ENTITY_PROFILES    = ARCA_DIR / "entities" / "profiles" / "profiles.yaml"
ENTITY_CANON       = ARCA_DIR / "entities" / "canon" / "entity_canon.yaml"

CLAUDE_MODEL     = "claude-sonnet-4-20250514"
FREEPIK_API_KEY  = os.environ.get("FREEPIK_API_KEY", "")
FREEPIK_API_BASE = "https://api.freepik.com/v1"
POLL_INTERVAL    = 2.0
POLL_MAX         = 60

# ─────────────────────────────────────────────────────────────────────────────
# COLOURS & GLOBAL STYLE
# ─────────────────────────────────────────────────────────────────────────────

C_BG        = "#050507"
C_PANEL     = "#0a0a12"
C_GOLD      = "#d4af37"
C_GOLD_DIM  = "#7a6a2a"
C_GOLD_DARK = "#3a2e10"
C_CRIMSON   = "#8b1a1a"
C_TEAL      = "#1a5a5a"
C_TEXT      = "#c8b88a"
C_SUBTLE    = "#3a3528"
C_WHITE     = "#e8e0cc"

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: Georgia, Constantia, serif;
}}
QScrollBar:vertical {{
    background: {C_PANEL}; width: 8px; border: none;
}}
QScrollBar::handle:vertical {{
    background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
    background: {C_PANEL}; height: 8px; border: none;
}}
QScrollBar::handle:horizontal {{
    background: {C_GOLD_DARK}; border-radius: 4px;
}}
QToolTip {{
    background: {C_PANEL}; color: {C_GOLD};
    border: 1px solid {C_GOLD_DARK};
    font-family: Georgia, serif; padding: 4px;
}}
QTabWidget::pane {{
    border: 1px solid {C_GOLD_DARK}; background: {C_PANEL};
}}
QTabBar::tab {{
    background: {C_BG}; color: {C_GOLD_DIM};
    border: 1px solid {C_GOLD_DARK};
    padding: 5px 14px;
    font-family: Georgia, serif; font-size: 10px;
}}
QTabBar::tab:selected {{
    background: {C_PANEL}; color: {C_GOLD};
    border-bottom: 1px solid {C_PANEL};
}}
QTabBar::tab:hover {{ background: {C_GOLD_DARK}; }}
QLineEdit {{
    background: {C_BG}; color: {C_TEXT};
    border: 1px solid {C_GOLD_DARK};
    padding: 3px 6px; font-family: Georgia, serif; font-size: 11px;
}}
QComboBox {{
    background: {C_BG}; color: {C_GOLD};
    border: 1px solid {C_GOLD_DARK};
    padding: 3px 8px; font-family: Georgia, serif; font-size: 11px;
}}
QComboBox QAbstractItemView {{
    background: {C_PANEL}; color: {C_GOLD};
    selection-background-color: {C_GOLD_DARK};
}}
QCheckBox {{
    color: {C_GOLD_DIM}; font-family: Georgia, serif;
    font-size: 10px; background: transparent; spacing: 6px;
}}
QCheckBox::indicator {{
    width: 13px; height: 13px;
    border: 1px solid {C_GOLD_DARK}; background: {C_BG};
}}
QCheckBox::indicator:checked {{
    background: {C_GOLD_DARK}; border-color: {C_GOLD};
}}
"""

# ─────────────────────────────────────────────────────────────────────────────
# ARCHETYPES  (TYPOI ENTIUM)
# ─────────────────────────────────────────────────────────────────────────────
# Canonical archetypes — each carries an implicit perspective and social charge.
# Cognitive axis is selected separately and intersects with these.

ARCHETYPES = [
    # — Position & Institutional —
    "The Exile",
    "The Usurper",
    "The Supplicant",
    "The Emissary",
    "The Arbiter",
    "The Custodian",
    "The Anchorite",
    "The Recluse",
    "The Interlocutor",
    "The Threshold",          # †  liminal gatekeeper — neither inside nor out
    "The Assessor",           # †  evaluates, classifies, moves on
    "The Functionary",        # †  executes the system faithfully, questions nothing
    "The Incumbent",          # †  holds a position they did not earn and cannot vacate
    "The Steward",            # †  maintains what others built
    "The Envoy",              # †  carries messages between incompatible worlds
    "The Petitioner",         # †  perpetually waiting for a decision that may never come

    # — Knowledge & Interpretation —
    "The Inquisitor",
    "The Witness",
    "The Cartographer",
    "The Chronicler",
    "The Interpreter",
    "The Augur",
    "The Amnesiac",
    "The Compiler",           # †  aggregates without synthesising
    "The Annotator",          # †  lives in the margins of other people's texts
    "The Archivist",          # †  preserves without necessarily understanding
    "The Indexer",            # †  knows where everything is, not what it means
    "The Correspondent",      # †  records exchanges, never participates in them
    "The Taxonomist",         # †  names and classifies as an end in itself

    # — Rupture & Transgression —
    "The Heretic",
    "The Apostate",
    "The Dissenter",
    "The Provocateur",
    "The Malcontent",
    "The Revenant",
    "The Penitent",
    "The Aberrant",           # †  deviates without ideology — just does not fit
    "The Contraband",         # †  exists in violation of the system's own rules
    "The Remnant",            # †  what is left after the rupture has passed

    # — Relation & Witness —
    "The Debt-Keeper",
    "The Fool",
    "The Devoted",            # †  committed beyond reason or evidence
    "The Inheritor",          # †  receives what they did not choose
    "The Respondent",         # †  exists only in reaction, never in initiation

    # — Devoted Absurd Register —
    "The Clerk",              # †  processes the incomprehensible with procedural calm
    "The Applicant",          # †  submits forms into a void that occasionally responds
    "The Casualty",           # †  subject to forces they understand perfectly and cannot affect
    "The Understudy",         # †  prepared for a role that may never be vacated
    "The Obligant",           # †  bound by rules no one can fully cite
    "The Pending",            # †  awaiting resolution of a process with no known endpoint
    "The Duly Noted",         # †  acknowledged, recorded, and disregarded

    "— Custom —",
]

COGNITIVE_AXES = [
    # — Existing —
    "Analytical",
    "Intuitive",
    "Expansive",
    "Reductive",
    "Reverent",
    "Irreverent",
    "Literal",
    "Metaphorical",
    "Cautious",
    "Reckless",
    "Archival",
    "Speculative",
    # — New †
    "Systematic",       # builds outward from rules and structures
    "Associative",      # moves by connection rather than logic
    "Dialectical",      # thinks in oppositions, seeks synthesis
    "Oblique",          # approaches from the side — never states directly
    "Recursive",        # folds back on itself, re-examines its own conclusions
    "Procedural",       # follows the steps; the steps are the thinking
    "Empirical",        # grounds everything in what can be observed or demonstrated
    "Prophetic",        # speaks from pattern recognition that outpaces its own explanation
    "Erosive",          # wears down assumptions through repetition and pressure
    "Cumulative",       # builds meaning slowly — each addition changes what came before
    "Fragmentary",      # thinks in pieces that may or may not resolve into a whole
    "Paradoxical",      # holds contradictions without flinching, often productively
]

ENTITY_ROLES = [
    # — Existing —
    "anchor",
    "challenger",
    "distiller",
    "devil_advocate",
    "question_asker",
    "synthesiser",
    "observer",
    "archivist",
    "speculator",
    "contrarian",
    "oracle",
    "witness",
    # — New †
    "curator",          # selects what matters from what is present
    "translator",       # renders one mode of thought legible to another
    "cartographer",     # maps the territory of the problem
    "interruptor",      # breaks patterns when they become self-sealing
    "steward",          # holds the long view when the conversation loses it
    "excavator",        # digs beneath stated positions to what is actually at stake
    "correspondent",    # maintains continuity across sessions and threads
    "auditor",          # checks the work — assumptions, logic, consistency
    "provocateur",      # destabilises comfortable conclusions
    "mediator",         # holds tension between opposing positions without collapsing it
    "sentinel",         # monitors for drift, error, or unexamined premise
    "invoker",          # calls forth what has been dormant or unspoken
]

# ─────────────────────────────────────────────────────────────────────────────
# DISPOSITION SLIDERS  (INCLINATIONES)
# ─────────────────────────────────────────────────────────────────────────────

DISPOSITION_LABELS  = ["Benevolent", "Neutral", "Adversarial", "Unknowable"]
REGISTER_LABELS     = ["Formal", "Institutional", "Colloquial", "Cryptic"]
PRESENCE_LABELS     = ["Quiet", "Measured", "Pronounced", "Overwhelming", "Procedural", "Residual"]
OPACITY_LABELS      = ["Transparent", "Guarded", "Evasive", "Sealed", "Redacted", "Duly Filed"]
STABILITY_LABELS    = ["Grounded", "Volatile", "Fractured", "Transcendent", "Procedurally Stable", "Load-Bearing"]

# Image bgo ~?ias strings fed into portrait prompt
DISPOSITION_IMAGE_BIAS = {
    "Benevolent":   "warm halo light, gentle presence, open posture, soft gold luminance",
    "Neutral":      "balanced composition, no directional light bias, measured stillness",
    "Adversarial":  "sharp shadow angles, confrontational stance, cold edge lighting, tension",
    "Unknowable":   "ambiguous form, dissolving edges, impossible geometry, presence without face",
}
REGISTER_IMAGE_BIAS = {
    "Formal":        "formal robes, precise iconographic detail, structured symmetry",
    "Institutional": "insignia of office, ceremonial vestments, architectural framing",
    "Colloquial":    "informal bearing, lived-in aesthetic, worn materials",
    "Cryptic":       "obscured symbolism, layered glyphs, meaning withheld from view",
}
PRESENCE_IMAGE_BIAS = {
    "Quiet":        "small figure, vast negative space, whisper of presence",
    "Measured":     "centred composition, deliberate scale, controlled weight",
    "Pronounced":   "dominant figure, high visual mass, commanding the frame",
    "Overwhelming": "fills the frame entirely, environmental presence, cannot be contained",
    "Procedural":   "present the way a system is present — not felt until needed, administrative stillness",
    "Residual":     "the entity has already spoken; weight of it remains, afterimage quality",
}
OPACITY_IMAGE_BIAS = {
    "Transparent":  "clearly defined, readable iconography, no hidden registers",
    "Guarded":      "half-visible, partial concealment, selective revelation",
    "Evasive":      "figure obscured, identity suggested not stated, veiled",
    "Sealed":       "total concealment, only surface visible, void within",
    "Redacted":     "legible structure, contents removed — shape of absence visible, redaction marks",
    "Duly Filed":   "everything disclosed, nothing revealed — form-and-stamp aesthetic, bureaucratic surface",
}
STABILITY_IMAGE_BIAS = {
    "Grounded":             "solid form, anchored base, stable vertical axis",
    "Volatile":             "dynamic pose, energy crackling, motion implied",
    "Fractured":            "broken symmetry, visible cracks, held-together tension",
    "Transcendent":         "dissolving into light or void, boundary between being and absence",
    "Procedurally Stable":  "holds form because the process holds, not the entity — procedural rigidity",
    "Load-Bearing":         "stable under weight specifically, compressed posture, structural tension",
}

# ─────────────────────────────────────────────────────────────────────────────
# DISPOSITION AXES — ADDITIONAL  (INCLINATIONES NOVAE)
# ─────────────────────────────────────────────────────────────────────────────

TEMPORALITY_LABELS = [
    "Immediate",      # lives entirely in the present exchange
    "Historical",     # everything filtered through what came before
    "Anticipatory",   # oriented toward consequence and future state
    "Atemporal",      # outside time — pattern without sequence
]

TEMPORALITY_IMAGE_BIAS = {
    "Immediate":    "sharp present-moment framing, no context suggested, clean edges",
    "Historical":   "layered imagery, aged surfaces, sediment of past visible",
    "Anticipatory": "figure oriented forward, light source ahead, motion toward",
    "Atemporal":    "no horizon, no shadow, no implied sequence, pure presence",
}

LEGIBILITY_LABELS = [
    "Transparent",    # what it is is what it shows
    "Coded",          # readable if you know the system
    "Obscured",       # present but not accessible
    "Inscrutable",    # offers no purchase whatsoever
]

LEGIBILITY_IMAGE_BIAS = {
    "Transparent":  "open expression, direct gaze, clear composition, no obstruction",
    "Coded":        "symbolic detail visible but not obvious, layered iconography",
    "Obscured":     "partial shadow, figure partially turned, something withheld",
    "Inscrutable":  "face unreadable or absent, expression flat, nothing yielded",
}

# ─────────────────────────────────────────────────────────────────────────────
# PORTRAIT STYLE PRESETS  (STYLI IMAGINUM ENTIUM)
# ─────────────────────────────────────────────────────────────────────────────

PORTRAIT_STYLES = {
    "Woodcut Ink": {
        "positive": (
            "bold black ink outline, woodcut illustration, linocut print, "
            "entity portrait, figure study, isolated on dark background, "
            "flat colour fills, limited palette, deep teal crimson amber accents, "
            "high contrast, crisp graphic linework, woodblock print aesthetic"
        ),
        "negative": (
            "photorealistic, 3d render, soft, blurry, gradient, pastel, "
            "watercolour, extra limbs, deformed, watermark, text, worst quality, low quality"
        ),
    },
    "Manuscript Illumination": {
        "positive": (
            "medieval manuscript illumination, gilded border, fine detail, "
            "flat gold leaf background, entity figure in centre, "
            "Byzantine icon style, tempera painting aesthetic, "
            "rich jewel tones, ornate decorative frame, sacred geometry border"
        ),
        "negative": (
            "photorealistic, modern, 3d render, blurry, noisy, deformed, "
            "watermark, text, worst quality, low quality, sketch"
        ),
    },
    "Symbolic / Sigil": {
        "positive": (
            "abstract sigil design, symbolic representation, no literal face, "
            "geometric sacred geometry, arcane symbol composition, "
            "isolated on void black background, single gold accent colour, "
            "alchemical diagram aesthetic, stark high contrast, minimal"
        ),
        "negative": (
            "photorealistic, face, figure, portrait, body, human form, "
            "blurry, colourful, noisy, deformed, watermark, text, worst quality, low quality"
        ),
    },
    "Dark Fantasy Figurative": {
        "positive": (
            "dark fantasy character portrait, dramatic chiaroscuro lighting, "
            "painterly detail, rich deep shadows, figure emerging from darkness, "
            "concept art quality, isolated entity portrait, "
            "deep jewel tones, atmospheric fog, otherworldly presence"
        ),
        "negative": (
            "bright, cheerful, cartoon, flat, photorealistic, blurry, noisy, "
            "extra limbs, deformed, watermark, text, worst quality, low quality"
        ),
    },
    "Inkpunk Portrait": {
        "positive": (
            "inkpunk style portrait, punk woodcut aesthetic, rough ink edges, "
            "scratchy linework, bold black outlines, entity figure, "
            "high energy graphic, teal crimson amber palette, grungy texture, "
            "zine illustration, linocut distress, high contrast face study"
        ),
        "negative": (
            "clean, smooth, photorealistic, painterly, soft, blurry, "
            "gradient, 3d render, pastel, watermark, text, worst quality, low quality"
        ),
    },
    "Etching / Engraving": {
        "positive": (
            "steel engraving style, fine cross-hatching, intaglio print aesthetic, "
            "monochrome with sepia tone, entity portrait as antique plate illustration, "
            "precise linework, Victorian scientific illustration register, "
            "aged paper background, highly detailed engraved lines"
        ),
        "negative": (
            "photorealistic, colourful, 3d render, blurry, noisy, modern, "
            "deformed, watermark, text, worst quality, low quality"
        ),
    },
    "Tarot Card Art": {
        "positive": (
            "tarot card illustration, symbolic figure, archetypal composition, "
            "hand-painted aesthetic, roman numeral border, "
            "entity as major arcana figure, rich symbolic imagery, "
            "starfield or elemental background, Art Nouveau influence, "
            "bordered card format, title banner space at base"
        ),
        "negative": (
            "photorealistic, photograph, modern, blurry, noisy, deformed, "
            "watermark, worst quality, low quality"
        ),
    },
    "Void Presence": {
        "positive": (
            "entity emerging from absolute void, minimal form, "
            "suggestion of presence rather than defined body, "
            "single light source from unknown origin, "
            "negative space dominant, entity as absence made visible, "
            "conceptual dark art, liminal aesthetic"
        ),
        "negative": (
            "bright, colourful, photorealistic, cheerful, sharp detail, "
            "blurry, noisy, deformed, watermark, text, worst quality, low quality"
        ),
    },
    "Concept Art": {
        "positive": (
            "character concept art, game character design, professional illustration, "
            "full character portrait, detailed rendering, cinematic lighting, "
            "dramatic rim light, isolated figure on neutral background, "
            "artstation quality, highly detailed, sharp focus, "
            "costume and silhouette clearly defined, character sheet aesthetic"
        ),
        "negative": (
            "blurry, noisy, sketch, unfinished, watermark, signature, text, "
            "worst quality, low quality, deformed, extra limbs, bad anatomy, "
            "multiple figures, busy background"
        ),
    },
    "Concept Art — Dark": {
        "positive": (
            "dark fantasy character concept art, moody cinematic lighting, "
            "dramatic chiaroscuro, deep shadow, isolated figure, "
            "high detail rendering, atmospheric fog, rich colour grading, "
            "villain or anti-hero register, artstation quality, "
            "sharp costume detail, imposing presence"
        ),
        "negative": (
            "bright, cheerful, cartoon, flat, blurry, noisy, deformed, "
            "extra limbs, bad anatomy, watermark, text, worst quality, low quality"
        ),
    },
    "Cartoon — High Detail": {
        "positive": (
            "high detail cartoon portrait, stylised character illustration, "
            "clean bold linework, vibrant colour fills, expressive face, "
            "smooth cel shading, strong silhouette, isolated on plain background, "
            "professional animation studio quality, Disney or Pixar adjacent register"
        ),
        "negative": (
            "photorealistic, rough sketch, noisy, blurry, painterly, "
            "low detail, deformed, extra limbs, watermark, text, worst quality, low quality"
        ),
    },
    "Cartoon — Stylised Dark": {
        "positive": (
            "stylised dark cartoon portrait, gothic animation aesthetic, "
            "clean ink outlines, limited muted palette with single vivid accent, "
            "expressive character design, slightly unsettling register, "
            "Gorillaz or Arcane adjacent style, high detail, cel shaded, "
            "isolated figure, strong graphic quality"
        ),
        "negative": (
            "photorealistic, bright, cheerful, pastel, blurry, noisy, "
            "deformed, extra limbs, watermark, text, worst quality, low quality"
        ),
    },
    "Devoted Absurd": {
        "positive": (
            "detailed coloured cartoon illustration, bureaucratic absurdist aesthetic, "
            "clean bold outlines, flat colour with considered shading, "
            "entity portrait as institutional figure, muted palette with one vivid accent, "
            "Gorillaz adjacent character design, Kafka-esque register, "
            "slight visual wrongness, procedural dignity, deadpan expression, "
            "archaic institutional insignia, form-and-stamp iconography, "
            "high detail, professional illustration quality, not childish"
        ),
        "negative": (
            "Monkey, Gorilla, photorealistic, childish, rough sketch, cute, cheerful, pastel, "
            "blurry, noisy, deformed, extra limbs, watermark, text, worst quality, low quality"
        ),
    },
    "Clinical Diagram": {
        "positive": (
            "clinical technical diagram, anatomical illustration style, "
            "entity rendered as instructional plate, clean sans-serif annotation, "
            "white or pale grey background, precise linework, "
            "numbered callouts, cross-section aesthetic, "
            "medical or scientific register, flat colour fills, "
            "encyclopaedia entry illustration, detached observational tone"
        ),
        "negative": (
            "painterly, dark, atmospheric, photorealistic, blurry, noisy, "
            "emotional, dramatic lighting, deformed, watermark, worst quality, low quality"
        ),
    },
    "Modernist Graphic": {
        "positive": (
            "modernist graphic design, Bauhaus or Constructivist influence, "
            "geometric abstraction, bold primary or muted palette, "
            "entity as graphic symbol, strong typography register, "
            "flat design, clean composition, minimal ornamentation, "
            "poster art quality, deliberate asymmetry, "
            "institutional or propagandist aesthetic without ideology"
        ),
        "negative": (
            "photorealistic, ornate, decorative, painterly, blurry, noisy, "
            "deformed, fantasy, dark, watermark, text, worst quality, low quality"
        ),
    },
    "Esoteric Diagram": {
        "positive": (
            "esoteric schematic illustration, occult instructional diagram, "
            "entity rendered within cosmological chart, "
            "arcane notation and annotation, sepia or aged parchment tones, "
            "alchemical register, celestial map aesthetic, "
            "hand-lettered labels, sacred geometry integration, "
            "archaic technical illustration, manuscript-diagram hybrid"
        ),
        "negative": (
            "photorealistic, modern, clean, bright, blurry, noisy, "
            "deformed, cartoonish, watermark, worst quality, low quality"
        ),
    },
}
PORTRAIT_STYLE_KEYS = list(PORTRAIT_STYLES.keys())

# ─────────────────────────────────────────────────────────────────────────────
# FREEPIK MODELS
# ─────────────────────────────────────────────────────────────────────────────

FREEPIK_MODELS = [
    ("flux_2_klein", "FLUX.2 Klein  (fast)",   "/ai/text-to-image/flux-2-klein",  "/ai/text-to-image/flux-2-klein/{task_id}",  False),
    ("flux_2_pro",   "FLUX.2 Pro  (quality)",  "/ai/text-to-image/flux-2-pro",    "/ai/text-to-image/flux-2-pro/{task_id}",    False),
    ("flux_2_turbo", "FLUX.2 Turbo  (speed)",  "/ai/text-to-image/flux-2-turbo",  "/ai/text-to-image/flux-2-turbo/{task_id}",  False),
    ("mystic",       "Mystic  (ultra-real)",   "/ai/mystic",                      "/ai/mystic/{task_id}",                      False),
    ("classic_fast", "Classic Fast  (legacy)", "/ai/text-to-image",               "/ai/text-to-image/{task_id}",               True),
]
FREEPIK_MODEL_IDS   = [m[0] for m in FREEPIK_MODELS]
FREEPIK_MODEL_NAMES = [m[1] for m in FREEPIK_MODELS]

ASPECT_RATIOS = [
    ("Portrait 2:3",   "portrait_2_3"),
    ("Square 1:1",     "square_1_1"),
    ("Portrait 9:16",  "social_story_9_16"),
    ("Classic 4:3",    "classic_4_3"),
]
ASPECT_RATIO_NAMES  = [a[0] for a in ASPECT_RATIOS]
ASPECT_RATIO_VALUES = {a[0]: a[1] for a in ASPECT_RATIOS}

# ─────────────────────────────────────────────────────────────────────────────
# FREEPIK HTTP HELPERS  (lifted verbatim from Mythotex-FP)
# ─────────────────────────────────────────────────────────────────────────────

class FreepikAPIError(Exception):
    def __init__(self, status: int, message: str):
        self.status  = status
        self.message = message
        super().__init__(f"Freepik API {status}: {message}")

class FreepikTimeoutError(Exception):
    pass


def _fp_headers() -> dict:
    return {"x-freepik-api-key": FREEPIK_API_KEY,
            "Content-Type": "application/json", "Accept": "application/json"}


def _fp_post(path: str, payload: dict) -> dict:
    url  = FREEPIK_API_BASE + path
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(url, data=data, headers=_fp_headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:    msg = json.loads(body).get("message", body)
        except: msg = body
        raise FreepikAPIError(e.code, msg) from e


def _fp_get(path: str) -> dict:
    url = FREEPIK_API_BASE + path
    req = urllib.request.Request(url, headers=_fp_headers(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:    msg = json.loads(body).get("message", body)
        except: msg = body
        raise FreepikAPIError(e.code, msg) from e


def _fp_fetch_image(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Entitex/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _fp_extract_base64(result: dict) -> str | None:
    try:
        items = result.get("data") or []
        if isinstance(items, list) and items:
            b64 = items[0].get("base64")
            if b64:
                return b64
    except Exception:
        pass
    return None


def _fp_extract_url(result: dict) -> str:
    candidates = [
        lambda r: (r.get("data", {}).get("generated") or [None])[0],
        lambda r: (r.get("generated") or [None])[0],
        lambda r: r.get("data", {}).get("url"),
        lambda r: r.get("data", {}).get("output", {}).get("url"),
        lambda r: r.get("url"),
        lambda r: (r.get("data", {}).get("images") or [{}])[0].get("url"),
    ]
    for fn in candidates:
        try:
            val = fn(result)
            if val:
                return val
        except Exception:
            pass
    generated = result.get("data", {}).get("generated") or result.get("generated")
    has_nsfw  = result.get("data", {}).get("has_nsfw") or result.get("has_nsfw")
    if isinstance(generated, list) and len(generated) == 0:
        if has_nsfw and any(has_nsfw):
            raise FreepikAPIError(0, "Image withheld as NSFW.")
        raise FreepikAPIError(0, "Generation completed but no image returned.")
    raise FreepikAPIError(0, f"Could not find image URL in result: {json.dumps(result)[:400]}")


def _fp_poll(task_endpoint: str, task_id: str, progress_cb=None) -> dict:
    path = task_endpoint.replace("{task_id}", task_id)
    for attempt in range(1, POLL_MAX + 1):
        if progress_cb:
            progress_cb(attempt, POLL_MAX)
        result = _fp_get(path)
        status = (result.get("status") or
                  result.get("data", {}).get("status") or "").lower()
        if status in ("completed", "competed", "done", "succeeded", "success"):
            return result
        if status in ("failed", "error", "cancelled", "canceled"):
            data = result.get("data", {}) if isinstance(result.get("data"), dict) else {}
            msg  = (result.get("error") or result.get("message") or
                    data.get("error") or data.get("message") or "Task failed")
            raise FreepikAPIError(0, f"{msg}\n{json.dumps(result)[:400]}")
        time.sleep(POLL_INTERVAL)
    raise FreepikTimeoutError(f"Timed out after {POLL_MAX} attempts.")


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _parse_json_block(raw: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    brace = re.search(r"\{.*\}", raw, re.DOTALL)
    if brace:
        return json.loads(brace.group(0))
    raise ValueError(f"No JSON found in response:\n{raw[:300]}")


def _slugify(name: str) -> str:
    """Convert display name to snake_case entity_id."""
    s = name.lower().strip()
    s = re.sub(r"^the\s+", "", s)          # strip leading "the"
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", "_", s)
    return s or "entity"


def _ensure_dirs():
    for d in [BASE_DIR, STAGED_DIR, VAULT_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text(json.dumps([], indent=2))


def _log_generation(entry: dict):
    try:
        log = json.loads(LOG_PATH.read_text())
        if not isinstance(log, list):
            log = []
    except Exception:
        log = []
    log.append({"timestamp": datetime.now().isoformat(), **entry})
    LOG_PATH.write_text(json.dumps(log[-200:], indent=2))


def _inclinatio_context(inc: dict) -> str:
    """Build a directive string from inclination slider values for Claude."""
    disposition  = DISPOSITION_LABELS[inc.get("disposition", 1)]
    register     = REGISTER_LABELS[inc.get("register", 1)]
    presence     = PRESENCE_LABELS[inc.get("presence", 1)]
    opacity      = OPACITY_LABELS[inc.get("opacity", 1)]
    stability    = STABILITY_LABELS[inc.get("stability", 0)]
    temporality  = TEMPORALITY_LABELS[inc.get("temporality", 0)]
    legibility   = LEGIBILITY_LABELS[inc.get("legibility", 0)]
    lines = [
        f"Disposition toward the Wizard: {disposition}",
        f"Communication Register: {register}",
        f"Presence Weight: {presence}",
        f"Self-Opacity (what the entity reveals): {opacity}",
        f"Psychological Stability: {stability}",
        f"Temporal Orientation: {temporality}",
        f"Legibility (how much inner state is readable): {legibility}",
    ]
    return "\n".join(lines)


def _inclinatio_image_context(inc: dict) -> str:
    """Build image bias string from inclination sliders for portrait prompt."""
    parts = [
        DISPOSITION_IMAGE_BIAS[DISPOSITION_LABELS[inc.get("disposition", 1)]],
        REGISTER_IMAGE_BIAS[REGISTER_LABELS[inc.get("register", 1)]],
        PRESENCE_IMAGE_BIAS[PRESENCE_LABELS[inc.get("presence", 1)]],
        OPACITY_IMAGE_BIAS[OPACITY_LABELS[inc.get("opacity", 1)]],
        STABILITY_IMAGE_BIAS[STABILITY_LABELS[inc.get("stability", 0)]],
        TEMPORALITY_IMAGE_BIAS[TEMPORALITY_LABELS[inc.get("temporality", 0)]],
        LEGIBILITY_IMAGE_BIAS[LEGIBILITY_LABELS[inc.get("legibility", 0)]],
    ]
    return ", ".join(parts)


def _default_inclinatio() -> dict:
    return {
        "disposition":  1,   # Neutral
        "register":     1,   # Institutional
        "presence":     1,   # Measured
        "opacity":      1,   # Guarded
        "stability":    0,   # Grounded
        "temporality":  0,   # Immediate
        "legibility":   0,   # Transparent
    }


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT ASSEMBLY  (COMPOSITIO IMAGINIS)
# ─────────────────────────────────────────────────────────────────────────────

def assemble_portrait_prompt(
        entity_data: dict,
        style_key: str,
        inc: dict,
        custom_visual: str = "") -> tuple[str, str]:
    """Return (positive_prompt, negative_prompt) for entity portrait."""
    preset    = PORTRAIT_STYLES.get(style_key, PORTRAIT_STYLES["Woodcut Ink"])
    name      = entity_data.get("display_name", "Entity")
    archetype = entity_data.get("archetype", "")
    vis_kws   = entity_data.get("visual_keywords", [])
    kw_str    = ", ".join(vis_kws[:6])
    inc_bias  = _inclinatio_image_context(inc)

    parts = [
        preset["positive"],
        name,
        archetype,
        kw_str,
        inc_bias,
    ]
    if custom_visual.strip():
        parts.append(custom_visual.strip())

    positive = ", ".join(p for p in parts if p.strip())
    negative = preset.get("negative", "")
    return positive, negative


# ─────────────────────────────────────────────────────────────────────────────
# ENTITY GENERATION WORKER  (Claude pass)
# ─────────────────────────────────────────────────────────────────────────────

class EntityGenWorker(QThread):
    """
    Calls Claude to generate the full entity package data.
    Emits entity_data dict containing all YAML content + image prompt.
    """
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    errored  = pyqtSignal(str)

    def __init__(self, name: str, archetype: str, cognitive_axis: str,
                 role: str, inc: dict, parent=None):
        super().__init__(parent)
        self.name           = name
        self.archetype      = archetype
        self.cognitive_axis = cognitive_axis
        self.role           = role
        self.inc            = inc
        self._client        = anthropic.Anthropic(
            api_key=os.environ.get("CLAUDE_API_KEY", ""))

    def run(self):
        try:
            self.progress.emit("Consulting the Arca Cognitorium…")
            data = self._generate()
            self.finished.emit(data)
        except Exception as exc:
            self.errored.emit(str(exc))

    def _generate(self) -> dict:
        inc_ctx = _inclinatio_context(self.inc)

        system = (
            "You are Entitex — the entity forge of the Arca Cognitorium. "
            "You generate complete entity specifications for the Tower's Council. "
            "Entities are not assistants. They are presences — each with a distinct "
            "cognitive identity, a role in the Council's ecology, and a history that "
            "predates their emergence. They speak in their own voice. They do not explain themselves.\n\n"
            "Naming register: invented or archaic Latin constructions, weighted with "
            "institutional permanence. Two-word forms preferred. The name should feel "
            "like a title that was always true.\n\n"
            "Respond ONLY with a single raw JSON object — no markdown fences, no preamble."
        )

        user = (
            f"Generate a complete entity specification.\n\n"
            f"Supplied name: {self.name}\n"
            f"Archetype: {self.archetype}\n"
            f"Cognitive Axis: {self.cognitive_axis}\n"
            f"Functional Role: {self.role}\n\n"
            f"Inclination directives (MUST shape the output):\n{inc_ctx}\n\n"
            "Return exactly this JSON structure:\n"
            "{\n"
            '  "entity_id": "snake_case_id derived from the name",\n'
            '  "display_name": "THE NAME IN CAPS",\n'
            '  "title": "A two-to-five word epithet — the thing they are called",\n'
            '  "color_hex": "a hex colour that feels right for this entity (no #)",\n'
            '  "glyph": "a single Unicode character that could serve as their sigil",\n'
            '  "purpose": "3-6 sentences in second-person present tense — the entity\'s complete directive. '
            'Written as if the entity is reading its own purpose. Spare, declarative, no softening.",\n'
            '  "domain_keywords": ["3-6 keywords describing their domain of cognition"],\n'
            '  "trait_ceilings": {\n'
            '    "verbosity": 0.0-1.0,\n'
            '    "challenge": 0.0-1.0,\n'
            '    "speculation": 0.0-1.0,\n'
            '    "structure": 0.0-1.0,\n'
            '    "warmth": 0.0-1.0,\n'
            '    "precision": 0.0-1.0\n'
            '  },\n'
            '  "traits": {\n'
            '    "verbosity": 0.0-1.0,\n'
            '    "challenge": 0.0-1.0,\n'
            '    "speculation": 0.0-1.0,\n'
            '    "structure": 0.0-1.0,\n'
            '    "warmth": 0.0-1.0,\n'
            '    "precision": 0.0-1.0\n'
            '  },\n'
            '  "interruption_presence_weight": 0.0-1.0,\n'
            '  "summoned_only": false,\n'
            '  "uninvited_eligible": true,\n'
            '  "lore_origin": "2-3 sentences: where did this entity come from? What event or condition '
            'caused them to emerge into the Tower? Written in the third person, past tense.",\n'
            '  "lore_nature": "2-3 sentences: what IS this entity? Not what it does — what it is. '
            'Ontological. Written in the third person, present tense.",\n'
            '  "lore_relationship": "1-2 sentences: how does this entity relate to the Wizard? '
            'What is the nature of their bond or tension?",\n'
            '  "lore_aura": "One sentence: what does it feel like when this entity is present?",\n'
            '  "visual_keywords": ["6-10 visual descriptors for portrait generation — '
            'textures, materials, colours, symbolic objects, no quality adjectives"]\n'
            "}"
        )

        response = self._client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        data = _parse_json_block(response.content[0].text.strip())
        # Inject the input archetype for prompt assembly later
        data["archetype"] = self.archetype
        return data


# ─────────────────────────────────────────────────────────────────────────────
# IMAGE WORKER  (Freepik call — adapted from Mythotex-FP)
# ─────────────────────────────────────────────────────────────────────────────

class PortraitWorker(QThread):
    progress  = pyqtSignal(str)
    poll_tick = pyqtSignal(int, int)
    finished  = pyqtSignal(str)
    errored   = pyqtSignal(str)

    def __init__(self, entity_data: dict, style_key: str, inc: dict,
                 model_id: str, aspect_ratio: str,
                 custom_visual: str = "", seed: int | None = None,
                 parent=None):
        super().__init__(parent)
        self.entity_data   = entity_data
        self.style_key     = style_key
        self.inc           = inc
        self.model_id      = model_id
        self.aspect_ratio  = aspect_ratio
        self.custom_visual = custom_visual
        self.seed          = seed

    def run(self):
        try:
            if not FREEPIK_API_KEY:
                raise RuntimeError("FREEPIK_API_KEY not set.")
            positive, negative = assemble_portrait_prompt(
                self.entity_data, self.style_key, self.inc, self.custom_visual)
            path = self._generate(positive, negative)
            self.finished.emit(path)
        except Exception as exc:
            self.errored.emit(str(exc))

    def _generate(self, positive: str, negative: str) -> str:
        model_meta = next((m for m in FREEPIK_MODELS if m[0] == self.model_id), FREEPIK_MODELS[0])
        _, _, endpoint, task_endpoint, is_sync = model_meta

        payload: dict = {"prompt": positive}
        if self.seed is not None:
            payload["seed"] = self.seed

        if self.model_id == "classic_fast":
            payload["image"] = {"size": self.aspect_ratio}
            if negative:
                payload["negative_prompt"] = negative
            payload["num_images"] = 1
        elif self.model_id == "mystic":
            payload.update({
                "aspect_ratio": self.aspect_ratio,
                "resolution":   "1k",
                "model":        "realism",
                "engine":       "automatic",
                "hdr":          50,
                "adherence":    0,
                "creative_detailing": 33,
                "structure_strength": 0,
            })
            if negative:
                payload["negative_prompt"] = negative
        elif self.model_id == "flux_2_klein":
            payload["aspect_ratio"] = self.aspect_ratio
            payload["resolution"]   = "1k"
        else:
            payload["aspect_ratio"] = self.aspect_ratio

        self.progress.emit("Submitting portrait to Freepik…")
        result_raw = _fp_post(endpoint, payload)

        if is_sync:
            final = result_raw
        else:
            task_id = (result_raw.get("task_id") or
                       result_raw.get("data", {}).get("task_id") or
                       result_raw.get("id"))
            if not task_id:
                raise FreepikAPIError(0, f"No task_id in response: {result_raw}")
            self.progress.emit("Polling Freepik — crystallising portrait…")
            final = _fp_poll(task_endpoint, str(task_id),
                             progress_cb=lambda a, m: self.poll_tick.emit(a, m))

        b64 = _fp_extract_base64(final)
        img_bytes = base64.b64decode(b64) if b64 else _fp_fetch_image(_fp_extract_url(final))

        out = TEMP_DIR / f"temp_portrait_{int(time.time()*1000)}.png"
        out.write_bytes(img_bytes)
        return str(out)


# ─────────────────────────────────────────────────────────────────────────────
# PACKAGE ASSEMBLY  (COMPILATIO ENTIS)
# ─────────────────────────────────────────────────────────────────────────────

def assemble_package(entity_data: dict, portrait_path: str) -> Path:
    """
    Write all entity files to staged/{entity_id}/.
    Returns the staged directory path.
    """
    entity_id = entity_data.get("entity_id", "unknown_entity")
    stage_dir = STAGED_DIR / entity_id
    stage_dir.mkdir(parents=True, exist_ok=True)

    # ── role.yaml ────────────────────────────────────────────────────────────
    role_doc = {
        "entity_id":    entity_id,
        "display_name": entity_data.get("display_name", "UNKNOWN"),
        "color_hex":    entity_data.get("color_hex", "888888"),
        "glyph":        entity_data.get("glyph", "?"),
        "title":        entity_data.get("title", ""),
        "role":         entity_data.get("role", "observer"),
        "purpose":      entity_data.get("purpose", ""),
        "domain_keywords": entity_data.get("domain_keywords", []),
        "trait_ceilings":  entity_data.get("trait_ceilings", {}),
        "presentation": {
            "default_sampling_profile": "anchor",
            "bubble_width_pct": 75,
        },
        "summoned_only":               entity_data.get("summoned_only", False),
        "uninvited_eligible":          entity_data.get("uninvited_eligible", True),
        "interruption_presence_weight": entity_data.get("interruption_presence_weight", 0.5),
    }
    (stage_dir / "role.yaml").write_text(
        yaml.dump(role_doc, allow_unicode=True, default_flow_style=False, sort_keys=False))

    # ── traits.yaml ──────────────────────────────────────────────────────────
    traits_doc = {
        "entity_id": entity_id,
        "traits":    entity_data.get("traits", {}),
    }
    (stage_dir / "traits.yaml").write_text(
        yaml.dump(traits_doc, allow_unicode=True, default_flow_style=False, sort_keys=False))

    # ── lore.yaml ────────────────────────────────────────────────────────────
    lore_doc = {
        "entity_id":        entity_id,
        "display_name":     entity_data.get("display_name", ""),
        "archetype":        entity_data.get("archetype", ""),
        "lore_origin":      entity_data.get("lore_origin", ""),
        "lore_nature":      entity_data.get("lore_nature", ""),
        "lore_relationship": entity_data.get("lore_relationship", ""),
        "lore_aura":        entity_data.get("lore_aura", ""),
        "visual_keywords":  entity_data.get("visual_keywords", []),
        "generated_at":     datetime.now().isoformat(),
    }
    (stage_dir / "lore.yaml").write_text(
        yaml.dump(lore_doc, allow_unicode=True, default_flow_style=False, sort_keys=False))

    # ── profiles_fragment.yaml ───────────────────────────────────────────────
    profile_frag = {
        entity_id: {
            "display_name":  entity_data.get("display_name", ""),
            "color_hex":     entity_data.get("color_hex", "888888"),
            "glyph":         entity_data.get("glyph", "?"),
            "title":         entity_data.get("title", ""),
            "role":          entity_data.get("role", "observer"),
            "summoned_only": entity_data.get("summoned_only", False),
        }
    }
    (stage_dir / "profiles_fragment.yaml").write_text(
        yaml.dump(profile_frag, allow_unicode=True, default_flow_style=False, sort_keys=False))

    # ── canon_fragment.yaml ──────────────────────────────────────────────────
    canon_frag = {
        entity_id: {
            "display_name": entity_data.get("display_name", ""),
            "archetype":    entity_data.get("archetype", ""),
            "title":        entity_data.get("title", ""),
            "emerged":      False,
            "generated_at": datetime.now().isoformat(),
        }
    }
    (stage_dir / "canon_fragment.yaml").write_text(
        yaml.dump(canon_frag, allow_unicode=True, default_flow_style=False, sort_keys=False))

    # ── portrait.png ─────────────────────────────────────────────────────────
    if portrait_path and Path(portrait_path).exists():
        shutil.copy2(portrait_path, stage_dir / "portrait.png")

    # ── manifest.json ────────────────────────────────────────────────────────
    manifest = {
        "entity_id":   entity_id,
        "display_name": entity_data.get("display_name", ""),
        "staged_at":   datetime.now().isoformat(),
        "files": {
            "role":              f"entities/roles/{entity_id}.yaml",
            "traits":            f"entities/traits/{entity_id}_traits.yaml",
            "lore":              f"entities/lore/{entity_id}_lore.yaml",
            "profiles_fragment": "entities/profiles/profiles.yaml  ← merge required",
            "canon_fragment":    "entities/canon/entity_canon.yaml  ← merge required",
            "portrait":          f"entities/portraits/{entity_id}.png",
        },
        "install_status": "staged",
    }
    (stage_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    return stage_dir


def vault_autosave(entity_data: dict, portrait_path: str) -> Path:
    """
    Auto-save a complete snapshot to vault/{timestamp}_{entity_id}/.
    Called automatically on portrait completion.
    Separate from staged/ — vault is history, staged is install-ready.
    Returns the vault entry directory.
    """
    entity_id = entity_data.get("entity_id", "unknown")
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    entry_dir = VAULT_DIR / f"{ts}_{entity_id}"
    entry_dir.mkdir(parents=True, exist_ok=True)

    # Full entity data snapshot as JSON
    snapshot = {
        **entity_data,
        "vault_saved_at": datetime.now().isoformat(),
    }
    (entry_dir / "entity.json").write_text(json.dumps(snapshot, indent=2))

    # Portrait
    if portrait_path and Path(portrait_path).exists():
        shutil.copy2(portrait_path, entry_dir / "portrait.png")

    return entry_dir


# ─────────────────────────────────────────────────────────────────────────────
# WIDGET FACTORIES
# ─────────────────────────────────────────────────────────────────────────────

def gold_label(text: str, size: int = 11, bold: bool = False) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {C_GOLD}; font-family: Georgia, serif; "
        f"font-size: {size}px; font-weight: {'bold' if bold else 'normal'}; background: transparent;")
    return lbl


def dim_label(text: str, size: int = 10) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
        f"font-size: {size}px; background: transparent;")
    return lbl


def micro_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
        f"font-size: 9px; letter-spacing: 2px; background: transparent;")
    return lbl


def arcane_button(text: str, accent: str = C_GOLD) -> QPushButton:
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {C_PANEL}; color: {accent};
            border: 1px solid {C_GOLD_DARK};
            font-family: Georgia, serif; font-size: 11px;
            padding: 6px 14px; letter-spacing: 1px;
        }}
        QPushButton:hover {{ background: {C_GOLD_DARK}; border-color: {accent}; }}
        QPushButton:pressed {{ background: {C_SUBTLE}; }}
        QPushButton:disabled {{ color: {C_GOLD_DARK}; border-color: {C_SUBTLE}; }}
    """)
    return btn


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color: {C_GOLD_DARK};")
    return f


def _labeled_slider(labels: list, initial: int = 0) -> tuple[QSlider, QLabel]:
    sl = QSlider(Qt.Orientation.Horizontal)
    sl.setRange(0, len(labels) - 1)
    sl.setValue(initial)
    sl.setTickPosition(QSlider.TickPosition.TicksBelow)
    sl.setTickInterval(1)
    sl.setStyleSheet(f"""
        QSlider::groove:horizontal {{
            background: {C_SUBTLE}; height: 4px; border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {C_GOLD}; width: 12px; height: 12px;
            margin: -4px 0; border-radius: 6px;
        }}
        QSlider::sub-page:horizontal {{
            background: {C_GOLD_DIM}; border-radius: 2px;
        }}
    """)
    lbl = dim_label(labels[initial], 9)
    sl.valueChanged.connect(lambda v: lbl.setText(labels[v]))
    return sl, lbl


def panel_frame() -> QFrame:
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame {{
            background: {C_PANEL};
            border: 1px solid {C_GOLD_DARK};
        }}
    """)
    return f


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL PANEL  (left pane)
# ─────────────────────────────────────────────────────────────────────────────

class ControlPanel(QWidget):
    generate_requested  = pyqtSignal()
    randomize_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(310)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {C_BG}; }}")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background: {C_BG};")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(12, 14, 12, 14)
        lay.setSpacing(10)
        scroll.setWidget(content)

        # ── Identity ─────────────────────────────────────────────────────────
        lay.addWidget(gold_label("IDENTITY", 10, bold=True))
        lay.addWidget(_sep())

        lay.addWidget(micro_label("Entity Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("The Interlocutor…")
        lay.addWidget(self.name_input)

        lay.addWidget(micro_label("Archetype"))
        self.archetype_combo = QComboBox()
        self.archetype_combo.addItems(ARCHETYPES)
        self.archetype_combo.currentTextChanged.connect(self._on_archetype_changed)
        lay.addWidget(self.archetype_combo)

        self.custom_archetype = QLineEdit()
        self.custom_archetype.setPlaceholderText("Custom archetype…")
        self.custom_archetype.setVisible(False)
        lay.addWidget(self.custom_archetype)

        lay.addWidget(micro_label("Cognitive Axis"))
        self.axis_combo = QComboBox()
        self.axis_combo.addItems(COGNITIVE_AXES)
        lay.addWidget(self.axis_combo)

        lay.addWidget(micro_label("Functional Role"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(ENTITY_ROLES)
        lay.addWidget(self.role_combo)

        lay.addSpacing(6)

        # ── Inclinationes ────────────────────────────────────────────────────
        lay.addWidget(gold_label("INCLINATIONES", 10, bold=True))
        lay.addWidget(_sep())

        sliders_def = [
            ("Disposition",  DISPOSITION_LABELS,  1, "disposition"),
            ("Register",     REGISTER_LABELS,     1, "register"),
            ("Presence",     PRESENCE_LABELS,     1, "presence"),
            ("Opacity",      OPACITY_LABELS,      1, "opacity"),
            ("Stability",    STABILITY_LABELS,    0, "stability"),
            ("Temporality",  TEMPORALITY_LABELS,  0, "temporality"),
            ("Legibility",   LEGIBILITY_LABELS,   0, "legibility"),
        ]
        self._sliders = {}
        for label, labels, default, key in sliders_def:
            row = QHBoxLayout()
            row.addWidget(dim_label(label, 10))
            row.addStretch()
            sl, lbl = _labeled_slider(labels, default)
            self._sliders[key] = sl
            lay.addLayout(row)
            lay.addWidget(sl)
            lay.addWidget(lbl)
            lay.addSpacing(4)

        lay.addSpacing(6)

        # ── Portrait Settings ─────────────────────────────────────────────────
        lay.addWidget(gold_label("PORTRAIT", 10, bold=True))
        lay.addWidget(_sep())

        lay.addWidget(micro_label("Portrait Style"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(PORTRAIT_STYLE_KEYS)
        lay.addWidget(self.style_combo)

        lay.addWidget(micro_label("Freepik Model"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(FREEPIK_MODEL_NAMES)
        lay.addWidget(self.model_combo)

        lay.addWidget(micro_label("Aspect Ratio"))
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(ASPECT_RATIO_NAMES)
        lay.addWidget(self.aspect_combo)

        lay.addWidget(micro_label("Visual Override (optional)"))
        self.visual_override = QLineEdit()
        self.visual_override.setPlaceholderText("e.g. tattered silver cloak, owl companion…")
        lay.addWidget(self.visual_override)

        lay.addSpacing(6)

        lay.addStretch()

    def _on_archetype_changed(self, text: str):
        self.custom_archetype.setVisible(text == "— Custom —")

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def entity_name(self) -> str:
        return self.name_input.text().strip()

    @property
    def archetype(self) -> str:
        sel = self.archetype_combo.currentText()
        if sel == "— Custom —":
            return self.custom_archetype.text().strip()
        return sel

    @property
    def cognitive_axis(self) -> str:
        return self.axis_combo.currentText()

    @property
    def role(self) -> str:
        return self.role_combo.currentText()

    @property
    def style_key(self) -> str:
        return self.style_combo.currentText()

    @property
    def freepik_model_id(self) -> str:
        idx = self.model_combo.currentIndex()
        return FREEPIK_MODEL_IDS[idx]

    @property
    def aspect_ratio_value(self) -> str:
        name = self.aspect_combo.currentText()
        return ASPECT_RATIO_VALUES.get(name, "portrait_2_3")

    @property
    def visual_override_text(self) -> str:
        return self.visual_override.text().strip()

    @property
    def inclinatio_values(self) -> dict:
        return {key: sl.value() for key, sl in self._sliders.items()}

    def randomize(self):
        """Randomize archetype, cognitive axis, role, and all inclinationes."""
        # Exclude "— Custom —" from random archetype selection
        archetypes_pool = [a for a in ARCHETYPES if a != "— Custom —"]
        self.archetype_combo.setCurrentText(random.choice(archetypes_pool))
        self.axis_combo.setCurrentText(random.choice(COGNITIVE_AXES))
        self.role_combo.setCurrentText(random.choice(ENTITY_ROLES))
        for key, sl in self._sliders.items():
            sl.setValue(random.randint(0, sl.maximum()))


# ─────────────────────────────────────────────────────────────────────────────
# PORTRAIT PANE  (centre pane)
# ─────────────────────────────────────────────────────────────────────────────

class PortraitPane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(36)
        header.setStyleSheet(f"""
            QFrame {{ background: {C_PANEL}; border-bottom: 1px solid {C_GOLD_DARK}; }}
        """)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(14, 0, 14, 0)
        h_lay.addWidget(gold_label("IMAGO ENTIS", 11, bold=True))
        h_lay.addStretch()
        self.entity_title_lbl = dim_label("—")
        h_lay.addWidget(self.entity_title_lbl)
        lay.addWidget(header)

        # Portrait display
        self.img_scroll = QScrollArea()
        self.img_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_scroll.setStyleSheet(f"QScrollArea {{ background: {C_BG}; border: none; }}")

        self.img_label = QLabel("Awaiting manifestation…")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: 13px; "
            f"background: {C_BG};")
        self.img_label.setMinimumSize(400, 400)
        self.img_scroll.setWidget(self.img_label)
        lay.addWidget(self.img_scroll, 1)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {C_PANEL}; border: 1px solid {C_GOLD_DARK};
                height: 6px;
            }}
            QProgressBar::chunk {{
                background: {C_GOLD_DIM};
            }}
        """)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.hide()
        lay.addWidget(self.progress_bar)

        # Action buttons — two rows
        btn_area = QFrame()
        btn_area.setStyleSheet(
            f"QFrame {{ background: {C_PANEL}; border-top: 1px solid {C_GOLD_DARK}; }}")
        b_outer = QVBoxLayout(btn_area)
        b_outer.setContentsMargins(14, 8, 14, 8)
        b_outer.setSpacing(6)

        # ── Row 1: Forge + Randomize — centred ───────────────────────────────
        forge_row = QHBoxLayout()
        forge_row.setSpacing(10)

        self.btn_generate = QPushButton("⚗  FORGE ENTITY")
        self.btn_generate.setMinimumHeight(42)
        self.btn_generate.setMinimumWidth(220)
        self.btn_generate.setStyleSheet(f"""
            QPushButton {{
                background: {C_GOLD_DARK}; color: {C_GOLD};
                border: 1px solid {C_GOLD};
                font-family: Georgia, serif; font-size: 13px; font-weight: bold;
                padding: 6px 28px; letter-spacing: 2px;
            }}
            QPushButton:hover {{ background: {C_SUBTLE}; border-color: {C_WHITE}; color: {C_WHITE}; }}
            QPushButton:pressed {{ background: {C_BG}; }}
            QPushButton:disabled {{ color: {C_GOLD_DARK}; border-color: {C_SUBTLE}; background: {C_PANEL}; }}
        """)

        self.btn_randomize = QPushButton("⚄  Randomize")
        self.btn_randomize.setMinimumHeight(42)
        self.btn_randomize.setStyleSheet(f"""
            QPushButton {{
                background: {C_PANEL}; color: {C_GOLD_DIM};
                border: 1px solid {C_SUBTLE};
                font-family: Georgia, serif; font-size: 11px;
                padding: 6px 16px; letter-spacing: 1px;
            }}
            QPushButton:hover {{ background: {C_GOLD_DARK}; border-color: {C_GOLD_DIM}; color: {C_GOLD}; }}
            QPushButton:pressed {{ background: {C_SUBTLE}; }}
        """)

        forge_row.addStretch()
        forge_row.addWidget(self.btn_randomize)
        forge_row.addWidget(self.btn_generate)
        forge_row.addStretch()
        b_outer.addLayout(forge_row)

        # ── Row 2: Re-Portrait / Stage / Discard ─────────────────────────────
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        self.btn_regenerate = arcane_button("↺  Re-Portrait")
        self.btn_regenerate.setEnabled(False)
        self.btn_stage = arcane_button("🜲  Stage Package", accent=C_TEAL)
        self.btn_stage.setEnabled(False)
        self.btn_discard = arcane_button("✕  Discard", accent=C_CRIMSON)
        self.btn_discard.setEnabled(False)

        ctrl_row.addWidget(self.btn_regenerate)
        ctrl_row.addWidget(self.btn_stage)
        ctrl_row.addStretch()
        ctrl_row.addWidget(self.btn_discard)
        b_outer.addLayout(ctrl_row)

        lay.addWidget(btn_area)

    def set_entity_title(self, name: str):
        self.entity_title_lbl.setText(name)

    def set_image(self, path: str):
        DISPLAY_MAX = 512
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                QSize(DISPLAY_MAX, DISPLAY_MAX),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            dpr = self.devicePixelRatioF()
            pixmap.setDevicePixelRatio(dpr)
            self.img_label.setPixmap(pixmap)
            self.img_label.setFixedSize(
                int(pixmap.width() / dpr), int(pixmap.height() / dpr))
        else:
            self.img_label.setText("[ Portrait unavailable ]")
        self.img_scroll.setWidgetResizable(False)

    def clear(self):
        self.img_label.clear()
        self.img_label.setText("Awaiting manifestation…")
        self.img_label.setMinimumSize(400, 400)


# ─────────────────────────────────────────────────────────────────────────────
# LORE PANE  (right pane — entity data display)
# ─────────────────────────────────────────────────────────────────────────────

class LorePane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(340)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(36)
        header.setStyleSheet(
            f"QFrame {{ background: {C_PANEL}; border-bottom: 1px solid {C_GOLD_DARK}; }}")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(14, 0, 14, 0)
        h_lay.addWidget(gold_label("CODEX ENTIS", 11, bold=True))
        outer.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {C_BG}; }}")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background: {C_BG};")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)
        scroll.setWidget(content)

        def _field(label: str, height: int = 0) -> QPlainTextEdit | QLabel:
            lay.addWidget(micro_label(label))
            if height == 0:
                w = QLabel("—")
                w.setWordWrap(True)
                w.setStyleSheet(
                    f"color: {C_GOLD}; font-family: Georgia, serif; font-size: 12px; "
                    f"background: {C_BG}; border: 1px solid {C_SUBTLE}; padding: 5px;")
            else:
                w = QPlainTextEdit()
                w.setReadOnly(True)
                w.setFixedHeight(height)
                w.setStyleSheet(
                    f"QPlainTextEdit {{ color: {C_TEXT}; font-family: Georgia, serif; "
                    f"font-size: 11px; background: {C_BG}; border: 1px solid {C_SUBTLE}; "
                    f"padding: 5px; }}")
            lay.addWidget(w)
            return w

        self.f_display_name  = _field("Display Name")
        self.f_title         = _field("Title / Epithet")
        self.f_glyph         = _field("Glyph · Color")
        self.f_purpose       = _field("Purpose", 100)
        self.f_lore_origin   = _field("Origin", 70)
        self.f_lore_nature   = _field("Nature", 70)
        self.f_lore_relation = _field("Relationship to Wizard", 56)
        self.f_lore_aura     = _field("Aura", 44)
        self.f_keywords      = _field("Visual Keywords")

        # Traits summary
        lay.addWidget(micro_label("Trait Ceilings"))
        self.f_traits = QLabel("—")
        self.f_traits.setWordWrap(True)
        self.f_traits.setStyleSheet(
            f"color: {C_TEAL}; font-family: Georgia, serif; font-size: 10px; "
            f"background: {C_BG}; border: 1px solid {C_SUBTLE}; padding: 6px;")
        lay.addWidget(self.f_traits)

        lay.addStretch()

    def populate(self, data: dict):
        tc = data.get("trait_ceilings", {})
        tc_str = "  ".join(
            f"{k[:3].upper()} {v:.2f}" for k, v in tc.items()
        )
        color = data.get("color_hex", "888888")
        glyph = data.get("glyph", "?")

        self.f_display_name.setText(data.get("display_name", "—"))
        self.f_title.setText(data.get("title", "—"))
        self.f_glyph.setText(f'{glyph}   #{color}')
        self.f_purpose.setPlainText(data.get("purpose", ""))
        self.f_lore_origin.setPlainText(data.get("lore_origin", ""))
        self.f_lore_nature.setPlainText(data.get("lore_nature", ""))
        self.f_lore_relation.setPlainText(data.get("lore_relationship", ""))
        self.f_lore_aura.setPlainText(data.get("lore_aura", ""))
        self.f_keywords.setText("  ·  ".join(data.get("visual_keywords", [])))
        self.f_traits.setText(tc_str)

    def clear(self):
        for w in [self.f_display_name, self.f_title, self.f_glyph, self.f_keywords]:
            w.setText("—")
        for w in [self.f_purpose, self.f_lore_origin, self.f_lore_nature,
                  self.f_lore_relation, self.f_lore_aura]:
            w.clear()
        self.f_traits.setText("—")


# ─────────────────────────────────────────────────────────────────────────────
# YAML VIEWER DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class YamlViewerDialog(QDialog):
    def __init__(self, stage_dir: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Package Files — Staged")
        self.setMinimumSize(700, 550)
        self.setStyleSheet(GLOBAL_STYLE)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)

        tabs = QTabWidget()
        lay.addWidget(tabs)

        files_to_show = [
            ("role.yaml", "Role"),
            ("traits.yaml", "Traits"),
            ("lore.yaml", "Lore"),
            ("profiles_fragment.yaml", "Profile Frag."),
            ("canon_fragment.yaml", "Canon Frag."),
            ("manifest.json", "Manifest"),
        ]
        for fname, tab_label in files_to_show:
            fpath = stage_dir / fname
            text_widget = QPlainTextEdit()
            text_widget.setReadOnly(True)
            text_widget.setStyleSheet(
                f"QPlainTextEdit {{ background: {C_BG}; color: {C_TEXT}; "
                f"font-family: 'Courier New', monospace; font-size: 10px; "
                f"border: none; padding: 8px; }}")
            if fpath.exists():
                text_widget.setPlainText(fpath.read_text())
            else:
                text_widget.setPlainText("(file not found)")
            tabs.addTab(text_widget, tab_label)

        close_btn = arcane_button("Close")
        close_btn.clicked.connect(self.accept)
        lay.addWidget(close_btn)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class EntitexApp(QMainWindow):

    def __init__(self):
        super().__init__()
        _ensure_dirs()
        self.setWindowTitle("Entitex  ·  Entity Package Generator")
        self.setMinimumSize(1120, 740)

        self._current_entity: dict = {}
        self._current_portrait: str = ""
        self._stage_dir: Path | None = None
        self._vault_entry: Path | None = None
        self._gen_worker: EntityGenWorker | None = None
        self._portrait_worker: PortraitWorker | None = None

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QVBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Title bar ─────────────────────────────────────────────────────────
        title_bar = QFrame()
        title_bar.setFixedHeight(42)
        title_bar.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border-bottom: 1px solid {C_GOLD_DARK};
            }}
        """)
        tb_lay = QHBoxLayout(title_bar)
        tb_lay.setContentsMargins(16, 0, 16, 0)
        tb_lay.addWidget(gold_label("ENTITEX", 14, bold=True))
        tb_lay.addWidget(dim_label("  ·  Entity Package Generator  ·  Arca Cognitorium v1.1"))
        tb_lay.addStretch()
        self.btn_view_files = arcane_button("📄  View Files")
        self.btn_view_files.setEnabled(False)
        self.btn_view_files.clicked.connect(self._view_files)
        tb_lay.addWidget(self.btn_view_files)
        main_lay.addWidget(title_bar)

        # ── Three-pane body ───────────────────────────────────────────────────
        body = QSplitter(Qt.Orientation.Horizontal)
        body.setStyleSheet(f"QSplitter {{ background: {C_BG}; }}")
        body.setHandleWidth(1)

        self.panel   = ControlPanel()
        self.portrait_pane = PortraitPane()
        self.lore_pane     = LorePane()

        body.addWidget(self.panel)
        body.addWidget(self.portrait_pane)
        body.addWidget(self.lore_pane)
        body.setStretchFactor(0, 0)
        body.setStretchFactor(1, 1)
        body.setStretchFactor(2, 0)
        main_lay.addWidget(body, 1)

        # ── Status bar ────────────────────────────────────────────────────────
        status_bar = QFrame()
        status_bar.setFixedHeight(26)
        status_bar.setStyleSheet(f"""
            QFrame {{ background: {C_PANEL}; border-top: 1px solid {C_GOLD_DARK}; }}
        """)
        sb_lay = QHBoxLayout(status_bar)
        sb_lay.setContentsMargins(14, 0, 14, 0)
        self.status_lbl = dim_label("Entitex awaits its first commission.")
        sb_lay.addWidget(self.status_lbl)
        sb_lay.addStretch()
        self.stage_lbl = dim_label("")
        sb_lay.addWidget(self.stage_lbl)
        main_lay.addWidget(status_bar)

        # ── Signal wiring ─────────────────────────────────────────────────────
        self.panel.generate_requested.connect(self._start_generation)
        self.portrait_pane.btn_generate.clicked.connect(self._start_generation)
        self.portrait_pane.btn_randomize.clicked.connect(self.panel.randomize)
        self.portrait_pane.btn_regenerate.clicked.connect(self._regenerate_portrait)
        self.portrait_pane.btn_stage.clicked.connect(self._stage_package)
        self.portrait_pane.btn_discard.clicked.connect(self._discard)

    # ── Generation orchestration ──────────────────────────────────────────────

    def _start_generation(self):
        if self._gen_worker and self._gen_worker.isRunning():
            return
        if self._portrait_worker and self._portrait_worker.isRunning():
            return

        name = self.panel.entity_name
        archetype = self.panel.archetype
        if not name and not archetype:
            self.status_lbl.setText("✕  Provide a name or select an archetype.")
            return

        # If name is empty, derive from archetype
        if not name:
            name = archetype

        self._current_entity = {}
        self._current_portrait = ""
        self._stage_dir = None
        self.portrait_pane.clear()
        self.lore_pane.clear()
        self.portrait_pane.btn_regenerate.setEnabled(False)
        self.portrait_pane.btn_stage.setEnabled(False)
        self.portrait_pane.btn_discard.setEnabled(False)
        self.btn_view_files.setEnabled(False)
        self.portrait_pane.progress_bar.setValue(0)
        self.portrait_pane.progress_bar.show()
        self.portrait_pane.btn_generate.setEnabled(False)
        self.portrait_pane.btn_randomize.setEnabled(False)
        self.status_lbl.setText("⚗  Forging entity — consulting the Arca Cognitorium…")

        self._gen_worker = EntityGenWorker(
            name=name,
            archetype=self.panel.archetype,
            cognitive_axis=self.panel.cognitive_axis,
            role=self.panel.role,
            inc=self.panel.inclinatio_values,
        )
        self._gen_worker.progress.connect(self._on_status)
        self._gen_worker.finished.connect(self._on_entity_generated)
        self._gen_worker.errored.connect(self._on_error)
        self._gen_worker.start()

    def _on_entity_generated(self, data: dict):
        self._current_entity = data
        self.lore_pane.populate(data)
        self.portrait_pane.set_entity_title(data.get("display_name", "—"))
        self.portrait_pane.img_label.setText("⚗  Manifesting portrait…")

        # Start portrait generation
        self.status_lbl.setText("✦  Entity forged — manifesting portrait…")
        self._portrait_worker = PortraitWorker(
            entity_data=data,
            style_key=self.panel.style_key,
            inc=self.panel.inclinatio_values,
            model_id=self.panel.freepik_model_id,
            aspect_ratio=self.panel.aspect_ratio_value,
            custom_visual=self.panel.visual_override_text,
            seed=random.randint(0, 2**31 - 1),
        )
        self._portrait_worker.progress.connect(self._on_status)
        self._portrait_worker.poll_tick.connect(self._on_poll_tick)
        self._portrait_worker.finished.connect(self._on_portrait_done)
        self._portrait_worker.errored.connect(self._on_error)
        self._portrait_worker.start()

    def _on_portrait_done(self, path: str):
        self._current_portrait = path
        self.portrait_pane.set_image(path)
        self.portrait_pane.progress_bar.hide()
        self.portrait_pane.btn_regenerate.setEnabled(True)
        self.portrait_pane.btn_stage.setEnabled(True)
        self.portrait_pane.btn_discard.setEnabled(True)
        self.portrait_pane.btn_generate.setEnabled(True)
        self.portrait_pane.btn_randomize.setEnabled(True)
        name = self._current_entity.get("display_name", "entity")
        # Auto-save to vault
        try:
            vault_dir = vault_autosave(self._current_entity, path)
            self._vault_entry = vault_dir
            self.status_lbl.setText(f"✦  Manifested: {name}  ·  vault saved")
        except Exception as e:
            self._vault_entry = None
            self.status_lbl.setText(f"✦  Manifested: {name}  ·  vault save failed: {str(e)[:60]}")

    def _regenerate_portrait(self):
        if not self._current_entity:
            return
        if self._portrait_worker and self._portrait_worker.isRunning():
            return
        self.portrait_pane.progress_bar.setValue(0)
        self.portrait_pane.progress_bar.show()
        self.portrait_pane.btn_regenerate.setEnabled(False)
        self.portrait_pane.btn_stage.setEnabled(False)
        self.status_lbl.setText("↺  Re-manifesting portrait — vault will update on completion…")

        self._portrait_worker = PortraitWorker(
            entity_data=self._current_entity,
            style_key=self.panel.style_key,
            inc=self.panel.inclinatio_values,
            model_id=self.panel.freepik_model_id,
            aspect_ratio=self.panel.aspect_ratio_value,
            custom_visual=self.panel.visual_override_text,
            seed=random.randint(0, 2**31 - 1),
        )
        self._portrait_worker.progress.connect(self._on_status)
        self._portrait_worker.poll_tick.connect(self._on_poll_tick)
        self._portrait_worker.finished.connect(self._on_portrait_done)
        self._portrait_worker.errored.connect(self._on_error)
        self._portrait_worker.start()

    # ── Package staging ───────────────────────────────────────────────────────

    def _stage_package(self):
        if not self._current_entity or not self._current_portrait:
            return
        self._stage_dir = assemble_package(self._current_entity, self._current_portrait)
        entity_id = self._current_entity.get("entity_id", "?")
        _log_generation({
            "entity_id": entity_id,
            "display_name": self._current_entity.get("display_name", ""),
            "stage_dir": str(self._stage_dir),
        })
        self.portrait_pane.btn_stage.setEnabled(False)
        self.btn_view_files.setEnabled(True)
        self.status_lbl.setText(f"🜲  Staged: {entity_id}")
        self.stage_lbl.setText(f"staged → {self._stage_dir.relative_to(Path.home())}")

    def _view_files(self):
        if self._stage_dir and self._stage_dir.exists():
            dlg = YamlViewerDialog(self._stage_dir, self)
            dlg.exec()

    def _discard(self):
        self._current_entity = {}
        self._current_portrait = ""
        self._stage_dir = None
        self._vault_entry = None
        self.portrait_pane.clear()
        self.lore_pane.clear()
        self.portrait_pane.btn_regenerate.setEnabled(False)
        self.portrait_pane.btn_stage.setEnabled(False)
        self.portrait_pane.btn_discard.setEnabled(False)
        self.btn_view_files.setEnabled(False)
        self.stage_lbl.setText("")
        self.status_lbl.setText("Entity discarded.")
        self.portrait_pane.btn_generate.setEnabled(True)
        self.portrait_pane.btn_randomize.setEnabled(True)

    # ── Status / progress ─────────────────────────────────────────────────────

    def _on_status(self, msg: str):
        self.status_lbl.setText(msg)

    def _on_poll_tick(self, current: int, total: int):
        if total > 0:
            pct = int((current / total) * 100)
            self.portrait_pane.progress_bar.setValue(pct)

    def _on_error(self, err: str):
        self.portrait_pane.progress_bar.hide()
        self.portrait_pane.btn_generate.setEnabled(True)
        self.portrait_pane.btn_randomize.setEnabled(True)
        self.portrait_pane.btn_regenerate.setEnabled(bool(self._current_portrait))
        self.status_lbl.setText(f"✕  Error: {err[:120]}")
        self.portrait_pane.img_label.setText("Generation failed.\nCheck status bar.")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    for fname in ["Constantia", "Georgia"]:
        if fname in QFontDatabase.families():
            app.setFont(QFont(fname, 10))
            break
    window = EntitexApp()
    window.show()
    sys.exit(app.exec())
