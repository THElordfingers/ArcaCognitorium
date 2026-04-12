# EXVACUA LORICUM
### Expositio · v1.0 · Arca Cognitorium — Exocognii Suite

---

## I. IDENTITY

**Name & Version:** Exvacua Loricum · v1.0

**Tagline:** The lore accumulates. Exvacua Loricum decides what becomes canon.

**Classification:** Local FastAPI memory service — passive ingestion layer with
active ratification interface and living canon synthesis engine.

**Status:** Active development. Core service built and functional. Judicium UI
and rendered output (`.wiz`) are Session B work, not yet built.

---

## II. PURPOSE

**Problem Statement:** The Cogniverse generates lore continuously and
incidentally — in conversation, in build sessions, in the names of things
and the decisions made about them. None of it is captured systematically.
By the time a lore document is wanted, the source material is scattered
across dozens of conversation exports and build notes, half of it paraphrased
or forgotten. The Wizard should not have to be a diligent archivist to have
a living lore record.

**Motivation:** The Tower is an organism, not a database. Its world should
deepen over time without the Wizard manually curating every detail. The
motivation was to build a system that watches passively, infers intelligently,
and asks for Wizard judgment only at the moment it matters — ratification —
not at every emission.

**Intended Outcome:** After Exvacua Loricum is running, every conversation
about the Cogniverse leaves a trace. Over time, the lore corpus grows without
deliberate effort. The Wizard is invited to ratify, not to document. The Tower
entities have access to a living canon that reflects the actual history and
texture of their world.

**Anti-Purpose:** Exvacua Loricum does not generate lore. It does not invent
names, history, or cosmology. It observes what already exists and asks whether
it should be kept. Creation remains entirely with the Wizard and the entities.

---

## III. AUDIENCE

**Primary Users:** LordFingers — sole Wizard. Interacts via the Judicium
ratification interface and the Praesidium read layer. Also interacts
indirectly every time any Exocognii app emits to the service.

**Secondary Users:** All Exocognii applications as write clients. Praesidium
as the primary read client. Tower entities, once the Praesidium read layer
surfaces lore context into entity sessions.

**Assumed Knowledge:** The Wizard understands the Cogniverse register,
the naming conventions, and the concept of lore as distinct from operational
build notes. Apps writing to the service need only know the Involucrum format.

**Out-of-Scope Audiences:** Any user expecting a traditional tagging or
wiki interface. This is not a note-taking app. The Wizard does not write
lore into Exvacua Loricum — the Wizard ratifies what the system infers.

---

## IV. DESIGN PHILOSOPHY

**Core Principles:**

The Wizard is the authority, not the clerk. The system handles the clerical
work. The Wizard handles judgment.

Nothing becomes canon without explicit ratification. Inferences accumulate
quietly. The Judicium ceremony is the only gate.

Nothing is deleted. Rejected and ignored Lorixii are retained for audit.
Classification is the only operation applied to unwanted content.

The lore corpus is authored by two hands — the Loretic Crystalizer writes
from ratified canon, the Wizard edits directly. Both are legitimate. Neither
overwrites the other without flagging.

Aesthetics matter. Loridex Cards and Exlorica are rendered documents, not
database records. The Aestheticum system exists because lore should feel
like it was illuminated, not exported.

**Tradeoff Positions:** Inference quality over inference speed. Actio
Interpretus runs on a scheduled heartbeat with a threshold override — it is
not instantaneous, and that is deliberate. A slower, thoughtful classification
is preferable to a fast, noisy one.

**Aesthetic Direction:** Dense, tactile, authoritative. The feel of something
classified and filed by an ancient bureaucracy. Nothing casual, nothing
approximate.

**What This Philosophy Rejects:** Auto-canonisation. The system never
promotes a Lorix to canon on its own authority. It drafts, presents, and
waits.

---

## V. TECHNICAL CONCEPT

**Mental Model:** A two-stage accumulation and ratification pipeline. The
Lorixii Speculativum is the unratified pile — everything the system has
observed but not yet judged. The canon layer (Loridex Cards + Exlorica +
Loricum Ratifex) is the ratified record. The Judicium ceremony is the gate
between them. Nothing crosses the gate without the Wizard.

**Core Abstractions:**

A Lorix is the atomic unit of observed content — raw, unmodified, sourced,
and classified by Actio Interpretus with a confidence level and an inferred
domain.

A Loridex Card is a structured canon index entry — title, domain, tags,
source Lorixii. Compact. Authoritative. The spine of a canon entry.

An Exloricum is the long-form prose document bound to a Loridex Card. Where
the Card is a classification, the Exloricum is the actual lore text. Dense,
atmospheric, treated as a living document.

The Loricum Ratifex is the master compendium — one document, sectioned by
domain, updated by the Loretic Crystalizer after every ratification, editable
directly by the Wizard. The two authorship tracks coexist via provenance
comments.

