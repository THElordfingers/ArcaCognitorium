# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ         Codexium-Chromaticus_IdeaForge.md   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

# AESTHETIC TRINITY — BUREAU I
## Codexium Chromaticus · Sequentiae Umbrarum
### IdeaForge Build Document · Phase 1 Idea Brief + Phase 2 Seed Prompt

> **Bureau Seal:** *Auctoritas Spectralis*
> **Mandate:** Unified source of color themes for the entire Tower jurisdiction.
> Every palette issued by this bureau is law. All other applications defer to it.

---

## PHASE 1 — IDEA BRIEF

| Field | Content |
|---|---|
| **App Name** | Codexium Chromaticus |
| **Bureau Latin** | Sequentiae Umbrarum — *the succession of shadows* |
| **One-Line Purpose** | A PyQt6 desktop application for composing, ratifying, and exporting authoritative color theme packages that govern the visual identity of every application in the Tower |
| **Platform** | Debian Trixie / KDE Plasma 6 / X11 / Python 3.11 + PyQt6 |
| **Visual Identity** | ModusArcanus — void black, aurum gold, parchment text. The application is itself a demonstration of compliance with the standard it enforces. |
| **Role in Trinity** | Bureau I — foundation. Its output (`theme.json`) is a dependency for Bureaus II and III. Must exist and produce a ratified palette before downstream tools can operate at full power. |

### Core Loop

1. **Compositio** — The Wizard constructs a palette by setting base colors via hex input or OKLAB coordinate sliders. The system continuously derives the full chromatic token hierarchy from the base pair.
2. **Scrutinium** — Live accessibility audit: WCAG 2.1, APCA, and perceptual contrast metrics update in real-time across all token pairs. Vision simulation overlays available.
3. **Auto-Render** — The application continuously skins itself with the in-progress palette. The Wizard sees the theme applied to real arcane widgets — not abstract swatches.
4. **Ratificatio** — The Wizard formally ratifies a palette. It receives a seal (timestamp + SHA-256 of the token set), a Latin designator, and enters the Chromatic Registry (SQLite).
5. **Promulgatio** — Ratified themes are exported as `theme.json` (Tower canonical format), `.qss` (Qt stylesheet), and `.md` (human-readable palette card). Tower broadcast is stubbed for v2.

### Key Features (v1)

