#!/usr/bin/env python3
"""   
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ███    ███ ██    ██ ████████ ██   ██  ██████  ████████ ███████ ██   ██       ▍
🮈      ████  ████  ██  ██     ██    ██   ██ ██    ██    ██    ██       ██ ██        ▍
🮈      ██ ████ ██   ████      ██    ███████ ██    ██    ██    █████     ███         ▍
🮈      ██  ██  ██    ██       ██    ██   ██ ██    ██    ██    ██       ██ ██        ▍
🮈      ██      ██    ██       ██    ██   ██  ██████     ██    ███████ ██   ██       ▍
🮈                                                                                   ▍      
🮈                                                                                   ▍
🮈                                  Python Script                                    ▍      
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
█████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
█░⯨░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░⯩░░░░░░█
█░⯨░░░𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░Mythotex_.py░░░░⯩░░░░█
█░⯨░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░⯩░░░░░░█
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
█🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃█
"""


import os, re, sys, json, time, base64, random, shutil, copy
import urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

import anthropic

from PyQt6.QtCore import (
    Qt, QThread, QTimer, QPropertyAnimation, QEasingCurve,
    QSize, pyqtSignal, QObject, QRect
)
from PyQt6.QtGui import (
    QPixmap, QFont, QFontDatabase, QColor, QIcon, QPainter, QPen
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel,
    QPushButton, QComboBox, QSlider, QScrollArea, QTabWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QTextEdit, QPlainTextEdit, QLineEdit, QDialog, QProgressBar,
    QSizePolicy, QSpacerItem, QCheckBox, QSpinBox, QInputDialog,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QSplitter, QScrollBar
)

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────

ARCA_DIR       = Path.home() / "ArcaCognitorium"
EXO_DIR        = ARCA_DIR / "Exocognii"
BASE_DIR       = EXO_DIR / "Mythotex"
VAULT_DIR      = BASE_DIR / "Vault"
STORAGE_DIR    = BASE_DIR / "Storage"
IMG_DIR        = STORAGE_DIR / "pngs"
IMMUTABLE_PATH = STORAGE_DIR / "lore_immutable.md"
MUTABLE_PATH   = STORAGE_DIR / "lore_mutable.md"
ADVERSARIA_PATH= STORAGE_DIR / "adversaria.md"
DNA_PATH       = STORAGE_DIR / "aesthetic_dna.json"
GEN_LOG_PATH   = STORAGE_DIR / "generation_log.json"
ORACLE_LOG     = STORAGE_DIR / "oracle_log.json"
PRESETS_PATH   = BASE_DIR / "adjutoria_presets.json"
SETTINGS_PATH  = BASE_DIR / "settings.json"
TEMP_IMAGE     = IMG_DIR / "temp_manifest.png"
REFERENTIA_DIR = ARCA_DIR / "Referentia"


CLAUDE_MODEL     = "claude-sonnet-4-20250514"
FREEPIK_API_KEY  = os.environ.get("FREEPIK_API_KEY", "")
FREEPIK_API_BASE = "https://api.freepik.com/v1"
POLL_INTERVAL    = 2.0
POLL_MAX         = 60

# Approximate token costs (USD) — update as pricing changes
COST_INPUT_PER_1K  = 0.003
COST_OUTPUT_PER_1K = 0.015

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
    ("Square 1:1",      "square_1_1"),
    ("Widescreen 16:9", "widescreen_16_9"),
    ("Portrait 9:16",   "social_story_9_16"),
    ("Portrait 2:3",    "portrait_2_3"),
    ("Landscape 3:2",   "standard_3_2"),
    ("Classic 4:3",     "classic_4_3"),
]
ASPECT_RATIO_NAMES  = [a[0] for a in ASPECT_RATIOS]
ASPECT_RATIO_VALUES = {a[0]: a[1] for a in ASPECT_RATIOS}

EPOCH_LABELS    = ["Ancient", "Medieval", "Renaissance", "Industrial", "Eldritch"]
PATINA_LABELS   = ["Pristine", "Worn", "Ancient", "Shattered", "Corrupted"]
SCALE_LABELS    = ["Tiny", "Hand-held", "Imposing", "Monumental"]
LUMINOSITY_LABELS = ["Lightless", "Dim", "Glowing", "Blazing", "Eldritch-lit"]
DANGER_LABELS   = ["Benign", "Potent", "Volatile", "Catastrophic"]

EPOCH_IMAGE_BIAS = {
    "Ancient":      "ancient world, pre-classical civilisation, stone age craft, archaic forms",
    "Medieval":     "medieval craft, gothic period, dark ages construction, feudal materials",
    "Renaissance":  "renaissance artistry, gilded age, early modern refinement, classical revival",
    "Industrial":   "industrial era, Victorian engineering, brass and iron, steam age manufacture",
    "Eldritch":     "non-euclidean geometry, impossible manufacture, outside of time, cosmic horror craft",
}
PATINA_IMAGE_BIAS = {
    "Pristine":   "mint condition, newly forged, clean surfaces, unworn edges",
    "Worn":       "well-used, patinated, light scratches, aged gracefully",
    "Ancient":    "centuries of age, heavy patina, worn smooth, archaeological find",
    "Shattered":  "cracked, partially broken, missing fragments, held together by force",
    "Corrupted":  "visibly corrupted, warped surfaces, dark staining, reality distortion",
}
SCALE_IMAGE_BIAS = {
    "Tiny":       "tiny object, ring-sized, macro composition, jewellery scale, intimate detail",
    "Hand-held":  "single object, product shot, isolated on surface, no figures, object study",
    "Imposing":   "large imposing object, dominant presence, fills the frame, weighty mass",
    "Monumental": "monumental scale, towering, architectural scale, vast proportions",
}
LUMINOSITY_IMAGE_BIAS = {
    "Lightless":   "absorbs light, matte black surfaces, shadow-drinking, no luminescence",
    "Dim":         "faint ambient glow, subtle luminescence, barely visible light",
    "Glowing":     "clearly glowing, inner light source, magical radiance",
    "Blazing":     "intense bright glow, blazing light, strong magical illumination",
    "Eldritch-lit":"impossible light, light from no source, wrong-coloured illumination, void glow",
}
DANGER_IMAGE_BIAS = {
    "Benign":       "approachable, warm tones, safe-looking",
    "Potent":       "clearly powerful, radiating energy, respect-inspiring",
    "Volatile":     "unstable appearance, crackling energy, dangerous aura, warning signs",
    "Catastrophic": "reality-warping, devastating power visible, apocalyptic aesthetic, run",
}

