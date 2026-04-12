# SYSTEMS CHECK — DEPARTAMENTUM DOCUMENTALIS (Bureau III)

*A4 · Triumviratus Aestheticus Imperialis · Arca Cognitorium · MMXXVI*

---

## Summary

The legally binding document authority. `.bureau` pipe-tag markup format
with YAML frontmatter. Parser produces a dataclass AST with inline formatting
spans. Two emitters: Python for `.md` (box-drawing tables, 80-char wrap),
Node.js docx library for `.wiz` (full wizdoc aesthetic). CLI backend (`compile`,
`new`, `templates`) and PyQt6 GUI with syntax-highlighted editor and 300ms
debounced live rich-text preview. SQLite document library. `.bureau.json`
companion sidecar per document. 28/28 tests passing.

Motto: *Ｄｅｆｉｎｅ! Ｄｅｓｉｇｎａ! Ｄｅｎｏｔａ! Ｄｉｓｃｅｄｅ!*

---

## Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  .bureau markup parser            │  YAML frontmatter + pipe-tag syntax.       │
│                                   │  `|{TAG}|content|{/TAG}|`                  │
│                                   │  Explicit close for multi-line blocks.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Inline spans                     │  Bold, italic, code, colour-token          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  .md emitter (Python)             │  Box-drawing character tables, 80-char     │
│                                   │  wrap, ModusArcanus colour palette         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  .wiz emitter (Node.js)           │  Full wizdoc aesthetic. Node.js docx       │
│                                   │  library. Python invokes via subprocess.   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  5 built-in templates             │  expositio, dux_tome, build_doc,           │
│                                   │  palette_card, blank                       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  CLI                              │  `compile <file>` → .md + .wiz             │
│                                   │  `new <name> <template>` → scaffold        │
│                                   │  `templates` → list available              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  GUI                              │  Syntax-highlighted editor + live rich-    │
│                                   │  text preview at 300ms debounce            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  SQLite document library          │  Persistent across sessions                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  .bureau.json companion sidecar   │  Provenance metadata per document          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Bureau I theme.json consumption  │  GUI chrome uses Bureau I colours.         │
│                                   │  Document content uses fixed wizdoc        │
│                                   │  palette — not affected by theme.          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  28/28 tests passing              │                                            │
╰───────────────────────────────────┴────────────────────────────────────────────╯

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  theme.json from Bureau I (GUI chrome)                  │
│              │  .bureau source files                                   │
│              │  SQLite document library                                │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  .md files (Python .md emitter)                         │
│              │  .wiz files (Node.js docx emitter — renamed .docx)      │
│              │  .bureau.json companion sidecars                        │
│              │  SQLite document library                                │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  PyQt6 (GUI), Node.js + docx npm (wiz_export.js)        │
│              │  Bureau I theme.json (GUI chrome only — has fallback)   │
│              │  No ClaudeBox, no API calls                             │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Launch & Verification

```bash
# Confirm Node.js + docx available
node --version && npm list -g docx

# CLI smoke tests
cd ~/ArcaCognitorium/Exocognii/A4/DepartamentumDocumentalis
python -m DepartamentumDocumentalis templates
python -m DepartamentumDocumentalis new test_doc expositio
python -m DepartamentumDocumentalis compile test_doc.bureau

# GUI
python -m DepartamentumDocumentalis --gui

# Tests
pytest tests/ -v
```

Verification steps:

1. `templates` lists 5 built-in templates
2. `new` produces a `.bureau` file with correct YAML frontmatter
3. `compile` produces both `.md` and `.wiz` in the same directory
4. `.md` has box-drawing tables and 80-char wrapped body text
5. `.wiz` opens cleanly in LibreOffice Writer with correct styling
6. `.bureau.json` sidecar created alongside compiled documents
7. GUI opens — editor and preview both functional

Checklist:

- 28/28 tests passing
- Node.js + `docx` npm installed and accessible from subprocess
- `.bureau` → `.md` round-trip preserves all content
- `.wiz` opens without error in LibreOffice — fonts and colours correct
- GUI chrome uses Bureau I theme.json (not hardcoded constants)
- Document content uses fixed wizdoc palette (independent of theme)

---

## Open Items

Armarium GUI drawer (Component Library browsing via GUI) — not yet built.
Dux Tome for Bureau III will need a revision pass once Armarium is built.

Font enforcement: `.wiz` emitter uses Georgia as fallback everywhere.
Ebon Sigil, Varnyx, VL Gothic, Runavess not enforced. Font audit on
CastrumDigitos needed to confirm availability before enforcing.

Bureau III deploy path is `Exocognii/A4/` — not the full
AestheticAuthoritarianAssociativeAlliance/ path of Bureaus I and II.
Path unification deferred.

---

## Claude.ai Collaboration Prompt

```
You are assisting with DEPARTAMENTUM DOCUMENTALIS (Bureau III) — the
document template forge of the Arca Cognitorium. PyQt6, Python 3.11,
Node.js for .wiz emission. Debian Trixie.

Architecture:
- .bureau markup: YAML frontmatter + pipe-tag syntax
  Format: |{TAG}|content|{/TAG}|
  Explicit close required for multi-line block tags.
- Parser produces dataclass AST with typed node list + inline spans
- Two emitters: Python (.md) and Node.js docx library (.wiz)
- .md: box-drawing character tables, 80-char wrap, ModusArcanus colours
- .wiz: full wizdoc aesthetic via Node.js docx library
  Python invokes via subprocess — keeps Python ecosystem clean
- GUI chrome uses Bureau I theme.json
- Document content uses FIXED wizdoc palette — not affected by theme
- .bureau.json companion sidecar per compiled document
- CLI: compile / new / templates commands
- No ClaudeBox, no API calls
- 28/28 tests must pass after any change

Deploy path: Exocognii/A4/DepartamentumDocumentalis/
Motto: Define! Designa! Denota! Discede!

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＤＥＰＡＲＴＡＭＥＮＴＵＭ ＤＯＣＵＭＥＮＴＡＬＩＳ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  Departamentum Documentalis (Bureau III)              ║
║    Version      ·  1.0                                                  ║
║    Tests        ·  28/28 passing                                        ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
