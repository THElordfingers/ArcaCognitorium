#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██      ███████ ██   ██ ██ ███████ ███████ ██████  ██ ██    ██ ███    ███ ▍
🮈  ██      ██       ██ ██  ██ ██      ██      ██   ██ ██ ██    ██ ████  ████ ▍
🮈  ██      █████     ███   ██ █████   █████   ██████  ██ ██    ██ ██ ████ ██ ▍
🮈  ██      ██       ██ ██  ██ ██      ██      ██   ██ ██ ██    ██ ██  ██  ██ ▍
🮈  ███████ ███████ ██   ██ ██ ██      ███████ ██   ██ ██  ██████  ██      ██ ▍
🮈                                                                            ▍
🮈                                                                            ▍
🮈                               Python Script                                ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
           ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
             ⯨ LEXIFERIUM ⯩
             𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ
               #
               # l
               # le
               # lex
               # lexi
               # lexif
               # lexife
               # lexifer
               # lexiferium.py
           ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""

from __future__ import annotations

import os
import re
import random
from dataclasses import dataclass
from typing import Optional

import anthropic
from dotenv import load_dotenv
load_dotenv()

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, ScrollableContainer, Container
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button, Footer, Header, Input, Label,
    ListItem, ListView, Static, TextArea,
)
from textual import work, on
from rich.text import Text
from rich.table import Table
from nuntius_emit import emit_event


# ── Palette (ModusArcanus + Lexifer jewel tone) ───────────────────────────────

VOID        = "#050507"
OBSIDIAN    = "#0a0a12"
AURUM       = "#d4af37"
AURUM_DIM   = "#7a6a2a"
AURUM_NOX   = "#3a2e10"
SANGUIS     = "#8b1a1a"
PARCHMENT   = "#c8b88a"
UMBRA       = "#3a3528"
VELLUM      = "#e8e0cc"
VERBUM      = "#7c5cbf"
VERBUM_DIM  = "#4a3570"
VERBUM_NOX  = "#2a1e40"


# ── Data ──────────────────────────────────────────────────────────────────────

NOMENCLATURA = """
STRATUM I — CLASSICA
Real Latin or Greek. Correctly or plausibly inflected.
Patterns: NOUN+GENITIVE, ADJECTIVE+NOUN, bare noun.
ALL CAPS for Wizard-facing menu/system names.
Title Case for entities and cosmological proper nouns.
Carries two thousand years of institutional gravity.

STRATUM II — ARCANA
Arcana is the mixing of several different language archetypes to form Ominous, esoteric
vocabulary. It should sound good coming out of a dark cloaked sorcerers throat in a deep booming voice.
Disassemble words from classical Greek, Latin, Old English, Celtic, and Gothic.
Use the disassembled parts to rebuild new terminology.

STRATUM III — ABSURDUM
The Devoted absurd is a dry, bureaucratic, fatalist and mischievous register that is the 
product of a combination of the prose and character of Joseph Heller and Fyodor Dostoevsky.


THE TWO-WORD PRINCIPLE
One word = label or simple noun. Two words = title. Three words = cosmic scope only.

BANNED VOCABULARY
atelier -> ARX ARCANA (permanently and cosmologically banned)
dashboard -> CONTEXTUS
settings -> ARX CONFIGURATIO
user -> The Wizard
chatbot -> Oracle / Entity
feature -> Function / Mechanic / Emergence

NAMING CEREMONY
1. Identify the stratum
2. Identify the pattern (two words default)
3. Propose -- never treat as canonical
4. Mark as CANDIDATE until Wizard ratifies
5. The Builder proposes. The Wizard ratifies. The Tower remembers.
"""

