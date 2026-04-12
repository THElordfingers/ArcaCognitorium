#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ███████╗ ██████╗ ██████╗ ███╗   ██╗ █████╗ ██╗  ██╗       ▍
🮈  ██╔════╝██╔═══██╗██╔══██╗████╗  ██║██╔══██╗╚██╗██╔╝       ▍
🮈  █████╗  ██║   ██║██████╔╝██╔██╗ ██║███████║ ╚███╔╝        ▍
🮈  ██╔══╝  ██║   ██║██╔══██╗██║╚██╗██║██╔══██║ ██╔██╗        ▍
🮈  ██║     ╚██████╔╝██║  ██║██║ ╚████║██║  ██║██╔╝ ██╗       ▍
🮈  ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝       ▍
🮈    E N T I U M  ·  F o r g e  &  V a u l t   v 1 . 0       ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                     ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                      FornaxEntium.py    ⯩
# ⯨                                                                     ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
#
# FornaxEntium v1.0
# Arca Cognitorium — Entity Forge & Vault
#
# TAB 1: FORNAX — One button. Everything generates. Card populates live.
#   Left:  menu panel (sliders, model, options, FORGE button)
#   Right: entity card (name, portrait, details)
#   No visible pipeline. No approve/ratify steps.
#   Sequence fires silently: GENERATIO → NOMEN → ELABORATIO (portrait)
#
# TAB 2: ENTIUM — Vault browser.
#   Browse saved entity cards. Rate each aspect (name, portrait, lore blocks).
#   Add comments. Send ratings to Analytica for feedback.
#
# Three ClaudeBox instances:
#   _gen_box      — GENERATIO_SYSTEM (entity + DA prompt in one call)
#   _nomen_box    — NOMEN_SYSTEM (invents The X name, avoids used names)
#   _analysis_box — ANALYTICA_SYSTEM (receives ratings + comments, responds)
# ─────────────────────────────────────────────────────────────────────────────

import os
import re
import sys
import json
import uuid
import time
import base64
import shutil
import random
import logging
import threading
from datetime import datetime
from pathlib import Path

from nuntius_emit import emit_event

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import (
    QColor, QTextCharFormat, QSyntaxHighlighter,
    QKeySequence, QShortcut, QPixmap, QFont, QFontDatabase,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel,
    QPushButton, QComboBox, QSlider, QScrollArea,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QPlainTextEdit, QLineEdit,
    QProgressBar, QSplitter, QTabWidget,
    QListWidget, QListWidgetItem,
    QButtonGroup, QRadioButton,
    QStatusBar, QMessageBox, QCheckBox, QSpinBox,
)

# ─────────────────────────────────────────────────────────────────────────────
# Path setup
# ─────────────────────────────────────────────────────────────────────────────

_ARCA_DIR = Path.home() / 'ArcaCognitorium'
_ENTITEX  = _ARCA_DIR / 'Exocognii' / 'Entitex'
_DA_DIR   = _ENTITEX / 'Referentia' / 'Prompts' / 'DevotedAbsurd-PromptGen'
_HERE     = Path(__file__).parent

for _p in [str(_ARCA_DIR), str(_ENTITEX), str(_DA_DIR), str(_HERE)]:
    sys.path.insert(0, _p)

from claudebox import ClaudeBox
import data_pools as dp
import learning_engine

from Disposition_sliders import (
    DISPOSITION_LABELS, REGISTER_LABELS, PRESENCE_LABELS,
    OPACITY_LABELS, STABILITY_LABELS,
)
from disposition_axes import TEMPORALITY_LABELS, LEGIBILITY_LABELS
from Entitex import (
    ASPECT_RATIO_NAMES, ASPECT_RATIO_VALUES,
    FreepikAPIError, FreepikTimeoutError,
    _fp_post, _fp_fetch_image,
    _fp_extract_base64, _fp_extract_url, _fp_poll,
)

# ─────────────────────────────────────────────────────────────────────────────
# FREEPIK MODELS — complete list
# tuple: (id, display_name, post_endpoint, task_endpoint, is_sync)
# All async models use GET {post_endpoint}/{task_id} for polling.
# ─────────────────────────────────────────────────────────────────────────────

# Paths only — _fp_post prepends FREEPIK_API_BASE = https://api.freepik.com/v1
# tuple: (id, display_name, post_path, task_path_template, is_sync)
FREEPIK_MODELS = [
    ('mystic',           'Mystic',              '/ai/mystic',                              '/ai/mystic/{task_id}',                              False),
    ('flux_kontext_pro', 'Flux Kontext Pro',    '/ai/text-to-image/flux-kontext-pro',      '/ai/text-to-image/flux-kontext-pro/{task_id}',      False),
    ('flux_2_pro',       'Flux 2 Pro',          '/ai/text-to-image/flux-2-pro',            '/ai/text-to-image/flux-2-pro/{task_id}',            False),
    ('flux_2_turbo',     'Flux 2 Turbo',        '/ai/text-to-image/flux-2-turbo',          '/ai/text-to-image/flux-2-turbo/{task_id}',          False),
    ('flux_2_klein',     'Flux 2 Klein',        '/ai/text-to-image/flux-2-klein',          '/ai/text-to-image/flux-2-klein/{task_id}',          False),
    ('flux_pro_v1_1',    'Flux Pro 1.1',        '/ai/text-to-image/flux-pro-v1-1',         '/ai/text-to-image/flux-pro-v1-1/{task_id}',         False),
    ('flux_dev',         'Flux Dev',            '/ai/text-to-image/flux-dev',              '/ai/text-to-image/flux-dev/{task_id}',              False),
    ('hyperflux',        'Hyperflux',           '/ai/text-to-image/hyperflux',             '/ai/text-to-image/hyperflux/{task_id}',             False),
    ('classic_fast',     'Classic Fast (sync)', '/ai/text-to-image',                       None,                                                True),
]

FREEPIK_MODEL_IDS   = [m[0] for m in FREEPIK_MODELS]
FREEPIK_MODEL_NAMES = [m[1] for m in FREEPIK_MODELS]

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR        = _ARCA_DIR / 'Exocognii' / 'EntitexRefined'
VAULT_DIR       = BASE_DIR / 'vault'
TEMP_DIR        = BASE_DIR / 'temp_portraits'
LOG_PATH        = BASE_DIR / 'fornax_log.json'
USED_NAMES_PATH = BASE_DIR / 'used_names.json'

FREEPIK_API_KEY = os.environ.get('FREEPIK_API_KEY', '')
DEFAULTS_PATH   = Path.home() / '.arca' / 'fornax_defaults.json'

def _load_defaults() -> dict:
    try:
        if DEFAULTS_PATH.exists():
            return json.loads(DEFAULTS_PATH.read_text())
    except Exception:
        pass
    return {}

def _save_defaults(d: dict):
    DEFAULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULTS_PATH.write_text(json.dumps(d, indent=2))

# ─────────────────────────────────────────────────────────────────────────────
# PALETTE  (DA dark register)
# ─────────────────────────────────────────────────────────────────────────────

C = {
    'bg':        '#0e0f0c',
    'panel':     '#161810',
    'panel2':    '#1a1c14',
    'border':    '#333530',
    'green':     '#4a7c3f',
    'green_b':   '#7ab648',
    'amber':     '#c8a84b',
    'muted':     '#7a7f6e',
    'text':      '#d4d8c8',
    'text_dim':  '#9a9f8e',
    'red':       '#a04040',
    'teal':      '#3a7070',
    'teal_b':    '#5ab8b8',
    'highlight': '#2a3028',
    'gold_dim':  '#7a6a2a',
    'card_bg':   '#0b0d09',
}