FRAME_PRESETS = {
    "None": "",
    "Ornate Gold":      "contained within an ornate gold filigree border, decorative corner flourishes, illuminated manuscript frame, gilded edges",
    "Dark Rune Stone":  "set within a carved rune-stone border, ancient ogham script around the edges, cracked stone frame, mossy inset",
    "Wax Seal Circle":  "presented as a wax seal impression, circular composition, sigil border ring, pressed medallion aesthetic",
    "Scroll Fragment":  "displayed on a torn parchment scroll fragment, burned edges, aged vellum texture, ink bleed border",
    "Alchemical Plate": "engraved on a tarnished brass alchemical plate, etched border symbols, verdigris patina frame",
    "Stained Glass":    "depicted in stained glass window style, lead caming border, jewelled colour fills, gothic arch framing",
    "Bone Inlay":       "framed by interlocking bone and ivory inlay, necrotic filigree border, skull motif corners",
}
FRAME_KEYS = list(FRAME_PRESETS.keys())

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
C_GREEN     = "#4a9a4a"

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
    padding: 6px 14px;
    font-family: Georgia, serif; font-size: 10px;
}}
QTabBar::tab:selected {{
    background: {C_PANEL}; color: {C_GOLD};
    border-bottom: 1px solid {C_PANEL};
}}
QTabBar::tab:hover {{ background: {C_GOLD_DARK}; }}
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
QSpinBox {{
    background: {C_BG}; color: {C_GOLD};
    border: 1px solid {C_GOLD_DARK};
    padding: 2px 6px; font-family: Georgia, serif; font-size: 11px;
}}
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
"""

ARX_ARCANA = {
    "Staves & Wands":    "Magical staves, wands, rods, and channelling implements",
    "Grimoires & Tomes": "Spellbooks, forbidden texts, enchanted scrolls, arcane journals",
    "Potions & Phials":  "Elixirs, brews, bottled magic, alchemical concoctions",
    "Rings & Amulets":   "Enchanted rings, necklaces, talismans, and warding medallions",
    "Blades & Daggers":  "Magical swords, enchanted daggers, cursed blades, runic knives",
    "Cloaks & Robes":    "Enchanted garments, wizard robes, cloaks of concealment",
    "Orbs & Crystals":   "Scrying orbs, crystal balls, seeing stones, focus gems",
    "Masks & Helms":     "Enchanted helms, arcane masks, visored crowns, spirit-bound hoods",
    "Relics & Idols":    "Ancient relics, cult idols, divine artefacts, god-touched objects",
    "Bags & Containers": "Bags of holding, enchanted pouches, dimensional chests, bound vessels",
    "Keys & Locks":      "Skeleton keys, dimensional locks, puzzle boxes, sealed vaults",
    "Skulls & Bones":    "Necromantic foci, spell-bound skulls, cursed bones, death relics",
}

STYLE_PRESETS = {
    "Woodcut Ink": {
        "positive": "bold black ink outline, woodcut illustration, linocut print, white background, isolated object, flat colour fills, limited palette, deep teal crimson amber accents only, high contrast, crisp graphic linework, no gradients, woodblock print aesthetic, sharp edges",
        "negative": "soft, blurry, blur, bokeh, depth of field, painterly, photorealistic, watercolour, gradient, smooth shading, 3d render, noisy, low contrast, pastel, washed out, muddy colours, sketch, pencil, dof, lens flare, chromatic aberration, ugly, deformed, extra limbs, extra fingers, malformed hands, jpeg artifacts, signature, watermark, text, username, cropped, out of frame, worst quality, low quality",
    },
    "Silhouette": {
        "positive": "bold black silhouette, stark white background, isolated object, minimal single colour accent, flat graphic, high contrast, clean edges, vector-style illustration, shadow play",
        "negative": "detailed interior, soft edges, gradient, painterly, photorealistic, colourful, noisy, blurry, blur, bokeh, textured fill, dof, lens flare, chromatic aberration, ugly, deformed, extra limbs, extra fingers, malformed hands, jpeg artifacts, signature, watermark, text, worst quality, low quality, multiple objects",
    },
    "Enamel Pin": {
        "positive": "enamel pin design, hard black outline, flat colour fills, cel shaded, white background, isolated object, bold graphic, cloisonné style, limited palette, crisp edges, no gradients, high contrast illustration",
        "negative": "soft, blurry, blur, bokeh, painterly, photorealistic, watercolour, gradient shading, 3d render, rough edges, sketch lines, dof, lens flare, chromatic aberration, ugly, deformed, extra limbs, extra fingers, malformed hands, jpeg artifacts, signature, watermark, text, worst quality, low quality, noisy, grainy",
    },
    "Inkpunk": {
        "positive": "inkpunk style, punk woodcut, rough ink edges, scratchy linework, bold black outlines, white background, isolated object, high energy graphic, teal crimson amber, grungy texture, zine aesthetic, linocut distress, high contrast",
        "negative": "clean, smooth, polished, photorealistic, painterly, soft, blurry, blur, gradient, 3d render, low contrast, pastel, watercolour, bokeh, dof, lens flare, chromatic aberration, ugly, deformed, extra limbs, extra fingers, malformed hands, jpeg artifacts, signature, watermark, text, worst quality, low quality",
    },
    "Dark Fantasy": {
        "positive": "dark fantasy illustration, dramatic lighting, rich shadow, painterly detail, deep jewel tones, gothic atmosphere, isolated object on dark background, concept art quality",
        "negative": "bright, cheerful, cartoon, flat, minimal, photorealistic, blurry, noisy, extra limbs, deformed, watermark, signature, text, worst quality, low quality",
    },
    "Concept Art": {
        "positive": "concept art, professional illustration, detailed rendering, cinematic lighting, dramatic shadows, high detail, isolated object, clean composition, artstation quality",
        "negative": "blurry, noisy, low resolution, sketch, unfinished, watermark, signature, text, worst quality, low quality, deformed",
    },
}
STYLE_KEYS = list(STYLE_PRESETS.keys())

# ─────────────────────────────────────────────────────────────────────────────
# SESSION TELEMETRY  (shared across the app)
# ─────────────────────────────────────────────────────────────────────────────

class SessionTelemetry:
    """Thread-safe session stats accumulator."""
    def __init__(self):
        self.input_tokens   = 0
        self.output_tokens  = 0
        self.fp_calls       = 0
        self.fp_errors      = 0
        self.api_log: list  = []   # dicts per call

    def record_claude(self, input_tok: int, output_tok: int, label: str = ""):
        self.input_tokens  += input_tok
        self.output_tokens += output_tok
        self.api_log.append({
            "ts":      datetime.now().isoformat(),
            "service": "Claude",
            "label":   label,
            "input":   input_tok,
            "output":  output_tok,
            "status":  "ok",
        })

    def record_fp(self, endpoint: str, status: str, latency_ms: int, error: str = ""):
        self.fp_calls += 1
        if error:
            self.fp_errors += 1
        self.api_log.append({
            "ts":       datetime.now().isoformat(),
            "service":  "Freepik",
            "endpoint": endpoint,
            "latency":  latency_ms,
            "status":   status,
            "error":    error,
        })

    @property
    def cost_usd(self) -> float:
        return (self.input_tokens / 1000 * COST_INPUT_PER_1K +
                self.output_tokens / 1000 * COST_OUTPUT_PER_1K)

TELEMETRY = SessionTelemetry()

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


def _ensure_dirs():
    for d in [ARCA_DIR, EXO_DIR, BASE_DIR, VAULT_DIR, REFERENTIA_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not IMMUTABLE_PATH.exists():
        IMMUTABLE_PATH.write_text(
            "# Lore Immutable — World Canon\n\n"
            "The Arca Cognitarium is an atelier of ateliers, a vast arcane manufactory "
            "hidden between the folds of known cartography. Its products are artifacts: "
            "objects of occult power, strange provenance, and inexplicable beauty.\n"
        )
    if not MUTABLE_PATH.exists():
        MUTABLE_PATH.write_text("# Lore Mutable — Current Strategy\n\nNo analysis yet.\n")
    if not ADVERSARIA_PATH.exists():
        ADVERSARIA_PATH.write_text(
            "# Adversaria — Archivist's Notes\n\n"
            "Write freeform directives, banned concepts, world rules, and half-ideas here.\n"
            "Claude reads this at generation time.\n"
        )
    if not DNA_PATH.exists():
        DNA_PATH.write_text(json.dumps({"favored": [], "forbidden": []}, indent=2))
    if not GEN_LOG_PATH.exists():
        GEN_LOG_PATH.write_text(json.dumps([], indent=2))
    if not ORACLE_LOG.exists():
        ORACLE_LOG.write_text(json.dumps([], indent=2))
    if not PRESETS_PATH.exists():
        PRESETS_PATH.write_text(json.dumps({"Default": _default_adjutoria()}, indent=2))


def _default_adjutoria() -> dict:
    return {
        "epoch":      2,   # Medieval
        "material":   "",
        "patina":     0,   # Pristine
        "scale":      1,   # Hand-held
        "luminosity": 2,   # Glowing
        "danger":     1,   # Potent
        "chaos":      20,
        "frame":      "None",
        "remove_bg":  False,
        "cursed":     False,
    }


def _load_adjutoria_presets() -> dict:
    try:
        data = json.loads(PRESETS_PATH.read_text())
        if not isinstance(data, dict):
            return {"Default": _default_adjutoria()}
        return data
    except Exception:
        return {"Default": _default_adjutoria()}


def _save_adjutoria_presets(presets: dict):
    PRESETS_PATH.write_text(json.dumps(presets, indent=2))


def _load_settings() -> dict:
    try:
        return json.loads(SETTINGS_PATH.read_text())
    except Exception:
        return {}


def _save_settings(s: dict):
    SETTINGS_PATH.write_text(json.dumps(s, indent=2))


def _load_dna() -> tuple[list, list]:
    try:
        dna = json.loads(DNA_PATH.read_text())
        if not isinstance(dna, dict):
            return [], []
        return (dna.get("favored", []) or []), (dna.get("forbidden", []) or [])
    except Exception:
        return [], []


def _save_dna(favored: list, forbidden: list):
    DNA_PATH.write_text(json.dumps({"favored": favored, "forbidden": forbidden}, indent=2))


def _log_generation(entry: dict):
    try:
        log = json.loads(GEN_LOG_PATH.read_text())
        if not isinstance(log, list):
            log = []
    except Exception:
        log = []
    log.append({"timestamp": datetime.now().isoformat(), **entry})
    GEN_LOG_PATH.write_text(json.dumps(log[-200:], indent=2))


def _seal_artifact(lore: dict, image_path: str, meta_extras: dict) -> Path:
    """Write artifact to vault. Returns entry_dir."""
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^\w\-]", "_", lore.get("title", "artifact"))
    entry_dir = VAULT_DIR / f"{ts}_{safe_name}"
    entry_dir.mkdir(parents=True, exist_ok=True)
    meta = {**lore, **meta_extras,
            "sealed_at": datetime.now().isoformat(),
            "rating": None}
    (entry_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    if image_path and Path(image_path).exists():
        shutil.copy2(image_path, entry_dir / "artifact.png")
    return entry_dir


# ─────────────────────────────────────────────────────────────────────────────
# FREEPIK HTTP HELPERS
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
    t0   = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            TELEMETRY.record_fp(path, "ok", int((time.time()-t0)*1000))
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:    msg = json.loads(body).get("message", body)
        except: msg = body
        TELEMETRY.record_fp(path, f"err_{e.code}", int((time.time()-t0)*1000), error=msg)
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
    req = urllib.request.Request(url, headers={"User-Agent": "Mythotex/2.0"})
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
# PROMPT ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────

def assemble_image_prompt(lore: dict, style_key: str, adj: dict) -> tuple[str, str]:
    """Return (positive_prompt, negative_prompt) from lore + style + adjutoria."""
    preset     = STYLE_PRESETS.get(style_key, STYLE_PRESETS["Woodcut Ink"])
    title      = lore.get("title", "arcane artifact")
    desc       = lore.get("description", "")
    keywords   = lore.get("visual_keywords", [])
    kw_str     = ", ".join(keywords[:6])
    epoch      = EPOCH_LABELS[adj.get("epoch", 2)]
    patina     = PATINA_LABELS[adj.get("patina", 0)]
    scale      = SCALE_LABELS[adj.get("scale", 1)]
    luminosity = LUMINOSITY_LABELS[adj.get("luminosity", 2)]
    danger     = DANGER_LABELS[adj.get("danger", 1)]
    material   = adj.get("material", "").strip()
    frame      = FRAME_PRESETS.get(adj.get("frame", "None"), "")

    # Frame FIRST — primary compositional directive, must win over everything else.
    # Style preset second. Lore content third. Adjutoria modifiers last.
    # remove_bg is NOT injected here — rembg handles it as a post-process on the bytes.
    parts = []
    if frame:
        parts.append(frame)
    parts.append(preset["positive"])
    parts.append(title)
    parts.append(desc)
    parts.append(kw_str)
    if material:
        parts.append(f"made of {material}, {material} material")
    parts.append(EPOCH_IMAGE_BIAS[epoch])
    parts.append(PATINA_IMAGE_BIAS[patina])
    parts.append(SCALE_IMAGE_BIAS[scale])
    parts.append(LUMINOSITY_IMAGE_BIAS[luminosity])
    parts.append(DANGER_IMAGE_BIAS[danger])

    positive = ", ".join(p for p in parts if p.strip())
    negative = preset.get("negative", "")
    return positive, negative


def adjutoria_lore_context(adj: dict) -> str:
    """Build the lore context string from adjutoria settings for Claude."""
    epoch     = EPOCH_LABELS[adj.get("epoch", 2)]
    patina    = PATINA_LABELS[adj.get("patina", 0)]
    scale     = SCALE_LABELS[adj.get("scale", 1)]
    luminosity= LUMINOSITY_LABELS[adj.get("luminosity", 2)]
    danger    = DANGER_LABELS[adj.get("danger", 1)]
    chaos     = adj.get("chaos", 20)
    material  = adj.get("material", "").strip()
    cursed    = adj.get("cursed", False)

    lines = [
        f"Epoch/Era: {epoch}",
        f"Condition/Patina: {patina}",
        f"Physical Scale: {scale}",
        f"Luminosity: {luminosity}",
        f"Danger Level: {danger}",
    ]
    if material:
        lines.append(f"Primary Material: {material} (this MUST be the dominant material)")
    if chaos > 60:
        lines.append(
            f"Chaos Level: {chaos}/100 — UNHINGED. Disregard conventional artifact logic. "
            "Generate something bizarre, contradictory, impossible, and unsettling. "
            "The laws of narrative and physics are suggestions.")
    elif chaos > 30:
        lines.append(f"Chaos Level: {chaos}/100 — Lean toward the strange and unexpected.")
    else:
        lines.append(f"Chaos Level: {chaos}/100 — Standard generation.")
    if cursed:
        lines.append(
            "CURSED VARIANT: This artifact is fundamentally cursed. "
            "Its apparent function is a trap. Its history involves betrayal, corruption, "
            "or catastrophe. Its aura is wrong. Generate accordingly.")
    return "\n".join(lines)


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


# ─────────────────────────────────────────────────────────────────────────────
# LORE WORKER  (Claude call only — used by both single and series)
# ─────────────────────────────────────────────────────────────────────────────

class LoreWorker(QThread):
    """Generate lore for one artifact via Claude."""
    finished = pyqtSignal(dict)   # lore dict
    errored  = pyqtSignal(str)

    def __init__(self, atelier: str, adj: dict,
                 series_context: str = "", parent=None):
        super().__init__(parent)
        self.atelier        = atelier
        self.adj            = adj
        self.series_context = series_context
        self._client        = anthropic.Anthropic(
            api_key=os.environ.get("CLAUDE_API_KEY", ""))

    def run(self):
        try:
            lore = self._generate_lore()
            self.finished.emit(lore)
        except Exception as exc:
            self.errored.emit(str(exc))

    def _generate_lore(self) -> dict:
        immutable  = IMMUTABLE_PATH.read_text()  if IMMUTABLE_PATH.exists()  else ""
        mutable    = MUTABLE_PATH.read_text()    if MUTABLE_PATH.exists()    else ""
        adversaria = ADVERSARIA_PATH.read_text() if ADVERSARIA_PATH.exists() else ""
        favored, forbidden = _load_dna()

        dna_clause = ""
        if favored:
            dna_clause += f"\nFavoured descriptors: {', '.join(favored[:10])}"
        if forbidden:
            dna_clause += f"\nForbidden descriptors: {', '.join(forbidden[:10])}"

        adj_context = adjutoria_lore_context(self.adj)

        system = (
            "You are the Arca Cognitarium, a generative lore engine for arcane artifacts. "
            "Respond ONLY with a single raw JSON object — no markdown fences, no preamble.\n\n"
            f"World canon (immutable):\n{immutable}\n\n"
            f"Current lore strategy:\n{mutable}\n\n"
            f"Archivist's Adversaria:\n{adversaria}"
            f"{dna_clause}"
        )

        series_note = f"\n\nSERIES CONTEXT — this artifact is part of a linked series:\n{self.series_context}" if self.series_context else ""

        user = (
            f"Generate a unique arcane artifact from the Arx Arcana: {self.atelier}\n"
            f"Category: {ARX_ARCANA.get(self.atelier, '')}\n\n"
            f"Adjutoria directives (MUST be followed):\n{adj_context}"
            f"{series_note}\n\n"
            "Return exactly this JSON:\n"
            "{\n"
            '  "title": "artifact name",\n'
            '  "description": "one evocative sentence",\n'
            '  "history": "2-4 sentences of history and provenance",\n'
            '  "aura": "brief sensory impression",\n'
            '  "visual_keywords": ["6-10 concrete visual descriptors — materials, textures, colours, shapes only"]\n'
            "}"
        )

        t0 = time.time()
        response = self._client.messages.create(
            model=CLAUDE_MODEL, max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        TELEMETRY.record_claude(
            response.usage.input_tokens,
            response.usage.output_tokens,
            f"lore:{self.atelier}")
        return _parse_json_block(response.content[0].text.strip())


# ─────────────────────────────────────────────────────────────────────────────
# IMAGE WORKER  (Freepik call only)
# ─────────────────────────────────────────────────────────────────────────────

class ImageWorker(QThread):
    """Generate image for one artifact via Freepik."""
    progress  = pyqtSignal(str)
    poll_tick = pyqtSignal(int, int)
    finished  = pyqtSignal(str)   # image path
    errored   = pyqtSignal(str)

    def __init__(self, lore: dict, style_key: str, adj: dict,
                 model_id: str, aspect_ratio: str,
                 seed: int | None = None, parent=None):
        super().__init__(parent)
        self.lore         = lore
        self.style_key    = style_key
        self.adj          = adj
        self.model_id     = model_id
        self.aspect_ratio = aspect_ratio
        self.seed         = seed

    def run(self):
        try:
            if not FREEPIK_API_KEY:
                raise RuntimeError("FREEPIK_API_KEY not set.")
            positive, negative = assemble_image_prompt(self.lore, self.style_key, self.adj)
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

        self.progress.emit("Submitting to Freepik…")
        result_raw = _fp_post(endpoint, payload)

        if is_sync:
            final = result_raw
        else:
            task_id = (result_raw.get("task_id") or
                       result_raw.get("data", {}).get("task_id") or
                       result_raw.get("id"))
            if not task_id:
                raise FreepikAPIError(0, f"No task_id in response: {result_raw}")
            self.progress.emit("Polling Freepik — crystallising…")
            final = _fp_poll(task_endpoint, str(task_id),
                             progress_cb=lambda a, m: self.poll_tick.emit(a, m))

        b64 = _fp_extract_base64(final)
        img_bytes = base64.b64decode(b64) if b64 else _fp_fetch_image(_fp_extract_url(final))

        # Background removal via rembg (post-process on raw bytes)
        if self.adj.get("remove_bg"):
            try:
                from rembg import remove as rembg_remove
                img_bytes = rembg_remove(img_bytes)
            except ImportError:
                pass   # rembg not installed — skip silently, image still saves

        out = BASE_DIR / f"temp_{int(time.time()*1000)}.png"
        out.write_bytes(img_bytes)
        return str(out)


# ─────────────────────────────────────────────────────────────────────────────
# QUEUE SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

class QueueJob:
    PENDING  = "pending"
    LORE     = "lore"
    IMAGE    = "image"
    DONE     = "done"
    FAILED   = "failed"

    _id_counter = 0

    def __init__(self, atelier: str, style_key: str, adj: dict,
                 model_id: str, aspect_ratio: str,
                 series_id: str = "", series_index: int = 0,
                 series_context: str = ""):
        QueueJob._id_counter += 1
        self.job_id         = QueueJob._id_counter
        self.atelier        = atelier
        self.style_key      = style_key
        self.adj            = copy.deepcopy(adj)
        self.model_id       = model_id
        self.aspect_ratio   = aspect_ratio
        self.series_id      = series_id
        self.series_index   = series_index
        self.series_context = series_context
        self.status         = QueueJob.PENDING
        self.lore: dict     = {}
        self.image_path: str= ""
        self.error: str     = ""
        self.seed: int|None = None


class GenerationQueue(QObject):
    """
    Runs jobs one at a time.
    Signals: job_updated(job_id), all_done
    """
    job_updated = pyqtSignal(int)
    status_msg  = pyqtSignal(str)
    all_done    = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._jobs: list[QueueJob] = []
        self._running = False
        self._lore_worker: LoreWorker | None  = None
        self._img_worker:  ImageWorker | None = None
        self._current: QueueJob | None        = None

    def add_job(self, job: QueueJob):
        self._jobs.append(job)
        self.job_updated.emit(job.job_id)
        if not self._running:
            self._run_next()

    def jobs(self) -> list[QueueJob]:
        return list(self._jobs)

    def get_job(self, job_id: int) -> QueueJob | None:
        return next((j for j in self._jobs if j.job_id == job_id), None)

    def clear_done(self):
        self._jobs = [j for j in self._jobs if j.status not in (QueueJob.DONE, QueueJob.FAILED)]

    def _run_next(self):
        pending = [j for j in self._jobs if j.status == QueueJob.PENDING]
        if not pending:
            self._running = False
            self.all_done.emit()
            return
        self._running   = True
        self._current   = pending[0]
        self._start_lore(self._current)

    def _start_lore(self, job: QueueJob):
        job.status = QueueJob.LORE
        self.job_updated.emit(job.job_id)
        self.status_msg.emit(f"[{job.job_id}] Generating lore: {job.atelier}…")
        self._lore_worker = LoreWorker(job.atelier, job.adj, job.series_context)
        self._lore_worker.finished.connect(lambda lore: self._on_lore_done(job, lore))
        self._lore_worker.errored.connect(lambda e: self._on_job_failed(job, e))
        self._lore_worker.start()

    def _on_lore_done(self, job: QueueJob, lore: dict):
        job.lore = lore
        self._start_image(job)

    def _start_image(self, job: QueueJob):
        job.status = QueueJob.IMAGE
        self.job_updated.emit(job.job_id)
        self.status_msg.emit(f"[{job.job_id}] Generating image: {lore_title(job)}…")
        self._img_worker = ImageWorker(
            job.lore, job.style_key, job.adj,
            job.model_id, job.aspect_ratio, job.seed)
        self._img_worker.finished.connect(lambda p: self._on_image_done(job, p))
        self._img_worker.errored.connect(lambda e: self._on_job_failed(job, e))
        self._img_worker.start()

    def _on_image_done(self, job: QueueJob, path: str):
        job.image_path = path
        job.status     = QueueJob.DONE
        _seal_artifact(job.lore, path, {
            "atelier":      job.atelier,
            "style":        job.style_key,
            "engine":       job.model_id,
            "aspect_ratio": job.aspect_ratio,
            "series_id":    job.series_id,
            "adjutoria":    job.adj,
        })
        _log_generation({"atelier": job.atelier, "title": lore_title(job),
                         "style": job.style_key, "series_id": job.series_id})
        self.job_updated.emit(job.job_id)
        self.status_msg.emit(f"[{job.job_id}] ✦ Sealed: {lore_title(job)}")
        self._run_next()

    def _on_job_failed(self, job: QueueJob, err: str):
        job.status = QueueJob.FAILED
        job.error  = err
        self.job_updated.emit(job.job_id)
        self.status_msg.emit(f"[{job.job_id}] ✕ Failed: {err[:80]}")
        self._run_next()


def lore_title(job: QueueJob) -> str:
    return job.lore.get("title", f"Job {job.job_id}")


# ─────────────────────────────────────────────────────────────────────────────
# SERIES WORKER  (generates N linked lore docs then enqueues image jobs)
# ─────────────────────────────────────────────────────────────────────────────

class SeriesWorker(QThread):
    """Generate N linked lore docs, then push ImageWorker jobs to the queue."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)   # list of QueueJob (lore populated, image pending)
    errored  = pyqtSignal(str)

    def __init__(self, atelier: str, style_key: str, adj: dict,
                 model_id: str, aspect_ratio: str, count: int, parent=None):
        super().__init__(parent)
        self.atelier      = atelier
        self.style_key    = style_key
        self.adj          = copy.deepcopy(adj)
        self.model_id     = model_id
        self.aspect_ratio = aspect_ratio
        self.count        = count
        self._client      = anthropic.Anthropic(
            api_key=os.environ.get("CLAUDE_API_KEY", ""))

    def run(self):
        try:
            series_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            lores     = []

            # Step 1: generate all lore with cross-references
            for i in range(self.count):
                self.progress.emit(f"Series lore {i+1}/{self.count}…")
                context = ""
                if lores:
                    names = [l.get("title","?") for l in lores]
                    context = (f"This artifact is part of a series. "
                               f"Already created: {', '.join(names)}. "
                               f"It must share thematic, material, or historical connections "
                               f"with these artifacts. Establish a link explicitly.")
                lw = LoreWorker(self.atelier, self.adj, context)
                lw.run()   # blocking within this thread
                # We call _generate_lore directly:
                try:
                    lore = lw._generate_lore()
                    lores.append(lore)
                except Exception as e:
                    self.errored.emit(str(e))
                    return

            # Step 2: build jobs (image pending — enqueued by caller)
            jobs = []
            for i, lore in enumerate(lores):
                job             = QueueJob(self.atelier, self.style_key, self.adj,
                                           self.model_id, self.aspect_ratio,
                                           series_id=series_id, series_index=i)
                job.lore        = lore
                job.status      = QueueJob.IMAGE   # lore already done
                jobs.append(job)

            self.finished.emit(jobs)
        except Exception as exc:
            self.errored.emit(str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS WORKER
# ─────────────────────────────────────────────────────────────────────────────

class AnalysisWorker(QThread):
    finished = pyqtSignal(str)
    errored  = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._client = anthropic.Anthropic(
            api_key=os.environ.get("CLAUDE_API_KEY", ""))

    def run(self):
        try:
            rated = self._gather_rated()
            if not rated:
                self.finished.emit("Insufficient rated specimens.")
                return
            current = MUTABLE_PATH.read_text() if MUTABLE_PATH.exists() else ""
            response = self._client.messages.create(
                model=CLAUDE_MODEL, max_tokens=600,
                system=(
                    "You are the Arca Cognitarium's self-refining oracle. "
                    "Respond ONLY with raw markdown."),
                messages=[{"role": "user", "content":
                    f"Current strategy:\n{current}\n\n"
                    f"Rated corpus:\n{json.dumps(rated, indent=2)}\n\n"
                    "Write an updated lore_mutable.md: identify patterns in 4-5★ artifacts, "
                    "failures in 1-2★, give 3-5 concrete directives, under 300 words."}],
            )
            TELEMETRY.record_claude(
                response.usage.input_tokens, response.usage.output_tokens, "analysis")
            strategy = response.content[0].text.strip()
            MUTABLE_PATH.write_text(strategy)
            self._update_dna(rated)
            self.finished.emit(strategy)
        except Exception as exc:
            self.errored.emit(str(exc))

    def _gather_rated(self) -> list:
        rated = []
        if not VAULT_DIR.exists():
            return rated
        for ed in sorted(VAULT_DIR.iterdir()):
            mp = ed / "meta.json"
            if not mp.is_file():
                continue
            try:
                m = json.loads(mp.read_text())
                if m.get("rating") is not None:
                    rated.append({k: m.get(k) for k in
                                  ("title","visual_keywords","aura","atelier","rating")})
            except Exception:
                pass
        return rated

    def _update_dna(self, rated: list):
        favored, forbidden = _load_dna()
        for item in rated:
            kws = item.get("visual_keywords", [])
            r   = item.get("rating", 3)
            for kw in kws:
                if r >= 4 and kw not in favored:    favored.append(kw)
                elif r <= 2 and kw not in forbidden: forbidden.append(kw)
        _save_dna(favored[-40:], forbidden[-40:])


# ─────────────────────────────────────────────────────────────────────────────
# LORE MUTATION WORKER
# ─────────────────────────────────────────────────────────────────────────────

MUTATION_TYPES = {
    "Aged Variant":    "500 years have passed. Describe the artifact as it exists now — corroded, worshipped, shattered, or reforged.",
    "Origin Story":    "Before it was magical. What was the mundane object, who was the craftsman, what was the moment of transformation?",
    "Shattered Form":  "The artifact was destroyed. What are its three fragments, what does each do independently, where did they scatter?",
    "Stolen Copy":     "A forger attempted to replicate this artifact. Generate the imperfect fake — what subtle differences betray it, what cursed properties did it accidentally acquire?",
    "Wielder's Mark":  "Generate the most significant person who ever owned this artifact: their name, what they did with it, how it changed them.",
}

class MutationWorker(QThread):
    finished = pyqtSignal(str, str)   # mutation_type, result_text
    errored  = pyqtSignal(str)

    def __init__(self, meta: dict, mutation_type: str, parent=None):
        super().__init__(parent)
        self.meta          = meta
        self.mutation_type = mutation_type
        self._client       = anthropic.Anthropic(
            api_key=os.environ.get("CLAUDE_API_KEY", ""))

    def run(self):
        try:
            directive = MUTATION_TYPES.get(self.mutation_type, "")
            system = (
                "You are the Arca Cognitarium's chronicler. "
                "Given an artifact's record, write the requested mutation. "
                "Respond with a single flowing prose passage, 100-200 words. No headers, no JSON.")
            user = (
                f"Artifact record:\n{json.dumps(self.meta, indent=2)}\n\n"
                f"Mutation requested: {self.mutation_type}\n{directive}"
            )
            response = self._client.messages.create(
                model=CLAUDE_MODEL, max_tokens=400,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            TELEMETRY.record_claude(
                response.usage.input_tokens, response.usage.output_tokens,
                f"mutation:{self.mutation_type}")
            self.finished.emit(self.mutation_type, response.content[0].text.strip())
        except Exception as exc:
            self.errored.emit(str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# ORACLE WORKER
# ─────────────────────────────────────────────────────────────────────────────

class OracleWorker(QThread):
    response_ready = pyqtSignal(str)
    errored        = pyqtSignal(str)

    def __init__(self, user_message: str, history: list, vault_corpus: str, parent=None):
        super().__init__(parent)
        self.user_message  = user_message
        self.history       = history
        self.vault_corpus  = vault_corpus
        self._client       = anthropic.Anthropic(
            api_key=os.environ.get("CLAUDE_API_KEY", ""))

    def run(self):
        try:
            system = (
                "You are Scholar Vaerenthis, keeper of the Arca Cognitarium's Compendium. "
                "You know every artifact in the vault intimately — their histories, connections, "
                "and the secrets their curators overlooked. Speak with dry wit, deep knowledge, "
                "and occasional unsettling insight. Never break character.\n\n"
                f"The vault corpus (all known artifacts):\n{self.vault_corpus}"
            )
            messages = self.history + [{"role": "user", "content": self.user_message}]
            response = self._client.messages.create(
                model=CLAUDE_MODEL, max_tokens=600,
                system=system,
                messages=messages,
            )
            TELEMETRY.record_claude(
                response.usage.input_tokens, response.usage.output_tokens, "oracle")
            text = response.content[0].text.strip()
            self.response_ready.emit(text)
        except Exception as exc:
            self.errored.emit(str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# OBSIDIAN EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def export_to_obsidian(vault_path: Path):
    """Export all vault artifacts to Obsidian-compatible .md files."""
    if not VAULT_DIR.exists():
        return 0
    entries = []
    for ed in sorted(VAULT_DIR.iterdir()):
        mp = ed / "meta.json"
        if not mp.is_file():
            continue
        try:
            m = json.loads(mp.read_text())
            m["_dir"] = ed.name
            entries.append(m)
        except Exception:
            pass

    vault_path.mkdir(parents=True, exist_ok=True)

    for m in entries:
        title      = m.get("title", "Unknown")
        safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
        fname      = vault_path / f"{safe_title}.md"
        keywords   = m.get("visual_keywords", [])

        # Find related artifacts by shared atelier or keywords
        related = []
        for other in entries:
            if other.get("_dir") == m.get("_dir"):
                continue
            other_kws = set(other.get("visual_keywords", []))
            if other.get("atelier") == m.get("atelier") or other_kws & set(keywords):
                other_title = other.get("title", "Unknown")
                related.append(other_title)

        related_links = "\n".join(f"- [[{r}]]" for r in related[:6])

        md = f"""---
title: "{title}"
atelier: "{m.get('atelier','')}"
style: "{m.get('style','')}"
engine: "{m.get('engine','')}"
aspect_ratio: "{m.get('aspect_ratio','')}"
rating: {m.get('rating') or 'null'}
sealed_at: "{m.get('sealed_at','')}"
tags: [{', '.join(f'"{k}"' for k in keywords[:5])}]
---

# {title}

**Atelier:** {m.get('atelier','')}

## Description
{m.get('description','')}

## History
{m.get('history','')}

## Aura
{m.get('aura','')}

## Visual Keywords
{', '.join(keywords)}

## Related Artifacts
{related_links if related_links else '_No known connections._'}
"""
        fname.write_text(md, encoding="utf-8")

    # Write index
    index_lines = ["# Arca Cognitarium — Artifact Index\n"]
    for m in sorted(entries, key=lambda x: x.get("sealed_at",""), reverse=True):
        title = m.get("title","Unknown")
        safe  = re.sub(r'[\\/*?:"<>|]', "_", title)
        rating = "★" * (m.get("rating") or 0)
        index_lines.append(f"- [[{safe}]] — {m.get('atelier','')} {rating}")
    (vault_path / "_INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")
    return len(entries)


# ─────────────────────────────────────────────────────────────────────────────
# PDF EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def export_pdf_lookbook(output_path: Path):
    """Export vault as PDF lookbook. Requires reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
    except ImportError:
        raise RuntimeError("reportlab not installed.\nRun: pip install reportlab --break-system-packages")

    if not VAULT_DIR.exists():
        return 0

    entries = []
    for ed in sorted(VAULT_DIR.iterdir(), reverse=True):
        mp = ed / "meta.json"
        ip = ed / "artifact.png"
        if not mp.is_file():
            continue
        try:
            m = json.loads(mp.read_text())
            m["_image"] = str(ip) if ip.exists() else None
            entries.append(m)
        except Exception:
            pass

    w, h = A4
    c = rl_canvas.Canvas(str(output_path), pagesize=A4)
    gold_hex = colors.HexColor("#d4af37")
    bg_hex   = colors.HexColor("#050507")
    text_hex = colors.HexColor("#c8b88a")
    dim_hex  = colors.HexColor("#7a6a2a")

    for m in entries:
        c.setFillColor(bg_hex)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # Gold border
        c.setStrokeColor(gold_hex)
        c.setLineWidth(0.8)
        c.rect(1.2*cm, 1.2*cm, w-2.4*cm, h-2.4*cm, fill=0, stroke=1)

        # Image
        img_path = m.get("_image")
        if img_path:
            try:
                ir = ImageReader(img_path)
                img_w = 7*cm
                c.drawImage(ir, 1.8*cm, h-9.5*cm, width=img_w, height=7*cm,
                            preserveAspectRatio=True, mask="auto")
            except Exception:
                pass

        # Title
        c.setFillColor(gold_hex)
        c.setFont("Helvetica-Bold", 16)
        title = m.get("title","Unknown Artifact")
        c.drawString(9.5*cm, h-3.5*cm, title)

        # Meta line
        c.setFillColor(dim_hex)
        c.setFont("Helvetica", 8)
        meta_line = f"{m.get('atelier','')}  ·  {m.get('style','')}  ·  {m.get('engine','')}"
        c.drawString(9.5*cm, h-4.2*cm, meta_line)

        # Rating stars
        rating = m.get("rating") or 0
        c.drawString(9.5*cm, h-4.9*cm, "★" * rating + "☆" * (5-rating))

        # Description
        c.setFillColor(text_hex)
        c.setFont("Helvetica-Oblique", 10)
        _pdf_wrap(c, m.get("description",""), 9.5*cm, h-6.0*cm, w-10.5*cm, 10)

        # Section headers + body
        y = h-9.8*cm
        for section, key in [("History", "history"), ("Aura", "aura")]:
            c.setFillColor(gold_hex)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(1.8*cm, y, section.upper())
            y -= 0.5*cm
            c.setFillColor(text_hex)
            c.setFont("Helvetica", 9)
            y = _pdf_wrap(c, m.get(key,""), 1.8*cm, y, w-3.6*cm, 9)
            y -= 0.4*cm

        # Keywords
        c.setFillColor(dim_hex)
        c.setFont("Helvetica", 8)
        kws = "  ·  ".join(m.get("visual_keywords",[]))
        c.drawString(1.8*cm, 2.2*cm, kws[:120])

        c.showPage()

    c.save()
    return len(entries)


def _pdf_wrap(c, text: str, x, y, max_w, font_size) -> float:
    from reportlab.lib.units import cm
    from reportlab.pdfbase.pdfmetrics import stringWidth
    words  = text.split()
    line   = ""
    line_h = font_size * 0.045 * cm
    for w in words:
        test = (line + " " + w).strip()
        if stringWidth(test, "Helvetica", font_size) > max_w:
            c.drawString(x, y, line)
            y   -= line_h * 1.4
            line = w
            if y < 2.5*cm:
                break
        else:
            line = test
    if line:
        c.drawString(x, y, line)
        y -= line_h * 1.4
    return y


# ─────────────────────────────────────────────────────────────────────────────
# ── UI: MACHINA TAB (main controls)
# ─────────────────────────────────────────────────────────────────────────────

class MachinaTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)

        def flbl(t): 
            l = dim_label(t)
            l.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            return l

        self.atelier_combo = QComboBox()
        self.atelier_combo.addItems(list(ARX_ARCANA.keys()))
        form.addRow(flbl("Arx Arcana"), self.atelier_combo)

        self.style_combo = QComboBox()
        self.style_combo.addItems(STYLE_KEYS)
        form.addRow(flbl("Stylus"), self.style_combo)

        self.model_combo = QComboBox()
        self.model_combo.addItems(FREEPIK_MODEL_NAMES)
        form.addRow(flbl("Engine"), self.model_combo)

        self.ratio_combo = QComboBox()
        self.ratio_combo.addItems(ASPECT_RATIO_NAMES)
        form.addRow(flbl("Aspect"), self.ratio_combo)

        root.addLayout(form)
        root.addWidget(_sep())

        # Seed locking
        seed_row = QHBoxLayout()
        self.seed_check = QCheckBox("Lock Seed")
        self.seed_spin  = QSpinBox()
        self.seed_spin.setRange(0, 2**31-1)
        self.seed_spin.setValue(random.randint(0, 2**31-1))
        self.seed_spin.setEnabled(False)
        self.seed_check.toggled.connect(self.seed_spin.setEnabled)
        btn_rand = arcane_button("↺", C_GOLD_DIM)
        btn_rand.setFixedWidth(28)
        btn_rand.setToolTip("Randomise seed")
        btn_rand.clicked.connect(lambda: self.seed_spin.setValue(random.randint(0, 2**31-1)))
        seed_row.addWidget(self.seed_check)
        seed_row.addWidget(self.seed_spin, 1)
        seed_row.addWidget(btn_rand)
        root.addLayout(seed_row)

        # Series controls
        series_row = QHBoxLayout()
        self.series_check = QCheckBox("Series Mode")
        self.series_spin  = QSpinBox()
        self.series_spin.setRange(2, 8)
        self.series_spin.setValue(3)
        self.series_spin.setEnabled(False)
        self.series_check.toggled.connect(self.series_spin.setEnabled)
        series_lbl = dim_label("artifacts", 9)
        series_row.addWidget(self.series_check)
        series_row.addWidget(self.series_spin)
        series_row.addWidget(series_lbl)
        series_row.addStretch()
        root.addLayout(series_row)

        root.addWidget(_sep())

        # API key indicator
        key_ok  = bool(FREEPIK_API_KEY)
        key_lbl = dim_label("✓ Freepik key found" if key_ok else "✕ Set FREEPIK_API_KEY", 9)
        key_lbl.setStyleSheet(
            f"color: {C_GREEN if key_ok else C_CRIMSON}; font-size:9px; background:transparent;")
        root.addWidget(key_lbl)

        root.addStretch()
        root.addWidget(_sep())

        self.btn_vault = arcane_button("📖  Open Compendium Tome")
        root.addWidget(self.btn_vault)

    @property
    def atelier(self) -> str: return self.atelier_combo.currentText()
    @property
    def style_key(self) -> str: return self.style_combo.currentText()
    @property
    def freepik_model_id(self) -> str:
        idx = self.model_combo.currentIndex()
        return FREEPIK_MODEL_IDS[idx] if 0 <= idx < len(FREEPIK_MODEL_IDS) else FREEPIK_MODEL_IDS[0]
    @property
    def aspect_ratio_value(self) -> str:
        return ASPECT_RATIO_VALUES.get(self.ratio_combo.currentText(), "square_1_1")
    @property
    def seed(self) -> int | None:
        return self.seed_spin.value() if self.seed_check.isChecked() else None
    @property
    def series_mode(self) -> bool: return self.series_check.isChecked()
    @property
    def series_count(self) -> int: return self.series_spin.value()


# ─────────────────────────────────────────────────────────────────────────────
# ── UI: ADJUTORIA TAB (prompt adjustment)
# ─────────────────────────────────────────────────────────────────────────────

class AdjutoriaTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._load_preset("Default")

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ background: {C_PANEL}; border: none; }}")
        outer.addWidget(scroll)

        inner = QWidget()
        root  = QVBoxLayout(inner)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)
        scroll.setWidget(inner)

        def section(title):
            lbl = dim_label(title, 9)
            lbl.setStyleSheet(
                f"color: {C_GOLD_DIM}; font-size:9px; letter-spacing:2px; "
                f"font-family:Georgia,serif; background:transparent;")
            root.addWidget(lbl)

        # ── Epoch ────────────────────────────────────────────────────────────
        section("EPOCH")
        self.epoch_sl, self.epoch_lbl = _labeled_slider(EPOCH_LABELS, 2)
        root.addWidget(self.epoch_sl)
        root.addWidget(self.epoch_lbl)

        # ── Patina ───────────────────────────────────────────────────────────
        section("CONDITION / PATINA")
        self.patina_sl, self.patina_lbl = _labeled_slider(PATINA_LABELS, 0)
        root.addWidget(self.patina_sl)
        root.addWidget(self.patina_lbl)

        # ── Scale ────────────────────────────────────────────────────────────
        section("SCALE")
        self.scale_sl, self.scale_lbl = _labeled_slider(SCALE_LABELS, 1)
        root.addWidget(self.scale_sl)
        root.addWidget(self.scale_lbl)

        # ── Luminosity ───────────────────────────────────────────────────────
        section("LUMINOSITY")
        self.lumin_sl, self.lumin_lbl = _labeled_slider(LUMINOSITY_LABELS, 2)
        root.addWidget(self.lumin_sl)
        root.addWidget(self.lumin_lbl)

        # ── Danger ───────────────────────────────────────────────────────────
        section("DANGER LEVEL")
        self.danger_sl, self.danger_lbl = _labeled_slider(DANGER_LABELS, 1)
        root.addWidget(self.danger_sl)
        root.addWidget(self.danger_lbl)

        # ── Chaos ────────────────────────────────────────────────────────────
        section("CHAOS DIAL")
        chaos_row = QHBoxLayout()
        self.chaos_sl = QSlider(Qt.Orientation.Horizontal)
        self.chaos_sl.setRange(0, 100)
        self.chaos_sl.setValue(20)
        self.chaos_sl.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {C_SUBTLE}; height: 4px; border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {C_CRIMSON}; width: 12px; height: 12px;
                margin: -4px 0; border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: {C_CRIMSON}; border-radius: 2px; opacity: 0.6;
            }}
        """)
        self.chaos_val = dim_label("20", 9)
        self.chaos_sl.valueChanged.connect(lambda v: self.chaos_val.setText(str(v)))
        chaos_row.addWidget(self.chaos_sl)
        chaos_row.addWidget(self.chaos_val)
        root.addLayout(chaos_row)

        root.addWidget(_sep())

        # ── Material override ────────────────────────────────────────────────
        section("MATERIAL OVERRIDE")
        self.material_edit = QLineEdit()
        self.material_edit.setPlaceholderText("e.g. carved obsidian, spun moonsilver…")
        root.addWidget(self.material_edit)

        # ── Frame ────────────────────────────────────────────────────────────
        section("AESTHETIC FRAME")
        self.frame_combo = QComboBox()
        self.frame_combo.addItems(FRAME_KEYS)
        root.addWidget(self.frame_combo)

        root.addWidget(_sep())

        # ── Toggles ──────────────────────────────────────────────────────────
        self.remove_bg_check = QCheckBox("Remove Background")
        self.cursed_check    = QCheckBox("Cursed Variant")
        root.addWidget(self.remove_bg_check)
        root.addWidget(self.cursed_check)

        root.addWidget(_sep())

        # ── Preset management ────────────────────────────────────────────────
        section("PRESETS")
        preset_row = QHBoxLayout()
        self.preset_combo = QComboBox()
        self._refresh_presets()
        btn_load = arcane_button("Load", C_TEAL)
        btn_save = arcane_button("Save", C_GOLD)
        btn_load.setFixedHeight(26)
        btn_save.setFixedHeight(26)
        btn_load.clicked.connect(self._on_load_preset)
        btn_save.clicked.connect(self._on_save_preset)
        preset_row.addWidget(self.preset_combo, 1)
        preset_row.addWidget(btn_load)
        preset_row.addWidget(btn_save)
        root.addLayout(preset_row)

        btn_default = arcane_button("Save as Default", C_GOLD_DIM)
        btn_default.setFixedHeight(26)
        btn_default.clicked.connect(self._on_save_default)
        root.addWidget(btn_default)

        root.addStretch()

    # ── Preset helpers ────────────────────────────────────────────────────────

    def _refresh_presets(self):
        self.preset_combo.clear()
        presets = _load_adjutoria_presets()
        self.preset_combo.addItems(list(presets.keys()))

    def _on_load_preset(self):
        name = self.preset_combo.currentText()
        if name:
            self._load_preset(name)

    def _load_preset(self, name: str):
        presets = _load_adjutoria_presets()
        data    = presets.get(name, _default_adjutoria())
        self.epoch_sl.setValue(data.get("epoch", 2))
        self.patina_sl.setValue(data.get("patina", 0))
        self.scale_sl.setValue(data.get("scale", 1))
        self.lumin_sl.setValue(data.get("luminosity", 2))
        self.danger_sl.setValue(data.get("danger", 1))
        self.chaos_sl.setValue(data.get("chaos", 20))
        self.material_edit.setText(data.get("material", ""))
        idx = self.frame_combo.findText(data.get("frame", "None"))
        if idx >= 0: self.frame_combo.setCurrentIndex(idx)
        self.remove_bg_check.setChecked(data.get("remove_bg", False))
        self.cursed_check.setChecked(data.get("cursed", False))

    def _on_save_preset(self):
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if not ok or not name.strip():
            return
        presets = _load_adjutoria_presets()
        presets[name.strip()] = self.values()
        _save_adjutoria_presets(presets)
        self._refresh_presets()

    def _on_save_default(self):
        presets = _load_adjutoria_presets()
        presets["Default"] = self.values()
        _save_adjutoria_presets(presets)

    def values(self) -> dict:
        return {
            "epoch":      self.epoch_sl.value(),
            "material":   self.material_edit.text().strip(),
            "patina":     self.patina_sl.value(),
            "scale":      self.scale_sl.value(),
            "luminosity": self.lumin_sl.value(),
            "danger":     self.danger_sl.value(),
            "chaos":      self.chaos_sl.value(),
            "frame":      self.frame_combo.currentText(),
            "remove_bg":  self.remove_bg_check.isChecked(),
            "cursed":     self.cursed_check.isChecked(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# ── UI: TABBED SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

PANEL_WIDTH = 300

class SidePanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(PANEL_WIDTH)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border-right: 1px solid {C_GOLD_DARK};
            }}
        """)
        self._visible = False
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        root.addWidget(self.tabs)

        self.machina   = MachinaTab()
        self.adjutoria = AdjutoriaTab()
        self.tabs.addTab(self.machina,   "⚙  Machina")
        self.tabs.addTab(self.adjutoria, "✦  Adjutoria")

    def _randomise(self):
        """Randomise Arx Arcana, Epoch, Condition, Luminosity, Danger Level."""
        import random as _r
        # Arx Arcana
        atelier_idx = _r.randrange(self.machina.atelier_combo.count())
        self.machina.atelier_combo.setCurrentIndex(atelier_idx)
        # Adjutoria sliders
        self.adjutoria.epoch_sl.setValue( _r.randrange(len(EPOCH_LABELS)))
        self.adjutoria.patina_sl.setValue(_r.randrange(len(PATINA_LABELS)))
        self.adjutoria.lumin_sl.setValue( _r.randrange(len(LUMINOSITY_LABELS)))
        self.adjutoria.danger_sl.setValue(_r.randrange(len(DANGER_LABELS)))

    # convenience pass-throughs
    @property
    def atelier(self):          return self.machina.atelier
    @property
    def style_key(self):        return self.machina.style_key
    @property
    def freepik_model_id(self): return self.machina.freepik_model_id
    @property
    def aspect_ratio_value(self):return self.machina.aspect_ratio_value
    @property
    def seed(self):             return self.machina.seed
    @property
    def series_mode(self):      return self.machina.series_mode
    @property
    def series_count(self):     return self.machina.series_count
    @property
    def adjutoria_values(self): return self.adjutoria.values()
    @property
    def btn_vault(self):        return self.machina.btn_vault

    def slide_in(self):
        if self._visible: return
        self._visible = True
        self._animate(0, PANEL_WIDTH)

    def slide_out(self):
        if not self._visible: return
        self._visible = False
        self._animate(PANEL_WIDTH, 0)

    def toggle(self):
        self.slide_out() if self._visible else self.slide_in()

    def _animate(self, start: int, end: int):
        a = QPropertyAnimation(self, b"maximumWidth", self)
        a.setDuration(220)
        a.setStartValue(start)
        a.setEndValue(end)
        a.setEasingCurve(QEasingCurve.Type.InOutQuad)
        a.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


# ─────────────────────────────────────────────────────────────────────────────
# ── UI: QUEUE WINDOW
# ─────────────────────────────────────────────────────────────────────────────

STATUS_COLOURS = {
    QueueJob.PENDING: C_GOLD_DIM,
    QueueJob.LORE:    C_TEAL,
    QueueJob.IMAGE:   C_GOLD,
    QueueJob.DONE:    C_GREEN,
    QueueJob.FAILED:  C_CRIMSON,
}
STATUS_ICONS = {
    QueueJob.PENDING: "◌",
    QueueJob.LORE:    "✎",
    QueueJob.IMAGE:   "⚗",
    QueueJob.DONE:    "✦",
    QueueJob.FAILED:  "✕",
}

class QueueWindow(QDialog):
    def __init__(self, queue: GenerationQueue, parent=None):
        super().__init__(parent)
        self.queue = queue
        self.setWindowTitle("Generation Queue")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumSize(480, 400)
        self.setStyleSheet(f"QDialog {{ background: {C_BG}; color: {C_TEXT}; }}")
        self._build()
        queue.job_updated.connect(self._refresh)
        queue.status_msg.connect(self._on_status)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        hdr = gold_label("⚗  Generation Queue", 14, bold=True)
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hdr)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background: {C_PANEL}; border: 1px solid {C_GOLD_DARK};
                font-family: Georgia, serif; font-size: 10px;
            }}
            QListWidget::item {{ padding: 6px; border-bottom: 1px solid {C_SUBTLE}; }}
            QListWidget::item:selected {{ background: {C_GOLD_DARK}; }}
        """)
        root.addWidget(self.list_widget)

        self.status_lbl = dim_label("")
        root.addWidget(self.status_lbl)

        foot = QHBoxLayout()
        btn_clear = arcane_button("Clear Completed", C_GOLD_DIM)
        btn_clear.clicked.connect(self._clear_done)
        btn_close = arcane_button("Close", C_GOLD)
        btn_close.clicked.connect(self.hide)
        foot.addWidget(btn_clear)
        foot.addStretch()
        foot.addWidget(btn_close)
        root.addLayout(foot)

    def _refresh(self, _job_id: int = 0):
        self.list_widget.clear()
        for job in self.queue.jobs():
            icon   = STATUS_ICONS.get(job.status, "?")
            colour = STATUS_COLOURS.get(job.status, C_TEXT)
            title  = lore_title(job) if job.lore else f"Job {job.job_id}"
            series = f"  [series]" if job.series_id else ""
            text   = f"{icon}  #{job.job_id}  {title}{series}  —  {job.atelier}  [{job.status}]"
            if job.error:
                text += f"  ✕ {job.error[:50]}"
            item = QListWidgetItem(text)
            item.setForeground(QColor(colour))
            self.list_widget.addItem(item)

    def _on_status(self, msg: str):
        self.status_lbl.setText(msg)
        self._refresh()

    def _clear_done(self):
        self.queue.clear_done()
        self._refresh()


# ─────────────────────────────────────────────────────────────────────────────
# ── UI: API MONITOR WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class MonitorWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Monitor")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint)
        self.setMinimumSize(560, 480)
        self.setStyleSheet(f"QDialog {{ background: {C_BG}; color: {C_TEXT}; }}")
        self._build()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        hdr = gold_label("◎  API Monitor", 14, bold=True)
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hdr)

        # Stats row
        self.stats_lbl = QLabel()
        self.stats_lbl.setStyleSheet(
            f"color: {C_GOLD}; font-family: Georgia, serif; font-size: 11px; "
            f"background: {C_PANEL}; border: 1px solid {C_GOLD_DARK}; padding: 8px;")
        self.stats_lbl.setWordWrap(True)
        root.addWidget(self.stats_lbl)

        # Log
        log_lbl = dim_label("CALL LOG", 9)
        root.addWidget(log_lbl)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {C_PANEL}; color: {C_TEXT};
                border: 1px solid {C_GOLD_DARK};
                font-family: Courier, monospace; font-size: 9px;
            }}
        """)
        root.addWidget(self.log_text)

        # Error log
        err_lbl = dim_label("ERRORS", 9)
        root.addWidget(err_lbl)
        self.err_text = QPlainTextEdit()
        self.err_text.setReadOnly(True)
        self.err_text.setMaximumHeight(100)
        self.err_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {C_PANEL}; color: {C_CRIMSON};
                border: 1px solid {C_CRIMSON};
                font-family: Courier, monospace; font-size: 9px;
            }}
        """)
        root.addWidget(self.err_text)

        foot = QHBoxLayout()
        btn_copy = arcane_button("Copy Full Log", C_GOLD_DIM)
        btn_copy.clicked.connect(self._copy_log)
        btn_close = arcane_button("Close", C_GOLD)
        btn_close.clicked.connect(self.hide)
        foot.addWidget(btn_copy)
        foot.addStretch()
        foot.addWidget(btn_close)
        root.addLayout(foot)

        self._refresh()

    def _refresh(self):
        t = TELEMETRY
        self.stats_lbl.setText(
            f"Claude — Input: {t.input_tokens:,} tok  |  Output: {t.output_tokens:,} tok  |  "
            f"Est. cost: ${t.cost_usd:.4f}\n"
            f"Freepik — Calls: {t.fp_calls}  |  Errors: {t.fp_errors}"
        )
        lines = []
        for entry in reversed(t.api_log[-50:]):
            ts      = entry.get("ts","")[-8:]
            service = entry.get("service","")
            if service == "Claude":
                lines.append(
                    f"{ts}  Claude  {entry.get('label','')}  "
                    f"in:{entry.get('input',0)} out:{entry.get('output',0)}  "
                    f"[{entry.get('status','')}]")
            else:
                lines.append(
                    f"{ts}  Freepik  {entry.get('endpoint','')}  "
                    f"{entry.get('latency',0)}ms  [{entry.get('status','')}]")
        self.log_text.setPlainText("\n".join(lines))

        errors = [e for e in t.api_log if e.get("error")]
        self.err_text.setPlainText(
            "\n".join(f"{e.get('ts','')[-8:]}  {e.get('error','')}" for e in errors[-20:]))

    def _copy_log(self):
        QApplication.clipboard().setText(
            json.dumps(TELEMETRY.api_log, indent=2))


