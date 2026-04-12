# COGNOSIS
### Expositio · v1.0 · Arca Cognitorium — Exocognii Suite

---

## I. IDENTITY

**Name & Version:** Cognosis · v1.0

**Tagline:** Three services. One memory organism. Nothing manually documented.

**Classification:** Suite of three local FastAPI memory services forming the
ambient memory layer of the Exocognii ecosystem — lore canon, build
continuity, and Wizard-facing advisory interface.

**Status:** Exvacua Loricum and Perpetuum Aedificare built and running.
Praesidium read layer and Nuntius client wiring are the remaining Tier 4
work.

---

## II. PURPOSE

**Problem Statement:** The Arca Cognitorium generates two distinct and
valuable kinds of memory: lore — the world-building, naming, cosmological, and
narrative content that gives the Tower its texture — and build continuity —
the current state, open questions, and momentum of active development work.
Both kinds of memory exist implicitly in sessions and conversations. Neither
is captured reliably without a dedicated system. Without capture, every new
session begins from a partial picture.

**Motivation:** The Tower should remember. Not because the Wizard maintains a
log, but because the system watches and infers. The motivation for Cognosis
was to make memory a property of the ecosystem, not of the Wizard's diligence.

**Intended Outcome:** After Cognosis is fully wired, every Exocognii app
emission leaves a trace. Lore accumulates in Exvacua Loricum and surfaces
through Judicium ratification into a living canon. Build state accumulates
in Perpetuum Aedificare and surfaces through Praesidium as a current picture
of active work. The Wizard is never starting from scratch.

**Anti-Purpose:** Cognosis is not a document store. It is not a file manager.
It is not a note-taking application. It is an inference and ratification
layer — it transforms ambient emissions into structured, intentional memory.

---

## III. AUDIENCE

**Primary Users:** LordFingers — sole Wizard. Interacts with Exvacua Loricum
through Judicium ratification. Interacts with Perpetuum Aedificare through
Praesidium's advisory surface and the Nota Brevis quick capture path.

**Secondary Users:** All Exocognii applications as write clients via Nuntius.
Praesidium as the primary read client for both services.

**Assumed Knowledge:** The Wizard understands the Cogniverse lore register and
the concept of Nodi Momentuum as units of work. App authors need only know
the Involucrum format and the Nuntius import pattern.

**Out-of-Scope Audiences:** Anyone expecting real-time synchronisation, cloud
storage, or multi-user access. Cognosis is a local, single-Wizard system.

---

## IV. DESIGN PHILOSOPHY

**Core Principles:**

Apps emit. Cognosis infers. The Wizard ratifies. This division of
responsibility is inviolable. Apps never decide what is lore or what is
build-relevant — that determination belongs to Exvacua Loricum and Perpetuum
Aedificare respectively.

Both services are sovereign. If one is down, the other continues receiving
writes. There is no shared ingest layer, no routing dependency between them.
Nuntius fires both POST calls fire-and-forget.

Nothing is deleted. Both services retain rejected, ignored, and dismissed
content as classified records. Only status changes — never removal.

The Wizard is the only ratification authority. Exvacua Loricum never promotes
a Lorix to canon on its own. Perpetuum Aedificare never finalises a node as
resolved without Wizard action.

**Tradeoff Positions:** Inference quality over ingestion speed. Both services
use Claude for classification, which costs API calls. This is deliberate —
the alternative is the Wizard manually tagging every emission.

**Aesthetic Direction:** Invisible infrastructure. Cognosis should be felt
rather than operated. The Wizard interacts with its outputs — the Loricum
Ratifex, the Judicium ceremony, the Praesidium work graph — not with the
plumbing underneath.

**What This Philosophy Rejects:** Passive archiving without inference. A
system that only stores and retrieves without classifying is a search problem,
not a memory problem. Cognosis is a memory problem.

---

## V. TECHNICAL CONCEPT

**Mental Model:** Two accumulation-and-distillation pipelines running in
parallel, sharing a common write format (Involucrum), a common client library
(Nuntius), and a common read surface (Praesidium). Each pipeline has its own
ingest layer, its own Claude-powered distillation engine, and its own canon
or graph output.

**Core Abstractions:**

The Involucrum is the write contract. Every app constructs one envelope per
emission: source app, version, timestamp, optional hint, and body. Nuntius
fires this envelope to both services simultaneously.

Exvacua Loricum's pipeline: raw captures → Lorixii Speculativum → Actio
Interpretus classification → Judicium ratification → Loridex Cards +
Exlorica + Loricum Ratifex.