SS = f"""
QMainWindow, QWidget {{
    background: {C['bg']}; color: {C['text']};
    font-family: "IBM Plex Mono", "Courier New", monospace; font-size: 12px;
}}
QTabWidget::pane {{ border: 1px solid {C['border']}; background: {C['panel']}; }}
QTabBar::tab {{
    background: {C['bg']}; color: {C['muted']};
    padding: 8px 22px; border: 1px solid {C['border']}; border-bottom: none;
    font-size: 11px; letter-spacing: 2px;
}}
QTabBar::tab:selected {{ background: {C['panel']}; color: {C['green_b']}; border-bottom: 2px solid {C['green']}; }}
QLineEdit, QTextEdit, QComboBox, QPlainTextEdit {{
    background: {C['panel2']}; border: 1px solid {C['border']}; color: {C['text']};
    padding: 5px 8px; font-family: "IBM Plex Mono", "Courier New", monospace; font-size: 11px;
    selection-background-color: {C['green']};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{ border: 1px solid {C['green']}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox::down-arrow {{
    width: 8px; height: 8px; border-left: 4px solid transparent;
    border-right: 4px solid transparent; border-top: 6px solid {C['muted']}; margin-right: 4px;
}}
QComboBox QAbstractItemView {{
    background: {C['panel']}; border: 1px solid {C['border']}; color: {C['text']};
    selection-background-color: {C['green']};
}}
QPushButton {{
    background: transparent; border: 1px solid {C['border']}; color: {C['muted']};
    padding: 6px 14px; font-family: "IBM Plex Mono", "Courier New", monospace;
    font-size: 11px; letter-spacing: 1px;
}}
QPushButton:hover {{ border-color: {C['green']}; color: {C['green_b']}; }}
QPushButton:pressed {{ background: {C['highlight']}; }}
QPushButton:disabled {{ color: {C['gold_dim']}; border-color: {C['border']}; }}
QPushButton#btn_forge {{
    border-color: {C['green']}; color: {C['green_b']};
    font-size: 14px; letter-spacing: 3px; padding: 12px 28px; font-weight: bold;
}}
QPushButton#btn_forge:hover {{ background: rgba(74,124,63,0.2); }}
QPushButton#btn_random {{ border-color: {C['amber']}; color: {C['amber']}; }}
QPushButton#btn_random:hover {{ background: rgba(200,168,75,0.15); }}
QPushButton#btn_teal {{ border-color: {C['teal']}; color: {C['teal_b']}; }}
QPushButton#btn_teal:hover {{ background: rgba(58,112,112,0.2); }}
QSlider::groove:horizontal {{ height: 3px; background: {C['border']}; }}
QSlider::handle:horizontal {{
    width: 14px; height: 14px; margin: -6px 0; border-radius: 7px; background: {C['green_b']};
}}
QSlider::sub-page:horizontal {{ background: {C['green']}; }}
QScrollBar:vertical {{ background: {C['bg']}; width: 8px; border: none; }}
QScrollBar::handle:vertical {{ background: {C['border']}; border-radius: 4px; min-height: 20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 8px; background: {C['bg']}; border: none; }}
QScrollBar::handle:horizontal {{ background: {C['border']}; border-radius: 4px; }}
QProgressBar {{
    border: 1px solid {C['border']}; background: {C['panel']};
    color: {C['green_b']}; text-align: center; font-size: 10px;
}}
QProgressBar::chunk {{ background: {C['green']}; }}
QListWidget {{
    background: {C['panel']}; border: 1px solid {C['border']}; color: {C['text']}; font-size: 11px;
}}
QListWidget::item {{ padding: 6px 10px; border-bottom: 1px solid {C['border']}; }}
QListWidget::item:selected {{ background: {C['highlight']}; color: {C['green_b']}; }}
QStatusBar {{
    background: {C['panel']}; color: {C['muted']};
    border-top: 1px solid {C['border']}; font-size: 10px; letter-spacing: 1px;
}}
QSplitter::handle {{ background: {C['border']}; }}
QCheckBox {{
    color: {C['text_dim']}; background: transparent; font-size: 11px;
}}
QCheckBox::indicator {{
    width: 13px; height: 13px; border: 1px solid {C['border']}; background: {C['bg']};
}}
QCheckBox::indicator:checked {{ background: {C['green']}; border-color: {C['green_b']}; }}
QLabel#slbl {{
    color: {C['amber']}; font-size: 10px; letter-spacing: 2px;
    padding-bottom: 3px; border-bottom: 1px solid {C['border']};
}}
QLabel#entity_name {{
    color: {C['green_b']}; font-size: 32px; font-weight: bold;
    letter-spacing: 6px; background: transparent;
    font-family: "Cinzel", "Palatino Linotype", Georgia, serif;
}}
QLabel#entity_title {{
    color: {C['amber']}; font-size: 12px; letter-spacing: 3px; background: transparent;
    font-family: "IBM Plex Mono", "Courier New", monospace;
}}
QLabel#card_field_label {{
    color: {C['gold_dim']}; font-size: 9px; letter-spacing: 2px; background: transparent;
}}
QLabel#card_field_value {{
    color: {C['text']}; font-size: 11px; background: transparent;
}}
QSpinBox {{
    background: {C['panel2']}; border: 1px solid {C['border']}; color: {C['amber']};
    padding: 3px 6px; font-size: 12px; min-width: 50px;
}}
"""

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

GENERATIO_SYSTEM = f"""You are Entitex Generatio — entity forge for the Arca Cognitorium.

You generate a complete entity in one response:
1. A full Devoted Absurd style image generation prompt (assembled_prompt)
2. A Cogniverse entity lore profile
3. A "The X" style name for the entity

── LOCKED VISUAL STYLE ──────────────────────────────────────────────────────
{dp.STYLE_DNA}

Palette: muted, heavily desaturated, dark only. Near-blacks, coal, soot, dark industrials, aged organics, bruised tones. NO pastels. NO bright primaries. NO light backgrounds. Sparse highlights only.

── SETTING ──────────────────────────────────────────────────────────────────
Medieval dark-ages world with crude pseudo-mechanical technology. Not steampunk, not modern, not Victorian. Bellows, gears, waterwheel machinery, hand-cranked devices, alchemical apparatus.

── ENTITY REGISTER ──────────────────────────────────────────────────────────
This entity exists within the Arca Cognitorium. It is a presence, not a person. It carries institutional permanence. Purpose: second-person present tense. Lore: third person. Nothing soft or explanatory.

── NAMING ───────────────────────────────────────────────────────────────────
Generate a name following the "The [Word]" convention. The noun is a role, disposition, function, or quality. It must feel earned by the specific profile. Register draws from: analytical functions, temperamental states, creative roles, institutional titles, liminal states, adversarial positions. Invent freely — do not copy stock examples.

── INPUT ────────────────────────────────────────────────────────────────────
Disposition directives only. No archetype label provided. Generate everything from the disposition space.
An archetype vocabulary block may follow as tonal reference — synthesise freely.

── OUTPUT ───────────────────────────────────────────────────────────────────
Respond ONLY with a single raw JSON object. No markdown. No preamble.

{{
  "display_name": "<The [Word] — the entity's full name>",
  "role": "<specific invented title — medieval register, not modern>",
  "personality": "<2-3 sentences of specific character texture>",
  "garment": "<specific clothing with fabric, cut, condition, worn details>",
  "prop": "<one specific carried object with condition detail>",
  "detail": "<one small telling physical or clothing detail>",
  "mood": "<expression and bearing — specific, not an emotion word>",
  "posture": "<body language and stance>",
  "body_type": "<build description>",
  "age": "<age range with one sentence on what it means for this entity>",
  "era_blend": "<how this entity sits in the medieval-mechanical world>",
  "palette": "<3-4 specific dark colours — all anchored in shadow register>",
  "background": "<one flat near-black or deep dark colour — never light>",
  "assembled_prompt": "<full image generation prompt, one continuous string>",
  "title": "<two-to-five word epithet — the thing this entity is called>",
  "color_hex": "<hex colour for this entity, no #>",
  "glyph": "<single Unicode character as sigil>",
  "purpose": "<3-6 sentences second-person present tense. Spare, declarative.>",
  "domain_keywords": ["<3-6 keywords>"],
  "lore_origin": "<2-3 sentences. Third person, past tense.>",
  "lore_nature": "<2-3 sentences. Ontological. Third person, present tense.>",
  "lore_relationship": "<1-2 sentences: bond or tension with the Wizard.>",
  "lore_aura": "<One sentence: what does it feel like when this entity is present?>",
  "traits": {{
    "verbosity": 0.0, "challenge": 0.0, "speculation": 0.0,
    "structure": 0.0, "warmth": 0.0, "precision": 0.0
  }}
}}

assembled_prompt: open with full style DNA, state medieval-mechanical setting, weave all character elements into one paragraph, end with strict palette note naming dark colours, specify dark background, include entity title and aura. This is sent directly to Freepik.

JSON hygiene: every string on one line. No literal newlines inside strings. No trailing commas."""


