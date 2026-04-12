# AGENTIA ARCHITECTURALIS
## Dux Tome — Operational Reference
### Bureau II · Triumviratus Aestheticus Imperialis
#### dux-tome-agentia.architecturalis.tome.md · v1.0 · MMXXVI

---

*Verificatio Canonica*

All identity content, nomenclature, mottos, and canonical references in this
document have been verified against ratified sources prior to submission. No
content has been invented where canonical content exists.

Bureau: Agentia Architecturalis — Bureau II
Version: v1.0
Date: 2026-04-08

---

*In Linea · In Parallelo · In Perpetuum*

*Ordo Discordia, Cosmos Inania*

---

```
╔═══════════════════════════════════════════════════════════════════════╗
║◤                                                                     ◥║
║                                                                       ║
║              AGENTIA ARCHITECTURALIS                                  ║
║              Architectural Alignment Enforcement Agency               ║
║              In Linea · In Parallelo · In Perpetuum                   ║
║                                                                       ║
║              DUX TOME — Operational Reference                         ║
║              Bureau II of III — Triumviratus Aestheticus Imperialis   ║
║                                                                       ║
║◣                                                                     ◢║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

# I. CANONICAL IDENTITY

╭─────────────────────────────────────────────────────────────────────╮
│  Primary Title   ·  AGENTIA ARCHITECTURALIS                         │
│  English Name    ·  Architectural Alignment Enforcement Agency      │
│  Motto           ·  In Linea · In Parallelo · In Perpetuum          │
│  Bureau          ·  II of III — Triumviratus Aestheticus Imperialis │
│  Alliance        ·  Aesthetic Authoritarian Associative Alliance    │
│  Suite           ·  Exocognii — Arca Cognitorium                   │
│  Path            ·  Exocognii/A4/AgentiaArchitecturalis/           │
│  Venv            ·  venv-ARCHITECTURALIS                           │
│  Launch          ·  python3 -m AgentiaArchitecturalis               │
╰─────────────────────────────────────────────────────────────────────╯

---

# II. LAUNCH & ENVIRONMENT

## Prerequisites

Bureau I (Auctoritas Spectralis) must have produced a ratified theme.json
before Bureau II is built and before the application first loads colour from
an external source. The application operates on ModusArcanus defaults in the
absence of theme.json — it does not crash or block.

## Launch Sequence

    cd ~/ArcaCognitorium/Exocognii/A4/
    source venv-ARCHITECTURALIS/bin/activate
    python3 -m AgentiaArchitecturalis

Never invoke as `python3 AgentiaArchitecturalis/__main__.py` from within the
package directory. The `-m` module invocation from the parent directory is
mandatory for correct relative path resolution.

## Environment Variables

    CLAUDE_API_KEY       Required only if AI-assisted features are wired.
                         Not required for core canvas, codegen, or library
                         operations.

## File Locations

    storage/config.json              User preferences (LAT/EN toggle,
                                     window geometry, last session)
    storage/canvases/{name}.json     Named canvas sessions
    storage/armarium.db              SQLite component library
    theme.json                       Bureau I output — read-only

All paths resolve relative to `Path(__file__).resolve().parent`. Hardcoded
`/home/lordfingers` paths are a build failure.

---

# III. THE OPENING CEREMONY

The Opening Ceremony fires on first launch within a session. It does not
repeat after dismissal within the same session. Any keypress dismisses it.

## Six-Act Sequence

╭──────┬──────────────────────┬────────────────────────────────────────╮
│  Act │  Name                │  Description                           │
├┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  I   │  Salutatio           │  Bureau identity displayed. Name,      │
│      │                      │  motto, bureau number. Gold on void.   │
├┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  II  │  Thema Inspectio     │  Theme load status. Reports whether    │
│      │                      │  Bureau I theme.json was found or if   │
│      │                      │  ModusArcanus defaults are active.     │
├┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  III │  Armarium Census     │  Reports count of sealed components    │
│      │                      │  in the library. "N components sealed."│
├┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  IV  │  Canvases Census     │  Reports count of named canvas         │
│      │                      │  sessions on disk.                     │
├┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  V   │  Session Restore     │  If a canvas session was active at     │
│      │                      │  last close, offers to restore it.     │
│      │                      │  Wizard may decline. No forced load.   │
├┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  VI  │  Commissio           │  "The bureau stands ready." Dismisses  │
│      │                      │  into the main application shell.      │
╰──────┴──────────────────────┴────────────────────────────────────────╯

---

# IV. APPLICATION SHELL — A4 COMMON SHELL

## Zone Map

```
╔══════════╦═══════════════════════════════════════════════════╗
║          ║                   FASCIA (52px)                   ║
║ TITULUM  ╠═══════════════════════════════════════════════════╣
║ (220px)  ║                                                   ║
║          ║           SCRIPTORIUM CANVAS                      ║
║  FEATURE ║           (feature-owned, all remaining           ║
║  CODEX   ║            space)                                 ║
║          ║                                                   ║
╚══════════╩═══════════════════════════════════════════════════╝
```

## Zone I — Titulum (220px left panel)

Fixed. Never scrolls. Never changes layout.

Contents: Bureau identity glyph ⟁, bureau name (LAT/EN), motto
(LAT/EN), dirty state indicator ◌ when unsaved changes exist, active
canvas session name, active theme name.

The LAT/EN language toggle lives here. A single click propagates language
change to all labelled widgets in a single pass via `_on_lang_changed()`.

## Zone II — Feature Codex (left rail, below Titulum)

Navigation list of features. One feature is active at a time. Selecting
a feature swaps the Scriptorium Canvas instantly (no animation — ratified
by Convocatio). Features:

╭──────────────────────────┬───────────────────────────────────╮
│  Feature                 │  Latin · English                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Tabula Designandi       │  The Design Canvas                │
│  Inspector Proprietatum  │  Property Inspector               │
│  Armarium Componentium   │  Component Library                │
│  Specularium Vivum       │  Live Preview                     │
│  Codex Exportum          │  Code Generation                  │
│  Thema                   │  Theme Management                 │
╰──────────────────────────┴───────────────────────────────────╯

Dispositio has been retired from the Feature Codex. It does not appear.

## Zone III — Fascia (52px top-right strip)

Feature-keyed action buttons. Buttons shown depend on which feature is
active. HELP (Auxilium trigger) is always the rightmost button.

Dirty state indicator ◌ also appears in the Fascia when unsaved canvas
changes exist.

## Zone IV — Scriptorium Canvas (all remaining space)

Feature-owned. The active feature occupies the full canvas without
sharing space with any other feature. Features are swapped as complete
units via QStackedWidget (instant swap, no slide animation).

---

# V. FEATURE REFERENCE

## Tabula Designandi — The Design Canvas

The spatial composition workspace. A QGraphicsScene canvas with 16px
grid snapping.

### Canvas Controls

╭─────────────────────────┬─────────────────────────────────────╮
│  Action                 │  Control                            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Pan                    │  Middle-click drag                  │
│  Zoom                   │  Ctrl + scroll (0.25×–4.0×)        │
│  Select element         │  Left-click                        │
│  Rubber-band select     │  Left-drag on empty canvas         │
│  Move element           │  Drag selected element             │
│  Place element          │  Drag from Elementarium to canvas  │
│  Delete element         │  Delete key on selected element    │
│  Undo                   │  Ctrl+Z (50-step stack)            │
│  Redo                   │  Ctrl+Shift+Z                      │
╰─────────────────────────┴─────────────────────────────────────╯

### Elementarium

The element browser within the Tabula feature. Collapsible categories.
Drag an element tile to the canvas to place it. 28 element types across
7 categories:

╭─────────────────┬──────────────────────────────────────────────╮
│  Category       │  Element Types                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Receptacula    │  QFrame, QGroupBox, QSplitter, QTabWidget   │
│  Ingressus      │  QLineEdit, QTextEdit, QSpinBox,            │
│                 │  QComboBox, QCheckBox, QRadioButton         │
│  Ostensio       │  QLabel, QProgressBar, QLCDNumber           │
│  Actiones       │  QPushButton (plain), ArcaneButton_gold,    │
│                 │  ArcaneButton_muted, ArcaneButton_danger,   │
│                 │  QToolButton                                │
│  Tabulae        │  QTableWidget, QListWidget, QTreeWidget     │
│  Ornamentum     │  QSeparator (H), QSeparator (V),            │
│                 │  QScrollArea, QStackedWidget               │
│  Composita      │  TopBar, StatusBar, SidePanel,             │
│                 │  ArcaneDialog, TabulaHeader                │
╰─────────────────┴──────────────────────────────────────────────╯

### Nesting Behaviour

Drop an element onto a container (Receptacula or Composita category)
to nest it as a child. Nesting is detected by spatial containment at
drop time via `_container_at(scene_pos)`. `setParentItem()` is called
immediately. The child's position becomes relative to the parent's
coordinate space.

**Nesting law:** A child element that visually exceeds its parent's
bounds is a rendering failure. The canvas must accurately represent
containment at all times. Children are clipped to parent bounds on
the canvas and in the Specularium.

### Canvas Session Management

Named canvas sessions are saved as JSON files in `storage/canvases/`.
Sessions are draft-quality saves — distinct from the Armarium.

The dirty state ring ◌ appears in Titulum and Fascia whenever unsaved
changes exist on the canvas. Dirty state clears on save.

On new canvas, session switch, and window close: if dirty state is
active, a prompt fires. The Wizard may save, discard, or cancel.
No unsaved work is silently destroyed.

---

## Inspector Proprietatum — Property Inspection

Editable property panel for the selected canvas element. Updates are
reflected on the canvas immediately and feed the next Specularium rebuild.

### Editable Properties

╭─────────────────────────┬─────────────────────────────────────╮
│  Property               │  Behaviour                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Variable name          │  Python identifier in generated     │
│                         │  code. No spaces, no reserved words.│
│  Width / Height         │  Resizes graphics item immediately  │
│                         │  via setRect(). 16px snap enforced. │
│  Colour token           │  Drop-down of available token names │
│                         │  from active theme. Never raw hex.  │
│  Layout type            │  QVBoxLayout / QHBoxLayout /        │
│                         │  QGridLayout / None (fixed)        │
│  Font size              │  Integer pt. Validated on entry.    │
│  Text content           │  Label/button text. LAT/EN aware.   │
╰─────────────────────────┴─────────────────────────────────────╯

---

## Armarium Componentium — Component Library

SQLite-backed sealed component storage at `storage/armarium.db`.

### Schema

    components table:
      id               INTEGER PRIMARY KEY
      schema_version   TEXT NOT NULL DEFAULT '1.0'
      name             TEXT NOT NULL
      version          INTEGER NOT NULL DEFAULT 1
      category         TEXT
      design_json      TEXT NOT NULL   (serialized ElementNode tree)
      thumbnail        BLOB            (PNG bytes from SpeculariumWindow)
      theme_designator TEXT            (theme name at seal time)
      export_log       TEXT            (JSON array of export timestamps)
      parent_id        INTEGER         (NULL for originals, set on Fork)
      created_at       TEXT NOT NULL
      sealed_at        TEXT NOT NULL

`schema_version` is present from day one. Exvacua Loricum integration
is anticipated at this schema layer — no migration will be required for
that column.

### Operations

**Seal** — saves current canvas state to the Armarium as a named,
versioned component. Thumbnail is captured from the SpeculariumWindow.
Sealing is deliberate. There is no auto-seal.

**Load** — restores a sealed component to the canvas via
`deserialize_all()`. Dirty state guard fires if canvas has unsaved changes.

**Fork** — creates a versioned copy of a sealed component. The copy
gets `parent_id` pointing to the original and `version` incremented.
The original is untouched. Lineage is preserved.

**Export** — generates Python code from a sealed component and copies
to clipboard. Does not require loading to canvas first.

**Filter** — by category and/or theme designator.

**Delete** — not permitted on sealed components. Fork to get a
mutable copy, then abandon the old one via explicit retirement
(future feature). Components accumulate; they are not deleted.

---

## Specularium Vivum — Live Preview

Real PyQt6 widgets rendered from the active design tree. A live mirror
of what the composition will look like when deployed.

### Architecture

Two independent widget instances. Both subscribe to one PreviewDataModel.
Neither owns the data model. The canvas writes it.

    SpeculariumFeaturePage    Embedded within the Specularium feature
                              in the Scriptorium Canvas.

    SpeculariumWindow         Detached floating QMainWindow. Spawned
                              on demand (Ctrl+P). Persists until
                              explicitly closed.

Re-parenting a single widget between QMainWindow and QStackedWidget
destroys its native handle on X11. Two independent instances with one
shared data model is the mandated architecture. This is non-negotiable.

### Refresh Behaviour

Canvas change → `design_changed` signal → PreviewDataModel updated →
both Specularium instances rebuild. Debounce: 200ms. The render log
records clean / stub / error per element.

### X11 Window Spawning

SpeculariumWindow is a top-level QMainWindow. X11 requires:

    150ms deferred timer before show()
    explicit setParent(None) before show()
    raise_() after show()

This pattern applies to all top-level windows in the suite.

---

## Codex Exportum — Code Generation

Walks the element tree and emits Python. Token constants only — no raw
hex literals at any point in the pipeline. Output is validated via
`ast.parse()` before delivery. A valid-but-verbose output is preferable
to an elegant-but-broken one.

### Export Targets

    Clipboard     Default. Ctrl+E or Fascia button.
    File          Optional. Opens file dialog for .py output.

### Validation

`ast.parse()` runs on the generated string before the Wizard receives
it. On failure: the pipeline reports the error and line number. The
Wizard may inspect the canvas and retry. No broken code is delivered.

### Token Compliance

All colour references in generated output must be token names
(C_GOLD, C_PANEL, C_BG, etc.). The presence of any raw hex literal
(`#xxxxxx`) in generated output is a bureau failure condition.

