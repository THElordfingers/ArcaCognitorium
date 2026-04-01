╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║   ＰＥＲＰＥＴＵＵＭ ＡＥＤＩＦＩＣＡＲＥ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ   ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  Perpetuum Aedificare                                 ║
║    Version      ·  1.0                                                  ║
║    Port         ·  8732                                                 ║
║    Started      ·  04-01-2026                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
╔═════════════════════╗
║ Verification steps: ║
╚═════════════════════╝


☐  1. Service starts cleanly on port 8732
2. Aggrexuum status returns last run timestamp and pending count
3. Nota Brevis POST returns a capture UUID
4. Pending captures list shows the test entry
5. Manual Actio Aggrexuum fires — creates or updates a Nodus
6. Nodi list shows the resulting node with Nodifex description
7. Database file exists at configured path




═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Checklist: ║
╚════════════╝


- Port 8732 not already in use at launch
- SQLite database initialises with 7 seeded Nodicum types
- ClaudeBox resolves from `arca_repo_path` in config
- CLAUDE_API_KEY env var is set
- Actio Aggrexuum creates meaningful Nodus from capture content
- Drift threshold defaults to 0.65 — adjustable in config
- Driftuum Attentio fires once per node, not repeatedly







═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Open Items ║
╚════════════╝


Praesidium read layer not yet built — Wizard cannot yet query build state
through a unified surface. This is the most consequential deferred item in
the Cognosis suite.

Nuntius not yet built — apps do not yet emit Involucrum automatically.
Until Nuntius exists, all emissions are manual (Nota Brevis, curl).
