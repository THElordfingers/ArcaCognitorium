# Agentia Architecturalis — Expositio

> Bureau II · The Architectural Alignment Enforcement Agency
> Aesthetic Authoritarian Associative Alliance (A4)

---

## I. Identity

- **Name:** The Architectural Alignment Enforcement Agency
- **Latin:** Agentia Architecturalis
- **Motto:** In Linea, In Parallelo, In Perpetuum 
	(Lined up, Parallel, Forever.)
- **Version:** 1.0.0
- **Tagline:** 
  — no element is unsanctioned.
- **Classification:** PyQt6 visual UI component designer.
- **Status:** Active development. Core pipeline functional.
  21/21 tests pass.
- **Dependencies:** Bureau I (Auctoritas Spectralis) for
  theme.json input.

---

## II. Purpose

### Problem Statement

Building ModusArcanus-compliant UI panels requires writing
repetitive PyQt6 boilerplate. The Wizard must mentally
translate spatial design intent into code — a lossy, slow
process. There is no visual sandbox for composing widget
arrangements before committing them to code.

### Motivation

Bureau II replaces the Fenestrarium. It provides a visual
design surface where the Wizard works spatially, not
textually. Code generation is an export artifact, not the
primary interaction. The tool consumes Bureau I's ratified
palettes so all designs are chromatically compliant from
the start.

### Intended Outcome

Clean, correct Python/PyQt6 code blocks ready for
integration into Tower applications. A growing Component
Library of reusable, versioned, forkable designs.

### Anti-Purpose

This is not a code editor. It does not compile or run the
generated code. It does not manage application logic,
signals, or data binding. It designs static widget
compositions.

---

## III. Audience

- **Primary:** The Wizard (LordFingers) — sole operator.
- **Secondary:** The Builder, consuming exported code.
  Arx Aedificare as downstream integration target.
- **Assumed Knowledge:** Familiarity with PyQt6 widget
  classes and ModusArcanus layout conventions.

---

## IV. Design Philosophy

- Spatial over textual — the Wizard places widgets
  visually, not by writing code.
- Token references over hardcoded values — generated code
  uses C_GOLD, not "#d4af37".
- Library over clipboard — designs are saved, versioned,
  forked, and searchable.
- Preview fidelity — the Specularium renders real PyQt6
  widgets, not mockups.
- Rejects: Drag-and-drop complexity for its own sake. The
  canvas is simple and honest.

---

## V. Technical Concept

A categorized palette of element types feeds a
QGraphicsScene-based canvas. Elements are placed, nested,
configured via an inspector, and previewed as real widgets.
Completed designs serialize to JSON, persist in SQLite, and
export as Python code.

Core abstractions: CanvasElement (abstract base — renders,
serializes, previews, generates code), DesignDocument (the
complete serialized tree), ElementNode (single tree node),
PropertySet (configurable properties per element, colors as
token names).

Key decisions: QGraphicsScene for item-level canvas
operations, element factory pattern for extensibility,
ast.parse() as codegen sanity check.

---

## VI. Functional Scope

### Core

- 28 element types across 7 palette categories
  (Receptacula, Ingressus, Ostensio, Actiones, Tabulae,
  Ornamentum, Composita)
- Drag-and-drop or click-to-place element placement
- Container nesting with automatic child layout
- Context-sensitive property inspector with token-based
  color selection
- Live preview using real PyQt6 widgets (200ms debounce)
- Component Library (SQLite): save, load, fork, version,
  archive, search
- Python/PyQt6 code generation with ModusArcanus headers
  and token constants
- theme.json consumption from Bureau I with fallback to
  ModusArcanus defaults
- Undo/redo via serialized canvas snapshots
- Zoom (Ctrl+scroll), grid toggle, snap-to-grid

### Exclusions

- No AI integration, no network dependency
- No signal/slot wiring or application logic
- No colour-science dependency — colors come from
  Bureau I or defaults

---

## VII. Constraints

- Python 3.11+, PyQt6 6.6+. Single dependency.
- Depends on Bureau I output (theme.json) but operates
  independently with defaults.
- Target: CastrumDigitos (Debian Trixie, KDE Plasma 6).
- Single-user application.

---

## VIII. Success Criteria

- Compose a panel, save it, and export valid Python code
- 21/21 tests pass; generated code passes ast.parse()
- Failure: generated code produces import errors or widget
  crashes in a Tower application

---

## IX. Glossary

- **Elementarium** — the categorized widget palette
  (left panel)
- **Tabula Designandi** — the design canvas (centre)
- **Inspectorium** — the property editor (right upper)
- **Specularium Vivum** — the live preview panel
  (right lower)
- **Armarium Componentium** — the Component Library
  drawer (bottom)
- **Promulgatio** — code export stage
- **CanvasElement** — abstract base class for all
  placeable element types
- **DesignDocument** — the complete serialized design
  tree stored in SQLite

---

*Ordo Discordia, Cosmos Inania*
