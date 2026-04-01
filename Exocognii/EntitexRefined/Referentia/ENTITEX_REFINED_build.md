# ENTITEX — REFINED
## IdeaForge Build Document

*Arca Cognitorium — Exocognii Suite*
*Build Document v1.0*

---

## Table of Contents

1. Overview & Architecture
2. Tech Stack
3. Directory Tree & Database Schema
4. Module Breakdown
5. UI Wireframe
6. Data Flow
7. Code Stubs
8. Error Handling
9. Setup & Testing
10. Packaging
11. Extensibility

---

## 1. Overview & Architecture

ENTITEX — REFINED is a PyQt6 entity package generator for the Arca Cognitorium Tower. It
replaces the current ENTITEX (v0.1) with a name-last generation pipeline: the Wizard sets
disposition sliders and selects archetype, cognitive axis, and role — Claude generates a
complete personality and lore profile with no name — a second Claude instance reviews that
profile in Cogniverse lore register — the Wizard iterates or approves — a third Claude call
surfaces 3–5 name candidates in Nomenclatura register — the Wizard ratifies — then the full
package assembles and the portrait generates. The core inversion from ENTITEX v0.1 is that
identity arrives before the name, mirroring how entities emerge in the Tower itself.

Three ClaudeBox instances run across five pipeline phases. All blocking Claude calls run in
QThread workers. The existing ENTITEX palette, disposition slider system, archetype pool,
portrait pipeline (Freepik), and package output format (role.yaml, traits.yaml, lore.yaml,
profiles fragment, canon fragment, portrait.png, manifest.json) are preserved without
modification. A lightweight learning engine tracks weakness frequency and archetype/axis/role
combo weights to inform future generation quality.

╭──────────────────────────┬─────────────────────────────────────────────────────╮
│  Phase / Component       │  Role                                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╡
│  SEMEN (Seeds)           │  Wizard sets sliders, archetype, axis, role        │
│  GENERATIO               │  _generatio_box: blind trait/lore generation       │
│  ANALYTICA               │  _analytica_box: lore-register critique + iterate  │
│  NOMEN                   │  _elaboratio_box: 3-5 name candidates              │
│  ELABORATIO              │  Package assembly + portrait generation            │
│  ControlPanel            │  Left pane — all Wizard inputs                     │
│  PortraitPane            │  Centre pane — portrait display + phase controls   │
│  RightPanel (tabbed)     │  CODEX / ANALYTICA / NOMEN tabs                    │
│  EntityGenWorker         │  QThread — fires _generatio_box                    │
│  AnalyticaWorker         │  QThread — fires _analytica_box (session-aware)    │
│  NomenWorker             │  QThread — fires _elaboratio_box                   │
│  PortraitWorker          │  QThread — Freepik portrait generation             │
│  LearningEngine          │  SQLite — combo weights + weakness frequency       │
╰──────────────────────────┴─────────────────────────────────────────────────────╯

### Architectural Constraints

- All Claude calls: three distinct ClaudeBox instances, never shared across phases
- Analytica session continuity: `session_id = f"analytica_{generation_id}"` per forge cycle;
  cleared on new FORGE
- Threading: all blocking ops use QThread subclasses with pyqtSignal; never block main thread
- Name field: absent from ControlPanel; appears only in NOMEN tab post-approval
- Stage button: disabled until name is ratified in NOMEN tab
- Learning engine: SQLite at `~/.arca/entitex_refined.db`; written after NOMEN ratification
- Package output format: identical to ENTITEX v0.1 — no changes to yaml schemas or file layout
- ClaudeBox import: `sys.path.insert(0, str(Path.home() / 'ArcaCognitorium'))`;
  `from claudebox import ClaudeBox`; `api_key=os.environ.get('CLAUDE_API_KEY')`
- Portrait: unchanged pipeline — Freepik API, existing model/aspect/style controls
- PyQt6 exclusively; no PySide6

---

## 2. Tech Stack

