# NUNTIUS
## IdeaForge Build Document
### Arca Cognitorium — Exocognii Infrastructure Layer
*Phase 1 Idea Brief + Phase 2 Seed Prompt · v1.0*

---

## CONTENTS

  I.    Status Verdict
  II.   Phase 1 — Idea Brief
  III.  Phase 2 — Seed Prompt

---

# I. STATUS VERDICT

**NUNTIUS — NOT BUILT. PARTIALLY SPECIFIED BY IMPLICATION.**

Evidence:

  · Memory Schema v0.4, Section 4.1: the Involucrum write path is
    defined as two direct HTTP POST calls from a shared client library
    — one to Exvacua Loricum (8731), one to Perpetuum Aedificare (8732).
    NUNTIUS does not yet exist. The dual-POST pattern is the current
    interim design.
  · Memory Schema v0.4, Section 4.4: the shared client library that
    fires those POSTs is explicitly named as pending — "name pending
    the next naming sweep." NUNTIUS resolves this naming gap. It is
    simultaneously the name of the hub and the resolution of that
    open item.
  · Cogmentation Gospel: NUNTIUS listed as "Not yet built — Central
    messenger hub; all Involucrum traffic routes through here."
  · Memory register: NUNTIUS is in the build horizon. No code,
    no schema, no architecture document exists.

**NUNTIUS is the hub that replaces the dual-POST client pattern with a
centralised routing layer. All Exocognii apps write once. NUNTIUS
fans out to all registered consumers.**

---

---

# II. PHASE 1 — IDEA BRIEF

---

╭──────────────────────────────┬────────────────────────────────────────╮
│  Field                       │  Content                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  App Name                    │  NUNTIUS                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  One-Line Purpose            │  A centralised FastAPI message hub     │
│                              │  that receives Involucrum payloads     │
│                              │  from all Exocognii applications and   │
│                              │  fans them out to all registered       │
│                              │  consumer services, eliminating        │
│                              │  direct app-to-service coupling.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Platform                    │  Debian Trixie / Python 3.11           │
│                              │  FastAPI service — no GUI              │
│                              │  Port: TBD (Wizard ratifies;          │
│                              │  candidate: 8730 — sits below          │
│                              │  Exvacua Loricum at 8731)              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Core Loop                   │  1. App constructs one Involucrum      │
│                              │     payload                            │
│                              │  2. App POSTs to NUNTIUS /emit         │
│                              │  3. NUNTIUS fans out to all            │
│                              │     registered consumers               │
│                              │     (fire-and-forget per consumer)     │
│                              │  4. NUNTIUS returns 202 Accepted       │
│                              │     immediately — does not wait for    │
│                              │     consumer acknowledgement           │
│                              │  5. Each consumer receives and         │
│                              │     processes independently            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Key Features (v1)           │  · Single POST endpoint /emit          │
│                              │  · Consumer registry — services        │
│                              │    declared in Configuus, not          │
│                              │    hard-coded in NUNTIUS               │
│                              │  · Async fan-out — all consumers       │
│                              │    receive in parallel via             │
│                              │    asyncio.gather                      │
│                              │  · Per-consumer failure isolation —    │
│                              │    one consumer down does not          │
│                              │    block others or the emitting app    │
│                              │  · Emission log — SQLite ring buffer   │
│                              │    of recent Involucrum payloads       │
│                              │    with delivery status per consumer   │
│                              │  · /status endpoint — health of        │
│                              │    NUNTIUS and all registered          │
│                              │    consumers                           │
│                              │  · /log endpoint — recent emissions,   │
│                              │    consumer delivery outcomes          │
│                              │  · Replaces the dual-POST shared       │
│                              │    client library — apps import        │
│                              │    NuntiusClient instead               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Explicit Out of Scope (v1)  │  · Guaranteed delivery / retry queues  │
│                              │  · Consumer acknowledgement waiting    │
│                              │  · Message transformation per          │
│                              │    consumer                            │
│                              │  · Consumer-side filtering             │
│                              │    (consumers receive all emissions)   │
│                              │  · Authentication / payload signing    │
│                              │  · Remote (non-local) transport        │
│                              │  · Admin UI (PRAESIDIUM widget         │
│                              │    reads /status — that is the UI)     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Technical Risks             │  · Fan-out latency: if a consumer      │
│                              │    hangs, asyncio.gather with          │
│                              │    per-consumer timeout prevents       │
│                              │    stall propagation. Timeout must     │
│                              │    be short (2s default).              │
│                              │  · SQLite write contention: emission   │
│                              │    log writes happen on every POST.    │
│                              │    WAL mode required.                  │
│                              │  · Migration from dual-POST: existing  │
│                              │    apps (PRAESIDIUM, Dolium, etc.)     │
│                              │    currently import the unnamed        │
│                              │    shared client. All must be          │
│                              │    updated to NuntiusClient.           │
│                              │    This is a migration, not just       │
│                              │    a new build.                        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Visual Identity             │  No UI. FastAPI service.               │
│                              │  PRAESIDIUM widget consumes            │
│                              │  /status for display.                  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  v2 Wishlist                 │  · Per-consumer payload filtering      │
│                              │    (hint-based routing rules)          │
│                              │  · Retry queue with exponential        │
│                              │    backoff for failed consumer         │
│                              │    deliveries                          │
│                              │  · Dead-letter store for emissions     │
│                              │    that failed all consumers           │
│                              │  · PRAESIDIUM emission stream widget   │
│                              │    (live tail of /log)                 │
│                              │  · Mundana State Bus integration —     │
│                              │    NUNTIUS emits on mundana.nuntius    │
│                              │    on every fan-out for real-time      │
│                              │    pipeline visibility                 │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Open Questions              │  · Port number: 8730 is proposed.     │
│                              │    Confirm before Configuus update.   │
│                              │  · The unnamed shared client library   │
│                              │    in the interim dual-POST design —   │
│                              │    does it get canonically named       │
│                              │    NuntiusClient, or does that name    │
│                              │    belong only to the hub-aware        │
│                              │    v2 client? Recommendation: one      │
│                              │    name, one client. The old pattern   │
│                              │    is retired on NUNTIUS build.        │
│                              │  · Consumer timeout default (2s):      │
│                              │    confirm acceptable for all          │
│                              │    registered consumers.               │
╰──────────────────────────────┴────────────────────────────────────────╯


