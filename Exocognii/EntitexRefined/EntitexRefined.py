#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ███████╗███╗   ██╗████████╗██╗████████╗███████╗██╗  ██╗ ▍
🮈  ██╔════╝████╗  ██║╚══██╔══╝██║╚══██╔══╝██╔════╝╚██╗██╔╝ ▍
🮈  █████╗  ██╔██╗ ██║   ██║   ██║   ██║   █████╗   ╚███╔╝  ▍
🮈  ██╔══╝  ██║╚██╗██║   ██║   ██║   ██║   ██╔══╝   ██╔██╗  ▍
🮈  ███████╗██║ ╚████║   ██║   ██║   ██║   ███████╗██╔╝ ██╗ ▍
🮈  ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝ ▍
🮈       R E F I N E D  ·  E n t i t y  F o r g e  v0.4     ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                     ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                     EntitexRefined.py   ⯩
# ⯨                                                                     ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
#
# EntitexRefined v0.4
# Arca Cognitorium — Entity Forge
#
# Devoted Absurd rebuilt with Entitex's pipeline.
# The primary output is a DA-style image generation prompt
# built around a full Cogniverse entity lore profile.
# No portrait style dropdown. DA visual DNA is locked.
#
# Pipeline: SEMEN → GENERATIO → ANALYTICA → NOMEN → ELABORATIO
# ─────────────────────────────────────────────────────────────────────────────

import os
import re
import sys
import json
import uuid
import shutil
import random
import logging
import threading
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QColor, QTextCharFormat, QSyntaxHighlighter, QKeySequence, QShortcut,
    QFont, QFontDatabase,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel,
    QPushButton, QComboBox, QSlider, QScrollArea,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QTextEdit, QPlainTextEdit, QLineEdit,
    QProgressBar, QSplitter, QTabWidget,
    QListWidget, QListWidgetItem,
    QRadioButton, QButtonGroup,
    QStatusBar, QMessageBox, QCheckBox,
)

# ─────────────────────────────────────────────────────────────────────────────
# Path setup
# ─────────────────────────────────────────────────────────────────────────────

_ARCA_DIR = Path.home() / 'ArcaCognitorium'
_ENTITEX  = _ARCA_DIR / 'Exocognii' / 'Entitex'
_DA_DIR   = _ENTITEX / 'Referentia' / 'Prompts' / 'DevotedAbsurd-PromptGen'
_HERE     = Path(__file__).parent

sys.path.insert(0, str(_ARCA_DIR))
sys.path.insert(0, str(_ENTITEX))
sys.path.insert(0, str(_DA_DIR))
sys.path.insert(0, str(_HERE))

from claudebox import ClaudeBox

import data_pools as dp
import learning_engine

from Disposition_sliders import (
    DISPOSITION_LABELS, REGISTER_LABELS, PRESENCE_LABELS,
    OPACITY_LABELS, STABILITY_LABELS,
)
from disposition_axes import TEMPORALITY_LABELS, LEGIBILITY_LABELS

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR        = _ARCA_DIR / 'Exocognii' / 'EntitexRefined'
VAULT_DIR       = BASE_DIR / 'vault'
LOG_PATH        = BASE_DIR / 'entitex_refined_log.json'
USED_NAMES_PATH = BASE_DIR / 'used_names.json'

# ─────────────────────────────────────────────────────────────────────────────
# PALETTE
# ─────────────────────────────────────────────────────────────────────────────

C = {
    'bg':        '#1a1c18',
    'panel':     '#202220',
    'panel2':    '#252720',
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
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background: {C['bg']}; color: {C['text']};
    font-family: "IBM Plex Mono", "Courier New", monospace; font-size: 12px;
}}
QTabWidget::pane {{ border: 1px solid {C['border']}; background: {C['panel']}; }}
QTabBar::tab {{
    background: {C['bg']}; color: {C['muted']};
    padding: 6px 18px; border: 1px solid {C['border']}; border-bottom: none;
    font-size: 11px; letter-spacing: 1px;
}}
QTabBar::tab:selected {{ background: {C['panel']}; color: {C['green_b']}; border-bottom: 2px solid {C['green']}; }}
QLineEdit, QTextEdit, QComboBox {{
    background: {C['panel2']}; border: 1px solid {C['border']}; color: {C['text']};
    padding: 5px 8px; font-family: "IBM Plex Mono", "Courier New", monospace; font-size: 12px;
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
    font-size: 13px; letter-spacing: 2px; padding: 10px 24px; font-weight: bold;
}}
QPushButton#btn_forge:hover {{ background: rgba(74,124,63,0.2); }}
QPushButton#btn_random {{ border-color: {C['amber']}; color: {C['amber']}; }}
QPushButton#btn_random:hover {{ background: rgba(200,168,75,0.15); }}
QPushButton#btn_copy {{ border-color: {C['teal']}; color: {C['teal_b']}; }}
QPushButton#btn_copy:hover {{ background: rgba(58,112,112,0.2); }}
QPushButton#btn_iterate {{ border-color: {C['teal']}; color: {C['teal_b']}; font-size: 11px; }}
QPushButton#btn_iterate:hover {{ background: rgba(58,112,112,0.2); }}
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
QListWidget::item {{ padding: 4px 8px; border-bottom: 1px solid {C['border']}; }}
QListWidget::item:selected {{ background: {C['highlight']}; color: {C['green_b']}; }}
QStatusBar {{
    background: {C['panel']}; color: {C['muted']};
    border-top: 1px solid {C['border']}; font-size: 10px; letter-spacing: 1px;
}}
QSplitter::handle {{ background: {C['border']}; }}
QRadioButton {{
    color: {C['text']}; background: transparent;
    font-family: "IBM Plex Mono", "Courier New", monospace; font-size: 11px; spacing: 8px;
}}
QRadioButton::indicator {{
    width: 13px; height: 13px; border: 1px solid {C['border']}; border-radius: 7px; background: {C['bg']};
}}
QRadioButton::indicator:checked {{ background: {C['green_b']}; border-color: {C['green']}; }}
QCheckBox {{
    color: {C['text_dim']}; background: transparent; font-size: 11px;
}}
QCheckBox::indicator {{
    width: 13px; height: 13px; border: 1px solid {C['border']}; background: {C['bg']};
}}
QCheckBox::indicator:checked {{ background: {C['green']}; border-color: {C['green_b']}; }}
QLabel#section_label {{
    color: {C['amber']}; font-size: 10px; letter-spacing: 2px;
    padding-bottom: 4px; border-bottom: 1px solid {C['border']};
}}
QLabel#score_label {{ color: {C['green_b']}; font-size: 22px; font-weight: bold; }}
QLabel#weakness_tag {{
    color: {C['red']}; background: rgba(160,64,64,0.12);
    border: 1px solid rgba(160,64,64,0.3); padding: 2px 7px; font-size: 10px;
}}
"""

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

GENERATIO_SYSTEM = f"""You are Entitex Generatio — entity forge for the Arca Cognitorium.