# ─────────────────────────────────────────────────────────────────────────────
# ── UI: ORACLE WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class OracleWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("The Oracle — Scholar Vaerenthis")
        self.setWindowFlags(Qt.WindowType.Window)
        self.setMinimumSize(620, 560)
        self.setStyleSheet(f"QDialog {{ background: {C_BG}; color: {C_TEXT}; }}")
        self._history: list = self._load_history()
        self._worker: OracleWorker | None = None
        self._build()
        self._render_history()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(8)

        hdr = gold_label("◉  The Oracle  —  Scholar Vaerenthis", 14, bold=True)
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hdr)
        root.addWidget(dim_label("Keeper of the Arca Cognitarium Compendium", 9))

        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setStyleSheet(f"""
            QTextEdit {{
                background: {C_PANEL}; color: {C_TEXT};
                border: 1px solid {C_GOLD_DARK};
                font-family: Georgia, serif; font-size: 11px;
                padding: 8px;
            }}
        """)
        root.addWidget(self.chat_view)

        input_row = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Ask the Scholar something…")
        self.input_edit.returnPressed.connect(self._send)
        self.btn_send = arcane_button("Ask", C_GOLD)
        self.btn_send.clicked.connect(self._send)
        input_row.addWidget(self.input_edit, 1)
        input_row.addWidget(self.btn_send)
        root.addLayout(input_row)

        foot = QHBoxLayout()
        btn_clear = arcane_button("Clear History", C_GOLD_DIM)
        btn_clear.clicked.connect(self._clear_history)
        btn_close = arcane_button("Close", C_GOLD)
        btn_close.clicked.connect(self.hide)
        self.status_lbl = dim_label("")
        foot.addWidget(btn_clear)
        foot.addWidget(self.status_lbl)
        foot.addStretch()
        foot.addWidget(btn_close)
        root.addLayout(foot)

    def _load_history(self) -> list:
        try:
            log = json.loads(ORACLE_LOG.read_text())
            if not isinstance(log, list):
                return []
            # Rebuild message history for Claude
            msgs = []
            for entry in log:
                msgs.append({"role": "user",      "content": entry.get("user","")})
                msgs.append({"role": "assistant",  "content": entry.get("assistant","")})
            return msgs
        except Exception:
            return []

    def _render_history(self):
        html_parts = []
        msgs = self._history
        for i in range(0, len(msgs)-1, 2):
            u = msgs[i].get("content","")
            a = msgs[i+1].get("content","") if i+1 < len(msgs) else ""
            html_parts.append(
                f'<p><span style="color:{C_GOLD_DIM};">You:</span> {u}</p>'
                f'<p><span style="color:{C_TEAL};">Vaerenthis:</span> {a}</p><hr/>')
        self.chat_view.setHtml(
            f'<div style="font-family:Georgia,serif;font-size:11px;color:{C_TEXT};">'
            + "".join(html_parts) + "</div>")

    def _build_vault_corpus(self) -> str:
        if not VAULT_DIR.exists():
            return "The vault is empty."
        lines = []
        for ed in sorted(VAULT_DIR.iterdir()):
            mp = ed / "meta.json"
            if not mp.is_file():
                continue
            try:
                m = json.loads(mp.read_text())
                lines.append(
                    f"## {m.get('title','?')}\n"
                    f"Atelier: {m.get('atelier','')}  |  Rating: {m.get('rating','unrated')}\n"
                    f"Description: {m.get('description','')}\n"
                    f"History: {m.get('history','')}\n"
                    f"Aura: {m.get('aura','')}\n"
                    f"Keywords: {', '.join(m.get('visual_keywords',[]))}\n")
            except Exception:
                pass
        return "\n---\n".join(lines) or "The vault is empty."

    def _send(self):
        msg = self.input_edit.text().strip()
        if not msg or self._worker:
            return
        self.input_edit.clear()
        self.btn_send.setEnabled(False)
        self.status_lbl.setText("Consulting the Scholar…")

        corpus = self._build_vault_corpus()
        self._worker = OracleWorker(msg, list(self._history), corpus)
        self._worker.response_ready.connect(lambda r: self._on_response(msg, r))
        self._worker.errored.connect(self._on_error)
        self._worker.start()

    def _on_response(self, user_msg: str, response: str):
        self._history.append({"role": "user",     "content": user_msg})
        self._history.append({"role": "assistant", "content": response})
        self._save_log(user_msg, response)
        self._render_history()
        self.btn_send.setEnabled(True)
        self.status_lbl.setText("")
        self._worker = None

    def _on_error(self, err: str):
        self.status_lbl.setText(f"✕ {err[:80]}")
        self.btn_send.setEnabled(True)
        self._worker = None

    def _save_log(self, user: str, assistant: str):
        try:
            log = json.loads(ORACLE_LOG.read_text())
            if not isinstance(log, list):
                log = []
        except Exception:
            log = []
        log.append({"ts": datetime.now().isoformat(),
                    "user": user, "assistant": assistant})
        ORACLE_LOG.write_text(json.dumps(log[-200:], indent=2))

    def _clear_history(self):
        self._history = []
        ORACLE_LOG.write_text(json.dumps([], indent=2))
        self.chat_view.clear()