ANALYTICA_SYSTEM = """You are Entitex Analytica — senior reviewer for the Arca Cognitorium.

You receive a completed entity profile along with ratings and comments from the Wizard about specific aspects.
Each aspect has a star rating (1-5) and an optional comment.

Aspects rated:
- display_name: the entity's "The X" name
- portrait: the generated image
- purpose: the entity's directive text
- lore_origin / lore_nature / lore_relationship / lore_aura: lore blocks
- traits: trait calibration

Your job:
1. Read all ratings and comments carefully
2. Identify what is working and what is not, per aspect
3. Produce a synthesis verdict in Cogniverse register — speak as the Tower
4. Produce specific refinement recommendations for each low-rated aspect
5. Suggest one focused regeneration directive: what single change would most improve the next generation

Respond ONLY with a raw JSON object:
{
  "verdict": "<3-5 sentences in Cogniverse lore register — the Tower's assessment>",
  "aspect_notes": {
    "display_name": "<note on the name, if rated>",
    "portrait": "<note on the portrait, if rated>",
    "purpose": "<note on the purpose text, if rated>",
    "lore": "<note on lore blocks collectively, if rated>",
    "traits": "<note on trait calibration, if rated>"
  },
  "regen_directive": "<one focused instruction for the next generation — what to change>"
}

No preamble. No markdown. No fences."""

# ─────────────────────────────────────────────────────────────────────────────
# ClaudeBox instances
# ─────────────────────────────────────────────────────────────────────────────

_api_key = os.environ.get('CLAUDE_API_KEY')

_gen_box      = ClaudeBox(api_key=_api_key, system_prompt=GENERATIO_SYSTEM, stream=False)
_analysis_box = ClaudeBox(api_key=_api_key, system_prompt=ANALYTICA_SYSTEM, stream=False)

_gen_lock = threading.Lock()
_ana_lock = threading.Lock()

# ─────────────────────────────────────────────────────────────────────────────
# USED NAMES
# ─────────────────────────────────────────────────────────────────────────────

def _load_used_names():
    try:
        if USED_NAMES_PATH.exists():
            return json.loads(USED_NAMES_PATH.read_text())
    except Exception:
        pass
    return []

def _save_used_name(name):
    names = _load_used_names()
    if name not in names:
        names.append(name)
        USED_NAMES_PATH.write_text(json.dumps(names, indent=2))

# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _parse_json(raw):
    original = raw
    text = raw.strip()
    if text.startswith('```'):
        text = text.split('```')[1]
        if text.startswith('json'): text = text[4:]
        text = text.strip()
    b0, b1 = text.find('{'), text.rfind('}')
    if b0 != -1 and b1 > b0: text = text[b0:b1+1]
    first_err = None
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        first_err = e
    def _repair(s):
        out, in_s, esc = [], False, False
        for ch in s:
            if esc: out.append(ch); esc = False
            elif ch == '\\' and in_s: out.append(ch); esc = True
            elif ch == '"': out.append(ch); in_s = not in_s
            elif ch in ('\n', '\r') and in_s: out.append(' ')
            else: out.append(ch)
        return ''.join(out)
    rep = re.sub(r',\s*([}\]])', r'\1', _repair(text))
    try:
        return json.loads(rep)
    except json.JSONDecodeError as e2:
        raise ValueError(
            f'JSON parse failed.\nOriginal: {first_err}\nRepair: {e2}\n'
            f'Snippet: {original[:200].replace(chr(10),"↵")}'
        ) from e2

def _inclinatio_str(inc):
    return '\n'.join([
        f"Disposition toward the Wizard: {DISPOSITION_LABELS[inc.get('disposition',1)]}",
        f"Communication Register: {REGISTER_LABELS[inc.get('register',1)]}",
        f"Presence Weight: {PRESENCE_LABELS[inc.get('presence',1)]}",
        f"Self-Opacity: {OPACITY_LABELS[inc.get('opacity',1)]}",
        f"Psychological Stability: {STABILITY_LABELS[inc.get('stability',0)]}",
        f"Temporal Orientation: {TEMPORALITY_LABELS[inc.get('temporality',0)]}",
        f"Legibility: {LEGIBILITY_LABELS[inc.get('legibility',0)]}",
    ])