The Arx Loricuum is the taxonomy register — seeded domains and emergent tags,
all Wizard-governable.

**Data Flow:** Apps emit Involucrum payloads → Lorixii Speculativum accumulates
pending content → Actio Interpretus classifies (lore-relevant or ignored),
infers domain and tags → Actio Interpretus clusters related Lorixii by domain
→ Judicium session opens for a topic cluster → five phases: cull, elaborate,
draft Card, draft Exloricum, ratify → Sacramentum Finalitus writes to canon →
Loretic Crystalizer updates the Loricum Ratifex.

**System Boundaries:** Exvacua Loricum owns lore classification, ratification,
and canon storage. It does not own the Tower. It does not own entity behaviour.
It does not generate creative content — it synthesises from what the Wizard
and the build process have already produced.

**Key Technical Decisions:** SQLite over a full database server — this is a
local service for a single Wizard. FastAPI over a heavier framework —
endpoints are the interface, not a UI. Actio Interpretus as a scheduled
background engine rather than inline — keeping the write path fire-and-forget.

---

## VI. FUNCTIONAL SCOPE

**Core Capabilities:** Involucrum ingestion from all apps. File drop and
Lorixii Extractuum corpus scour. Claude-powered lore classification via Actio
Interpretus. Five-phase Judicium ratification ceremony. Loridex Card and
Exloricum production. Loricum Ratifex synthesis via Loretic Crystalizer.
Arx Loricuum taxonomy management. Full REST API surface.

**Supporting Capabilities:** Actio Revisicus — revision flagging for existing
canon when new lore creates tension. Direct Wizard editing of Exlorica and
Ratifex sections. Aestheticum bundle system for rendered output styling.
Scheduled heartbeat with threshold-triggered early firing.

**Explicit Exclusions:** No UI (Judicium UI is Session B work). No Tower
write access. No lore generation — synthesis only from existing material.
No multi-user support.

**Future Scope:** Judicium UI in Praesidium. Full `.wiz` rendered output via
Actio Duxuum. Aestheticum bundle authoring interface.

---

## VII. CONSTRAINTS & CONTEXT

**Technical Constraints:** Python 3.11+. FastAPI. SQLite — local file, no
server. Port 8731. ClaudeBox via canonical repo path. CLAUDE_API_KEY
environment variable. Paths resolved via `~/.arca/config.json`.

**External Dependencies:** ClaudeBox — all Actio Interpretus and Judicium
Claude calls route through it. PyYAML optional — fallback parser included.
uvicorn for serving.

**Regulatory or Compliance Context:** None. Entirely local. No network
exposure beyond localhost.

---

## VIII. SUCCESS CRITERIA

**Functional Success:** The service starts cleanly, accepts Involucrum
payloads from any app, runs Actio Interpretus on schedule, and produces
Loridex Cards and Exlorica when a Judicium session is committed.

**User Success:** The Wizard can open a Judicium session on a topic cluster,
move through the five phases, ratify, and see a new entry appear in the
Loricum Ratifex — without having manually written any of the source material
that fed it.

**Failure Conditions:** If Actio Interpretus classifies primarily as
`ignored` when real lore content is being emitted, the classification prompt
needs tuning. If the Judicium ceremony feels like data entry rather than
a ratification ritual, the UI design has failed its purpose.

---

## IX. GLOSSARY

**Lorix / Lorixii Speculativum** — the unratified accumulation layer. A Lorix
is one captured observation. Speculativum means speculative — pending judgment.

**Actio Interpretus** — the inference pass. Reads pending Lorixii, classifies
lore-relevance, infers domain and tags.

**Judicium Exlorica** — the ratification ceremony. Five phases from cull to
commit.

**Loridex Card** — structured canon index entry. Compact, classified, precise.

**Exloricum** — long-form prose canon document bound to a Loridex Card.

**Loricum Ratifex** — master lore compendium. One document, sectioned by domain.

**Loretic Crystalizer** — post-ratification engine. Updates the Ratifex after
every Sacramentum Finalitus.

**Sacramentum Finalitus** — Phase V of Judicium. The commit to canon.

**Arx Loricuum** — taxonomy register. Domains and tags, seeded and emergent.

**Aestheticum** — a bundle of rendering instructions governing the visual
output of Loridex Cards, Exlorica, and Ratifex sections.

**Actio Revisicus** — revision flagging. Triggered when new lore creates
tension with existing canon entries.

**Involucrum** — the shared write format. The envelope all apps use to emit
content to Cognosis services.

---

## X. REVISION NOTES

**v1.0 — 2026-03-28**
Initial build. Core service complete: ingestion, Actio Interpretus,
Judicium five-phase ceremony, Loretic Crystalizer, Loricum Ratifex.
Judicium UI and `.wiz` rendered output deferred to Session B.
Naming ratified this session: Nuntius (shared client), Cognosis (suite).