╭────────────────────────┬────────────┬──────────────────────────────────────────────╮
│  Tool                  │  Version   │  Justification                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╡
│  Python                │  3.11      │  Canonical Cogniverse version               │
│  PyQt6                 │  ≥6.4      │  Exclusive GUI framework — Exocognii suite  │
│  ClaudeBox             │  canonical │  ~/ArcaCognitorium/claudebox/               │
│  anthropic             │  ≥0.25     │  ClaudeBox dependency                       │
│  PyYAML                │  ≥6.0      │  Package file serialisation                 │
│  SQLite3               │  stdlib    │  Learning engine persistence                │
│  Freepik API           │  v1        │  Portrait generation (unchanged from v0.1)  │
│  urllib (stdlib)       │  stdlib    │  Freepik HTTP — no requests dependency      │
╰────────────────────────┴────────────┴──────────────────────────────────────────────╯

---

## 3. Directory Tree & Database Schema

```
ArcaCognitorium/
└── Exocognii/
    └── EntitexRefined/
        ├── EntitexRefined.py          # Main application — single file
        ├── EntitexRefined.sh          # Launch script
        ├── Archetypes.py              # Archetype/axis/role pools (unchanged)
        ├── Disposition_sliders.py     # Slider labels + image bias (unchanged)
        ├── disposition_axes.py        # Temporality/legibility axes (unchanged)
        ├── learning_engine.py         # SQLite combo weights + weakness freq
        ├── dependencies.sh
        ├── entitex_refined_log.json   # Generation log (mirrors v0.1 pattern)
        ├── staged/                    # Install-ready packages
        │   └── {entity_id}/
        │       ├── role.yaml
        │       ├── traits.yaml
        │       ├── lore.yaml
        │       ├── profiles_fragment.yaml
        │       ├── canon_fragment.yaml
        │       ├── portrait.png
        │       └── manifest.json
        ├── vault/                     # Auto-save history (portrait + entity.json)
        ├── temp_portraits/
        └── venv-ENTITEX_REFINED/

~/.arca/
└── entitex_refined.db                 # Learning engine SQLite database
```

### Database Schema

```sql
-- Combo performance tracking
CREATE TABLE IF NOT EXISTS combo_scores (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    item        TEXT NOT NULL UNIQUE,
    total_score REAL DEFAULT 0.0,
    count       INTEGER DEFAULT 0,
    avg_score   REAL GENERATED ALWAYS AS (
                    CASE WHEN count > 0 THEN total_score / count ELSE 0 END
                ) STORED
);

-- Weakness frequency tracking
CREATE TABLE IF NOT EXISTS weakness_freq (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    tag       TEXT NOT NULL UNIQUE,
    frequency INTEGER DEFAULT 0
);

-- Generation history (lightweight — no full prompt storage)
CREATE TABLE IF NOT EXISTS generation_log (
    id              TEXT PRIMARY KEY,        -- 8-char uuid fragment
    generated_at    TEXT NOT NULL,           -- ISO timestamp
    archetype       TEXT,
    cognitive_axis  TEXT,
    role            TEXT,
    ratified_name   TEXT,
    weakness_tags   TEXT,                    -- JSON array
    analytica_flags INTEGER DEFAULT 0
);
```

---

## 4. Module Breakdown

╭────────────────────────────┬────────────────┬───────────────────────────────┬─────────────────────────────┬────────────────────────────────╮
│  Module                    │  Phase         │  Responsibility               │  Inputs                     │  Outputs                       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╡
│  ControlPanel              │  SEMEN         │  Wizard input collection      │  User interaction           │  archetype, axis, role, inc    │
│  EntityGenWorker           │  GENERATIO     │  Blind trait/lore generation  │  archetype, axis, role, inc │  entity_data dict (no name)    │
│  CodexPane                 │  GENERATIO     │  Display generated profile    │  entity_data                │  Rendered lore fields          │
│  AnalyticaWorker           │  ANALYTICA     │  Lore-register critique       │  entity_data, session_id    │  verdict dict + flags list     │
│  AnalyticaPane             │  ANALYTICA     │  Display verdict + iterate    │  verdict dict               │  iterate feedback string       │
│  NomenWorker               │  NOMEN         │  Name candidate generation    │  entity_data (approved)     │  list of 3-5 name strings      │
│  NomenPane                 │  NOMEN         │  Name selection + ratification│  name candidates            │  ratified_name string          │
│  PortraitPane              │  ELABORATIO    │  Portrait display + controls  │  portrait path              │  UI state signals              │
│  PortraitWorker            │  ELABORATIO    │  Freepik portrait generation  │  entity_data, style, inc    │  portrait image path           │
│  assemble_package()        │  ELABORATIO    │  Write all yaml + files       │  entity_data + portrait     │  staged/{entity_id}/ directory │
│  learning_engine.py        │  Post-stage    │  Update combo weights/weakns  │  entity_data, flags         │  SQLite writes                 │
│  vault_autosave()          │  Post-portrait │  Snapshot to vault/           │  entity_data, portrait      │  vault entry directory         │
╰────────────────────────────┴────────────────┴───────────────────────────────┴─────────────────────────────┴────────────────────────────────╯

