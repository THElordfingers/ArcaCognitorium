# LORE CORPUS
### Expositio · v1.0 · 2026-03-29

---

## I. IDENTITY

**Name & Version** — Lore Corpus · v1.0

**Tagline** — The published record of ratified Cogniverse lore: read by
everything, written by nothing but the authority that earned the right.

**Classification** — Shared read layer and file system substrate. Not a
standalone application. A structured data store with an accompanying reader
module and a Textual display widget, consumed by Tower and Exocognii alike.

**Status** — Stable. Initialised and ready for first entries from Exvacua
Loricum when that service is built.

---

## II. PURPOSE

**Problem Statement** — The Tower and the Exocognii suite need access to
ratified Cogniverse lore, but lore ratification happens in a separate service
(Exvacua Loricum) that the Tower does not speak to directly. Without a
neutral landing zone between the two, every consumer would need its own
pipeline into the ratification system — coupling everything to a service that
doesn't exist yet and may be unavailable at runtime.

**Motivation** — The Tower is an organism. Its entities, its Scribae, its
Council — all of them should be able to draw on a living body of ratified lore
without needing to understand where that lore came from or how it was
assembled. The Corpus is the membrane between the making of lore and the
use of it.

**Intended Outcome** — Any component in the suite — a Scribae process in the
Tower, a Praesidium read panel, a future Exocognii tool — can call
`lore_corpus.get_exloricum(id)` and receive the prose of a ratified lore entry
without knowing anything about Exvacua Loricum's internal mechanics. The
Corpus exists so that nothing else has to know how lore is made.

**Anti-Purpose** — The Lore Corpus does not write, ratify, infer, classify, or
judge lore. It does not trigger distillation. It does not communicate with
Exvacua Loricum at runtime. It is not a database service. It is a structured
directory of files with a reader sitting in front of it.

---

## III. AUDIENCE

**Primary Users** — Developers and systems within the Arca Cognitorium suite
integrating ratified lore into their runtime behaviour. In the Tower: the
Scribae, Luminarious, The Builder. In Exocognii: any app that needs to surface
or reference canonical lore.

**Secondary Users** — LordFingers, reading lore entries via the Book widget
from within the Tower, or inspecting the register and corpus files directly.

**Assumed Knowledge** — Callers of `lore_corpus.py` are expected to know a
lore entry's UUID or to query by domain or tag. The corpus does not provide
search or inference — that is Exvacua Loricum's territory.

**Out-of-Scope Audiences** — End users of a future public Tower instance, if
such a thing ever exists. The Corpus is internal infrastructure.

---

## IV. DESIGN PHILOSOPHY

**Core Principles**

- Read-only by design. The corpus has one write authority: Exvacua Loricum at
  Sacramentum Finalitus. No other path exists.
- Fail silently, never raise. A missing file returns None. A missing register
  returns an empty list. The Tower must not crash because a lore entry is
  absent.
- One source of truth. All files live at `Shared/Lore/`. Nothing is duplicated
  into tool directories.
- Terminal-native display. The Book widget renders in Textual. No HTML, no
  browser. The Tower is a terminal instrument and the lore should feel like
  part of it.

**Tradeoff Positions** — Flat file storage over SQLite. The corpus is
append-only and read-heavy. SQLite adds a dependency and a daemon for no gain
at current scale. YAML and Markdown files are inspectable, diffable, and
committable to git without tooling.

**Aesthetic Direction** — The corpus files carry the full Modus Arcanus
register: box-drawing headers, archaic Latin naming, parchment-and-void palette
in the widget. The data is not decoration; the decoration is part of the data.

**What This Philosophy Rejects** — A unified database layer shared between
Exvacua Loricum and the Corpus. The separation is intentional. Exvacua Loricum
is sovereign over its own storage. The Corpus is a published output, not a
shared schema.

---

## V. TECHNICAL CONCEPT

**Mental Model** — Think of the Corpus as a library shelf. Exvacua Loricum is
the bindery: it takes raw material, assembles it into a book, and places it on
the shelf. The Corpus is the shelf and the catalogue. `lore_corpus.py` is the
librarian — it knows where things are and hands them to whoever asks.

**Core Abstractions**

- `register.yaml` — the master catalogue. One entry per ratified Exloricum.
  Flat list. Every reader opens this first.
- Exloricum `.md` — the prose body of a lore entry. The actual book text.
- Loridex Card `.card.json` — the metadata record mirrored from Exvacua
  Loricum. Domain, tags, ratification timestamp, linked entries.
- `domains.yaml` — the taxonomy register. Seeded domains, emergent tags.
  Mirrors the Arx Loricuum from Exvacua Loricum.
- `LoreBookScreen` — the Textual modal that renders an Exloricum as a
  manuscript page within the Tower's terminal interface.

