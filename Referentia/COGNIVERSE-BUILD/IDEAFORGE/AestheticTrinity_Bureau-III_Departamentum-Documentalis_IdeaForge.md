# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ     Departamentum-Documentalis_IdeaForge.md   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

# AESTHETIC TRINITY — BUREAU III
## Departamentum Documentalis · Define! Designa! Denota! Discede!
### IdeaForge Build Document · Phase 1 Idea Brief + Phase 2 Seed Prompt

> **Bureau Seal:** *Departamentum Documentalis*
> **Mandate:** Inarguable authority on document templates and form masters for the Tower.
> Every written output, structured record, or exportable form produced within the Tower's jurisdiction must conform to a template ratified by this bureau.

---

## PHASE 1 — IDEA BRIEF

| Field | Content |
|---|---|
| **App Name** | Departamentum Documentalis |
| **Bureau Latin** | *Define! Designa! Denota! Discede!* — Define it. Design it. Denote it. Dismiss it. |
| **One-Line Purpose** | A PyQt6 desktop template forge for authoring, ratifying, and publishing structured document templates and form masters that govern all Tower-produced written outputs |
| **Platform** | Debian Trixie / KDE Plasma 6 / X11 / Python 3.11 + PyQt6 |
| **Visual Identity** | ModusArcanus — sourced from Bureau I's ratified theme.json; falls back to embedded defaults if absent |
| **Role in Trinity** | Bureau III — largest scope, least urgent as a development dependency. Its work governs documents, not code. Tower tools can operate without it until their output documentation needs are formalized. |

### Core Loop

1. **Definitio** — The Wizard defines the purpose and structure of a new document type. Fields are named and typed (text, date, enum, numeric, freeform block). The Wizard declares whether the form is *static* (filled once and sealed) or *recurrent* (used as a repeating record form).
2. **Designatio** — The Wizard lays out the document template in a visual composer: section headers, field blocks, dividers, footer signatures. A live preview renders the template in its ratified visual style.
3. **Notatio** — The Wizard annotates each field: label text (in the Cogniverse register), placeholder hint, validation rules, optionality.
4. **Ratificatio** — The template passes through a structural audit (all required metadata present, no orphaned fields, no unlabelled sections). A passing template is sealed and enters the Template Registry.
5. **Promulgatio** — Sealed templates are exported as: a `.md` master form (human-readable), a `.json` form schema (machine-readable; consumed by Tower tools that need to produce structured reports), and a PDF-ready render stub.

### Key Features (v1)

- **Template Fabricia** — section, field, divider, and signature-block components; each has a label, type, and metadata
- **Compositio Canvas** — visual template layout; drag-to-arrange sections; live preview of rendered template in ModusArcanus document style
- **Notatio Panel** — per-field annotation dock: label (Cogniverse Latin), hint, validation rules, required/optional toggle
- **Structural Auditor** — pre-ratification checker: all sections labelled, no orphaned fields, required metadata populated, section hierarchy coherent
- **Template Registry** — SQLite vault of sealed templates; each entry: name, form type (static/recurrent), field inventory, section count, seal hash, export paths
- **Promulgatio Engine** — exports `.md` master form, `.json` form schema, and a PDF-ready render (stub; full PDF in v2)
- **Form Instance Mode** — the Wizard can instantiate a sealed template, fill it with data, and export a completed form record (this is the daily-use mode once templates are ratified)
- **Bureau I/II Integration Stubs** — theme.json subscription (Bureau I) and archetype mockup embed (Bureau II layout previews pulled into template headers)

### Explicit Out of Scope (v1)

- No real-time collaboration or multi-user editing
- No cloud storage or sync
- No full PDF rendering engine (export stub only; marked for v2 with a specific library recommendation)
- No automated form parsing or OCR import
- Does not generate application documentation (that is a different concern from document templates)

### What Distinguishes This From a Generic Form Builder

Most form builders are concerned with data capture for web submissions. Departamentum Documentalis is concerned with *aesthetic authority over Tower-produced written matter*. Its templates are not data schemas for APIs — they are *styled, named, ratified documents* that carry the Tower's visual identity and the Wizard's seal. The output is a living artefact, not a database row. The `Define! Designa! Denota! Discede!` motto is the workflow: define the purpose, design the form, annotate every field, and dismiss it once sealed.

### Relationship to Bureaus I and II

- Reads `theme.json` from Bureau I for document styling (color, typography)
- Pulls sealed Layout Archetypes from Bureau II as optional embedded header panels (UI mockup panels inside template cards — stub in v1, wired in v2)
- Does not feed upstream — it is the terminus of the Aesthetic Trinity's data flow

### What Tower Tools Use This

Any Tower application that produces a structured output — a session report, a ratification record, an entity brief, an IdeaForge document — can consume a template from this bureau's registry. The `.json` form schema becomes the contract for those outputs.

Examples of templates this bureau would ratify:
- The IdeaForge Phase 1 Idea Brief template (the one the Wizard fills in to commission a build)
- The Expositio (application documentation card)
- The Dux Tome (application governance document)
- Entity Spec Sheets (for Entitex entities)
- Session Handoff documents

### Technical Risks

- **Live document preview** — rendering a styled, multi-section document layout as a live PyQt6 canvas without becoming a word processor
- **Form Instance Mode** — a filled form that looks like the template but is clearly a record instance, not the master; provenance must be unambiguous
- **JSON schema export** — the form schema must be well-formed enough that Tower tools can consume it without knowing anything about Departamentum Documentalis's internals

### v2 Wishlist