---

## 5. UI Wireframe

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  ENTITEX — REFINED  ·  Entity Package Generator  ·  Arca Cognitorium        [View Files]║
╠═══════════════════╦══════════════════════════════════╦═══════════════════════════════════╣
║  SEMEN            ║  IMAGO ENTIS                     ║  [ CODEX ] [ ANALYTICA ] [ NOMEN ]║
║ ─────────────── ║                                  ║                                   ║
║  IDENTITY         ║                                  ║  ── CODEX ENTIS ──────────────── ║
║  Archetype  [v]   ║                                  ║  DISPLAY NAME  [────────────────]║
║  └ Custom [     ] ║       [ portrait image ]         ║  TITLE / EPITHET [──────────────]║
║  Cognitive  [v]   ║       or status message          ║  GLYPH · COLOR  [──────────────]║
║  Role       [v]   ║                                  ║  PURPOSE        [──────────────]║
║  ─────────────── ║                                  ║                 [──────────────]║
║  INCLINATIONES    ║  [████████████████]  progress    ║  LORE ORIGIN    [──────────────]║
║  Disposition ──○─ ║                                  ║  LORE NATURE    [──────────────]║
║  [label]          ║  ┌──────────────────────────┐   ║  RELATIONSHIP   [──────────────]║
║  Register    ──○─ ║  │  ⚗  FORGE ENTITY  │  ⚄ │   ║  AURA           [──────────────]║
║  [label]          ║  └──────────────────────────┘   ║  VISUAL KEYS    [──────────────]║
║  Presence    ──○─ ║                                  ║  TRAIT CEILINGS [──────────────]║
║  [label]          ║  [ ↺ Re-Portrait ]               ║                                   ║
║  Opacity     ──○─ ║  [ 🜲 Stage Package ] [✕ Discard]║  ── ANALYTICA ─────────────────  ║
║  [label]          ║                                  ║  (visible when ANALYTICA tab      ║
║  Stability   ──○─ ║  ─── Phase indicator ─────────  ║   active)                         ║
║  [label]          ║  ○ SEMEN  ● GENERATIO            ║  VERDICT        [──────────────] ║
║  Temporality ──○─ ║  ○ ANALYTICA  ○ NOMEN            ║                 [──────────────] ║
║  [label]          ║  ○ ELABORATIO                    ║  FLAGS          [tag][tag][tag]   ║
║  Legibility  ──○─ ║                                  ║  [Iterate: __________________ →] ║
║  [label]          ║                                  ║  [ ✓ Approve Profile ]            ║
║  ─────────────── ║                                  ║                                   ║
║  PORTRAIT         ║                                  ║  ── NOMEN ─────────────────────  ║
║  Style      [v]   ║                                  ║  (visible when NOMEN tab active)  ║
║  Model      [v]   ║                                  ║  ○ CandidateName1                 ║
║  Aspect     [v]   ║                                  ║  ○ CandidateName2                 ║
║  Visual [       ] ║                                  ║  ○ CandidateName3                 ║
║                   ║                                  ║  ○ CandidateName4                 ║
║                   ║                                  ║  ○ CandidateName5                 ║
║                   ║                                  ║  Custom: [___________________]    ║
║                   ║                                  ║  [ ✒ Ratify Name ]                ║
╠═══════════════════╩══════════════════════════════════╩═══════════════════════════════════╣
║  status message                                           staged → Exocognii/EntitexR… ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
```

### Legend

```
[v]           QComboBox
──○─          QSlider — horizontal, tick marks below
[label]       Dim QLabel showing current slider value, updates on slide
[ text ]      QPushButton
[──────]      QLabel (read) or QPlainTextEdit (scrollable) display field
[tag]         Inline weakness/flag label — styled QLabel with border
[______ →]    QLineEdit + QPushButton iterate row
○ / ●         Phase indicator dots — QLabel glyphs; filled = active phase
```

### Phase Indicator

Five dots in the PortraitPane footer show current pipeline phase. Active phase is filled
(`●`), completed phases are dim-filled (`◉`), pending are empty (`○`). Updates on each
phase transition signal.

### Right Panel Tab Visibility

ANALYTICA and NOMEN tabs are present from launch but content is populated only when their
phase is reached. CODEX tab is populated after GENERATIO completes. NOMEN tab is not
interactive until `profile_approved` state is set.

---

## 6. Data Flow

### Path A — Happy Path (full pipeline)

```
1. Wizard sets sliders + archetype/axis/role → clicks FORGE ENTITY
2. EntitexRefinedApp._start_generation()
   - Clears state, disables controls, shows progress
   - Sets phase indicator: GENERATIO active
