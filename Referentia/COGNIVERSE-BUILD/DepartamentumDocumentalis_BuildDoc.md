# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ   DepartamentumDocumentalis_BuildDoc.md   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

# DEPARTAMENTUM DOCUMENTALIS — Define! Designa! Denota! Discede!
## Bureau III · The Department of Documented Design Definitives
### Developer-Ready Build Document · v1.0

> **Parent Alliance:** Aesthetic Authoritarian Associative Alliance (A4)
> *Triumviratus Aestheticus Imperialis*
>
> **Bureau Seal:** *Departamentum Documentalis*
> **Mandate:** Every document produced under this department's
> authority bears its tag, obeys its template, and travels in
> pairs. The Bureau is thorough. The Bureau is always Theroux.

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

Departamentum Documentalis is a PyQt6 document authority
application. It is simultaneously a template design environment, a
document type registry, a style authority, a content authoring
surface, a document transition engine, and a paired output
enforcer. It is the Grand Home of the Tome.

The Bureau operates on three concurrent planes:

**Element Mode** — the Wizard designs individual document elements
(headings, body text, code blocks, tables, title blocks, pull
quotes, form fields, boilerplate blocks) with full typographic and
color control. Each element renders a live wireframe preview as
properties are configured. Elements are locked and promoted to the
template assembly stage.

**Template Mode** — locked elements are arranged into complete
document structures with named sections, required/optional
flagging, section reordering, form skeleton authoring, and
recurring header/footer definitions. Live document preview renders
the template as it would appear on its target surface (`.wiz` as a
dark page render, `.md` as terminal-style render).

**Transition Mode** — existing documents are loaded, a target
template is selected, and the Bureau reads the document's
`.bureau.json` companion to produce a diff view: current rendering
on the left, preview under the new template on the right. Conflicts
are flagged. The Wizard resolves conflicts before committing. The
transition produces fresh `.wiz` + `.md` output and updates the
companion JSON with a transition history entry. Originals are
archived, never deleted.

Every document produced by the Bureau carries a `.bureau.json`
companion file — the document's structural skeleton, template tag,
metadata, version, and transition history. This is what makes
retroactive restyling possible. The companion is the document's
memory. When a template changes, the Bureau reads the JSON,
rebuilds the document against the new template, and produces fresh
paired output. The content never has to move.

The Bureau consumes `theme.json` from Bureau I as a default color
source, but templates can diverge. Template-level color overrides
are fully supported. Independent color schemes (e.g., Loridex sepia
cards) are stored per tag and do not pollute the suite palette.

Output is always paired: `.wiz` + `.md` travel together. The Bureau
enforces this on export automatically. The Wizard never has to
remember.

### Architecture Stages

╭──────────────────┬──────────────────────────────────────────────╮
│ Stage            │ Role                                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Selectio         │ Browse document tags and templates in the    │
│ Elementorum      │ Registry; select surface type (.wiz / .md)   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Fabricatio       │ Element Mode — design individual document    │
│ Elementorum      │ elements with full typographic control       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Constructio      │ Template Mode — assemble elements into       │
│ Formae           │ complete document structure with sections    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Transitus        │ Transition Mode — restyle existing documents │
│                  │ against new templates via .bureau.json       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Promulgatio      │ Export paired .wiz + .md output; export tag  │
│                  │ registry for suite consumption               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Ratificatio      │ Wizard ratifies tags, templates, and color   │
│                  │ overrides as canonical                       │
╰──────────────────┴──────────────────────────────────────────────╯

### Keyboard Shortcuts

╭──────────────┬──────────────────────────────────────────────────╮
│ Binding      │ Action                                           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ q            │ Exire — quit application                        │
│ Ctrl+S       │ Sigillare — save current template               │
│ Ctrl+Shift+S │ Sigillare Novum — save as new template          │
│ Ctrl+E       │ Exportare — export paired output                │
│ Ctrl+Z       │ Revocare — undo                                 │
│ Ctrl+Shift+Z │ Restituere — redo                               │
│ Ctrl+N       │ Novum — new template                            │
│ Ctrl+O       │ Aperire — open from registry                    │
│ Ctrl+1       │ Focus Element Mode                              │
│ Ctrl+2       │ Focus Template Mode                             │
│ Ctrl+3       │ Focus Transition Mode                           │
│ Ctrl+L       │ Registrum — toggle Registry panel               │
│ Ctrl+P       │ Praevisu — toggle live preview                  │
│ Ctrl+T       │ Thema — load a theme.json                       │
│ Ctrl+R       │ Ratificare — ratify current template as canon   │
│ F1           │ Auxilium — help                                  │
╰──────────────┴──────────────────────────────────────────────────╯

---

## 2. Tech Stack

╭───────────────────────┬───────────┬──────────────────────────────╮
│ Tool                  │ Version   │ Justification                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Python                │ 3.11+     │ Suite standard               │
│ PyQt6                 │ 6.6+      │ ModusArcanus framework       │
│ python-docx           │ 1.1+      │ .wiz/.docx generation and    │
│                       │           │ parsing for transition mode  │
│ sqlite3               │ stdlib    │ Template registry, document  │
│                       │           │ archive, boilerplate store   │
│ json                  │ stdlib    │ .bureau.json companions,     │
│                       │           │ theme.json consumption       │
│ pathlib               │ stdlib    │ Path resolution              │
│ hashlib               │ stdlib    │ Template version hashing     │
│ markdown (or mistune) │ latest    │ .md preview rendering        │
╰───────────────────────┴───────────┴──────────────────────────────╯

No ClaudeBox. No AI integration. Offline standalone.

---

## 3. Directory Tree & Database Schema

### File Tree

