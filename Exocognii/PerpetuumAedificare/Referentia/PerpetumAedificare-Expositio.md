# PERPETUUM AEDIFICARE
### Expositio · v1.0 · Arca Cognitorium — Exocognii Suite

---

## I. IDENTITY

**Name & Version:** Perpetuum Aedificare · v1.0

**Tagline:** The build continues. Perpetuum Aedificare remembers where.

**Classification:** Local FastAPI memory service — ambient build continuity
tracker with Claude-powered aggregation, relationship graph, and drift
detection.

**Status:** Active development. Core service built and functional. Praesidium
read layer not yet wired.

---

## II. PURPOSE

**Problem Statement:** Active development on the Arca Cognitorium spans
multiple applications, architectural threads, open questions, and deferred
decisions. Each session begins with the same friction: what was the state of
this component, what was decided about that question, where did this thread
leave off. The Wizard should not have to maintain a separate project log
to answer questions the build process itself has already answered.

**Motivation:** The same philosophy that drives Exvacua Loricum for lore
applies to build work. Apps emit what they know. Something listens, infers,
and remembers. The Wizard should be able to ask "where am I with this" and
receive an accurate answer without having documented the journey.

**Intended Outcome:** After Perpetuum Aedificare is running, every meaningful
build event leaves a trace. The Wizard can surface the current state of any
active work unit, see what questions are still open, understand how components
relate to each other, and receive a quiet signal when something has drifted
stale relative to its connected work. The build is documented by the act of
building, not by a parallel documentation effort.

**Anti-Purpose:** Perpetuum Aedificare is not a task manager. It does not
assign priorities, set deadlines, or track time. It tracks shape and momentum.
It answers "what is this" and "where was it" — not "what should I do next."

---

## III. AUDIENCE

**Primary Users:** LordFingers — sole Wizard. Interacts primarily through
Praesidium once the read layer is wired. Also interacts directly via the
Nota Brevis endpoint for quick notes, and via Praesidium's advisory interface
for drift signals.

**Secondary Users:** All Exocognii applications as write clients via Nuntius.
Praesidium as the primary read and advisory interface.

**Assumed Knowledge:** The Wizard understands the project structure, the
Nodicum type system, and the concept of Nodi Momentuum as units of ongoing
work. Apps writing to the service need only know the Involucrum format.

**Out-of-Scope Audiences:** Anyone expecting project management features —
sprints, priorities, assignments, or deadlines. This is a continuity
prosthetic, not a workflow tool.

---

## IV. DESIGN PHILOSOPHY

**Core Principles:**

Documentation is a byproduct of working, not a separate activity. The system
captures what happens during build sessions. The Wizard does not manually
maintain state.

The Nodicum system is open. New node types can be proposed and ratified.
The seeded types are starting points, not a closed vocabulary.

Relationships are as important as nodes. The graph of how work units connect
to each other is where meaning lives. A node with many connections is a
Notiones Devoratrix Totalis — a context anchor that everything else orbits.

Drift detection is quiet. A Driftuum Attentio fires once and does not
resurface until the Wizard acknowledges it. The system does not nag.

The Tower is read-only from here. Perpetuum Aedificare can reference Tower
constructs via the Arca Absoluticum layer, but never writes to Tower storage.
The Tower receives nothing it did not generate itself.

**Tradeoff Positions:** Inference quality over friction reduction. The system
asks Claude to map captures to nodes — this costs API calls, but it means the
Wizard does not have to tag every emission manually.

**Aesthetic Direction:** Functional and declarative. The Nodifex is a
human-readable current-state description, not a structured enum. It should
read like someone who knows the project giving you a status update.

**What This Philosophy Rejects:** Mandatory documentation. The Wizard never
has to write anything into Perpetuum Aedificare. All documentation is
inferred. The Nota Brevis endpoint exists for moments when the Wizard wants
to be explicit, not as a requirement.

---

## V. TECHNICAL CONCEPT

**Mental Model:** A graph of work units connected by named relationships,
fed by an ambient capture stream. The Acquiuum Chronex is the raw intake.
The Nodus Momentuum graph is the distilled understanding. The Actio Aggrexuum
aggregation pass is what converts one into the other.

**Core Abstractions:**

An Acquiuum Chronex capture is a raw event — an app emission, a quick note,
a file scour result. It carries source, content, and a timestamp. It is
pending until Actio Aggrexuum maps it to a node.

A Nodus Momentuum is a unit of active work — an application, a feature, a
concept, a question, a decision, an artefact, or a session. It carries a
current-state description (Nodifex), open questions, decisions made, and
references to Tower constructs. It is the thing Perpetuum Aedificare
remembers.

An Exnodica is a directed relationship between two Nodi. The edge has a named
relationship type — `spawned_from`, `blocks`, `informs`, `supersedes`. The
topology implied by the Exnodica graph reflects the actual structure of the
project.

The Driftuum Metrica is a score on each Nodus that accumulates when the node
is stale relative to its connected nodes. A node that hasn't been touched in
two weeks while three of its connected nodes are active every day has high
drift. When drift crosses the configured threshold, a single Driftuum Attentio
flag fires.

