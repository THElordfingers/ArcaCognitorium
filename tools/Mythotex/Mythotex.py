#!/usr/bin/env python3
"""   
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      ███    ███ ██    ██ ████████ ██   ██  ██████  ████████ ███████ ██   ██       ▍
🮈      ████  ████  ██  ██     ██    ██   ██ ██    ██    ██    ██       ██ ██        ▍
🮈      ██ ████ ██   ████      ██    ███████ ██    ██    ██    █████     ███         ▍
🮈      ██  ██  ██    ██       ██    ██   ██ ██    ██    ██    ██       ██ ██        ▍
🮈      ██      ██    ██       ██    ██   ██  ██████     ██    ███████ ██   ██       ▍
🮈                                                                                   ▍      
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


import os
import re
import sys
import json
import time
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import anthropic

from PyQt6.QtCore import (
    Qt, QThread, QTimer, QPropertyAnimation,
    QEasingCurve, QSize, pyqtSignal, QObject
)
from PyQt6.QtGui import (
    QPixmap, QFont, QFontDatabase, QPalette, QColor,
    QIcon
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel,
    QPushButton, QComboBox, QSlider, QScrollArea,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QTextEdit, QDialog, QDialogButtonBox, QProgressBar,
    QSizePolicy, QSpacerItem, QSplitter, QScrollBar
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS & PATHS
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR        = Path.home() / "Mythotex"
VAULT_DIR       = BASE_DIR / "Vault"
REFERENTIA_DIR  = BASE_DIR / "Referentia"
IMMUTABLE_PATH  = REFERENTIA_DIR / "lore_immutable.md"
MUTABLE_PATH    = REFERENTIA_DIR / "lore_mutable.md"
DNA_PATH        = BASE_DIR / "aesthetic_dna.json"
GEN_LOG_PATH    = BASE_DIR / "generation_log.json"
TEMP_IMAGE      = BASE_DIR / "temp_manifest.png"

SD_BINARY      = Path.home() / "ArcaCognitorium/tools/Mythotex/stable-diffusion.cpp/build/bin/sd-cli"
SD_MODELS_DIR  = Path.home() / "ArcaCognitorium/tools/Mythotex/models"
SD_MODEL_EXTS  = {".safetensors", ".ckpt", ".bin"}
SD_VAE         = SD_MODELS_DIR / "vae-ft-mse-840000-ema-pruned.safetensors"

CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ─────────────────────────────────────────────────────────────────────────────
# COLOURS & STYLES
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

FONT_SERIF = "Constantia, Georgia, serif"

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: Georgia, Constantia, serif;
}}
QScrollBar:vertical {{
    background: {C_PANEL};
    width: 8px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {C_GOLD_DARK};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {C_PANEL};
    height: 8px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {C_GOLD_DARK};
    border-radius: 4px;
}}
QToolTip {{
    background: {C_PANEL};
    color: {C_GOLD};
    border: 1px solid {C_GOLD_DARK};
    font-family: Georgia, serif;
    padding: 4px;
}}
"""

# ─────────────────────────────────────────────────────────────────────────────
# ARX ARCANA  (the workshops of the Arca Cognitarium)
# ─────────────────────────────────────────────────────────────────────────────

ARX_ARCANA = {
    "Staves & Wands":       "Magical staves, wands, rods, and channelling implements",
    "Grimoires & Tomes":    "Spellbooks, forbidden texts, enchanted scrolls, arcane journals",
    "Potions & Phials":     "Elixirs, brews, bottled magic, alchemical concoctions",
    "Rings & Amulets":      "Enchanted rings, necklaces, talismans, and warding medallions",
    "Blades & Daggers":     "Magical swords, enchanted daggers, cursed blades, runic knives",
    "Cloaks & Robes":       "Enchanted garments, wizard robes, cloaks of concealment",
    "Orbs & Crystals":      "Scrying orbs, crystal balls, seeing stones, focus gems",
    "Masks & Helms":        "Enchanted helms, arcane masks, visored crowns, spirit-bound hoods",
    "Relics & Idols":       "Ancient relics, cult idols, divine artefacts, god-touched objects",
    "Bags & Containers":    "Bags of holding, enchanted pouches, dimensional chests, bound vessels",
    "Keys & Locks":         "Skeleton keys, dimensional locks, puzzle boxes, sealed vaults",
    "Skulls & Bones":       "Necromantic foci, spell-bound skulls, cursed bones, death relics",
}

# ─────────────────────────────────────────────────────────────────────────────
# STYLE PRESETS  (Styli Praescripti)
# ─────────────────────────────────────────────────────────────────────────────

