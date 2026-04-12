# AGENTIA ARCHITECTURALIS
## Expositio — Application Design Document
### Bureau II · Triumviratus Aestheticus Imperialis
#### v1.2 · Post-Convocatio · Sigillum Approbationis · MMXXVI

---

*Verificatio Canonica*

The submitting bureau confirms that all identity content, nomenclature, mottos,
and canonical references contained in this document have been verified against
ratified sources prior to submission. No content has been invented where
canonical content exists.

Bureau: Agentia Architecturalis — Bureau II
Version: v1.2
Date: MMXXVI · Post-Convocatio

---

*In Linea · In Parallelo · In Perpetuum*

*Ordo Discordia, Cosmos Inania*

---

# I. IDENTITY

## Name & Classification

**Canonical Title:** AGENTIA ARCHITECTURALIS
**English Name:** Architectural Alignment Enforcement Agency
**Bureau:** II of III — Triumviratus Aestheticus Imperialis
**Suite:** Exocognii — Arca Cognitorium
**Classification:** PyQt6 desktop design tool — visual component composer and
code generation instrument
**Version:** v1.2 (build-ready — Sigillum Approbationis received 2026-04-08)
**Path:** `Exocognii/A4/AgentiaArchitecturalis/`
**Venv:** `venv-ARCHITECTURALIS`
**Launch:** `python3 -m AgentiaArchitecturalis` from parent directory

## Thesis

The Agentia does not build software. It legislates its appearance — then generates
the code that makes that legislation executable.

## Status

Active development. Core canvas mechanics operational. A4 Common Shell reformation
(Titulum / Feature Codex / Fascia / Scriptorium Canvas) approved by Convocatio
Iudicii under Sigillum sub Conditione. Build order: Bureau I first, Bureau II
second. Build proceeds on ratification of v1.2 package.

---

# II. PURPOSE

## Problem Statement

Building PyQt6 applications within the Exocognii suite requires composing
complex widget hierarchies with consistent ModusArcanus theming. Doing this by
hand — writing layout code from scratch for each new application — is slow,
error-prone, and visually incoherent across tools. There is no shared spatial
understanding of how components fit together before code is written.

The problem is not that code is difficult to write. The problem is that
*arrangement is invisible* until runtime. The Wizard cannot reason spatially
about widget composition without placing widgets spatially.

## Motivation

The Exocognii suite is built by one person across many sessions. Each new
application requires a UI. Each UI requires ModusArcanus styling. Without a
shared instrument for composing and generating these UIs, each application
develops independently and inconsistently. The Agentia is the instrument that
enforces coherence before a line of application code is written.

## Intended Outcome

The Wizard opens the Agentia, arranges PyQt6 widgets spatially on a canvas,
nests containers with children, inspects and adjusts properties, verifies the
rendered result in the Specularium, and exports valid, styled, deployment-ready
Python code. That code is then placed directly into an Exocognii application.
The application looks correct from the first run.

## Anti-Purpose

The Agentia does not:

- Wire signals and slots. Generated code is structural only — static compositions.
- Run, test, or deploy applications.
- Manage application logic, state, or data models.
- Replace Bureau I (Auctoritas Spectralis) as the authority on colour. It consumes
  theme.json. It never writes it.
- Serve as a general-purpose Python IDE or code editor.
- Generate code for frameworks other than PyQt6.

---

# III. AUDIENCE

## Primary User

One: the Wizard, LordFingers. A single-developer builder of the Arca Cognitorium
and the Exocognii suite. Operating on Debian Trixie / KDE Plasma 6 / X11 on a
machine called CastrumDigitos. Deeply familiar with PyQt6, the ModusArcanus
design system, and the full Cogniverse naming register. Fluent in the Latin
naming layer. Builds late at night across multiple parallel projects.

The Wizard does not need onboarding. The Wizard needs an instrument that behaves
with authority and does not break.

## Secondary Users

None at present. Future: other Wizards operating their own Tower instances may
receive the suite. At that point the Agentia becomes a shared instrument. The
current architecture does not preclude multi-user use but does not design for it.

## Assumed Knowledge

The Agentia assumes its user knows:

- PyQt6 widget types, layouts, and naming conventions
- The ModusArcanus colour token system (C_GOLD, C_PANEL, etc.)
- The Cogniverse nomenclature register — Latin names are used without explanation
- The A4 Common Shell spatial grammar (Titulum, Feature Codex, Fascia,
  Scriptorium Canvas)