- Full PDF export via `reportlab` or `weasyprint` — styled, printable, with the Tower's visual identity intact
- Template inheritance — a child template that extends a parent, overriding specific fields
- Form record browser — browse all completed form instances, search by template, filter by date
- Bureau II archetype embed — pull a live UI mockup panel from Bureau II into a template header automatically

### Open Questions (Require Wizard Ratification Before Build)

- **Document type taxonomy** — what are the canonical Tower document types? Confirm the first set to template (IdeaForge Brief, Expositio, Dux Tome, Entity Spec Sheet — what else?)
- **Form instance storage** — does Departamentum Documentalis store completed form instances, or does each Tower tool own its own record storage and merely consumes the template schema?

---

## PHASE 2 — SEED PROMPT

```
You are a senior software architect writing for a mid-level Linux developer.
Produce complete, developer-ready construction documentation for
"Departamentum Documentalis" — a ModusArcanus-compliant PyQt6 desktop application
built with Python 3.11 + PyQt6 on Debian Trixie / KDE Plasma 6 / X11.

Departamentum Documentalis is a document template forge: the Wizard defines
the structure and layout of a Tower document type, annotates every field,
passes the template through a structural audit, and seals it. Sealed templates
are exported as a .md master form, a .json form schema (consumed by Tower tools
that produce structured outputs), and a PDF-ready render stub.

It is Bureau III of the Aesthetic Trinity — the terminus. It consumes theme.json
from Bureau I and may embed UI archetypes from Bureau II. It produces no upstream
dependencies; it governs all Tower-produced written matter.

Architecture stages:
1. Definitio    — document type declared: name, form_type (static/recurrent), purpose statement
2. Designatio   — visual template composition: sections, field blocks, dividers, signature blocks arranged on canvas
3. Notatio      — per-field annotation: label (Cogniverse Latin), hint text, type, validation rules, optionality
4. Ratificatio  — structural audit: all sections labelled, no orphaned fields, required metadata complete; passing template sealed and registered
5. Promulgatio  — export: .md master form, .json form schema, PDF-ready render stub

Architectural constraints:
- Framework: PyQt6 only. No tkinter, customtkinter, or PySide6.
- Theme source: reads theme.json from Bureau I. If absent, embedded ModusArcanus defaults + THEMA NON RATIFICATUM banner.
- Document canvas: QScrollArea containing a QFrame-based page mockup. Not a QTextEdit. The template is composed from widget-level section components, not freeform text entry.
- Field types supported in v1: text (single-line), text_block (multi-line), date, enum (dropdown), numeric, boolean (checkbox). Each rendered consistently.
- Form Instance Mode: a sealed template can be instantiated; the Wizard fills data fields; the result is exported as a completed record. Record is distinct from master (different header branding).
- Storage: SQLite via sqlite3. No ORM. CREATE TABLE verbatim.
- JSON schema export: must be self-describing — a consuming Tower tool should be able to render a form from the schema alone without accessing the registry.
- Threading: file I/O, export, DB writes use QRunnable + WorkerSignals.
- Naming: all UI copy in Cogniverse Latin. No English in the interface.
- File headers: every .py uses the ModusArcanus standard header.
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
   - CREATE TABLE: template_registry, field_definitions, form_instances, export_log

4. Module Breakdown
   - Table: Module | Stage | Responsibility | Inputs | Outputs | Dependencies

5. UI Wireframe
   - ASCII multi-panel: Section/Field Palette (left dock), Compositio canvas (centre, scrollable page mockup), Notatio Inspector (right dock), Audit Report (bottom drawer), Promulgatio controls (status bar)
   - Full legend
   - Show the Form Instance Mode state (distinct header branding on the canvas)

6. Data Flow — 3 paths:
   - (a) Happy path: define type → compose → annotate → audit pass → seal → export .md + .json
   - (b) Audit failure: unlabelled section or orphaned field → cited violations, sealing blocked
   - (c) Form instance export: instantiate sealed template → fill → export completed record as .md

7. Code Stubs
   - All public classes and functions with type hints and docstrings
   - StructuralAuditor: full audit pseudocode (section labelling check, field orphan check, required metadata check, hierarchy coherence check)
   - schema_exporter: .json form schema TypedDict — define it completely as a Tower contract
   - form_renderer: QFrame-based page component that renders a template or instance
   - instance_export: completed record export to .md

8. Error Handling — per-module table: Error | Cause | Strategy
   - Include: theme.json absent, DB init failure, export write failure, schema validation failure on import by a Tower tool (document this from the consumer's perspective)

9. Setup & Testing
   - requirements.txt
   - Install, run, test commands
   - One unit test per core module
   - Integration test: define template → compose → annotate → audit → seal → instantiate → fill → export record → verify .json schema is self-describing

10. Packaging
    - .desktop file template (verbatim)
    - PyInstaller command with all flags

11. Extensibility — 6 features:
    - Full PDF Export (reportlab or weasyprint; styled with Tower visual identity)
    - Template Inheritance (child template extends parent, overrides specific fields)
    - Form Record Browser (browse completed instances by template and date)
    - Bureau II Archetype Embed (pull UI mockup panel from Bureau II into template header automatically)
    - Template Versioning (ratified templates are immutable; new versions create new sealed entries; old instances reference their template version hash)
    - Tower Form Registry API stub (a minimal HTTP endpoint that Tower tools can query to fetch the latest schema for a named template)

snake_case. No filler. Every sentence carries information.
Write for a mid-level developer with ModusArcanus.dux.tome.md, the Bureau I theme.json schema, and the Bureau II archetype registry schema as reference documents.
```

---

*IdeaForge · Bureau III · Departamentum Documentalis · ＭＭＸＸＶＩ*