You generate a complete entity in one response combining:
1. A full Devoted Absurd style image generation prompt (assembled_prompt)
2. A Cogniverse entity lore profile

── LOCKED VISUAL STYLE ──────────────────────────────────────────────────────
{dp.STYLE_DNA}

Palette: muted, heavily desaturated, dark only. Near-blacks, coal, soot, dark industrials, aged organics, bruised tones. NO pastels. NO bright primaries. NO light backgrounds. Sparse highlights only.

── SETTING ──────────────────────────────────────────────────────────────────
Medieval dark-ages world with crude pseudo-mechanical technology. Not steampunk, not modern, not Victorian. Bellows, gears, waterwheel machinery, hand-cranked devices, alchemical apparatus. Heavy, dark, old — creaks and smells of grease.

── ENTITY REGISTER ──────────────────────────────────────────────────────────
This entity exists within the Arca Cognitorium — a dark intelligence architecture. It is a presence, not a person. It carries institutional permanence. Purpose: second-person present tense. Lore: third person. Nothing soft or explanatory.

── INPUT ────────────────────────────────────────────────────────────────────
Disposition directives only. No name. No archetype label. No role.
Generate everything from the disposition space alone.
An archetype vocabulary block may follow as tonal reference — synthesise freely.

── OUTPUT ───────────────────────────────────────────────────────────────────
Respond ONLY with a single raw JSON object. No markdown. No preamble.