- Python 3.11 syntax in generated output

## Out-of-Scope Audiences

Anyone who does not know PyQt6 will not understand the generated code. Anyone
unfamiliar with ModusArcanus will not understand why hex literals are absent from
the output. This is not a consumer design tool. It is a bureau instrument.

---

# IV. DESIGN PHILOSOPHY

## Core Principles

**Structure before beauty.** The canvas is a spatial argument. Elements placed
here are not assembled by the machine — they are arranged by the Wizard. The
tool reveals the possible arrangement; the judgment is human. The Agentia never
auto-arranges, never suggests layouts, never rearranges without instruction.

**Containment is law.** A child element that visually exceeds its parent's bounds
is not a design choice — it is a rendering failure. The nesting standard is
non-negotiable. The canvas must accurately portray containment at all times.

**The output is the product.** Everything else — canvas, inspector, library,
preview — is the apparatus that produces it. The Codex Exportum is the point
where the bureau fulfils its mandate. If the code is wrong, the bureau has failed.
If the code is right, the bureau has served.

**One feature at a time.** The A4 Common Shell mandates that one feature occupies
the full Scriptorium Canvas. Features do not share space. They do not compete for
attention. The Wizard navigates deliberately, not frantically.

**The Specularium shows truth; the canvas shows structure.** The canvas is not
a pixel-perfect mockup. It is a spatial layout instrument. Elements have
proportionally honest default sizes — a QLabel is thin, a QFrame is large — but
no claim is made that the canvas looks like the deployed application. The
Specularium is where rendered truth lives.

## Tradeoff Positions

**Spatial honesty over pixel accuracy.** Element sizes on the canvas are
proportionally honest (a button is smaller than a container) but are not
px-perfect runtime renders. The Specularium handles accuracy. The canvas handles
structure.

**Explicit navigation over ambient context.** The Wizard explicitly chooses a
feature via the Feature Codex. There is no ambient state, no hidden pane, no
drawer that sneaks into view. What is on screen is what was chosen.

**Generated code correctness over generated code elegance.** The codegen pipeline
validates via `ast.parse()` before offering output. A valid-but-verbose output
is preferable to an elegant-but-broken one.

**Bureau I sovereignty over local convenience.** Bureau II never modifies
theme.json. It never guesses at colour values. It reads what Bureau I wrote.
If Bureau I has not written a theme, ModusArcanus defaults apply. The
dependency is constitutional.

## Aesthetic Direction

ModusArcanus throughout. Dark void (C_BG `#050507`) as primary surface. Gold
(C_GOLD `#d4af37`) as the only bright colour — reserved for authority,
interactivity, and active state. Georgia serif for all UI labels. Courier Prime
monospace for code, properties, and status information. The interface should feel
like a bureau: purposeful, slightly formal, not warm.

## What This Philosophy Rejects

Drag-to-auto-snap, auto-arrange, and AI-assisted layout suggestion — the Wizard
arranges. The tool executes.

Animated feature transitions — the Convocatio ratified instant stack swaps.
220ms slide animations are not for navigation.

Pixel-perfect canvas rendering — the Specularium handles that. The canvas is
for composition, not presentation.

Hex literals in generated code — token constants only. C_GOLD, not `#d4af37`.
This is non-negotiable.

---

# V. TECHNICAL CONCEPT

## Mental Model

The Agentia is a spatial composition instrument connected to a code emission
pipeline. The Wizard places widget specifications (CanvasElements) onto a
QGraphicsScene. Each CanvasElement is a data record — it knows its type,
its properties, and its children. It does not know about layout engines or
signal connections. When the Wizard is satisfied with the composition, the
codegen pipeline walks the element tree and emits Python.

Think of the canvas as a blueprint and the Specularium as the built room.
The blueprint is structural. The room is real. The Codex Exportum is the
translation from one to the other.

## Core Abstractions

