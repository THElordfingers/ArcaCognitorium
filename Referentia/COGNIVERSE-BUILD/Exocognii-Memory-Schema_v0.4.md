┌─────────────────────────────────────────────────────────────┐
│  ::REVIEW FLAGS                                             │
├─────────────────────────────────────────────────────────────┤
│  01  Lorixii Speculativum gained an `ignored` status        │
│      (Actio Interpretus determined not lore-relevant)       │
│      not present in v0.2 — confirm this is wanted           │
│                                                             │
│  02  Two names pending (Section 4.4) — deferred by          │
│      Wizard, not blocking build but noted                   │
│                                                             │
│  03  Judicium session `phase_data` is a freeform JSON       │
│      blob — phase-specific payload shape is unspecified.    │
│      May need definition before Judicium UI is built        │
│                                                             │
│  04  Driftuum Metrica threshold value is undeclared —       │
│      cadence intervals are in Configuus but drift           │
│      threshold has no default or config key yet             │
└─────────────────────────────────────────────────────────────┘








# SYSTEMICA MEMORIUM EXOCOGNII — SCHEMA REFERENCE
### Exvacua Loricum · Perpetuum Aedificare · Praesidium
*Arca Cognitorium — Exocognii Suite*
*v0.4 — Theory Phase Document — Complete*

---

## I. EXVACUA LORICUM

**Role:** Lore canon memory system. Passive accumulator, active ratification, living synthesis.
The system watches, collects, and infers — nothing becomes canon until the Wizard commits it.
Apps never decide what is lore. That is Exvacua Loricum's job.

**Service:** Local FastAPI — port declared in Configuus.
**Clients:** All apps write to it on every emission. Praesidium reads. Wizard via Judicium UI.

---

### 1.1 Ingestion Pathways

| Source | Mechanism | Notes |
|---|---|---|
| App writes | FastAPI POST, Involucrum envelope — all apps, always | Live, ambient |
| Manual file drop | Wizard deposits file at designated path | Parsed on drop |
| Lorixii Extractuum | Wizard-invoked crawl of repo files and conversation exports | Archaeology — primary current use |

All three pathways feed the Lorixii Speculativum. Source type is always preserved.
Apps do not decide relevance — Actio Interpretus determines what is claimed.

---

### 1.2 Distillation Cadence

Actio Interpretus runs on a scheduled heartbeat with threshold override.

| Parameter | Default | Configuus Key |
|---|---|---|
| Schedule interval | 10 minutes | `exvacua_loricum.interpretus_interval` |
| Threshold — pending Lorixii | 20 | `exvacua_loricum.interpretus_threshold` |

When pending Lorixii count crosses threshold, Actio Interpretus fires immediately
regardless of schedule. After firing, the schedule resets from that point.
Both parameters are tunable in the Configuus without touching code.

---

### 1.3 Lorixii Speculativum — Unratified Accumulation Layer

**Storage:** SQLite

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `source_type` | enum: `app_log` · `file_drop` · `actio_extracticus` | Ingestion pathway |
| `source_ref` | string | App name, file path, or scour target — depends on source_type |
| `ingested_at` | timestamp | |
| `raw_content` | text | Original content, unmodified |
| `inferred_domain` | string | Actio Interpretus best guess at top-level domain |
| `inferred_tags` | JSON array | Suggested tags, pending Wizard governance |
| `confidence` | enum: `low` · `medium` · `high` | System certainty that this is lore-relevant |
| `status` | enum: `pending` · `in_judicium` · `consumed` · `rejected` · `ignored` | Lifecycle state |
| `judicium_id` | UUID · nullable | Null until claimed by a Judicium Exlorica session |
| `related_lorixii` | JSON array of UUIDs | Lorixii the system clusters with this one |

`consumed` — Lorix fed a ratified Card and is archived.
`rejected` — Wizard dismissed at Judicium. Never deleted. Only classified.
`ignored` — Actio Interpretus determined not lore-relevant. Retained for audit.