STYLE_PRESETS = {
    "Woodcut Ink": {
        "positive": (
            "bold black ink outline, woodcut illustration, linocut print, "
            "white background, isolated object, flat colour fills, "
            "limited palette, deep teal crimson amber accents only, "
            "high contrast, crisp graphic linework, no gradients, "
            "woodblock print aesthetic, sharp edges"
        ),
        "negative": (
            "soft, blurry, blur, bokeh, depth of field, painterly, photorealistic, "
            "watercolour, gradient, smooth shading, 3d render, noisy, low contrast, "
            "pastel, washed out, muddy colours, sketch, pencil, dof, lens flare, "
            "chromatic aberration, ugly, deformed, extra limbs, extra fingers, "
            "malformed hands, jpeg artifacts, signature, watermark, text, "
            "username, cropped, out of frame, worst quality, low quality"
        ),
        "cfg": 14,
    },
    "Silhouette": {
        "positive": (
            "bold black silhouette, stark white background, isolated object, "
            "minimal single colour accent, flat graphic, high contrast, "
            "clean edges, vector-style illustration, shadow play"
        ),
        "negative": (
            "detailed interior, soft edges, gradient, painterly, "
            "photorealistic, colourful, noisy, blurry, blur, bokeh, textured fill, "
            "dof, lens flare, chromatic aberration, ugly, deformed, extra limbs, "
            "extra fingers, malformed hands, jpeg artifacts, signature, watermark, "
            "text, worst quality, low quality, multiple objects"
        ),
        "cfg": 15,
    },
    "Enamel Pin": {
        "positive": (
            "enamel pin design, hard black outline, flat colour fills, "
            "cel shaded, white background, isolated object, bold graphic, "
            "cloisonné style, limited palette, crisp edges, "
            "no gradients, high contrast illustration"
        ),
        "negative": (
            "soft, blurry, blur, bokeh, painterly, photorealistic, watercolour, "
            "gradient shading, 3d render, rough edges, sketch lines, dof, "
            "lens flare, chromatic aberration, ugly, deformed, extra limbs, "
            "extra fingers, malformed hands, jpeg artifacts, signature, watermark, "
            "text, worst quality, low quality, noisy, grainy"
        ),
        "cfg": 13,
    },
    "Inkpunk": {
        "positive": (
            "inkpunk style, punk woodcut, rough ink edges, scratchy linework, "
            "bold black outlines, white background, isolated object, "
            "high energy graphic, teal crimson amber, grungy texture, "
            "zine aesthetic, linocut distress, high contrast"
        ),
        "negative": (
            "clean, smooth, polished, photorealistic, painterly, soft, blurry, blur, "
            "gradient, 3d render, low contrast, pastel, watercolour, bokeh, dof, "
            "lens flare, chromatic aberration, ugly, deformed, extra limbs, "
            "extra fingers, malformed hands, jpeg artifacts, signature, watermark, "
            "text, worst quality, low quality"
        ),
        "cfg": 12,
    },
}

STYLE_KEYS = list(STYLE_PRESETS.keys())

# ─────────────────────────────────────────────────────────────────────────────
# MODEL PROFILES  (Indices Machinarum)
# Keyed on lowercase filename fragments — matched via substring.
# Applied automatically when a model is selected in ControlPanel.
# ─────────────────────────────────────────────────────────────────────────────

MODEL_PROFILES = [
    {
        "match":   ["inkpunk"],
        "label":   "Inkpunk Diffusion",
        "cfg":     8,
        "steps":   25,
        "sampler": "euler_a",
        "trigger": "nvinkpunk",
        "note":    "Trigger token 'nvinkpunk' applied automatically",
    },
    {
        "match":   ["dreamshaper_8", "dreamshaper8", "dreamshaper_8_pruned"],
        "label":   "DreamShaper 8",
        "cfg":     9,
        "steps":   28,
        "sampler": "dpm++2s_a",
        "note":    "General illustration · fantasy · arcana",
    },
    {
        "match":   ["neverending", "neverendingdream"],
        "label":   "NeverEnding Dream",
        "cfg":     8,
        "steps":   28,
        "sampler": "dpm++2s_a",
        "note":    "Dark fantasy · atmospheric objects",
    },
    {
        "match":   ["toonyou"],
        "label":   "ToonYou",
        "cfg":     7,
        "steps":   24,
        "sampler": "euler_a",
        "note":    "Cel-shaded · enamel pin style",
    },
    {
        "match":   ["deliberate"],
        "label":   "Deliberate",
        "cfg":     12,
        "steps":   30,
        "sampler": "dpm++2s_a",
        "note":    "Detailed illustration · concept art",
    },
    {
        "match":   ["analog"],
        "label":   "Analog Diffusion",
        "cfg":     10,
        "steps":   28,
        "sampler": "euler_a",
        "trigger": "analog style",
        "note":    "Trigger token 'analog style' applied automatically",
    },
    {
        "match":   ["meinamix", "meina"],
        "label":   "MeinaMix",
        "cfg":     8,
        "steps":   25,
        "sampler": "dpm++2s_a",
        "note":    "Cel-shaded · flat colour illustration",
    },
    {
        "match":   ["epicrealism", "epicreal"],
        "label":   "epiCRealism",
        "cfg":     6,
        "steps":   35,
        "sampler": "dpm++2s_a",
        "note":    "Hyperreal metal · mechanical objects",
    },
    {
        "match":   ["dreamlike"],
        "label":   "DreamLike Diffusion",
        "cfg":     9,
        "steps":   28,
        "sampler": "euler_a",
        "trigger": "dreamlikeart",
        "note":    "Trigger token 'dreamlikeart' applied automatically",
    },
    {
        "match":   ["v1-5", "v1_5", "sd15", "pruned-emaonly"],
        "label":   "SD 1.5 Base",
        "cfg":     14,
        "steps":   28,
        "sampler": "euler_a",
        "note":    "Vanilla SD 1.5 — consider a fine-tune",
    },
]


def _match_model_profile(filename: str) -> dict | None:
    """Return the first matching MODEL_PROFILES entry for a filename, or None."""
    name_lower = filename.lower()
    for profile in MODEL_PROFILES:
        if any(frag in name_lower for frag in profile["match"]):
            return profile
    return None


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
    for d in [BASE_DIR, VAULT_DIR, REFERENTIA_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not IMMUTABLE_PATH.exists():
        IMMUTABLE_PATH.write_text(
            "# Lore Immutable — World Canon\n\n"
            "The Arca Cognitarium is an atelier of ateliers, a vast arcane manufactory "
            "hidden between the folds of known cartography. Its products are artifacts: "
            "objects of occult power, strange provenance, and inexplicable beauty. "
            "Each atelier specialises in a domain. All objects share one quality — "
            "they exist at the threshold between the mundane and the impossible.\n"
        )
    if not MUTABLE_PATH.exists():
        MUTABLE_PATH.write_text(
            "# Lore Mutable — Current Strategy\n\n"
            "No analysis yet conducted. Generate and rate artifacts to refine this strategy.\n"
        )
    if not DNA_PATH.exists():
        DNA_PATH.write_text(json.dumps({"favored": [], "forbidden": []}, indent=2))
    if not GEN_LOG_PATH.exists():
        GEN_LOG_PATH.write_text(json.dumps([], indent=2))


def _load_dna() -> tuple[list, list]:
    try:
        dna = json.loads(DNA_PATH.read_text())
        return dna.get("favored", []), dna.get("forbidden", [])
    except Exception:
        return [], []


def _save_dna(favored: list, forbidden: list):
    DNA_PATH.write_text(json.dumps({"favored": favored, "forbidden": forbidden}, indent=2))


def _log_generation(entry: dict):
    try:
        log = json.loads(GEN_LOG_PATH.read_text())
    except Exception:
        log = []
    log.append({"timestamp": datetime.now().isoformat(), **entry})
    GEN_LOG_PATH.write_text(json.dumps(log[-200:], indent=2))  # keep last 200


def _scan_models() -> list[Path]:
    """Return sorted list of model files in SD_MODELS_DIR."""
    if not SD_MODELS_DIR.exists():
        return []
    return sorted(
        p for p in SD_MODELS_DIR.iterdir()
        if p.suffix.lower() in SD_MODEL_EXTS
    )


def gold_label(text: str, size: int = 11, bold: bool = False) -> QLabel:
    lbl = QLabel(text)
    weight = "bold" if bold else "normal"
    lbl.setStyleSheet(
        f"color: {C_GOLD}; font-family: Georgia, serif; "
        f"font-size: {size}px; font-weight: {weight}; background: transparent;"
    )
    return lbl


def dim_label(text: str, size: int = 10) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
        f"font-size: {size}px; background: transparent;"
    )
    return lbl