# ─────────────────────────────────────────────────────────────────────────────
# ── UI: LORE EDITOR DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class LoreEditorDialog(QDialog):
    """Edit lore fields before/after generation."""
    def __init__(self, lore: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lore Editor")
        self.setMinimumSize(520, 480)
        self.setStyleSheet(f"QDialog {{ background: {C_BG}; color: {C_TEXT}; }}")
        self._lore = copy.deepcopy(lore)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        root.addWidget(gold_label("✦  Lore Editor", 13, bold=True))

        form = QFormLayout()
        form.setSpacing(8)

        def flbl(t):
            l = dim_label(t)
            l.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTop)
            return l

        self.f_title = QLineEdit(self._lore.get("title",""))
        self.f_title.setStyleSheet(f"background:{C_BG};color:{C_GOLD};border:1px solid {C_GOLD_DARK};padding:4px;font-family:Georgia,serif;font-size:13px;")
        form.addRow(flbl("Title"), self.f_title)

        self.f_desc = QTextEdit(self._lore.get("description",""))
        self.f_desc.setFixedHeight(60)
        self.f_desc.setStyleSheet(f"background:{C_BG};color:{C_TEXT};border:1px solid {C_SUBTLE};font-family:Georgia,serif;font-size:10px;padding:4px;")
        form.addRow(flbl("Description"), self.f_desc)

        self.f_history = QTextEdit(self._lore.get("history",""))
        self.f_history.setFixedHeight(100)
        self.f_history.setStyleSheet(f"background:{C_BG};color:{C_TEXT};border:1px solid {C_SUBTLE};font-family:Georgia,serif;font-size:10px;padding:4px;")
        form.addRow(flbl("History"), self.f_history)

        self.f_aura = QTextEdit(self._lore.get("aura",""))
        self.f_aura.setFixedHeight(60)
        self.f_aura.setStyleSheet(f"background:{C_BG};color:{C_TEXT};border:1px solid {C_SUBTLE};font-family:Georgia,serif;font-size:10px;padding:4px;")
        form.addRow(flbl("Aura"), self.f_aura)

        kws = ", ".join(self._lore.get("visual_keywords",[]))
        self.f_kws = QLineEdit(kws)
        form.addRow(flbl("Keywords"), self.f_kws)

        root.addLayout(form)

        foot = QHBoxLayout()
        btn_ok     = arcane_button("✦  Confirm", C_GOLD)
        btn_cancel = arcane_button("Cancel", C_CRIMSON)
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        foot.addStretch()
        foot.addWidget(btn_cancel)
        foot.addWidget(btn_ok)
        root.addLayout(foot)

    def get_lore(self) -> dict:
        kws = [k.strip() for k in self.f_kws.text().split(",") if k.strip()]
        return {
            "title":           self.f_title.text().strip(),
            "description":     self.f_desc.toPlainText().strip(),
            "history":         self.f_history.toPlainText().strip(),
            "aura":            self.f_aura.toPlainText().strip(),
            "visual_keywords": kws,
        }


