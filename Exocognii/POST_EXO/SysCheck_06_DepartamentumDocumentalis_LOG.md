╔══════════════════════════════════════════════════════════════════════════════════╗
║◤                                                                               ◥ ║
║                                                                                  ║
║  ＤＥＰＡＲＴＡＭＥＮＴＵＭ ＤＯＣＵＭＥＮＴＡＬＩＳ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ ║
║                                                                                  ║
║◣                                                                               ◢ ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                  ║
║    Application  ·  Departamentum Documentalis (Bureau III)                       ║
║    Version      ·  1.0                                                           ║
║    Tests        ·  28/28 passing                                                 ║
║    Started      ·  04-01-2026                                                    ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
╔═════════════════════╗
║ Verification steps: ║
╚═════════════════════╝

☐  1. `templates` lists 5 built-in templates
2. `new` produces a `.bureau` file with correct YAML frontmatter
3. `compile` produces both `.md` and `.wiz` in the same directory
4. `.md` has box-drawing tables and 80-char wrapped body text
5. `.wiz` opens cleanly in LibreOffice Writer with correct styling
6. `.bureau.json` sidecar created alongside compiled documents
7. GUI opens — edito




═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Checklist: ║
╚════════════╝

- 28/28 tests passing
- Node.js + `docx` npm installed and accessible from subprocess
- `.bureau` → `.md` round-trip preserves all content
- `.wiz` opens without error in LibreOffice — fonts and colours correct
- GUI chrome uses Bureau I theme.json (not hardcoded constants)
- Document content uses fixed wizdoc palette (independent of theme)








═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Open Items ║
╚════════════╝

Armarium GUI drawer (Component Library browsing via GUI) — not yet built.
Dux Tome for Bureau III will need a revision pass once Armarium is built.

Font enforcement: `.wiz` emitter uses Georgia as fallback everywhere.
Ebon Sigil, Varnyx, VL Gothic, Runavess not enforced. Font audit on
CastrumDigitos needed to confirm availability before enforcing.

Bureau III deploy path is `Exocognii/A4/` — not the full
AestheticAuthoritarianAssociativeAlliance/ path of Bureaus I and II.
Path unification deferred.