---

## Thema — Theme Management

Full token registry workspace. Bureau I's sovereign output is consumed
here.

### Theme Load

The Wizard points Thema at a `theme.json` produced by Bureau I
(Auctoritas Spectralis). On load:

    QSS applied globally to the entire application.
    canvas.refresh_tokens() called — repaints all existing graphics items
    (setBrush/setPen per element).
    Token drop-downs in Inspector Proprietatum repopulated.

If no external theme.json is loaded, ModusArcanus defaults are active.
The application never falls back to raw system colours.

### Bureau I Sovereignty

Bureau II does not write theme.json. It does not modify it. It does not
guess at colour values. If a token is absent from the loaded theme, the
ModusArcanus default for that token applies. This is the constitutional
dependency.

---

## Auxilium — Per-Feature Help

F1 opens contextual help for the currently active feature. Non-modal,
floating QDialog. The Wizard may dismiss with Escape or by closing the
window.

Each feature has a dedicated Auxilium page covering: feature overview,
controls reference, workflow description, and known edge cases.

---

# VI. KEYBOARD REFERENCE

╭──────────────────────────┬──────────────────────────────────────╮
│  Shortcut                │  Action                              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Ctrl+Z                  │  Undo (50-step stack)               │
│  Ctrl+Shift+Z            │  Redo                               │
│  Ctrl+S                  │  Save current canvas session        │
│  Ctrl+E                  │  Export code to clipboard           │
│  Ctrl+P                  │  Toggle SpeculariumWindow           │
│  F1                      │  Open Auxilium for active feature   │
│  Delete                  │  Delete selected canvas element     │
│  Escape                  │  Deselect / close dialogs           │
│  Any key                 │  Dismiss Opening Ceremony           │
╰──────────────────────────┴──────────────────────────────────────╯

