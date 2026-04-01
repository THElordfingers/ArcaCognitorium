# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ       Agentia-Architecturalis_IdeaForge.md   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

# AESTHETIC TRINITY — BUREAU II
## Agentia Architecturalis · In Linea, In Parallelo, In Perpetuum
### IdeaForge Build Document · Phase 1 Idea Brief + Phase 2 Seed Prompt

> **Bureau Seal:** *Agentia Architecturalis*
> **Mandate:** The inarguable authority on UI interface construction and testing.
> Every interactive surface built in the Tower must be validated by this bureau before it governs the Wizard's attention.

---

## PHASE 1 — IDEA BRIEF

| Field | Content |
|---|---|
| **App Name** | Agentia Architecturalis |
| **Bureau Latin** | *In Linea, In Parallelo, In Perpetuum* — aligned, parallel, and without end |
| **One-Line Purpose** | A PyQt6 desktop laboratory for designing, testing, and ratifying UI component layouts under the ModusArcanus visual standard, consuming a theme.json from Bureau I as its substrate |
| **Platform** | Debian Trixie / KDE Plasma 6 / X11 / Python 3.11 + PyQt6 |
| **Visual Identity** | ModusArcanus — sourced from a ratified `theme.json` produced by Bureau I. If no theme.json exists, falls back to embedded ModusArcanus defaults. |
| **Role in Trinity** | Bureau II — most actively used during Tower development. The Wizard builds and tests UI components here before deploying them to live tools. Depends on Bureau I for theme; its sealed archetypes inform Bureau III's template work. |

### Core Loop

1. **Componimentum** — The Wizard selects a widget type from the Component Palette. Parameters (text, accent, size, state) are configured via the Property Inspector.
2. **Specularium** — The component renders live in the preview canvas, skinned with the active theme.json. The Wizard can resize the canvas, cycle states (default/hover/active/disabled), and toggle vision simulation.
3. **Compositio** — Multiple components are arranged into a panel composition — rows, columns, QSplitter regions — on an 8px snapping grid.
4. **Iudicium** — The composition is measured against ModusArcanus compliance rules: spacing constants, color role correctness, font hierarchy, keyboard tab order. Violations are cited by rule name and location.
5. **Sigillatio** — A passing composition is sealed as a named Architectura Archetype: serialized to JSON, logged in the Architectura Registry (SQLite), and exported as a Python QWidget scaffold.

### Key Features (v1)

- **Component Fabricia** — palette of all canonical ModusArcanus widget types; each instantiated via factory functions from the dux.tome; parameters editable via property dock
- **Live Specularium** — resizable canvas; widgets rendered in all states; active theme.json applied; hotload stub present
- **Compositio Panel** — drag-to-arrange multi-widget layouts; 8px grid snap; QSplitter-based region definition
- **Iudicium Engine** — automated rule checker: color-role violations, spacing deviations, font hierarchy breaks, unreachable tab stops; scored report per composition
- **Architectura Registry** — SQLite vault of sealed archetypes; each entry: name, widget inventory, rule score, theme hash, export path, timestamp
- **Scaffold Export** — sealed layout exported as a Python QWidget subclass with ModusArcanus header, correct QSS references, stubbed methods
- **Theme Subscription Stub** — watches for theme.json updates from Bureau I (fully wired in v2; stub + fallback banner in v1)

### Explicit Out of Scope (v1)

- No code editing or Python REPL inside the app
- No animation timeline editor
- No live sync to running Tower applications
- No import of third-party UI layouts (Qt Designer .ui files, etc.)
- Does not generate full application skeletons — only QWidget panel scaffolds

### What Distinguishes This From a Generic UI Builder

This is not a general-purpose widget toolkit browser. It is a *compliance laboratory* for one specific visual standard. Every widget it renders is a ModusArcanus widget. Every rule it checks is a ModusArcanus rule. The output is a sealed, scored, citable Layout Archetype that a Tower application can import directly. It enforces the law; it does not suggest options.

### Relationship to Bureau I

- Reads `theme.json` — does not produce it
- If absent: embedded ModusArcanus defaults activate; visible warning banner: *THEMA NON RATIFICATUM — FALLBACK ACTIVO*
- Every sealed archetype stores the theme hash from which it was built — layout provenance is traceable to a Bureau I ratification

### Relationship to Bureau III

- Bureau III pulls from the Architectura Registry to embed panel mockups into document templates
- Bureau II exports layout previews as PNG renders for Bureau III consumption (stub in v1)

### Technical Risks

- **Live canvas resize without layout thrash** — QWidget-based preview that reflows correctly at arbitrary canvas dimensions
- **State forcing** — hover/active/disabled pseudo-states forced programmatically via setProperty() + style().polish(); exotic widgets may require proxy widget pattern
- **Iudicium rule engine** — reliable programmatic spacing and color-role checker without false positives requires careful widget introspection

### v2 Wishlist

- Animation authoring: define and preview 220ms InOutQuad transitions natively
- Full theme.json hotload via file watcher
- Blueprint export: archetype as JSON readable by Tower tools at startup for self-configuration
- Accessibility pipeline: pipe layout to Bureau I's Scrutinium Engine for combined color + layout audit

### Open Questions (Require Wizard Ratification Before Build)

