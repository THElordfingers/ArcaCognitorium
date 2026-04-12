# EXOCOGNII WIRING — Handoff Document
## For Claude Code Continuation
### 2026-04-12

---

## CONTEXT

This session walked through the entire Exocognii ecosystem piece by piece,
established a shared mental map of every component and its role, then began
the wiring work to connect all standalone apps into a functioning organism.

The Exocognii is fully built. Every app runs. Every service runs. The gap
is connectivity — nothing talks to anything else yet.

---

## SYSTEM MAP

### Infrastructure (all built, all running)

| Service               | Port  | Purpose                                      |
|----------------------|-------|----------------------------------------------|
| Mundana State Bus     | —     | Unix socket pub/sub at /tmp/mundana.sock     |
| NUNTIUS              | 8730  | FastAPI Involucrum routing hub               |
| Exvacua Loricum      | 8731  | Lore memory (AI-assisted, ratification flow) |
| Perpetuum Aedificare | 8732  | Build memory (node graph, drift detection)   |
| CAELESTIS            | —     | Celestial engine (pyswisseph, Vedic sidereal)|
| Celestial Resolver   | —     | Per-entity influence vector computation      |

All six Machinae built at ~/ArcaCognitorium/machinae/:
machina_caelestis.py, machina_circadiana.py, machina_horologica.py,
machina_meteorologica.py, machina_solaris.py, machina_tidalis.py

### Apps (all built, all running)

| App                    | Purpose                                         |
|------------------------|------------------------------------------------|
| PRAESIDIUM            | Ambient desktop canvas, nervous system display   |
| GNOSIUM EXANIMA       | Primary conversational surface, system brain     |
| Arx Aedificarix       | Dedicated code builder (Builder entity)          |
| Dolium v2             | Four-chamber ideation pipeline                   |
| ENTITEX               | Entity package generator                         |
| A4 Bureau I (AS)      | Colour theme governance, writes theme.json       |
| A4 Bureau II (AA)     | UI component designer                            |
| A4 Bureau III (DD)    | Template sovereignty engine, document production |
| Vigilarum v2          | Celestial display (standalone, not connected)    |
| Lexiferium            | Vocabulary/naming oracle (Textual TUI)           |

### Key Architectural Decisions Made This Session

- PRAESIDIUM = nervous system display. Launch apps, monitor services/logs,
  view documents, manage git. Not where work happens — where awareness lives.
- GNOSIUM = the brain. General chat, system queries, pre-Dolium sandbox,
  entity testing. Queries Perpetuum and Exvacua behind the scenes.
- Arx = code only. Dedicated forge.
- Perpetuum = pure data service. No chat, no ClaudeBox. Conversational
  access through GNOSIUM.
- Exvacua = has ClaudeBox for intelligent lore parsing. Conversational
  access through PRAESIDIUM's chat widget.
- All template requests route through NUNTIUS to Bureau III.
- Dolium output format = "Documentum Aedificii" — build docs that feed
  directly into Arx's pick list.
- theme.json propagation = QFileSystemWatcher, not Mundana. File is the
  contract; works even when infrastructure is offline.
- Any app needing a document template that doesn't exist fires a template
  request through NUNTIUS. Bureau III receives it. PRAESIDIUM surfaces
  the notification.
- PRAESIDIUM display requirements: app status LEDs (on/off per app),
  service status LEDs, per-app token tracking, live activity/log feeds.

---

## WIRING PHASES

### Phase 1: NUNTIUS Emissions — DONE (partial)
Every app emits Involucrum payloads through NuntiusClient on meaningful events.

#### Canonical emit pattern (from GNOSIUM):
```python
# nuntius_emit.py — one per app, canonical pattern
from Exocognii.Nuntius.nuntius_client import (
    NuntiusClient, NuntiusDaemonNotRunningError,
)
payload = {
    "source_app": APP_ID,
    "source_version": APP_VERSION,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "hint": hint,
    "body": body,
}
try:
    NuntiusClient().emit(payload)
except NuntiusDaemonNotRunningError:
    # log and continue — never block app function
```

#### Status:

COMPLETED — written directly to disk via MCP:
- DD (Bureau III): nuntius_emit.py created. 4 call sites patched
  (scriptorium.py, mandate_bench.py, propagatio_worker.py, api.py).
  Old nuntius_client.py retired (still on disk, nothing imports it).
  Emits: "document_composed", "mandate_swap", "propagatio_migration"
- Bureau I (AS): nuntius_emit.py created. app.py patched.
  Emits: "theme_ratified" (designator, seal, tokens)
- Bureau II (AA): nuntius_emit.py created. armarium_feature.py patched.
  Emits: "component_sealed" (name, category, theme_designator)

COMPLETED — user placed from bundle:
- ENTITEX: nuntius_emit.py placed. Emit on vault autosave (~line 1886
  of Entitex.py). Emits: "entity_vaulted"
- Dolium: nuntius_emit.py placed. Emits on chamber graduation and
  Codex Paratum completion.
- Arx Aedificarix: nuntius_emit.py placed. Emits on session open/close.
- Lexiferium: nuntius_emit.py placed. Emits on term ratification.

NEEDS VERIFICATION:
- The four user-placed apps (ENTITEX, Dolium, Arx, Lexiferium) need
  verification that the emit calls were wired into the correct methods.
  The bundle included instructions but exact method names were inferred,
  not confirmed from source. Run each app and confirm NUNTIUS receives
  the emissions.