```
~/ArcaCognitorium/Exocognii/
└── AestheticAuthoritarianAssociativeAlliance/
    └── DepartamentumDocumentalis/
        ├── __init__.py
        ├── __main__.py                 # Entry point
        ├── app.py                      # QApplication + main window
        ├── element_mode.py             # Element design canvas + inspector
        ├── template_mode.py            # Template assembly + section mgmt
        ├── transition_mode.py          # Document restyling engine
        ├── registry.py                 # Tag registry + template SQLite ops
        ├── archive.py                  # Document archive SQLite ops
        ├── boilerplate.py              # Boilerplate block store + refs
        ├── companion.py                # .bureau.json read/write/migrate
        ├── renderer_wiz.py             # .wiz generation via python-docx
        ├── renderer_md.py              # .md generation
        ├── preview.py                  # Live preview panel (wiz + md)
        ├── parser_wiz.py               # Parse existing .wiz → companion
        ├── parser_md.py                # Parse existing .md → companion
        ├── theme_loader.py             # theme.json consumer (shared w/ BII)
        ├── schema.py                   # TypedDict definitions
        ├── constants.py                # Defaults, element catalog, tag seeds
        ├── workers.py                  # QRunnable + WorkerSignals
        ├── elements/
        │   ├── __init__.py
        │   ├── base.py                 # DocElement ABC
        │   ├── headings.py             # H1–H6 with font/color/spacing
        │   ├── body.py                 # Body text, blockquote
        │   ├── code.py                 # Code blocks (md + wiz)
        │   ├── tables.py               # Tables with cantSplit
        │   ├── lists.py                # Bullet, numbered
        │   ├── decorative.py           # HR, section divider, colophon
        │   ├── wiz_only.py             # Title block, pull quote, deco header
        │   ├── forms.py                # Form field placeholders
        │   └── boilerplate_block.py    # Reusable block element
        ├── storage/
        │   ├── bureau.db               # SQLite (created on first run)
        │   └── companions/             # .bureau.json files
        ├── exports/                    # Paired output lands here
        └── tests/
            ├── test_element_mode.py
            ├── test_template_mode.py
            ├── test_transition.py
            ├── test_companion.py
            ├── test_registry.py
            ├── test_renderer_wiz.py
            ├── test_renderer_md.py
            └── test_integration.py
```

### Database Schema

```sql
-- ═══════════════════════════════════════════════════════════
-- TAG REGISTRY — document type definitions
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS tag_registry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tag             TEXT    NOT NULL UNIQUE,  -- e.g. "LORIDEX", "EXPOSITIO"
    display_name    TEXT    NOT NULL,         -- "Loridex Card"
    pipe_tag        TEXT    NOT NULL UNIQUE,  -- "|{LORIDEX}|"
    surfaces        TEXT    NOT NULL,         -- JSON array: [".wiz", ".md"]
    color_scheme    TEXT    NOT NULL DEFAULT 'inherited',
                                             -- 'inherited' | 'independent'
    color_overrides TEXT    DEFAULT NULL,     -- JSON dict of token overrides
    paired_output   INTEGER NOT NULL DEFAULT 1,  -- 1 = always paired
    status          TEXT    NOT NULL DEFAULT 'draft',
                                             -- 'draft' | 'canonical' | 'deprecated'
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL,
    notes           TEXT    DEFAULT ''
);

-- ═══════════════════════════════════════════════════════════
-- TEMPLATES — document structure definitions
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS templates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id          INTEGER NOT NULL REFERENCES tag_registry(id),
    name            TEXT    NOT NULL,
    surface         TEXT    NOT NULL,         -- '.wiz' | '.md'
    template_json   TEXT    NOT NULL,         -- serialized TemplateDocument
    section_schema  TEXT    NOT NULL,         -- JSON: named sections + required flags
    version         INTEGER NOT NULL DEFAULT 1,
    version_hash    TEXT    NOT NULL,         -- SHA-256 of template_json
    status          TEXT    NOT NULL DEFAULT 'draft',
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL
);

-- ═══════════════════════════════════════════════════════════
-- ELEMENTS — designed document elements
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS doc_elements (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    element_type    TEXT    NOT NULL,         -- 'heading_h1', 'body', etc.
    surface         TEXT    NOT NULL,         -- '.wiz' | '.md' | 'both'
    properties_json TEXT    NOT NULL,         -- serialized DocElementProperties
    is_locked       INTEGER NOT NULL DEFAULT 0,
    is_boilerplate  INTEGER NOT NULL DEFAULT 0,
    name            TEXT    DEFAULT '',
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL
);

-- ═══════════════════════════════════════════════════════════
-- BOILERPLATE — reusable content blocks
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS boilerplate_blocks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    content_json    TEXT    NOT NULL,         -- serialized element + content
    template_refs   TEXT    DEFAULT '[]',     -- JSON array of template IDs using it
    version         INTEGER NOT NULL DEFAULT 1,
    status          TEXT    NOT NULL DEFAULT 'active',
                                             -- 'active' | 'deprecated'
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL
);

-- ═══════════════════════════════════════════════════════════
-- DOCUMENT ARCHIVE — all documents produced
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS document_archive (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    tag_id          INTEGER REFERENCES tag_registry(id),
    template_id     INTEGER REFERENCES templates(id),
    companion_path  TEXT    NOT NULL,         -- path to .bureau.json
    wiz_path        TEXT    DEFAULT NULL,
    md_path         TEXT    DEFAULT NULL,
    version         INTEGER NOT NULL DEFAULT 1,
    status          TEXT    NOT NULL DEFAULT 'current',
                                             -- 'current' | 'archived' | 'superseded'
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL
);

-- ═══════════════════════════════════════════════════════════
-- RATIFICATION QUEUE
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS ratification_queue (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type       TEXT    NOT NULL,         -- 'tag' | 'template' | 'color_override'
    item_id         INTEGER NOT NULL,
    submitted_at    TEXT    NOT NULL,
    ratified_at     TEXT    DEFAULT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending',
                                             -- 'pending' | 'ratified' | 'rejected'
    notes           TEXT    DEFAULT ''
);
```

### .bureau.json Schema