**Data Flow:** App emits Involucrum → Nuntius POSTs to `/acquiuum` → capture
lands as pending in Acquiuum Chronex → Actio Aggrexuum fires on schedule or
threshold → Claude maps each capture to an existing Nodus or creates a new one
→ Nodifex updated, captures marked aggregated → Driftuum pass scores all
active Nodi → drift flags issued where threshold crossed → Praesidium reads
nodes, graph, and drift flags for the Wizard.

**System Boundaries:** Perpetuum Aedificare owns build capture, node
management, relationship graph, and drift detection. It does not own lore
classification (that is Exvacua Loricum's domain). It does not own the Tower.
It reads Tower constructs as references but never modifies them.

**Key Technical Decisions:** Same stack as Exvacua Loricum — SQLite, FastAPI,
ClaudeBox. Faster cadence (5 minute interval, 10 capture threshold) because
build signals are more time-sensitive than lore signals. Drift threshold
configurable in Configuus — resolves the open flag from schema v0.4.

---

## VI. FUNCTIONAL SCOPE

**Core Capabilities:** Four capture pathways — app emission, Nota Brevis,
Oratio Extracticum conversation scour, file drop. Claude-powered aggregation
via Actio Aggrexuum. Nodus Momentuum CRUD. Exnodica relationship graph.
Arca Absoluticum Tower reference layer. Driftuum Sentifex drift detection.
Full REST API surface.

**Supporting Capabilities:** Wizard manual node assignment for captures.
Direct Nodifex and open questions editing. Wizard-set Nodicum overrides.
Aggrexuum log for every pass. Driftuum log for every flag issued.

**Explicit Exclusions:** No task management. No priorities or deadlines.
No UI (Praesidium read layer is separate). No Tower write access.
No multi-user support.

**Future Scope:** Praesidium read layer — advisory interface surfacing nodes,
drift flags, and graph queries. Nuntius wiring to all existing Exocognii apps.

---

## VII. CONSTRAINTS & CONTEXT

**Technical Constraints:** Python 3.11+. FastAPI. SQLite. Port 8732.
ClaudeBox via canonical repo path. CLAUDE_API_KEY environment variable.
Paths resolved via `~/.arca/config.json`.

**External Dependencies:** ClaudeBox — all Actio Aggrexuum classification
calls. uvicorn for serving.

**Regulatory or Compliance Context:** None. Entirely local.

---

## VIII. SUCCESS CRITERIA

**Functional Success:** The service starts cleanly, accepts captures from
any app, runs Actio Aggrexuum on schedule, produces Nodi Momentuum that
accurately reflect active build work, and issues Driftuum Attentio flags
when nodes fall stale relative to their connected work.

**User Success:** The Wizard can open Praesidium, look at the current node
list, and immediately understand what is active, what has drifted, and how
the pieces connect — without having manually written any of it.

**Failure Conditions:** If Actio Aggrexuum consistently creates duplicate
nodes for the same work unit rather than mapping to existing ones, the
classification prompt needs tuning. If drift flags fire too frequently or
too rarely, the threshold in Configuus needs adjustment.

---

## IX. GLOSSARY

**Acquiuum Chronex** — the capture surface. Raw events before aggregation.

**Actio Aggrexuum** — the aggregation pass. Maps captures to Nodi, updates
Nodifex, runs Driftuum scoring.

**Nodus Momentuum** — atomic unit of active work. The thing Perpetuum
Aedificare tracks.

**Nodicum** — the type of a Nodus. Seeded types: system, feature, concept,
question, decision, artefact, session. Extensible.

**Nodifex** — the current state of a Nodus. Human-readable, freeform text.
Not an enum. Updated by Actio Aggrexuum and by the Wizard directly.

**Exnodica** — a directed relationship between two Nodi. The edge table of
the work graph.

**Notiones Devoratrix Totalis** — informal name for a Nodus with many
Exnodica connections. A context anchor.

**Driftuum Metrica** — drift score on a Nodus. 0.0–1.0. Rises with staleness
relative to connected active nodes.

**Driftuum Attentio** — a single drift flag. Fires once when threshold crossed.
Does not resurface until Wizard triggers Driftuum Agnosco.

**Arca Absoluticum** — Tower reference layer on a Nodus. Read-only references
to Tower constructs (FOLIUM, FILUM, grimoire snapshots).

**Involucrum** — the shared write format used by all Exocognii apps to emit
to Cognosis services.

**Nota Brevis** — a quick Wizard note. Low-friction capture path for explicit
thoughts that don't come from an app emission.

**Oratio Extracticum** — conversation scour. Parses exported conversation
files for build-relevant content.

---

## X. REVISION NOTES

**v1.0 — 2026-03-28**
Initial build. Core service complete: all four capture pathways, Actio
Aggrexuum with Driftuum Sentifex, Nodus CRUD, Exnodica graph, Arca
Absoluticum references. Drift threshold default added (0.65) resolving
schema v0.4 review flag 04. Praesidium read layer deferred to next session.
Nuntius wiring to existing apps deferred to Tier 4 completion.