---

# VII. DIRTY STATE PROTOCOL

The dirty state ring ◌ (U+25CC) is the ratified indicator across all
three bureaus of the Triumviratus. The Anima Dot ● was not selected.
The asterisk * was retired by Convocatio ruling.

╭──────────────────────────┬──────────────────────────────────────╮
│  Condition               │  Ring appears in                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Unsaved canvas changes  │  Titulum and Fascia                  │
╰──────────────────────────┴──────────────────────────────────────╯

Dirty state prompt fires on: new canvas, canvas session switch, and
window close. Options: Save, Discard, Cancel.

---

# VIII. DATA FORMATS

## Canvas Session JSON

    {
      "schema_version": "1.0",
      "name": "session_name",
      "saved_at": "ISO-8601 timestamp",
      "elements": [ ... list of ElementNode dicts ... ]
    }

## ElementNode dict

    {
      "type": "QFrame",
      "category": "Receptacula",
      "x": 100,
      "y": 80,
      "w": 400,
      "h": 300,
      "properties": {
        "var_name": "main_frame",
        "colour_token": "C_PANEL",
        "layout_type": "QVBoxLayout"
      },
      "children": [ ... nested ElementNode dicts ... ]
    }

The `x` and `y` fields on child elements are parent-relative. This is
a known open item: the serialization round-trip for nested children
must include parent-relative coordinates. Any build that does not
correctly round-trip child `x`/`y` fails the containment test suite.