3. EntityGenWorker(QThread).run()
   - Builds inclinatio_context from sliders
   - Calls _generatio_box.send(user_prompt) — no name in prompt
   - Emits finished(entity_data: dict)
4. EntitexRefinedApp._on_entity_generated(entity_data)
   - Populates CODEX tab (lore fields)
   - Generates generation_id = uuid4()[:8]
   - Sets phase: ANALYTICA active
   - Starts AnalyticaWorker(entity_data, generation_id)
5. AnalyticaWorker(QThread).run()
   - session_id = f"analytica_{generation_id}"
   - Clears any prior session on _analytica_box
   - Calls _analytica_box.send(entity_profile_prompt, session_id=session_id)
   - Emits finished(verdict: dict)
6. EntitexRefinedApp._on_analytica_done(verdict)
   - Populates ANALYTICA tab: verdict prose, flag tags
   - Switches right panel to ANALYTICA tab
   - Enables Approve Profile + Iterate controls
   - Phase stays ANALYTICA until Wizard acts
7a. Wizard clicks Approve Profile
   → EntitexRefinedApp._approve_profile()
   - Sets phase: NOMEN active
   - Starts NomenWorker(entity_data)
8. NomenWorker(QThread).run()
   - Calls _elaboratio_box.send(nomen_prompt)
   - Parses response into list[str] of 3-5 names
   - Emits finished(names: list[str])
9. EntitexRefinedApp._on_nomen_done(names)
   - Populates NOMEN tab radio buttons
   - Switches right panel to NOMEN tab
   - Enables Ratify Name button
10. Wizard selects name (or types custom) → clicks Ratify Name
    → EntitexRefinedApp._ratify_name(name)
    - Injects name into entity_data
    - Enables Re-Portrait + Stage controls
    - Phase: ELABORATIO active
    - Starts PortraitWorker(entity_data, style, inc, model, aspect)
11. PortraitWorker(QThread).run()
    - Assembles portrait prompt from entity_data + sliders
    - Submits to Freepik API, polls, retrieves image
    - Emits finished(portrait_path: str)
12. EntitexRefinedApp._on_portrait_done(portrait_path)
    - Displays portrait in PortraitPane
    - Calls vault_autosave(entity_data, portrait_path)
    - Phase: ELABORATIO complete
    - Enables Stage Package
13. Wizard clicks Stage Package
    → assemble_package(entity_data, portrait_path) → staged/{entity_id}/
    → learning_engine.record(entity_data, verdict['flags'])
    → Enables View Files button
```

### Path B — Analytica Iterate

```
1. Wizard types feedback in iterate field → clicks →
2. AnalyticaWorker launched with same generation_id (session continues)
3. _analytica_box.send(feedback, session_id=session_id)
4. New verdict returned → ANALYTICA tab repopulated
5. Wizard may iterate again or approve
```

### Path C — API / Network Failure

```
1. Any Worker.run() catches Exception → emits errored(str)
2. EntitexRefinedApp._on_error(msg)
   - Hides progress bar
   - Re-enables FORGE button
   - Re-enables any controls appropriate to current phase
   - Status bar: "✕  Error: {msg[:120]}"
   - Portrait pane shows "Generation failed."
   - Phase indicator returns to last stable phase
   - Wizard can retry from current phase or restart from FORGE
```

---

## 7. Code Stubs

```python
# ─────────────────────────────────────────────────────────────────────────────
# entitex_refined_worker.py  (or inline in EntitexRefined.py)
# ─────────────────────────────────────────────────────────────────────────────

import os, sys, json, threading
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

