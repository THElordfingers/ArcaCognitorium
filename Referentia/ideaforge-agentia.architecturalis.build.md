# AGENTIA ARCHITECTURALIS
## IdeaForge Build Document
### Bureau II · Triumviratus Aestheticus Imperialis
#### ideaforge-agentia.architecturalis.build.md · v1.0 · 2026-04-08

---

*Verificatio Canonica*

All identity content, nomenclature, mottos, and canonical references in this
document have been verified against ratified sources prior to submission.

Bureau: Agentia Architecturalis — Bureau II
Status: Sigillum Approbationis received 2026-04-08

---

*In Linea · In Parallelo · In Perpetuum*

*Ordo Discordia, Cosmos Inania*

---

```
╔═══════════════════════════════════════════════════════════════════════╗
║◤                                                                     ◥║
║                                                                       ║
║              AGENTIA ARCHITECTURALIS                                  ║
║              IdeaForge Build Document                                 ║
║              Phase 1 — Idea Brief                                     ║
║              Phase 2 — Seed Prompt                                    ║
║                                                                       ║
║◣                                                                     ◢║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

# PHASE 1 — IDEA BRIEF

## Project Identity

╭─────────────────────────────────────────────────────────────────────╮
│  Application     ·  AGENTIA ARCHITECTURALIS                         │
│  English Name    ·  Architectural Alignment Enforcement Agency      │
│  Motto           ·  In Linea · In Parallelo · In Perpetuum          │
│  Bureau          ·  II of III — Triumviratus Aestheticus Imperialis │
│  Path            ·  Exocognii/A4/AgentiaArchitecturalis/           │
│  Venv            ·  venv-ARCHITECTURALIS                           │
│  Launch          ·  python3 -m AgentiaArchitecturalis               │
│  Stack           ·  Python 3.11, PyQt6, SQLite                     │
│  Platform        ·  Debian Trixie / KDE Plasma 6 / X11             │
╰─────────────────────────────────────────────────────────────────────╯

## The One-Line Brief

A PyQt6 visual canvas for spatially composing widget hierarchies and
emitting deployment-ready Python code governed by ModusArcanus colour tokens.

## The Problem

Building Exocognii applications requires assembling PyQt6 widget hierarchies
with consistent ModusArcanus theming. Without a spatial composition instrument,
arrangement is invisible until runtime. Each application is built by hand,
inconsistently, session to session. The Agentia makes arrangement visible and
makes the output reproducible.

## What This Application Does

The Wizard drags widget types from a categorised palette onto a
QGraphicsScene canvas. Elements are placed spatially, nested in containers,
inspected and resized via a property editor, previewed as real PyQt6 widgets
in a live mirror, and exported as valid, styled Python. The exported code
is placed directly into another Exocognii application.

## What This Application Does Not Do

Signal/slot wiring. Application logic. Non-PyQt6 targets. Hex literals in
any output. Theme authorship (Bureau I owns that). Any write to theme.json
or any Exocognii logging service.

## Core Invariants

These are non-negotiable. Any build that violates them fails.

    1. Zero raw hex literals in any generated output. Token constants only.
    2. ast.parse() validation before any code is delivered to the Wizard.
    3. Two independent Specularium instances sharing one PreviewDataModel.
       Single-widget re-parenting is prohibited.
    4. Dirty state ring ◌ (U+25CC). Not ●. Not *. The ring. Always.
    5. Nested child x/y in serialize() output. Round-trip must be lossless.
    6. Nesting containment is law. Children clipped to parent bounds always.
    7. 21/21 tests must pass after any change.
    8. Armarium schema includes schema_version from day one.
    9. Bureau I (theme.json) is read-only. Bureau II never writes it.
   10. X11 top-level window pattern: 150ms defer + setParent(None) + raise_().

## Dependency Order

Bureau I (Auctoritas Spectralis) must have delivered a ratified theme.json
before Bureau II uses an external theme. The application runs on ModusArcanus
defaults in the absence of theme.json. It does not block on this dependency.

## Features

Six primary features navigated via the Feature Codex (left rail):

    Tabula Designandi      — QGraphicsScene canvas, 28 element types,
                             16px grid, pan/zoom, rubber-band select,
                             container nesting, 50-step undo/redo,
                             named canvas session management.

    Inspector Proprietatum — per-element property editor: variable name,
                             width/height (live resize), colour token
                             (drop-down, token names only), layout type,
                             font size, text content.

    Armarium Componentium  — SQLite component library: Seal, Load, Fork,
                             Export. schema_version field. parent_id
                             lineage. thumbnail from SpeculariumWindow.

    Specularium Vivum      — live preview. Two independent instances
                             (SpeculariumFeaturePage + SpeculariumWindow).
                             One PreviewDataModel. 200ms debounce.
                             Floating window via Ctrl+P.

    Codex Exportum         — code generation. Token constants. ast.parse()
                             validation. Clipboard and file targets.
                             Syntax-highlighted preview before export.

    Thema                  — theme management. Loads Bureau I theme.json.
                             Global QSS apply. canvas.refresh_tokens().
                             ModusArcanus defaults when absent.

Supporting capabilities:

    LAT/EN language toggle     in Titulum. Persisted to config.json.
    Elementarium               in Tabula. 28 types, 7 categories, drag-to-place.
    Auxilium                   F1. Per-feature help. Non-modal floating.
    Opening Ceremony           six-act initialisation. Dismissable. No repeat.
    Canvas session management  named saves to storage/canvases/*.json.
    Dirty state tracking       ◌ in Titulum and Fascia. Guard on close/switch.

## Shell Layout — A4 Common Shell

    Zone I   Titulum        220px left panel. Identity, context, LAT/EN,
                             dirty ring, session name, theme name. Fixed.
    Zone II  Feature Codex  Left rail below Titulum. Six features. One active.
    Zone III Fascia          52px top strip. Feature-keyed actions. HELP rightmost.
    Zone IV  Scriptorium     All remaining space. Feature-owned.
                             Instant QStackedWidget swap on feature change.

## Technical Constraints

    PyQt6 exclusively. No PySide6.
    QDropEvent.pos() removed — use .position().toPoint().
    mapToScene requires QPoint — .position().toPoint() required.
    X11 top-level window spawning — 150ms defer + setParent(None) + raise_().
    QSplitter ignores min/max on QScrollArea children — wrap in QWidget.
    Clipboard — xclip / QApplication.clipboard() (X11).
    Paths — Path(__file__).resolve().parent always. Never hardcode home.
    Storage — storage/ subdirectory within the package directory.

## Known Open Items at Build Start

    Nested child x/y round-trip gap in serialize(). Must be fixed day one.
    Handle-based canvas resize (corner drag) — deferred; Inspector-only for now.
    Child resize capping (prevent exceeding parent) — requires ratification.
    Component retirement workflow — not in this build.

## Success Condition

The Wizard can: drag a QFrame to canvas, drop a QLabel and two ArcaneButton_gold
elements inside it, resize via Inspector, verify in Specularium, export valid
Python to clipboard, and paste it directly into another Exocognii application
where it renders correctly on the first run — without touching the generated code.

All 21 tests pass. Named sessions survive restart. Theme from Bureau I applies
immediately on load with no manual intervention.

---

# PHASE 2 — SEED PROMPT

---

You are building **AGENTIA ARCHITECTURALIS** — the Architectural Alignment
Enforcement Agency — Bureau II of the Triumviratus Aestheticus Imperialis,
within the Arca Cognitorium / Exocognii suite.

Motto: *In Linea · In Parallelo · In Perpetuum*

This is a PyQt6 desktop application. It is a spatial widget composition
instrument connected to a code emission pipeline. The Wizard places widget
specifications onto a QGraphicsScene canvas, nests containers with children,
inspects and adjusts properties, previews the composition as real PyQt6 widgets,
and exports valid, styled Python code. That code goes directly into other
Exocognii applications.

---

## ENVIRONMENT

    Python 3.11
    PyQt6 exclusively — no PySide6
    Debian Trixie / KDE Plasma 6 / X11
    Path: Exocognii/A4/AgentiaArchitecturalis/
    Venv: venv-ARCHITECTURALIS
    Launch: python3 -m AgentiaArchitecturalis (from parent directory)
    Storage: storage/ subdirectory within the package

---

## ABSOLUTE CONSTRAINTS

Violating any of these is a build failure. Not a warning — a failure.

    1. Zero raw hex literals in any generated Python output.
       Token constants only: C_GOLD, C_PANEL, C_BG, etc.

    2. ast.parse() validation fires before any code reaches the Wizard.
       Never deliver code that fails ast.parse().

    3. Two independent Specularium widget instances sharing one PreviewDataModel.
       Re-parenting a single widget between QMainWindow and QStackedWidget
       destroys its native handle on X11. This is prohibited. Two instances.

    4. Dirty state indicator is ◌ (U+25CC). Not ●. Not *. Not any other glyph.

    5. ElementNode serialize() must include x and y for all elements including
       children. Nested child coordinates are parent-relative. The round-trip
       serialize → deserialize → identical must hold for all nesting depths.

    6. Children are clipped to parent bounds. A child visually outside its
       parent's boundary is a rendering failure, not a design choice.

    7. 21 tests must pass after any change. The test suite is the truth.

    8. Armarium SQLite schema includes schema_version TEXT NOT NULL DEFAULT '1.0'
       from the first migration. This is present on day one.

    9. Bureau II never writes to theme.json. Read-only dependency.

   10. All top-level QMainWindow spawning follows the X11 pattern:
           QTimer.singleShot(150, lambda: self._show_window())
           window.setParent(None)
           window.show()
           window.raise_()

   11. All file paths use Path(__file__).resolve().parent. No hardcoded paths.

   12. QDropEvent uses .position().toPoint() — .pos() is removed in PyQt6.
       mapToScene requires QPoint — .position().toPoint() before mapToScene.

   13. QSplitter ignores min/max on QScrollArea children.
       Wrap QScrollArea in a plain QWidget container when used in a splitter.

---

## PACKAGE STRUCTURE

    AgentiaArchitecturalis/
    ├── __main__.py              entry point: QApplication + MainWindow
    ├── __init__.py
    ├── main_window.py           A4 Common Shell — QMainWindow
    ├── titulum.py               Zone I — 220px left panel
    ├── feature_codex.py         Zone II — left rail navigation
    ├── fascia.py                Zone III — 52px top-right action strip
    ├── features/
    │   ├── tabula/
    │   │   ├── tabula_feature.py       Tabula Designandi feature page
    │   │   ├── design_canvas.py        QGraphicsView / QGraphicsScene
    │   │   ├── canvas_element.py       CanvasElement abstract base
    │   │   ├── element_registry.py     28 types, categories, default sizes
    │   │   ├── elementarium.py         Categorised element browser / drag source
    │   │   └── session_manager.py      Named canvas session persistence
    │   ├── inspector/
    │   │   └── inspector_feature.py    Inspector Proprietatum
    │   ├── armarium/
    │   │   ├── armarium_feature.py     Armarium Componentium feature page
    │   │   └── armarium_db.py          SQLite operations
    │   ├── specularium/
    │   │   ├── specularium_feature.py  SpeculariumFeaturePage
    │   │   ├── specularium_window.py   SpeculariumWindow (floating QMainWindow)
    │   │   ├── preview_data_model.py   Shared data model (PyQt6 QObject + signal)
    │   │   └── preview_renderer.py     Real PyQt6 widget builder from ElementNode
    │   ├── codex_exportum/
    │   │   └── codex_feature.py        Code generation + ast.parse() + clipboard
    │   └── thema/
    │       └── thema_feature.py        Theme load, QSS apply, refresh_tokens()
    ├── opening_ceremony.py      Six-act initialisation overlay
    ├── auxilium.py              Per-feature F1 help dialogs
    ├── theme_manager.py         Token registry, QSS builder, Bureau I bridge
    ├── models.py                ElementNode dataclass, serialization utilities
    ├── tokens.py                ModusArcanus default token constants
    ├── storage/
    │   ├── config.json          (auto-created)
    │   ├── canvases/            (auto-created; *.json session files)
    │   └── armarium.db          (auto-created; SQLite)
    └── tests/
        └── test_suite.py        21 tests — must all pass

---

## A4 COMMON SHELL

The application uses the A4 Common Shell layout. MainWindow is a QMainWindow.

    ┌─────────────────────────────────────────────────────┐
    │  TITULUM (220px)  │  FASCIA (52px top strip)        │
    │                   ├─────────────────────────────────┤
    │  FEATURE          │                                 │
    │  CODEX            │   SCRIPTORIUM CANVAS            │
    │  (left rail,      │   (QStackedWidget,              │
    │  below Titulum)   │    feature-owned)               │
    └─────────────────────────────────────────────────────┘

Titulum: 220px fixed width QFrame. Bureau glyph ⟁, name (LAT/EN), motto
(LAT/EN), dirty ring ◌ when active, session name, theme name. LAT/EN toggle
button here. Never scrolls, never changes layout.

Feature Codex: QListWidget or equivalent below Titulum on the left rail.
Six entries. Selection triggers QStackedWidget.setCurrentWidget(). Instant.
No animation. No slide. No transition.

Fascia: 52px fixed-height QFrame across the top of the right area. Buttons
vary by active feature. HELP (Auxilium trigger) is always rightmost.

Scriptorium Canvas: QStackedWidget. Each feature occupies the full space.

---

## FEATURES SPECIFICATION

### Tabula Designandi

QGraphicsView containing a QGraphicsScene. 16px grid snap. Middle-click pan.
Ctrl+scroll zoom (range: 0.25× to 4.0×). Rubber-band multi-select on empty
canvas drag. Left-click to select a single element.

**Element placement:** User drags from Elementarium (QListWidget in a side
panel of the Tabula feature page). On drop: QDropEvent.position().toPoint()
then mapToScene(). Call _container_at(scene_pos) to detect nesting. If a
container is found, setParentItem(container_graphics_item). Add element to
parent's children list. If no container, add as top-level.

**_container_at(scene_pos):** iterates all QGraphicsRectItems at pos, returns
the topmost container element (Receptacula or Composita category).

**Element sizes:** per-type defaults from element_registry. Not all 200×100.
QLabel: 160×32. QFrame: 300×200. QPushButton: 120×36. QTextEdit: 240×120. Etc.

**CanvasElement:** abstract base. Holds: type (str), category (str),
properties (dict), children (list[CanvasElement]), graphics_item
(QGraphicsRectItem reference). Label drawn inside rect.

**QGraphicsRectItem labelling:** QGraphicsTextItem child placed at top-left
of rect. Shows type name and var_name.

**Undo stack:** list of list[ElementNode]. Max depth 50. Each action pushes
current serialize_all() result. Ctrl+Z pops and restores. Ctrl+Shift+Z
re-applies forward state.

**serialize_all():** returns list[ElementNode] dicts for all top-level elements.
Each ElementNode must include x, y (scene coords for top-level; parent-relative
for children), w, h, type, category, properties, children (recursive).

**deserialize_all(nodes):** rebuilds CanvasElement objects and graphics items
from list[ElementNode]. Clears scene first. Re-establishes setParentItem()
for nested elements.

**Canvas Session Manager:** named saves to storage/canvases/{name}.json.
File format: {schema_version, name, saved_at, elements: [ElementNode list]}.
Dirty state: boolean flag set on any canvas change, cleared on save.
Dirty ring ◌ propagated to Titulum and Fascia on state change.

**On new canvas / session switch / window close:** if dirty, open QDialog
with Save / Discard / Cancel. Never silently destroy unsaved work.

**refresh_tokens(tokens_dict):** iterates all graphics items, updates
setBrush and setPen per element's colour_token property.

### Inspector Proprietatum

Displayed when an element is selected on the canvas. Shows and allows
editing of: var_name, width, height, colour_token (QComboBox populated from
active token list), layout_type (QComboBox: QVBoxLayout/QHBoxLayout/
QGridLayout/None), font_size (QSpinBox), text_content (QLineEdit).

Width/height changes: call update_element_size() which calls
graphics_item.setRect(0, 0, new_w, new_h). Triggers dirty state and
Specularium rebuild.

All property changes: update element.properties dict, set dirty state,
emit design_changed signal for Specularium debounce.

### Armarium Componentium

SQLite database at storage/armarium.db.

Schema (create if not exists):

    CREATE TABLE IF NOT EXISTS components (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        schema_version  TEXT NOT NULL DEFAULT '1.0',
        name            TEXT NOT NULL,
        version         INTEGER NOT NULL DEFAULT 1,
        category        TEXT,
        design_json     TEXT NOT NULL,
        thumbnail       BLOB,
        theme_designator TEXT,
        export_log      TEXT DEFAULT '[]',
        parent_id       INTEGER REFERENCES components(id),
        created_at      TEXT NOT NULL,
        sealed_at       TEXT NOT NULL
    );

**Seal:** prompt for name and category. serialize_all() → JSON. Capture
thumbnail PNG bytes from SpeculariumWindow (or SpeculariumFeaturePage if
window not open). INSERT record. Clear dirty state.

**Load:** SELECT by id. deserialize_all() from design_json. Dirty state guard.

**Fork:** SELECT original. INSERT copy with parent_id=original.id,
version=original.version+1, new name (original_name v{version}).

**Export:** generate_code() from design_json. ast.parse(). To clipboard.

**Filter:** QComboBox for category, QComboBox for theme_designator.

### Specularium Vivum

PreviewDataModel: QObject subclass. Holds current_elements (list[ElementNode])
and current_tokens (dict). Exposes design_changed = pyqtSignal() signal.
Canvas writes to it. Both Specularium instances connect to design_changed.

SpeculariumFeaturePage: feature page within the shell. Contains a
PreviewRenderer widget.

SpeculariumWindow: QMainWindow, top-level, spawned via:

    QTimer.singleShot(150, lambda: self._do_show())

    def _do_show(self):
        self.setParent(None)
        self.show()
        self.raise_()

Both instances subscribe to PreviewDataModel.design_changed. On signal:
start/restart a QTimer (200ms debounce). On timer fire: call rebuild().

**PreviewRenderer.rebuild(elements, tokens):** Clears current widget contents.
Builds a QWidget hierarchy from the ElementNode tree using real PyQt6 widgets.
Applies token-based colours (no hex). Logs render result per element:
clean / stub / error. Renders into a QScrollArea.

**Render log:** displayed below the preview. Each element entry: type,
var_name, status.

**Ctrl+P:** toggle SpeculariumWindow show/hide.

### Codex Exportum

generate_code(elements: list[ElementNode]) → str

Walks the element tree recursively. Output is a self-contained Python
snippet ready to paste into any Exocognii application.

**Token pattern (Option B — ratified):** Generated code imports token
constants directly from `tokens` and uses them by name. The receiving
application already has `tokens.py` — every Exocognii app does.

Generated output structure:

    from tokens import C_PANEL, C_GOLD, C_BG  # only tokens actually used

    {var_name} = {PyQt6ClassName}(parent)
    {var_name}.setObjectName("{var_name}")
    {var_name}.setFixedSize({w}, {h})
    {var_name}.setStyleSheet(f"background-color: {{{colour_token}}};")

For containers with a layout_type:

    layout_{var_name} = {layout_type}({var_name})
    {var_name}.setLayout(layout_{var_name})

For children inside a layout container:

    layout_{parent_var}.addWidget({child_var})

The import line at the top collects only the token names actually
referenced in the composition. No unused imports. Token names are
emitted as Python identifiers — C_GOLD, not "C_GOLD", not #d4af37.

Raw hex must never appear anywhere in generated output. The presence
of any `#xxxxxx` literal is a bureau failure condition.