```json
{
    "schema_version": "1.0",
    "document_name": "ModusArcanus.dux.tome",
    "tag": "DUXTOME",
    "pipe_tag": "|{DUXTOME}|",
    "template_id": 3,
    "template_version": 2,
    "template_hash": "a1b2c3d4...",
    "surfaces": [".wiz", ".md"],
    "created_at": "2026-03-29T00:00:00Z",
    "updated_at": "2026-03-29T00:00:00Z",
    "sections": [
        {
            "name": "Philosophy",
            "required": true,
            "element_refs": ["heading_h2", "body"],
            "content_hash": "e5f6g7h8..."
        }
    ],
    "boilerplate_refs": ["standard_header", "colophon_block"],
    "color_scheme": "inherited",
    "transition_history": [
        {
            "from_template": 2,
            "to_template": 3,
            "transitioned_at": "2026-03-29T00:00:00Z",
            "conflicts_resolved": 0,
            "notes": ""
        }
    ],
    "metadata": {
        "author": "LordFingers",
        "bureau_version": "1.0.0"
    }
}
```

---

## 4. Module Breakdown

╭────────────────────┬──────────────┬──────────────────────────┬──────────────────────┬──────────────────────┬──────────────────╮
│ Module             │ Stage        │ Responsibility           │ Inputs               │ Outputs              │ Dependencies     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ app.py             │ —            │ QApplication, main       │ sys.argv             │ Running window       │ all modules      │
│                    │              │ window, mode switching   │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ element_mode.py    │ Fabricatio   │ Element design canvas;   │ Surface type,        │ Locked DocElement    │ elements/*,      │
│                    │              │ element property         │ element catalog      │ instances with       │ preview          │
│                    │              │ inspector; wireframe     │                      │ configured           │                  │
│                    │              │ preview per element      │                      │ properties           │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ template_mode.py   │ Constructio  │ Section-based template   │ Locked elements      │ TemplateDocument     │ element_mode,    │
│                    │              │ assembly; section        │                      │ with section schema  │ preview,         │
│                    │              │ reordering; form         │                      │                      │ boilerplate      │
│                    │              │ skeleton authoring       │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ transition_mode.py │ Transitus    │ Load doc + companion;    │ Existing doc +       │ Restyled .wiz + .md  │ companion,       │
│                    │              │ select target template;  │ .bureau.json +       │ pair; updated        │ parser_*,        │
│                    │              │ diff view; conflict      │ target template      │ companion            │ renderer_*       │
│                    │              │ resolution; commit       │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ registry.py        │ —            │ Tag registry + template  │ SQL ops              │ Query results;       │ sqlite3          │
│                    │              │ CRUD; ratification       │                      │ registry.json        │                  │
│                    │              │ queue management         │                      │ export               │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ archive.py         │ —            │ Document archive CRUD;   │ SQL ops              │ Archive entries;     │ sqlite3          │
│                    │              │ version tracking         │                      │ file paths           │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ boilerplate.py     │ —            │ Boilerplate block store; │ Block definitions    │ Block content;       │ sqlite3          │
│                    │              │ reference tracking;      │                      │ ref update signals   │                  │
│                    │              │ cascade update on change │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ companion.py       │ —            │ .bureau.json read/write; │ File path or dict    │ CompanionDoc         │ json, pathlib    │
│                    │              │ schema validation;       │                      │ TypedDict            │                  │
│                    │              │ transition history mgmt  │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ renderer_wiz.py    │ Promulgatio  │ Generate .wiz via        │ TemplateDocument +   │ .wiz file            │ python-docx      │
│                    │              │ python-docx; apply       │ content + colors     │                      │                  │
│                    │              │ wizdoc style guide       │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ renderer_md.py     │ Promulgatio  │ Generate .md; apply      │ TemplateDocument +   │ .md file             │ —                │
│                    │              │ markdown style guide     │ content + colors     │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ parser_wiz.py      │ Transitus    │ Parse existing .wiz →    │ .wiz file path       │ Best-effort          │ python-docx      │
│                    │              │ extract structure for     │                      │ CompanionDoc with    │                  │
│                    │              │ companion generation     │                      │ conflict flags       │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ parser_md.py       │ Transitus    │ Parse existing .md →     │ .md file path        │ CompanionDoc         │ —                │
│                    │              │ extract structure         │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ preview.py         │ —            │ Live document preview;   │ TemplateDocument +   │ Rendered preview     │ renderer_*,      │
│                    │              │ .wiz = dark page,        │ active tokens        │ panel                │ theme_loader     │
│                    │              │ .md = terminal render    │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ theme_loader.py    │ —            │ theme.json consumer      │ File path            │ Tokens dict; QSS     │ json             │
│                    │              │ (identical to Bureau II) │                      │                      │                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ schema.py          │ —            │ TypedDict definitions    │ —                    │ All schema types     │ —                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ constants.py       │ —            │ Defaults, element        │ —                    │ Element catalog,     │ —                │
│                    │              │ catalog, seed tags       │                      │ seed data            │                  │
╰────────────────────┴──────────────┴──────────────────────────┴──────────────────────┴──────────────────────┴──────────────────╯

---

## 5. UI Wireframe

```
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║  ☰  ✦  DEPARTAMENTUM DOCUMENTALIS  ✦       Define! Designa! Denota!    [Thema ▼]  [?]     ║
╠═════════════════════╦════════════════════════════════════════════════════╦═════════════════════╣
║  REGISTRUM          ║  TABULA MAGNA                                     ║  PROPRIETATES       ║
║                     ║  ┌──────────────────────────────────────────────┐ ║                     ║
║  ▸ INDICIUM TYPORUM ║  │  [Element]  [Template]  [Transition]        │ ║  ── Element Mode ── ║
║  ┌────────────────┐ ║  │                                              │ ║  ELEMENTUM: H2      ║
║  │ |{EXPOSITIO}|  │ ║  │  ┌─────────────────┐  ┌──────────────────┐ │ ║  ┌─────────────────┐║
║  │  ▸ wiz template│ ║  │  │ ELEMENTA        │  │ WIREFRAME        │ │ ║  │ TYPOGRAPHIA     │║
║  │  ▸ md template │ ║  │  │                 │  │                  │ │ ║  │ Font: Varnyx    │║
║  │  ◈ canonical   │ ║  │  │ ▸ Capita        │  │ ┌──────────────┐│ │ ║  │ Size: [28pt]    │║
║  │                │ ║  │  │   H1  H2  H3   │  │ │              ││ │ ║  │ Weight: [Bold]  │║
║  │ |{DUXTOME}|    │ ║  │  │   H4  H5  H6   │  │ │  Section     ││ │ ║  │ Style: [Normal] │║
║  │  ▸ wiz template│ ║  │  │                 │  │ │  Header      ││ │ ║  │                 │║
║  │  ▸ md template │ ║  │  │ ▸ Corpus        │  │ │              ││ │ ║  │ COLORES         │║
║  │                │ ║  │  │   Body          │  │ │  Live render ││ │ ║  │ Text: [#7EC8C8] │║
║  │ |{LORIDEX}|    │ ║  │  │   Blockquote   │  │ │  of element  ││ │ ║  │ BG:   [inherit] │║
║  │  ▸ wiz (sepia) │ ║  │  │   Code Block   │  │ │  as props    ││ │ ║  │                 │║
║  │  ◈ independent │ ║  │  │                 │  │ │  change      ││ │ ║  │ SPATIUM         │║
║  │                │ ║  │  │ ▸ Tabulae       │  │ │              ││ │ ║  │ Before: [180]   │║
║  │ |{GENERAL}|    │ ║  │  │   Table         │  │ └──────────────┘│ │ ║  │ After:  [180]   │║
║  │  ▸ wiz template│ ║  │  │   Bullet List   │  │                  │ │ ║  │ Indent: [0]     │║
║  └────────────────┘ ║  │  │   Number List   │  │                  │ │ ║  │                 │║
║                     ║  │  │                 │  │                  │ │ ║  │ REGULAE         │║
║  ▸ ARCHIVUM         ║  │  │ ▸ Ornamentum    │  │                  │ │ ║  │ [✓] ALL CAPS    │║
║  ┌────────────────┐ ║  │  │   HR / Divider  │  │                  │ │ ║  │ [ ] cantSplit   │║
║  │ ModusArcanus   │ ║  │  │   Colophon      │  │                  │ │ ║  │ [ ] Boilerplate │║
║  │  .dux.tome     │ ║  │  │                 │  │                  │ │ ║  │                 │║
║  │ Expositio      │ ║  │  │ ▸ Formae (.wiz) │  │                  │ │ ║  │ [🔒 Lock]       │║
║  │  .praesidium   │ ║  │  │   Title Block  │  │                  │ │ ║  └─────────────────┘║
║  │ CogGospel      │ ║  │  │   Pull Quote   │  │                  │ │ ║                     ║
║  │  (no companion)│ ║  │  │   Form Field   │  │                  │ │ ║                     ║
║  └────────────────┘ ║  │  │   Boilerplate  │  │                  │ │ ║                     ║
║                     ║  │  └─────────────────┘  └──────────────────┘ │ ║                     ║
║                     ║  └──────────────────────────────────────────────┘ ║                     ║
╠═════════════════════╩════════════════════════════════════════════════════╩═════════════════════╣
║  SPECTRUM CHROMATICUM   Inherited: ██ BG ██ PANEL ██ GOLD ██ TEXT     Override: [+ Color]    ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  ⚙ The Department awaits your submission.                       Fabricatio · Element Mode    ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝
```

### Wireframe Legend

╭────────────────────────┬─────────────────────────────────────────────────╮
│ Element                │ Description                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ TopBar                 │ QFrame, 52px. App title with motto, theme       │
│                        │ selector, help button.                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ REGISTRUM (left)       │ Two collapsible sections. INDICIUM TYPORUM:     │
│                        │ tag registry tree — each tag expands to show    │
│                        │ associated templates, surface types, color      │
│                        │ scheme status (inherited/independent), canon    │
│                        │ status. ARCHIVUM: produced documents with       │
│                        │ companion JSON status indicators. Filterable    │
│                        │ by tag.                                         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ TABULA MAGNA (centre)  │ Three mode tabs at top: Element, Template,      │
│                        │ Transition. Element Mode: split — left has      │
│                        │ element catalog grouped by type (Capita,        │
│                        │ Corpus, Tabulae, Ornamentum, Formae); right     │
│                        │ has live wireframe preview of selected element  │
│                        │ that updates as properties change. Template     │
│                        │ Mode: full document canvas with named sections  │
│                        │ arranged vertically, live document preview.     │
│                        │ Transition Mode: side-by-side diff view —      │
│                        │ current on left, new template on right.         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ PROPRIETATES (right)   │ Context-sensitive inspector. In Element Mode:   │
│                        │ TYPOGRAPHIA (font, size, weight, style),        │
│                        │ COLORES (text/bg from active palette or         │
│                        │ override), SPATIUM (before/after spacing,       │
│                        │ indent), REGULAE (ALL CAPS, cantSplit,          │
│                        │ boilerplate flag), Lock button. In Template     │
│                        │ Mode: section name, required flag, element      │
│                        │ refs, notes. In Transition Mode: conflict       │
│                        │ details per flagged element.                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ SPECTRUM CHROMATICUM   │ Bottom color bar. Shows active palette tokens   │
│ (bottom bar)           │ from theme.json or tag-level overrides. Click   │
│                        │ any swatch to assign to selected element.       │
│                        │ [+ Color] opens override dialog for per-tag     │
│                        │ independent colors. Independent schemes         │
│                        │ flagged with ◈.                                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ StatusBar              │ QFrame, 28px. Left: declarative status.         │
│                        │ Right: current stage + mode indicator.          │
╰────────────────────────┴─────────────────────────────────────────────────╯

---

## 6. Data Flow

### Path (a) — Happy path: design elements → build template → export paired output

```
1.  Wizard opens Bureau III, selects Element Mode
2.  Wizard chooses surface: .wiz
3.  Element catalog populates with .wiz elements (all .md elements
    plus Title Block, Pull Quote, Decorative Header, Form Field,
    Boilerplate Block)
4.  Wizard clicks "H2" in Capita group
5.  element_mode.py creates DocElement with default H2 properties
    from wizdoc-style-guide: Varnyx Regular, 28pt, Bold, #7EC8C8
6.  Wireframe preview renders a live H2 heading sample
7.  Wizard adjusts spacing in PROPRIETATES: before=240, after=180
8.  Wireframe updates in real-time
9.  Wizard clicks [🔒 Lock] — element is finalized
10. Wizard repeats for Body, Code Block, Table, Section Divider
11. Wizard switches to Template Mode (Ctrl+2)
12. template_mode.py presents section assembly canvas
13. Wizard creates sections: "Philosophy", "Colour System",
    "Typography", "Widget Patterns"
14. Wizard drags locked elements into each section
15. Wizard marks "Philosophy" as required, others as optional
16. Wizard defines recurring header (ModusArcanus file header
    block) and footer (colophon)
17. Live preview renders full document in dark-page .wiz style
18. Wizard presses Ctrl+S — template saved to templates table
19. Wizard assigns template to |{DUXTOME}| tag
20. Wizard presses Ctrl+R — template enters ratification queue
21. Wizard ratifies → template status = 'canonical'
22. Wizard presses Ctrl+E — export:
    a. renderer_wiz.py generates .wiz file via python-docx
    b. renderer_md.py generates .md file
    c. companion.py generates .bureau.json
    d. All three written to exports/
    e. Archive entry created in document_archive table
    f. Status: "✦  Paired output sealed: ModusArcanus.dux.tome"
```

### Path (b) — Transition: restyle legacy document

```
1.  Wizard switches to Transition Mode (Ctrl+3)
2.  Wizard loads existing document: ModusArcanus.dux.tome.md
3.  transition_mode.py checks for .bureau.json companion
4.  No companion found — legacy document
5.  parser_md.py parses the .md file:
    a. Identifies heading hierarchy
    b. Extracts section boundaries
    c. Detects code blocks, tables, lists
    d. Generates best-effort CompanionDoc
    e. Flags ambiguities: "Section 'IV. Widget Patterns' —
       contains mixed heading levels. Manual review required."
6.  Best-effort companion shown to Wizard for review
7.  Wizard corrects any misidentified sections
8.  Wizard selects target template: |{DUXTOME}| canonical .md
9.  transition_mode.py produces diff view:
    a. Left panel: current document rendering
    b. Right panel: preview under new template
    c. Conflict highlights in C_CRIMSON:
       - "Source has 4 H4 headings; target template expects H3"
       - "Source code blocks use no specified language tag"
10. Wizard resolves conflicts via inspector panel
11. Wizard commits transition:
    a. renderer_md.py produces new .md under target template
    b. companion.py writes .bureau.json with transition history
    c. Original .md moved to archive (status = 'superseded')
    d. New .md + companion placed in exports/
    e. Status: "✦  Transition complete. 2 conflicts resolved."
```

### Path (c) — Boilerplate update cascades to templates

```
1.  Wizard opens Element Mode
2.  Wizard edits the "standard_header" boilerplate block:
    changes the ModusArcanus header ornament characters
3.  boilerplate.py detects this block has template_refs:
    [template_id=2, template_id=5, template_id=8]
4.  boilerplate.py emits boilerplate_updated signal
5.  Notification: "⌬  Boilerplate 'standard_header' updated.
    3 templates reference this block."
6.  Wizard views affected templates list
7.  For each affected template:
    a. Template is NOT auto-modified — the Bureau is thorough
    b. Template marked with "pending boilerplate sync" flag
    c. When Wizard opens any affected template, the updated
       boilerplate renders in place. Wizard confirms.
8.  No document is re-exported automatically — the Wizard
    decides when to re-render affected documents
```

---

## 7. Code Stubs

### schema.py — Bureau Type Definitions

```python
"""Type definitions for the Bureau's document authority system."""

from typing import TypedDict, Optional


class DocElementProperties(TypedDict, total=False):
    """Configurable properties for a document element."""
    # Typography
    font_family: str        # e.g. "Varnyx Regular", "VL Gothic"
    font_size: int          # pt
    font_weight: str        # "normal" | "bold"
    font_style: str         # "normal" | "italic"
    text_transform: str     # "none" | "uppercase"
    letter_spacing: int     # px (for micro-label pattern)

    # Colors (hex or token name)
    text_color: str         # Hex or token ref
    bg_color: str           # Hex, token ref, or "inherit"

    # Spacing
    spacing_before: int     # pt
    spacing_after: int      # pt
    indent: int             # pt
    alignment: str          # "left" | "center" | "right" | "justify"

    # Rules
    all_caps: bool
    cant_split: bool        # Tables only — prevent page break
    is_boilerplate: bool    # Marks as reusable block

    # Surface-specific (.wiz only)
    page_break_before: bool
    border_bottom: bool     # For section dividers
    decorative_style: str   # "rule" | "ornament" | "colophon"


class DocElement(TypedDict):
    """A designed document element."""
    id: str                 # UUID4
    element_type: str       # "heading_h1" .. "heading_h6", "body",
                            # "code_block", "table", "bullet_list",
                            # "numbered_list", "hr", "blockquote",
                            # "title_block", "section_divider",
                            # "pull_quote", "deco_header", "colophon",
                            # "form_field", "boilerplate_block"
    surface: str            # ".wiz" | ".md" | "both"
    properties: DocElementProperties
    is_locked: bool
    name: str               # Human label


class SectionDef(TypedDict):
    """A named section in a template."""
    name: str               # e.g. "Philosophy", "Colour System"
    required: bool
    element_refs: list[str] # List of DocElement IDs
    sort_order: int
    notes: str


class TemplateDocument(TypedDict):
    """A complete template definition."""
    schema_version: str     # "1.0"
    tag: str                # "DUXTOME", "EXPOSITIO", etc.
    surface: str            # ".wiz" | ".md"
    name: str
    sections: list[SectionDef]
    header_element_id: Optional[str]   # Recurring header
    footer_element_id: Optional[str]   # Recurring footer
    boilerplate_refs: list[str]        # Boilerplate block IDs
    color_scheme: str       # "inherited" | "independent"
    color_overrides: Optional[dict]    # Token overrides if independent
    metadata: dict


class TransitionEntry(TypedDict):
    """A single entry in a document's transition history."""
    from_template_id: int
    to_template_id: int
    transitioned_at: str    # ISO 8601
    conflicts_resolved: int
    notes: str


class CompanionDoc(TypedDict):
    """The .bureau.json companion file schema."""
    schema_version: str
    document_name: str
    tag: str
    pipe_tag: str
    template_id: int
    template_version: int
    template_hash: str
    surfaces: list[str]
    created_at: str
    updated_at: str
    sections: list[dict]    # Name, required, element_refs, content_hash
    boilerplate_refs: list[str]
    color_scheme: str
    transition_history: list[TransitionEntry]
    metadata: dict


class TagRegistryEntry(TypedDict):
    """A document type tag in the registry."""
    tag: str                # "LORIDEX"
    display_name: str       # "Loridex Card"
    pipe_tag: str           # "|{LORIDEX}|"
    surfaces: list[str]     # [".wiz", ".md"]
    color_scheme: str       # "inherited" | "independent"
    color_overrides: Optional[dict]
    paired_output: bool
    status: str             # "draft" | "canonical" | "deprecated"
```

### companion.py — .bureau.json Manager

```python
"""Read, write, and validate .bureau.json companion files."""

import json
from pathlib import Path
from datetime import datetime, timezone


def create_companion(document_name: str, tag: str,
                     template_id: int, template_version: int,
                     template_hash: str, sections: list[dict],
                     surface: str = '.wiz',
                     color_scheme: str = 'inherited') -> dict:
    """Create a new .bureau.json companion dict."""
    ...


def load_companion(path: Path) -> dict:
    """Load and validate a .bureau.json file.

    Raises ValueError if schema_version is unsupported.
    Raises FileNotFoundError if path does not exist.
    """
    ...


def save_companion(companion: dict, path: Path) -> None:
    """Write companion dict to .bureau.json file."""
    ...


def add_transition_entry(companion: dict,
                         from_template: int, to_template: int,
                         conflicts: int = 0,
                         notes: str = '') -> dict:
    """Append a transition history entry. Returns updated companion."""
    ...


def validate_companion(data: dict) -> list[str]:
    """Validate companion against CompanionDoc schema.

    Returns list of error strings. Empty = valid.
    """
    ...
```

### renderer_wiz.py — .wiz Generator

```python
"""Generate .wiz (docx) files from template definitions."""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path


def render_wiz(template: dict, content: dict,
               tokens: dict, output_path: Path) -> None:
    """Generate a .wiz file from a template and content.

    Applies wizdoc-style-guide typography:
    - Title: Ebon Sigil, 64pt, Bold, Centred
    - H1: Varnyx Regular, 36pt, Bold, ALL CAPS
    - H2: Varnyx Regular, 28pt, Bold
    - Body: VL Gothic, 10pt, Regular
    - Code: Courier New, 10pt, teal on amethyst

    Colors from tokens dict (theme.json or tag overrides).
    All tables use cantSplit on rows.
    Output extension is .wiz not .docx.
    """
    ...


def _apply_heading_style(paragraph, level: int,
                         properties: dict, tokens: dict) -> None:
    """Apply heading typography from element properties."""
    ...


def _apply_body_style(paragraph, properties: dict,
                      tokens: dict) -> None:
    """Apply body text typography from element properties."""
    ...


def _create_table(doc, rows: int, cols: int,
                  properties: dict, tokens: dict):
    """Create a styled table with cantSplit on all rows."""
    ...
```

### renderer_md.py — .md Generator

```python
"""Generate .md files from template definitions."""

from pathlib import Path


def render_md(template: dict, content: dict,
              output_path: Path) -> None:
    """Generate a .md file from a template and content.

    Applies markdown-style-guide conventions:
    - Box-drawing character tables, not pipe tables
    - 80 character line width
    - Heading hierarchy matching template sections
    - Code blocks with language tags
    """
    ...


def _render_heading(level: int, text: str) -> str:
    """Render a markdown heading at the specified level."""
    ...


def _render_table(headers: list[str],
                  rows: list[list[str]]) -> str:
    """Render a box-drawing character table.

    Uses ╭─┬─╮ / ├┄┼┄┤ / ╰─┴─╯ characters.
    Calculates column widths from content.
    """
    ...
```

### transition_mode.py — Document Restyling Engine

```python
"""Transition Mode — restyle documents against new templates."""

from PyQt6.QtWidgets import QWidget, QSplitter
from PyQt6.QtCore import pyqtSignal


class TransitionEngine(QWidget):
    """Side-by-side diff view for document template transitions."""

    transition_complete = pyqtSignal(str)  # document name

    def load_document(self, doc_path: str,
                      companion_path: str = None) -> None:
        """Load a document for transition.

        If companion_path is None, attempt auto-discovery:
        1. Look for {doc_name}.bureau.json alongside the doc
        2. If not found, parse the document to generate a
           best-effort companion (Wizard reviews before commit)
        """
        ...

    def set_target_template(self, template_id: int) -> None:
        """Select the target template for restyling."""
        ...

    def compute_diff(self) -> list[dict]:
        """Compare source structure against target template.

        Returns list of conflict dicts:
        {
            'source_element': str,
            'target_element': str,
            'conflict_type': str,  # 'missing' | 'type_mismatch' | 'level_mismatch'
            'description': str,
            'resolved': bool,
            'resolution': str | None
        }
        """
        ...

    def resolve_conflict(self, conflict_index: int,
                         resolution: str) -> None:
        """Apply a Wizard resolution to a specific conflict."""
        ...

    def commit_transition(self) -> None:
        """Execute the transition.

        1. Render new .wiz and/or .md under target template
        2. Generate/update .bureau.json with transition entry
        3. Archive original (status = 'superseded')
        4. Write new files to exports/
        """
        ...
```

### constants.py — Element Catalog & Defaults

```python
"""Element catalog, seed tags, and Bureau defaults."""


# ═══════════════════════════════════════════════════════════
# ELEMENT CATALOG — grouped by UI category
# ═══════════════════════════════════════════════════════════

ELEMENT_CATALOG = {
    'capita': {
        'label': 'Capita',
        'description': 'Heading hierarchy',
        'elements': [
            'heading_h1', 'heading_h2', 'heading_h3',
            'heading_h4', 'heading_h5', 'heading_h6',
        ],
        'surface': 'both',
    },
    'corpus': {
        'label': 'Corpus',
        'description': 'Body text elements',
        'elements': ['body', 'blockquote', 'code_block'],
        'surface': 'both',
    },
    'tabulae': {
        'label': 'Tabulae',
        'description': 'Tables and lists',
        'elements': ['table', 'bullet_list', 'numbered_list'],
        'surface': 'both',
    },
    'ornamentum': {
        'label': 'Ornamentum',
        'description': 'Decorative and structural',
        'elements': ['hr', 'section_divider', 'colophon'],
        'surface': 'both',
    },
    'formae': {
        'label': 'Formae',
        'description': 'WizDoc-only structural elements',
        'elements': [
            'title_block', 'pull_quote', 'deco_header',
            'form_field', 'boilerplate_block',
        ],
        'surface': '.wiz',
    },
}


# ═══════════════════════════════════════════════════════════
# SEED TAGS — pre-populated on first run
# ═══════════════════════════════════════════════════════════

SEED_TAGS = [
    {
        'tag': 'EXPOSITIO',
        'display_name': 'Expositio',
        'pipe_tag': '|{EXPOSITIO}|',
        'surfaces': ['.wiz', '.md'],
        'color_scheme': 'inherited',
        'paired_output': True,
    },
    {
        'tag': 'DUXTOME',
        'display_name': 'Dux Tome',
        'pipe_tag': '|{DUXTOME}|',
        'surfaces': ['.wiz', '.md'],
        'color_scheme': 'inherited',
        'paired_output': True,
    },
    {
        'tag': 'LORIDEX',
        'display_name': 'Loridex Card',
        'pipe_tag': '|{LORIDEX}|',
        'surfaces': ['.wiz', '.md'],
        'color_scheme': 'independent',
        'paired_output': True,
    },
    {
        'tag': 'GENERAL',
        'display_name': 'General Document',
        'pipe_tag': '|{GENERAL}|',
        'surfaces': ['.wiz', '.md'],
        'color_scheme': 'inherited',
        'paired_output': True,
    },
]


APP_TITLE = '✦  DEPARTAMENTUM DOCUMENTALIS  ✦'
APP_SUBTITLE = 'Define! Designa! Denota! Discede!'
BUREAU_FULL = 'The Department of Documented Design Definitives'
BUREAU_LATIN = 'Departamentum Documentalis'
```

---

## 8. Error Handling

╭─────────────────────┬──────────────────────────┬─────────────────────────────────╮
│ Module              │ Error                    │ Strategy                        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ app.py              │ python-docx import fail  │ Error dialog: "python-docx not  │
│                     │                          │ found." .wiz rendering disabled │
│                     │                          │ — .md mode still functional.    │
│                     │                          │ App does not exit.              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ registry.py         │ DB init failure          │ Attempt directory creation.     │
│                     │                          │ If fails: error dialog with     │
│                     │                          │ path. App continues without     │
│                     │                          │ persistence — design only.      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ parser_wiz.py       │ .wiz parse produces      │ Flag each ambiguity with        │
│                     │ ambiguous structure       │ specific description. Present   │
│                     │                          │ best-effort companion to        │
│                     │                          │ Wizard. Nothing commits until   │
│                     │                          │ Wizard confirms. Conflicts      │
│                     │                          │ highlighted in C_CRIMSON.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ parser_wiz.py       │ .wiz file is corrupt     │ Catch python-docx exceptions.   │
│                     │ or not a valid docx      │ Error dialog: "⌬  Document     │
│                     │                          │ could not be parsed." No        │
│                     │                          │ companion generated.            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ renderer_wiz.py     │ Font not found on system │ Fall back to Georgia (always    │
│                     │ (Varnyx, Ebon Sigil)     │ available). Log warning with    │
│                     │                          │ missing font name. Status:      │
│                     │                          │ "⌬  Font substitution active." │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ renderer_md.py      │ Box-drawing table column │ Fall back to pipe-table format  │
│                     │ calculation overflow     │ for that table. Log warning.    │
│                     │ (extremely wide content) │ Document still generates.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ transition_mode.py  │ Source document has no    │ Fall back to parser. Generate   │
│                     │ companion and parser     │ minimal companion with          │
│                     │ cannot determine         │ unclassified sections. Wizard   │
│                     │ structure                │ must manually map content to    │
│                     │                          │ template sections.              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ boilerplate.py      │ Referenced boilerplate    │ Template renders placeholder    │
│                     │ block deleted/missing    │ text: "[Missing boilerplate:    │
│                     │                          │ {name}]". Status warning.       │
│                     │                          │ Export still proceeds —          │
│                     │                          │ placeholder is visible.         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ companion.py        │ .bureau.json schema      │ Validate on load. If version    │
│                     │ version mismatch         │ is older: attempt migration.    │
│                     │                          │ If newer: refuse load with      │
│                     │                          │ version error. Migration adds   │
│                     │                          │ missing fields with defaults.   │
╰─────────────────────┴──────────────────────────┴─────────────────────────────────╯

---

## 9. Setup & Testing

### requirements.txt

```
PyQt6>=6.6.0
python-docx>=1.1.0
```

### Install & Run

```bash
cd ~/ArcaCognitorium/Exocognii/AestheticAuthoritarianAssociativeAlliance/DepartamentumDocumentalis

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m DepartamentumDocumentalis
```

### Unit Tests

**test_element_mode.py** — Create a heading_h2 DocElement. Assert
default properties match wizdoc-style-guide (Varnyx, 28pt, Bold,
#7EC8C8). Lock it. Assert is_locked is True. Attempt to modify
properties — assert modification rejected.

**test_template_mode.py** — Create a TemplateDocument with two
sections. Assert sections are ordered. Add a locked element to
section 1. Serialize. Assert template_json is valid JSON. Add a
required section. Assert section_schema includes required flag.

**test_transition.py** — Create a source CompanionDoc and a target
TemplateDocument with different section structures. Call
compute_diff(). Assert conflicts list is non-empty. Assert
conflict_type is 'missing' for sections in source not in target.

**test_companion.py** — Create a companion dict via
create_companion(). Assert schema_version is "1.0". Save to temp
file. Load back. Assert all fields match. Add a transition entry.
Assert transition_history length is 1.

**test_registry.py** — Create in-memory DB. Insert a seed tag.
Assert pipe_tag is "|{EXPOSITIO}|". Insert a template referencing
the tag. Assert tag_id matches. Attempt duplicate pipe_tag — assert
IntegrityError.

**test_renderer_wiz.py** — Render a minimal template (one H1 +
body) to .wiz. Assert file exists. Open with python-docx. Assert
first paragraph style is heading. Assert font matches config.

**test_renderer_md.py** — Render a minimal template to .md. Assert
file exists. Read contents. Assert first line starts with "#".
Assert box-drawing table characters present if template includes
a table.

### Integration Test

**test_integration.py** — End-to-end:

```
1.  Create tag "TEST" with pipe_tag "|{TEST}|"
2.  Design 3 elements: heading_h1, body, table
3.  Lock all elements
4.  Create template with 2 sections using the elements
5.  Save template to in-memory registry
6.  Assign template to tag "TEST"
7.  Render .wiz to temp dir → assert file exists
8.  Render .md to temp dir → assert file exists
9.  Generate .bureau.json → assert valid CompanionDoc
10. Load companion back → assert template_id matches
11. Create second template (target) with 3 sections
12. Run compute_diff() between companion and target
13. Assert conflict detected (section count mismatch)
14. Resolve conflict, commit transition
15. Assert transition_history length is 1
16. Assert original archived (status = 'superseded')
```

---

## 10. Packaging

### Desktop File

```ini
[Desktop Entry]
Name=Departamentum Documentalis
Comment=The Department of Documented Design Definitives — document authority
Exec=bash -c "cd $HOME/ArcaCognitorium && python -m Exocognii.AestheticAuthoritarianAssociativeAlliance.DepartamentumDocumentalis"
Icon=departamentum-documentalis
Terminal=false
Type=Application
Categories=Development;Office;
Keywords=document;template;style;bureau;arcane;
StartupWMClass=departamentum-documentalis
```

Place at: `~/.local/share/applications/DepartamentumDocumentalis.desktop`

Icon at: `~/.local/share/icons/departamentum-documentalis.png`

Launch script:
`~/ArcaCognitorium/launch_departamentum_documentalis.sh`

```bash
#!/bin/bash
cd ~/ArcaCognitorium/Exocognii/AestheticAuthoritarianAssociativeAlliance/DepartamentumDocumentalis
source .venv/bin/activate
python -m DepartamentumDocumentalis
```

---

## 11. Extensibility

╭───────────────────────────┬──────────────────────────────┬──────────────────────────────────╮
│ Feature                   │ User Value                   │ Implementation Approach           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Batch Transition          │ Restyle an entire folder of  │ Queue-based worker. Wizard       │
│                           │ documents against a new      │ selects folder + target template │
│                           │ template in one pass         │ + conflict strategy (skip /      │
│                           │                              │ auto-resolve / flag). Worker     │
│                           │                              │ processes each doc, produces     │
│                           │                              │ report at end.                   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ AI Content Authoring      │ ClaudeBox-powered content    │ Council entity fills form        │
│                           │ generation within form       │ skeleton fields based on         │
│                           │ skeletons                    │ context prompt. Wizard reviews   │
│                           │                              │ and commits. Content respects    │
│                           │                              │ template structure.              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Template Marketplace      │ Import/export template       │ Templates serialized as self-    │
│                           │ packages between Bureau      │ contained .dept archives (JSON   │
│                           │ instances                    │ + element defs + sample render). │
│                           │                              │ Import validates against local   │
│                           │                              │ tag registry.                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Registry Broadcast        │ When a tag or template is    │ ZMQ PUB socket. Suite apps       │
│                           │ ratified, notify all suite   │ subscribe to registry changes.   │
│                           │ apps so they can update      │ Payload: tag_id + status change. │
│                           │ their tag references         │ v1 stubs without binding.        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Detritus Pipeline Link    │ Deprecated templates and     │ When a template or boilerplate   │
│                           │ boilerplate blocks feed      │ is deprecated, emit to Detritus  │
│                           │ into the sediment layer      │ Pipeline intake. Sediment layer  │
│                           │                              │ compacts into historical record. │
│                           │                              │ Nothing is truly deleted.        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Document Search           │ Full-text search across all  │ SQLite FTS5 extension on         │
│                           │ archived documents           │ document_archive content. Query   │
│                           │                              │ surface in the Archivum panel.   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Chromatic Covenant Link   │ Commit ratified templates    │ Git subprocess: stage template   │
│                           │ and registry.json to the     │ + registry exports, commit with  │
│                           │ ArcaCognitorium repository   │ "[DEPT] {tag}: {template_name}", │
│                           │                              │ push to origin/main.             │
╰───────────────────────────┴──────────────────────────────┴──────────────────────────────────╯

---

## Appendix: Suite Manifest Entry

```json
{
    "id": "departamentum_documentalis",
    "name": "Departamentum Documentalis",
    "bureau": "Departamentum Documentalis",
    "alliance": "A4",
    "path": "Exocognii/AestheticAuthoritarianAssociativeAlliance/DepartamentumDocumentalis",
    "entry": "__main__.py",
    "version": "1.0.0",
    "status": "development",
    "dependencies": ["auctoritas_spectralis"]
}
```

---

*⟁*

*Ordo Discordia, Cosmos Inania*

*IdeaForge · Bureau III · Departamentum Documentalis · ＭＭＸＸＶＩ*