╭───────────────────────┬──────────────────────────────────────────────────────╮
│  Abstraction          │  Definition                                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  CanvasElement        │  Abstract base for all placeable items. Holds type,  │
│                       │  category, properties dict, children list, and a     │
│                       │  reference to its QGraphicsRectItem.                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  DesignCanvas         │  QGraphicsView managing the scene, all element       │
│                       │  placement, nesting detection, undo/redo stack,      │
│                       │  token refresh, and serialization.                   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ElementNode          │  Serialized dict form of a CanvasElement. The        │
│                       │  portable representation used for saves, loads,      │
│                       │  undo state, and codegen input.                      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Canvas Session       │  A named, persisted canvas state. Stored as JSON in  │
│                       │  `storage/canvases/{name}.json`. Separate from the   │
│                       │  Component Library. Draft-quality saves.             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Component            │  A sealed, versioned canvas composition in the       │
│                       │  Armarium. SQLite-backed. Production-quality.        │
│                       │  Carries thumbnail, theme designator, export log.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  PreviewDataModel     │  Shared data holder for the Specularium. Owns the    │
│                       │  current design tree and active tokens. Both         │
│                       │  Specularium instances subscribe to it. Neither      │
│                       │  owns it. The canvas writes it.                      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Token                │  A named colour constant (C_GOLD, C_PANEL, etc.)     │
│                       │  resolved from the active theme.json. Used           │
│                       │  throughout properties, rendering, and generated     │
│                       │  code. Never a raw hex value at the application      │
│                       │  level.                                              │
╰───────────────────────┴──────────────────────────────────────────────────────╯

## Data Flow

```
Bureau I (Auctoritas Spectralis)
  └── writes theme.json
        │
        ▼
Agentia Architecturalis — Thema feature
  └── loads theme.json → active token dict
        │
        ├── QSS applied to entire application
        │
        └── canvas.refresh_tokens() → repaints all existing graphics items
              │
              ▼
        DesignCanvas (QGraphicsScene)
          ├── Elementarium: drag element → dropEvent → add_element()
          │     └── _container_at(scene_pos) → nest or top-level
          │     └── create_graphics_item(x, y, w, h, tokens)
          │     └── setParentItem() if nested
          │
          ├── Inspector: property_changed → update_element_size() or repaint
          │
          ├── serialize_all() → list[ElementNode]
          │     │
          │     ├── → PreviewDataModel → SpeculariumFeaturePage
          │     │                      → SpeculariumWindow (floating)
          │     │
          │     ├── → CanvasSessionManager.save() → storage/canvases/*.json
          │     │
          │     └── → generate_code() → ast.parse() → clipboard / file
          │
          └── undo_stack: list[list[ElementNode]] (max 50)

Armarium (ComponentLibrary)
  └── SQLite: name / category / design_json / thumbnail / theme_designator
        ├── Seal: serialize_all() + thumbnail from SpeculariumWindow
        ├── Load: deserialize_all() → canvas restored
        ├── Fork: copy record, increment version
        └── Export: generate_code() → clipboard
```

## System Boundaries

The Agentia owns its canvas state, its component library, its canvas sessions,
and its code generation pipeline. It does not own colour. It reads token values
from Bureau I's output and falls back to ModusArcanus defaults when no external
theme is present.

It does not write to Involucrum, Exvacua Loricum, or Perpetuum Aedificare. It
is a design-time tool. Its outputs (generated Python code, sealed components)
are used by the Wizard when building other tools — never by other tools at
runtime.

## Key Technical Decisions

**QGraphicsScene over a layout-based canvas.** QGraphicsScene provides true
spatial placement with arbitrary positioning and nesting via `setParentItem()`.
A layout-based approach would impose flow constraints that conflict with the
tool's purpose.

**Serialization as the undo mechanism.** The undo stack holds lists of
serialized ElementNode dicts, not command objects. This means undo can restore
any canvas state without implementing inverse operations for every action type.
Cost: memory (50 states × canvas complexity). Acceptable for the use case.

**Token constants in generated code, never hex.** The generated output must be
portable across theme changes. A component sealed with C_GOLD remains correctly
themed if the Wizard applies a new theme.json from Bureau I. Raw hex would break
on theme change.

**Two independent Specularium instances sharing a data model.** The floating
window pattern requires two separate PreviewRenderer widgets. Re-parenting a
single widget between QMainWindow and QStackedWidget causes destruction of the
widget's native handle on X11. Two instances with one PreviewDataModel is the
correct architecture.

**AST validation before export.** The codegen pipeline may produce syntactically
invalid Python under edge cases (malformed variable names, nesting depth
overflows). `ast.parse()` catches these before the Wizard receives broken code.

---

# VI. FUNCTIONAL SCOPE

## Core Capabilities

**Tabula Designandi — The Design Canvas**
Spatial placement of 28 element types across 7 categories on a 16px grid-snapped
QGraphicsScene canvas. Middle-click pan, Ctrl+scroll zoom (0.25×–4.0×). Rubber-
band selection. Container nesting via spatial drop detection. Element resize via
Inspector. 50-step undo/redo. Named canvas sessions persisted to disk.

