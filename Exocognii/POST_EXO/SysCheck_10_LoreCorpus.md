# SYSTEMS CHECK — LORE CORPUS

*Tower Shared Infrastructure · Arca Cognitorium · MMXXVI*

---

## Summary

Shared read layer and file system substrate for ratified Cogniverse lore.
Not a standalone application — a structured directory with an accompanying
Python reader module (`lore_corpus.py`) and a Textual display widget
(`LoreBookScreen`). Consumed by Tower entities, Scribae, and any Exocognii
tool that needs to surface or reference canonical lore. Entirely read-only
from all consumer perspectives: the sole writer is Exvacua Loricum at
Sacramentum Finalitus. Currently inert — write side awaits Exvacua Loricum
Session B.

---

## Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  register.yaml                    │  Master catalogue. One entry per ratified  │
│                                   │  Exloricum. Every reader opens this first. │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  domains.yaml                     │  Taxonomy register. 8 seeded Cogniverse    │
│                                   │  domains.                                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Exloricum .md files              │  Prose body per ratified entry.            │
│                                   │  `corpus/{uuid}.md` per entry.             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Loridex Card .card.json files    │  Metadata per ratified entry.              │
│                                   │  `corpus/{uuid}.card.json` per entry.      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  lore_corpus.py reader            │  get_register(), get_entry(),              │
│                                   │  get_exloricum(), get_card(),              │
│                                   │  list_by_domain(), list_by_tag(),          │
│                                   │  list_by_status(), list_all_domains(),     │
│                                   │  get_domain_info(), corpus_status()        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  LoreBookScreen widget            │  Textual modal. Renders Exloricum as       │
│                                   │  styled manuscript: gold header band,      │
│                                   │  scrollable parchment body. Accept UUID    │
│                                   │  or pre-loaded data via from_data().       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  setup_lore_corpus.py             │  Idempotent init script. --check dry-run   │
│                                   │  support.                                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Graceful failure throughout      │  Missing file → None. Missing register     │
│                                   │  → empty list. Never raises to caller.     │
│                                   │  PyYAML absent → empty returns + warning.  │
╰───────────────────────────────────┴────────────────────────────────────────────╯

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  Shared/Lore/register.yaml                              │
│              │  Shared/Lore/domains.yaml                               │
│              │  Shared/Lore/corpus/{uuid}.md                           │
│              │  Shared/Lore/corpus/{uuid}.card.json                    │
│              │  ~/.arca/config.json (lore_corpus_path resolution)      │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  Nothing. Read-only by design.                          │
│              │  (Exvacua Loricum is the sole writer at Sacramentum)    │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  PyYAML (soft dep — graceful degradation if absent)     │
│              │  Textual (for LoreBookScreen widget)                    │
│              │  No ClaudeBox, no API calls, no network                 │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Launch & Verification

```bash
# Run init script (idempotent — safe to run multiple times)
cd ~/ArcaCognitorium
python Shared/setup_lore_corpus.py

# Dry-run check
python Shared/setup_lore_corpus.py --check

# Verify structure exists
ls ~/ArcaCognitorium/Shared/Lore/
# Expected: register.yaml  domains.yaml  corpus/

# Test reader from Python
python -c "
import sys; sys.path.insert(0, '/home/lordfingers/ArcaCognitorium')
from Shared.lore_corpus import lore_corpus
print(lore_corpus.corpus_status())
print(lore_corpus.list_all_domains())
"
```

Verification steps:

1. `Shared/Lore/` directory exists
2. `register.yaml` exists (empty list is correct — corpus starts empty)
3. `domains.yaml` exists with 8 seeded domains
4. `corpus/` subdirectory exists
5. `lore_corpus.get_register()` returns a list without raising
6. `lore_corpus.corpus_status()` returns a dict without raising
7. `lore_corpus.get_exloricum("nonexistent-uuid")` returns None, not exception

Checklist:

- Directory structure initialised (setup_lore_corpus.py run successfully)
- All reader functions return gracefully on empty corpus
- PyYAML installed (confirm — absent degrades to empty returns)
- LoreBookScreen dismisses cleanly via `esc` or `q` in Textual
- No blocking I/O on Textual main thread (LoreBookScreen uses async read)
- Path resolves from config or falls back to ~/ArcaCognitorium/Shared/Lore/

---

## Open Items

The corpus is currently inert. register.yaml is an empty list. It will
remain inert until Exvacua Loricum Session B implements the write side
(Actio Duxuum depositing files at Sacramentum Finalitus).

Scribae integration is a future dedicated Tower build session — the SCRIBAE
use the reader to extract and distribute lore through the Tower.

A dedicated book-crafting application for richer lore display outside the
Tower terminal is future scope. Name deferred to Lexifer.

---

## Claude.ai Collaboration Prompt

```
You are assisting with the LORE CORPUS — the shared read layer for
ratified Cogniverse lore in the Arca Cognitorium. Python 3.11, Textual.
Not a standalone app. A shared library and file directory.

Architecture:
- Directory: ArcaCognitorium/Shared/Lore/
  register.yaml — master index (one entry per Exloricum)
  domains.yaml — taxonomy register (8 seeded domains)
  corpus/{uuid}.md — Exloricum prose body
  corpus/{uuid}.card.json — Loridex Card metadata
- lore_corpus.py: read-only reader. Public API:
  get_register(), get_entry(id), get_exloricum(id), get_card(id),
  list_by_domain(d), list_by_tag(t), list_by_status(s),
  list_all_domains(), get_domain_info(d), corpus_status()
- NEVER raises to callers — all functions return None or [] on missing data
- PyYAML is a soft dep — if absent, all returns are empty with log warning
- Path resolution: ~/.arca/config.json → fallback ~/ArcaCognitorium
- LoreBookScreen: Textual modal widget at Shared/widgets/lore_book.py
  Accepts UUID or pre-loaded data via from_data()
  No blocking I/O on Textual main thread
- Sole write authority is Exvacua Loricum at Sacramentum Finalitus.
  The corpus reader never writes anything.
- Bureau is excluded from lore rendering scope by design — this is
  Textual-native display only.

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＬＯＲＥ ＣＯＲＰＵＳ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ                       ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    System       ·  Lore Corpus                                          ║
║    Version      ·  1.0                                                  ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