---

### 1.4 Loridex Card — Structured Canon Index Entry

**Storage:** SQLite (raw) + `.md` + `.wiz` (rendered via Actio Duxuum)

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Canonical ID — shared with bound Exloricum |
| `title` | string | Lore entry name |
| `domain` | string | Top-level domain from Arx Loricuum |
| `tags` | JSON array | Emergent tag set, Wizard-governed |
| `status` | enum: `ratified` · `flagged_for_revision` | Canon status |
| `ratified_at` | timestamp | |
| `source_lorixii` | JSON array of UUIDs | Lorixii Speculativum entries that fed this Card |
| `linked_cards` | JSON array of UUIDs | Related canonical entries |
| `exloricum_id` | UUID | Bound Exloricum reference |
| `revision_history` | JSON array | `{ timestamp, note }` per Actio Revisicus event |

**Rendering:** Two rendered representations produced at ratification and on demand via Actio Duxuum.
Styled per the active Aestheticum. Aesthetic register: dense, tactile, authoritative —
the feel of something classified and filed by an ancient bureaucracy.

---

### 1.5 Exloricum — Long-Form Prose Canon Document

**Storage:** SQLite pointer record + `.md` file on disk + `.wiz` rendered version

**SQLite record:**

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Canonical ID — shared with bound Loridex Card |
| `card_id` | UUID | Explicit back-reference to Loridex Card |
| `title` | string | Mirrors Card title — may diverge if prose warrants different heading |
| `created_at` | timestamp | Ratification timestamp |
| `last_revised_at` | timestamp | Updated on every Actio Revisicus |
| `revision_count` | integer | |
| `file_path` | string | Path to canonical `.md` file on disk |
| `wiz_path` | string | Path to rendered `.wiz` version |
| `aestheticum` | string | Active Aestheticum at last render |
| `word_count` | integer | Tracked for Loretic Crystalizer — large Exlorica receive different synthesis treatment |

**File structure:** YAML frontmatter mirroring SQLite fields, followed by open prose body.
SQLite record and frontmatter stay in sync — one source of truth, two access surfaces.

**Aesthetic register:** Expansive, atmospheric. Each one a world. Gallery of inhabited truths.

---

### 1.6 Loricum Ratifex — Master Lore Compendium

**Storage:** SQLite singleton record + `.md` file on disk + `.wiz` rendered version

**SQLite record:**

| Field | Type | Description |
|---|---|---|
| `id` | integer | Singleton — always 1 |
| `last_crystalized_at` | timestamp | Last Loretic Crystalizer pass |
| `last_wizard_edit_at` | timestamp | Last manual Wizard amendment |
| `version` | integer | Increments on every change regardless of author |
| `file_path` | string | Canonical `.md` on disk |
| `wiz_path` | string | Rendered `.wiz` version |
| `aestheticum` | string | Active Aestheticum |

**File structure:** H1 section per top-level domain from Arx Loricuum. Subsections per tag
cluster beneath. Each section carries provenance comment:

```
<!-- crystalizer: 2026-03-21 -->
<!-- wizard: 2026-03-22 -->
```

The Loretic Crystalizer reads provenance before operating. Wizard-authored sections
are not overwritten — flagged for review if new ratified lore creates tension.

Both the Loretic Crystalizer and the Wizard are legitimate authors.

---

### 1.7 Arx Loricuum — Taxonomy Register

**Storage:** SQLite

| Field | Type | Description |
|---|---|---|
| `id` | UUID | |
| `name` | string | Domain or tag name |
| `type` | enum: `domain` · `tag` | Top-level domain vs emergent tag |
| `parent_domain` | UUID · nullable | For tags — which domain they sit beneath |
| `status` | enum: `seeded` · `ratified` · `proposed` · `rejected` | |
| `proposed_by` | enum: `system` · `wizard` | Origin |
| `created_at` | timestamp | |