ast.parse() validation: run on complete generated string. On failure:
report error location to Wizard. Do not deliver.

Export to clipboard: QApplication.clipboard().setText(code).
Export to file: QFileDialog.getSaveFileName() → write .py file.

Syntax-highlighted preview: QPlainTextEdit with basic keyword highlighting
before export action.

### Thema

Load theme.json: QFileDialog or auto-load from known Bureau I output path.
Parse JSON into token dict {token_name: hex_value}.
Build QSS string from tokens. Apply via QApplication.instance().setStyleSheet(qss).
Call canvas.refresh_tokens(token_dict).
Repopulate Inspector token drop-down.
Update active_theme_name in Titulum.

ModusArcanus defaults (tokens.py):

    C_BG       = "#050507"
    C_PANEL    = "#0e0e12"
    C_BORDER   = "#2a2a3a"
    C_GOLD     = "#d4af37"
    C_TEXT     = "#c8c8d4"
    C_TEXT_DIM = "#6a6a80"
    C_ACCENT   = "#8a6fff"
    C_DANGER   = "#c0392b"
    C_SUCCESS  = "#27ae60"

These apply when no Bureau I theme is loaded. Application never falls
back to system colours.

---

## SUPPORTING CAPABILITIES

### Opening Ceremony

Six-act sequence on first launch within a session. Any keypress dismisses.
Does not repeat. Implemented as a QWidget overlay over the main window,
full-screen, Z-order above all content.