## Consumer Registry (v1)

Consumers are declared in Configuus under `nuntius.consumers`. NUNTIUS
reads this list at startup. No consumers are hard-coded in service code.

╭──────────────────────────────┬────────────────────────────────────────╮
│  Consumer                    │  Endpoint                              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Exvacua Loricum             │  http://localhost:8731/lorix           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Perpetuum Aedificare        │  http://localhost:8732/acquiuum        │
╰──────────────────────────────┴────────────────────────────────────────╯

New consumers are added to Configuus only. No code change to NUNTIUS
required. This is the primary extensibility mechanism.


## Relationship to Mundana State Bus

NUNTIUS and the Mundana State Bus are complementary, not competing:

  · Mundana State Bus — real-time state. High frequency. Celestial
    and app presence signals. Ephemeral. Unix socket.

  · NUNTIUS — durable observation routing. Low-to-medium frequency.
    Narrative content (what the Wizard said, what was built, what
    lore emerged). HTTP. SQLite emission log.

They do not replace each other. An app may use both: Mundana State
Bus for live heartbeat and token counts, NUNTIUS for Involucrum
observation payloads.


## Architecture Decision Record

**FastAPI over raw socket.**
NUNTIUS handles Involucrum payloads — narrative, structured JSON,
moderate frequency. HTTP overhead is acceptable. FastAPI gives the
/status and /log endpoints for free and integrates cleanly with
the existing Exvacua Loricum / Perpetuum Aedificare service pattern.

**202 Accepted, not 200 OK.**
NUNTIUS returns 202 immediately on receipt. Fan-out is async and
post-response. Apps must never block on consumer delivery.

**Consumer timeout: 2 seconds per consumer.**
Prevents one slow or absent consumer from stalling the fan-out
for all others. Consumer failure is logged; it does not propagate.

**SQLite emission log, WAL mode.**
Provides a recent history of what was emitted and whether each
consumer received it. Ring buffer — configurable max rows.
WAL mode mandatory to handle concurrent fan-out writes safely.

**Migration is a first-class concern.**
PRAESIDIUM, Dolium, and any other app using the current dual-POST
unnamed client must be migrated to NuntiusClient. The build document
must include a migration checklist covering every affected app.