Seeded domains declared in Exvacua Loricum config at system init.
Emergent tags accumulate from Actio Interpretus inference. Both are Wizard-governable.

---

### 1.8 Aestheticum — Theme System

Loridex Cards and Exlorica are rendered via the Aestheticum bundle system.

**Bundle structure:**
```
aesthetica/
└── {aestheticum_name}/
    ├── Loridex Aesthetidux       — Loridex Card rendering instructions
    ├── Exlorica Aesthetidux      — Exloricum rendering instructions
    └── Compendium Aesthetidux    — Loricum Ratifex section rendering instructions
```

Swap the Aestheticum, swap all output aesthetics. Per-artefact override supported —
Loridex Aesthetidux can be overridden without touching Exlorica Aesthetidux.
Style docs are drop-in. Artefact content is stable; presentation layer is configurable.

---

### 1.9 Judicium Exlorica — Ratification Ceremony

Triggered per topic cluster. Lorixii grouped by inferred domain and related_lorixii
links are packaged and presented to the Wizard for ratification.

Judicium session state is owned by Exvacua Loricum. The UI is a renderer —
it calls the API at each phase transition. The API tracks position and decisions.

**Judicium Session — SQLite table:**

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Session ID |
| `topic` | string | Human-readable topic label for this cluster |
| `domain_hint` | string | Inferred domain that triggered the cluster |
| `lorixii_ids` | JSON array of UUIDs | All Lorixii in scope for this session |
| `current_phase` | integer | 1–5 — current Phasis |
| `phase_data` | JSON | Phase-specific working state — selections, edits, drafted card |
| `status` | enum: `open` · `committed` · `abandoned` | |
| `opened_at` | timestamp | |
| `committed_at` | timestamp · nullable | |
| `card_id` | UUID · nullable | Populated at Sacramentum Finalitus |
| `exloricum_id` | UUID · nullable | Populated at Sacramentum Finalitus |

**Five phases:**

| Phase | Name | Description |
|---|---|---|
| Phasis I | Obscuranda Necessitum | Allow / deny individual Lorixii from the cluster |
| Phasis II | Colloquium Elucidativum | Conversational — Wizard elaborates, corrects, contextualises |
| Phasis III | Ostensio Loridexii | Loridex Card drafted and presented for review |
| Phasis IV | Exlorica Methodicum | Exloricum drafted, presented for final edits |
| Phasis V | Sacramentum Finalitus | Wizard ratifies — Card and Exloricum written to canon, Loretic Crystalizer triggered |

**Actio Revisicus:** When newly ratified lore touches existing canon entries,
a revision session is flagged. Existing Exloricum and Loridex Card are surfaced for amendment.

---

### 1.10 Loretic Crystalizer

Post-ratification analytic engine. Triggered after every Sacramentum Finalitus.

- Reads the ratified Loridex Card's domain and tags from Arx Loricuum
- Locates the corresponding section in the Loricum Ratifex
- Checks provenance comments before operating
- Surgically updates only the sections touched by the new entry
- Skips or flags Wizard-authored sections
- Increments Loricum Ratifex version counter
- Updates `last_crystalized_at`

---

### 1.11 Lorixii Extractuum — Corpus Scour System

Wizard-invoked archaeology crawl. Designated source paths (repo files, conversation exports)
are parsed for lore-relevant material and fed into the Lorixii Speculativum.

Each invoked crawl is an **Actio Extracticus**. The inference pass that processes
raw content into structured Lorixii is the **Actio Interpretus**.

---

### 1.12 API Surface

**Lorixii Speculativum — observation pile**
```
POST   /lorix                    — ingest a single Lorix (Involucrum envelope)
POST   /lorix/drop               — ingest a file drop
POST   /extracticus              — invoke an Actio Extracticus (scour session)
GET    /lorixii                  — list Lorixii, filterable by status/domain/confidence
GET    /lorix/{id}               — fetch a single Lorix
DELETE /lorix/{id}               — reject a Lorix (sets status: rejected)
```