**Inspector Proprietatum — Property Inspection**
Per-element property editor. Variable name, width, height, colour tokens, layout
type, font size, text content. Width/height changes resize the graphics item
immediately. All changes are reflected in the next Specularium rebuild.

**Armarium Componentium — Component Library**
SQLite-backed sealed component storage. Versioned, forkable. Filter by category
and theme. Load restores to canvas. Fork creates versioned copy. Export generates
code to clipboard.

**Specularium Vivum — Live Preview**
Real PyQt6 widgets rendered from the design tree. 200ms debounce. Render log
per element (clean / stub / error). Available as Feature Page within the shell
and as a detached floating QMainWindow (Ctrl+P). Two independent instances
sharing one PreviewDataModel.

**Codex Exportum — Code Generation**
Walks element tree, emits Python using token constants only (no hex literals).
Validated via `ast.parse()` before delivery. Output: clipboard or file. Preview
with syntax highlighting before export.

**Thema — Theme Management**
Full token registry workspace. Loads theme.json from Bureau I. Applies new QSS
globally. Calls `canvas.refresh_tokens()` to repaint all existing canvas graphics
items immediately. Resets to ModusArcanus defaults when no external theme is
loaded.

## Supporting Capabilities

**LAT/EN Language Toggle** — persisted to `storage/config.json`. Propagates to
all labelled widgets in a single pass. Latin is canonical; English is the
readable layer.

**Elementarium** — categorised, collapsible element browser within the Tabula
feature. Drag-to-place. 28 element types across 7 categories (Receptacula,
Ingressus, Ostensio, Actiones, Tabulae, Ornamentum, Composita).

**Canvas Session Management** — named canvas saves as JSON files in
`storage/canvases/`. Separate from the Component Library. Dirty state tracking
with indicator in Titulum and Fascia. Unsaved-change prompt on new canvas,
session switch, and window close.

**Auxilium — Per-Feature Help** — F1 opens contextual help for the currently
active feature. Non-modal, floating. Content covers overview, controls,
workflow, and edge cases per feature.

**Opening Ceremony** — a brief six-act initialisation sequence on first launch.
Dismissable at any keypress. Does not repeat within a session.

## Explicit Exclusions

- Signal/slot wiring in generated code
- Application logic, data model generation, or business logic
- Non-PyQt6 framework targets
- Hex literals in output at any point in the pipeline
- Pixel-perfect canvas rendering (Specularium handles that)
- Writing to theme.json or any Bureau I artefact
- Writing to Involucrum or any Exocognii logging service at runtime

## Future Scope

The Armarium data model is built to anticipate Exvacua Loricum integration.
The design JSON schema is versioned (`schema_version: "1.0"`) to allow migration.
Handle-based canvas resizing (corner drag handles on selected elements) is a
known deferred item — currently Inspector-driven only. Child resize capping
(prevent child from exceeding parent bounds on resize) requires ratification
before implementation.

---

# VII. CONSTRAINTS & CONTEXT

## Technical Constraints

╭────────────────────────┬──────────────────────────────────────────────────────╮
│  Constraint            │  Detail                                              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  OS                    │  Debian Trixie / KDE Plasma 6 / X11                  │
│  Framework             │  PyQt6 exclusively. No PySide6.                      │
│  Python                │  3.11                                                │
│  QDropEvent            │  `.pos()` removed in PyQt6 — use                    │
│                        │  `.position().toPoint()`                             │
│  QDropEvent mapToScene │  `mapToScene` requires `QPoint`, not `QPointF` —    │
│                        │  `.position().toPoint()` required                   │
│  X11 window spawning   │  Top-level windows require 150ms defer + explicit   │
│                        │  `setParent()` + `raise_()` after visible           │
│  QSplitter             │  Ignores min/max on QScrollArea children — wrap     │
│                        │  in plain QWidget container                         │
│  Clipboard             │  xclip only (X11). QApplication.clipboard().        │
│  Paths                 │  Always `Path(__file__).resolve().parent` — never   │
│                        │  hardcode `/home/lordfingers`                       │
│  Tests                 │  21/21 must pass after any change                   │
╰────────────────────────┴──────────────────────────────────────────────────────╯

## External Dependencies