Perpetuum Aedificare's pipeline: raw captures → Acquiuum Chronex → Actio
Aggrexuum aggregation → Nodus Momentuum graph + Driftuum Sentifex scoring.

Praesidium is the read layer above both. It queries Exvacua Loricum for lore
content and Perpetuum Aedificare for build continuity, and surfaces both
to the Wizard through the Praesidium UI widgets.

**Data Flow:** App event occurs → Nuntius fires two POST calls simultaneously
→ Exvacua Loricum receives (lore classification pipeline begins) → Perpetuum
Aedificare receives (build aggregation pipeline begins) → each service
processes independently on its own cadence → Praesidium reads the results.

**System Boundaries:** Cognosis is outside the Tower. The Tower receives
nothing from Cognosis. Perpetuum Aedificare can hold read-only references to
Tower constructs via Arca Absoluticum, but the Tower is not aware of this.
Exvacua Loricum is entirely independent of the Tower.

**Key Technical Decisions:** Two separate services rather than one unified
service — lore memory and build memory have different cadences, different
distillation logics, and different canon structures. Coupling them would
compromise both. The common write format (Involucrum) and common client
library (Nuntius) provide the unification without the coupling.

---

## VI. FUNCTIONAL SCOPE

**Core Capabilities:** Ambient emission capture from all Exocognii apps.
Lore classification and ratification via Exvacua Loricum. Build continuity
tracking and drift detection via Perpetuum Aedificare. Shared Involucrum
write format. Nuntius client library for uniform app-side emission. Praesidium
advisory read surface.

**Supporting Capabilities:** Manual Wizard capture via Nota Brevis (build)
and file drop / Lorixii Extractuum (lore). Direct editing of canon content
and work node state. Taxonomy governance via Arx Loricuum. Configurable
distillation cadence and thresholds.

**Explicit Exclusions:** No cloud sync. No multi-user support. No Tower write
access. No real-time event streaming to external consumers.

**Future Scope:** Nuntius wired to all existing Exocognii apps. Praesidium
read layer. Exvacua Loricum Session B — Judicium UI and `.wiz` rendered
output.

---

## VII. CONSTRAINTS & CONTEXT

**Technical Constraints:** Python 3.11+. FastAPI. SQLite (local). Ports 8731
(Exvacua Loricum) and 8732 (Perpetuum Aedificare). ClaudeBox via canonical
repo path. All paths resolved via `~/.arca/config.json`.

**External Dependencies:** ClaudeBox — all inference calls for both services.
Nuntius — shared client library, lives in `Exocognii/Shared/`. uvicorn.

---

## VIII. SUCCESS CRITERIA

**Functional Success:** Both services start independently, accept Involucrum
payloads, run their respective distillation passes on schedule, and produce
correct canon or graph output. Nuntius fires to both without the emitting app
needing to know either service exists.

**User Success:** The Wizard can ask "what is the current state of Dolium v2"
and Praesidium can answer accurately from Perpetuum Aedificare without the
Wizard having written a status update. The Wizard can look at the Loricum
Ratifex and recognise lore that emerged from actual build conversations, now
ratified and structured.

**Failure Conditions:** If the two services develop dependency on each other
at the data layer, the architecture has failed. If Nuntius ever makes both
POST calls synchronously and waits on responses, it has broken the
fire-and-forget contract.

---

## IX. GLOSSARY

**Cognosis** — the collective name for the three Cognosis services: Exvacua
Loricum, Perpetuum Aedificare, and Praesidium.

**Involucrum** — the shared write contract. The envelope format all apps use
to emit to Cognosis services.

**Nuntius** — the shared client library. The utility imported by every app
to fire Involucrum payloads to both services simultaneously.

**Exvacua Loricum** — lore canon memory service. Port 8731.

**Perpetuum Aedificare** — build continuity memory service. Port 8732.

**Praesidium** — the Wizard-facing advisory interface. Read layer above both
services. Not a write client.

**Actio Interpretus** — Exvacua Loricum's classification engine.

**Actio Aggrexuum** — Perpetuum Aedificare's aggregation engine.

---

## X. REVISION NOTES

**v1.0 — 2026-03-28**
Suite named Cognosis. Exvacua Loricum and Perpetuum Aedificare built.
Nuntius named and specified. Praesidium read layer and Nuntius wiring to
existing apps deferred to remaining Tier 4 work.
