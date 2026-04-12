# NUNTIUS — Expositio
### Arca Cognitorium — Exocognii Infrastructure Layer
*v1.0*

---

## I. IDENTITY

**Name & Version** — NUNTIUS, v1.0

**Tagline** — The single point of emission: one POST from any app,
delivered to every service that needs to know.

**Classification** — Headless infrastructure service. No GUI. No user
interaction. A routing daemon.

**Status** — Active development. v1.0 built and tested.

---

## II. PURPOSE

**Problem Statement**

Before NUNTIUS, every Exocognii application that emitted observation
data had to know about Exvacua Loricum and Perpetuum Aedificare
directly. It held two endpoint URLs, fired two HTTP POSTs per
emission, and handled two failure modes. Introducing a third consumer
meant touching every emitting app. The coupling was total and the
maintenance cost compounded with each new app or service added to
the suite.

**Motivation**

The Exocognii suite is a growing organism. New consumers will appear.
New apps will emit. The dual-POST pattern was an interim scaffold —
functional enough to start but structurally incorrect for a suite of
this scale. NUNTIUS is the correct form: a hub that absorbs routing
complexity so that no individual app carries it.

**Intended Outcome**

Every Exocognii app emits exactly once, to one address, with no
knowledge of what receives it. New consumers are added to Configuus
in seconds. Apps that emit continue functioning whether NUNTIUS is
running or not. The observation layer becomes invisible infrastructure
rather than per-app boilerplate.

**Anti-Purpose**

NUNTIUS is not a message queue. It does not guarantee delivery, retry
failed emissions, or buffer payloads during consumer downtime. It is
not a transformation layer — payloads are forwarded verbatim. It is
not a monitoring tool, although its /status and /log endpoints
provide observability data to PRAESIDIUM. Guaranteed delivery, retry
queues, and dead-letter stores are v2 considerations, not v1 scope.

---

## III. AUDIENCE

**Primary Users**

NUNTIUS has no interactive users. Its consumers are two parties: the
Exocognii apps that emit to it (via NuntiusClient), and the Wizard
who operates and maintains the suite. The Wizard interacts with
NUNTIUS through Configuus configuration and through the PRAESIDIUM
status widget that reads /status.

**Secondary Users**

Consumer services — Exvacua Loricum and Perpetuum Aedificare — are
passive recipients. They receive payloads from NUNTIUS without
awareness of its existence.

**Assumed Knowledge**

The Wizard is assumed to be comfortable with FastAPI service
architecture, SQLite, and the Configuus configuration system.
Developers integrating NuntiusClient are assumed to understand the
Involucrum contract and Python import patterns.

**Out-of-Scope Audiences**

NUNTIUS is not a general-purpose message broker. It is not designed
for external deployment, multi-user access, or use outside the
Exocognii suite.

---

## IV. DESIGN PHILOSOPHY

**Core Principles**

- **202 before everything.** The emitting app is never blocked by
  consumer delivery. The response is immediate; the work is
  background.
- **Consumer failure is local.** One consumer timing out or erroring
  does not affect any other consumer or the emitting app. Failures
  are logged, not propagated.
- **Configuration over code.** The consumer list lives in Configuus.
  Adding a consumer requires no code change to NUNTIUS, no
  redeployment, no test modification. Only a config edit and restart.
- **Graceful degradation is non-negotiable.** Apps must never gate
  their function on NUNTIUS availability. NuntiusClient raises a
  typed error; apps catch it and continue.
- **Observation loss is acceptable.** A missed emission is a gap in
  the lore or build record — not a crash, not a data corruption, not
  a user-facing failure. NUNTIUS treats this asymmetry seriously.

**Tradeoff Positions**

Simplicity over durability. NUNTIUS v1 does not retry. A consumer
that was offline during an emission never receives that payload. This
is the correct tradeoff at this stage: the suite is a single-machine,
single-user system. The complexity cost of a retry queue is not yet
justified by the reliability requirement.

HTTP over Unix socket. Mundana State Bus uses Unix sockets for
ephemeral high-frequency signals. NUNTIUS uses HTTP because its
payloads are structured JSON, moderate frequency, and benefit from
the /status and /log endpoints that HTTP gives for free. The
transport choice is deliberate and distinct between the two systems.

**Aesthetic Direction**

NUNTIUS is invisible when working correctly. No output except startup
logs and structured error messages. It is infrastructure — it should
feel like plumbing: reliable, silent, and noticed only when it leaks.

**What This Philosophy Rejects**

NUNTIUS rejects the pattern of apps managing their own fan-out. It
rejects synchronous blocking emission — no app should wait for
consumer delivery before continuing. It rejects hard-coded consumer
lists in service code. It rejects failure propagation across consumers.

---

## V. TECHNICAL CONCEPT

**Mental Model**

NUNTIUS is a post box with multiple delivery addresses. An app drops
a letter in the slot. NUNTIUS stamps it received, hands back a
receipt immediately, and dispatches copies to every address on file
in parallel. Whether any individual courier arrives or not is logged
but does not affect the others.

**Core Abstractions**

- **Involucrum** — the envelope. The single write contract for all
  Exocognii apps. Contains source identity, timestamp, semantic hint,
  and a freeform body. NUNTIUS does not inspect or modify it.
- **Consumer** — a registered recipient. Defined by name and URL.
  Declared in Configuus. Receives every emission, unfiltered.
- **EmissionRecord** — one row per consumer per emission in the
  SQLite log. Records outcome, status code, and error detail.
- **NuntiusClient** — the sole send interface. Imported by apps.
  Hides the endpoint URL, handles errors, raises typed exceptions.