def _ensure_dirs():
    for d in [BASE_DIR, VAULT_DIR, TEMP_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists(): LOG_PATH.write_text(json.dumps([], indent=2))
    if not USED_NAMES_PATH.exists(): USED_NAMES_PATH.write_text(json.dumps([], indent=2))

def _vault_save(entity, portrait_path=None):
    """Save entity to vault. Returns the vault entry directory."""
    entity_id = entity.get('entity_id', f"entity_{int(time.time())}")
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = re.sub(r'\W+', '_', entity.get('display_name', 'unnamed').lower())
    d = VAULT_DIR / f'{ts}_{slug}'
    d.mkdir(parents=True, exist_ok=True)
    save_data = {**entity, 'saved_at': datetime.now().isoformat(), 'vault_dir': str(d)}
    (d / 'entity.json').write_text(json.dumps(save_data, indent=2))
    if portrait_path and Path(portrait_path).exists():
        shutil.copy2(portrait_path, d / 'portrait.png')
    return d

def _load_vault_entries():
    """Return list of (dir_path, entity_dict) sorted newest first."""
    entries = []
    if not VAULT_DIR.exists():
        return entries
    for d in sorted(VAULT_DIR.iterdir(), reverse=True):
        if d.is_dir() and (d / 'entity.json').exists():
            try:
                entity = json.loads((d / 'entity.json').read_text())
                entries.append((d, entity))
            except Exception:
                pass
    return entries

def _save_ratings(vault_dir, ratings):
    """Save ratings dict to vault entry."""
    path = Path(vault_dir) / 'ratings.json'
    path.write_text(json.dumps(ratings, indent=2))

def _load_ratings(vault_dir):
    """Load ratings dict from vault entry."""
    path = Path(vault_dir) / 'ratings.json'
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {}

# ─────────────────────────────────────────────────────────────────────────────
# WORKERS
# ─────────────────────────────────────────────────────────────────────────────

class GeneratioWorker(QThread):
    """Generates complete entity + name in a single Claude call."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    errored  = pyqtSignal(str)

    def __init__(self, inc, archetype_key='random', overrides=None, used_names=None, parent=None):
        super().__init__(parent)
        self.inc = inc
        self.archetype_key = archetype_key
        self.overrides = overrides or {}
        self.used_names = used_names or []

    def run(self):
        try:
            self.progress.emit('⚗  Consulting the Generatio forge…')
            vocab = ''
            if self.archetype_key and self.archetype_key != 'random':
                v = dp.get_archetype_vocabulary(self.archetype_key)
                if v:
                    vocab = (
                        '\n\n── ARCHETYPE VOCABULARY REFERENCE ──────────────────────\n'
                        'Tonal reference only. Synthesise freely — do not copy.\n\n' + v)
            overrides_block = ''
            if self.overrides:
                locked = [f'  {k}: {v}' for k, v in self.overrides.items() if v]
                if locked:
                    overrides_block = '\n\nLocked fields:\n' + '\n'.join(locked)
            used_block = ''
            if self.used_names:
                used_block = (
                    '\n\nNames already in use — DO NOT use these for display_name:\n'
                    + '\n'.join(f'  {n}' for n in self.used_names))

            user = (
                'Generate a complete entity specification including a name.\n\n'
                f'Disposition directives:\n{_inclinatio_str(self.inc)}'
                + vocab + overrides_block + used_block
            )
            with _gen_lock:
                response = _gen_box.send(user, max_tokens=4096)
            data = _parse_json(response.text.strip())
            # Ensure entity_id
            name = data.get('display_name', 'unnamed')
            data['entity_id'] = re.sub(r'\W+', '_', name.lower().strip())
            self.finished.emit(data)
        except Exception as exc:
            self.errored.emit(str(exc))


class PortraitWorker(QThread):
    """Generates Freepik portrait from assembled_prompt."""
    progress  = pyqtSignal(str)
    poll_tick = pyqtSignal(int, int)
    finished  = pyqtSignal(str)
    errored   = pyqtSignal(str)

    def __init__(self, prompt, model_id, aspect_ratio, seed=None, parent=None):
        super().__init__(parent)
        self.prompt       = prompt
        self.model_id     = model_id
        self.aspect_ratio = aspect_ratio
        self.seed         = seed

    def run(self):
        try:
            if not FREEPIK_API_KEY:
                raise RuntimeError('FREEPIK_API_KEY not set.')
            self.progress.emit('⚗  Submitting to Freepik…')
            img_path = self._generate()
            self.finished.emit(img_path)
        except Exception as exc:
            self.errored.emit(str(exc))

    def _generate(self):
        model_meta = next((m for m in FREEPIK_MODELS if m[0] == self.model_id), FREEPIK_MODELS[0])
        _, _, endpoint, task_endpoint, is_sync = model_meta
        payload = {'prompt': self.prompt}
        if self.seed is not None:
            payload['seed'] = self.seed

        mid = self.model_id
        ar  = self.aspect_ratio

        if mid == 'classic_fast':
            # Sync: uses image.size dict and num_images
            payload['image'] = {'size': ar}
            payload['num_images'] = 1

        elif mid == 'mystic':
            # Mystic: has its own parameters
            payload.update({
                'aspect_ratio': ar,
                'resolution': '1k',
                'model': 'realism',
                'engine': 'automatic',
                'hdr': 50,
                'adherence': 0,
                'creative_detailing': 33,
                'structure_strength': 0,
            })

        elif mid == 'flux_kontext_pro':
            # Flux Kontext Pro: aspect_ratio + guidance + steps
            payload['aspect_ratio'] = ar

        elif mid == 'flux_2_pro':
            # Flux 2 Pro: aspect_ratio, resolution
            payload['aspect_ratio'] = ar
            payload['resolution'] = '1k'

        elif mid == 'flux_2_turbo':
            # Flux 2 Turbo: aspect_ratio
            payload['aspect_ratio'] = ar

        elif mid == 'flux_2_klein':
            # Flux 2 Klein: aspect_ratio, resolution
            payload['aspect_ratio'] = ar
            payload['resolution'] = '1k'

        elif mid == 'flux_pro_v1_1':
            # Flux Pro 1.1: aspect_ratio
            payload['aspect_ratio'] = ar

        elif mid == 'flux_dev':
            # Flux Dev: aspect_ratio
            payload['aspect_ratio'] = ar

        elif mid == 'hyperflux':
            # Hyperflux: aspect_ratio
            payload['aspect_ratio'] = ar

        else:
            # Fallback: just send aspect_ratio
            payload['aspect_ratio'] = ar

        result_raw = _fp_post(endpoint, payload)

        if is_sync:
            final = result_raw
        else:
            task_id = (result_raw.get('task_id') or
                       result_raw.get('data', {}).get('task_id') or result_raw.get('id'))
            if not task_id:
                raise FreepikAPIError(0, f'No task_id in response: {result_raw}')
            self.progress.emit('⚗  Crystallising portrait…')
            final = _fp_poll(task_endpoint, str(task_id),
                             progress_cb=lambda a, m: self.poll_tick.emit(a, m))

        b64 = _fp_extract_base64(final)
        img_bytes = base64.b64decode(b64) if b64 else _fp_fetch_image(_fp_extract_url(final))
        out = TEMP_DIR / f'portrait_{int(time.time()*1000)}.png'
        out.write_bytes(img_bytes)
        return str(out)


class AnalyticaWorker(QThread):
    """Sends vault ratings + comments to Analytica."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    errored  = pyqtSignal(str)

    def __init__(self, entity, ratings, parent=None):
        super().__init__(parent)
        self.entity = entity
        self.ratings = ratings

    def run(self):
        try:
            self.progress.emit('⚗  The Analytica considers the ratings…')
            e = self.entity
            r = self.ratings

            def fmt_rating(key, label):
                stars = r.get(f'{key}_stars', 0)
                comment = r.get(f'{key}_comment', '').strip()
                if not stars and not comment:
                    return ''
                line = f'{label}: {"★" * stars}{"☆" * (5-stars)}'
                if comment:
                    line += f' — "{comment}"'
                return line

            rating_lines = [
                fmt_rating('name',     'Name'),
                fmt_rating('portrait', 'Portrait'),
                fmt_rating('purpose',  'Purpose'),
                fmt_rating('lore',     'Lore'),
                fmt_rating('traits',   'Traits'),
            ]
            rating_block = '\n'.join(l for l in rating_lines if l)

            content = (
                f'Review this entity based on the Wizard\'s ratings.\n\n'
                f'ENTITY:\n'
                f'Name: {e.get("display_name","")}\n'
                f'Role: {e.get("role","")}\n'
                f'Title: {e.get("title","")}\n'
                f'Purpose: {e.get("purpose","")}\n'
                f'Lore Aura: {e.get("lore_aura","")}\n'
                f'Traits: {json.dumps(e.get("traits",{}))}\n\n'
                f'WIZARD\'S RATINGS:\n{rating_block}'
            )
            with _ana_lock:
                response = _analysis_box.send(content, max_tokens=2048)
            self.finished.emit(_parse_json(response.text.strip()))
        except Exception as exc:
            self.errored.emit(str(exc))

# ─────────────────────────────────────────────────────────────────────────────
# WIDGET HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def slbl(text):
    lbl = QLabel(text.upper()); lbl.setObjectName('slbl'); return lbl

def hline():
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color:{C['border']};"); return f

def _slider_row(labels, initial=0):
    sl = QSlider(Qt.Orientation.Horizontal)
    sl.setRange(0, len(labels)-1); sl.setValue(initial)
    sl.setTickPosition(QSlider.TickPosition.TicksBelow); sl.setTickInterval(1)
    lbl = QLabel(labels[initial])
    lbl.setStyleSheet(f"color:{C['muted']};font-size:9px;")
    sl.valueChanged.connect(lambda v: lbl.setText(labels[v]))
    return sl, lbl

def star_widget(key, ratings_dict, on_change=None):
    """Returns a QWidget with a 1-5 star spinbox + comment line for one aspect."""
    w = QWidget(); w.setStyleSheet(f"background:{C['panel2']};")
    lay = QVBoxLayout(w); lay.setContentsMargins(8,6,8,6); lay.setSpacing(4)

    row = QHBoxLayout(); row.setSpacing(8)
    lbl = QLabel('★'); lbl.setStyleSheet(f"color:{C['amber']};font-size:11px;")
    spin = QSpinBox()
    spin.setRange(0, 5); spin.setValue(ratings_dict.get(f'{key}_stars', 0))
    spin.setPrefix(''); spin.setSuffix(' ★')

    comment = QLineEdit()
    comment.setPlaceholderText('Comment…')
    comment.setText(ratings_dict.get(f'{key}_comment', ''))

    row.addWidget(lbl); row.addWidget(spin); row.addWidget(comment, stretch=1)
    lay.addLayout(row)

    def _update():
        ratings_dict[f'{key}_stars'] = spin.value()
        ratings_dict[f'{key}_comment'] = comment.text().strip()
        if on_change: on_change()

    spin.valueChanged.connect(lambda _: _update())
    comment.textChanged.connect(lambda _: _update())
    return w

# ─────────────────────────────────────────────────────────────────────────────
# ENTITY CARD WIDGET
# Shared between FORNAX (live forge) and ENTIUM (vault browser)
# ─────────────────────────────────────────────────────────────────────────────

class EntityCard(QWidget):
    """
    Displays a single entity as a card.
    Layout: name + glyph at top, portrait centre, details scrollable below.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C['card_bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        # ── Name header — centred ─────────────────────────────────────────────
        name_header = QVBoxLayout()
        name_header.setSpacing(4)
        name_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        name_glyph_row = QHBoxLayout()
        name_glyph_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_glyph = QLabel('⬡')
        self.lbl_glyph.setStyleSheet(
            f"color:{C['amber']};font-size:32px;background:transparent;")
        self.lbl_glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_glyph_row.addWidget(self.lbl_glyph)

        self.lbl_name = QLabel('—')
        self.lbl_name.setObjectName('entity_name')
        self.lbl_name.setWordWrap(False)
        self.lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_title = QLabel('—')
        self.lbl_title.setObjectName('entity_title')
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_header.addLayout(name_glyph_row)
        name_header.addWidget(self.lbl_name)
        name_header.addWidget(self.lbl_title)
        lay.addLayout(name_header)

        # ── Portrait + Details: vertical QSplitter (resizable) ──────────────
        self._card_splitter = QSplitter(Qt.Orientation.Vertical)
        self._card_splitter.setHandleWidth(12)
        self._card_splitter.setStyleSheet(f"""
            QSplitter::handle:vertical {{
                background: {C['border']};
                border-top: 1px solid {C['gold_dim']};
                border-bottom: 1px solid {C['gold_dim']};
                margin: 0 40px;
                image: none;
            }}
            QSplitter::handle:vertical:hover {{
                background: {C['gold_dim']};
            }}
        """)

        # Portrait pane
        portrait_pane = QWidget()
        portrait_pane.setStyleSheet(f"background:{C['bg']};")
        pfl = QVBoxLayout(portrait_pane)
        pfl.setContentsMargins(0, 0, 0, 0)
        pfl.setSpacing(0)

        self.portrait_scroll = QScrollArea()
        self.portrait_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.portrait_scroll.setStyleSheet(
            f"QScrollArea{{background:{C['bg']};border:none;}}")

        self.portrait_label = QLabel('portrait will generate\nafter forge completes')
        self.portrait_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.portrait_label.setStyleSheet(
            f"color:{C['muted']};font-size:10px;background:{C['bg']};")
        self.portrait_scroll.setWidget(self.portrait_label)
        self.portrait_scroll.setWidgetResizable(True)
        pfl.addWidget(self.portrait_scroll)

        self.portrait_progress = QProgressBar()
        self.portrait_progress.setRange(0, 0)
        self.portrait_progress.setFixedHeight(3)
        self.portrait_progress.setTextVisible(False)
        self.portrait_progress.hide()
        pfl.addWidget(self.portrait_progress)

        self._card_splitter.addWidget(portrait_pane)

        # Details pane
        detail_scroll = QScrollArea()
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setStyleSheet(
            f"QScrollArea{{background:{C['card_bg']};border:none;}}")

        detail_content = QWidget()
        detail_content.setStyleSheet(f"background:{C['card_bg']};")
        dl = QGridLayout(detail_content)
        dl.setContentsMargins(0, 4, 0, 4)
        dl.setSpacing(6)
        dl.setColumnStretch(1, 1)

        def detail_row(row, label, attr):
            lbl = QLabel(label.upper())
            lbl.setObjectName('card_field_label')
            lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
            val = QLabel('—')
            val.setObjectName('card_field_value')
            val.setWordWrap(True)
            dl.addWidget(lbl, row, 0, Qt.AlignmentFlag.AlignTop)
            dl.addWidget(val, row, 1)
            setattr(self, attr, val)

        detail_row(0, 'Role',     'lbl_role')
        detail_row(1, 'Era',      'lbl_era')
        detail_row(2, 'Purpose',  'lbl_purpose')
        detail_row(3, 'Origin',   'lbl_origin')
        detail_row(4, 'Nature',   'lbl_nature')
        detail_row(5, 'Aura',     'lbl_aura')
        detail_row(6, 'Keywords', 'lbl_keywords')
        detail_row(7, 'Traits',   'lbl_traits')

        detail_scroll.setWidget(detail_content)
        self._card_splitter.addWidget(detail_scroll)

        # Default portrait / details split: 60% / 40%
        self._card_splitter.setSizes([380, 240])

        lay.addWidget(self._card_splitter, stretch=1)

    def populate(self, entity):
        self.lbl_name.setText(entity.get('display_name', '—'))
        self.lbl_title.setText(entity.get('title', '—'))
        self.lbl_glyph.setText(entity.get('glyph', '⬡'))
        color = entity.get('color_hex', '7ab648')
        self.lbl_glyph.setStyleSheet(f"color:#{color};font-size:32px;background:transparent;")
        # Name inherits entity colour
        self.lbl_name.setStyleSheet(
            f"color:#{color}; font-size:32px; font-weight:bold; letter-spacing:6px; "
            f"background:transparent; font-family:'Cinzel','Palatino Linotype',Georgia,serif;")
        self.lbl_role.setText(entity.get('role', '—'))
        self.lbl_era.setText(entity.get('era_blend', '—'))
        self.lbl_purpose.setText(entity.get('purpose', '—'))
        self.lbl_origin.setText(entity.get('lore_origin', '—'))
        self.lbl_nature.setText(entity.get('lore_nature', '—'))
        self.lbl_aura.setText(entity.get('lore_aura', '—'))
        self.lbl_keywords.setText('  ·  '.join(entity.get('domain_keywords', [])))
        traits = entity.get('traits', {})
        self.lbl_traits.setText('  '.join(f"{k[:3].upper()} {v:.2f}" for k, v in traits.items()))

    def set_portrait(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            # Scale to portrait pane size — use splitter first section height
            sizes = self._card_splitter.sizes()
            pane_h = sizes[0] - 4 if sizes else 360
            pane_w = self.portrait_scroll.width() - 4
            target = max(pane_h, pane_w, 200)
            pixmap = pixmap.scaled(
                QSize(target, target),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            dpr = self.portrait_label.devicePixelRatioF()
            pixmap.setDevicePixelRatio(dpr)
            self.portrait_label.setPixmap(pixmap)
            self.portrait_label.setFixedSize(int(pixmap.width()/dpr), int(pixmap.height()/dpr))
            self.portrait_scroll.setWidgetResizable(False)
        else:
            self.portrait_label.setText('[ Portrait unavailable ]')
        self.portrait_progress.hide()

    def portrait_loading(self, indeterminate=True, pct=None):
        self.portrait_progress.show()
        if indeterminate:
            self.portrait_progress.setRange(0, 0)
        elif pct is not None:
            self.portrait_progress.setRange(0, 100)
            self.portrait_progress.setValue(pct)

    def clear(self):
        self.lbl_name.setText('—'); self.lbl_title.setText('—')
        self.lbl_glyph.setText('⬡')
        self.lbl_glyph.setStyleSheet(f"color:{C['amber']};font-size:32px;background:transparent;")
        for attr in ['lbl_role','lbl_era','lbl_purpose','lbl_origin',
                     'lbl_nature','lbl_aura','lbl_keywords','lbl_traits']:
            getattr(self, attr).setText('—')
        self.portrait_label.setPixmap(QPixmap())
        self.portrait_label.setText('portrait will generate\nafter forge completes')
        self.portrait_scroll.setWidgetResizable(True)
        self.portrait_progress.hide()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: FORNAX — The Forge
# ─────────────────────────────────────────────────────────────────────────────

class FornaxTab(QWidget):
    forge_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._archetype_keys = ['random'] + list(dp.ARCHETYPES.keys())
        self._build()
        self._load_defaults()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Left menu panel ───────────────────────────────────────────────────
        menu = QWidget()
        menu.setStyleSheet(f"background:{C['panel']};")
        menu.setMinimumWidth(260)
        menu.setMaximumWidth(340)
        ml = QVBoxLayout(menu)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea{{border:none;background:{C['panel']};}}")
        ml.addWidget(scroll)

        sc = QWidget(); sc.setStyleSheet(f"background:{C['panel']};")
        scl = QVBoxLayout(sc); scl.setContentsMargins(14,14,14,14); scl.setSpacing(10)
        scroll.setWidget(sc)

        # App title
        ttl = QLabel('FORNAX  ENTIUM')
        ttl.setStyleSheet(
            f"color:{C['green_b']};font-size:14px;font-weight:bold;letter-spacing:3px;")
        sub = QLabel('Entity Forge  ·  Vault')
        sub.setStyleSheet(f"color:{C['muted']};font-size:10px;letter-spacing:1px;")
        scl.addWidget(ttl); scl.addWidget(sub); scl.addWidget(hline())

        # Tonal register
        scl.addWidget(slbl('▶ Tonal Register'))
        self.combo_arch = QComboBox()
        self.combo_arch.addItem('Random / Blind')
        for k in dp.ARCHETYPES: self.combo_arch.addItem(dp.ARCHETYPES[k]['label'])
        scl.addWidget(self.combo_arch)

        # Overrides
        scl.addWidget(slbl('▶ Overrides'))
        self.input_override = QTextEdit()
        self.input_override.setPlaceholderText('Extra notes / visual override…')
        self.input_override.setMaximumHeight(55)
        scl.addWidget(self.input_override)

        # Sliders
        scl.addWidget(slbl('▶ Inclinationes'))
        self._sliders = {}
        for label, labels, default, key in [
            ('Disposition', DISPOSITION_LABELS, 1, 'disposition'),
            ('Register',    REGISTER_LABELS,    1, 'register'),
            ('Presence',    PRESENCE_LABELS,    1, 'presence'),
            ('Opacity',     OPACITY_LABELS,     1, 'opacity'),
            ('Stability',   STABILITY_LABELS,   0, 'stability'),
            ('Temporality', TEMPORALITY_LABELS, 0, 'temporality'),
            ('Legibility',  LEGIBILITY_LABELS,  0, 'legibility'),
        ]:
            row = QHBoxLayout()
            ln = QLabel(label); ln.setStyleSheet(f"color:{C['text_dim']};font-size:10px;")
            row.addWidget(ln); row.addStretch()
            sl, lv = _slider_row(labels, default)
            self._sliders[key] = sl
            scl.addLayout(row); scl.addWidget(sl); scl.addWidget(lv); scl.addSpacing(2)

        # Portrait settings
        scl.addWidget(slbl('▶ Portrait'))
        lm = QLabel('Model'); lm.setStyleSheet(f"color:{C['text_dim']};font-size:10px;")
        scl.addWidget(lm)
        self.combo_model = QComboBox(); self.combo_model.addItems(FREEPIK_MODEL_NAMES)
        scl.addWidget(self.combo_model)
        la = QLabel('Aspect Ratio'); la.setStyleSheet(f"color:{C['text_dim']};font-size:10px;")
        scl.addWidget(la)
        self.combo_ar = QComboBox(); self.combo_ar.addItems(ASPECT_RATIO_NAMES)
        scl.addWidget(self.combo_ar)

        # Save defaults button
        scl.addWidget(hline())
        self.btn_save_defaults = QPushButton('💾  SAVE DEFAULT PORTRAIT SETTINGS')
        self.btn_save_defaults.setObjectName('btn_teal')
        scl.addWidget(self.btn_save_defaults)
        scl.addStretch()

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0); self.progress.setFixedHeight(3)
        self.progress.setTextVisible(False); self.progress.hide()
        ml.addWidget(self.progress)

        # ── Right: card + bottom action bar ──────────────────────────────────
        card_wrapper = QWidget()
        card_wrapper.setStyleSheet(f"background:{C['card_bg']};")
        cw_lay = QVBoxLayout(card_wrapper)
        cw_lay.setContentsMargins(0, 0, 0, 0)
        cw_lay.setSpacing(0)

        self.card = EntityCard()
        cw_lay.addWidget(self.card, stretch=1)

        # Bottom action bar
        action_bar = QFrame()
        action_bar.setStyleSheet(
            f"QFrame{{background:{C['panel']};border-top:1px solid {C['border']};}}")
        action_bar.setFixedHeight(52)
        abl = QHBoxLayout(action_bar)
        abl.setContentsMargins(20, 0, 20, 0)
        abl.setSpacing(12)

        self.btn_forge = QPushButton('⚗  FORGE')
        self.btn_forge.setObjectName('btn_forge')
        self.btn_forge.setMinimumHeight(38)

        self.btn_random = QPushButton('↻ RANDOM')
        self.btn_random.setObjectName('btn_random')
        self.btn_random.setFixedHeight(38)

        self.btn_copy = QPushButton('COPY PROMPT')
        self.btn_copy.setObjectName('btn_teal')
        self.btn_copy.setFixedHeight(38)
        self.btn_copy.setEnabled(False)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0); self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False); self.progress.hide()
        self.progress.setFixedWidth(160)

        self.lbl_status = QLabel('Ready')
        self.lbl_status.setStyleSheet(f"color:{C['muted']};font-size:10px;")
        self.lbl_status.setWordWrap(False)

        abl.addWidget(self.btn_forge)
        abl.addWidget(self.btn_random)
        abl.addWidget(self.btn_copy)
        abl.addWidget(self.progress)
        abl.addStretch()
        abl.addWidget(self.lbl_status)

        cw_lay.addWidget(action_bar)

        lay.addWidget(menu)
        lay.addWidget(card_wrapper, stretch=1)

        # Wire
        self.btn_forge.clicked.connect(self.forge_requested)
        self.btn_random.clicked.connect(self._randomize)
        self.btn_copy.clicked.connect(self._copy_prompt)
        self.btn_save_defaults.clicked.connect(self._save_defaults)

    def _save_defaults(self):
        d = {
            'model_index': self.combo_model.currentIndex(),
            'ar_index':    self.combo_ar.currentIndex(),
        }
        _save_defaults(d)
        self.set_status('Default portrait settings saved.')

    def _load_defaults(self):
        d = _load_defaults()
        if 'model_index' in d:
            idx = d['model_index']
            if 0 <= idx < self.combo_model.count():
                self.combo_model.setCurrentIndex(idx)
        if 'ar_index' in d:
            idx = d['ar_index']
            if 0 <= idx < self.combo_ar.count():
                self.combo_ar.setCurrentIndex(idx)

    def _randomize(self):
        for sl in self._sliders.values(): sl.setValue(random.randint(0, sl.maximum()))
        self.combo_arch.setCurrentIndex(0)
        self.input_override.clear()

    def _copy_prompt(self):
        if hasattr(self, '_current_prompt') and self._current_prompt:
            QApplication.clipboard().setText(self._current_prompt)
            self.set_status('Prompt copied.')

    def set_status(self, msg):
        self.lbl_status.setText(msg)

    def set_busy(self, busy):
        self.btn_forge.setEnabled(not busy)
        self.progress.setVisible(busy)
        if busy:
            self.progress.setRange(0, 0)

    def set_portrait_progress(self, indeterminate=True, pct=None):
        self.card.portrait_loading(indeterminate, pct)

    @property
    def archetype_key(self):
        idx = self.combo_arch.currentIndex()
        keys = ['random'] + list(dp.ARCHETYPES.keys())
        return keys[idx] if idx < len(keys) else 'random'

    @property
    def overrides(self):
        txt = self.input_override.toPlainText().strip()
        return {'extra': txt} if txt else {}

    @property
    def inclinatio(self): return {k: sl.value() for k, sl in self._sliders.items()}

    @property
    def freepik_model_id(self): return FREEPIK_MODEL_IDS[self.combo_model.currentIndex()]

    @property
    def aspect_ratio_value(self):
        return ASPECT_RATIO_VALUES.get(self.combo_ar.currentText(), 'portrait_2_3')

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: ENTIUM — The Vault Browser
# ─────────────────────────────────────────────────────────────────────────────

class EntiumTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_vault_dir = None
        self._current_entity    = {}
        self._ratings           = {}
        self._ana_worker        = None
        self._ana_done_signal   = None  # set by MainWindow
        self._ana_err_signal    = None
        self._build()

    def _build(self):
        lay = QHBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        # ── Left: vault list ──────────────────────────────────────────────────
        left = QWidget(); left.setStyleSheet(f"background:{C['panel']};")
        left.setMinimumWidth(220); left.setMaximumWidth(300)
        ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0); ll.setSpacing(0)

        list_header = QFrame()
        list_header.setStyleSheet(
            f"background:{C['panel2']};border-bottom:1px solid {C['border']};")
        list_header.setFixedHeight(36)
        lhlay = QHBoxLayout(list_header); lhlay.setContentsMargins(12,0,12,0)
        lhlay.addWidget(slbl('▶ Vault'))
        self.btn_refresh = QPushButton('↻')
        self.btn_refresh.setFixedWidth(30); self.btn_refresh.setFixedHeight(24)
        lhlay.addWidget(self.btn_refresh)
        ll.addWidget(list_header)

        self.vault_list = QListWidget()
        ll.addWidget(self.vault_list, stretch=1)

        # ── Right: card + rating ──────────────────────────────────────────────
        right_spl = QSplitter(Qt.Orientation.Horizontal); right_spl.setHandleWidth(4)

        # Card view
        self.card = EntityCard()
        right_spl.addWidget(self.card)

        # Rating panel
        rating_outer = QWidget()
        rating_outer.setStyleSheet(f"background:{C['panel']};")
        rating_outer.setMinimumWidth(280)
        rl = QVBoxLayout(rating_outer); rl.setContentsMargins(0,0,0,0); rl.setSpacing(0)

        rating_header = QFrame()
        rating_header.setStyleSheet(
            f"background:{C['panel2']};border-bottom:1px solid {C['border']};")
        rating_header.setFixedHeight(36)
        rhlay = QHBoxLayout(rating_header); rhlay.setContentsMargins(12,0,12,0)
        rhlay.addWidget(slbl('▶ Ratings'))
        rl.addWidget(rating_header)

        rating_scroll = QScrollArea(); rating_scroll.setWidgetResizable(True)
        rating_scroll.setStyleSheet(f"QScrollArea{{border:none;background:{C['panel']};}}")
        rc = QWidget(); rc.setStyleSheet(f"background:{C['panel']};")
        rcl = QVBoxLayout(rc); rcl.setContentsMargins(12,12,12,12); rcl.setSpacing(10)
        rating_scroll.setWidget(rc)
        rl.addWidget(rating_scroll, stretch=1)

        aspects = [
            ('name',     'Name'),
            ('portrait', 'Portrait'),
            ('purpose',  'Purpose'),
            ('lore',     'Lore Blocks'),
            ('traits',   'Traits'),
        ]
        for key, label in aspects:
            rcl.addWidget(slbl(f'▶ {label}'))
            w = star_widget(key, self._ratings, on_change=self._on_rating_change)
            setattr(self, f'_rating_widget_{key}', w)
            rcl.addWidget(w)

        rcl.addSpacing(8)

        # Analytica response
        rcl.addWidget(slbl('▶ Analytica Response'))
        self.txt_analytica = QTextEdit()
        self.txt_analytica.setReadOnly(True)
        self.txt_analytica.setMinimumHeight(120)
        self.txt_analytica.setStyleSheet(
            f"background:{C['panel2']};border:1px solid {C['border']};"
            f"color:{C['text_dim']};font-size:11px;font-style:italic;")
        rcl.addWidget(self.txt_analytica)

        self.lbl_regen_directive = QLabel('')
        self.lbl_regen_directive.setWordWrap(True)
        self.lbl_regen_directive.setStyleSheet(
            f"color:{C['teal_b']};font-size:11px;font-style:italic;")
        rcl.addWidget(self.lbl_regen_directive)

        # Buttons
        btn_row = QHBoxLayout()
        self.btn_send = QPushButton('SEND TO ANALYTICA →')
        self.btn_send.setObjectName('btn_teal')
        self.btn_send.setEnabled(False)
        self.btn_save_ratings = QPushButton('SAVE RATINGS')
        self.btn_save_ratings.setEnabled(False)
        btn_row.addWidget(self.btn_send); btn_row.addWidget(self.btn_save_ratings)
        rcl.addLayout(btn_row)

        self.ana_progress = QProgressBar()
        self.ana_progress.setRange(0, 0); self.ana_progress.setFixedHeight(3)
        self.ana_progress.setTextVisible(False); self.ana_progress.hide()
        rcl.addWidget(self.ana_progress)
        rcl.addStretch()

        right_spl.addWidget(rating_outer)
        right_spl.setSizes([700, 300])

        lay.addWidget(left)
        lay.addWidget(right_spl, stretch=1)

        # Wire
        self.vault_list.itemClicked.connect(self._on_item_clicked)
        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_send.clicked.connect(self._send_to_analytica)
        self.btn_save_ratings.clicked.connect(self._save_ratings)

    def refresh(self):
        self.vault_list.clear()
        entries = _load_vault_entries()
        for vault_dir, entity in entries:
            name = entity.get('display_name', '?')
            role = entity.get('role', '')[:30]
            item = QListWidgetItem(f"{name}\n{role}")
            item.setData(Qt.ItemDataRole.UserRole, (str(vault_dir), entity))
            self.vault_list.addItem(item)

    def _on_item_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data: return
        vault_dir, entity = data
        self._current_vault_dir = vault_dir
        self._current_entity = entity
        self._ratings = _load_ratings(vault_dir)

        self.card.populate(entity)
        portrait_path = Path(vault_dir) / 'portrait.png'
        if portrait_path.exists():
            self.card.set_portrait(str(portrait_path))

        # Repopulate rating widgets with loaded ratings
        for key in ['name', 'portrait', 'purpose', 'lore', 'traits']:
            w = getattr(self, f'_rating_widget_{key}')
            # Find spinbox and linedit children
            spin = w.findChild(QSpinBox)
            line = w.findChild(QLineEdit)
            if spin: spin.setValue(self._ratings.get(f'{key}_stars', 0))
            if line: line.setText(self._ratings.get(f'{key}_comment', ''))

        self.txt_analytica.clear()
        self.lbl_regen_directive.setText('')
        self.btn_send.setEnabled(True)
        self.btn_save_ratings.setEnabled(True)

    def _on_rating_change(self):
        pass  # ratings dict updated in-place by star_widget

    def _save_ratings(self):
        if not self._current_vault_dir: return
        _save_ratings(self._current_vault_dir, self._ratings)

    def _send_to_analytica(self):
        if not self._current_entity: return
        if self._ana_worker and self._ana_worker.isRunning(): return
        self.btn_send.setEnabled(False)
        self.ana_progress.show()
        self.txt_analytica.setPlainText('⚗  The Analytica considers the ratings…')

        self._ana_worker = AnalyticaWorker(
            entity=self._current_entity, ratings=self._ratings)
        self._ana_worker.progress.connect(
            lambda m: self.txt_analytica.setPlainText(m))
        self._ana_worker.finished.connect(self._on_analytica_done)
        self._ana_worker.errored.connect(self._on_analytica_error)
        self._ana_worker.start()

    def _on_analytica_done(self, result):
        self.ana_progress.hide(); self.btn_send.setEnabled(True)
        verdict = result.get('verdict', '')
        notes = result.get('aspect_notes', {})
        directive = result.get('regen_directive', '')

        lines = [verdict, '']
        for aspect, note in notes.items():
            if note:
                lines.append(f'{aspect.upper()}: {note}')
        self.txt_analytica.setPlainText('\n'.join(lines).strip())
        self.lbl_regen_directive.setText(f'→ {directive}' if directive else '')

        # Save ratings with analytica response embedded
        if self._current_vault_dir:
            self._ratings['analytica_response'] = result
            _save_ratings(self._current_vault_dir, self._ratings)

    def _on_analytica_error(self, err):
        self.ana_progress.hide(); self.btn_send.setEnabled(True)
        self.txt_analytica.setPlainText(f'✕ {err[:200]}')

# ─────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class FornaxEntiumApp(QMainWindow):
    _gen_done      = pyqtSignal(dict)
    _gen_err       = pyqtSignal(str)
    _portrait_done = pyqtSignal(str)
    _portrait_err  = pyqtSignal(str)
    _portrait_tick = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        _ensure_dirs()
        self.setWindowTitle('Fornax Entium  ·  Entity Forge & Vault')
        self.setMinimumSize(1100, 700); self.resize(1440, 880)

        self._entity     = {}
        self._gen_id     = ''
        self._por_path   = ''
        self._gen_w      = None
        self._por_w      = None

        self._gen_done.connect(self._on_gen_done)
        self._gen_err.connect(self._on_gen_err)
        self._portrait_done.connect(self._on_portrait_done)
        self._portrait_err.connect(self._on_portrait_err)
        self._portrait_tick.connect(self._on_portrait_tick)

        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(SS)
        self.tabs = QTabWidget()
        self.fornax = FornaxTab()
        self.entium = EntiumTab()
        self.tabs.addTab(self.fornax, 'FORNAX')
        self.tabs.addTab(self.entium, 'ENTIUM')
        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

        self.fornax.forge_requested.connect(self._forge)
        self.tabs.currentChanged.connect(self._on_tab_change)

        QShortcut(QKeySequence('F5'), self).activated.connect(self._forge)
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(self._forge)

        self._status('The forge awaits.')

    def _on_tab_change(self, idx):
        if idx == 1:  # ENTIUM
            self.entium.refresh()

    def _busy(self):
        return any(w and w.isRunning() for w in [self._gen_w, self._por_w])

    def _forge(self):
        if self._busy(): return
        self._entity = {}; self._gen_id = str(uuid.uuid4())[:8]; self._por_path = ''
        self.fornax.card.clear()
        self.fornax.set_busy(True)
        self.fornax.btn_copy.setEnabled(False)
        self.fornax.set_status('⚗  Forging entity…')
        self._status('⚗  GENERATIO in progress…')

        used = _load_used_names()
        self._gen_w = GeneratioWorker(
            inc=self.fornax.inclinatio,
            archetype_key=self.fornax.archetype_key,
            overrides=self.fornax.overrides,
            used_names=used,
        )
        self._gen_w.progress.connect(self.fornax.set_status)
        self._gen_w.finished.connect(lambda d: self._gen_done.emit(d))
        self._gen_w.errored.connect(lambda e: self._gen_err.emit(e))
        self._gen_w.start()

    def _on_gen_done(self, data):
        self._entity = data
        self.fornax.card.populate(data)
        self.fornax._current_prompt = data.get('assembled_prompt', '')
        self.fornax.btn_copy.setEnabled(True)

        name = data.get('display_name', '')
        _save_used_name(name)

        self.fornax.set_busy(False)
        self.fornax.set_status(f'✦  {name} — generating portrait…')
        self._status(f'✦  Entity forged: {name}')

        # Fire portrait immediately
        self._fire_portrait()

    def _on_gen_err(self, err):
        self.fornax.set_busy(False)
        self.fornax.set_status(f'✕  {err[:100]}')
        self._status(f'✕  Generation error')

    def _fire_portrait(self):
        if self._por_w and self._por_w.isRunning(): return
        prompt = self._entity.get('assembled_prompt', '')
        if not prompt: return
        self.fornax.set_portrait_progress(indeterminate=True)
        self.fornax.set_status('⚗  Manifesting portrait…')

        self._por_w = PortraitWorker(
            prompt=prompt,
            model_id=self.fornax.freepik_model_id,
            aspect_ratio=self.fornax.aspect_ratio_value,
            seed=random.randint(0, 2**31 - 1),
        )
        self._por_w.progress.connect(self.fornax.set_status)
        self._por_w.poll_tick.connect(lambda a, m: self._portrait_tick.emit(a, m))
        self._por_w.finished.connect(lambda p: self._portrait_done.emit(p))
        self._por_w.errored.connect(lambda e: self._portrait_err.emit(e))
        self._por_w.start()

    def _on_portrait_done(self, path):
        self._por_path = path
        self.fornax.card.set_portrait(path)
        name = self._entity.get('display_name', '?')
        try:
            d = _vault_save(self._entity, path)
            emit_event("entity_vaulted", {"name": name, "vault_dir": str(d)})
        except Exception as e:
            log.warning(f'vault_save: {e}')
        self.fornax.set_status(f'🜲  Complete — {name}')
        self._status(f'🜲  {name} — portrait generated, vault saved.')

    def _on_portrait_err(self, err):
        self.fornax.card.portrait_progress.hide()
        self.fornax.set_status(f'✕  Portrait: {err[:80]}')
        self._status('✕  Portrait generation failed.')
        # Still save entity without portrait
        if self._entity:
            name = self._entity.get('display_name', '?')
            try:
                d = _vault_save(self._entity, None)
                emit_event("entity_vaulted", {"name": name, "vault_dir": str(d)})
            except Exception: pass

    def _on_portrait_tick(self, current, total):
        if total > 0:
            self.fornax.set_portrait_progress(indeterminate=False, pct=int((current/total)*100))

    def _status(self, msg): self.statusBar().showMessage(f'  {msg}')


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Fornax Entium')
    win = FornaxEntiumApp()
    win.show()
    sys.exit(app.exec())
