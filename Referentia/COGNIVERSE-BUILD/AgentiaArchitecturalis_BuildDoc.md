# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ     AgentiaArchitecturalis_BuildDoc.md   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

# AGENTIA ARCHITECTURALIS — In Linea, In Parallelo, In Perpetuum
## Bureau II · The Architectural Alignment Enforcement Agency · AAEAgency
### Developer-Ready Build Document · v1.0

> **Parent Alliance:** Aesthetic Authoritarian Associative Alliance (A4)
> *Triumviratus Aestheticus Imperialis*
>
> **Bureau Seal:** *Agentia Architecturalis*
> **Mandate:** Every widget placed under this agency's authority
> conforms to the arcane standard. No element is unsanctioned.

---

## Table of Contents

1.  Overview & Architecture
2.  Tech Stack
3.  Directory Tree & Database Schema
4.  Module Breakdown
5.  UI Wireframe
6.  Data Flow
7.  Code Stubs
8.  Error Handling
9.  Setup & Testing
10. Packaging
11. Extensibility

---

## 1. Overview & Architecture

Agentia Architecturalis is a PyQt6 visual UI component designer.
The Wizard assembles interface panels and widget compositions by
selecting elements from a categorized palette, placing them on a
live canvas, configuring their properties through an inspector, and
previewing the result as real rendered PyQt6 widgets. Completed
designs are saved to a Component Library (SQLite), categorized by
type and purpose, and can be loaded, altered, forked, and
re-exported at any time. The final output is a minimal, clean
Python/PyQt6 code block ready for integration into Tower
applications or handoff to The Builder via Arx Aedificare.

This tool replaces the Fenestrarium. It is not a code editor — it
is a visual sandbox where the Wizard works spatially, not
textually. Code generation is an export artifact, not the primary
interaction surface.

Bureau II consumes `theme.json` from Bureau I (Auctoritas
Spectralis). All color values on the canvas are drawn from the
active ratified palette. When no ratified palette is loaded, the
ModusArcanus defaults apply. Widget patterns from ModusArcanus are
baked into the element palette as pre-configured factories — the
dux tome is the source of truth at build time, not at runtime.

### Architecture Stages

╭──────────────────┬──────────────────────────────────────────────╮
│ Stage            │ Role                                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Selectio         │ Browse and select elements from the          │
│                  │ categorized widget palette                   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Compositio       │ Place, arrange, and nest elements on the     │
│                  │ canvas via drag-and-drop or click-to-place   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Inspectio        │ Configure properties of the selected         │
│                  │ element — colors, sizing, labels, spacing,   │
│                  │ layout role                                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Specularium      │ Live preview — real PyQt6 widgets rendered   │
│                  │ from the canvas composition, skinned by the  │
│                  │ active theme                                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Armarium         │ Save to / load from the Component Library;   │
│                  │ categorize, search, fork, version            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Promulgatio      │ Export as Python/PyQt6 code block;            │
│                  │ copy to clipboard or write to file            │
╰──────────────────┴──────────────────────────────────────────────╯

### Keyboard Shortcuts

╭──────────────┬──────────────────────────────────────────────────╮
│ Binding      │ Action                                           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ q            │ Exire — quit application                        │
│ Ctrl+S       │ Sigillare — save current design to library      │
│ Ctrl+Shift+S │ Sigillare Novum — save as new entry             │
│ Ctrl+E       │ Exportare — export code to clipboard            │
│ Ctrl+Shift+E │ Exportare Filum — export code to file           │
│ Ctrl+Z       │ Revocare — undo                                 │
│ Ctrl+Shift+Z │ Restituere — redo                               │
│ Ctrl+N       │ Novum — new blank canvas                        │
│ Ctrl+O       │ Aperire — open from library                     │
│ Ctrl+L       │ Armarium — toggle library drawer                │
│ Ctrl+T       │ Thema — load a theme.json                       │
│ Ctrl+P       │ Specularium — toggle live preview               │
│ Delete       │ Dissolvere — remove selected element            │
│ Ctrl+D       │ Duplicare — duplicate selected element          │
│ Ctrl+G       │ Congregare — group selected elements            │
│ Ctrl+Shift+G │ Discindere — ungroup                            │
│ F1           │ Auxilium — help                                  │
╰──────────────┴──────────────────────────────────────────────────╯

---

## 2. Tech Stack

╭───────────────────────┬───────────┬──────────────────────────────╮
│ Tool                  │ Version   │ Justification                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Python                │ 3.11+     │ Suite standard               │
│ PyQt6                 │ 6.6+      │ ModusArcanus framework;      │
│                       │           │ QGraphicsScene for canvas    │
│ sqlite3               │ stdlib    │ Component Library storage    │
│ json                  │ stdlib    │ theme.json consumption,      │
│                       │           │ design serialization         │
│ pathlib               │ stdlib    │ Path resolution              │
│ textwrap / ast        │ stdlib    │ Code generation formatting   │
╰───────────────────────┴───────────┴──────────────────────────────╯

