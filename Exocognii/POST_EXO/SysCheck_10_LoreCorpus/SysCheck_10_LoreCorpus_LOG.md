╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＬＯＲＥ ＣＯＲＰＵＳ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ                    ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    System       ·  Lore Corpus                                          ║
║    Version      ·  1.0                                                  ║
║    Started      ·  04-01-2026                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
╔═════════════════════╗
║ Verification steps: ║
╚═════════════════════╝


☐  1. `Shared/Lore/` directory exists
2. `register.yaml` exists (empty list is correct — corpus starts empty)
3. `domains.yaml` exists with 8 seeded domains
4. `corpus/` subdirectory exists
5. `lore_corpus.get_register()` returns a list without raising
6. `lore_corpus.corpus_status()` returns a dict without raising
7. `lore_corpus.get_exloricum("nonexistent-uuid")` returns None, not exception




═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Checklist: ║
╚════════════╝

- Directory structure initialised (setup_lore_corpus.py run successfully)
- All reader functions return gracefully on empty corpus
- PyYAML installed (confirm — absent degrades to empty returns)
- LoreBookScreen dismisses cleanly via `esc` or `q` in Textual
- No blocking I/O on Textual main thread (LoreBookScreen uses async read)
- Path res







═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Open Items ║
╚════════════╝

The corpus is currently inert. register.yaml is an empty list. It will
remain inert until Exvacua Loricum Session B implements the write side
(Actio Duxuum depositing files at Sacramentum Finalitus).

Scribae integration is a future dedicated Tower build session — the SCRIBAE
use the reader to extract and distribute lore through the Tower.

A dedicated book-crafting application for richer lore display outside the
Tower terminal is future scope. Name deferred to Lexifer.