**Data Flow Overview** — Exvacua Loricum completes a Sacramentum Finalitus →
writes `.md` and `.card.json` to `Shared/Lore/corpus/` → appends an entry to
`register.yaml`. At Tower runtime: a component calls `lore_corpus.get_entry()`
or `get_exloricum()` → the reader parses register.yaml → locates and reads the
relevant file → returns the content. The Book widget wraps the prose read in a
Textual modal for direct Wizard display.

**System Boundaries** — The Corpus owns: the `Shared/Lore/` directory, the
`register.yaml` schema, the `domains.yaml` taxonomy, the `lore_corpus.py`
reader, and the `lore_book.py` widget. It does not own Exvacua Loricum's
internal storage, the ratification pipeline, or any Tower memory layer.

**Key Technical Decisions**

- PyYAML for register parsing. Soft dependency — if absent, all corpus calls
  return empty/None with a log warning rather than crashing.
- Path resolution via `~/.arca/config.json`. Consistent with every other
  Exocognii component. Fallback to `~/ArcaCognitorium` if config absent.
- `LoreBookScreen` accepts either a UUID (reads corpus itself) or pre-loaded
  data via `from_data()` — avoids a redundant file read when the caller
  already holds the entry.

---

## VI. FUNCTIONAL SCOPE

**Core Capabilities** — Read any ratified lore entry by UUID. Filter the
register by domain or tag. Retrieve the taxonomy of seeded domains. Display an
Exloricum as a styled manuscript modal in any Textual application.

**Supporting Capabilities** — `corpus_status()` health check for Praesidium
diagnostics. `_render_prose()` internal Markdown-to-Rich-markup converter
handling headings, bold, italic, and horizontal rules.

**Explicit Exclusions** — Writing to the corpus. Ratification logic. Search or
full-text indexing. Inference or classification. Network calls. Any interaction
with Exvacua Loricum at runtime.

**Future Scope** — When Exvacua Loricum is built, it will be the sole writer
to this corpus. The Praesidium read layer will surface corpus queries through
`corpus_status()` and domain/tag filtering. The Scribae (Tower build, separate
session) will consume the corpus reader as part of their extraction mechanics.

---

## VII. CONSTRAINTS & CONTEXT

**Technical Constraints** — Python 3.11+. Textual for the Book widget. PyYAML
as soft dependency (graceful degradation if absent). All paths via
`Path.home()` — no hardcoded user paths. X11 / Debian Trixie / KDE Plasma 6.

**External Dependencies** — PyYAML (`pip install pyyaml --break-system-packages`).
Textual (already present in Tower). No network dependencies. No API calls.

**Structural Dependency** — The corpus is inert until Exvacua Loricum exists
and begins depositing files. `register.yaml` is initialised empty. All reader
calls on an empty corpus return gracefully.

---

## VIII. SUCCESS CRITERIA

**Functional Success** — `lore_corpus.get_register()` returns a list (empty or
populated) without raising. `lore_corpus.get_exloricum(id)` returns prose text
for a valid UUID and None for an invalid one. `LoreBookScreen` opens, renders
content, and dismisses cleanly via `esc` or `q`.

**User Success** — The Wizard opens a lore entry from within the Tower and
reads it in a styled manuscript overlay without leaving the terminal. The entry
feels like something retrieved from a vault, not a text file opened in a
viewer.

**Quality Benchmarks** — No exception propagates out of any `lore_corpus`
function under any file-system condition. Widget renders within one frame of
being pushed. No blocking I/O on the Textual main thread.

**Failure Conditions** — The corpus raises an unhandled exception on a missing
file. The Book widget renders raw Markdown syntax instead of styled prose. Path
resolution silently uses the wrong directory without logging a warning.

---

## IX. GLOSSARY

**Lore Corpus** — The published, ratified lore store. Distinct from Exvacua
Loricum's internal working storage. Read by all; written by Exvacua Loricum
only.

**Exloricum** — A long-form prose lore document. The body text of a ratified
lore entry. Stored as `.md` in `corpus/`.

**Loridex Card** — The structured metadata record for a lore entry. Domain,
tags, ratification date, linked entries. Stored as `.card.json` in `corpus/`.

**register.yaml** — The master index. One YAML entry per ratified Exloricum.
The first file any reader opens.

**Sacramentum Finalitus** — The ratification ceremony in Exvacua Loricum.
Completion of this ceremony is the only trigger for a write to the Corpus.

**Scribae** — Tower-side custodians of the Lore Engine. They extract from the
Corpus and distribute lore through the Tower. A separate Tower build — not part
of this deliverable.

**LoreBookScreen** — The Textual modal widget. Renders an Exloricum as a
styled manuscript page within the terminal.

---

## X. REVISION NOTES

**2026-03-29 · v1.0** — Initial build. Corpus structure established. Reader
and Book widget delivered. Bureau excluded from Lore rendering scope by
design decision: Bureau handles PyQt6 document authority; Lore display remains
Textual-native. A dedicated book-crafting application is the forward path for
richer lore document presentation outside the Tower.

---

*Expositio · Lore Corpus · v1.0 · Ordo Discordia, Cosmos Inania*