- **Component taxonomy** — canonical list of ModusArcanus widget types this bureau knows about (confirm: buttons, sliders, combos, labels, text fields, separators, panels, status bars — anything else?)
- **Iudicium rule set** — what are the formally named, citable rules? Need Cogniverse register names (e.g., *Lex Spatii Octo* for the 8px spacing law)

---

## PHASE 2 — SEED PROMPT

```
You are a senior software architect writing for a mid-level Linux developer.
Produce complete, developer-ready construction documentation for
"Agentia Architecturalis" — a ModusArcanus-compliant PyQt6 desktop application
built with Python 3.11 + PyQt6 on Debian Trixie / KDE Plasma 6 / X11.

Agentia Architecturalis is a UI component layout laboratory: the Wizard
instantiates ModusArcanus-standard widgets, arranges them into panel
compositions, submits the result to the Iudicium compliance engine, and
upon passing — seals the layout as a reusable Architectura Archetype.

It is Bureau II of the Aesthetic Trinity. It depends on Bureau I (Codexium
Chromaticus) for its theme.json substrate. Its sealed archetypes feed Bureau III.

Architecture stages:
1. Componimentum  — widget selection and property configuration; all widgets via ModusArcanus factory functions
2. Specularium    — live canvas: widget preview in all states (default/hover/active/disabled); resizable canvas
3. Compositio     — multi-widget layout arrangement on an 8px-snapping grid; QSplitter-based regions
4. Iudicium       — automated compliance check: color role, spacing, font hierarchy, tab order; scored report
5. Sigillatio     — passing layout sealed as a named Architectura Archetype in SQLite; Python QWidget scaffold exported

Architectural constraints:
- Framework: PyQt6 only. No tkinter, customtkinter, or PySide6.
- Theme source: reads theme.json from Bureau I. If absent, applies embedded ModusArcanus defaults with a visible THEMA NON RATIFICATUM warning banner.
- Widget factory: all widgets created via ModusArcanus factory functions (arcane_button, gold_label, dim_label, etc. from dux.tome). No ad-hoc styling anywhere.
- State forcing: hover/active/disabled states forced via setProperty() + style().polish(). Not mouse simulation.
- Grid: all layout snaps to 8px unit. Iudicium flags any spacing not divisible by 8 as a rule violation.
- Storage: SQLite via sqlite3. No ORM. CREATE TABLE statements verbatim.
- Export: Python QWidget scaffold uses ModusArcanus file header and imports factory functions from a shared Shared/ module stub.
- Threading: file I/O, export, DB writes use QRunnable + WorkerSignals. Main thread never blocks.
- Naming: all UI copy in Cogniverse Latin (Nomina Arcana). No English in the interface.
- File headers: every .py uses the ModusArcanus standard header block.
- Path resolution: always Path.home().

Begin with a Table of Contents.

Sections — fully specified:

1. Overview & Architecture
   - One paragraph summary
   - Stage table: Name | Role
   - Keyboard shortcuts table

2. Tech Stack — table: Tool | Version | Justification

3. Directory Tree & Database Schema
   - Full annotated file tree
   - CREATE TABLE: architectura_registry, iudicium_reports, archetype_exports

4. Module Breakdown
   - Table: Module | Stage | Responsibility | Inputs | Outputs | Dependencies

5. UI Wireframe
   - ASCII multi-panel: Component Palette (left dock), Specularium canvas (centre, dominant), Property Inspector (right dock), Iudicium Report (bottom collapsible drawer), Sigillatio controls (status bar)
   - Full legend
   - THEMA NON RATIFICATUM banner placement shown

6. Data Flow — 3 paths:
   - (a) Happy path: select widget → configure → arrange → iudicium pass → seal → export scaffold
   - (b) Iudicium failure: layout fails rule → cited violation report, sealing blocked
   - (c) Theme load failure: theme.json absent or malformed → fallback activates, banner shown

7. Code Stubs
   - All public classes and functions with type hints and docstrings
   - IudiciumEngine: full rule-check pseudocode (spacing validator, color-role checker, font hierarchy checker, tab-order walker)
   - widget_factory module: all ModusArcanus factory function stubs
   - theme_loader: load → validate schema → apply or fallback
   - scaffold_export: QWidget subclass as a Python string template

8. Error Handling — per-module table: Error | Cause | Strategy
   - Include: theme.json schema violation, DB init failure, export write failure, state-force failure on exotic widgets

9. Setup & Testing
   - requirements.txt
   - Install, run, test commands
   - One unit test per core module
   - Integration test: instantiate widget → arrange → iudicium → assert pass → seal → read back from registry

10. Packaging
    - .desktop file template (verbatim)
    - PyInstaller command with all flags

11. Extensibility — 6 features:
    - Animation Authoring (220ms InOutQuad transitions defined and previewed natively)
    - Blueprint Export (archetype as JSON read by Tower tools at startup)
    - Full Theme Hotload (file watcher, live reskin)
    - Accessibility Pipeline (route layout to Bureau I Scrutinium for combined audit)
    - Comparative Iudicium (diff two sealed archetypes)
    - Archetype Library Sync (push sealed archetypes to ArcaCognitorium Shared/ via git stub)

snake_case. No filler. Every sentence carries information.
Write for a mid-level developer with ModusArcanus.dux.tome.md and the Bureau I theme.json schema as reference documents.
```

---

*IdeaForge · Bureau II · Agentia Architecturalis · ＭＭＸＸＶＩ*