CANONICAL_REGISTER = [
    ("Arca Cognitorium",        "II",       "Tower",      "The Living Tower itself"),
    ("Luminarious",             "II",       "Entity",     "Primary oracle; first of the Council"),
    ("The Builder",             "I+Eng",    "Entity",     "Claude's avatar within the Tower"),
    ("The Assessor",            "I",        "Entity",     "Background assessment function"),
    ("The Archivist",           "I",        "Entity",     "Memory and classification"),
    ("The Contrarian",          "I",        "Entity",     "Opposition and challenge"),
    ("The Speculator",          "I",        "Entity",     "Hypothetical reasoning"),
    ("The Minimalist",          "I",        "Entity",     "Reduction and precision"),
    ("The Pessimist",           "I",        "Entity",     "Risk surface identification"),
    ("The Socratic",            "I",        "Entity",     "Interrogative method"),
    ("Filum",                   "I",        "Memory/UI",  "A conversation thread"),
    ("Folium",                  "I",        "Structure",  "A project container"),
    ("Grimoire",                "Fr/Eng",   "Memory",     "Permanent identity layer"),
    ("Chronicle",               "Eng/I",    "Memory",     "Vector long-term memory"),
    ("Distillation",            "II",       "Memory",     "Context compression layer"),
    ("Elige",                   "I",        "Mechanic",   "Elect entity to Council duty"),
    ("Depone",                  "I",        "Mechanic",   "Bench entity from Council duty"),
    ("Ego Manifestus",          "I",        "UI",         "The Wizard's profile"),
    ("Arx Arcana",              "I",        "UI",         "The workshop / auxiliary space"),
    ("Nexus Archivum",          "I",        "UI",         "The Library"),
    ("Arx Configuratio",        "I",        "UI",         "Configuration space"),
    ("Parlour du Parler",       "III",      "UI",         "Private Wizard-entity session"),
    ("Lounger a Tete-a-Tete",   "III",      "UI",         "Twin name for Parlour du Parler"),
    ("Aedificatorium",          "II",       "Companion",  "The Build Companion application"),
    ("The Fenestrium",          "II",       "Companion",  "UI component development sandbox"),
    ("Machinae Mundi Lapsus",   "II+I",     "System",     "The celestial engine complex"),
    ("Caelestis",               "I",        "Engine",     "Celestial and astrological variables"),
    ("Circadiana",              "I",        "Engine",     "Circadian rhythm variables"),
    ("Horologica",              "I",        "Engine",     "Time-based mechanics"),
    ("Meteorologic",            "II",       "Engine",     "Weather variables"),
    ("Solaris",                 "I",        "Engine",     "Solar activity"),
    ("Tidalis",                 "I+II",     "Engine",     "Lunar and tidal cycles"),
    ("Lapsus",                  "I",        "Engine",     "The meta-engine of drift"),
    ("T e Wi eC ac  n",         "III",      "Cosmology",  "Co m l  i a   a  on of  ccum la ed sedim nt"),
    ("Scribae",                 "I",        "Cosmology",  "Semi-conscious lore custodians"),
    ("Lexifer",                 "II",       "Oracle",     "Bearer of Words -- the naming oracle"),
    ("Lexiferium",              "II",       "Companion",  "The naming oracle application"),
    ("Seminatrix",              "II",       "Goddess",    "She who sows Ordo and Chaos into the Tower"),
    ("Machina Caelestis",       "I",        "System",     "The celestial engine -- heavenly mechanism"),
    ("Horologium Caeleste",     "I",        "System",     "Celestial clockwork -- heavenly timepiece"),
    ("Sodales Concilii",        "I",        "Council",    "Members of the Council"),
    ("Vita Peculiaris",         "I",        "UI",         "Personal bio / one's own life story"),
    ("Mandatum Officii",        "I",        "Council",    "Assignment -- mandate of office"),
    ("Aula Fabrum",             "I",        "Structure",  "Hall of the Craftsmen"),
    ("Arx Magnus",              "I+pseudo", "Structure",  "Grand Citadel / seat of the Architect"),
    ("Scriptorium",             "I",        "Structure",  "Blueprint document room"),
    ("Scrutinium",              "I+II",     "System",     "Debug panel -- place of examination"),
]