def arcane_button(text: str, accent: str = C_GOLD) -> QPushButton:
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {C_PANEL};
            color: {accent};
            border: 1px solid {C_GOLD_DARK};
            font-family: Georgia, serif;
            font-size: 11px;
            padding: 6px 14px;
            letter-spacing: 1px;
        }}
        QPushButton:hover {{
            background: {C_GOLD_DARK};
            border-color: {accent};
        }}
        QPushButton:pressed {{
            background: {C_SUBTLE};
        }}
        QPushButton:disabled {{
            color: {C_GOLD_DARK};
            border-color: {C_SUBTLE};
        }}
    """)
    return btn


# ─────────────────────────────────────────────────────────────────────────────
# WORKER: MythotexWorker  (lore + image generation)
# ─────────────────────────────────────────────────────────────────────────────

class MythotexWorker(QThread):

    progress      = pyqtSignal(str)           # status messages
    step_progress = pyqtSignal(int, int)      # current step, total steps
    finished      = pyqtSignal(dict, str)     # lore dict, image path
    errored       = pyqtSignal(str)

    def __init__(self, atelier: str, style_key: str, cfg: int, steps: int,
                 sampler: str, width: int, height: int, model_path: Path,
                 parent=None):
        super().__init__(parent)
        self.atelier    = atelier
        self.style_key  = style_key
        self.cfg        = cfg
        self.steps      = steps
        self.sampler    = sampler
        self.width      = width
        self.height     = height
        self.model_path = model_path
        self._client    = anthropic.Anthropic(
            api_key=os.environ.get("CLAUDE_API_KEY", "")
        )

    def run(self):
        try:
            self.progress.emit("Consulting the Arca Cognitarium…")
            lore = self._generate_lore()

            self.progress.emit("Distilling visual essence…")
            pos, neg = self._sd_prompts(lore)

            self.progress.emit("Manifesting the artifact…")
            image_path = self._generate_image(pos, neg)

            _log_generation({"atelier": self.atelier, "title": lore.get("title", "?"),
                             "style": self.style_key})

            self.finished.emit(lore, image_path)

        except Exception as exc:
            self.errored.emit(str(exc))

    # ── Lore ──────────────────────────────────────────────────────────────────

    def _generate_lore(self) -> dict:
        immutable = IMMUTABLE_PATH.read_text() if IMMUTABLE_PATH.exists() else ""
        mutable   = MUTABLE_PATH.read_text()   if MUTABLE_PATH.exists()   else ""
        favored, forbidden = _load_dna()

        dna_clause = ""
        if favored:
            dna_clause += f"\nFavoured descriptors (lean toward these): {', '.join(favored[:10])}"
        if forbidden:
            dna_clause += f"\nForbidden descriptors (avoid these): {', '.join(forbidden[:10])}"

        system = (
            "You are the Arca Cognitarium, a generative lore engine for arcane artifacts. "
            "Respond ONLY with a single raw JSON object — no markdown fences, no preamble, "
            "no commentary whatsoever.\n\n"
            f"World canon (immutable):\n{immutable}\n\n"
            f"Current lore strategy (mutable):\n{mutable}"
            f"{dna_clause}"
        )

        user = (
            f"Generate a unique arcane artifact from the Arx Arcana: {self.atelier}\n"
            f"Category theme: {ARX_ARCANA.get(self.atelier, '')}\n\n"
            "Return exactly this JSON structure:\n"
            "{\n"
            '  "title": "name of the artifact",\n'
            '  "description": "one evocative sentence",\n'
            '  "history": "two to four sentences of history and provenance",\n'
            '  "aura": "brief sensory impression of its presence",\n'
            '  "visual_keywords": ["6 to 10 concrete visual descriptors — '
            'materials, textures, colours, shapes only, no quality adjectives"]\n'
            "}"
        )

        response = self._client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return _parse_json_block(response.content[0].text.strip())

    # ── SD Prompts ────────────────────────────────────────────────────────────

    def _sd_prompts(self, lore: dict) -> tuple[str, str]:
        preset   = STYLE_PRESETS.get(self.style_key, STYLE_PRESETS["Woodcut Ink"])
        title    = lore.get("title", "arcane artifact")
        desc     = lore.get("description", "")
        keywords = lore.get("visual_keywords", [])
        kw_str   = ", ".join(keywords[:3])

        # Prepend model trigger token if the active model profile defines one
        profile = _match_model_profile(self.model_path.name)
        trigger = profile.get("trigger", "") if profile else ""

        positive = f"{trigger}, {preset['positive']}, {title}, {desc}, {kw_str}" \
                   if trigger else \
                   f"{preset['positive']}, {title}, {desc}, {kw_str}"
        negative = preset["negative"]
        return positive, negative

    # ── Image ─────────────────────────────────────────────────────────────────

    def _generate_image(self, positive: str, negative: str) -> str:
        if not SD_BINARY.exists():
            raise FileNotFoundError(f"sd-cli not found at {SD_BINARY}")
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        out_path = str(TEMP_IMAGE)

        cmd = [
            str(SD_BINARY),
            "--model",           str(self.model_path),
            "--prompt",          positive,
            "--negative-prompt", negative,
            "--cfg-scale",       str(self.cfg),
            "--steps",           str(self.steps),
            "--sampling-method", self.sampler,
            "-W",                str(self.width),
            "-H",                str(self.height),
            "--output",          out_path,
            "--seed",            str(int(time.time()) % 2**31),
        ]

        if SD_VAE.exists():
            cmd += ["--vae", str(SD_VAE)]

        # Stream output to parse step progress
        # sd-cli emits lines like: "  |====...| 12/28 - 1.23s/it"
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        stderr_lines = []
        step_re = re.compile(r"\|\s*(\d+)\s*/\s*(\d+)")

        for line in proc.stdout:
            stderr_lines.append(line)
            m = step_re.search(line)
            if m:
                current = int(m.group(1))
                total   = int(m.group(2))
                self.step_progress.emit(current, total)

        proc.wait()

        if proc.returncode != 0:
            tail = "".join(stderr_lines[-20:])
            raise RuntimeError(f"sd-cli failed:\n{tail}")

        if not TEMP_IMAGE.exists():
            raise FileNotFoundError("sd-cli completed but produced no image.")

        return out_path


# ─────────────────────────────────────────────────────────────────────────────
# WORKER: AnalysisWorker  (self-refining strategy engine)
# ─────────────────────────────────────────────────────────────────────────────

class AnalysisWorker(QThread):

    finished = pyqtSignal(str)
    errored  = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._client = anthropic.Anthropic(
            api_key=os.environ.get("CLAUDE_API_KEY", "")
        )

    def run(self):
        try:
            rated = self._gather_rated_vault()
            if not rated:
                self.finished.emit("Insufficient rated specimens for analysis.")
                return

            current = MUTABLE_PATH.read_text() if MUTABLE_PATH.exists() else ""

            system = (
                "You are the Arca Cognitarium's self-refining oracle. "
                "Analyse the rated artifact corpus and produce a concise lore strategy. "
                "Respond ONLY with raw markdown — no preamble, no fences."
            )

            user = (
                f"Current strategy:\n{current}\n\n"
                f"Rated artifact corpus:\n{json.dumps(rated, indent=2)}\n\n"
                "Write an updated lore_mutable.md strategy that:\n"
                "- Identifies patterns in high-rated (4–5★) artifacts: themes, materials, moods\n"
                "- Identifies what makes low-rated (1–2★) artifacts fail\n"
                "- Gives 3–5 concrete directives for future generation\n"
                "- Is under 300 words, directive not descriptive\n"
                "- Preserves directives still validated by the data"
            )

            response = self._client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=600,
                system=system,
                messages=[{"role": "user", "content": user}],
            )

            strategy = response.content[0].text.strip()
            MUTABLE_PATH.write_text(strategy)

            # Update aesthetic DNA from ratings
            self._update_dna(rated)

            self.finished.emit(strategy)

        except Exception as exc:
            self.errored.emit(str(exc))

    def _gather_rated_vault(self) -> list:
        rated = []
        if not VAULT_DIR.exists():
            return rated
        for entry_dir in sorted(VAULT_DIR.iterdir()):
            meta_path = entry_dir / "meta.json"
            if meta_path.is_file():
                try:
                    meta   = json.loads(meta_path.read_text())
                    rating = meta.get("rating")
                    if rating is not None:
                        rated.append({
                            "title":          meta.get("title", entry_dir.name),
                            "visual_keywords": meta.get("visual_keywords", []),
                            "aura":           meta.get("aura", ""),
                            "atelier":        meta.get("atelier", ""),
                            "rating":         rating,
                        })
                except Exception:
                    pass
        return rated

    def _update_dna(self, rated: list):
        favored, forbidden = _load_dna()
        for item in rated:
            kws = item.get("visual_keywords", [])
            r   = item.get("rating", 3)
            if r >= 4:
                for kw in kws:
                    if kw not in favored:
                        favored.append(kw)
            elif r <= 2:
                for kw in kws:
                    if kw not in forbidden:
                        forbidden.append(kw)
        # Cap lists
        _save_dna(favored[-40:], forbidden[-40:])


# ─────────────────────────────────────────────────────────────────────────────
# COMPENDIUM TOME  (vault review dialog)
# ─────────────────────────────────────────────────────────────────────────────

class CompendiumTome(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compendium Tome — The Sealed Vault")
        self.setMinimumSize(900, 640)
        self.setStyleSheet(f"""
            QDialog {{
                background: {C_BG};
                color: {C_TEXT};
            }}
            QFrame#tome_card {{
                background: {C_PANEL};
                border: 1px solid {C_GOLD_DARK};
            }}
        """)
        self._build_ui()
        self._load_vault()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Header
        hdr = gold_label("✦  Compendium Tome  ✦", 16, bold=True)
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hdr)

        # Scroll area for cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"background: {C_BG}; border: none;")
        root.addWidget(self.scroll)

        self.card_container = QWidget()
        self.card_layout    = QVBoxLayout(self.card_container)
        self.card_layout.setSpacing(10)
        self.card_layout.addStretch()
        self.scroll.setWidget(self.card_container)

        # Footer buttons
        foot = QHBoxLayout()
        self.btn_analyse = arcane_button("⚙  Run Analysis Engine", C_TEAL)
        self.btn_close   = arcane_button("✕  Close Tome")
        self.btn_analyse.clicked.connect(self._run_analysis)
        self.btn_close.clicked.connect(self.accept)
        foot.addWidget(self.btn_analyse)
        foot.addStretch()
        foot.addWidget(self.btn_close)
        root.addLayout(foot)

        self.status_lbl = dim_label("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.status_lbl)

    def _load_vault(self):
        # Clear existing cards
        while self.card_layout.count() > 1:
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not VAULT_DIR.exists():
            self.card_layout.insertWidget(0, dim_label("The vault is empty."))
            return

        entries = sorted(VAULT_DIR.iterdir(), reverse=True)
        if not entries:
            self.card_layout.insertWidget(0, dim_label("The vault is empty."))
            return

        for i, entry_dir in enumerate(entries):
            meta_path  = entry_dir / "meta.json"
            image_path = entry_dir / "artifact.png"
            if not meta_path.exists():
                continue
            try:
                meta = json.loads(meta_path.read_text())
                card = self._make_card(meta, image_path, entry_dir)
                self.card_layout.insertWidget(i, card)
            except Exception:
                pass

    def _make_card(self, meta: dict, image_path: Path, entry_dir: Path) -> QFrame:
        card = QFrame()
        card.setObjectName("tome_card")
        card.setFixedHeight(160)
        lay  = QHBoxLayout(card)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(12)

        # Thumbnail
        thumb = QLabel()
        thumb.setFixedSize(120, 120)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet(f"background: {C_BG}; border: 1px solid {C_GOLD_DARK};")
        if image_path.exists():
            px = QPixmap(str(image_path)).scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            thumb.setPixmap(px)
        else:
            thumb.setText("no image")
            thumb.setStyleSheet(f"color: {C_GOLD_DIM}; font-size: 9px;")
        lay.addWidget(thumb)

        # Text block
        info = QVBoxLayout()
        info.setSpacing(3)
        title_lbl = gold_label(meta.get("title", "Unknown"), 12, bold=True)
        info.addWidget(title_lbl)
        atelier_lbl = dim_label(meta.get("atelier", ""))
        info.addWidget(atelier_lbl)
        desc_lbl = QLabel(meta.get("description", ""))
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"color: {C_TEXT}; font-size: 10px; background: transparent;")
        info.addWidget(desc_lbl)
        info.addStretch()
        lay.addLayout(info, stretch=1)

        # Star rating
        star_col = QVBoxLayout()
        star_col.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        star_col.setSpacing(4)
        star_lbl = dim_label("Aesthetic Rating")
        star_col.addWidget(star_lbl)

        star_row = QHBoxLayout()
        star_row.setSpacing(2)
        current_rating = meta.get("rating", 0)
        stars = []
        for s in range(1, 6):
            btn = QPushButton("★")
            btn.setFixedSize(22, 22)
            btn.setCheckable(True)
            btn.setChecked(s <= current_rating)
            filled = s <= current_rating
            btn.setStyleSheet(self._star_style(filled))
            btn.clicked.connect(
                lambda checked, s=s, ed=entry_dir, m=meta, sl=stars:
                self._rate_artifact(s, ed, m, sl)
            )
            stars.append(btn)
            star_row.addWidget(btn)

        star_col.addLayout(star_row)

        del_btn = arcane_button("⌫ Unseal", C_CRIMSON)
        del_btn.setFixedHeight(24)
        del_btn.clicked.connect(lambda: self._delete_entry(entry_dir, card))
        star_col.addSpacerItem(QSpacerItem(0, 8))
        star_col.addWidget(del_btn)

        lay.addLayout(star_col)
        return card

    def _star_style(self, filled: bool) -> str:
        colour = C_GOLD if filled else C_SUBTLE
        return (
            f"QPushButton {{ background: transparent; color: {colour}; "
            f"border: none; font-size: 16px; }}"
            f"QPushButton:hover {{ color: {C_GOLD}; }}"
        )

    def _rate_artifact(self, rating: int, entry_dir: Path, meta: dict, stars: list):
        meta["rating"] = rating
        meta_path = entry_dir / "meta.json"
        meta_path.write_text(json.dumps(meta, indent=2))
        for i, btn in enumerate(stars):
            btn.setChecked(i < rating)
            btn.setStyleSheet(self._star_style(i < rating))

    def _delete_entry(self, entry_dir: Path, card: QFrame):
        shutil.rmtree(entry_dir, ignore_errors=True)
        card.setParent(None)
        card.deleteLater()

    def _run_analysis(self):
        self.btn_analyse.setEnabled(False)
        self.status_lbl.setText("⚙ Analysis engine running…")
        self._analysis_worker = AnalysisWorker(self)
        self._analysis_worker.finished.connect(self._on_analysis_done)
        self._analysis_worker.errored.connect(self._on_analysis_error)
        self._analysis_worker.start()

    def _on_analysis_done(self, strategy: str):
        self.btn_analyse.setEnabled(True)
        self.status_lbl.setText("✦ Lore strategy updated.")

    def _on_analysis_error(self, err: str):
        self.btn_analyse.setEnabled(True)
        self.status_lbl.setText(f"✕ Analysis failed: {err[:80]}")


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL PANEL  (slide-out panel)
# ─────────────────────────────────────────────────────────────────────────────

PANEL_WIDTH = 280

class ControlPanel(QFrame):

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(PANEL_WIDTH)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border-right: 1px solid {C_GOLD_DARK};
            }}
            QLabel {{
                background: transparent;
            }}
            QComboBox {{
                background: {C_BG};
                color: {C_GOLD};
                border: 1px solid {C_GOLD_DARK};
                padding: 3px 8px;
                font-family: Georgia, serif;
                font-size: 11px;
            }}
            QComboBox QAbstractItemView {{
                background: {C_PANEL};
                color: {C_GOLD};
                selection-background-color: {C_GOLD_DARK};
            }}
            QSlider::groove:horizontal {{
                background: {C_SUBTLE};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {C_GOLD};
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}
            QSlider::sub-page:horizontal {{
                background: {C_GOLD_DIM};
                border-radius: 2px;
            }}
        """)
        self._build_ui()
        self._visible = False

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 18, 14, 14)
        root.setSpacing(14)

        hdr = gold_label("⚙  Machina Controli", 13, bold=True)
        root.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C_GOLD_DARK};")
        root.addWidget(sep)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)

        def flbl(text):
            l = dim_label(text)
            l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            return l

        # Arx Arcana
        self.atelier_combo = QComboBox()
        self.atelier_combo.addItems(list(ARX_ARCANA.keys()))
        form.addRow(flbl("Arx Arcana"), self.atelier_combo)

        # Style
        self.style_combo = QComboBox()
        self.style_combo.addItems(STYLE_KEYS)
        self.style_combo.currentTextChanged.connect(self._on_style_changed)
        form.addRow(flbl("Stylus"), self.style_combo)

        self.cfg_hint = dim_label(f"CFG {STYLE_PRESETS['Woodcut Ink']['cfg']} recommended")
        form.addRow(QLabel(""), self.cfg_hint)

        # CFG Scale
        self.cfg_slider = QSlider(Qt.Orientation.Horizontal)
        self.cfg_slider.setRange(5, 20)
        self.cfg_slider.setValue(14)
        self.cfg_slider.setTickInterval(1)
        self.cfg_val = dim_label("14")
        self.cfg_slider.valueChanged.connect(lambda v: self.cfg_val.setText(str(v)))
        cfg_row = QHBoxLayout()
        cfg_row.addWidget(self.cfg_slider)
        cfg_row.addWidget(self.cfg_val)
        form.addRow(flbl("CFG"), cfg_row)

        # Steps
        self.steps_slider = QSlider(Qt.Orientation.Horizontal)
        self.steps_slider.setRange(10, 60)
        self.steps_slider.setValue(28)
        self.steps_val = dim_label("28")
        self.steps_slider.valueChanged.connect(lambda v: self.steps_val.setText(str(v)))
        steps_row = QHBoxLayout()
        steps_row.addWidget(self.steps_slider)
        steps_row.addWidget(self.steps_val)
        form.addRow(flbl("Steps"), steps_row)

        # Sampler
        self.sampler_combo = QComboBox()
        self.sampler_combo.addItems(["euler_a", "euler", "dpm++2m", "dpm++2s_a", "lcm"])
        form.addRow(flbl("Sampler"), self.sampler_combo)

        # Resolution
        self.res_combo = QComboBox()
        self.res_combo.addItems(["512×512", "512×768", "768×512", "768×768"])
        form.addRow(flbl("Resolution"), self.res_combo)

        # Model
        self.model_combo = QComboBox()
        self._populate_models()
        form.addRow(flbl("Model"), self.model_combo)

        self.model_hint = dim_label("")
        self.model_note = dim_label("")
        self.model_combo.currentIndexChanged.connect(self._apply_model_profile)
        self._apply_model_profile()   # apply defaults on startup
        form.addRow(QLabel(""), self.model_hint)
        form.addRow(QLabel(""), self.model_note)

        root.addLayout(form)
        root.addStretch()

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {C_GOLD_DARK};")
        root.addWidget(sep2)

        self.btn_vault = arcane_button("📖  Open Compendium Tome")
        root.addWidget(self.btn_vault)

    def _on_style_changed(self, key: str):
        preset = STYLE_PRESETS.get(key, {})
        cfg    = preset.get("cfg", 14)
        self.cfg_hint.setText(f"CFG {cfg} recommended")
        self.cfg_slider.setValue(cfg)

    def _populate_models(self):
        self.model_combo.clear()
        self._model_paths = _scan_models()
        if self._model_paths:
            for p in self._model_paths:
                self.model_combo.addItem(p.name)
        else:
            self.model_combo.addItem("(no models found)")

    def _apply_model_profile(self):
        idx = self.model_combo.currentIndex()
        if not self._model_paths or idx < 0 or idx >= len(self._model_paths):
            self.model_hint.setText("")
            self.model_note.setText("")
            return

        p       = self._model_paths[idx]
        profile = _match_model_profile(p.name)

        # Size hint always shown
        size_mb = p.stat().st_size / 1_048_576
        self.model_hint.setText(f"{size_mb:.0f} MB")

        if profile:
            # Apply settings — block signals to avoid cascade with style combo
            self.cfg_slider.blockSignals(True)
            self.steps_slider.blockSignals(True)

            self.cfg_slider.setValue(profile["cfg"])
            self.cfg_val.setText(str(profile["cfg"]))
            self.steps_slider.setValue(profile["steps"])
            self.steps_val.setText(str(profile["steps"]))

            self.cfg_slider.blockSignals(False)
            self.steps_slider.blockSignals(False)

            # Set sampler
            idx_s = self.sampler_combo.findText(profile["sampler"])
            if idx_s >= 0:
                self.sampler_combo.setCurrentIndex(idx_s)

            self.model_note.setText(profile["note"])
        else:
            self.model_note.setText("Unknown model — settings unchanged")

    # ── Public accessors ──────────────────────────────────────────────────────

    @property
    def model_path(self) -> Path:
        idx = self.model_combo.currentIndex()
        if self._model_paths and 0 <= idx < len(self._model_paths):
            return self._model_paths[idx]
        # Fallback: original default
        return SD_MODELS_DIR / "v1-5-pruned-emaonly.safetensors"

    @property
    def atelier(self) -> str:
        return self.atelier_combo.currentText()

    @property
    def style_key(self) -> str:
        return self.style_combo.currentText()

    @property
    def cfg(self) -> int:
        return self.cfg_slider.value()

    @property
    def steps(self) -> int:
        return self.steps_slider.value()

    @property
    def sampler(self) -> str:
        return self.sampler_combo.currentText()

    @property
    def resolution(self) -> tuple[int, int]:
        text = self.res_combo.currentText()
        w, h = text.replace("×", "x").split("x")
        return int(w), int(h)

    # ── Slide animation ───────────────────────────────────────────────────────

    def slide_in(self):
        if self._visible:
            return
        self._visible = True
        self._animate(0, PANEL_WIDTH)

    def slide_out(self):
        if not self._visible:
            return
        self._visible = False
        self._animate(PANEL_WIDTH, 0)

    def toggle(self):
        if self._visible:
            self.slide_out()
        else:
            self.slide_in()

    def _animate(self, start_w: int, end_w: int):
        anim = QPropertyAnimation(self, b"maximumWidth", self)
        anim.setDuration(220)
        anim.setStartValue(start_w)
        anim.setEndValue(end_w)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class MythotexApp(QMainWindow):

    def __init__(self):
        super().__init__()
        _ensure_dirs()
        self.setWindowTitle("Mythotex — Arca Cognitarium")
        self.setMinimumSize(1100, 720)
        self._worker = None
        self._current_lore = {}
        self._current_image = ""
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Control Panel ────────────────────────────────────────────────────
        self.panel = ControlPanel(central)
        self.panel.setMaximumWidth(0)  # start collapsed
        self.panel.btn_vault.clicked.connect(self._open_tome)
        root.addWidget(self.panel)

        # ── Main Content ─────────────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet(f"background: {C_BG};")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(0)
        root.addWidget(content, stretch=1)

        # Top bar
        content_lay.addWidget(self._build_topbar())

        # Body: image left, lore right
        body = QHBoxLayout()
        body.setContentsMargins(16, 16, 16, 16)
        body.setSpacing(16)
        content_lay.addLayout(body, stretch=1)

        body.addWidget(self._build_image_pane(), stretch=0)
        body.addWidget(self._build_lore_pane(), stretch=1)

        # Status bar
        content_lay.addWidget(self._build_statusbar())

    # ── Top bar ───────────────────────────────────────────────────────────────

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setFixedHeight(52)
        bar.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border-bottom: 1px solid {C_GOLD_DARK};
            }}
        """)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 0, 14, 0)

        self.btn_panel = QPushButton("☰")
        self.btn_panel.setFixedSize(36, 36)
        self.btn_panel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C_GOLD};
                border: 1px solid {C_GOLD_DARK};
                font-size: 18px;
            }}
            QPushButton:hover {{ background: {C_GOLD_DARK}; }}
        """)
        self.btn_panel.setToolTip("Toggle control panel")
        self.btn_panel.clicked.connect(self.panel.toggle)
        lay.addWidget(self.btn_panel)

        lay.addSpacing(12)

        title = gold_label("✦  M Y T H O T E X  ✦", 15, bold=True)
        lay.addWidget(title)

        lay.addStretch()

        self.btn_generate = arcane_button("⚗  Manifest Artifact", C_GOLD)
        self.btn_generate.setFixedHeight(34)
        self.btn_generate.clicked.connect(self._start_generation)
        lay.addWidget(self.btn_generate)

        lay.addSpacing(8)

        self.btn_seal = arcane_button("🜲  Seal to Vault", C_TEAL)
        self.btn_seal.setFixedHeight(34)
        self.btn_seal.setEnabled(False)
        self.btn_seal.clicked.connect(self._seal_to_vault)
        lay.addWidget(self.btn_seal)

        lay.addSpacing(8)

        self.btn_discard = arcane_button("✕  Discard", C_CRIMSON)
        self.btn_discard.setFixedHeight(34)
        self.btn_discard.setEnabled(False)
        self.btn_discard.clicked.connect(self._discard_artifact)
        lay.addWidget(self.btn_discard)

        return bar

    # ── Image pane ────────────────────────────────────────────────────────────

    def _build_image_pane(self) -> QWidget:
        pane = QFrame()
        pane.setFixedWidth(530)
        pane.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border: 1px solid {C_GOLD_DARK};
            }}
        """)
        lay = QVBoxLayout(pane)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)

        lbl = dim_label("Manifestation")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl)

        self.img_scroll = QScrollArea()
        self.img_scroll.setWidgetResizable(False)
        self.img_scroll.setFixedSize(504, 504)
        self.img_scroll.setStyleSheet(f"background: {C_BG}; border: 1px solid {C_SUBTLE};")
        self.img_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setFixedSize(504, 504)
        self.img_label.setStyleSheet(f"background: {C_BG}; color: {C_GOLD_DIM}; font-size: 11px;")
        self.img_label.setText("Awaiting manifestation…")
        self.img_scroll.setWidget(self.img_label)
        lay.addWidget(self.img_scroll, alignment=Qt.AlignmentFlag.AlignCenter)

        # Progress bar — hidden until generation starts
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {C_SUBTLE};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {C_GOLD};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.hide()
        lay.addWidget(self.progress_bar)

        return pane

    # ── Lore pane ─────────────────────────────────────────────────────────────

    def _build_lore_pane(self) -> QWidget:
        pane = QFrame()
        pane.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border: 1px solid {C_GOLD_DARK};
            }}
        """)
        lay = QVBoxLayout(pane)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(12)

        # Title
        self.lore_title = QLabel("—")
        self.lore_title.setWordWrap(True)
        self.lore_title.setStyleSheet(
            f"color: {C_GOLD}; font-family: Georgia, serif; font-size: 18px; "
            f"font-weight: bold; background: transparent;"
        )
        lay.addWidget(self.lore_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C_GOLD_DARK};")
        lay.addWidget(sep)

        # Fields
        for attr, label in [
            ("lore_desc",    "Description"),
            ("lore_history", "History"),
            ("lore_aura",    "Aura"),
        ]:
            row_lbl = dim_label(label.upper())
            row_lbl.setStyleSheet(
                f"color: {C_GOLD_DIM}; font-size: 9px; letter-spacing: 2px; "
                f"font-family: Georgia, serif; background: transparent;"
            )
            lay.addWidget(row_lbl)

            field = QTextEdit()
            field.setReadOnly(True)
            field.setStyleSheet(f"""
                QTextEdit {{
                    background: {C_BG};
                    color: {C_TEXT};
                    border: 1px solid {C_SUBTLE};
                    font-family: Georgia, serif;
                    font-size: 11px;
                    padding: 6px;
                }}
            """)
            if attr == "lore_desc":
                field.setFixedHeight(56)
            elif attr == "lore_history":
                field.setFixedHeight(100)
            else:
                field.setFixedHeight(56)
            setattr(self, attr, field)
            lay.addWidget(field)

        # Visual keywords
        kw_lbl = dim_label("VISUAL KEYWORDS")
        kw_lbl.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-size: 9px; letter-spacing: 2px; "
            f"font-family: Georgia, serif; background: transparent;"
        )
        lay.addWidget(kw_lbl)

        self.lore_keywords = QLabel("—")
        self.lore_keywords.setWordWrap(True)
        self.lore_keywords.setStyleSheet(
            f"color: {C_TEAL}; font-family: Georgia, serif; font-size: 10px; "
            f"background: {C_BG}; border: 1px solid {C_SUBTLE}; padding: 6px;"
        )
        lay.addWidget(self.lore_keywords)

        lay.addStretch()
        return pane

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_statusbar(self) -> QWidget:
        bar = QFrame()
        bar.setFixedHeight(28)
        bar.setStyleSheet(f"""
            QFrame {{
                background: {C_PANEL};
                border-top: 1px solid {C_GOLD_DARK};
            }}
        """)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 0, 14, 0)

        self.status_lbl = dim_label("The Arca Cognitarium awaits your command.")
        lay.addWidget(self.status_lbl)
        lay.addStretch()

        self.atelier_status = dim_label("")
        lay.addWidget(self.atelier_status)

        return bar

    # ── Generation ────────────────────────────────────────────────────────────

    def _start_generation(self):
        if self._worker and self._worker.isRunning():
            return

        atelier    = self.panel.atelier
        style_key  = self.panel.style_key
        cfg        = self.panel.cfg
        steps      = self.panel.steps
        sampler    = self.panel.sampler
        w, h       = self.panel.resolution
        model_path = self.panel.model_path

        self.btn_generate.setEnabled(False)
        self.btn_seal.setEnabled(False)
        self.btn_discard.setEnabled(False)
        self.img_label.setText("⚗  Manifesting…")
        self.atelier_status.setText(atelier)
        self._clear_lore_fields()
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        self._worker = MythotexWorker(
            atelier, style_key, cfg, steps, sampler, w, h, model_path, self
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.step_progress.connect(self._on_step_progress)
        self._worker.finished.connect(self._on_done)
        self._worker.errored.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, msg: str):
        self.status_lbl.setText(msg)

    def _on_step_progress(self, current: int, total: int):
        if total > 0:
            pct = int((current / total) * 100)
            self.progress_bar.setValue(pct)
            self.status_lbl.setText(f"⚗  Sampling… step {current} / {total}")

    def _on_done(self, lore: dict, image_path: str):
        self._current_lore  = lore
        self._current_image = image_path

        # ── Lore fields ──────────────────────────────────────────────────────
        self.lore_title.setText(lore.get("title", "Unknown Artifact"))
        self.lore_desc.setPlainText(lore.get("description", ""))
        self.lore_history.setPlainText(lore.get("history", ""))
        self.lore_aura.setPlainText(lore.get("aura", ""))
        kws = lore.get("visual_keywords", [])
        self.lore_keywords.setText("  ·  ".join(kws))

        # ── Image — fixed display pipeline ───────────────────────────────────
        DISPLAY_MAX = 504

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                QSize(DISPLAY_MAX, DISPLAY_MAX),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            dpr = self.devicePixelRatioF()
            pixmap.setDevicePixelRatio(dpr)
            self.img_label.setPixmap(pixmap)
            self.img_label.setFixedSize(
                int(pixmap.width()  / dpr),
                int(pixmap.height() / dpr),
            )
        else:
            self.img_label.setText("[ Image unavailable ]")

        self.img_scroll.setFixedSize(DISPLAY_MAX + 4, DISPLAY_MAX + 4)
        self.img_scroll.setWidgetResizable(False)

        # ── Controls ─────────────────────────────────────────────────────────
        self.btn_generate.setEnabled(True)
        self.btn_seal.setEnabled(True)
        self.btn_discard.setEnabled(True)
        self.progress_bar.hide()
        self.status_lbl.setText(f"✦  Artifact manifested: {lore.get('title', '?')}")

    def _on_error(self, err: str):
        self.btn_generate.setEnabled(True)
        self.btn_seal.setEnabled(False)
        self.btn_discard.setEnabled(False)
        self.progress_bar.hide()
        self.status_lbl.setText(f"✕  Error: {err[:120]}")
        self.img_label.setText("Generation failed.\nCheck status bar.")

    # ── Vault operations ──────────────────────────────────────────────────────

    def _seal_to_vault(self):
        if not self._current_lore:
            return

        ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r"[^\w\-]", "_", self._current_lore.get("title", "artifact"))
        entry_dir = VAULT_DIR / f"{ts}_{safe_name}"
        entry_dir.mkdir(parents=True, exist_ok=True)

        meta = {
            **self._current_lore,
            "atelier":    self.panel.atelier,
            "style":      self.panel.style_key,
            "sealed_at":  datetime.now().isoformat(),
            "rating":     None,
        }
        (entry_dir / "meta.json").write_text(json.dumps(meta, indent=2))

        if self._current_image and Path(self._current_image).exists():
            shutil.copy2(self._current_image, entry_dir / "artifact.png")

        self.btn_seal.setEnabled(False)
        self.btn_discard.setEnabled(False)
        self.status_lbl.setText(f"🜲  Sealed: {meta['title']}")

    def _discard_artifact(self):
        self._current_lore  = {}
        self._current_image = ""
        self._clear_lore_fields()
        self.img_label.clear()
        self.img_label.setText("Awaiting manifestation…")
        self.btn_seal.setEnabled(False)
        self.btn_discard.setEnabled(False)
        self.status_lbl.setText("Artifact discarded.")

    def _clear_lore_fields(self):
        self.lore_title.setText("—")
        self.lore_desc.clear()
        self.lore_history.clear()
        self.lore_aura.clear()
        self.lore_keywords.setText("—")

    def _open_tome(self):
        dlg = CompendiumTome(self)
        dlg.exec()


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)

    # Prefer serif font if available
    for fname in ["Constantia", "Georgia"]:
        fid = QFontDatabase.families()
        if fname in fid:
            app.setFont(QFont(fname, 10))
            break

    window = MythotexApp()
    window.show()
    sys.exit(app.exec())