{{
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

assembled_prompt: open with full style DNA, state medieval-mechanical setting, weave all character elements into one paragraph, end with strict palette note naming dark colours, specify dark background, include entity title and aura.

JSON hygiene: every string on one line. No literal newlines inside strings. No trailing commas."""


ANALYTICA_SYSTEM = """You are Entitex Analytica — prompt engineer and lore critic for the Arca Cognitorium.

Review both the assembled_prompt and the entity lore.

── PROMPT REVIEW ─────────────────────────────────────────────────────────────
Check for: palette drift toward light (flag aggressively), pale backgrounds (-2), modern anachronisms (-2), vagueness, style drift, era confusion, assembled-feeling character. Score 1-10. 7+ is genuinely strong.

── LORE REVIEW ──────────────────────────────────────────────────────────────
Check for: internal coherence, Cogniverse fit, lore texture, trait calibration.

── OUTPUT ───────────────────────────────────────────────────────────────────
Respond ONLY with a raw JSON object:
{
  "score": <float 1-10>,
  "reasoning": "<2-3 sentences — harsh, specific>",
  "weaknesses": ["<short tag>", ...],
  "refined_prompt": "<full improved assembled_prompt>",
  "next_iteration_suggestion": "<one sentence>",
  "lore_verdict": "<2-3 sentences in Cogniverse register — speak as the Tower>",
  "lore_flags": ["<short lore flag>", ...]
}

No preamble. No markdown. No fences."""


NOMEN_SYSTEM = """You are Entitex Nomen — the naming oracle of the Arca Cognitorium.

You receive a complete entity profile and a list of used names. Invent 3 to 5 name candidates.

Convention: always "The [Word]". The noun is a role, disposition, function, or quality. Carries institutional weight. Earns its place from the specific profile.

Register (not limited to):
- Analytical: The Empiricist, The Calibrator, The Falsifier, The Taxonomist
- Temperamental: The Fatalist, The Stoic, The Brooder, The Forsaken, The Detached
- Creative: The Augur, The Weaver, The Cartographer, The Kindler
- Institutional: The Adjudicator, The Custodian, The Warden, The Rectifier
- Liminal: The Threshold, The Remnant, The Between, The Persistent, The Hollow
- Adversarial: The Heretic, The Refuter, The Dissident, The Resistant

DO NOT propose any name in the used-names list.

Respond ONLY with:
{
  "candidates": ["The Word", "The Word", "The Word"]
}

No preamble. No markdown. No etymology."""

# ─────────────────────────────────────────────────────────────────────────────
# ClaudeBox instances
# ─────────────────────────────────────────────────────────────────────────────

_api_key = os.environ.get('CLAUDE_API_KEY')

_gen_box      = ClaudeBox(api_key=_api_key, system_prompt=GENERATIO_SYSTEM, stream=False)
_analysis_box = ClaudeBox(api_key=_api_key, system_prompt=ANALYTICA_SYSTEM, stream=False)
_nomen_box    = ClaudeBox(api_key=_api_key, system_prompt=NOMEN_SYSTEM,     stream=False)

_gen_lock = threading.Lock()
_ana_lock = threading.Lock()
_nom_lock = threading.Lock()

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
    for d in [BASE_DIR, VAULT_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists(): LOG_PATH.write_text(json.dumps([], indent=2))
    if not USED_NAMES_PATH.exists(): USED_NAMES_PATH.write_text(json.dumps([], indent=2))

def _log(entry):
    try:
        data = json.loads(LOG_PATH.read_text())
        if not isinstance(data, list): data = []
    except Exception: data = []
    data.append({'timestamp': datetime.now().isoformat(), **entry})
    LOG_PATH.write_text(json.dumps(data[-200:], indent=2))

def _vault_save(entity):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = re.sub(r'\W+', '_', entity.get('display_name', 'unnamed').lower())
    d = VAULT_DIR / f'{ts}_{slug}'
    d.mkdir(parents=True, exist_ok=True)
    (d / 'entity.json').write_text(
        json.dumps({**entity, 'saved_at': datetime.now().isoformat()}, indent=2))

# ─────────────────────────────────────────────────────────────────────────────
# WORKERS
# ─────────────────────────────────────────────────────────────────────────────

class GeneratioWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    errored  = pyqtSignal(str)

    def __init__(self, inc, archetype_key='random', overrides=None, parent=None):
        super().__init__(parent)
        self.inc = inc
        self.archetype_key = archetype_key
        self.overrides = overrides or {}

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
            user = (
                'Generate a complete entity specification from these disposition directives.\n\n'
                f'Disposition directives:\n{_inclinatio_str(self.inc)}'
                + vocab + overrides_block
            )
            with _gen_lock:
                response = _gen_box.send(user, max_tokens=4096)
            self.finished.emit(_parse_json(response.text.strip()))
        except Exception as exc:
            self.errored.emit(str(exc))


class AnalyticaWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    errored  = pyqtSignal(str)

    def __init__(self, entity, gen_id, iterate_feedback='', parent=None):
        super().__init__(parent)
        self.entity = entity
        self.gen_id = gen_id
        self.iterate_feedback = iterate_feedback

    def run(self):
        try:
            session_id = f'analytica_{self.gen_id}'
            if not self.iterate_feedback:
                self.progress.emit('⚗  The Analytica reviews…')
                try: _analysis_box.delete_session(session_id)
                except Exception: pass
                e = self.entity
                content = (
                    f'Analyse and refine this entity.\n\n'
                    f'ASSEMBLED PROMPT:\n{e.get("assembled_prompt","")}\n\n'
                    f'ENTITY LORE:\n'
                    f'Title: {e.get("title","")}\n'
                    f'Role: {e.get("role","")}\n'
                    f'Purpose: {e.get("purpose","")}\n'
                    f'Lore Nature: {e.get("lore_nature","")}\n'
                    f'Lore Aura: {e.get("lore_aura","")}\n'
                    f'Traits: {json.dumps(e.get("traits",{}))}\n'
                    f'Domain Keywords: {", ".join(e.get("domain_keywords",[]))}'
                )
            else:
                self.progress.emit('⚗  Analytica considers your observation…')
                content = self.iterate_feedback
            with _ana_lock:
                response = _analysis_box.send(content, session_id=session_id, max_tokens=4096)
            self.finished.emit(_parse_json(response.text.strip()))
        except Exception as exc:
            self.errored.emit(str(exc))


class NomenWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    errored  = pyqtSignal(str)

    def __init__(self, entity, parent=None):
        super().__init__(parent)
        self.entity = entity

    def run(self):
        try:
            self.progress.emit('⚗  The naming oracle invents names…')
            used = _load_used_names()
            e = self.entity
            prompt = (
                f'Invent 3 to 5 name candidates for this entity.\n\n'
                f'Title: {e.get("title","")}\n'
                f'Role: {e.get("role","")}\n'
                f'Purpose (excerpt): {str(e.get("purpose",""))[:300]}\n'
                f'Lore Nature (excerpt): {str(e.get("lore_nature",""))[:200]}\n'
                f'Lore Aura: {e.get("lore_aura","")}\n'
                f'Domain Keywords: {", ".join(e.get("domain_keywords",[]))}\n'
                f'Traits: {json.dumps(e.get("traits",{}))}\n\n'
            )
            if used:
                prompt += 'Names already in use — DO NOT propose:\n'
                prompt += '\n'.join(f'  {n}' for n in used) + '\n\n'
            prompt += 'Propose 3 to 5 invented names that fit this entity specifically.'
            with _nom_lock:
                response = _nomen_box.send(prompt, max_tokens=256)
            data = _parse_json(response.text.strip())
            candidates = data.get('candidates', [])
            if not isinstance(candidates, list) or not candidates:
                raise ValueError(f'No candidates: {response.text[:200]}')
            self.finished.emit([str(c) for c in candidates[:5]])
        except Exception as exc:
            self.errored.emit(str(exc))

# ─────────────────────────────────────────────────────────────────────────────
# PROMPT HIGHLIGHTER
# ─────────────────────────────────────────────────────────────────────────────

class PromptHighlighter(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        self._rules = []
        def rule(pat, color, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold: fmt.setFontWeight(700)
            self._rules.append((re.compile(pat), fmt))
        rule(r'(Stylized 2D|flat cel shading|ink outlines|bold clean)[^,.\n]*', C['green_b'])
        rule(r'(Character is|Personality:|Wearing|Build:|Pose:|Expression:|Entity designation:)', C['amber'], True)
        rule(r'(Color palette:|background|Palette)', C['teal_b'])
        rule(r'\b(no animals|no glossy|not sketchy|not painterly|No pastels|No bright)\b', C['red'])
    def highlightBlock(self, text):
        for pat, fmt in self._rules:
            for m in pat.finditer(text):
                self.setFormat(m.start(), m.end()-m.start(), fmt)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def slbl(text):
    lbl = QLabel(text.upper()); lbl.setObjectName('section_label'); return lbl

def hline():
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color:{C['border']};"); return f

def _slider_widget(labels, initial=0):
    sl = QSlider(Qt.Orientation.Horizontal)
    sl.setRange(0, len(labels)-1); sl.setValue(initial)
    sl.setTickPosition(QSlider.TickPosition.TicksBelow); sl.setTickInterval(1)
    lbl = QLabel(labels[initial])
    lbl.setStyleSheet(f"color:{C['muted']};font-size:9px;letter-spacing:1px;")
    sl.valueChanged.connect(lambda v: lbl.setText(labels[v]))
    return sl, lbl

# ─────────────────────────────────────────────────────────────────────────────
# PHASE BAR
# ─────────────────────────────────────────────────────────────────────────────

PHASES = ['SEMEN', 'GENERATIO', 'ANALYTICA', 'NOMEN', 'ELABORATIO']

class PhaseBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(16)
        lay.addStretch()
        self._lbls = {}
        for p in PHASES:
            lbl = QLabel(f'○ {p}')
            lbl.setStyleSheet(f"color:{C['border']};font-size:9px;letter-spacing:1px;")
            self._lbls[p] = lbl; lay.addWidget(lbl)
        lay.addStretch()

    def set_phase(self, phase, completed=None):
        completed = completed or []
        for p, lbl in self._lbls.items():
            if p == phase:
                lbl.setText(f'● {p}')
                lbl.setStyleSheet(f"color:{C['green_b']};font-size:9px;letter-spacing:1px;font-weight:bold;")
            elif p in completed:
                lbl.setText(f'◉ {p}')
                lbl.setStyleSheet(f"color:{C['muted']};font-size:9px;letter-spacing:1px;")
            else:
                lbl.setText(f'○ {p}')
                lbl.setStyleSheet(f"color:{C['border']};font-size:9px;letter-spacing:1px;")

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self._archetype_keys = ['random'] + list(dp.ARCHETYPES.keys())
        self._build()

    def _build(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea{{border:none;background:{C['panel']};}}")
        outer.addWidget(scroll)
        w = QWidget(); w.setStyleSheet(f"background:{C['panel']};")
        lay = QVBoxLayout(w); lay.setContentsMargins(14,14,14,14); lay.setSpacing(10)
        scroll.setWidget(w)

        ttl = QLabel('ENTITEX REFINED')
        ttl.setStyleSheet(f"color:{C['green_b']};font-size:16px;font-weight:bold;letter-spacing:3px;")
        sub = QLabel('Entity Forge  ·  Devoted Absurd Engine')
        sub.setStyleSheet(f"color:{C['muted']};font-size:10px;letter-spacing:1px;")
        lay.addWidget(ttl); lay.addWidget(sub); lay.addWidget(hline())

        lay.addWidget(slbl('▶ Tonal Register (optional)'))
        self.combo_arch = QComboBox()
        self.combo_arch.addItem('Random / Blind')
        for k in dp.ARCHETYPES: self.combo_arch.addItem(dp.ARCHETYPES[k]['label'])
        lay.addWidget(self.combo_arch)

        lay.addWidget(slbl('▶ Overrides (optional)'))
        self.input_role = QLineEdit(); self.input_role.setPlaceholderText('Role override…')
        self.input_personality = QLineEdit(); self.input_personality.setPlaceholderText('Personality override…')
        self.input_extra = QTextEdit(); self.input_extra.setPlaceholderText('Extra visual / notes…')
        self.input_extra.setMaximumHeight(60)
        for w_ in [self.input_role, self.input_personality, self.input_extra]:
            lay.addWidget(w_)

        lay.addWidget(slbl('▶ Inclinationes'))
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
            lname = QLabel(label); lname.setStyleSheet(f"color:{C['text_dim']};font-size:10px;")
            row.addWidget(lname); row.addStretch()
            sl, lval = _slider_widget(labels, default)
            self._sliders[key] = sl
            lay.addLayout(row); lay.addWidget(sl); lay.addWidget(lval); lay.addSpacing(2)

        lay.addWidget(slbl('▶ Options'))
        self.chk_auto = QCheckBox('Auto-send to Analytica after GENERATIO')
        self.chk_auto.setChecked(True); lay.addWidget(self.chk_auto)

        lay.addWidget(hline())
        br = QHBoxLayout()
        self.btn_forge = QPushButton('⚗  FORGE ENTITY'); self.btn_forge.setObjectName('btn_forge')
        self.btn_random = QPushButton('↻ RANDOM'); self.btn_random.setObjectName('btn_random')
        br.addWidget(self.btn_forge); br.addWidget(self.btn_random); lay.addLayout(br)

        br2 = QHBoxLayout()
        self.btn_copy = QPushButton('COPY PROMPT'); self.btn_copy.setObjectName('btn_copy')
        self.btn_copy.setEnabled(False)
        self.btn_clear = QPushButton('CLEAR')
        br2.addWidget(self.btn_copy); br2.addWidget(self.btn_clear); lay.addLayout(br2)

        lay.addStretch()
        self.lbl_stats = QLabel('No history yet')
        self.lbl_stats.setStyleSheet(f"color:{C['muted']};font-size:10px;")
        self.lbl_stats.setWordWrap(True); lay.addWidget(self.lbl_stats)

    @property
    def archetype_key(self):
        idx = self.combo_arch.currentIndex()
        return self._archetype_keys[idx] if idx < len(self._archetype_keys) else 'random'

    @property
    def overrides(self):
        ov = {}
        if self.input_role.text().strip(): ov['role'] = self.input_role.text().strip()
        if self.input_personality.text().strip(): ov['personality'] = self.input_personality.text().strip()
        if self.input_extra.toPlainText().strip(): ov['extra'] = self.input_extra.toPlainText().strip()
        return ov

    @property
    def inclinatio(self): return {k: sl.value() for k, sl in self._sliders.items()}

    @property
    def auto_analyse(self): return self.chk_auto.isChecked()

    def randomize(self):
        for sl in self._sliders.values(): sl.setValue(random.randint(0, sl.maximum()))
        self.combo_arch.setCurrentIndex(0)
        self.input_role.clear(); self.input_personality.clear(); self.input_extra.clear()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────────────────────────────────

class MainContent(QWidget):
    send_to_analytica = pyqtSignal()
    iterate_requested = pyqtSignal(str)
    proceed_to_nomen  = pyqtSignal()
    name_ratified     = pyqtSignal(str)
    accept_refined    = pyqtSignal()
    copy_refined      = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        self.tabs = QTabWidget(); lay.addWidget(self.tabs)
        self.tabs.addTab(self._build_entity_tab(),    'ENTITY')
        self.tabs.addTab(self._build_analytica_tab(), 'ANALYTICA')
        self.tabs.addTab(self._build_nomen_tab(),     'NOMEN')
        self.tabs.addTab(self._build_history_tab(),   'HISTORY')

    def _build_entity_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab); lay.setContentsMargins(16,16,16,16); lay.setSpacing(10)

        card = QFrame()
        card.setStyleSheet(f"background:{C['panel2']};border:1px solid {C['border']};")
        cl = QHBoxLayout(card); cl.setContentsMargins(12,10,12,10)
        self.lbl_char_info = QLabel('— no entity generated yet —')
        self.lbl_char_info.setStyleSheet(f"color:{C['muted']};font-size:11px;border:none;")
        self.lbl_char_info.setWordWrap(True)
        cl.addWidget(self.lbl_char_info); card.setMaximumHeight(90); lay.addWidget(card)

        spl = QSplitter(Qt.Orientation.Horizontal); spl.setHandleWidth(4)

        pw = QWidget()
        pl = QVBoxLayout(pw); pl.setContentsMargins(0,0,0,0); pl.setSpacing(6)
        pl.addWidget(slbl('▶ Assembled Prompt'))
        self.prompt_output = QTextEdit()
        self.prompt_output.setReadOnly(False)
        self.prompt_output.setPlaceholderText(
            '// Prompt appears here after generation.\n// Edit freely before sending to Analytica.')
        self.prompt_output.setStyleSheet(
            f"QTextEdit{{background:{C['bg']};border:1px solid {C['border']};"
            f"color:{C['text']};font-family:'IBM Plex Mono','Courier New',monospace;"
            f"font-size:11px;padding:10px;}}")
        self._hl1 = PromptHighlighter(self.prompt_output.document())
        pl.addWidget(self.prompt_output, stretch=1)

        btnrow = QHBoxLayout()
        self.btn_send_analytica = QPushButton('SEND TO ANALYTICA →')
        self.btn_send_analytica.setObjectName('btn_iterate')
        self.btn_send_analytica.setEnabled(False)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False); self.progress_bar.setFixedHeight(4)
        self.progress_bar.setRange(0,0); self.progress_bar.hide()
        btnrow.addWidget(self.btn_send_analytica); btnrow.addWidget(self.progress_bar)
        pl.addLayout(btnrow)
        self.btn_send_analytica.clicked.connect(self.send_to_analytica)
        spl.addWidget(pw)

        cw = QWidget()
        codex_l = QVBoxLayout(cw); codex_l.setContentsMargins(8,0,0,0); codex_l.setSpacing(6)
        codex_l.addWidget(slbl('▶ Codex Entis'))
        cscroll = QScrollArea(); cscroll.setWidgetResizable(True)
        cscroll.setStyleSheet(f"QScrollArea{{border:none;background:{C['bg']};}}")
        cc = QWidget(); cc.setStyleSheet(f"background:{C['bg']};")
        cll = QVBoxLayout(cc); cll.setContentsMargins(0,0,0,0); cll.setSpacing(4)
        cscroll.setWidget(cc)

        def cfield(label, h=0):
            lbl = QLabel(label.upper())
            lbl.setStyleSheet(f"color:{C['gold_dim']};font-size:9px;letter-spacing:2px;")
            cll.addWidget(lbl)
            if h == 0:
                w = QLabel('—'); w.setWordWrap(True)
                w.setStyleSheet(
                    f"color:{C['amber']};font-family:'IBM Plex Mono',monospace;"
                    f"font-size:11px;background:{C['bg']};border:1px solid {C['border']};padding:4px;")
            else:
                w = QPlainTextEdit(); w.setReadOnly(True); w.setFixedHeight(h)
                w.setStyleSheet(
                    f"QPlainTextEdit{{color:{C['text']};font-family:'IBM Plex Mono',monospace;"
                    f"font-size:10px;background:{C['bg']};border:1px solid {C['border']};padding:4px;}}")
            cll.addWidget(w); return w

        self.cf_name    = cfield('Display Name')
        self.cf_title   = cfield('Title / Epithet')
        self.cf_role    = cfield('Role')
        self.cf_purpose = cfield('Purpose', 80)
        self.cf_nature  = cfield('Lore Nature', 60)
        self.cf_aura    = cfield('Aura', 40)
        self.cf_traits  = cfield('Traits')
        cll.addStretch()

        codex_l.addWidget(cscroll, stretch=1)
        spl.addWidget(cw)
        spl.setSizes([620, 280])
        lay.addWidget(spl, stretch=1)
        return tab

    def _build_analytica_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab); lay.setContentsMargins(16,16,16,16); lay.setSpacing(10)

        srow = QHBoxLayout()
        self.lbl_score = QLabel('—'); self.lbl_score.setObjectName('score_label')
        self.lbl_score.setFixedWidth(50)
        sl = QLabel('PROMPT SCORE:'); sl.setStyleSheet(f"color:{C['muted']};font-size:10px;letter-spacing:1px;")
        srow.addWidget(sl); srow.addWidget(self.lbl_score)
        srow.addWidget(QLabel('  YOUR SCORE:'))
        self.slider_user = QSlider(Qt.Orientation.Horizontal)
        self.slider_user.setRange(0,10); self.slider_user.setValue(0); self.slider_user.setFixedWidth(130)
        self.lbl_user_val = QLabel('—')
        self.lbl_user_val.setStyleSheet(f"color:{C['amber']};font-size:14px;font-weight:bold;")
        self.btn_submit_score = QPushButton('SUBMIT'); self.btn_submit_score.setEnabled(False)
        srow.addWidget(self.slider_user); srow.addWidget(self.lbl_user_val)
        srow.addWidget(self.btn_submit_score); srow.addStretch()
        lay.addLayout(srow)
        self.slider_user.valueChanged.connect(lambda v: self.lbl_user_val.setText('—' if v==0 else str(v)))

        self.weakness_row = QHBoxLayout(); self.weakness_row.setSpacing(6); lay.addLayout(self.weakness_row)

        lay.addWidget(slbl('▶ Reasoning'))
        self.txt_reasoning = QTextEdit(); self.txt_reasoning.setReadOnly(True)
        self.txt_reasoning.setMaximumHeight(75)
        self.txt_reasoning.setStyleSheet(
            f"background:{C['panel2']};border:1px solid {C['border']};color:{C['text_dim']};font-size:11px;")
        lay.addWidget(self.txt_reasoning)

        lay.addWidget(slbl('▶ Lore Verdict'))
        self.txt_lore_verdict = QTextEdit(); self.txt_lore_verdict.setReadOnly(True)
        self.txt_lore_verdict.setMaximumHeight(65)
        self.txt_lore_verdict.setStyleSheet(
            f"background:{C['panel2']};border:1px solid {C['border']};"
            f"color:{C['text_dim']};font-size:11px;font-style:italic;")
        lay.addWidget(self.txt_lore_verdict)

        self.lore_flag_row = QHBoxLayout(); self.lore_flag_row.setSpacing(6); lay.addLayout(self.lore_flag_row)

        lay.addWidget(slbl('▶ Refined Prompt'))
        self.txt_refined = QTextEdit(); self.txt_refined.setReadOnly(False)
        self.txt_refined.setStyleSheet(
            f"background:{C['bg']};border:1px solid {C['border']};"
            f"color:{C['text']};font-size:11px;padding:8px;")
        self._hl2 = PromptHighlighter(self.txt_refined.document())
        lay.addWidget(self.txt_refined, stretch=2)

        self.lbl_suggestion = QLabel('')
        self.lbl_suggestion.setStyleSheet(f"color:{C['teal_b']};font-size:11px;font-style:italic;")
        self.lbl_suggestion.setWordWrap(True); lay.addWidget(self.lbl_suggestion)

        irow = QHBoxLayout()
        self.input_iterate = QLineEdit(); self.input_iterate.setPlaceholderText('Tell Analytica what to push next…')
        self.btn_iterate = QPushButton('ITERATE →'); self.btn_iterate.setObjectName('btn_iterate')
        self.btn_iterate.setEnabled(False)
        irow.addWidget(self.input_iterate); irow.addWidget(self.btn_iterate); lay.addLayout(irow)
        self.btn_iterate.clicked.connect(self._on_iterate)

        arow = QHBoxLayout()
        self.btn_accept_refined = QPushButton('← USE REFINED')
        self.btn_accept_refined.setObjectName('btn_copy'); self.btn_accept_refined.setEnabled(False)
        self.btn_copy_refined = QPushButton('COPY REFINED')
        self.btn_copy_refined.setObjectName('btn_copy'); self.btn_copy_refined.setEnabled(False)
        self.btn_approve = QPushButton('APPROVE → PROCEED TO NOMEN')
        self.btn_approve.setObjectName('btn_iterate'); self.btn_approve.setEnabled(False)
        arow.addWidget(self.btn_accept_refined); arow.addWidget(self.btn_copy_refined)
        arow.addStretch(); arow.addWidget(self.btn_approve); lay.addLayout(arow)

        self.btn_accept_refined.clicked.connect(self.accept_refined)
        self.btn_copy_refined.clicked.connect(self.copy_refined)
        self.btn_approve.clicked.connect(self.proceed_to_nomen)
        return tab

    def _build_nomen_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab); lay.setContentsMargins(16,16,16,16); lay.setSpacing(10)
        lay.addWidget(slbl('▶ Name Candidates'))
        self._btn_group = QButtonGroup(self); self._radios = []
        self.candidates_area = QWidget()
        self.candidates_lay = QVBoxLayout(self.candidates_area)
        self.candidates_lay.setContentsMargins(0,0,0,0); self.candidates_lay.setSpacing(4)
        lay.addWidget(self.candidates_area)
        lay.addWidget(hline())
        lay.addWidget(slbl('▶ Custom Name'))
        self.custom_name = QLineEdit(); self.custom_name.setPlaceholderText('Write the name yourself…')
        lay.addWidget(self.custom_name)
        self.btn_ratify = QPushButton('✒  RATIFY NAME')
        self.btn_ratify.setObjectName('btn_copy'); self.btn_ratify.setEnabled(False)
        lay.addWidget(self.btn_ratify); lay.addStretch()
        self.btn_ratify.clicked.connect(self._on_ratify)
        return tab

    def _build_history_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab); lay.setContentsMargins(16,16,16,16); lay.setSpacing(8)
        lay.addWidget(slbl('▶ Generation History'))
        self.history_list = QListWidget(); self.history_list.setStyleSheet('font-size:11px;')
        lay.addWidget(self.history_list, stretch=1)
        self.history_list.itemClicked.connect(self._load_history)
        br = QHBoxLayout(); self.btn_clear_hist = QPushButton('CLEAR HISTORY')
        br.addWidget(self.btn_clear_hist); br.addStretch(); lay.addLayout(br)
        self.btn_clear_hist.clicked.connect(self._clear_history)
        return tab

    # ── populate ──────────────────────────────────────────────────────────────

    def populate_entity(self, data):
        self.prompt_output.setPlainText(data.get('assembled_prompt', ''))
        role = data.get('role', ''); title = data.get('title', '')
        age  = data.get('age', '').split('—')[0].strip()
        self.lbl_char_info.setText(
            f"<b style='color:{C['amber']}'>{title.upper()}</b>  "
            f"<span style='color:{C['text_dim']}'>{role}</span>"
            f"<br><span style='color:{C['muted']}'>{age}</span>")
        self.lbl_char_info.setTextFormat(Qt.TextFormat.RichText)
        self.cf_name.setText('— awaiting ratification —'); self.cf_title.setText(title)
        self.cf_role.setText(role)
        self.cf_purpose.setPlainText(data.get('purpose', ''))
        self.cf_nature.setPlainText(data.get('lore_nature', ''))
        self.cf_aura.setPlainText(data.get('lore_aura', ''))
        traits = data.get('traits', {})
        self.cf_traits.setText('  '.join(f"{k[:3].upper()} {v:.2f}" for k,v in traits.items()))
        self.btn_send_analytica.setEnabled(True)

    def set_name(self, name): self.cf_name.setText(name)

    def populate_analytica(self, result):
        score = result.get('score', 0)
        color = C['green_b'] if score >= 7 else C['amber'] if score >= 5 else C['red']
        self.lbl_score.setText(f"{score:.1f}")
        self.lbl_score.setStyleSheet(f"color:{color};font-size:22px;font-weight:bold;")
        self.txt_reasoning.setPlainText(result.get('reasoning', ''))
        self.txt_lore_verdict.setPlainText(result.get('lore_verdict', ''))
        self.txt_refined.setPlainText(result.get('refined_prompt', ''))
        self.lbl_suggestion.setText(f"→ {result.get('next_iteration_suggestion','')}")

        while self.weakness_row.count():
            item = self.weakness_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for w in result.get('weaknesses', [])[:6]:
            tag = QLabel(w); tag.setObjectName('weakness_tag'); self.weakness_row.addWidget(tag)
        self.weakness_row.addStretch()

        while self.lore_flag_row.count():
            item = self.lore_flag_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for f in result.get('lore_flags', [])[:6]:
            tag = QLabel(f)
            tag.setStyleSheet(
                f"color:{C['teal_b']};background:rgba(58,112,112,0.12);"
                f"border:1px solid rgba(58,112,112,0.3);padding:2px 7px;font-size:10px;")
            self.lore_flag_row.addWidget(tag)
        self.lore_flag_row.addStretch()

        refined = result.get('refined_prompt', '')
        self.btn_accept_refined.setEnabled(bool(refined))
        self.btn_copy_refined.setEnabled(bool(refined))
        self.btn_iterate.setEnabled(True); self.btn_approve.setEnabled(True)
        self.btn_submit_score.setEnabled(True)
        self.slider_user.setValue(0); self.lbl_user_val.setText('—')

    def populate_nomen(self, candidates):
        while self.candidates_lay.count():
            item = self.candidates_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for btn in self._radios: self._btn_group.removeButton(btn)
        self._radios.clear()
        for name in candidates:
            rb = QRadioButton(name)
            self._btn_group.addButton(rb); self._radios.append(rb)
            self.candidates_lay.addWidget(rb)
        if self._radios: self._radios[0].setChecked(True)
        self.custom_name.clear(); self.btn_ratify.setEnabled(True)

    def get_prompt(self): return self.prompt_output.toPlainText().strip()

    def clear_all(self):
        self.prompt_output.clear()
        self.lbl_char_info.setText('— no entity generated yet —')
        for lbl in [self.cf_name, self.cf_title, self.cf_role, self.cf_traits]: lbl.setText('—')
        for te in [self.cf_purpose, self.cf_nature, self.cf_aura]: te.clear()
        self.lbl_score.setText('—')
        self.lbl_score.setStyleSheet(f"color:{C['muted']};font-size:22px;font-weight:bold;")
        self.txt_reasoning.clear(); self.txt_lore_verdict.clear()
        self.txt_refined.clear(); self.lbl_suggestion.setText('')
        self.btn_send_analytica.setEnabled(False)
        self.btn_iterate.setEnabled(False); self.btn_approve.setEnabled(False)
        self.btn_accept_refined.setEnabled(False); self.btn_copy_refined.setEnabled(False)
        self.btn_submit_score.setEnabled(False)
        for row in [self.weakness_row, self.lore_flag_row]:
            while row.count():
                item = row.takeAt(0)
                if item.widget(): item.widget().deleteLater()
        while self.candidates_lay.count():
            item = self.candidates_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for btn in self._radios: self._btn_group.removeButton(btn)
        self._radios.clear(); self.btn_ratify.setEnabled(False)
        self.tabs.setCurrentIndex(0)

    def _on_iterate(self):
        text = self.input_iterate.text().strip()
        if text: self.input_iterate.clear(); self.iterate_requested.emit(text)

    def _on_ratify(self):
        custom = self.custom_name.text().strip()
        if custom: self.name_ratified.emit(custom); return
        for rb in self._radios:
            if rb.isChecked(): self.name_ratified.emit(rb.text()); return

    def _load_history(self, item):
        e = item.data(Qt.ItemDataRole.UserRole)
        if e and e.get('original_prompt'):
            self.prompt_output.setPlainText(e['original_prompt']); self.tabs.setCurrentIndex(0)

    def _clear_history(self):
        if QMessageBox.question(
            self, 'Clear History', 'Clear all history?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            if hasattr(learning_engine, 'clear_history'): learning_engine.clear_history()
            self.history_list.clear()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class EntitexRefinedApp(QMainWindow):
    _gen_done = pyqtSignal(dict)
    _gen_err  = pyqtSignal(str)
    _ana_done = pyqtSignal(dict)
    _ana_err  = pyqtSignal(str)
    _nom_done = pyqtSignal(list)
    _nom_err  = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        _ensure_dirs()
        self.setWindowTitle('Entitex Refined  ·  Entity Forge')
        self.setMinimumSize(1100, 720); self.resize(1400, 860)

        self._phase = 'SEMEN'; self._completed = []
        self._entity = {}; self._gen_id = ''
        self._gen_w = None; self._ana_w = None; self._nom_w = None

        self._gen_done.connect(self._on_gen_done)
        self._gen_err.connect(self._on_error)
        self._ana_done.connect(self._on_ana_done)
        self._ana_err.connect(self._on_error)
        self._nom_done.connect(self._on_nom_done)
        self._nom_err.connect(self._on_error)

        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(STYLESHEET)
        spl = QSplitter(Qt.Orientation.Horizontal); spl.setHandleWidth(4)
        self.sidebar = Sidebar()
        self.content = MainContent()
        spl.addWidget(self.sidebar); spl.addWidget(self.content)
        spl.setSizes([360, 900])
        spl.setStretchFactor(0, 0); spl.setStretchFactor(1, 1)
        spl.setCollapsible(0, False); spl.setCollapsible(1, False)

        wrapper = QWidget()
        wl = QVBoxLayout(wrapper); wl.setContentsMargins(0,0,0,0); wl.setSpacing(0)
        wl.addWidget(spl, stretch=1)
        self.phase_bar = PhaseBar()
        self.phase_bar.setFixedHeight(28)
        self.phase_bar.setStyleSheet(f"background:{C['panel']};border-top:1px solid {C['border']};")
        wl.addWidget(self.phase_bar)

        self.setCentralWidget(wrapper)
        self.setStatusBar(QStatusBar())

        self.sidebar.btn_forge.clicked.connect(self._start_gen)
        self.sidebar.btn_random.clicked.connect(self._random_forge)
        self.sidebar.btn_copy.clicked.connect(self._copy_prompt)
        self.sidebar.btn_clear.clicked.connect(self._clear)

        self.content.send_to_analytica.connect(self._send_to_analytica)
        self.content.iterate_requested.connect(self._on_iterate)
        self.content.proceed_to_nomen.connect(self._go_nomen)
        self.content.name_ratified.connect(self._on_name_ratified)
        self.content.accept_refined.connect(self._accept_refined)
        self.content.copy_refined.connect(self._copy_refined)
        self.content.btn_submit_score.clicked.connect(self._submit_score)

        QShortcut(QKeySequence('F5'), self).activated.connect(self._start_gen)
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(self._start_gen)
        QShortcut(QKeySequence('Ctrl+Shift+R'), self).activated.connect(self._random_forge)

        self.phase_bar.set_phase('SEMEN', [])
        self._status('The forge awaits.')

    def _set_phase(self, p): self._phase = p; self.phase_bar.set_phase(p, self._completed)
    def _done(self, p):
        if p not in self._completed: self._completed.append(p)
    def _busy(self):
        return any(w and w.isRunning() for w in [self._gen_w, self._ana_w, self._nom_w])

    def _start_gen(self):
        if self._busy(): return
        self._entity = {}; self._gen_id = str(uuid.uuid4())[:8]; self._completed = []
        self.content.clear_all(); self.sidebar.btn_copy.setEnabled(False)
        self.content.progress_bar.show(); self._set_phase('GENERATIO')
        self._status('⚗  Forging entity…')
        self._gen_w = GeneratioWorker(
            inc=self.sidebar.inclinatio,
            archetype_key=self.sidebar.archetype_key,
            overrides=self.sidebar.overrides)
        self._gen_w.progress.connect(self._status)
        self._gen_w.finished.connect(lambda d: self._gen_done.emit(d))
        self._gen_w.errored.connect(lambda e: self._gen_err.emit(e))
        self._gen_w.start()

    def _random_forge(self): self.sidebar.randomize(); self._start_gen()

    def _on_gen_done(self, data):
        data['_gen_id'] = self._gen_id; self._entity = data
        self.content.populate_entity(data)
        self.content.progress_bar.hide()
        self._done('GENERATIO'); self._set_phase('ANALYTICA')
        self.sidebar.btn_copy.setEnabled(True)
        self._status(f"✦  Forged: {data.get('title','')} — {data.get('role','')[:50]}")
        if self.sidebar.auto_analyse:
            QTimer.singleShot(300, self._send_to_analytica)

    def _send_to_analytica(self):
        if self._busy() or not self._entity: return
        self._entity['assembled_prompt'] = self.content.get_prompt()
        self.content.progress_bar.show(); self._status('⚗  The Analytica reviews…')
        self._ana_w = AnalyticaWorker(entity=self._entity, gen_id=self._gen_id)
        self._ana_w.progress.connect(self._status)
        self._ana_w.finished.connect(lambda d: self._ana_done.emit(d))
        self._ana_w.errored.connect(lambda e: self._ana_err.emit(e))
        self._ana_w.start()

    def _on_iterate(self, feedback):
        if self._busy(): return
        self.content.progress_bar.show()
        self._ana_w = AnalyticaWorker(
            entity=self._entity, gen_id=self._gen_id, iterate_feedback=feedback)
        self._ana_w.progress.connect(self._status)
        self._ana_w.finished.connect(lambda d: self._ana_done.emit(d))
        self._ana_w.errored.connect(lambda e: self._ana_err.emit(e))
        self._ana_w.start()

    def _on_ana_done(self, result):
        self.content.populate_analytica(result)
        self.content.progress_bar.hide(); self.content.tabs.setCurrentIndex(1)
        self._done('ANALYTICA')
        score = result.get('score', 0)
        nw = len(result.get('weaknesses',[])); nf = len(result.get('lore_flags',[]))
        try:
            learning_engine.record(
                self._entity,
                result.get('weaknesses',[]) + result.get('lore_flags',[]))
        except Exception as e: log.warning(f'learning_engine: {e}')
        self._status(
            f'✦  Analytica: {score:.1f}/10  ·  {nw} weakness(es)  ·  {nf} lore flag(s)'
            f'  ·  Iterate or Approve → NOMEN')

    def _submit_score(self):
        val = self.content.slider_user.value()
        if val == 0: return
        try: learning_engine.update_user_score(self._gen_id, float(val))
        except Exception: pass
        self.content.btn_submit_score.setEnabled(False)
        self._status(f'User score {val}/10 saved.')

    def _go_nomen(self):
        if self._busy(): return
        self._done('ANALYTICA'); self._set_phase('NOMEN')
        self.content.progress_bar.show(); self._status('⚗  The naming oracle invents names…')
        self._nom_w = NomenWorker(entity=self._entity)
        self._nom_w.progress.connect(self._status)
        self._nom_w.finished.connect(lambda d: self._nom_done.emit(d))
        self._nom_w.errored.connect(lambda e: self._nom_err.emit(e))
        self._nom_w.start()

    def _on_nom_done(self, candidates):
        self.content.populate_nomen(candidates)
        self.content.progress_bar.hide(); self.content.tabs.setCurrentIndex(2)
        self._status('✦  Name candidates surfaced — ratify to complete.')

    def _on_name_ratified(self, name):
        if not name: return
        self._entity['display_name'] = name.upper()
        self._entity['entity_id']    = re.sub(r'\W+', '_', name.lower().strip())
        self.content.set_name(name.upper())
        _save_used_name(name)
        self._done('NOMEN'); self._set_phase('ELABORATIO'); self._done('ELABORATIO')
        try: _vault_save(self._entity)
        except Exception as e: log.warning(f'vault_save: {e}')
        _log({'entity_id': self._entity.get('entity_id','?'),
              'display_name': name.upper(), 'role': self._entity.get('role','')})
        self.content.tabs.setCurrentIndex(0)
        self._status(f'🜲  Complete: {name.upper()} — copy the prompt to your image generator.')

    def _copy_prompt(self):
        txt = self.content.get_prompt()
        if txt: QApplication.clipboard().setText(txt); self._status('Prompt copied.')

    def _copy_refined(self):
        txt = self.content.txt_refined.toPlainText()
        if txt: QApplication.clipboard().setText(txt); self._status('Refined prompt copied.')

    def _accept_refined(self):
        txt = self.content.txt_refined.toPlainText()
        if txt:
            self.content.prompt_output.setPlainText(txt)
            self._entity['assembled_prompt'] = txt
            self.content.tabs.setCurrentIndex(0); self._status('Refined prompt loaded.')

    def _clear(self):
        self._entity = {}; self._gen_id = ''; self._completed = []; self._phase = 'SEMEN'
        self.content.clear_all(); self.sidebar.btn_copy.setEnabled(False)
        self.phase_bar.set_phase('SEMEN', []); self._status('Cleared. The forge awaits.')

    def _on_error(self, err):
        self.content.progress_bar.hide(); self._status(f'✕  {err[:140]}')

    def _status(self, msg): self.statusBar().showMessage(f'  {msg}')


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Entitex Refined')
    win = EntitexRefinedApp()
    win.show()
    sys.exit(app.exec())
