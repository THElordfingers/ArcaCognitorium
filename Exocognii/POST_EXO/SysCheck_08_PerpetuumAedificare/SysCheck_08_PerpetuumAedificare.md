# SYSTEMS CHECK — PERPETUUM AEDIFICARE

*Cognosis Suite · Arca Cognitorium · MMXXVI*

---

## Summary

Build continuity memory service. Local FastAPI on port 8732. Captures ambient
build events from all Exocognii apps via four pathways, aggregates them into a
graph of Nodi Momentuum (active work units) using Claude, detects drift via
Driftuum Sentifex, and is designed to surface the current shape of the project
through the Praesidium read layer (not yet built). Faster cadence than Exvacua
Loricum (5-minute interval, 10-capture threshold) because build signals are
more time-sensitive. Tower read-only via Arca Absoluticum — Perpetuum
Aedificare never writes to Tower storage.

---

## Feature List

╭───────────────────────────────────────┬──────────────────────────────────┬────────────╮
│  Feature                              │  Trigger                         │  Status    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Involucrum ingestion                 │  POST /acquiuum                  │  Working   │
│  Nota Brevis (quick note)             │  POST /acquiuum/nota             │  Working   │
│  Oratio Extracticum (conv. scour)     │  POST /acquiuum/oratio           │  Working   │
│  File drop ingestion                  │  POST /acquiuum (file_drop type) │  Working   │
│  Actio Aggrexuum (aggregation)        │  Scheduled + threshold override  │  Working   │
│  Nodus Momentuum CRUD                 │  POST/GET/PUT/DELETE /nodus      │  Working   │
│  Nodi listing and filtering           │  GET /nodi                       │  Working   │
│  Exnodica relationship graph          │  POST /exnodica                  │  Working   │
│  Relationship editing                 │  PUT /exnodica/{id}              │  Working   │
│  Arca Absoluticum Tower refs          │  POST /nodus/{id}/arca           │  Working   │
│  Driftuum Sentifex                    │  Fires inside Actio Aggrexuum    │  Working   │
│  Driftuum Attentio flags              │  Auto when threshold crossed     │  Working   │
│  Manual capture-to-node assignment    │  PUT /acquiuum/{id}/node         │  Working   │
│  Aggrexuum status                     │  GET /aggrexuum/status           │  Working   │
│  Praesidium read layer                │  Not yet built                   │  Partial   │
│  Nuntius wiring to all apps           │  Not yet built                   │  Partial   │
╰───────────────────────────────────────┴──────────────────────────────────┴────────────╯

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  POST payloads from all apps (Involucrum envelopes)     │
│              │  Quick Wizard notes (Nota Brevis)                       │
│              │  File paths for conversation scour                      │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  ~/.arca/perpetuum_aedificare.db (SQLite — all data:    │
│              │   Acquiuum Chronex, Nodi, Exnodica, drift log)          │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Config      │  ~/.arca/config.json                                    │
│              │    perpetuum_aedificare_db (db path)                    │
│              │    perpetuum_aedificare_store (file store path)         │
│              │    perpetuum_aedificare.aggrexuum_interval (default 300s│
│              │    perpetuum_aedificare.aggrexuum_threshold (default 10)│
│              │    perpetuum_aedificare.drift_threshold (default 0.65)  │
│              │    port (default 8732)                                  │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  ClaudeBox at ~/ArcaCognitorium/claudebox/              │
│              │  CLAUDE_API_KEY environment variable                    │
│              │  FastAPI, uvicorn                                       │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Launch & Verification

```bash
# Start service
cd ~/ArcaCognitorium/Exocognii/PerpetuumAedificare
python main.py
# Service runs on port 8732

# Health check
curl http://localhost:8732/aggrexuum/status

# Send a test capture (Nota Brevis — lowest friction)
curl -X POST http://localhost:8732/acquiuum/nota \
  -H "Content-Type: application/json" \
  -d '{"body":"Working on the Cognosis wiring pass."}'

# Confirm capture is pending
curl http://localhost:8732/acquiuum?status=pending

# Manually trigger aggregation
curl -X POST http://localhost:8732/aggrexuum

# List nodes created by aggregation
curl http://localhost:8732/nodi

# Check drift flags
curl http://localhost:8732/nodi?status=active
```

Verification steps:

1. Service starts cleanly on port 8732
2. Aggrexuum status returns last run timestamp and pending count
3. Nota Brevis POST returns a capture UUID
4. Pending captures list shows the test entry
5. Manual Actio Aggrexuum fires — creates or updates a Nodus
6. Nodi list shows the resulting node with Nodifex description
7. Database file exists at configured path

Checklist:

- Port 8732 not already in use at launch
- SQLite database initialises with 7 seeded Nodicum types
- ClaudeBox resolves from `arca_repo_path` in config
- CLAUDE_API_KEY env var is set
- Actio Aggrexuum creates meaningful Nodus from capture content
- Drift threshold defaults to 0.65 — adjustable in config
- Driftuum Attentio fires once per node, not repeatedly

---

## Open Items

Praesidium read layer not yet built — Wizard cannot yet query build state
through a unified surface. This is the most consequential deferred item in
the Cognosis suite.

Nuntius not yet built — apps do not yet emit Involucrum automatically.
Until Nuntius exists, all emissions are manual (Nota Brevis, curl).

---

## Claude.ai Collaboration Prompt

```
You are assisting with PERPETUUM AEDIFICARE — the build continuity memory
service of the Arca Cognitorium. FastAPI, Python 3.11, SQLite. Port 8732.

Architecture:
- Four capture pathways: Indicatum Machina (app emission via /acquiuum),
  Nota Brevis (/acquiuum/nota), Oratio Extracticum (/acquiuum/oratio),
  file drop (/acquiuum with source_type: file_drop)
- Acquiuum Chronex: raw capture table. Statuses: pending → aggregated / dismissed
- Actio Aggrexuum: Claude maps each capture to existing Nodus or creates
  new one. Updates Nodifex (current-state description). Runs on schedule
  (5min) or threshold (10 pending). Both configurable.
- Nodus Momentuum: atomic work unit. Carries Nodicum type (seeded: system,
  feature, concept, question, decision, artefact, session), Nodifex,
  open_questions, decisions, Arca Absoluticum refs, drift score.
- Exnodica: directed edges between Nodi. Labels: spawned_from, blocks,
  informs, supersedes. Inferred or wizard_set confidence.
- Driftuum Sentifex: scores all active Nodi after each Aggrexuum pass.
  Score from staleness + connected node activity. Flag fires once at 0.65.
- Tower boundary: Perpetuum Aedificare reads Tower construct refs via
  Arca Absoluticum — never writes to Tower storage.
- ClaudeBox: canonical path from arca_repo_path in ~/.arca/config.json
- CLAUDE_API_KEY env var — never ANTHROPIC_API_KEY

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＰＥＲＰＥＴＵＵＭ ＡＥＤＩＦＩＣＡＲＥ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ        ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  Perpetuum Aedificare                                 ║
║    Version      ·  1.0                                                  ║
║    Port         ·  8732                                                 ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