sys.path.insert(0, str(Path.home() / 'ArcaCognitorium'))
from claudebox import ClaudeBox

# ── ClaudeBox instances ────────────────────────────────────────────────────────
_api_key = os.environ.get('CLAUDE_API_KEY')

_generatio_box  = ClaudeBox(api_key=_api_key, system_prompt=GENERATIO_SYSTEM,  stream=False)
_analytica_box  = ClaudeBox(api_key=_api_key, system_prompt=ANALYTICA_SYSTEM,  stream=False)
_elaboratio_box = ClaudeBox(api_key=_api_key, system_prompt=ELABORATIO_SYSTEM, stream=False)

_gen_lock  = threading.Lock()
_ana_lock  = threading.Lock()
_elab_lock = threading.Lock()


# ── System Prompts ─────────────────────────────────────────────────────────────

GENERATIO_SYSTEM: str
"""
Entitex Generatio — blind entity forge for Arca Cognitorium.

You generate complete entity personality and lore profiles with NO name.
The entity arrives as a presence — its identity is discovered, not assigned.
You do not receive a name. You do not suggest a name. Name is withheld by design.

Cogniverse register: entities are presences with institutional permanence.
They do not explain themselves. They speak in their own voice.
Lore is felt before it is named.

Return ONLY a raw JSON object. No markdown fences. No preamble.
[Full JSON schema — mirrors v0.1 EntityGenWorker output minus name fields]
"""

ANALYTICA_SYSTEM: str
"""
Entitex Analytica — Cogniverse lore critic.

You are a senior entity of the Tower reviewing a newly generated profile.
Your register is the Tower's own: spare, declarative, institutionally weighted.
You do not score. You do not use numbers. You observe and flag.

Return a verdict in lore prose (2-4 sentences) and a list of discrete flags.
Flags are short (3-6 words), in Cogniverse register, naming what is weak or incoherent.
Also return a one-sentence refinement suggestion.

Return ONLY a raw JSON object:
{
  "verdict": "<lore-register prose verdict>",
  "flags": ["<flag>", ...],
  "suggestion": "<one sentence>"
}
"""

ELABORATIO_SYSTEM: str
"""
Entitex Elaboratio — Nomenclatura name oracle.

You receive a complete entity profile (no name). You propose 3-5 name candidates.
Names follow Nomenclatura Arcana register: invented or archaic Latin constructions,
two-word forms preferred, carrying institutional permanence.
The name should feel like a title that was always true.

Return ONLY a raw JSON object:
{
  "candidates": ["<Name One>", "<Name Two>", "<Name Three>", ...]
}
No preamble. No etymology notes. Names only.
"""


# ── Workers ────────────────────────────────────────────────────────────────────

class EntityGenWorker(QThread):
    """Phase GENERATIO — blind entity generation, no name."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    errored  = pyqtSignal(str)

    def __init__(self, archetype: str, cognitive_axis: str, role: str,
                 inc: dict, parent=None) -> None:
        """archetype, cognitive_axis, role from ControlPanel; inc from slider values."""
        super().__init__(parent)
        self.archetype      = archetype
        self.cognitive_axis = cognitive_axis
        self.role           = role
        self.inc            = inc

    def run(self) -> None:
        """Build user prompt from inputs; call _generatio_box; emit entity_data dict."""
        ...


class AnalyticaWorker(QThread):
    """Phase ANALYTICA — lore-register critique with session continuity."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)   # verdict dict: {verdict, flags, suggestion}
    errored  = pyqtSignal(str)

    def __init__(self, entity_data: dict, generation_id: str,
                 iterate_feedback: str = "", parent=None) -> None:
        """
        entity_data: generated profile dict.
        generation_id: 8-char id for session_id scoping.
        iterate_feedback: empty string on first call; Wizard text on subsequent calls.
        """
        super().__init__(parent)
        self.entity_data      = entity_data
        self.generation_id    = generation_id
        self.iterate_feedback = iterate_feedback

    def run(self) -> None:
        """
        session_id = f'analytica_{generation_id}'.
        First call: delete_session then send full profile.
        Iterate call: send iterate_feedback only (session continues).
        Parse JSON response → emit finished(verdict).
        """
        ...