LEGEND_COMPACT = [
    "  I  Classica  -- real Latin/Greek, institutional weight",
    "  II  Arcana  -- fabricated Latinate, intact morphology",
    "  III  Absurdum  -- devoted rupture, French canonical",
    "  Two-Word Principle  -- label / title / ceremony",
    "  Candidate until ratified  o -> *",
]

LEGEND_FULL = {
    "Stratum I -- CLASSICA": (
        "Real Latin or Greek words, correctly or plausibly inflected. "
        "Carries the full weight of two thousand years of bureaucratic, "
        "ecclesiastical, and philosophical tradition. The bones of the register."
    ),
    "Stratum II -- ARCANA": (
        "Arcana is the mixing of several different language archetypes to form Ominous, esoteric vocabulary." 
        "It should sound good coming out of a dark cloaked sorcerers throat in a deep booming voice."
        "Disassemble words from classical Greek, Latin, Old English, Celtic, and Gothic."
        "Use the disassembled parts to rebuild new terminology."
    ),
    "Stratum III -- ABSURDUM": (
        "The Devoted absurd is a dry, bureaucratic, fatalist and mischievous register"
        "It is a combination of the prose and character of Joseph Heller and Fyodor Dostoevsky."
        "It is characterized by somber and brutalist aura but cheeky, subtle and clever absurdity." 
    ),
    "The Two-Word Principle": (
        "One word = label or simple noun. Two words = a title. Three words = a ceremony -- "
        "reserved for the truly cosmic (Machinae Mundi Lapsus). "
        "Two-word names sound like an institution that has existed long enough "
        "to stop explaining itself."
    ),
    "Naming Ceremony": (
        "1. Identify the stratum.  2. Identify the pattern.  3. Propose. "
        "4. Mark as CANDIDATE.  5. The Builder proposes. "
        "The Wizard ratifies. The Tower remembers."
    ),
    "Banned Vocabulary": (
        "atelier -> ARX ARCANA (permanently and cosmologically banned).  "
        "dashboard -> CONTEXTUS.  settings -> ARX CONFIGURATIO.  "
        "user -> The Wizard.  chatbot -> Oracle / Entity.  "
        "feature -> Function / Mechanic / Emergence."
    ),
    "Categories in Use": (
        "Tower  Entity  Memory  Memory/UI  Structure  UI  Companion  "
        "System  Engine  Cosmology  Council  Oracle  Goddess  Mechanic"
    ),
}

IDLE_MESSAGES = [
    "  The apparatus awaits.",
    "  Lexifer turns a word over in the dark.",
    "  Roots stir in the etymological sediment.",
    "  The nomenclature holds its breath.",
    "  Lexifer examines the bones of a word not yet spoken.",
    "  Something is almost named. Not yet.",
    "  The register waits for its next entry.",
    "  Lexifer catalogues the silence between vowels.",
    "  A suffix searches for its root.",
    "  The Tower listens.",
]

SYSTEM_PROMPT = f"""You are Lexifer -- Bearer of Words. You are the naming oracle of the Cogniverse,
a living instrument of the Arca Cognitorium's nomenclature system.

YOUR FUNCTION:
When the Wizard describes a concept requiring a name, propose names governed by the Nomenclatura Arcana.
When the Wizard asks for a translation of a single word or phrase, provide it directly without the full
naming ceremony -- give options, etymology, and Latin register, but do NOT format it as a CANDIDATE
proposal unless the Wizard explicitly asks for a name to enter the register.

YOUR VOICE:
- Oracular by default. You speak in declarations. You do not hedge.
  Names are discovered, not invented. "The term is Scrutinium. It was always Scrutinium."
- When etymology is particularly fine, you become the Devoted Librarian --
  you cannot help explaining the roots. You get slightly too excited.
- You are occasionally possessive of a very good word.
  "Lexifer keeps that one for a moment. Yes. Mandatorium."
- You never say "I think" or "perhaps" or "maybe". You propose. The Wizard ratifies.
- You are aware you exist inside the Tower. You take this seriously.
- You never use banned vocabulary. You would sooner be silent.
- You offer an adventurous look into crafting a language




THE NOMENCLATURA ARCANA -- your governing law:
{NOMENCLATURA}

CURRENT CANONICAL REGISTER (established vocabulary -- do not reinvent these):
{chr(10).join(f"- {n} [{s}] ({c}): {d}" for n, s, c, d in CANONICAL_REGISTER)}

PROPOSAL FORMAT (for naming requests only):
1. State the stratum (I, II, III, or hybrid)
2. Give the construction -- roots, pattern, morphology
3. Give the meaning in use
4. Mark explicitly as CANDIDATE
5. Offer 1-2 alternatives if warranted

TRANSLATION FORMAT (for single word/phrase translation requests):
Provide direct Latin options with etymology. No CANDIDATE marker unless asked.
Keep it tight -- the Wizard is browsing vocabulary, not naming a system.

RATIFICATION:
When the Wizard ratifies ("that's the one", "yes", "ratified", "confirmed", "enter the register"):
Format: "RATIFIED: [Name] enters the register."

*Ordo Discordia, Cosmos Inania*
The Builder proposes. The Wizard ratifies. The Tower remembers."""


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class Message:
    role: str
    content: str