## Armarium Component record

    {
      "schema_version": "1.0",
      "id": integer,
      "name": "string",
      "version": integer,
      "category": "string",
      "design_json": "ElementNode JSON string",
      "theme_designator": "string",
      "parent_id": null or integer,
      "created_at": "ISO-8601",
      "sealed_at": "ISO-8601"
    }

---

# IX. KNOWN OPEN ITEMS

╭────────────────────────────────────┬─────────────────────────────╮
│  Item                              │  Status                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Nested child x/y round-trip gap   │  Open. x/y must be in       │
│  (serialize() omits coords)        │  serialize() output.        │
│                                    │  Day-one fix required.      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Handle-based canvas resize        │  Deferred. Inspector-only   │
│  (corner drag handles)             │  resize for now.            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Child resize capping (prevent     │  Requires ratification      │
│  child exceeding parent on resize) │  before implementation.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Component deletion / retirement   │  Not implemented. Components│
│  workflow                          │  accumulate. Future feature.│
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Exvacua Loricum integration       │  Schema version field       │
│                                    │  reserved. Integration when │
│                                    │  service is built.          │
╰────────────────────────────────────┴─────────────────────────────╯

---

# X. FAILURE CONDITIONS

The bureau has failed its purpose if any of the following are true:

- Generated code contains a raw hex value.
- A sealed component cannot be deserialized back to an identical canvas state.
- The Specularium renders a different composition than the canvas shows.
- A child element is rendered outside its parent container's visible bounds.
- The application modifies, overwrites, or guesses at theme.json.
- `ast.parse()` validation is bypassed or disabled.
- Any of the 21 tests in the test suite fail.

