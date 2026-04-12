# SYSTEMS CHECK — EXVACUA LORICUM

*Cognosis Suite · Arca Cognitorium · MMXXVI*

---

## Summary

Lore canon memory service. Local FastAPI on port 8731. Passive ingestion via
Involucrum envelopes — all Exocognii apps write, the system classifies.
Actio Interpretus (Claude-powered) runs on a 10-minute heartbeat or fires early
when 20 pending Lorixii accumulate. Five-phase Judicium ratification ceremony
moves clusters from the Lorixii Speculativum into the Loridex (canon index)
and Exlorica (prose documents) via Sacramentum Finalitus. The Loretic
Crystalizer updates the Loricum Ratifex (master compendium) after every
ratification. Nothing becomes canon without the Wizard's explicit act.

Session B work deferred: Judicium UI and `.wiz` rendered output.

---

## Feature List

╭───────────────────────────────────────┬──────────────────────────────────┬────────────╮
│  Feature                              │  Trigger                         │  Status    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Involucrum ingestion                 │  POST /lorix                     │  Working   │
│  File drop ingestion                  │  POST /lorix/drop                │  Working   │
│  Lorixii Extractuum (corpus scour)    │  POST /extracticus               │  Working   │
│  Actio Interpretus (classification)   │  Scheduled + threshold override  │  Working   │
│  Lorixii clustering by domain         │  Runs inside Interpretus pass    │  Working   │
│  Judicium Phase I (cull)              │  POST /judicium → /advance       │  Working   │
│  Judicium Phase II (elaboration)      │  POST /judicium/{id}/advance     │  Working   │
│  Judicium Phase III (Card draft)      │  Advance from Phase II           │  Working   │
│  Judicium Phase IV (Exloricum draft)  │  Advance from Phase III          │  Working   │
│  Judicium Phase V (Sacramentum)       │  POST /judicium/{id}/commit      │  Working   │
│  Loretic Crystalizer                  │  Auto after commit               │  Working   │
│  Loridex Card (SQLite + .md)          │  Produced at Sacramentum         │  Working   │
│  Exloricum (.md on disk)              │  Produced at Sacramentum         │  Working   │
│  Loricum Ratifex (.md on disk)        │  GET /ratifex                    │  Working   │
│  Direct Exloricum editing             │  PUT /exloricum/{id}             │  Working   │
│  Direct Ratifex section editing       │  PUT /ratifex/section/{domain}   │  Working   │
│  Arx Loricuum taxonomy                │  GET/POST /loricuum              │  Working   │
│  Actio Revisicus (revision flag)      │  POST /revisicus/{card_id}       │  Working   │
│  .wiz rendered output (Actio Duxuum)  │  Not yet built                   │  Partial   │
│  Judicium UI                          │  Not yet built — Session B       │  Partial   │
╰───────────────────────────────────────┴──────────────────────────────────┴────────────╯

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  POST payloads from all apps (Involucrum envelopes)     │
│              │  File drops at designated path                          │
│              │  Repo and file paths for corpus scours                  │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  ~/.arca/exvacua_loricum.db (SQLite — all structured    │
│              │   data: Lorixii, Cards, sessions, taxonomy)             │
│              │  ~/.arca/exvacua_loricum/loricum_ratifex.md             │
│              │  ~/.arca/exvacua_loricum/exlorica/{uuid}.md             │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Config      │  ~/.arca/config.json                                    │
│              │    exvacua_loricum_db (db path)                         │
│              │    exvacua_loricum_store (file store path)              │
│              │    exvacua_loricum.interpretus_interval (default 600s)  │
│              │    exvacua_loricum.interpretus_threshold (default 20)   │
│              │    port (default 8731)                                  │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  ClaudeBox at ~/ArcaCognitorium/claudebox/              │
│              │  CLAUDE_API_KEY environment variable                    │
│              │  FastAPI, uvicorn                                       │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Launch & Verification

```bash
# Start service
cd ~/ArcaCognitorium/Exocognii/ExvacuaLoricum
python main.py
# Service runs on port 8731

# Health check
curl http://localhost:8731/interpretus/status

# Send a test Lorix
curl -X POST http://localhost:8731/lorix \
  -H "Content-Type: application/json" \
  -d '{"source_app":"test","source_version":"0","timestamp":"2026-01-01T00:00:00Z","body":"Test lore content about the Cogniverse."}'

# Confirm Lorix is pending
curl http://localhost:8731/lorixii?status=pending

# Manually trigger classification
curl -X POST http://localhost:8731/interpretus

# Check taxonomy (10 domains should be seeded)
curl http://localhost:8731/loricuum
```

Verification steps:

1. Service starts cleanly on port 8731
2. Health check returns last interpretus timestamp and pending count
3. Test Lorix POST returns a UUID
4. Lorixii list shows the test entry as pending
5. Manual Actio Interpretus fires and classifies the test entry
6. 10 seeded domains exist in Arx Loricuum
7. Database file exists at configured path

Checklist:

- Port 8731 is not already in use at launch
- SQLite database initialises without error
- ClaudeBox resolves from `arca_repo_path` in config
- CLAUDE_API_KEY env var is set
- Actio Interpretus successfully calls Claude and writes classification
- Rejected and ignored Lorixii are retained — never deleted
- Exloricum .md files appear in store directory after Sacramentum

---

## Open Items

Session B — Judicium UI and `.wiz` rendered output via Actio Duxuum.
Nuntius not yet built — apps do not yet emit Involucrum automatically.
`.wiz` output deferred — `.md` is the only rendered output currently.

---

## Claude.ai Collaboration Prompt

```
You are assisting with EXVACUA LORICUM — the lore canon memory service
of the Arca Cognitorium. FastAPI, Python 3.11, SQLite. Port 8731.

Architecture:
- Involucrum envelope: {source_app, source_version, timestamp, hint?, body}
- Lorixii Speculativum: unratified observation pile in SQLite
  Statuses: pending → ignored / in_judicium → consumed / rejected
  Nothing is deleted — only classified
- Actio Interpretus: Claude-powered classification pass
  Fires on schedule (10min) or threshold (20 pending). Both configurable
  in ~/.arca/config.json.
- Arx Loricuum: taxonomy register — seeded domains + emergent tags.
  10 domains seeded at init.
- Judicium: five-phase ceremony. All state in phase_data JSON field.
  POST /judicium → open. /advance → progress. /commit → Sacramentum.
- Loretic Crystalizer: updates Loricum Ratifex .md after commit.
  Checks provenance comments — does not overwrite Wizard-authored sections.
- ClaudeBox: canonical path from arca_repo_path in ~/.arca/config.json
- CLAUDE_API_KEY env var — never ANTHROPIC_API_KEY
- All routes: SQLite via get_db() context manager, WAL mode, per-request

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＥＸＶＡＣＵＡ ＬＯＲＩＣＵＭ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ               ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  Exvacua Loricum                                      ║
║    Version      ·  1.0                                                  ║
║    Port         ·  8731                                                 ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