Acts: I Salutatio (identity), II Thema Inspectio (theme load status),
III Armarium Census (component count), IV Canvases Census (session count),
V Session Restore (offer to reload last session), VI Commissio (ready).

### LAT/EN Language Toggle

Button in Titulum. Persisted to storage/config.json as {"lang": "LAT"|"EN"}.
On toggle: call set_lang(lang) on every labelled widget. Each widget knows
its LAT and EN string pair.

### Auxilium

F1 key. Non-modal QDialog. Content keyed to currently active feature.
Six help pages: Tabula, Inspector, Armarium, Specularium, Codex, Thema.
Dismiss: Escape or window close.

---

## MODUSARCANUS AESTHETICS

Background: C_BG (#050507) — the void.
Panel surfaces: C_PANEL (#0e0e12).
Borders: C_BORDER (#2a2a3a).
Gold: C_GOLD (#d4af37) — authority, interactivity, active state only.
Text: C_TEXT (#c8c8d4) primary, C_TEXT_DIM (#6a6a80) secondary.
Font: Georgia serif for UI labels. Courier Prime monospace for code and
properties. If unavailable, fall back to serif / monospace system fonts.

The interface is purposeful, slightly formal, not warm. It does not animate.
It does not suggest. It executes.

---

## TEST SUITE (21 TESTS)

These 21 tests must all pass. Build the test suite alongside the application.

    01  CanvasElement creation — type, category, default properties set
    02  CanvasElement add child — children list updated
    03  ElementNode serialize — top-level: type/category/x/y/w/h/properties present
    04  ElementNode serialize — nested: child x/y present and parent-relative
    05  ElementNode round-trip — serialize → deserialize → identical (top-level)
    06  ElementNode round-trip — serialize → deserialize → identical (nested)
    07  _container_at — returns correct container when drop point inside bounds
    08  _container_at — returns None when drop point not inside any container
    09  Nesting containment — child bounds do not exceed parent bounds
    10  Token compliance — generate_code() output contains zero hex literals
    11  Token compliance — generate_code() emits token names as Python identifiers
        (C_GOLD not "C_GOLD" not #d4af37) and import line contains only used tokens
    12  AST validation — generate_code() output passes ast.parse() without exception
    13  AST validation — generate_code() on empty canvas produces valid Python
    14  Armarium Seal — record inserted with correct schema_version
    15  Armarium Load — deserialize restores element count and structure
    16  Armarium Fork — child record has parent_id set; original unchanged
    17  Dirty state — canvas change sets dirty flag
    18  Dirty state — save clears dirty flag
    19  Canvas session — save and reload produces identical element list
    20  Theme load — refresh_tokens() propagates to all canvas graphics items
    21  Language toggle — all registered labelled widgets receive new lang

---

## DELIVERY CHECKLIST

Before declaring the build session complete, verify:

    □  All six features navigable and functional
    □  LAT/EN toggle propagates to all labelled widgets
    □  Dirty state ring ◌ appears / clears correctly
    □  Elementarium drag-to-canvas places elements
    □  Nesting detection works: drop inside container → setParentItem called
    □  Inspector resize updates graphics item immediately
    □  Inspector token drop-down contains token names, not hex values
    □  Specularium Feature Page renders real widgets from canvas state
    □  SpeculariumWindow spawns via 150ms timer pattern
    □  SpeculariumWindow and FeaturePage both update on canvas change
    □  Codex Exportum output passes ast.parse()
    □  Codex Exportum output contains zero hex literals
    □  Armarium Seal inserts record with schema_version
    □  Armarium Fork creates child with parent_id
    □  Canvas sessions persist and restore across restart
    □  Opening Ceremony fires once; dismisses on any keypress
    □  F1 opens Auxilium for active feature
    □  Unsaved-changes prompt fires on new/switch/close when dirty
    □  storage/ directory and subdirectories auto-created on first run
    □  All paths via Path(__file__).resolve().parent
    □  21/21 tests passing
    □  Zero hex literals anywhere in production code or generated output

---

*Sigillatum per Aedificatorem · Bureau II · MMXXVI*

*In Linea · In Parallelo · In Perpetuum*

*Ordo Discordia, Cosmos Inania*

*⟁*