**Canon — Loridex Cards and Exlorica**
```
GET    /cards                    — list Loridex Cards, filterable by domain/tags/status
GET    /card/{id}                — fetch a single Loridex Card
GET    /card/{id}/exloricum      — fetch the bound Exloricum
GET    /exlorica                 — list all Exlorica
GET    /exloricum/{id}           — fetch a single Exloricum
PUT    /exloricum/{id}           — Wizard edits an Exloricum directly
```

**Loricum Ratifex**
```
GET    /ratifex                  — fetch the full Loricum Ratifex
GET    /ratifex/section/{domain} — fetch a single domain section
PUT    /ratifex/section/{domain} — Wizard edits a section directly
```

**Arx Loricuum — taxonomy**
```
GET    /loricuum                 — fetch full taxonomy register
POST   /loricuum/domain          — propose a new top-level domain
POST   /loricuum/tag             — propose a new tag
PUT    /loricuum/{id}            — approve/reject/rename an entry
```

**Judicium Exlorica — ratification sessions**
```
POST   /judicium                 — open a new Judicium session for a topic cluster
GET    /judicium/{id}            — fetch current Judicium state and phase
POST   /judicium/{id}/advance    — advance to next phase, payload varies by phase
POST   /judicium/{id}/commit     — Sacramentum Finalitus — write to canon
DELETE /judicium/{id}            — abandon a Judicium session
GET    /judicia                  — list open/recent Judicium sessions
```

**Actio Revisicus**
```
POST   /revisicus/{card_id}      — open a revision session against an existing card
```

**Distillation**
```
POST   /interpretus              — trigger Actio Interpretus manually
GET    /interpretus/status       — last pass timestamp, pending Lorix count
```

---

---

## II. PERPETUUM AEDIFICARE

**Role:** Continuity prosthetic. Tracks the shape and momentum of all active work
across the Exocognii suite. Answers: *where did I leave off · what is the current state of ·
what can I do next · is this still relevant.*

The system documents for the Wizard. Diligent documentation is what is being escaped,
not the price of admission. Apps never decide what is build-relevant.
That is Perpetuum Aedificare's job.

**Service:** Local FastAPI — port declared in Configuus.
**Clients:** All apps write to it on every emission. Praesidium reads.

---

### 2.1 Distillation Cadence

Actio Aggrexuum runs on a scheduled heartbeat with threshold override.

| Parameter | Default | Configuus Key |
|---|---|---|
| Schedule interval | 5 minutes | `perpetuum_aedificare.aggrexuum_interval` |
| Threshold — pending captures | 10 | `perpetuum_aedificare.aggrexuum_threshold` |

When pending Acquiuum Chronex count crosses threshold, Actio Aggrexuum fires immediately
regardless of schedule. After firing, the schedule resets from that point.
Both parameters are tunable in the Configuus without touching code.

Perpetuum Aedificare runs on a faster cadence than Exvacua Loricum — build captures
are more time-sensitive than lore inference.

---

### 2.2 Nodus Momentuum — Atomic Unit

**Storage:** SQLite (raw) + `.md` (human-readable snapshot on demand)

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `title` | string | Human-readable name of the thing-in-progress |
| `nodicum` | string | Inferred or Wizard-assigned type — see Nodicum System below |
| `nodicum_confidence` | enum: `inferred` · `wizard_set` | Provenance of type assignment |
| `nodifex` | text | Current state — human-readable, freeform, not an enum |
| `created_at` | timestamp | |
| `last_touched_at` | timestamp | Updated on any Acquiuum Chronex or Wizard interaction |
| `open_questions` | JSON array of strings | Unresolved threads |
| `decisions` | JSON array of `{ timestamp, text }` | Decisions made against this node |
| `arca_absoluta` | JSON array of `{ type, id }` | Read-only Arca Absoluticum references |
| `driftuum_metrica` | float | Current Driftuum Metrica score |
| `driftuum_attentio` | boolean | Whether Praesidium has surfaced this node's drift |
| `status` | enum: `active` · `dormant` · `resolved` · `abandoned` | Wizard-assigned lifecycle |