---

---

# III. PHASE 2 — SEED PROMPT

---

```
You are a senior software architect writing for an experienced Linux
developer.
Produce complete, developer-ready construction documentation for
"NUNTIUS" — a Python 3.11 FastAPI service with no GUI.

NUNTIUS is a centralised Involucrum message hub that receives observation
payloads from all Exocognii desktop applications via a single POST
endpoint and fans them out asynchronously to all registered consumer
services, eliminating direct app-to-service coupling across the suite.

Architecture pipeline in execution order:
  1. App constructs one Involucrum JSON payload.
  2. App calls NuntiusClient.emit(payload) — one HTTP POST to /emit.
  3. NUNTIUS logs the emission to SQLite (WAL mode) and returns 202
     Accepted immediately.
  4. NUNTIUS fans out to all consumers in parallel via asyncio.gather,
     with a per-consumer timeout of 2 seconds.
  5. Each consumer delivery outcome (success / timeout / error) is
     written to the emission log.
  6. Consumer services receive and process independently.

Architecture decisions to enforce — do not soften or defer any:

  - Transport: FastAPI on localhost:{port}. Port declared in Configuus
    under nuntius_api. Candidate port: 8730.
  - Single ingest endpoint: POST /emit — accepts Involucrum envelope.
    No per-consumer routing logic in the app. No target field.
  - Consumer registry: declared in Configuus under nuntius.consumers
    as a list of {name, url} objects. NUNTIUS reads at startup.
    No consumers hard-coded in service code. New consumers require
    only a Configuus entry — no NUNTIUS code change.
  - Fan-out: asyncio.gather with per-consumer httpx.AsyncClient POST.
    Each consumer receives the full Involucrum payload unmodified.
    Per-consumer timeout: 2 seconds. Consumer failure is logged and
    isolated — does not affect other consumers or block the emitting
    app.
  - Response: 202 Accepted on receipt. NUNTIUS never waits for
    consumer acknowledgement before responding.
  - Emission log: SQLite, WAL mode. Table: emissions. Columns:
    id, timestamp, source_app, payload (JSON text), consumer_name,
    consumer_url, outcome (success|timeout|error), status_code,
    error_detail. Ring buffer — max rows configurable in Configuus
    under nuntius.log_max_rows (default: 10000).
  - Client library: NuntiusClient class in
    ArcaCognitorium/Exocognii/Nuntius/nuntius_client.py.
    Replaces the current unnamed dual-POST shared client.
    API: NuntiusClient(config_path).emit(payload_dict) — fire and
    forget. Raises NuntiusDaemonNotRunningError if service unreachable.
    Apps catch and degrade gracefully — observation loss is
    acceptable; app function must not be gated on NUNTIUS.
  - /status endpoint: returns NUNTIUS health + per-consumer last-seen
    timestamp and last delivery outcome.
  - /log endpoint: returns paginated recent emission records with
    consumer delivery outcomes.
  - Startup: launched by PRAESIDIUM launcher or
    python -m Nuntius. Apps never start NUNTIUS.
  - Shutdown: SIGTERM / SIGINT caught. Graceful uvicorn shutdown.
  - Migration: NuntiusClient replaces the current dual-POST unnamed
    client. All existing apps that emit Involucrum payloads must be
    migrated. The document must include a migration checklist covering
    all affected apps: PRAESIDIUM, Dolium v2, and any future apps.

snake_case throughout. No filler. Every sentence carries information.
Write for a senior developer. Assume familiarity with FastAPI,
asyncio, httpx, and SQLite WAL mode.

Sections:

1. Overview & Architecture
   - One paragraph summary of purpose and role in the Exocognii suite
   - Relationship to Mundana State Bus — clarify these are distinct
     systems with complementary roles
   - Component table: Name | Role (one line each)
     Include: NUNTIUS daemon, NuntiusClient, Consumer Registry,
     Emission Log, /status endpoint, /log endpoint

2. Tech Stack
   Table: Tool | Version | Justification
   Include: Python 3.11, FastAPI, uvicorn, httpx (async),
   SQLite (stdlib), asyncio (stdlib), pathlib (stdlib)
   Justify httpx over aiohttp. Justify FastAPI over raw socket
   (contrast explicitly with Mundana State Bus transport decision).

3. Directory Tree
   Full annotated tree for:
   ArcaCognitorium/
   └── Exocognii/
       └── Nuntius/
   Include: __main__.py, nuntius_app.py, nuntius_client.py,
   nuntius_registry.py, nuntius_log.py, nuntius_config.py,
   __init__.py, tests/, requirements.txt, launch_nuntius.sh

4. Module Breakdown
   Table: Module | Responsibility | Inputs | Outputs | Dependencies
   Cover: nuntius_app, nuntius_client, nuntius_registry,
   nuntius_log, nuntius_config, __main__

5. Configuus Extension
   - Show the full Configuus block NUNTIUS requires:
     nuntius_api, nuntius.consumers (list), nuntius.log_max_rows,
     nuntius.consumer_timeout_seconds
   - Show a complete example Configuus snippet with both consumers
     (Exvacua Loricum, Perpetuum Aedificare) populated

6. Involucrum Contract
   - Restate the Involucrum schema (source_app, source_version,
     timestamp, hint, body)
   - Specify exactly what NUNTIUS does and does not modify
     (nothing — payload is forwarded verbatim)
   - Specify the emission log schema (all columns, types, notes)
   - Specify the /status response schema
   - Specify the /log response schema with pagination fields

7. Data Flow — 3 labeled paths:
   (a) Happy path: app emits → NUNTIUS logs → 202 returned →
       fan-out fires → both consumers receive → outcomes logged
   (b) Consumer timeout: one consumer hangs past 2s → timeout
       recorded in emission log → other consumers unaffected →
       202 already returned to app — no re-raise
   (c) NUNTIUS not running: NuntiusClient.emit() raises
       NuntiusDaemonNotRunningError → calling app catches →
       logs warning locally → continues without observation
       (graceful degradation contract)

8. Migration Guide
   - List every app currently using the dual-POST unnamed client
     pattern: PRAESIDIUM, Dolium v2 (and any others discovered
     in codebase audit)
   - Step-by-step migration per app:
     a. Install NuntiusClient import
     b. Remove dual-POST calls
     c. Replace with NuntiusClient(config).emit(payload)
     d. Wrap in try/except NuntiusDaemonNotRunningError
     e. Verify with test_emit in integration test
   - Note: the unnamed dual-POST client library is retired and
     must not be imported after migration

9. Code Stubs
   All public classes and methods. Type hints. One-line docstrings.
   Critical implementations must include pseudocode:
   - NuntiusApp.emit() — log write, 202 response, background
     fan-out trigger
   - NuntiusApp._fan_out() — asyncio.gather with timeout,
     outcome logging pseudocode
   - NuntiusClient.emit() — httpx POST, error handling,
     NuntiusDaemonNotRunningError raise pseudocode
   - NuntiusRegistry.load_from_configuus() — consumer list parse
   - NuntiusLog.record() — atomic WAL write, ring buffer purge

10. Error Handling
    Per-module table: Error | Cause | Strategy
    Include: NuntiusDaemonNotRunningError, consumer timeout,
    consumer HTTP error, malformed Involucrum payload (missing
    required fields), SQLite write failure, Configuus missing
    nuntius block.
    Include startup failure paths — what happens if Configuus
    is absent or consumers list is empty.

11. Setup & Testing
    - requirements.txt (full content)
    - Install and run commands
    - launch_nuntius.sh verbatim
    - Unit tests:
      · test_emit_returns_202.py — single emit, correct response
      · test_fanout_parallel.py — two consumers both receive payload
      · test_consumer_timeout.py — slow consumer times out, others
        unaffected
      · test_degraded_mode.py — NuntiusDaemonNotRunningError on
        NuntiusClient when service absent
      · test_emission_log.py — log entry written with correct
        consumer outcomes
      · test_registry_from_configuus.py — consumers loaded correctly

12. Extensibility — 5 features
    Name | User Value | Implementation Approach
    Include: hint-based consumer filtering, retry queue with
    backoff, dead-letter store, PRAESIDIUM live emission stream
    widget, Mundana State Bus integration on fan-out events
```

---

---

*⟁*

*Ordo Discordia, Cosmos Inania*
*NUNTIUS — IdeaForge v1.0*