╭────────────────────────┬──────────────────────────────────────────────────────╮
│  Dependency            │  Role & Risk                                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  PyQt6                 │  All UI. No fallback. Breaking API changes           │
│                        │  (e.g. QDropEvent.pos() removal) require            │
│                        │  immediate patches.                                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Bureau I output       │  `theme.json` — constitutional read-only            │
│  (theme.json)          │  dependency. Absent = ModusArcanus defaults.        │
│                        │  Bureau I builds first.                             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┌──────────────────────────────────────┤
│  SQLite                │  Armarium storage. Local only. No migration         │
│                        │  tooling yet — schema_version field reserved.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Google Fonts          │  IM Fell English + Courier Prime loaded in          │
│  (HTML wireframes)     │  wireframe documents only. Not in application.      │
╰────────────────────────┴──────────────────────────────────────────────────────╯

## Known Bugs Resolved During Development

╭────────────────────────────────────────┬─────────────────────────────────────╮
│  Bug                                   │  Resolution                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Crash on element drag to canvas       │  QDropEvent.pos() removed in PyQt6. │
│                                        │  Fixed: .position().toPoint()       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  TypeError: mapToScene QPointF         │  mapToScene requires QPoint.        │
│                                        │  Fixed: .position().toPoint()       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  All canvas elements same 200×100 size │  Element size registry added.       │
│                                        │  Per-type proportional defaults.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Theme load did not repaint canvas     │  refresh_tokens() added to canvas.  │
│                                        │  setBrush/setPen per element.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Language toggle didn't propagate      │  _on_lang_changed() now calls       │
│  to palette, session bar, drawer       │  set_lang() on every labelled       │
│                                        │  widget in one pass.                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  New canvas destroyed unsaved work     │  Dirty state guard added. Prompt    │
│  silently                              │  fires on new, switch, and close.   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Nesting: children not spatially       │  setParentItem() + _container_at()  │
│  inside parent on canvas              │  drop detection. Council nesting     │
│                                        │  standard applied.                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Inspector width/height did not        │  update_element_size() added.       │
│  resize canvas graphics items         │  setRect() called on change.        │
╰────────────────────────────────────────┴─────────────────────────────────────╯

---

# VIII. SUCCESS CRITERIA

## Functional Success

The application has succeeded when:

The Wizard can drag a QFrame onto the canvas, drop a QLabel and two
ArcaneButton_gold elements inside it, resize the frame via the Inspector,
verify the composition in the Specularium, and export valid Python code that
renders correctly when pasted into another Exocognii application — without
touching the generated code.

All 21 tests pass after any change.

The active theme from Bureau I is reflected immediately on all canvas elements
when loaded, with no manual intervention required.

Named canvas sessions survive application restart.

## User Success

The Wizard has been served when they can compose a new Exocognii UI panel in
under ten minutes, from blank canvas to exported code, without leaving the
application or writing any layout code by hand.

## Quality Benchmarks

╭──────────────────────┬────────────────────────────────────────────────────────╮
│  Benchmark           │  Target                                                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Test suite          │  21/21 passing at all times                           │
│  Codegen output      │  Validates via ast.parse() without exception          │
│  Token compliance    │  Zero hex literals in any generated output            │
│  Canvas serialise    │  Full round-trip: serialize → deserialize → identical │
│  Specularium rebuild │  ≤ 200ms debounce on design_changed signal            │
│  Canvas sessions     │  Persist and restore across application restart       │
│  Nesting containment │  No child element visually outside parent bounds      │
╰──────────────────────┴────────────────────────────────────────────────────────╯

## Failure Conditions

The bureau has failed its purpose if:

- Generated code contains a raw hex value.
- A sealed component cannot be deserialized back to an identical canvas state.
- The Specularium renders a different composition than the canvas shows.
- A child element is rendered outside its parent container's visible bounds.
- The application modifies, overwrites, or guesses at the contents of theme.json.

---

# IX. GLOSSARY