---

### 2.3 Nodicum — Node Type System

Seeded top-level types declared at system init. Perpetuum Aedificare infers Nodicum
from Acquiuum Chronex content. Wizard can override. No fixed enum — new types
can be proposed and ratified.

**Seeded Nodica:**

| Nodicum | Description |
|---|---|
| `system` | A full application or major architectural system |
| `feature` | A discrete capability within a system |
| `concept` | An idea, principle, or design pattern |
| `question` | An open question requiring resolution |
| `decision` | A resolved choice — closed, but preserved |
| `artefact` | A produced output — doc, file, schema, component |
| `session` | A working context — intent-bounded, not time-bounded |

---

### 2.4 Exnodica — Relationship Graph

**Storage:** SQLite edge table

| Field | Type | Description |
|---|---|---|
| `id` | UUID | |
| `from_node` | UUID | Source Nodus Momentuum |
| `to_node` | UUID | Target Nodus Momentuum |
| `relationship` | string | Inferred or Wizard-assigned — e.g. `spawned_from` · `blocks` · `informs` · `supersedes` |
| `relationship_confidence` | enum: `inferred` · `wizard_set` | |
| `created_at` | timestamp | |

Exnodica are the primary structure. There is no enforced hierarchy —
a Nodus Momentuum with many Exnodica is a Notiones Devoratrix Totalis.
The graph implies the topology.

---

### 2.5 Acquiuum Chronex — Capture Surface

All captures land as raw Acquiuum Chronex events, then mapped to Nodus Momentuum
by the Actio Aggrexuum.

**Storage:** SQLite capture log

| Field | Type | Description |
|---|---|---|
| `id` | UUID | |
| `source_type` | enum: `indicatum_machina` · `nota_brevis` · `oratio_extracticum` · `file_drop` | |
| `source_ref` | string | App name, note text, file path, or conversation ID |
| `raw_content` | text | |
| `captured_at` | timestamp | |
| `inferred_node_id` | UUID · nullable | Nodus Momentuum Actio Aggrexuum associates this with |
| `node_confidence` | enum: `inferred` · `wizard_set` | |
| `status` | enum: `pending` · `aggregated` · `dismissed` | |

**Capture types:**

| Name | Type | Mechanism | Friction |
|---|---|---|---|
| Indicatum Machina | `indicatum_machina` | Apps emit structured events via FastAPI | Zero — ambient |
| Nota Brevis | `nota_brevis` | Wizard drops a short text note | Near-zero |
| Oratio Extracticum | `oratio_extracticum` | Perpetuum Aedificare parses conversation exports | Wizard-invoked |
| File drop | `file_drop` | Wizard deposits file at designated path | Near-zero |

**Actio Aggrexuum:** The aggregation pass. Reads pending Acquiuum Chronex, infers or
confirms the target Nodus Momentuum, updates node state, and marks captures as aggregated.

---

### 2.6 Arca Absoluticum — Tower Reference Layer

Perpetuum Aedificare can read Tower constructs. The Tower is unaware of Perpetuum Aedificare.
Information crosses the boundary only when the Wizard deliberately carries it.

**Arca Absoluta fields on Nodus Momentuum:**

```json
"arca_absoluta": [
  { "type": "FOLIUM", "id": "uuid" },
  { "type": "FILUM",  "id": "uuid" },
  { "type": "grimoire_snapshot", "id": "uuid" }
]
```

These are read-only references. Perpetuum Aedificare never writes to Tower storage.
The Tower receives nothing it did not generate itself.

---

### 2.7 API Surface

