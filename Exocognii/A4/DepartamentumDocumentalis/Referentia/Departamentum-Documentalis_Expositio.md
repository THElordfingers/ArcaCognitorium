# DEPARTAMENTUM DOCUMENTALIS
### Expositio · v1.0
#### Bureau III · Triumviratus Aestheticus Imperialis · A4 Alliance
#### *Define! Designa! Denota! Discede!*

---

## I. Identity

```
Name     ·  Departamentum Documentalis
Version  ·  1.0
Bureau   ·  III — Triumviratus Aestheticus Imperialis
Port     ·  8733
Venv     ·  venv-DOC
Status   ·  Active Development — functional v1.0
```

The Template Sovereignty Engine. Governs all document standards across the
Exocognii suite via a SQLite-backed Forma registry and the TEXTUS MANDATUM
ORDINATIO decree table. Composes documents against those mandated standards
via both a PyQt6 authorship UI and a FastAPI /compose endpoint called by
peer applications in the suite.

---

## II. Purpose

**Problem Statement**

Document standards in a multi-application suite drift. Each application
invents its own formats, fields, and conventions independently. Over time,
no two documents of the same type look alike, reference the same fields, or
carry the same metadata. Retroactive correction is expensive and manual.

**Motivation**

The suite requires a single sovereign source of truth for what a document
of any given type must contain, how it must be structured, and which
Chromaticum theme governs its appearance. That source of truth must be
enforceable — not advisory.

**Intended Outcome**

Any application in the suite can call POST /compose with a doc_type and
content payload and receive correctly structured, consistently formatted
output files. When a standard changes, prior documents are retroactively
migrated and stamped VERSIO PRIOR. Nothing is lost. Everything is traceable.

**Anti-Purpose**

Departamentum Documentalis is not a general-purpose word processor. It does
not offer freeform layout. It does not manage images, diagrams, or rich
media. It governs document constitutions and composes against them.

---

## III. Audience

**Primary User** — LordFingers. Interacts through the PyQt6 authorship UI:
authoring Formae, composing documents in the Scriptorium, reviewing the
Archive, and managing the Mandate Bench.

**Secondary Users** — Peer Exocognii applications calling /compose
programmatically. These callers supply a doc_type and content_data payload
and receive files back. No knowledge of Forma internals required.

**Assumed Knowledge** — Familiarity with the Exocognii suite, the A4 bureau
structure, and the Cogniverse naming register.

---

## IV. Design Philosophy

**Sovereignty Over Flexibility** — The TEXTUS MANDATUM ORDINATIO is law.
Calling applications supply content into a predetermined schema. They do
not decide structure.

**Nothing Is Lost** — The Propagatio Engine never deletes. Superseded
records are stamped VERSIO PRIOR. Orphaned content is preserved as ORPHANED
CORPUS. The Archive is append-only in intent.

**Graceful Degradation** — Bureau I unavailability does not gate DD function.
Chromaticum queries fall back to cache, then to hardcoded defaults. NUNTIUS
unavailability is silently swallowed.

**Separation of Concerns** — FastAPI and PyQt6 share a SQLite WAL database
but operate on independent threads. All blocking operations use QRunnable
workers. The UI thread never blocks.

---

## V. Technical Concept

**Mental Model** — A Forma is a document constitution: it defines fields,
their types (FIXED or PERMISSIVE), their order, and the Chromaticum. The
TEXTUS MANDATUM ORDINATIO maps each doc_type to exactly one mandated Forma.
Composition fills a Forma's field schema with content and emits output files.

**Core Abstractions**

```
Forma                     Document constitution — fields, types, targets,
                          Chromaticum binding.

Forma Field               One field. FIXED (value set at definition,
                          immutable at compose time) or PERMISSIVE
                          (author-supplied).

TEXTUS MANDATUM ORDINATIO One active mandate per doc_type.

Scriptura Ordinata        Pipe-tag markup: |FIELD:name|, |FIXED:name|,
                          |SECTION:name|, |INJECT:zone|, |END|.

Archive                   Full production history. Every emitted document
                          receives a record with status, theme_snapshot,
                          output paths.

Propagatio Engine         Retroactive migration system. Triggered by mandate
                          changes.

Involucrum                Observation payload emitted to NUNTIUS.
```

**Data Flow**

```
Caller → doc_type + content_data
→ resolve mandated Forma
→ validate required PERMISSIVE fields
→ resolve FIXED values from Forma
→ build Scriptura Ordinata source
→ parse to AST
→ render to target formats
→ snapshot Chromaticum from Bureau I
→ write archive record
→ emit Involucrum
```