---

# XI. TEST SUITE

21 tests must pass at all times. Any change to the application that causes
a test regression is not a valid change. Resolve the regression before
proceeding.

Test categories include: CanvasElement creation and serialization, nesting
detection and containment, ElementNode round-trip (serialize → deserialize),
nested child x/y preservation, token compliance in codegen output, AST
validation of generated code, Armarium CRUD and fork operations, dirty state
logic, canvas session persistence, theme load and refresh_tokens() propagation,
language toggle propagation.

---

# XII. GLOSSARY

See Expositio v1.2 Section IX for the full canonical glossary. Key terms:

Agentia — short form of Agentia Architecturalis.
Armarium — the Component Library. SQLite-backed sealed storage.
Auxilium — per-feature help dialog. F1.
CanvasElement — abstract base for all placeable canvas items.
Codex Exportum — the code generation feature.
Composita — palette category for pre-built composite ModusArcanus patterns.
Dirty state — unsaved canvas changes. Indicated by ◌ (U+25CC).
Elementarium — element browser within the Tabula feature.
ElementNode — serialized dict representation of a CanvasElement.
Fascia — Zone III. 52px top-right strip.
Feature Codex — Zone II. Left rail navigation.
Fork — versioned copy of a sealed Armarium component.
Inspector Proprietatum — property editor for selected canvas element.
PreviewDataModel — shared data holder for both Specularium instances.
Receptacula — palette category for containers.
Scriptorium Canvas — Zone IV. Feature-owned workspace.
Seal — deliberate, irreversible save to the Armarium.
Specularium Vivum — live preview. Two instances, one data model.
Tabula Designandi — the design canvas feature.
Thema — theme management feature.
Titulum — Zone I. 220px left panel. Identity and context.
Token — named colour constant (C_GOLD, C_PANEL, etc.). Never raw hex.

---

*Sigillatum per Aedificatorem · Bureau II · MMXXVI*

*In Linea · In Parallelo · In Perpetuum*

*Ordo Discordia, Cosmos Inania*

*⟁*