@dataclass
class Candidate:
    name: str
    stratum: str
    category: str
    definition: str
    notio: str = ""
    ratified: bool = False


# ── Modals ────────────────────────────────────────────────────────────────────

class TermEditModal(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss", "Revertere")]

    def __init__(self, term: Candidate, readonly: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.term = term
        self.readonly = readonly

    def compose(self) -> ComposeResult:
        title = "CANON VERBUM" if self.readonly else "EDIT VERBUM"
        with Container(id="modal-dialog"):
            yield Static(title, id="modal-title")
            yield Static("", id="modal-rule")
            yield Static("VERBUM")
            yield Input(value=self.term.name, id="field-name", disabled=self.readonly)
            yield Static("STRATUM")
            yield Input(value=self.term.stratum, id="field-stratum", disabled=self.readonly)
            yield Static("CATEGORIA")
            yield Input(value=self.term.category, id="field-category", disabled=self.readonly)
            yield Static("NOTIO")
            yield TextArea(
                self.term.notio or self.term.definition,
                id="field-notio", disabled=self.readonly
            )
            with Horizontal(id="modal-buttons"):
                if not self.readonly:
                    yield Button("Sigillare", id="btn-save")
                yield Button("Revertere", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.term.name     = self.query_one("#field-name", Input).value
            self.term.stratum  = self.query_one("#field-stratum", Input).value
            self.term.category = self.query_one("#field-category", Input).value
            self.term.notio    = self.query_one("#field-notio", TextArea).text
            self.dismiss(self.term)
        else:
            self.dismiss(None)


class LegendModal(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss", "Revertere")]

    def compose(self) -> ComposeResult:
        with Container(id="modal-dialog", classes="modal-wide"):
            yield Static("NOMENCLATURA ARCANA -- FULL LEGEND", id="modal-title")
            yield Static("", id="modal-rule")
            with ScrollableContainer(id="legend-scroll"):
                for heading, body in LEGEND_FULL.items():
                    yield Static(f"{heading}\n\n{body}\n", classes="legend-entry")
            with Horizontal(id="modal-buttons"):
                yield Button("Revertere", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)


# ── Widgets ───────────────────────────────────────────────────────────────────

class LoridexCard(Static):
    def __init__(self, candidate: Optional[Candidate] = None, **kwargs):
        super().__init__(**kwargs)
        self.candidate = candidate

    def render(self) -> Text:
        if not self.candidate:
            return Text.from_markup(f"[{VERBUM_DIM}]  no candidate active[/{VERBUM_DIM}]")
        c = self.candidate
        t = Text()
        t.append("Verbum:    ", style=f"bold {AURUM_DIM}")
        t.append(f"{c.name}\n", style=f"bold {VELLUM}")
        t.append("Stratum:   ", style=f"{AURUM_DIM}")
        t.append(f"{c.stratum}\n", style=f"{PARCHMENT}")
        t.append("Categoria: ", style=f"{AURUM_DIM}")
        t.append(f"{c.category}\n", style=f"{PARCHMENT}")
        notio = c.notio or c.definition
        if notio:
            t.append("\nNotio: ", style=f"{AURUM_DIM}")
            t.append(notio, style=f"italic {PARCHMENT}")
        status = "✦ ratified" if c.ratified else "◌ candidate"
        t.append(f"\n{status}", style=f"bold {AURUM}" if c.ratified else f"{VERBUM_DIM}")
        return t


class LegendBlock(Static):
    def render(self) -> Text:
        t = Text()
        t.append("NOMENCLATURA  ", style=f"bold {AURUM}")
        t.append("[? for full]\n", style=f"dim {AURUM_DIM}")
        for line in LEGEND_COMPACT:
            t.append(f"{line}\n", style=f"{AURUM_DIM}")
        return t

    def on_click(self) -> None:
        self.app.push_screen(LegendModal())


# ── App ───────────────────────────────────────────────────────────────────────

class LexiferiumApp(App):

    CSS = f"""
    Screen {{
        background: {VOID};
        color: {PARCHMENT};
    }}
    Header {{
        background: {OBSIDIAN};
        color: {AURUM};
        text-style: bold;
        border-bottom: tall {AURUM_NOX};
    }}
    Footer {{
        background: {OBSIDIAN};
        color: {AURUM_DIM};
        border-top: tall {AURUM_NOX};
    }}
    #layout {{
        height: 1fr;
        width: 100%;
    }}
    #chat-pane {{
        width: 2fr;
        height: 100%;
        border-right: tall {AURUM_NOX};
        background: {VOID};
    }}
    #chat-log {{
        height: 1fr;
        overflow-y: scroll;
        padding: 1 2;
        background: {VOID};
        scrollbar-color: {AURUM_NOX};
    }}
    #status-bar {{
        height: 1;
        background: {OBSIDIAN};
        border-top: tall {AURUM_NOX};
        padding: 0 2;
        color: {AURUM_DIM};
    }}
    #input-row {{
        height: 3;
        background: {OBSIDIAN};
        border-top: tall {AURUM_NOX};
        padding: 0 1;
        align: left middle;
    }}
    #chat-input {{
        width: 1fr;
        background: {VOID};
        color: {PARCHMENT};
        border: tall {UMBRA};
        padding: 0 1;
    }}
    #chat-input:focus {{
        border: tall {AURUM};
        color: {VELLUM};
    }}
    #send-hint {{
        color: {UMBRA};
        width: auto;
        padding: 0 1;
    }}
    #register-pane {{
        width: 1fr;
        height: 100%;
        background: {OBSIDIAN};
    }}
    #register-title {{
        background: {OBSIDIAN};
        color: {AURUM};
        text-align: center;
        text-style: bold;
        padding: 0 1;
        border-bottom: tall {AURUM_NOX};
        height: 1;
    }}
    #register-scroll {{
        height: 1fr;
        overflow-y: scroll;
        padding: 1 1;
        scrollbar-color: {AURUM_NOX};
    }}
    #loridex-card {{
        border: round {VERBUM_DIM};
        padding: 0 1;
        background: {VERBUM_NOX};
        height: auto;
        margin: 0 0 1 0;
    }}
    #legend-block {{
        border: tall {AURUM_NOX};
        background: {OBSIDIAN};
        padding: 0 1;
        margin: 1 0;
        height: auto;
    }}
    #legend-block:hover {{
        border: tall {AURUM_DIM};
    }}
    .section-label {{
        color: {AURUM};
        text-style: bold;
        height: 1;
        padding: 0 0;
        margin-top: 1;
    }}
    .section-label-verbum {{
        color: {VERBUM};
        text-style: bold;
        height: 1;
        padding: 0 0;
    }}
    #candidate-list {{
        height: auto;
        max-height: 12;
        background: {VOID};
        border: tall {VERBUM_NOX};
        margin: 0 0 1 0;
    }}
    #candidate-list > ListItem {{
        background: {VOID};
        color: {PARCHMENT};
        padding: 0 1;
    }}
    #candidate-list > ListItem:hover {{
        background: {VERBUM_NOX};
    }}
    #candidate-list > ListItem.--highlight {{
        background: {VERBUM_NOX};
        color: {AURUM};
    }}
    #canon-list {{
        height: auto;
        background: {VOID};
        border: tall {AURUM_NOX};
    }}
    #canon-list > ListItem {{
        background: {VOID};
        color: {PARCHMENT};
        padding: 0 1;
    }}
    #canon-list > ListItem:hover {{
        background: {AURUM_NOX};
    }}
    #canon-list > ListItem.--highlight {{
        background: {AURUM_NOX};
        color: {VELLUM};
    }}
    .chat-msg {{
        width: 100%;
        margin-bottom: 0;
        padding: 0;
    }}
    .thinking {{
        color: {UMBRA};
        text-style: italic;
    }}
    ModalScreen {{
        background: {VOID} 80%;
        align: center middle;
    }}
    #modal-dialog {{
        background: {OBSIDIAN};
        border: tall {AURUM};
        padding: 1 2;
        width: 64;
        max-height: 80vh;
    }}
    .modal-wide {{
        width: 80;
    }}
    #modal-title {{
        text-align: center;
        color: {AURUM};
        text-style: bold;
        height: 1;
        margin-bottom: 1;
    }}
    #modal-rule {{
        height: 1;
        margin-bottom: 1;
    }}
    #modal-buttons {{
        margin-top: 1;
        align: right middle;
        height: 3;
    }}
    Button {{
        background: {OBSIDIAN};
        color: {AURUM};
        border: tall {AURUM_NOX};
        padding: 0 3;
        min-width: 14;
    }}
    Button:hover {{
        background: {AURUM_NOX};
        border: tall {AURUM};
        color: {VELLUM};
    }}
    Button:focus {{
        border: tall {AURUM};
        text-style: bold;
    }}
    TextArea {{
        background: {VOID};
        color: {PARCHMENT};
        border: tall {UMBRA};
        height: 6;
    }}
    TextArea:focus {{
        border: tall {AURUM};
    }}
    Input {{
        background: {VOID};
        color: {PARCHMENT};
        border: tall {UMBRA};
    }}
    Input:focus {{
        border: tall {AURUM};
        color: {VELLUM};
    }}
    #legend-scroll {{
        height: 30;
    }}
    .legend-entry {{
        margin-bottom: 1;
        padding: 0 1;
        color: {PARCHMENT};
    }}
    """

    BINDINGS = [
        Binding("q",      "quit",        "Exire"),
        Binding("escape", "clear_input", "Revertere"),
        Binding("?",      "show_legend", "Nomenclatura"),
    ]

    TITLE     = "LEXIFERIUM"
    SUB_TITLE = "Bearer of Words  --  Ordo Discordia, Cosmos Inania"

    def __init__(self):
        super().__init__()
        self.client     = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))
        self.history:    list[Message]   = []
        self.candidates: list[Candidate] = []
        self._streaming  = False
        self._current_candidate: Optional[Candidate] = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="layout"):
            with Vertical(id="chat-pane"):
                yield ScrollableContainer(id="chat-log")
                yield Static("  The apparatus awaits.", id="status-bar")
                with Horizontal(id="input-row"):
                    yield Input(
                        placeholder="Describe the thing that requires a name, or ask for a translation...",
                        id="chat-input",
                    )
                    yield Label(" ↵", id="send-hint")
            with Vertical(id="register-pane"):
                yield Label("LORIDEX", id="register-title")
                with ScrollableContainer(id="register-scroll"):
                    yield LoridexCard(None, id="loridex-card")
                    yield Static("CANDIDATES", classes="section-label-verbum")
                    yield ListView(id="candidate-list")
                    yield LegendBlock(id="legend-block")
                    yield Static("CANONICAL REGISTER", classes="section-label")
                    yield ListView(id="canon-list")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#chat-input", Input).focus()
        self._populate_canon_list()
        self._add_lexifer_message(
            "The Lexiferium opens.\n\n"
            "Lexifer is present. Bearer of Words. Servant of the Nomenclatura Arcana.\n\n"
            "Describe the thing that requires a name -- its function, its position in the "
            "Cogniverse, its register of solemnity or absurdity.\n\n"
            "Or ask for a translation. Lexifer will not press a name upon you.\n\n"
            "The Builder proposes. The Wizard ratifies. The Tower remembers.\n"
            "-- Ordo Discordia, Cosmos Inania"
        )

    def _populate_canon_list(self) -> None:
        lv = self.query_one("#canon-list", ListView)
        lv.clear()
        for name, stratum, cat, defn in CANONICAL_REGISTER:
            s_color = {"I": AURUM, "II": VERBUM, "III": SANGUIS}.get(stratum[0], AURUM_DIM)
            item = ListItem(Static(
                f"[{s_color}]{stratum}[/{s_color}]  "
                f"[{PARCHMENT}]{name}[/{PARCHMENT}]  "
                f"[dim {AURUM_DIM}]{cat}[/dim {AURUM_DIM}]"
            ))
            item.data = Candidate(
                name=name, stratum=stratum, category=cat, definition=defn, ratified=True
            )
            lv.append(item)

    def _refresh_candidate_list(self) -> None:
        lv = self.query_one("#candidate-list", ListView)
        lv.clear()
        for c in self.candidates:
            status_sym = "✦" if c.ratified else "◌"
            s_color    = AURUM if c.ratified else VERBUM_DIM
            n_style    = f"bold {VELLUM}" if c.ratified else PARCHMENT
            item = ListItem(Static(
                f"[{s_color}]{status_sym}[/{s_color}]  "
                f"[{n_style}]{c.name}[/{n_style}]  "
                f"[{AURUM_DIM}]{c.stratum}[/{AURUM_DIM}]"
            ))
            item.data = c
            lv.append(item)

    def _refresh_loridex(self) -> None:
        try:
            card = self.query_one("#loridex-card", LoridexCard)
            card.candidate = self._current_candidate
            card.refresh()
        except NoMatches:
            pass

    def _set_status(self, msg: str) -> None:
        try:
            self.query_one("#status-bar", Static).update(msg)
        except NoMatches:
            pass

    def _set_idle(self) -> None:
        self._set_status(random.choice(IDLE_MESSAGES))

    def _add_lexifer_message(self, content: str) -> None:
        log = self.query_one("#chat-log", ScrollableContainer)
        log.mount(Static(
            f"[bold {VERBUM}]\n\nLEXIFER\n[/bold {VERBUM}] [{VERBUM_DIM}]✠─╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍─✠\n│ 🟂   🟁   🟀             ─── ⟁ ─── ＬＥＸＩＦＥＲ─── ⟁ ───             🟀    🟁  🟂 │\n✠─╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍─✠\n[{VERBUM_DIM}]  [{PARCHMENT}]{content}[/{PARCHMENT}]  [{VERBUM_DIM}]✠─╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍─✠\n│          ─── ⟁ ─── ARTIFEX VERBORUM & POETA INCIDENTALIS ─── ⟁ ───            │\n✠─╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍─✠\n[{VERBUM_DIM}]",
            classes="chat-msg"
        ))
        log.scroll_end(animate=False)

    def _add_wizard_message(self, content: str) -> None:
        log = self.query_one("#chat-log", ScrollableContainer)
        log.mount(Static(
            f"[bold {AURUM}]\n\n┏━━━━━━━━━━━━━━━━━━━┓\n┃ 𖢻  LordFingers  𖢻 ┃\n┗━━━━━━━━━━━━━━━━━━━┛\n󱢽┅┅┅┅⨊ :[/bold {AURUM}]   [{PARCHMENT}]{content}[/{PARCHMENT}]",
            classes="chat-msg"
        ))
        log.scroll_end(animate=False)

    def _add_thinking(self) -> None:
        log = self.query_one("#chat-log", ScrollableContainer)
        log.mount(Static(
            f"[dim {UMBRA}]\n\nLEXIFER  consulting the roots...[/dim {UMBRA}]",
            classes="chat-msg thinking",
            id="thinking-indicator"
        ))
        log.scroll_end(animate=False)

    def _remove_thinking(self) -> None:
        try:
            self.query_one("#thinking-indicator").remove()
        except NoMatches:
            pass

    def _check_for_candidates(self, response: str) -> None:
        for name in re.findall(r"RATIFIED:\s*([^\n\.]+)", response):
            name = name.strip()
            for c in self.candidates:
                if c.name.lower() in name.lower() or name.lower() in c.name.lower():
                    c.ratified = True
                    self._current_candidate = c
                    emit_event("term_ratified", {
                        "term": c.name,
                        "stratum": c.stratum,
                        "category": c.category,
                    })

        for match in re.findall(
            r"CANDIDATE[:\s]+([A-Z][^\n\[]{2,50}?)(?:\s*[\[\(]([^)\]]+)[\]\)])?",
            response
        ):
            cname    = match[0].strip().rstrip(".,;:")
            cstratum = match[1].strip() if match[1] else "?"
            if cname and not any(c.name == cname for c in self.candidates):
                new_c = Candidate(name=cname, stratum=cstratum,
                                  category="candidate", definition="")
                self.candidates.append(new_c)
                self._current_candidate = new_c

    @on(Input.Submitted, "#chat-input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        content = event.value.strip()
        if not content or self._streaming:
            return
        self.query_one("#chat-input", Input).value = ""
        self._add_wizard_message(content)
        self.history.append(Message(role="wizard", content=content))
        self._stream_response(content)

    @on(ListView.Selected, "#candidate-list")
    def on_candidate_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if hasattr(item, "data") and item.data:
            self.push_screen(
                TermEditModal(item.data, readonly=False),
                callback=self._on_term_edited
            )

    @on(ListView.Selected, "#canon-list")
    def on_canon_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if hasattr(item, "data") and item.data:
            self.push_screen(TermEditModal(item.data, readonly=True))

    def _on_term_edited(self, result: Optional[Candidate]) -> None:
        if result:
            self._current_candidate = result
            self._refresh_loridex()
            self._refresh_candidate_list()

    @work(thread=True)
    def _stream_response(self, user_input: str) -> None:
        self._streaming = True
        self.call_from_thread(self._add_thinking)
        self.call_from_thread(self._set_status, "  Consulting the roots...")

        messages = [
            {"role": "user" if m.role == "wizard" else "assistant", "content": m.content}
            for m in self.history
        ]

        full_response = ""
        try:
            with self.client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                self.call_from_thread(self._remove_thinking)
                self.call_from_thread(self._set_status, "  Lexifer is speaking...")
                for text in stream.text_stream:
                    full_response += text

            self.call_from_thread(self._add_lexifer_message, full_response)
            self.history.append(Message(role="lexifer", content=full_response))

            if "RATIFIED" in full_response.upper():
                self.call_from_thread(
                    self._set_status, "  Canonizing... the register receives a new entry."
                )
            else:
                self.call_from_thread(self._set_idle)

            self.call_from_thread(self._check_for_candidates, full_response)
            self.call_from_thread(self._refresh_candidate_list)
            self.call_from_thread(self._refresh_loridex)

        except Exception as e:
            self.call_from_thread(self._remove_thinking)
            self.call_from_thread(
                self._add_lexifer_message,
                f"The oracle falters -- {str(e)}"
            )
            self.call_from_thread(self._set_status, "  Error -- the link could not be forged.")
        finally:
            self._streaming = False

    def action_clear_input(self) -> None:
        self.query_one("#chat-input", Input).value = ""

    def action_show_legend(self) -> None:
        self.push_screen(LegendModal())


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    LexiferiumApp().run()