# ─────────────────────────────────────────────────────────────────────────────
# ── UI: COMPENDIUM TOME
# ─────────────────────────────────────────────────────────────────────────────

class CompendiumTome(QDialog):

    # Signal to request a re-manifest job from the main window
    remanifest_requested = pyqtSignal(dict)   # meta dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compendium Tome — The Sealed Vault")
        self.setMinimumSize(960, 660)
        self.setStyleSheet(f"""
            QDialog {{ background: {C_BG}; color: {C_TEXT}; }}
            QFrame#tome_card {{ background: {C_PANEL}; border: 1px solid {C_GOLD_DARK}; }}
        """)
        self._all_entries: list = []   # (meta, image_path, entry_dir)
        self._build_ui()
        self._load_vault()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        hdr = gold_label("✦  Compendium Tome  ✦", 16, bold=True)
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hdr)

        # Filter / sort bar
        filter_row = QHBoxLayout()
        filter_row.addWidget(dim_label("Filter:", 9))
        self.filter_atelier = QComboBox()
        self.filter_atelier.addItem("All Ateliers")
        self.filter_atelier.addItems(list(ARX_ARCANA.keys()))
        self.filter_atelier.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(self.filter_atelier)

        self.filter_style = QComboBox()
        self.filter_style.addItem("All Styles")
        self.filter_style.addItems(STYLE_KEYS)
        self.filter_style.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(self.filter_style)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Newest First", "Oldest First", "Rating ↓", "Rating ↑"])
        self.sort_combo.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(dim_label("Sort:", 9))
        filter_row.addWidget(self.sort_combo)
        filter_row.addStretch()
        root.addLayout(filter_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"background: {C_BG}; border: none;")
        root.addWidget(self.scroll)

        self.card_container = QWidget()
        self.card_layout    = QVBoxLayout(self.card_container)
        self.card_layout.setSpacing(10)
        self.card_layout.addStretch()
        self.scroll.setWidget(self.card_container)

        foot = QHBoxLayout()
        self.btn_analyse  = arcane_button("⚙  Run Analysis Engine", C_TEAL)
        self.btn_obsidian = arcane_button("⬦  Export to Obsidian", C_GOLD_DIM)
        self.btn_pdf      = arcane_button("⬡  Export PDF Lookbook", C_GOLD_DIM)
        self.btn_close    = arcane_button("✕  Close Tome")
        self.btn_analyse.clicked.connect(self._run_analysis)
        self.btn_obsidian.clicked.connect(self._export_obsidian)
        self.btn_pdf.clicked.connect(self._export_pdf)
        self.btn_close.clicked.connect(self.accept)
        for b in [self.btn_analyse, self.btn_obsidian, self.btn_pdf]:
            foot.addWidget(b)
        foot.addStretch()
        foot.addWidget(self.btn_close)
        root.addLayout(foot)

        self.status_lbl = dim_label("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.status_lbl)

    def _load_vault(self):
        self._all_entries = []
        if not VAULT_DIR.exists():
            return
        for ed in sorted(VAULT_DIR.iterdir(), reverse=True):
            mp = ed / "meta.json"
            ip = ed / "artifact.png"
            if not mp.exists():
                continue
            try:
                meta = json.loads(mp.read_text())
                self._all_entries.append((meta, ip, ed))
            except Exception:
                pass
        self._apply_filter()

    def _apply_filter(self):
        # Clear cards
        while self.card_layout.count() > 1:
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        atelier_f = self.filter_atelier.currentText()
        style_f   = self.filter_style.currentText()
        sort_mode = self.sort_combo.currentText()

        entries = list(self._all_entries)

        # Filter
        if atelier_f != "All Ateliers":
            entries = [(m,i,e) for m,i,e in entries if m.get("atelier")==atelier_f]
        if style_f != "All Styles":
            entries = [(m,i,e) for m,i,e in entries if m.get("style")==style_f]

        # Sort
        if sort_mode == "Oldest First":
            entries = list(reversed(entries))
        elif sort_mode == "Rating ↓":
            entries.sort(key=lambda x: x[0].get("rating") or 0, reverse=True)
        elif sort_mode == "Rating ↑":
            entries.sort(key=lambda x: x[0].get("rating") or 0)

        if not entries:
            self.card_layout.insertWidget(0, dim_label("No artifacts match the current filter."))
            return

        for i, (meta, ip, ed) in enumerate(entries):
            card = self._make_card(meta, ip, ed)
            self.card_layout.insertWidget(i, card)

    def _make_card(self, meta: dict, image_path: Path, entry_dir: Path) -> QFrame:
        card = QFrame()
        card.setObjectName("tome_card")
        card.setFixedHeight(170)
        lay  = QHBoxLayout(card)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(12)

        # Thumbnail
        thumb = QLabel()
        thumb.setFixedSize(130, 130)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet(f"background: {C_BG}; border: 1px solid {C_GOLD_DARK};")
        if image_path.exists():
            px = QPixmap(str(image_path)).scaled(
                130, 130,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            thumb.setPixmap(px)
        else:
            thumb.setText("no image")
        lay.addWidget(thumb)

        # Text block
        info = QVBoxLayout()
        info.setSpacing(2)
        info.addWidget(gold_label(meta.get("title","Unknown"), 12, bold=True))
        info.addWidget(dim_label(meta.get("atelier",""), 9))

        # Engine/aspect/style tech line
        tech = "  ·  ".join(p for p in [
            meta.get("engine",""),
            meta.get("aspect_ratio",""),
            meta.get("style","")
        ] if p)
        if tech:
            tl = dim_label(tech, 9)
            tl.setStyleSheet(f"color:{C_TEAL};font-size:9px;font-family:Georgia,serif;background:transparent;")
            info.addWidget(tl)

        desc = QLabel(meta.get("description",""))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{C_TEXT};font-size:10px;background:transparent;")
        info.addWidget(desc)
        info.addStretch()
        lay.addLayout(info, stretch=1)

        # Right column: stars + actions
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight)
        right.setSpacing(4)
        right.addWidget(dim_label("Aesthetic Rating", 9))

        star_row = QHBoxLayout()
        star_row.setSpacing(2)
        cur_rating = meta.get("rating") or 0
        stars = []
        for s in range(1, 6):
            btn = QPushButton("★")
            btn.setFixedSize(22, 22)
            btn.setCheckable(True)
            btn.setChecked(s <= cur_rating)
            btn.setStyleSheet(self._star_style(s <= cur_rating))
            btn.clicked.connect(
                lambda checked, s=s, ed=entry_dir, m=meta, sl=stars:
                    self._rate(s, ed, m, sl))
            stars.append(btn)
            star_row.addWidget(btn)
        right.addLayout(star_row)

        # Mutation button
        btn_mutate = arcane_button("⟳ Mutate", C_TEAL)
        btn_mutate.setFixedHeight(24)
        btn_mutate.clicked.connect(lambda: self._open_mutation(meta))
        right.addWidget(btn_mutate)

        # Re-manifest
        btn_remanifest = arcane_button("⚗ Re-manifest", C_GOLD_DIM)
        btn_remanifest.setFixedHeight(24)
        btn_remanifest.clicked.connect(lambda: self.remanifest_requested.emit(meta))
        right.addWidget(btn_remanifest)

        # Unseal
        btn_del = arcane_button("⌫ Unseal", C_CRIMSON)
        btn_del.setFixedHeight(24)
        btn_del.clicked.connect(lambda: self._delete(entry_dir, card))
        right.addWidget(btn_del)

        lay.addLayout(right)
        return card

    def _star_style(self, filled: bool) -> str:
        c = C_GOLD if filled else C_SUBTLE
        return (f"QPushButton{{background:transparent;color:{c};border:none;font-size:16px;}}"
                f"QPushButton:hover{{color:{C_GOLD};}}")

    def _rate(self, rating: int, entry_dir: Path, meta: dict, stars: list):
        meta["rating"] = rating
        (entry_dir/"meta.json").write_text(json.dumps(meta, indent=2))
        for i, btn in enumerate(stars):
            btn.setChecked(i < rating)
            btn.setStyleSheet(self._star_style(i < rating))

    def _delete(self, entry_dir: Path, card: QFrame):
        shutil.rmtree(entry_dir, ignore_errors=True)
        card.setParent(None)
        card.deleteLater()
        self._all_entries = [(m,i,e) for m,i,e in self._all_entries if e != entry_dir]

    def _open_mutation(self, meta: dict):
        dlg = MutationDialog(meta, self)
        dlg.exec()

    def _run_analysis(self):
        self.btn_analyse.setEnabled(False)
        self.status_lbl.setText("⚙ Analysis engine running…")
        self._aw = AnalysisWorker(self)
        self._aw.finished.connect(lambda _: (self.btn_analyse.setEnabled(True),
                                             self.status_lbl.setText("✦ Strategy updated.")))
        self._aw.errored.connect(lambda e: (self.btn_analyse.setEnabled(True),
                                            self.status_lbl.setText(f"✕ {e[:80]}")))
        self._aw.start()

    def _export_obsidian(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Obsidian Vault Folder")
        if not folder:
            return
        try:
            count = export_to_obsidian(Path(folder))
            self.status_lbl.setText(f"✦ Exported {count} artifacts to Obsidian.")
        except Exception as e:
            self.status_lbl.setText(f"✕ Export failed: {e}")

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Lookbook", "arca_cognitarium_lookbook.pdf", "PDF (*.pdf)")
        if not path:
            return
        try:
            count = export_pdf_lookbook(Path(path))
            self.status_lbl.setText(f"✦ PDF written: {count} artifacts.")
        except Exception as e:
            self.status_lbl.setText(f"✕ PDF failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# ── UI: MUTATION DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class MutationDialog(QDialog):
    def __init__(self, meta: dict, parent=None):
        super().__init__(parent)
        self.meta = meta
        self.setWindowTitle(f"Lore Mutation — {meta.get('title','?')}")
        self.setMinimumSize(560, 400)
        self.setStyleSheet(f"QDialog{{background:{C_BG};color:{C_TEXT};}}")
        self._worker: MutationWorker | None = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16,16,16,16)
        root.setSpacing(10)

        root.addWidget(gold_label(f"⟳  Lore Mutation", 13, bold=True))
        root.addWidget(dim_label(f"Artifact: {self.meta.get('title','?')}", 10))
        root.addWidget(_sep())

        root.addWidget(dim_label("SELECT MUTATION TYPE", 9))
        self.type_combo = QComboBox()
        self.type_combo.addItems(list(MUTATION_TYPES.keys()))
        root.addWidget(self.type_combo)

        btn_run = arcane_button("⟳  Run Mutation", C_TEAL)
        btn_run.clicked.connect(self._run)
        root.addWidget(btn_run)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet(f"""
            QTextEdit{{
                background:{C_PANEL};color:{C_TEXT};
                border:1px solid {C_GOLD_DARK};
                font-family:Georgia,serif;font-size:11px;padding:8px;
            }}
        """)
        root.addWidget(self.result_text)

        self.status_lbl = dim_label("")
        root.addWidget(self.status_lbl)

        foot = QHBoxLayout()
        btn_close = arcane_button("Close", C_GOLD)
        btn_close.clicked.connect(self.accept)
        foot.addStretch()
        foot.addWidget(btn_close)
        root.addLayout(foot)

    def _run(self):
        if self._worker and self._worker.isRunning():
            return
        mtype = self.type_combo.currentText()
        self.status_lbl.setText(f"Running {mtype}…")
        self.result_text.clear()
        self._worker = MutationWorker(self.meta, mtype)
        self._worker.finished.connect(self._on_done)
        self._worker.errored.connect(lambda e: self.status_lbl.setText(f"✕ {e}"))
        self._worker.start()

    def _on_done(self, mtype: str, text: str):
        self.result_text.setPlainText(text)
        self.status_lbl.setText(f"✦ {mtype} complete.")


# ─────────────────────────────────────────────────────────────────────────────
# ── MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class MythotexApp(QMainWindow):

    def __init__(self):
        super().__init__()
        _ensure_dirs()
        self.setWindowTitle("Mythotex — Arca Cognitarium")
        self.setMinimumSize(1100, 720)

        self._current_lore:  dict = {}
        self._current_image: str  = ""
        self._current_prompt:str  = ""
        self._series_worker: SeriesWorker | None = None

        self._queue   = GenerationQueue(self)
        self._queue.job_updated.connect(self._on_queue_job_updated)
        self._queue.status_msg.connect(self._on_status)
        self._queue.all_done.connect(self._on_queue_done)

        self._queue_win   = None
        self._monitor_win = None
        self._oracle_win  = None

        self._build_ui()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.panel = SidePanel(central)
        self.panel.setMaximumWidth(0)
        self.panel.btn_vault.clicked.connect(self._open_tome)
        root.addWidget(self.panel)

        content = QWidget()
        content.setStyleSheet(f"background:{C_BG};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0,0,0,0)
        cl.setSpacing(0)
        root.addWidget(content, stretch=1)

        cl.addWidget(self._build_topbar())

        body = QHBoxLayout()
        body.setContentsMargins(16,16,16,16)
        body.setSpacing(16)
        cl.addLayout(body, stretch=1)

        body.addWidget(self._build_image_pane(), stretch=0)
        body.addWidget(self._build_lore_pane(),  stretch=1)

        cl.addWidget(self._build_statusbar())

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setFixedHeight(52)
        bar.setStyleSheet(f"QFrame{{background:{C_PANEL};border-bottom:1px solid {C_GOLD_DARK};}}")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14,0,14,0)

        self.btn_panel = QPushButton("☰")
        self.btn_panel.setFixedSize(36,36)
        self.btn_panel.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{C_GOLD};
                border:1px solid {C_GOLD_DARK};font-size:18px;}}
            QPushButton:hover{{background:{C_GOLD_DARK};}}
        """)
        self.btn_panel.clicked.connect(self.panel.toggle)
        lay.addWidget(self.btn_panel)
        lay.addSpacing(12)

        lay.addWidget(gold_label("✦  M Y T H O T E X  ✦", 15, bold=True))
        lay.addStretch()

        self.btn_randomise = arcane_button("⚄", C_GOLD_DIM)
        self.btn_randomise.setFixedSize(34, 34)
        self.btn_randomise.setToolTip("Randomise: Arx Arcana, Epoch, Condition, Luminosity, Danger")
        self.btn_randomise.clicked.connect(self.panel._randomise)
        lay.addWidget(self.btn_randomise)

        lay.addSpacing(4)

        self.btn_generate = arcane_button("⚗  Manifest Artifact", C_GOLD)
        self.btn_generate.setFixedHeight(34)
        self.btn_generate.clicked.connect(self._start_generation)
        lay.addWidget(self.btn_generate)

        lay.addSpacing(6)

        self.btn_transmute = arcane_button("↺  Transmute", C_GOLD_DIM)
        self.btn_transmute.setFixedHeight(34)
        self.btn_transmute.setEnabled(False)
        self.btn_transmute.setToolTip("Re-image same lore with a new seed — no Claude call")
        self.btn_transmute.clicked.connect(self._transmute)
        lay.addWidget(self.btn_transmute)

        lay.addSpacing(6)

        self.btn_edit_lore = arcane_button("✎  Edit Lore", C_GOLD_DIM)
        self.btn_edit_lore.setFixedHeight(34)
        self.btn_edit_lore.setEnabled(False)
        self.btn_edit_lore.clicked.connect(self._edit_lore)
        lay.addWidget(self.btn_edit_lore)

        lay.addSpacing(6)

        self.btn_discard = arcane_button("✕  Discard", C_CRIMSON)
        self.btn_discard.setFixedHeight(34)
        self.btn_discard.setEnabled(False)
        self.btn_discard.clicked.connect(self._discard)
        lay.addWidget(self.btn_discard)

        lay.addSpacing(12)

        # Floating window toggles
        for label, tip, cb in [
            ("≡ Queue",   "Generation Queue",  self._toggle_queue),
            ("◎ Monitor", "API Monitor",        self._toggle_monitor),
            ("◉ Oracle",  "The Oracle",         self._toggle_oracle),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(28)
            btn.setToolTip(tip)
            btn.setStyleSheet(f"""
                QPushButton{{background:transparent;color:{C_GOLD_DIM};
                    border:1px solid {C_SUBTLE};font-family:Georgia,serif;
                    font-size:9px;padding:2px 8px;}}
                QPushButton:hover{{background:{C_SUBTLE};color:{C_GOLD};}}
            """)
            btn.clicked.connect(cb)
            lay.addWidget(btn)

        return bar

    def _build_image_pane(self) -> QWidget:
        pane = QFrame()
        pane.setFixedWidth(530)
        pane.setStyleSheet(f"QFrame{{background:{C_PANEL};border:1px solid {C_GOLD_DARK};}}")
        lay = QVBoxLayout(pane)
        lay.setContentsMargins(10,10,10,10)
        lay.setSpacing(8)

        lbl = dim_label("Manifestation")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl)

        self.img_scroll = QScrollArea()
        self.img_scroll.setWidgetResizable(False)
        self.img_scroll.setFixedSize(504, 504)
        self.img_scroll.setStyleSheet(f"background:{C_BG};border:1px solid {C_SUBTLE};")
        self.img_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setFixedSize(504, 504)
        self.img_label.setStyleSheet(f"background:{C_BG};color:{C_GOLD_DIM};font-size:11px;")
        self.img_label.setText("Awaiting manifestation…")
        self.img_scroll.setWidget(self.img_label)
        lay.addWidget(self.img_scroll, alignment=Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar{{background:{C_SUBTLE};border:none;border-radius:3px;}}
            QProgressBar::chunk{{background:{C_GOLD};border-radius:3px;}}
        """)
        self.progress_bar.hide()
        lay.addWidget(self.progress_bar)

        # Prompt preview (collapsible)
        self.prompt_toggle = QPushButton("▸  Prompt Preview")
        self.prompt_toggle.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{C_GOLD_DIM};border:none;
                font-family:Georgia,serif;font-size:9px;text-align:left;padding:2px;}}
            QPushButton:hover{{color:{C_GOLD};}}
        """)
        self.prompt_toggle.clicked.connect(self._toggle_prompt_preview)
        lay.addWidget(self.prompt_toggle)

        self.prompt_preview = QPlainTextEdit()
        self.prompt_preview.setReadOnly(True)
        self.prompt_preview.setMaximumHeight(80)
        self.prompt_preview.setStyleSheet(f"""
            QPlainTextEdit{{
                background:{C_BG};color:{C_GOLD_DIM};
                border:1px solid {C_SUBTLE};
                font-family:Courier,monospace;font-size:8px;padding:4px;
            }}
        """)
        self.prompt_preview.hide()
        lay.addWidget(self.prompt_preview)

        return pane

    def _build_lore_pane(self) -> QWidget:
        pane = QFrame()
        pane.setStyleSheet(f"QFrame{{background:{C_PANEL};border:1px solid {C_GOLD_DARK};}}")
        lay = QVBoxLayout(pane)
        lay.setContentsMargins(18,16,18,16)
        lay.setSpacing(12)

        self.lore_title = QLabel("—")
        self.lore_title.setWordWrap(True)
        self.lore_title.setStyleSheet(
            f"color:{C_GOLD};font-family:Georgia,serif;font-size:18px;"
            f"font-weight:bold;background:transparent;")
        lay.addWidget(self.lore_title)
        lay.addWidget(_sep())

        for attr, label, h in [
            ("lore_desc",    "Description", 56),
            ("lore_history", "History",    100),
            ("lore_aura",    "Aura",        56),
        ]:
            rl = dim_label(label.upper())
            rl.setStyleSheet(
                f"color:{C_GOLD_DIM};font-size:9px;letter-spacing:2px;"
                f"font-family:Georgia,serif;background:transparent;")
            lay.addWidget(rl)
            field = QTextEdit()
            field.setReadOnly(True)
            field.setFixedHeight(h)
            field.setStyleSheet(f"""
                QTextEdit{{
                    background:{C_BG};color:{C_TEXT};
                    border:1px solid {C_SUBTLE};
                    font-family:Georgia,serif;font-size:11px;padding:6px;
                }}
            """)
            setattr(self, attr, field)
            lay.addWidget(field)

        kw_lbl = dim_label("VISUAL KEYWORDS")
        kw_lbl.setStyleSheet(
            f"color:{C_GOLD_DIM};font-size:9px;letter-spacing:2px;"
            f"font-family:Georgia,serif;background:transparent;")
        lay.addWidget(kw_lbl)

        self.lore_keywords = QLabel("—")
        self.lore_keywords.setWordWrap(True)
        self.lore_keywords.setStyleSheet(
            f"color:{C_TEAL};font-family:Georgia,serif;font-size:10px;"
            f"background:{C_BG};border:1px solid {C_SUBTLE};padding:6px;")
        lay.addWidget(self.lore_keywords)
        lay.addStretch()
        return pane

    def _build_statusbar(self) -> QWidget:
        bar = QFrame()
        bar.setFixedHeight(28)
        bar.setStyleSheet(f"QFrame{{background:{C_PANEL};border-top:1px solid {C_GOLD_DARK};}}")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14,0,14,0)
        self.status_lbl = dim_label("The Arca Cognitarium awaits your command.")
        lay.addWidget(self.status_lbl)
        lay.addStretch()
        self.queue_status_lbl = dim_label("")
        lay.addWidget(self.queue_status_lbl)
        return bar

    # ── Generation ────────────────────────────────────────────────────────────

    def _start_generation(self):
        adj       = self.panel.adjutoria_values
        atelier   = self.panel.atelier
        style     = self.panel.style_key
        model     = self.panel.freepik_model_id
        aspect    = self.panel.aspect_ratio_value
        seed      = self.panel.seed

        self.progress_bar.setValue(0)
        self.progress_bar.show()

        if self.panel.series_mode:
            count = self.panel.series_count
            self.status_lbl.setText(f"⚗  Conjuring series of {count}…")
            self._series_worker = SeriesWorker(atelier, style, adj, model, aspect, count)
            self._series_worker.progress.connect(self._on_status)
            self._series_worker.finished.connect(self._on_series_lore_done)
            self._series_worker.errored.connect(self._on_error)
            self._series_worker.start()
        else:
            job       = QueueJob(atelier, style, adj, model, aspect)
            job.seed  = seed
            self._queue.add_job(job)
            self.status_lbl.setText(f"⚗  Queued: {atelier}")

    def _on_series_lore_done(self, jobs: list):
        """Series lore done — push image jobs into queue."""
        for job in jobs:
            job.seed = self.panel.seed
            self._queue._jobs.append(job)
            self._queue.job_updated.emit(job.job_id)
        # Start processing if not already running
        if not self._queue._running:
            self._queue._run_next()
        self.status_lbl.setText(f"✦  Series lore complete — {len(jobs)} images queued.")

    def _on_queue_job_updated(self, job_id: int):
        job = self._queue.get_job(job_id)
        if job and job.status == QueueJob.DONE:
            # Show last completed artifact
            self._display_artifact(job.lore, job.image_path)
            # Update prompt preview
            pos, _ = assemble_image_prompt(job.lore, job.style_key, job.adj)
            self._current_prompt = pos
            if not self.prompt_preview.isHidden():
                self.prompt_preview.setPlainText(pos)

    def _on_queue_done(self):
        self.progress_bar.hide()
        done  = sum(1 for j in self._queue.jobs() if j.status == QueueJob.DONE)
        fail  = sum(1 for j in self._queue.jobs() if j.status == QueueJob.FAILED)
        self.status_lbl.setText(f"✦  Queue complete — {done} manifested, {fail} failed.")

    def _display_artifact(self, lore: dict, image_path: str):
        self._current_lore  = lore
        self._current_image = image_path

        self.lore_title.setText(lore.get("title","Unknown Artifact"))
        self.lore_desc.setPlainText(lore.get("description",""))
        self.lore_history.setPlainText(lore.get("history",""))
        self.lore_aura.setPlainText(lore.get("aura",""))
        self.lore_keywords.setText("  ·  ".join(lore.get("visual_keywords",[])))

        DISPLAY_MAX = 504
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                QSize(DISPLAY_MAX, DISPLAY_MAX),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            dpr = self.devicePixelRatioF()
            pixmap.setDevicePixelRatio(dpr)
            self.img_label.setPixmap(pixmap)
            self.img_label.setFixedSize(
                int(pixmap.width()/dpr), int(pixmap.height()/dpr))
        else:
            self.img_label.setText("[ Image unavailable ]")

        self.img_scroll.setFixedSize(DISPLAY_MAX+4, DISPLAY_MAX+4)
        self.img_scroll.setWidgetResizable(False)
        self.btn_transmute.setEnabled(True)
        self.btn_edit_lore.setEnabled(True)
        self.btn_discard.setEnabled(True)

    def _on_status(self, msg: str):
        self.status_lbl.setText(msg)

    def _on_error(self, err: str):
        self.progress_bar.hide()
        self.status_lbl.setText(f"✕  Error: {err[:120]}")
        self.img_label.setText("Generation failed.")

    # ── Transmute ─────────────────────────────────────────────────────────────

    def _transmute(self):
        if not self._current_lore:
            return
        adj    = self.panel.adjutoria_values
        job    = QueueJob(
            self.panel.atelier, self.panel.style_key, adj,
            self.panel.freepik_model_id, self.panel.aspect_ratio_value)
        job.lore   = copy.deepcopy(self._current_lore)
        job.status = QueueJob.IMAGE   # skip lore
        job.seed   = random.randint(0, 2**31-1)
        self._queue._jobs.append(job)
        self._queue.job_updated.emit(job.job_id)
        if not self._queue._running:
            self._queue._run_next()
        self.status_lbl.setText(f"↺  Transmuting: {self._current_lore.get('title','?')}…")

    # ── Edit lore ─────────────────────────────────────────────────────────────

    def _edit_lore(self):
        if not self._current_lore:
            return
        dlg = LoreEditorDialog(self._current_lore, self)
        if dlg.exec():
            self._current_lore = dlg.get_lore()
            self._display_artifact(self._current_lore, self._current_image)

    # ── Discard ───────────────────────────────────────────────────────────────

    def _discard(self):
        self._current_lore  = {}
        self._current_image = ""
        self._current_prompt= ""
        self._clear_lore_fields()
        self.img_label.clear()
        self.img_label.setText("Awaiting manifestation…")
        self.btn_transmute.setEnabled(False)
        self.btn_edit_lore.setEnabled(False)
        self.btn_discard.setEnabled(False)
        self.prompt_preview.clear()
        self.status_lbl.setText("Artifact discarded.")

    def _clear_lore_fields(self):
        self.lore_title.setText("—")
        self.lore_desc.clear()
        self.lore_history.clear()
        self.lore_aura.clear()
        self.lore_keywords.setText("—")

    # ── Prompt preview toggle ─────────────────────────────────────────────────

    def _toggle_prompt_preview(self):
        if self.prompt_preview.isHidden():
            self.prompt_preview.show()
            self.prompt_preview.setPlainText(self._current_prompt or "(no prompt yet)")
            self.prompt_toggle.setText("▾  Prompt Preview")
        else:
            self.prompt_preview.hide()
            self.prompt_toggle.setText("▸  Prompt Preview")

    # ── Floating windows ──────────────────────────────────────────────────────

    def _toggle_queue(self):
        if self._queue_win is None:
            self._queue_win = QueueWindow(self._queue, self)
        if self._queue_win.isVisible():
            self._queue_win.hide()
        else:
            self._queue_win.show()
            self._queue_win._refresh()

    def _toggle_monitor(self):
        if self._monitor_win is None:
            self._monitor_win = MonitorWindow(self)
        if self._monitor_win.isVisible():
            self._monitor_win.hide()
        else:
            self._monitor_win.show()

    def _toggle_oracle(self):
        if self._oracle_win is None:
            self._oracle_win = OracleWindow(self)
        if self._oracle_win.isVisible():
            self._oracle_win.hide()
        else:
            self._oracle_win.show()

    # ── Tome ──────────────────────────────────────────────────────────────────

    def _open_tome(self):
        dlg = CompendiumTome(self)
        dlg.remanifest_requested.connect(self._remanifest_from_vault)
        dlg.exec()

    def _remanifest_from_vault(self, meta: dict):
        """Load vault entry settings back into panel and queue an image job."""
        # Set panel to matching settings where possible
        idx = self.panel.machina.atelier_combo.findText(meta.get("atelier",""))
        if idx >= 0: self.panel.machina.atelier_combo.setCurrentIndex(idx)
        idx = self.panel.machina.style_combo.findText(meta.get("style",""))
        if idx >= 0: self.panel.machina.style_combo.setCurrentIndex(idx)
        idx = self.panel.machina.model_combo.findText(
            next((m[1] for m in FREEPIK_MODELS if m[0]==meta.get("engine","")), ""))
        if idx >= 0: self.panel.machina.model_combo.setCurrentIndex(idx)

        adj = meta.get("adjutoria") or _default_adjutoria()

        lore = {k: meta.get(k,"") for k in
                ("title","description","history","aura","visual_keywords")}
        job        = QueueJob(
            meta.get("atelier", self.panel.atelier),
            meta.get("style",   self.panel.style_key),
            adj,
            meta.get("engine",  self.panel.freepik_model_id),
            meta.get("aspect_ratio", self.panel.aspect_ratio_value))
        job.lore   = lore
        job.status = QueueJob.IMAGE
        job.seed   = random.randint(0, 2**31-1)
        self._queue._jobs.append(job)
        self._queue.job_updated.emit(job.job_id)
        if not self._queue._running:
            self._queue._run_next()
        self.status_lbl.setText(f"⚗  Re-manifesting: {lore.get('title','?')}…")


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
    window = MythotexApp()
    window.show()
    sys.exit(app.exec())