**Acquiuum Chronex — capture surface**
```
POST   /acquiuum                 — ingest a single Acquiuum Chronex (Involucrum envelope)
POST   /acquiuum/nota            — ingest a Nota Brevis (quick note, minimal envelope)
POST   /acquiuum/oratio          — invoke an Oratio Extracticum (conversation scour)
GET    /acquiuum                 — list Acquiuum Chronex, filterable by status/source_type
GET    /acquiuum/{id}            — fetch a single Acquiuum Chronex
PUT    /acquiuum/{id}/node       — Wizard manually assigns a capture to a Nodus Momentuum
DELETE /acquiuum/{id}            — dismiss a capture
```

**Actio Aggrexuum**
```
POST   /aggrexuum                — trigger an aggregation pass manually
GET    /aggrexuum/status         — last pass timestamp, pending capture count
```

**Nodus Momentuum — core**
```
POST   /nodus                    — create a Nodus Momentuum manually
GET    /nodi                     — list Nodi, filterable by nodicum/status/last_touched
GET    /nodus/{id}               — fetch a single Nodus Momentuum
PUT    /nodus/{id}               — update nodifex, nodicum, status, open_questions
DELETE /nodus/{id}               — mark abandoned
GET    /nodus/{id}/acquiuum      — fetch all captures associated with this node
```

**Exnodica — relationship graph**
```
POST   /exnodica                 — create a relationship between two Nodi
GET    /nodus/{id}/exnodica      — fetch all Exnodica for a node
PUT    /exnodica/{id}            — update relationship type or confidence
DELETE /exnodica/{id}            — remove a relationship
```

**Arca Absoluticum — Tower references**
```
POST   /nodus/{id}/arca          — attach an Arca Absoluticum reference to a node
DELETE /nodus/{id}/arca/{ref_id} — detach a reference
```

---

---

## III. PRAESIDIUM

**Role:** Wizard-facing query and advisory interface. Sits above Exvacua Loricum
and Perpetuum Aedificare. Surfaces relevance when the gap becomes meaningful —
not on a heartbeat. A quiet advisor, not a notification system.
Permanently read-only — never in the write path.

**Service:** Local FastAPI — port declared in Configuus.
**Clients:** Wizard only — via UI. Apps never write to Praesidium.

---

### 3.1 Driftuum Sentifex — Relevance Drift Detection

A Nodus Momentuum accumulates Driftuum Metrica when:
- `last_touched_at` has grown stale
- Connected Nodi Momentuum (via Exnodica) have been active recently
- The delta between the node's Nodifex and its connected nodes' states exceeds threshold

When Driftuum Metrica crosses threshold, Praesidium issues a Driftuum Attentio.
Once. Quietly. The flag does not resurface until the Wizard triggers Driftuum Agnosco
by interacting with the node.

**Storage:** SQLite drift log

| Field | Type | Description |
|---|---|---|
| `id` | UUID | |
| `node_id` | UUID | |
| `driftuum_metrica` | float | Score at time of Driftuum Attentio |
| `flagged_at` | timestamp | |
| `resolved_at` | timestamp · nullable | Driftuum Agnosco timestamp |
| `trigger_nodes` | JSON array of UUIDs | Nodi whose activity drove the drift |

---

### 3.2 API Surface

**Wizard-facing queries — Exvacua Loricum surface**
```
GET    /lore/search              — search canon by keyword, domain, or tag
GET    /lore/card/{id}           — fetch a Loridex Card via Praesidium
GET    /lore/exloricum/{id}      — fetch an Exloricum via Praesidium
GET    /lore/ratifex             — fetch the Loricum Ratifex
GET    /lore/ratifex/{domain}    — fetch a domain section of the Loricum Ratifex
GET    /lore/pending             — how many Lorixii are waiting in Lorixii Speculativum
GET    /lore/judicia             — list open Judicium sessions
```