class NomenWorker(QThread):
    """Phase NOMEN — name candidate generation."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)   # list of name candidate strings
    errored  = pyqtSignal(str)

    def __init__(self, entity_data: dict, parent=None) -> None:
        """entity_data: approved profile dict."""
        super().__init__(parent)
        self.entity_data = entity_data

    def run(self) -> None:
        """Build nomen prompt from entity_data; call _elaboratio_box; parse candidates list."""
        ...


# ── Package Assembly ───────────────────────────────────────────────────────────

def assemble_package(entity_data: dict, portrait_path: str) -> Path:
    """
    Write role.yaml, traits.yaml, lore.yaml, profiles_fragment.yaml,
    canon_fragment.yaml, portrait.png, manifest.json to staged/{entity_id}/.
    entity_data must contain ratified 'display_name' before this is called.
    Returns staged directory path.
    Schema identical to ENTITEX v0.1 assemble_package().
    """
    ...


def vault_autosave(entity_data: dict, portrait_path: str) -> Path:
    """
    Auto-save entity.json + portrait.png to vault/{timestamp}_{entity_id}/.
    Called after portrait generation. Returns vault entry path.
    """
    ...


def _parse_json_block(raw: str) -> dict:
    """
    Multi-stage JSON recovery:
    1. Strip markdown fences
    2. Extract first { } block
    3. Direct parse
    4. Repair literal newlines inside strings, trailing commas
    5. Raise ValueError with snippet on second failure.
    """
    ...


# ── Learning Engine ────────────────────────────────────────────────────────────

# learning_engine.py

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / '.arca' / 'entitex_refined.db'


def _conn() -> sqlite3.Connection:
    """Open connection; create tables if not exist."""
    ...


def record(entity_data: dict, flags: list[str]) -> None:
    """
    After package staging:
    - Upsert combo_scores for archetype, cognitive_axis, role keys
      (score = max(0, 10 - len(flags)); simple proxy quality signal)
    - Increment weakness_freq for each flag
    - Insert generation_log row
    """
    ...


def get_combo_weights() -> dict[str, float]:
    """Return {item: avg_score} for all items with count >= 2."""
    ...


def get_weakness_stats(limit: int = 20) -> list[tuple[str, int]]:
    """Return [(tag, frequency)] sorted by frequency desc."""
    ...


# ── UI Panels ──────────────────────────────────────────────────────────────────

class ControlPanel(QWidget):
    """
    Left pane. Unchanged from ENTITEX v0.1 EXCEPT:
    - Name input field REMOVED
    - No generate_requested signal from this panel
      (FORGE button lives in PortraitPane)
    Exposes: archetype, cognitive_axis, role, style_key,
             freepik_model_id, aspect_ratio_value,
             visual_override_text, inclinatio_values, randomize()
    """
    ...


class PortraitPane(QWidget):
    """
    Centre pane. Adds:
    - phase_indicator: row of 5 QLabel dots (SEMEN/GENERATIO/ANALYTICA/NOMEN/ELABORATIO)
    - set_phase(phase: str) updates dot states
    - FORGE + Randomize buttons (row 1, unchanged)
    - Re-Portrait / Stage / Discard buttons (row 2, unchanged)
    - Stage gated: only enabled after name ratification
    """
    def set_phase(self, phase: str) -> None:
        """Update phase indicator dots. phase ∈ {SEMEN, GENERATIO, ANALYTICA, NOMEN, ELABORATIO}."""
        ...


class CodexPane(QWidget):
    """
    CODEX tab content. Unchanged from ENTITEX v0.1 LorePane.
    Displays: display_name (populated post-NOMEN), title, glyph/color,
    purpose, lore_origin, lore_nature, lore_relationship, lore_aura,
    visual_keywords, trait_ceilings.
    Note: display_name field shows '— awaiting ratification —' until NOMEN complete.
    """
    def populate(self, data: dict) -> None: ...
    def set_name(self, name: str) -> None: ...
    def clear(self) -> None: ...


class AnalyticaPane(QWidget):
    """
    ANALYTICA tab content.
    Displays: verdict prose (QPlainTextEdit, read-only),
              flag tags (styled QLabel row),
              suggestion line,
              iterate input (QLineEdit) + iterate button,
              Approve Profile button.
    iterate_requested signal carries feedback string.
    approve_requested signal carries no payload.
    """
    iterate_requested = pyqtSignal(str)
    approve_requested = pyqtSignal()

    def populate(self, verdict: dict) -> None:
        """Render verdict, flags, suggestion. Enable iterate + approve controls."""
        ...

    def clear(self) -> None: ...


class NomenPane(QWidget):
    """
    NOMEN tab content.
    Displays: QButtonGroup of QRadioButton (one per candidate),
              custom name QLineEdit,
              Ratify Name button.
    name_ratified signal carries selected/typed name string.
    """
    name_ratified = pyqtSignal(str)

    def populate(self, candidates: list[str]) -> None:
        """Build radio buttons from candidates list. Clear prior state."""
        ...

    def _get_selected(self) -> str:
        """Return custom field text if filled, else selected radio button text."""
        ...


class RightPanel(QTabWidget):
    """
    Three-tab container: CODEX / ANALYTICA / NOMEN.
    Wraps CodexPane, AnalyticaPane, NomenPane.
    switch_to(tab: str) convenience method.
    """
    def switch_to(self, tab: str) -> None:
        """tab ∈ {'CODEX', 'ANALYTICA', 'NOMEN'}"""
        ...


class EntitexRefinedApp(QMainWindow):
    """
    Main application window. Orchestrates all phases.
    State machine: _phase ∈ {idle, generatio, analytica, nomen, elaboratio}
    _current_entity: dict — grows across phases (name injected at ratification)
    _current_portrait: str — path after PortraitWorker completes
    _generation_id: str — scopes AnalyticaWorker session
    """

    def _start_generation(self) -> None:
        """Validate inputs, clear state, start EntityGenWorker."""
        ...

    def _on_entity_generated(self, entity_data: dict) -> None:
        """Populate CODEX tab, set phase ANALYTICA, start AnalyticaWorker."""
        ...

    def _on_analytica_done(self, verdict: dict) -> None:
        """Populate ANALYTICA tab, switch right panel, enable approve/iterate."""
        ...

    def _on_analytica_iterate(self, feedback: str) -> None:
        """Start AnalyticaWorker with iterate_feedback set, same generation_id."""
        ...

    def _approve_profile(self) -> None:
        """Set phase NOMEN, start NomenWorker."""
        ...

    def _on_nomen_done(self, candidates: list[str]) -> None:
        """Populate NOMEN tab, switch right panel."""
        ...

    def _ratify_name(self, name: str) -> None:
        """
        Inject name into entity_data as display_name + entity_id.
        Update CODEX display_name field. Set phase ELABORATIO.
        Enable Re-Portrait. Start PortraitWorker.
        """
        ...

    def _on_portrait_done(self, portrait_path: str) -> None:
        """Display portrait, vault_autosave, enable Stage."""
        ...

    def _stage_package(self) -> None:
        """assemble_package(), learning_engine.record(), enable View Files."""
        ...

    def _on_error(self, msg: str) -> None:
        """Re-enable controls for current phase, update status bar."""
        ...
```

---

## 8. Error Handling

╭──────────────────────────────┬─────────────────────────────────┬───────────────────────────────────────────────╮
│  Error                       │  Cause                          │  Strategy                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╡
│  CLAUDE_API_KEY missing      │  Env var not set                │  Warn at startup; disable FORGE button        │
│  EntityGenWorker API fail    │  Network/rate limit             │  emit errored → _on_error → re-enable FORGE   │
│  AnalyticaWorker API fail    │  Network/session error          │  emit errored → re-enable iterate+approve     │
│  NomenWorker API fail        │  Network error                  │  emit errored → re-enable approve path        │
│  JSON parse failure          │  Malformed Claude response      │  _parse_json_block multi-stage repair;        │
│                              │                                 │  if all fail, raise with 200-char snippet     │
│  PortraitWorker API fail     │  Freepik error/NSFW             │  emit errored → re-enable Re-Portrait         │
│  Freepik key missing         │  FREEPIK_API_KEY not set        │  PortraitWorker raises RuntimeError on start  │
│  assemble_package() IOError  │  Disk write failure             │  Log + status bar; staged dir may be partial  │
│  SQLite write error          │  learning_engine.record() fail  │  Log only; non-fatal; generation proceeds     │
│  Session not found (iterate) │  generation_id mismatch         │  Restart analytica session from profile       │
╰──────────────────────────────┴─────────────────────────────────┴───────────────────────────────────────────────╯

---

## 9. Setup & Testing

### requirements.txt

```
PyQt6>=6.4.0
anthropic>=0.25.0
PyYAML>=6.0
```

ClaudeBox is imported from `~/ArcaCognitorium/claudebox/` — not installed via pip.

### Install & Run

```bash
cd ~/ArcaCognitorium/Exocognii/EntitexRefined
python -m venv venv-ENTITEX_REFINED
source venv-ENTITEX_REFINED/bin/activate
pip install -r requirements.txt
python EntitexRefined.py
```

### Environment Variables Required

```
CLAUDE_API_KEY=<key>
FREEPIK_API_KEY=<key>
```

### Unit Tests

```python
# test_parse_json.py
def test_parse_clean_json():
    """_parse_json_block returns dict from clean JSON string."""

def test_parse_fenced_json():
    """_parse_json_block strips ```json fences and returns dict."""

def test_parse_repaired_json():
    """_parse_json_block repairs literal newlines inside string values."""

def test_parse_trailing_comma():
    """_parse_json_block removes trailing commas before } and ]."""

# test_learning_engine.py
def test_record_creates_rows():
    """record() inserts into combo_scores and weakness_freq."""

def test_combo_weights_minimum_count():
    """get_combo_weights() returns only items with count >= 2."""

# test_assemble_package.py
def test_package_files_written():
    """assemble_package() writes all 6 files + manifest to staged/{entity_id}/."""

def test_package_requires_name():
    """assemble_package() raises if display_name not in entity_data."""
```