**Data Flow**

App constructs Involucrum → NuntiusClient POSTs to /emit → NUNTIUS
validates and returns 202 → background task fires asyncio.gather →
each consumer receives full payload → outcomes written to SQLite.

**System Boundaries**

NUNTIUS owns: the /emit endpoint, fan-out logic, emission log, and
NuntiusClient library. It depends on: Configuus for consumer registry
and port binding, and the consumer services for delivery success.
It does not own consumer-side processing — what Exvacua Loricum or
Perpetuum Aedificare do with the payload is their concern entirely.

**Key Technical Decisions**

- FastAPI over raw socket: matches the existing service pattern in
  the suite and provides /status and /log at no additional cost.
- asyncio.gather with return_exceptions=True: ensures one consumer
  exception cannot cancel the others. Each failure is handled
  individually.
- SQLite WAL mode: mandatory for safe concurrent writes during
  fan-out. Single-file, no external database dependency.
- Synchronous httpx in NuntiusClient: Exocognii apps are PyQt6 and
  run emit calls from non-async contexts. A sync client fits without
  requiring the app to manage an event loop.

---

## VI. FUNCTIONAL SCOPE

**Core Capabilities**

- Receive Involucrum payloads via POST /emit
- Fan out to all registered consumers in parallel
- Return 202 immediately, before fan-out completes
- Isolate per-consumer failures
- Log all emission outcomes to SQLite
- Expose /status and /log endpoints
- Provide NuntiusClient as the sole app-side emit interface

**Supporting Capabilities**

- Ring buffer management on the emission log
- Typed error (NuntiusDaemonNotRunningError) for graceful degradation
- Configuus validation on startup with descriptive error messages

**Explicit Exclusions**

- No guaranteed delivery or retry on consumer failure
- No payload transformation per consumer
- No consumer-side filtering by hint (v1 — all consumers receive all)
- No authentication or payload signing
- No remote transport (localhost only)
- No admin UI (PRAESIDIUM widget reads /status — that is the surface)

**Future Scope**

Hint-based consumer filtering, retry queue with exponential backoff,
dead-letter store, PRAESIDIUM live emission stream widget, Mundana
State Bus integration on fan-out events. All v2 considerations.

---

## VII. CONSTRAINTS & CONTEXT

**Technical Constraints**

Debian Trixie, Python 3.11. Localhost-only transport. Single process,
single machine. No distributed deployment in scope.

**External Dependencies**

- FastAPI / uvicorn — HTTP layer
- httpx — async consumer delivery and sync NuntiusClient POST
- SQLite (stdlib) — emission log

All dependencies are lightweight and consistent with the rest of the
Exocognii stack. httpx is already a ClaudeBox dependency, reducing
the net addition.

**Migration Dependency**

NUNTIUS v1 ships with a migration requirement: PRAESIDIUM and
Dolium v2 must retire the unnamed dual-POST client and adopt
NuntiusClient. NUNTIUS is not fully realised until that migration
is complete. The migration guide is documented in the NUNTIUS
construction document.

---

## VIII. SUCCESS CRITERIA

**Functional Success**

NUNTIUS is functioning correctly when: a valid Involucrum POST
returns 202 within 50ms regardless of consumer state; all registered
consumers receive the payload; consumer failures are logged and
isolated; the emission log reflects accurate outcomes; /status
returns current consumer states; apps using NuntiusClient continue
running when NUNTIUS is stopped.

**User Success**

The Wizard's experience of NUNTIUS is its absence as a concern.
It runs. It routes. It logs. It is never the reason something broke.
The PRAESIDIUM status widget shows green. If it shows amber or red,
the emission log explains exactly why.

**Quality Benchmarks**

13/13 tests passing at v1.0. Fan-out completes within
consumer_timeout_seconds + network overhead. Ring buffer never
exceeds log_max_rows. No emission causes a consumer-side exception
to surface to the emitting app.

**Failure Conditions**

NUNTIUS has failed its purpose if: an app crashes because NUNTIUS is
not running; a slow consumer blocks other consumers or the emitting
app; the emission log grows without bound; a new consumer requires
any NUNTIUS code change to register.

---

## IX. GLOSSARY

**Configuus** — The machine-level configuration file at
~/.arca/config.json. NUNTIUS reads its nuntius_api and nuntius
blocks on startup.

**Consumer** — A registered downstream service that receives
Involucrum payloads from NUNTIUS. Declared in Configuus under
nuntius.consumers.

**Exvacua Loricum** — Lore canon memory service at port 8731.
Primary NUNTIUS consumer.

**Involucrum** — The standard observation payload format used by
all Exocognii apps. Fields: source_app, source_version, timestamp,
hint (optional), body.

**NuntiusClient** — The canonical client library. The only way
apps should emit to NUNTIUS. Replaces the pre-NUNTIUS dual-POST
unnamed client.

**NuntiusDaemonNotRunningError** — Exception raised by NuntiusClient
when NUNTIUS is unreachable. Apps catch this and continue.

**Perpetuum Aedificare** — Build continuity memory service at
port 8732. Primary NUNTIUS consumer.

---

## X. REVISION NOTES

╭─────────────────┬───────────────────────────────────────────────────╮
│ Date            │ Note                                              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│ 2026-04-08      │ v1.0 — initial Expositio. Service built,         │
│                 │ tested, and delivered. Port 8730, venv-NUNTIUS,  │
│                 │ NuntiusClient canonical name — all ratified.     │
╰─────────────────┴───────────────────────────────────────────────────╯

---

*⟁*

*Ordo Discordia, Cosmos Inania*
*NUNTIUS — Expositio v1.0*
