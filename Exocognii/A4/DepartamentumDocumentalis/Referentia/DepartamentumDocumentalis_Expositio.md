# Departamentum Documentalis — Expositio

> Bureau III · Departamentum Documentalis
> Aesthetic Authoritarian Associative Alliance (A4)
> Ｄｅｆｉｎｅ! Ｄｅｓｉｇｎａ! Ｄｅｎｏｔａ! Ｄｉｓｃｅｄｅ!

---

## I. Identity

- **Name:** Departamentum Documentalis — The Department of
  Documented Design Definitives
- **Version:** 1.0.0
- **Tagline:** Define! Design! Denote! Leave!
- **Classification:** PyQt6 desktop document composition
  tool with CLI backend.
- **Status:** Active development. Core pipeline functional.
  28/28 tests pass. Both emitters verified.
- **Bureau Seal:** Departamentum Documentalis
- **Alliance:** A4 — Triumviratus Aestheticus Imperialis

---

## II. Purpose

### Problem Statement

Every document in the Cogniverse — Expositios, dux tomes,
build docs, palette cards — is currently handcrafted via
one-off Node.js or Python scripts. There is no reusable
template system, no persistent style authority, no way to
compose a document from a single source and emit it in both
`.wiz` and `.md` formats simultaneously.

### Motivation

Bureau III centralizes document authority. One tool
composes, previews, and emits all Cogniverse documents. The
Wizard writes in a native pipe-tag format (`.bureau`),
sees a live styled preview, and gets paired output in both
formats from a single source. Templates for every known
document type provide scaffolding.

### Intended Outcome

A `.bureau` file as the single source of truth for any
Cogniverse document. One command or one button produces
both the art-form `.wiz` and the readable `.md`, plus a
`.bureau.json` companion recording provenance.

### Anti-Purpose

This is not a word processor. It does not handle page
layout, image placement, or print production. It does not
replace Bureau I (color) or Bureau II (widgets). It governs
document content and styling.

---

## III. Audience

- **Primary:** The Wizard (LordFingers) — sole operator.
- **Secondary:** The Builder, producing documentation for
  apps. Any future Cogniverse contributor writing docs.
- **Assumed Knowledge:** Familiarity with the pipe-tag
  syntax (learnable in minutes) and the Cogniverse
  document types.

---

## IV. Design Philosophy

- Single source, dual output — one `.bureau` file produces
  both `.wiz` and `.md`.
- Art-form documents — `.wiz` output uses the full wizdoc
  style guide aesthetic (dark bg, gold/teal/violet
  typography, box-drawing tables).
- Template-driven — every known doc type has a built-in
  skeleton.
- GUI for composition, CLI for automation — the same
  parser and emitters serve both interfaces.
- Theme inheritance — GUI chrome from Bureau I; document
  content uses the fixed wizdoc palette.
- Rejects: WYSIWYG editing. The Wizard writes markup.
  The Bureau renders it.

---

## V. Technical Concept

### Mental Model

A `.bureau` file is a pipe-tag markup document with YAML
front matter. The parser converts it to an AST (list of
typed nodes with inline formatting spans). Two emitters
consume the AST: one produces `.md` (Python), one produces
`.wiz` (Node.js `docx` library). The GUI provides a
syntax-highlighted editor on the left and a live rich-text
preview on the right.

### Core Abstractions

- **BureauDocument** — complete parsed file: header + node
  list.
- **BureauNode** — a single content element: tag, content,
  inline spans, children (for tables), metadata.
- **InlineSpan** — formatted text fragment: bold, italic,
  code, or color-token reference.
- **DocumentHeader** — YAML front matter: title, type,
  version, author, theme.

### Key Technical Decisions

- Node.js `docx` library for `.wiz` emission — produces
  the highest-aesthetic output per wizdoc style guide.
- Python wrapper invokes Node via subprocess — keeps the
  Python ecosystem clean while leveraging the best docx
  tooling.
- Pipe-tag format with explicit block closes — deep
  formatting without ambiguity.
- `dataclass`-based AST — clean serialization to JSON for
  the Node emitter.

---

## VI. Functional Scope

### Core

- `.bureau` pipe-tag parser with YAML header, single tags,
  block tags, table blocks, inline formatting
- Inline spans: **bold**, *italic*, `code`,
  {{token|colored}}
- `.md` emitter (Python): box-drawing tables, 80-char wrap
- `.wiz` emitter (Node.js): full wizdoc aesthetic
- Bureau writer: AST → `.bureau` round-trip
- 5 built-in templates: expositio, dux_tome, build_doc,
  palette_card, blank
- CLI: compile, new (scaffold), templates (list)
- `.bureau.json` companion file with provenance
- GUI: syntax-highlighted editor + live preview
- SQLite document library
- Bureau I theme.json consumption for GUI chrome

### Exclusions

- No image embedding (future scope)
- No WYSIWYG editing
- No page layout or print production
- No ClaudeBox / AI integration

---

## VII. Constraints

- Python 3.11+, PyQt6 6.6+ (GUI), Node.js (`.wiz` emit).
- Target: CastrumDigitos (Debian Trixie, KDE Plasma 6).
- Depends on `npm install -g docx` for `.wiz` output.
- Single-user application.

---

## VIII. Success Criteria

- Scaffold a template, fill it, compile to `.wiz` + `.md`
  + `.bureau.json` in one command.
- 28/28 tests pass. Parser round-trips without loss.
- `.wiz` output opens correctly in LibreOffice with wizdoc
  styling intact.
- Failure: if a compiled `.wiz` renders with wrong colors,
  fonts, or broken tables.

---

## IX. Glossary

- **Compositio** — the editor stage (writing pipe-tags)
- **Specularium** — the live preview panel
- **Promulgatio** — compile / export stage
- **Sigillare** — save the `.bureau` source file
- **.bureau** — the pipe-tag source format
- **.wiz** — the styled docx output (renamed .docx)
- **.bureau.json** — provenance companion sidecar
- **Pipe-tag** — the `|tag|content|` markup syntax

---

*Ordo Discordia, Cosmos Inania*