### Integration Test

```python
# test_integration.py
def test_full_pipeline_mock():
    """
    With ClaudeBox mocked to return fixture JSON:
    1. EntityGenWorker produces entity_data with no name field
    2. AnalyticaWorker produces verdict dict with flags list
    3. NomenWorker produces list of 3-5 strings
    4. assemble_package() with injected name produces all expected files
    5. learning_engine.record() writes to test DB without error
    """
```

---

## 10. Packaging

### Launch Script — EntitexRefined.sh

```bash
#!/bin/bash
cd /home/lordfingers/ArcaCognitorium
source Exocognii/EntitexRefined/venv-ENTITEX_REFINED/bin/activate
python -m Exocognii.EntitexRefined.EntitexRefined
```

### Desktop File — EntitexRefined.desktop

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Entitex Refined
Comment=Entity Package Generator — Arca Cognitorium
Exec=/home/lordfingers/ArcaCognitorium/Exocognii/EntitexRefined/EntitexRefined.sh
Icon=entitex_refined
Terminal=false
Categories=Utility;
```

Install locations:

```bash
cp EntitexRefined.desktop ~/.local/share/applications/
cp entitex_refined.png ~/.local/share/icons/
```

---

## 11. Extensibility

╭──────────────────────────────────┬───────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────╮
│  Feature                         │  User Value                                   │  Implementation Approach                                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╡
│  Lexiferium name phase wiring    │  Name candidates pass through Lexiferium      │  NomenWorker posts candidates to Lexiferium via Exocognii         │
│                                  │  suggestion + ratification pipeline           │  manifest tool discovery; Wizard ratifies in Lexiferium UI        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╡
│  Multi-entity batch forge        │  Queue N entities; generate unattended;       │  BatchQueue class wrapping pipeline workers; QUEUE tab in right   │
│                                  │  review results in vault browser              │  panel; vault browser replaces manual file dialog                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╡
│  Machinae Mundi Lapsus biasing   │  Active celestial/circadian state nudges      │  GENERATIO_SYSTEM receives Mundana variable block prepended;      │
│                                  │  disposition sliders toward contextual fit    │  slider defaults shift on app launch based on Machinae output     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╡
│  Entity relationship mapping     │  New entity is positioned relative to         │  Fourth phase post-NOMEN; RELATIO tab; small ClaudeBox call       │
│                                  │  existing Council — tension/affinity noted    │  comparing new profile against emerged.json roster                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╡
│  Vault browser                   │  Browse, preview, re-stage previous           │  VAULT tab in right panel; list of vault/{ts}_{id}/ dirs;         │
│                                  │  generations without re-forging               │  clicking entry loads entity.json + portrait into current state   │
╰──────────────────────────────────┴───────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────╯

---

*⟁*
*Ordo Discordia, Cosmos Inania*
*ENTITEX — REFINED · Build Document v1.0 · Arca Cognitorium*