No ClaudeBox. No AI integration. No colour-science (colors come
from Bureau I's output). No network dependency. Fully offline.

---

## 3. Directory Tree & Database Schema

### File Tree

```
~/ArcaCognitorium/Exocognii/
└── AestheticAuthoritarianAssociativeAlliance/
    └── AgentiaArchitecturalis/
        ├── __init__.py
        ├── __main__.py                 # Entry point
        ├── app.py                      # QApplication setup + main window
        ├── canvas.py                   # QGraphicsScene/View design canvas
        ├── palette.py                  # Element palette — categorized widget list
        ├── inspector.py                # Property inspector for selected element
        ├── preview.py                  # Live preview renderer
        ├── library.py                  # Component Library SQLite operations
        ├── codegen.py                  # Python/PyQt6 code generation engine
        ├── theme_loader.py             # theme.json consumer + QSS applicator
        ├── schema.py                   # Design serialization format TypedDict
        ├── constants.py                # ModusArcanus defaults, palette categories
        ├── workers.py                  # QRunnable + WorkerSignals for IO
        ├── elements/
        │   ├── __init__.py
        │   ├── base.py                 # CanvasElement ABC — all elements inherit
        │   ├── containers.py           # QFrame, QGroupBox, QSplitter, QTabWidget
        │   ├── inputs.py               # QLineEdit, QComboBox, QSlider, QSpinBox
        │   ├── displays.py             # QLabel (gold, dim, micro), QProgressBar
        │   ├── buttons.py              # arcane_button variants, toggle, icon btn
        │   ├── tables.py               # QTableView, QHeaderView
        │   ├── text.py                 # QTextEdit, QPlainTextEdit (read-only)
        │   ├── decorative.py           # QFrame separators, spacers, rule lines
        │   └── composite.py            # Pre-built ModusArcanus patterns:
        │                               #   TopBar, StatusBar, ControlPanel,
        │                               #   SectionHeader, SwatchStrip
        ├── storage/
        │   └── component_library.db    # SQLite (created on first run)
        ├── exports/                    # Generated code files land here
        └── tests/
            ├── test_canvas.py
            ├── test_codegen.py
            ├── test_library.py
            ├── test_theme_loader.py
            ├── test_elements.py
            └── test_integration.py
```

### Database Schema — Component Library

```sql
CREATE TABLE IF NOT EXISTS components (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    category        TEXT    NOT NULL,  -- 'panel' | 'dialog' | 'toolbar' |
                                      -- 'card' | 'composite' | 'fragment'
    description     TEXT    DEFAULT '',
    design_json     TEXT    NOT NULL,  -- serialized DesignDocument
    thumbnail_png   BLOB    DEFAULT NULL,  -- 256x256 snapshot
    version         INTEGER NOT NULL DEFAULT 1,
    parent_id       INTEGER DEFAULT NULL REFERENCES components(id),
                                      -- non-null = forked from parent
    theme_designator TEXT   DEFAULT NULL,  -- theme.json designator used
    created_at      TEXT    NOT NULL,  -- ISO 8601
    updated_at      TEXT    NOT NULL,  -- ISO 8601
    tags            TEXT    DEFAULT '',  -- comma-separated
    is_archived     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS category_registry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    description     TEXT    DEFAULT '',
    sort_order      INTEGER NOT NULL DEFAULT 0
);

-- Seed default categories
INSERT OR IGNORE INTO category_registry (name, description, sort_order) VALUES
    ('panel',     'Full panel compositions — sidebars, content areas',  1),
    ('dialog',    'Modal and popup dialog layouts',                     2),
    ('toolbar',   'TopBar, StatusBar, action bar assemblies',           3),
    ('card',      'Self-contained data display cards',                  4),
    ('composite', 'Reusable multi-element building blocks',             5),
    ('fragment',  'Individual element configurations for reuse',        6);

CREATE TABLE IF NOT EXISTS export_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id    INTEGER NOT NULL REFERENCES components(id),
    format          TEXT    NOT NULL,  -- 'clipboard' | 'file'
    export_path     TEXT    DEFAULT NULL,
    exported_at     TEXT    NOT NULL   -- ISO 8601
);
```

---

## 4. Module Breakdown

╭────────────────────┬─────────────┬──────────────────────────┬──────────────────────┬──────────────────────┬──────────────────╮
│ Module             │ Stage       │ Responsibility           │ Inputs               │ Outputs              │ Dependencies     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ app.py             │ —           │ QApplication init,       │ sys.argv             │ Running window       │ all modules      │
│                    │             │ main window assembly,    │                      │                      │                  │
│                    │             │ undo/redo stack          │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ canvas.py          │ Compositio  │ QGraphicsScene + View;   │ Element drops,       │ Design tree (nested  │ elements/base    │
│                    │             │ manages element          │ mouse events,        │ element hierarchy);  │                  │
│                    │             │ placement, selection,    │ keyboard shortcuts   │ selection signals     │                  │
│                    │             │ nesting, drag, resize    │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ palette.py         │ Selectio    │ Categorized element      │ Element registry     │ Drag-start events;   │ elements/*,      │
│                    │             │ browser; drag source     │ from elements/       │ element factory       │ constants        │
│                    │             │                          │                      │ calls                │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ inspector.py       │ Inspectio   │ Property editor for      │ Selected element     │ Property change      │ elements/base,   │
│                    │             │ selected element:        │ reference            │ signals; triggers    │ theme_loader     │
│                    │             │ colors (from theme),     │                      │ canvas + preview     │                  │
│                    │             │ size, label, spacing,    │                      │ refresh              │                  │
│                    │             │ alignment, layout role   │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ preview.py         │ Specularium │ Renders the current      │ Design tree +        │ Live QWidget         │ theme_loader,    │
│                    │             │ canvas composition as    │ active theme         │ hierarchy in a       │ elements/*       │
│                    │             │ real PyQt6 widgets in    │                      │ preview container    │                  │
│                    │             │ a sandboxed panel        │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ library.py         │ Armarium    │ SQLite CRUD for          │ DesignDocument,      │ Query results;       │ sqlite3,         │
│                    │             │ component library;       │ search/filter        │ loaded designs;      │ schema           │
│                    │             │ save, load, fork,        │ criteria             │ thumbnail blobs      │                  │
│                    │             │ version, archive         │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ codegen.py         │ Promulgatio │ Traverse design tree,    │ DesignDocument +     │ Python source        │ schema,          │
│                    │             │ emit clean Python/PyQt6  │ active theme         │ string; clipboard    │ constants        │
│                    │             │ code with ModusArcanus   │                      │ or file              │                  │
│                    │             │ header and imports       │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ theme_loader.py    │ —           │ Parse theme.json,        │ File path to         │ TokenSet dict;       │ json, pathlib    │
│                    │             │ validate against         │ theme.json           │ QSS string for       │                  │
│                    │             │ ThemePackage schema,      │                      │ preview + canvas     │                  │
│                    │             │ generate QSS, apply      │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ schema.py          │ —           │ TypedDict definitions    │ —                    │ DesignDocument,      │ —                │
│                    │             │ for design serialization │                      │ ElementNode,         │                  │
│                    │             │ format                   │                      │ PropertySet          │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ constants.py       │ —           │ ModusArcanus defaults,   │ —                    │ Default tokens,      │ —                │
│                    │             │ element registry,        │                      │ category list,       │                  │
│                    │             │ palette categories       │                      │ element catalog      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ elements/base.py   │ —           │ CanvasElement ABC;       │ —                    │ Base class with      │ —                │
│                    │             │ serialization, property  │                      │ serialize/deserialize │                 │
│                    │             │ interface, bounding box  │                      │ property protocol    │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ workers.py         │ —           │ QRunnable + signals      │ Callable tasks       │ Signals: finished,   │ PyQt6            │
│                    │             │ for background IO        │                      │ error, result        │                  │
╰────────────────────┴─────────────┴──────────────────────────┴──────────────────────┴──────────────────────┴──────────────────╯

---

## 5. UI Wireframe

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  ☰  ✦  AGENTIA ARCHITECTURALIS  ✦         In Linea, In Parallelo    [Thema ▼]  [?]    ║
╠═══════════════╦══════════════════════════════════════════╦════════════════════════════════╣
║  ELEMENTARIUM ║  TABULA DESIGNANDI                      ║  INSPECTORIUM                  ║
║               ║                                         ║                                ║
║  ▸ Receptacula║  ┌─────────────────────────────────────┐ ║  ELEMENTUM: QFrame             ║
║    QFrame     ║  │                                     │ ║  ┌──────────────────────────┐  ║
║    QGroupBox  ║  │  ┌───────────────────────────────┐  │ ║  │ NOMEN                    │  ║
║    QSplitter  ║  │  │  ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓  │  │ ║  │ control_panel         │  ║
║    QTabWidget ║  │  │  ┃  TopBar (composite)     ┃  │  │ ║  │                          │  ║
║               ║  │  │  ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛  │  │ ║  │ AMPLITUDO                │  ║
║  ▸ Ingressus  ║  │  │                               │  │ ║  │ W: [280]  H: [auto]      │  ║
║    QLineEdit  ║  │  │  ┌──────────┐  ┌───────────┐  │  │ ║  │                          │  ║
║    QComboBox  ║  │  │  │ QLabel   │  │ QTextEdit │  │  │ ║  │ COLORES                  │  ║
║    QSlider    ║  │  │  │ (gold)   │  │ (parch.)  │  │  │ ║  │ BG: [C_PANEL    ▼]       │  ║
║    QSpinBox   ║  │  │  └──────────┘  └───────────┘  │  │ ║  │ Border: [C_GOLD_DARK ▼]  │  ║
║               ║  │  │                               │  │ ║  │                          │  ║
║  ▸ Ostensio   ║  │  │  ┌───────────────────────────┐│  │ ║  │ DISPOSITIO               │  ║
║    QLabel     ║  │  │  │ ⚗ Manifest  🜲 Seal      ││  │ ║  │ Layout: [Vertical  ▼]    │  ║
║    QProgress  ║  │  │  └───────────────────────────┘│  │ ║  │ Spacing: [16]  Pad: [8]  │  ║
║               ║  │  │                               │  │ ║  │ Alignment: [Left ▼]      │  ║
║  ▸ Actiones   ║  │  │  ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓  │  │ ║  │                          │  ║
║    Button     ║  │  │  ┃  StatusBar (composite)  ┃  │  │ ║  │ MARGINES                 │  ║
║    ToggleBtn  ║  │  │  ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛  │  │ ║  │ T:[0] R:[0] B:[0] L:[0]  │  ║
║               ║  │  └───────────────────────────────┘  │ ║  └──────────────────────────┘  ║
║  ▸ Tabulae    ║  │                                     │ ║                                ║
║    QTableView ║  │           ··· grid dots ···          │ ║  ─────────────────────────────  ║
║               ║  │                                     │ ║                                ║
║  ▸ Ornamentum ║  └─────────────────────────────────────┘ ║  SPECULARIUM VIVUM             ║
║    Separator  ║                                         ║  ┌──────────────────────────┐  ║
║    Spacer     ║  Zoom: [100%]  Grid: [ON]  Snap: [ON]  ║  │ ┏━━━━━━━━━━━━━━━━━━━━━┓ │  ║
║    RuleLine   ║                                         ║  │ ┃ ✦ TopBar ✦         ┃ │  ║
║               ║                                         ║  │ ┗━━━━━━━━━━━━━━━━━━━━━┛ │  ║
║  ▸ Composita  ║                                         ║  │ Section Header          │  ║
║    TopBar     ║                                         ║  │ Body text...            │  ║
║    StatusBar  ║                                         ║  │ [⚗ Manifest] [🜲 Seal] │  ║
║    ControlPnl ║                                         ║  │ ┏━━━━━━━━━━━━━━━━━━━━━┓ │  ║
║    SectHeader ║                                         ║  │ ┃ Status...           ┃ │  ║
║               ║                                         ║  │ ┗━━━━━━━━━━━━━━━━━━━━━┛ │  ║
║               ║                                         ║  └──────────────────────────┘  ║
╠═══════════════╩══════════════════════════════════════════╩════════════════════════════════╣
║  ARMARIUM COMPONENTIUM                                                              [▲] ║
║  ╭──────┬────────────────────┬─────────────┬──────────┬────────┬──────────────────────╮  ║
║  │  #   │ Name               │ Category    │ Version  │ Theme  │ Actions              │  ║
║  ├┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤  ║
║  │  1   │ Tower MainPanel    │ panel       │ v3       │ Aureus │ [Load] [Fork] [Exp]  │  ║
║  │  2   │ Entity Card        │ card        │ v1       │ —      │ [Load] [Fork] [Exp]  │  ║
║  ╰──────┴────────────────────┴─────────────┴──────────┴────────┴──────────────────────╯  ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║  ⚙ The Agency awaits alignment.                          Compositio · Unsaved · 6 elms  ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
```

### Wireframe Legend

╭────────────────────────┬─────────────────────────────────────────────────╮
│ Element                │ Description                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ TopBar                 │ QFrame, 52px. Hamburger toggle, app title,      │
│                        │ theme selector dropdown, help button.           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ ELEMENTARIUM (left)    │ Categorized palette. Collapsible groups:        │
│                        │ Receptacula (containers), Ingressus (inputs),   │
│                        │ Ostensio (displays), Actiones (buttons),        │
│                        │ Tabulae (tables), Ornamentum (decorative),      │
│                        │ Composita (pre-built ModusArcanus patterns).    │
│                        │ Elements are drag sources. Single-click shows   │
│                        │ element info tooltip; drag onto canvas to       │
│                        │ place.                                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ TABULA DESIGNANDI      │ QGraphicsScene + QGraphicsView. The design      │
│ (centre)               │ canvas. Elements rendered as bounding boxes     │
│                        │ with type labels and resize handles. Dotted     │
│                        │ grid background (toggleable). Snap-to-grid      │
│                        │ (toggleable). Container elements accept child   │
│                        │ drops — nesting shown by indented outlines.     │
│                        │ Selected element shows blue highlight +         │
│                        │ resize handles. Multi-select via Ctrl+click     │
│                        │ or rubber-band selection. Zoom via Ctrl+scroll. │
│                        │ Bottom toolbar: zoom %, grid toggle, snap       │
│                        │ toggle.                                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ INSPECTORIUM (right    │ Property editor for the selected canvas         │
│ upper)                 │ element. Sections: NOMEN (widget variable       │
│                        │ name), AMPLITUDO (width/height — fixed or       │
│                        │ auto), COLORES (BG/border/text as token         │
│                        │ dropdowns referencing the active theme —        │
│                        │ C_PANEL, C_BG, etc.), DISPOSITIO (layout        │
│                        │ type, spacing, padding, alignment),             │
│                        │ MARGINES (top/right/bottom/left). All           │
│                        │ changes apply immediately to canvas +           │
│                        │ preview. Inspector is context-sensitive —       │
│                        │ shows only properties relevant to the           │
│                        │ selected element type.                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ SPECULARIUM VIVUM      │ Live preview panel (right lower). Renders       │
│ (right lower)          │ the current canvas composition as actual        │
│                        │ PyQt6 widgets, skinned by the active theme.     │
│                        │ Updates on every canvas change (debounced       │
│                        │ 200ms). The preview is non-interactive —        │
│                        │ the Wizard does not click widgets here,         │
│                        │ only observes the rendered result. Toggle       │
│                        │ via Ctrl+P.                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ ARMARIUM COMPONENTIUM  │ Collapsible bottom drawer (Ctrl+L). Shows       │
│ (bottom)               │ saved components from the SQLite library.       │
│                        │ Columns: id, name, category, version,           │
│                        │ theme designator, action buttons (Load to       │
│                        │ canvas, Fork as new entry, Export code).        │
│                        │ Filterable by category. Collapsed by default.   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ StatusBar              │ QFrame, 28px. Left: declarative status          │
│                        │ message. Right: current stage + save state      │
│                        │ + element count on canvas.                      │
╰────────────────────────┴─────────────────────────────────────────────────╯

---

## 6. Data Flow

### Path (a) — Happy path: select → place → configure → preview → save → export

```
1.  Wizard drags QFrame from Receptacula palette section
2.  palette.py emits element_drag_start with element type identifier
3.  Wizard drops on canvas
4.  canvas.py creates a CanvasElement at drop position:
    a. Instantiates QGraphicsRectItem with default size (280x200)
    b. Labels it with type ("QFrame") and auto-generated variable
       name ("frame_1")
    c. Sets default properties from constants.py:
       bg=C_PANEL, border=C_GOLD_DARK, layout=Vertical
    d. Registers in the design tree as a root element
5.  Wizard drags QLabel into the QFrame on canvas
6.  canvas.py detects drop target is a container:
    a. Creates child CanvasElement inside the parent's bounds
    b. Adds to parent's children list in the design tree
    c. Re-layouts children within parent according to parent's
       layout type (Vertical → stack top-to-bottom)
7.  Wizard clicks the QLabel on canvas
8.  canvas.py emits element_selected with element reference
9.  inspector.py populates property fields for QLabel:
    a. NOMEN: "label_1" (editable)
    b. COLORES: text color dropdown showing token names
       (C_GOLD, C_GOLD_DIM, C_TEXT, C_WHITE — filtered to
       meaningful choices for this element type)
    c. Font size, bold toggle, micro-label toggle
    d. Text content field
10. Wizard changes text color from C_TEXT to C_GOLD
11. inspector.py emits property_changed signal
12. canvas.py updates the element's visual representation
13. preview.py receives design_changed signal (debounced 200ms):
    a. Walks the design tree
    b. For each ElementNode, instantiates the real PyQt6 widget
       with the configured properties
    c. Applies active theme QSS
    d. Renders into the Specularium container
14. Wizard presses Ctrl+S
15. library.py serializes the design tree to DesignDocument JSON
16. Save dialog: name, category dropdown, description, tags
17. library.py writes to component_library.db via worker thread
18. Thumbnail captured: preview.py grabs the preview panel as a
    256x256 PNG, stored as BLOB in the components table
19. Status: "🜲  Component sealed: Tower MainPanel v1"
20. Wizard presses Ctrl+E
21. codegen.py traverses the design tree:
    a. Generates imports (from PyQt6.QtWidgets import ...)
    b. Generates class definition with ModusArcanus file header
    c. For each element: instantiation, property setting,
       layout insertion — all using token references not
       hardcoded hex values
    d. Output references theme tokens by constant name
       (e.g. C_GOLD, not "#d4af37")
22. Code string copied to clipboard
23. Status: "✦  Code exported to clipboard: Tower MainPanel"
```

### Path (b) — Fork and alter: load existing → modify → save as new version

```
1.  Wizard presses Ctrl+L to open Armarium
2.  Wizard clicks [Load] on "Tower MainPanel v1"
3.  library.py reads design_json from components table
4.  canvas.py deserializes DesignDocument:
    a. Clears current canvas
    b. Reconstructs element hierarchy from ElementNode tree
    c. Positions and sizes elements per saved geometry
5.  preview.py renders the loaded design
6.  Wizard modifies — adds a new button, changes spacing
7.  Wizard presses Ctrl+S
8.  library.py detects this is a loaded design (has component id):
    a. Increments version number
    b. Updates existing row in components table
    c. Updates updated_at timestamp
9.  Status: "🜲  Component updated: Tower MainPanel v2"
    —OR—
    Wizard presses Ctrl+Shift+S (Save As New):
    a. Save dialog with name pre-filled + " (fork)"
    b. New row inserted with parent_id pointing to original
    c. Version starts at 1
    d. Status: "🜲  Component forked: Tower MainPanel (fork) v1"
```

### Path (c) — Theme load failure: invalid or missing theme.json

```
1.  Wizard presses Ctrl+T to load a theme
2.  File dialog opens, Wizard selects a file
3.  theme_loader.py attempts to parse JSON
4.  Parse fails — malformed JSON or missing required keys
5.  theme_loader.py emits theme_error signal with details:
    "⌬  Theme rejected: missing key 'tokens.c_gold'"
6.  Status bar: "⌬  Theme not loaded. ModusArcanus defaults active."
7.  Canvas and preview continue operating with MODUS_ARCANUS_DEFAULTS
8.  No canvas state is lost — the design is unaffected
9.  Inspector color dropdowns continue showing default token names
```

---

## 7. Code Stubs

### schema.py — Design Serialization Format

```python
"""Design document serialization schema for the Component Library."""

from typing import TypedDict, Optional


class PropertySet(TypedDict, total=False):
    """Configurable properties for a canvas element.

    Not all properties apply to all element types. The inspector
    shows only relevant properties per element type.
    """
    # Identity
    variable_name: str        # Python variable name for codegen
    label_text: str           # Display text (QLabel, QPushButton)

    # Geometry
    width: Optional[int]      # None = auto / fill parent
    height: Optional[int]     # None = auto / fill parent
    min_width: Optional[int]
    min_height: Optional[int]

    # Colors (as token names, not hex — resolved at render time)
    bg_token: str             # e.g. "c_panel"
    text_token: str           # e.g. "c_gold"
    border_token: str         # e.g. "c_gold_dark"
    accent_token: str         # e.g. "c_teal" for confirm buttons

    # Typography
    font_size: int            # px
    font_bold: bool
    font_italic: bool
    micro_label: bool         # uppercase + letter-spacing pattern
    letter_spacing: int       # px

    # Layout (for containers)
    layout_type: str          # "vertical" | "horizontal" | "grid" | "none"
    spacing: int              # px between children
    padding: int              # px internal padding
    alignment: str            # "left" | "center" | "right" | "fill"

    # Margins
    margin_top: int
    margin_right: int
    margin_bottom: int
    margin_left: int

    # Widget-specific
    border_width: int         # px
    border_style: str         # "solid" | "none"
    placeholder_text: str     # QLineEdit placeholder
    read_only: bool           # QTextEdit read-only mode
    button_accent: str        # "gold" | "teal" | "crimson"


class ElementNode(TypedDict):
    """A single element in the design tree."""
    id: str                   # UUID4 string
    element_type: str         # "QFrame" | "QLabel" | "QPushButton" | etc.
    element_category: str     # "container" | "input" | "display" | etc.
    properties: PropertySet
    children: list['ElementNode']  # Nested elements (containers only)
    x: float                  # Canvas X position (relative to parent)
    y: float                  # Canvas Y position (relative to parent)


class DesignDocument(TypedDict):
    """Complete serialized design — stored in component_library.db."""
    schema_version: str       # "1.0"
    canvas_width: int         # Design canvas dimensions
    canvas_height: int
    root_elements: list[ElementNode]  # Top-level elements on canvas
    theme_designator: Optional[str]   # Which theme was active
    metadata: dict            # Freeform metadata (creation context, notes)
```

### elements/base.py — Canvas Element ABC

```python
"""Abstract base class for all canvas elements."""

import uuid
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPen, QBrush, QColor


class CanvasElement(ABC):
    """Base class for all elements placeable on the design canvas.

    Every element knows how to:
    - Render itself as a QGraphicsItem on the canvas
    - Serialize its state to an ElementNode dict
    - Deserialize from an ElementNode dict
    - Report which properties are configurable for its type
    - Generate its corresponding PyQt6 code fragment
    """

    def __init__(self, element_type: str, category: str):
        self.id = str(uuid.uuid4())
        self.element_type = element_type
        self.category = category
        self.properties: dict = self._default_properties()
        self.children: list['CanvasElement'] = []
        self.graphics_item: QGraphicsRectItem | None = None

    @abstractmethod
    def _default_properties(self) -> dict:
        """Return default PropertySet for this element type."""
        ...

    @abstractmethod
    def configurable_properties(self) -> list[str]:
        """Return list of property names the inspector should show."""
        ...

    @abstractmethod
    def create_graphics_item(self, x: float, y: float,
                             w: float, h: float) -> QGraphicsRectItem:
        """Create the QGraphicsItem for canvas rendering."""
        ...

    @abstractmethod
    def create_preview_widget(self, tokens: dict):
        """Create the real PyQt6 widget for live preview."""
        ...

    @abstractmethod
    def generate_code(self, tokens: dict, indent: int = 0) -> str:
        """Generate Python/PyQt6 code fragment for this element."""
        ...

    def serialize(self) -> dict:
        """Serialize to ElementNode dict."""
        return {
            'id': self.id,
            'element_type': self.element_type,
            'element_category': self.category,
            'properties': dict(self.properties),
            'children': [c.serialize() for c in self.children],
            'x': self.graphics_item.pos().x() if self.graphics_item else 0,
            'y': self.graphics_item.pos().y() if self.graphics_item else 0,
        }

    def accepts_children(self) -> bool:
        """Whether this element is a container that accepts drops."""
        return self.category == 'container'
```

### canvas.py — Design Canvas

```python
"""QGraphicsScene-based design canvas with element management."""

from PyQt6.QtWidgets import (QGraphicsScene, QGraphicsView,
                              QGraphicsRectItem)
from PyQt6.QtCore import pyqtSignal, Qt, QPointF
from PyQt6.QtGui import QPen, QColor


class DesignCanvas(QGraphicsView):
    """Main design surface. Manages element placement and selection."""

    element_selected = pyqtSignal(object)   # CanvasElement or None
    design_changed = pyqtSignal()           # Any modification
    element_dropped = pyqtSignal(str, float, float)  # type, x, y

    def __init__(self, parent=None):
        self._scene = QGraphicsScene()
        super().__init__(self._scene, parent)
        self._elements: list = []         # Root CanvasElement list
        self._selected: object = None     # Current selection
        self._grid_visible = True
        self._snap_to_grid = True
        self._grid_size = 16              # px
        self._zoom = 1.0
        self._undo_stack: list = []
        self._redo_stack: list = []

    def add_element(self, element, x: float, y: float,
                    parent=None) -> None:
        """Place an element on the canvas at (x, y).

        If parent is a container element, nest inside it.
        Pushes state to undo stack.
        """
        ...

    def remove_selected(self) -> None:
        """Remove the currently selected element. Undoable."""
        ...

    def duplicate_selected(self) -> None:
        """Clone the selected element with offset. Undoable."""
        ...

    def group_selected(self) -> None:
        """Wrap multi-selected elements in a QFrame container."""
        ...

    def ungroup_selected(self) -> None:
        """Remove container wrapper, promote children to parent."""
        ...

    def serialize_all(self) -> list[dict]:
        """Serialize entire canvas to list of ElementNode dicts."""
        ...

    def deserialize_all(self, nodes: list[dict]) -> None:
        """Clear canvas and rebuild from ElementNode list."""
        ...

    def undo(self) -> None:
        """Restore previous canvas state from undo stack."""
        ...

    def redo(self) -> None:
        """Reapply undone canvas state from redo stack."""
        ...

    def _snap_position(self, pos: QPointF) -> QPointF:
        """Snap position to grid if snap is enabled."""
        ...

    def _draw_grid(self) -> None:
        """Render dotted grid background on the scene."""
        ...
```

### codegen.py — Code Generation Engine

```python
"""Generate clean Python/PyQt6 code from a design tree."""


def generate_code(design: dict, tokens: dict,
                  class_name: str = "GeneratedPanel") -> str:
    """Traverse design tree, emit complete Python module.

    Output includes:
    - ModusArcanus file header (version stamped)
    - PyQt6 imports (only what's needed)
    - Class definition inheriting QFrame
    - __init__ with all widget instantiation
    - Layout setup with proper nesting
    - Color references as token constants (C_GOLD, etc.)
      not hardcoded hex values
    - compose() method assembling the layout tree

    Token values are referenced by constant name. The generated
    code imports from a constants module, not from theme.json
    directly. This means the generated code adapts when a
    different theme is loaded at runtime.
    """
    ...


def _generate_imports(element_types: set[str]) -> str:
    """Produce minimal import block for used element types."""
    ...


def _generate_element(node: dict, indent: int,
                      tokens: dict) -> list[str]:
    """Recursively generate code for one element + children."""
    ...


def _variable_name(element_type: str, index: int) -> str:
    """Generate a valid Python variable name for an element."""
    ...


def _generate_header(class_name: str) -> str:
    """ModusArcanus file header with version number."""
    ...
```

### theme_loader.py — theme.json Consumer

```python
"""Load and validate theme.json from Bureau I."""

import json
from pathlib import Path


# Required keys in theme.json tokens section
REQUIRED_TOKENS = [
    'c_bg', 'c_panel', 'c_gold', 'c_gold_dim', 'c_gold_dark',
    'c_crimson', 'c_teal', 'c_text', 'c_subtle', 'c_white',
]

# ModusArcanus defaults — used when no theme is loaded
DEFAULTS = {
    'c_bg':        '#050507',
    'c_panel':     '#0a0a12',
    'c_gold':      '#d4af37',
    'c_gold_dim':  '#7a6a2a',
    'c_gold_dark': '#3a2e10',
    'c_crimson':   '#8b1a1a',
    'c_teal':      '#1a5a5a',
    'c_text':      '#c8b88a',
    'c_subtle':    '#3a3528',
    'c_white':     '#e8e0cc',
}


def load_theme(path: Path) -> dict:
    """Load and validate a theme.json file.

    Returns the tokens dict if valid.
    Raises ValueError with specific missing-key details if invalid.
    Raises FileNotFoundError if path does not exist.
    Raises json.JSONDecodeError if file is malformed.
    """
    ...


def validate_theme(data: dict) -> list[str]:
    """Check theme.json against ThemePackage schema.

    Returns list of error strings. Empty list = valid.
    """
    ...


def generate_qss(tokens: dict) -> str:
    """Generate complete QSS from token dict.

    Identical logic to Bureau I's auto_render.py — generates
    the same QSS so preview fidelity matches the live Tower.
    """
    ...


def get_active_tokens() -> dict:
    """Return currently loaded tokens, or defaults if none loaded."""
    ...
```

### preview.py — Live Preview Renderer

```python
"""Render design tree as real PyQt6 widgets in a preview panel."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import QTimer


class PreviewRenderer(QScrollArea):
    """Builds and displays real PyQt6 widgets from the design tree.

    Debounced at 200ms to avoid flicker during rapid editing.
    The preview container is non-interactive — widgets are
    displayed but do not respond to user input.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._rebuild)
        self._pending_design = None
        self._active_tokens = None

    def schedule_rebuild(self, design_tree: list[dict],
                         tokens: dict) -> None:
        """Queue a preview rebuild. Debounced at 200ms."""
        self._pending_design = design_tree
        self._active_tokens = tokens
        self._timer.start()

    def _rebuild(self) -> None:
        """Clear preview and reconstruct from design tree."""
        ...

    def _build_widget(self, node: dict,
                      tokens: dict) -> QWidget:
        """Recursively build a QWidget from an ElementNode.

        Maps element_type to real PyQt6 widget class.
        Applies properties from the node's PropertySet.
        Recurses into children for containers.
        """
        ...

    def capture_thumbnail(self, size: int = 256) -> bytes:
        """Grab the preview panel as a PNG byte string.

        Used for component library thumbnails.
        Returns PNG data suitable for BLOB storage.
        """
        ...
```

### library.py — Component Library

```python
"""SQLite CRUD for the Component Library."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone


class ComponentLibrary:
    """Manages saved component designs in SQLite."""

    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def initialize(self) -> None:
        """Create database and tables if they don't exist."""
        ...

    def save(self, name: str, category: str,
             design_json: str, description: str = '',
             tags: str = '', thumbnail: bytes = None,
             theme_designator: str = None,
             component_id: int = None) -> int:
        """Save or update a component. Returns component id.

        If component_id is provided, updates existing entry and
        increments version. Otherwise inserts new row.
        """
        ...

    def fork(self, source_id: int, new_name: str) -> int:
        """Create a new component forked from source. Returns new id.

        Sets parent_id to source_id. Version starts at 1.
        """
        ...

    def load(self, component_id: int) -> dict | None:
        """Load a component by id. Returns full row as dict."""
        ...

    def list_components(self, category: str = None,
                        archived: bool = False) -> list[dict]:
        """List components, optionally filtered by category."""
        ...

    def search(self, query: str) -> list[dict]:
        """Search components by name, description, or tags."""
        ...

    def archive(self, component_id: int) -> None:
        """Soft-delete — mark component as archived."""
        ...

    def log_export(self, component_id: int,
                   fmt: str, path: str = None) -> None:
        """Record an export event."""
        ...

    def close(self) -> None:
        """Close database connection."""
        ...
```

### constants.py — Element Registry & Defaults

```python
"""Element registry, palette categories, and ModusArcanus defaults."""


# Palette categories — ordered as they appear in the Elementarium
PALETTE_CATEGORIES = [
    {
        'id': 'receptacula',
        'label': 'Receptacula',
        'description': 'Containers and structural elements',
        'elements': ['QFrame', 'QGroupBox', 'QSplitter', 'QTabWidget'],
    },
    {
        'id': 'ingressus',
        'label': 'Ingressus',
        'description': 'Input and control elements',
        'elements': ['QLineEdit', 'QComboBox', 'QSlider', 'QSpinBox'],
    },
    {
        'id': 'ostensio',
        'label': 'Ostensio',
        'description': 'Display and label elements',
        'elements': ['QLabel_gold', 'QLabel_dim', 'QLabel_micro',
                     'QProgressBar'],
    },
    {
        'id': 'actiones',
        'label': 'Actiones',
        'description': 'Buttons and action triggers',
        'elements': ['ArcaneButton_gold', 'ArcaneButton_teal',
                     'ArcaneButton_crimson', 'ToggleButton'],
    },
    {
        'id': 'tabulae',
        'label': 'Tabulae',
        'description': 'Tables and data grids',
        'elements': ['QTableView'],
    },
    {
        'id': 'ornamentum',
        'label': 'Ornamentum',
        'description': 'Decorative and structural elements',
        'elements': ['Separator', 'Spacer', 'RuleLine'],
    },
    {
        'id': 'composita',
        'label': 'Composita',
        'description': 'Pre-built ModusArcanus widget patterns',
        'elements': ['TopBar', 'StatusBar', 'ControlPanel',
                     'SectionHeader', 'SwatchStrip'],
    },
]


# Default property values per element category
ELEMENT_DEFAULTS = {
    'container': {
        'bg_token': 'c_panel',
        'border_token': 'c_gold_dark',
        'layout_type': 'vertical',
        'spacing': 16,
        'padding': 8,
        'border_width': 1,
        'border_style': 'solid',
    },
    'input': {
        'bg_token': 'c_bg',
        'text_token': 'c_text',
        'border_token': 'c_subtle',
        'font_size': 11,
        'padding': 6,
    },
    'display': {
        'text_token': 'c_text',
        'font_size': 11,
        'font_bold': False,
    },
    'button': {
        'bg_token': 'c_panel',
        'text_token': 'c_gold',
        'border_token': 'c_gold_dark',
        'font_size': 11,
        'letter_spacing': 1,
        'padding': 6,
    },
}


APP_TITLE = '✦  AGENTIA ARCHITECTURALIS  ✦'
APP_SUBTITLE = 'In Linea, In Parallelo, In Perpetuum'
BUREAU_FULL = 'The Architectural Alignment Enforcement Agency'
BUREAU_LATIN = 'Agentia Architecturalis'
```

---

## 8. Error Handling

╭─────────────────────┬──────────────────────────┬─────────────────────────────────╮
│ Module              │ Error                    │ Strategy                        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ app.py              │ PyQt6 import failure     │ Print to stderr and exit.       │
│                     │                          │ Cannot show GUI without Qt.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ library.py          │ DB cannot be created     │ Attempt to create storage/      │
│                     │ or opened                │ directory. If fails: show       │
│                     │                          │ error dialog with path. App     │
│                     │                          │ continues — Wizard can design   │
│                     │                          │ and export but not save to      │
│                     │                          │ library.                        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ theme_loader.py     │ theme.json malformed     │ Emit theme_error signal with    │
│                     │ or missing keys          │ specific missing key names.     │
│                     │                          │ Fall back to MODUS_ARCANUS      │
│                     │                          │ defaults. No canvas data lost.  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ theme_loader.py     │ theme.json file not      │ FileNotFoundError caught. Show  │
│                     │ found at path            │ status message with full path.  │
│                     │                          │ Defaults remain active.         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ canvas.py           │ Deserialization failure   │ Catch JSONDecodeError and       │
│                     │ — corrupt design_json    │ KeyError. Show error dialog     │
│                     │                          │ naming the corrupt component.   │
│                     │                          │ Canvas remains in current       │
│                     │                          │ state (does not clear).         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ canvas.py           │ Unknown element_type     │ Deserializer encounters an      │
│                     │ in saved design          │ unregistered type. Replaces     │
│                     │                          │ with a placeholder QFrame       │
│                     │                          │ labeled "⌬ Unknown: {type}".   │
│                     │                          │ Design loads with warnings.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ preview.py          │ Widget instantiation     │ Catch all exceptions during     │
│                     │ fails during rebuild     │ preview build. Show partial     │
│                     │                          │ preview up to the failing       │
│                     │                          │ element. Status: "⌬  Preview   │
│                     │                          │ incomplete: {element_type}."    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ codegen.py          │ Generated code has       │ codegen runs ast.parse() on     │
│                     │ syntax errors            │ its own output as a sanity      │
│                     │                          │ check. If parse fails: show     │
│                     │                          │ error with line number. Code    │
│                     │                          │ not copied to clipboard.        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ codegen.py          │ Clipboard write failure  │ Fall back to writing to         │
│                     │ (no xclip on non-X11)    │ exports/ directory as .py       │
│                     │                          │ file. Status: "⌬  Clipboard    │
│                     │                          │ unavailable — written to file." │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ library.py          │ Thumbnail capture fails  │ Save proceeds without           │
│                     │                          │ thumbnail. thumbnail_png set    │
│                     │                          │ to NULL. Library displays       │
│                     │                          │ placeholder icon.              │
╰─────────────────────┴──────────────────────────┴─────────────────────────────────╯

---

## 9. Setup & Testing

### requirements.txt

```
PyQt6>=6.6.0
```

Single dependency. No colour-science needed — colors come from
theme.json or defaults.

### Install & Run

```bash
cd ~/ArcaCognitorium/Exocognii/AestheticAuthoritarianAssociativeAlliance/AgentiaArchitecturalis

# Create venv (first time)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python -m AgentiaArchitecturalis
# or:
python __main__.py
```

### Unit Tests

**test_canvas.py** — Create a DesignCanvas. Add a container element
at (0, 0). Add a child element inside it. Assert child is in
parent's children list. Serialize canvas. Assert output has one root
element with one child. Deserialize into a fresh canvas. Assert
structure matches.

**test_codegen.py** — Build a DesignDocument with a QFrame containing
a QLabel and a QPushButton. Call generate_code(). Assert output
contains "from PyQt6.QtWidgets import QFrame, QLabel, QPushButton".
Assert output contains the ModusArcanus file header. Run
ast.parse() on the output — assert no SyntaxError.

**test_library.py** — Create in-memory SQLite library. Save a
component. Read it back. Assert all fields match. Fork it. Assert
parent_id points to original. Assert version is 1. Archive the
original. List non-archived — assert only the fork appears.

**test_theme_loader.py** — Load a valid theme.json fixture. Assert
all 10 token keys present. Load a fixture with a missing key.
Assert ValueError raised with the key name in the message. Call
get_active_tokens() with no theme loaded — assert returns
MODUS_ARCANUS_DEFAULTS.

**test_elements.py** — Instantiate each element type from
elements/. Assert _default_properties() returns a dict. Assert
configurable_properties() returns a non-empty list. Assert
serialize() produces a dict with 'id', 'element_type',
'properties', 'children' keys.

### Integration Test

**test_integration.py** — End-to-end:

```
1.  Create DesignCanvas
2.  Add QFrame container at (0, 0)
3.  Add QLabel child with text_token="c_gold", label_text="Titulus"
4.  Add ArcaneButton child with accent="teal", label_text="⚗ Manifest"
5.  Serialize canvas → DesignDocument
6.  Save to in-memory ComponentLibrary with name "Test Panel"
7.  Load back from library → assert design_json parses
8.  Deserialize onto fresh canvas → assert 1 root, 2 children
9.  Generate code → assert ast.parse() passes
10. Assert code contains "QFrame", "QLabel", "QPushButton"
11. Assert code references "C_GOLD" not "#d4af37"
12. Fork component → assert new id, parent_id = original
```

---

## 10. Packaging

### Desktop File

```ini
[Desktop Entry]
Name=Agentia Architecturalis
Comment=The Architectural Alignment Enforcement Agency — visual UI component designer
Exec=bash -c "cd $HOME/ArcaCognitorium && python -m Exocognii.AestheticAuthoritarianAssociativeAlliance.AgentiaArchitecturalis"
Icon=agentia-architecturalis
Terminal=false
Type=Application
Categories=Development;
Keywords=ui;design;widget;layout;arcane;
StartupWMClass=agentia-architecturalis
```

Place at: `~/.local/share/applications/AgentiaArchitecturalis.desktop`

Icon at: `~/.local/share/icons/agentia-architecturalis.png`

Launch script at:
`~/ArcaCognitorium/launch_agentia_architecturalis.sh`

```bash
#!/bin/bash
cd ~/ArcaCognitorium/Exocognii/AestheticAuthoritarianAssociativeAlliance/AgentiaArchitecturalis
source .venv/bin/activate
python -m AgentiaArchitecturalis
```

### PyInstaller Command

```bash
pyinstaller \
    --name "AgentiaArchitecturalis" \
    --onefile \
    --windowed \
    --add-data "storage:storage" \
    __main__.py
```

### Runtime Path Resolution

```python
from pathlib import Path

def get_app_root() -> Path:
    """Resolve application root for both dev and packaged modes."""
    return Path(__file__).resolve().parent

def get_storage_path() -> Path:
    """Resolve storage directory, creating if needed."""
    storage = get_app_root() / 'storage'
    storage.mkdir(exist_ok=True)
    return storage

def get_exports_path() -> Path:
    """Resolve exports directory, creating if needed."""
    exports = get_app_root() / 'exports'
    exports.mkdir(exist_ok=True)
    return exports
```

---

## 11. Extensibility

╭───────────────────────────┬──────────────────────────────┬──────────────────────────────────╮
│ Feature                   │ User Value                   │ Implementation Approach           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Textual Output            │ Generate Textual/TUI code    │ Second codegen backend. Same     │
│                           │ alongside PyQt6              │ DesignDocument, different         │
│                           │                              │ emitter. Maps element types to   │
│                           │                              │ Textual widget classes. Emits    │
│                           │                              │ Textual CSS alongside Python.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Theme Live Sync           │ When Bureau I ratifies a new │ ZMQ SUB socket listening for     │
│                           │ theme, Bureau II reloads     │ theme broadcasts from Bureau I.  │
│                           │ automatically                │ On receive: reload tokens,       │
│                           │                              │ regenerate QSS, re-render        │
│                           │                              │ preview.                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Custom Element Plugin     │ Wizard defines new element   │ Plugin discovery: elements/      │
│                           │ types beyond the built-in    │ directory scanned for classes     │
│                           │ palette                      │ inheriting CanvasElement.         │
│                           │                              │ Auto-registered in palette.       │
│                           │                              │ Codegen maps via element_type     │
│                           │                              │ registry.                        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Component Marketplace     │ Import/export component      │ Components serialized as self-   │
│                           │ designs between Tower        │ contained .aac (JSON + thumbnail │
│                           │ instances                    │ archive) files. Import adds to   │
│                           │                              │ library with provenance marker.  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Layout Constraint Solver  │ Automatic layout suggestions │ Constraint engine analyzes        │
│                           │ based on element types and   │ element types, generates layout  │
│                           │ spatial arrangement          │ recommendations (spacing,        │
│                           │                              │ alignment). Wizard accepts or    │
│                           │                              │ rejects. Not auto-applied.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Arx Aedificare Bridge     │ Push exported code directly  │ IPC (Unix domain socket or       │
│                           │ to The Builder's code pane   │ shared clipboard with signal).   │
│                           │ in Arx Aedificare            │ Bureau II emits; Arx Aedificare  │
│                           │                              │ receives into active code pane.  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Animation Presets         │ Pre-configured property      │ Animation presets stored as       │
│                           │ animations (slide, fade,     │ named configs in constants.py.   │
│                           │ expand) for containers       │ Inspector exposes an "Animatio"  │
│                           │                              │ dropdown for container elements. │
│                           │                              │ Codegen emits QPropertyAnimation │
│                           │                              │ setup code.                      │
╰───────────────────────────┴──────────────────────────────┴──────────────────────────────────╯

---

## Appendix: Suite Manifest Entry

```json
{
    "id": "agentia_architecturalis",
    "name": "Agentia Architecturalis",
    "bureau": "Agentia Architecturalis",
    "alliance": "A4",
    "path": "Exocognii/AestheticAuthoritarianAssociativeAlliance/AgentiaArchitecturalis",
    "entry": "__main__.py",
    "version": "1.0.0",
    "status": "development",
    "dependencies": ["auctoritas_spectralis"]
}
```

---

*⟁*

*Ordo Discordia, Cosmos Inania*

*IdeaForge · Bureau II · Agentia Architecturalis · ＭＭＸＸＶＩ*