- **Chromatic Forge** — dual-input (hex + OKLAB sliders) for BG/FG base pair; full token hierarchy (C_PANEL, C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_CRIMSON, C_TEAL, C_TEXT, C_SUBTLE, C_WHITE) auto-derived from the base pair via a documented OKLAB pipeline
- **Scrutinium Engine** — real-time WCAG 2.1 + APCA contrast matrix for all token pairs; three vision simulation overlays (deuteranopia, protanopia, achromatopsia)
- **Self-Rendering Preview** — QApplication.instance().setStyleSheet() called on every palette change; the live window reskins without restart
- **Chromatic Registry** — SQLite vault of all ratified palettes; each entry: name, Latin designator, hex tokens, OKLAB values, contrast scores, seal hash, timestamp
- **Promulgation Engine** — exports `theme.json` (Tower canonical TypedDict schema), `.qss`, and `.md` palette card; Tower broadcast stub present
- **Sequence Viewer** — luminance ladder, OKLAB solar system projection, and harmony wheel for any selected palette in the registry (conceptually inspired by Pairz's stat-view philosophy — not its code or implementation)

### Explicit Out of Scope (v1)

- No BLE or hardware integration
- No web deployment or cloud sync
- No auto-application to running Tower tools (Tower broadcast is stubbed, not wired)
- No generative / AI-assisted palette suggestion
- No import of external theme formats (CSS variables, Figma tokens, etc.)
- Does not redesign or replace Pairz

### What Makes This Different From Pairz

Pairz is a *contrast analysis and exploration tool* — it helps a designer discover whether two colors work together and provides rich statistical infographics about that pair. It operates on *pairs*.

Codexium Chromaticus is a *theme governance system* — it produces a complete, hierarchical, named palette that becomes the law of the Tower. It operates on *systems of tokens*. It ratifies, seals, stores, and promulgates. It does not explore; it decides.

Conceptual debt to Pairz:
- OKLAB as the perceptual backbone (borrowed philosophy, not reimplemented from Pairz source)
- Real-time accessibility scoring as a first-class UI element (inspired by Pairz's live contrast model)
- The idea that the app itself demonstrates the palette it is building (Pairz does this implicitly; Codexium Chromaticus does it explicitly as its central mechanism)

What Pairz's architecture teaches us to avoid:
- customtkinter — replaced with PyQt6 (ModusArcanus standard)
- Monolithic single-file structure — decomposed into focused modules
- No formal storage schema — Codexium Chromaticus uses SQLite with a defined schema from day one

### Technical Risks

- **OKLAB derivation hierarchy** — computing the full token set from two base inputs without producing perceptually dissonant intermediates requires careful perceptual-space math
- **Self-skinning without flicker** — dynamically reapplying QSS to a live window on every slider change requires debouncing and careful paint scheduling
- **Ratification seal integrity** — ensuring the SHA-256 hash covers the canonical token representation so the seal is verifiable across export formats

### v2 Wishlist

- Tower broadcast via ZMQ — push ratified theme to all running Tower tools live on ratification
- Import mode — ingest a `.qss` or CSS-variable file and reverse-derive the token structure
- AI Palette Oracle — a Council entity proposes a palette from a lore description prompt
- Delta-E lock — guarantee minimum perceptual distance between all token pairs before ratification is permitted
- Palette lineage view — visual diff between two registered themes in the Registry

### Open Questions (Require Wizard Ratification Before Build)

- **Designator vocabulary** — what is the naming convention for a ratified palette? Latin color families? Arcane registers? The Wizard names; the bureau records.
- **theme.json schema** — must be formally defined before this document and published as Tower standard before Bureaus II and III can stub their dependencies correctly. This is the most critical pre-build decision.

---

## PHASE 2 — SEED PROMPT

```
You are a senior software architect writing for a mid-level Linux developer.
Produce complete, developer-ready construction documentation for
"Codexium Chromaticus" — a ModusArcanus-styled PyQt6 desktop application
built with Python 3.11 + PyQt6 on Debian Trixie / KDE Plasma 6 / X11.

Codexium Chromaticus is a color theme governance tool: the Wizard composes
a hierarchical palette of named color tokens, submits it to live perceptual
contrast audit, and — upon ratification — exports it as a sealed theme.json
package that governs the visual identity of all other Tower applications.

It is Bureau I of the Aesthetic Trinity. Its output (theme.json) is a
dependency for Bureau II (Agentia Architecturalis) and Bureau III
(Departamentum Documentalis).

Architecture stages:
1. Compositio    — BG/FG hex and OKLAB slider input; full token hierarchy derived in real-time from the base pair
2. Scrutinium    — real-time WCAG 2.1 + APCA contrast matrix across all token pairs; three vision simulation overlays
3. Auto-Render   — application reskins itself live on every palette change via QApplication.instance().setStyleSheet()
4. Ratificatio   — palette receives a seal (SHA-256 of canonical token dict + ISO timestamp), a Latin designator, and enters the Chromatic Registry (SQLite)
5. Promulgatio   — export to theme.json (canonical Tower TypedDict format), .qss (Qt stylesheet), and .md palette card; Tower broadcast stub present

Architectural constraints:
- Framework: PyQt6 only. No tkinter, customtkinter, or PySide6 anywhere.
- Visual identity: The application begins in the embedded ModusArcanus defaults (C_BG="#050507", C_GOLD="#d4af37", C_TEXT="#c8b88a", Georgia serif) and reskins as the Wizard works. It demonstrates compliance with the standard it enforces.
- OKLAB: use the `colour-science` library for all perceptual math. No custom OKLAB implementation.
- Derivation: all tokens (C_PANEL, C_GOLD_DIM, C_GOLD_DARK, C_CRIMSON, C_TEAL, C_SUBTLE, C_WHITE) are computed from the BG/FG base pair via a documented OKLAB derivation pipeline. The Wizard does not enter intermediate tokens manually.
- Self-render: QSS is regenerated on every palette change and applied via QApplication.instance().setStyleSheet(). Debounced at 150ms. No full window restart.
- Storage: SQLite via Python standard library sqlite3. No ORM. CREATE TABLE statements shown verbatim.
- Export: theme.json schema defined completely as a TypedDict — this is the Tower inter-app contract. Every field documented.
- Threading: all blocking ops (file I/O, DB writes, export) use QRunnable + WorkerSignals. Main thread never blocks.
- Naming: all UI copy in Cogniverse Latin register (Nomina Arcana from ModusArcanus). No English labels in the interface.
- File headers: every .py file uses the ModusArcanus standard header block.
- Path resolution: always Path.home(). Never hardcode /home/lordfingers.

Begin with a Table of Contents.

Sections — include every item, fully specified:

1. Overview & Architecture
   - One paragraph summary
   - Stage table: Name | Role
   - Keyboard shortcuts table

2. Tech Stack — table: Tool | Version | Justification

3. Directory Tree & Database Schema
   - Full annotated file tree
   - CREATE TABLE statements for: chromatic_registry, seal_log, export_log

4. Module Breakdown
   - Table: Module | Stage | Responsibility | Inputs | Outputs | Dependencies

5. UI Wireframe
   - ASCII multi-panel layout: Forge panel (left — hex inputs + OKLAB sliders), Scrutinium matrix (centre — contrast grid), Self-Render preview (right — live widget preview), Registry drawer (collapsible bottom), Promulgatio controls (status bar)
   - Full legend — every element explained

6. Data Flow — 3 labeled paths:
   - (a) Happy path: adjust sliders → auto-derive tokens → scrutinium passes → ratify → export theme.json
   - (b) Ratification blocked: palette fails WCAG AA minimum on one or more token pairs — blocked with full scored report; no seal issued
   - (c) Export failure: disk write error or theme.json schema validation failure — user notified, registry entry not marked as exported

7. Code Stubs
   - All public classes and functions with type hints and one-line docstrings
   - Full derivation pipeline pseudocode (OKLAB coordinate space → token hierarchy — show the math steps)
   - Ratification seal generation stub (SHA-256 of canonical token dict + timestamp + designator slot)
   - theme.json TypedDict — defined completely; this is the Tower standard
   - QSS generation function stub (takes token dict, returns complete QSS string)
   - Scrutinium engine: contrast matrix computation pseudocode

8. Error Handling — per-module table: Error | Cause | Strategy
   - Include: colour-science import failure, DB init failure, OKLAB computation returns NaN, QSS application failure, export write failure

9. Setup & Testing
   - requirements.txt (full content)
   - Install, run, test commands
   - One unit test per core module
   - Integration test: set BG/FG → derive tokens → assert scrutinium pass → ratify → read back from registry → export → validate theme.json against TypedDict schema

10. Packaging
    - .desktop file template (verbatim)
    - PyInstaller command with all relevant flags
    - Runtime asset path resolution pattern (Path.home())

11. Extensibility — 6 features:
    - Tower Broadcast (ZMQ push of ratified theme.json to all running Tower tools on ratification event)
    - Import Mode (ingest .qss or CSS-variable block; reverse-derive token structure into Compositio stage)
    - AI Palette Oracle (prompt a Council entity with a lore description; receive a proposed base pair and rationale)
    - Delta-E Lock (configurable minimum perceptual distance between all token pairs; blocks ratification if not met)
    - Palette Lineage (visual diff between two registry entries; show which tokens changed, by how much, in OKLAB space)
    - Chromatic Covenant (git push stub to commit ratified theme.json to the ArcaCognitorium repository)

snake_case. No filler. Every sentence carries information.
Write for a mid-level developer who has ModusArcanus.dux.tome.md loaded as their primary visual reference.
```

---

*IdeaForge · Bureau I · Codexium Chromaticus · ＭＭＸＸＶＩ*