╭──────────────────────────┬────────────────────────────────────────────────────╮
│  Term                    │  Definition in this application                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Agentia                 │  Short form of Agentia Architecturalis.            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Armarium                │  The Component Library. From Latin armarium       │
│                          │  (cabinet, chest). SQLite-backed sealed storage.  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Auxilium                │  Per-feature help dialog. From Latin auxilium      │
│                          │  (aid, assistance).                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  CanvasElement           │  The abstract base class for all placeable items  │
│                          │  on the Tabula. Not a PyQt6 widget — a data       │
│                          │  record that generates one.                       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Codex Exportum          │  The code generation feature. From Latin codex    │
│                          │  (book, record) + exportare (to carry out).       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Composita               │  Palette category for pre-built composite         │
│                          │  ModusArcanus widget patterns (TopBar, StatusBar, │
│                          │  etc.).                                           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Dirty state             │  A canvas that has unsaved changes. Indicated by  │
│                          │  the ring ◌ (U+25CC) in Titulum and Fascia.       │
│                          │  Asterisk (*) and Anima Dot (●) both retired.     │
│                          │  Ring is the ratified standard across all bureaus. │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Elementarium            │  The element browser within the Tabula feature.   │
│                          │  From Latin elementarium (primer, basic           │
│                          │  instruction). An intra-feature panel, not a zone.│
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ElementNode             │  The serialized dict representation of a          │
│                          │  CanvasElement. The currency of saves, undo,      │
│                          │  and codegen.                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Fascia                  │  Zone III. 52px top-right strip. Feature-keyed    │
│                          │  action buttons. HELP is always rightmost.        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Feature Codex           │  Zone II. Left rail below Titulum. Navigation     │
│                          │  list of features. One active at a time.          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Fork                    │  Creating a versioned copy of a sealed component  │
│                          │  in the Armarium. Lineage is preserved.           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Inspector Proprietatum  │  Property editor for the selected canvas element. │
│                          │  From Latin inspector (one who examines) +        │
│                          │  proprietatum (of properties).                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ModusArcanus            │  The visual design system governing all           │
│                          │  Exocognii applications. Defined in              │
│                          │  ModusArcanus.dux.tome.md.                       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Receptacula             │  Palette category for containers (QFrame,         │
│                          │  QGroupBox, QSplitter, QTabWidget). From Latin    │
│                          │  receptaculum (container, repository).            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Scriptorium Canvas      │  Zone IV. All remaining space. Feature-owned.    │
│                          │  From Latin scriptorium (writing room).           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Seal                    │  The act of saving a canvas to the Armarium       │
│                          │  as a named, versioned component. Sealing is      │
│                          │  deliberate and irreversible (fork to modify).    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Sigilla                 │  Latin imperative: seal. The primary save verb    │
│                          │  in UI copy.                                      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Specularium Vivum       │  Live preview. From Latin speculum (mirror) +     │
│                          │  vivum (living). Two instances: Feature Page      │
│                          │  and Floating Window, sharing one data model.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Tabula Designandi       │  The design canvas feature. From Latin tabula     │
│                          │  (board, surface) + designandi (of designing).   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Thema                   │  Theme management feature. Consumes Bureau I      │
│                          │  output. Read-only dependency.                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Titulum                 │  Zone I. 220px left panel. Bureau identity,       │
│                          │  live context, LAT/EN toggle. Fixed. Never        │
│                          │  scrolls, never changes layout.                   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Token                   │  A named colour constant. C_GOLD, C_PANEL, etc.   │
│                          │  Never a raw hex value in application code.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Triumviratus            │  Triumviratus Aestheticus Imperialis. The three-  │
│                          │  bureau governing body of Exocognii aesthetics.   │
│                          │  Bureau I (colour), II (component design),        │
│                          │  III (documentation).                             │
╰──────────────────────────┴────────────────────────────────────────────────────╯

---

# X. REVISION NOTES

╭──────────────────────┬───────────────────────────────────────────────────────╮
│  Version · Date      │  Change                                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  v1.0 · MMXXVI       │  Initial document. Submitted to Convocatio Iudicii.   │
│                      │  A4 Common Shell proposed. Seven wireframes.          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  v1.2 · MMXXVI       │  Post-Convocatio amendments applied:                  │
│                      │  · Canonical identity corrected throughout            │
│                      │  · LAT/EN toggle relocated to Titulum                 │
│                      │  · Zone dimensions enforced (220px / 52px)            │
│                      │  · Dispositio retired from Feature Codex              │
│                      │  · Specularium dual-mode architecture diagrammed      │
│                      │  · Nesting standard documented with examples          │
│                      │  · Thema confirmed as full workspace, not dropdown    │
│                      │  · Dirty state asterisk retired; Anima Dot proposed   │
│                      │  · Opening Ceremony submitted                         │
│                      │  · Verificatio Canonica block added                   │
│                      │  · Known bugs resolved in development logged          │
╰──────────────────────┴───────────────────────────────────────────────────────╯

---

*Sigillatum per Aedificatorem · Bureau II · MMXXVI*

*In Linea · In Parallelo · In Perpetuum.*

*Ordo Discordia, Cosmos Inania*

*⟁*