**Wizard-facing queries — Perpetuum Aedificare surface**
```
GET    /build/nodi               — list all Nodus Momentuum, filterable
GET    /build/nodus/{id}         — fetch a single Nodus Momentuum with Exnodica
GET    /build/search             — search nodes by title, nodicum, nodifex content
GET    /build/recent             — nodes touched most recently
GET    /build/stalled            — nodes dormant longest relative to their Exnodica activity
GET    /build/pending            — Acquiuum Chronex awaiting Actio Aggrexuum
```

**Driftuum Sentifex — advisory**
```
GET    /drift                    — all active Driftuum Attentio flags
GET    /drift/{node_id}          — drift detail for a specific node
POST   /drift/{node_id}/agnosco  — Wizard acknowledges — triggers Driftuum Agnosco
```

**Cross-system**
```
GET    /status                   — health of all three services, pending counts, last activity
GET    /search                   — unified search across Exvacua Loricum and Perpetuum Aedificare
```

---

---

## IV. SHARED INFRASTRUCTURE

---

### 4.1 Log Routing Architecture

Apps never decide what is lore-relevant or build-relevant. Both systems make that
determination independently. Every app emission goes to both services simultaneously.

**Write path:**
- App constructs one Involucrum payload
- Shared client library fires two POST calls — one to Exvacua Loricum, one to Perpetuum Aedificare
- Both calls are fire-and-forget — no response waiting
- Each service receives, queues, and processes independently
- Praesidium is permanently outside the write path

The shared client library lives in the Exocognii suite — imported once per app,
never duplicated. Name pending the next naming sweep.

**Service independence:** Each service is sovereign. If one is down, the other continues
receiving writes. No shared ingest layer, no routing dependency between services.

---

### 4.2 Involucrum — App Write Format

The Involucrum is the single write contract for all Exocognii apps.
No `target` field — routing is not the app's responsibility.
`hint` is optional — apps that know something about the content may suggest context,
but are never required to.

```json
{
  "source_app": "string",
  "source_version": "string",
  "timestamp": "ISO 8601",
  "hint": "optional — rough domain, node title, or context hint",
  "body": "freeform text — the observation or event"
}
```

---

### 4.3 Configuus — `~/.arca/config.json`

All Exocognii apps resolve shared paths from the Configuus. ClaudeBox is never copied —
apps import from the ArcaCognitorium repo path declared here.

**Minimum expected keys:**

```json
{
  "arca_repo_path": "/home/lordfingers/ArcaCognitorium",

  "exvacua_loricum_api": "http://localhost:{port}",
  "perpetuum_aedificare_api": "http://localhost:{port}",
  "praesidium_api": "http://localhost:{port}",

  "exvacua_loricum_db": "/path/to/exvacua_loricum.db",
  "perpetuum_aedificare_db": "/path/to/perpetuum_aedificare.db",
  "praesidium_db": "/path/to/praesidium.db",

  "exvacua_loricum_store": "/path/to/exvacua_loricum/",
  "perpetuum_aedificare_store": "/path/to/perpetuum_aedificare/",

  "exvacua_loricum": {
    "interpretus_interval": 600,
    "interpretus_threshold": 20
  },
  "perpetuum_aedificare": {
    "aggrexuum_interval": 300,
    "aggrexuum_threshold": 10
  }
}
```

Intervals are in seconds. Both distillation parameters are tunable here
without touching service code.

---

### 4.4 Pending — Next Naming Sweep

The following functional labels require names before build begins:

```
┌─────────────────────────────────────────────────────────────┐
│  PENDING NAMES                                              │
├─────────────────────────────────────────────────────────────┤
│  ├── Shared client library — the utility that fires both    │
│  │   POST calls per app emission                            │
│  └── Exocognii suite itself — the collective name for all   │
│      three services as a system                             │
└─────────────────────────────────────────────────────────────┘
```

---

*— End of Theory Phase Document —*
*Schema complete. API surfaces complete. Naming pass complete.*
*Distillation cadence complete. Log routing architecture complete.*
*Two names pending before build begins — see Section 4.4.*