ALREADY WIRED (pre-existing):
- GNOSIUM EXANIMA: connectivity/nuntius_emit.py already uses canonical
  pattern. Emits: "conversation", "session_lifecycle"

### Phase 2: Machinae → Mundana Publishing — READY TO INSTALL
Six Machinae write JSON to ~/.arca/machina_*.json on each update cycle.
A bridge module watches those files and publishes changes to Mundana.

FILE: mundana_machinae_bridge.py (included in this handoff)
DESTINATION: ~/ArcaCognitorium/Exocognii/MundanaStateBus/mundana_machinae_bridge.py

Uses relative imports from the MundanaStateBus package:
  from .mundana_client import MundanaClient, BusDaemonNotRunningError
  from .mundana_channels import CHANNELS

Channel mapping:
  machina_caelestis.json     → mundana.caelestis
  machina_circadiana.json    → mundana.circadiana
  machina_horologica.json    → mundana.horologica
  machina_meteorologica.json → mundana.meteorologica
  machina_solaris.json       → mundana.solaris
  machina_tidalis.json       → mundana.tidalis

Integration options:
  a) Standalone: python3 -m MundanaStateBus.mundana_machinae_bridge
  b) Threaded: import run_bridge and run in a daemon thread from the bus
     launcher, so starting Mundana automatically starts the bridge
  c) Launch script: add to launch_mundana.sh as a background process

Option (b) is cleanest — the bus and its bridge start and stop together.
Wire run_bridge into the bus's lifespan or launcher.

### Phase 3: PRAESIDIUM Subscriptions — NOT STARTED
PRAESIDIUM has been upgraded since this session began. Read its current
state fresh before wiring anything.

Required new capabilities:
- App status LED panel (on/off per Exocognii app)
- Service status LED panel (NUNTIUS, Exvacua, Perpetuum, Mundana, CAELESTIS)
- Per-app token tracking (all apps that use ClaudeBox)
- Live activity feed (NUNTIUS /log, Perpetuum captures, Exvacua ratifications)
- Mundana channel subscriptions for ambient data display

Data sources:
- Mundana channels → subscribe via MundanaClient + Qt bridge
- NUNTIUS /status and /log → HTTP poll
- Perpetuum /nodi, /aggrexuum/status → HTTP poll
- Exvacua (pending ratification inquiries) → HTTP poll
- App/service liveness → process check or Mundana mundana.app_status channel

### Phase 4: Pipelines — NOT STARTED
- Dolium → Documentum Aedificii → Arx pick list with build state tracking
- ENTITEX → celestial.yaml generation during entity forge
- Template request flow: any app → NUNTIUS → Bureau III (notification in PRAESIDIUM)
- theme.json file watch: Bureau I writes → every PyQt6 app watches and re-skins

### Phase 5: GNOSIUM as Brain — NOT STARTED
- Wire queries to Perpetuum /nodi (build state)
- Wire queries to Exvacua (lore corpus)
- Subscribe to Mundana for ambient awareness
- Emit to NUNTIUS (already done)
- Connect intelligence layer to PRAESIDIUM display

---

## FILE LOCATIONS

### Files written this session (live on disk):

~/ArcaCognitorium/Exocognii/A4/DepartamentumDocumentalis/
  nuntius_emit.py          — NEW (canonical emit module)
  scriptorium.py           — PATCHED v1.1 → v1.2
  mandate_bench.py         — PATCHED v1.1 → v1.2
  propagatio_worker.py     — PATCHED v1.1 → v1.2
  api.py                   — PATCHED v1.1 → v1.2
  nuntius_client.py        — RETIRED (still on disk, nothing imports it)

~/ArcaCognitorium/Exocognii/A4/AuctoritasSpectralis/
  nuntius_emit.py          — NEW
  app.py                   — PATCHED (import + emit after ratification)

~/ArcaCognitorium/Exocognii/A4/AgentiaArchitecturalis/
  nuntius_emit.py          — NEW
  features/armarium/armarium_feature.py — PATCHED (import + emit after seal)

### Files placed by user from bundle:

~/ArcaCognitorium/Exocognii/Entitex/nuntius_emit.py
~/ArcaCognitorium/Exocognii/Dolium/nuntius_emit.py
~/ArcaCognitorium/Exocognii/ArxAedificarix/nuntius_emit.py
~/ArcaCognitorium/Exocognii/Lexiferium/nuntius_emit.py  (or wherever it lives)

### Files in this handoff package:

mundana_machinae_bridge.py → install to MundanaStateBus/

---

## VERIFICATION CHECKLIST

Before starting Phase 3, verify:

1. Start NUNTIUS: launch_nuntius.sh
2. Start any app (e.g. Bureau I)
3. Perform a ratifiable action (e.g. ratify a theme)
4. Check NUNTIUS /log — confirm emission received
5. Check Perpetuum /nodi — confirm Actio Aggrexuum maps it
6. Repeat for each app with wired emissions

For Phase 2:
1. Start Mundana: launch_mundana.sh
2. Start at least one Machina in daemon mode
3. Start the bridge (however it's integrated)
4. Confirm Mundana has data on the corresponding channel

---

## DEAD / ABSORBED / BACK BURNER

Dead: Fenestrium (replaced by Bureau II)
Being absorbed: PAIRZ → Bureau I
Back burner: Incitamentum, Glyptorum, Sigilarium, Mythotex, Oculus
Novelty (future visual overhaul): Vigilarum v2