**Key Technical Decisions**

- FastAPI runs on a dedicated daemon thread with its own asyncio event loop,
  preventing conflict with Qt's event loop.
- SQLite WAL mode allows concurrent reads and writes across threads.
- The Scriptura Ordinata parser never raises — malformed input produces
  ParseError entries, not exceptions.
- Node.js docx shell-out uses a temp JSON intermediate rather than piped
  stdin.

---

## VI. Functional Scope

**Core Capabilities**

- Forma Registry — create, browse, filter, manage document constitutions.
- Forma Editor — field schemas, FIXED/PERMISSIVE, Chromaticum, output
  targets, version tracking.
- Scriptorium — Scriptura Ordinata editor, 400ms live .md preview, emit
  to .md / .wiz / .pdf.
- Document Archive — full production history, status vocabulary,
  theme_snapshot.
- Propagatio Engine — retroactive migration queue, batch and single-item.
- Mandate Bench — TEXTUS MANDATUM ORDINATIO governance, SWAP, history log.
- FastAPI on port 8733 — /compose, /forma/mandated/{doc_type}, /archive,
  /archive/register, /chromatica.

**Explicit Exclusions**

- General-purpose word processing or freeform layout.
- Image, diagram, or rich media composition.
- Multi-user or network deployment.
- NUNTIUS routing (v1 direct; migration deferred to v1.1).
- Exvacua Loricum lore tagging (fields reserved, unpopulated).
- .pdf rendering beyond Pandoc shell-out.

**Future Scope**

- NUNTIUS routing migration.
- Exvacua Loricum lore tagging integration.
- .wiz live preview in Scriptorium.
- Forma diff viewer.
- Batch Scriptorium composition.
- Mandate Bench export as .md snapshot.

---

## VII. Constraints & Context

**Technical Constraints**

- Python 3.11 · PyQt6 · FastAPI · SQLite WAL · Debian Trixie / KDE Plasma 6
- Node.js required for .wiz emission.
- Pandoc required for .pdf emission.
- Bureau I on port 8731 for Chromaticum resolution; graceful fallback.
- NUNTIUS on port 8730 for Involucrum emission; graceful fallback.

**External Dependencies**

```
Auctoritas Spectralis (Bureau I)  ·  port 8731  ·  Chromaticum
NUNTIUS                           ·  port 8730  ·  Involucrum routing
Node.js docx library              ·  .wiz generation
Pandoc                            ·  .pdf generation
```

---

## VIII. Success Criteria

**Functional Success**

- POST /compose with valid doc_type returns .md output with correct fields.
- A Forma can be created, mandated, and composed against without error.
- Mandate SWAP triggers propagatio queue population for CURRENT records.
- Bureau I unavailability does not prevent document emission.

**Failure Conditions**

- UI thread blocks on any I/O operation.
- Document emitted silently with missing REQUIRED PERMISSIVE fields.
- Archive record deleted rather than stamped VERSIO PRIOR.
- NUNTIUS unavailability causes an unhandled exception.

---

## IX. Glossary

```
╭──────────────────────────────┬───────────────────────────────────────────╮
│ Term                         │ Definition                                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Forma                        │ Document constitution. Field schema,      │
│                              │ output targets, Chromaticum.              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ FIXED field                  │ Value set at Forma definition. Immutable  │
│                              │ at compose time.                          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ PERMISSIVE field             │ Value supplied by author or caller.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ TEXTUS MANDATUM ORDINATIO    │ The decree table. One mandate per         │
│                              │ doc_type.                                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Scriptura Ordinata           │ Pipe-tag markup language for document     │
│                              │ authorship.                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ VERSIO PRIOR                 │ Archive status for a superseded record.   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ ORPHANED CORPUS              │ Content present in a prior document but   │
│                              │ absent from the new Forma. Preserved.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ theme_snapshot               │ 10-token Chromaticum values captured at   │
│                              │ emit time. Immutable after capture.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Involucrum                   │ Observation payload emitted to NUNTIUS.   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ Propagatio Engine            │ Retroactive migration system.             │
╰──────────────────────────────┴───────────────────────────────────────────╯
```

---

## X. Revision Notes

```
╭────────────┬───────────────────────────────┬──────────────────────────────╮
│ Date       │ Change                        │ Reason                       │
├┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ 2026-04-09 │ v1.0 initial Expositio.       │ Application reaches          │
│            │                               │ functional launch state.     │
╰────────────┴───────────────────────────────┴──────────────────────────────╯
```

---

*⟁ Ordo Discordia, Cosmos Inania*
