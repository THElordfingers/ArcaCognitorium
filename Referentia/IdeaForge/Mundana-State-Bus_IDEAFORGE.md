# MUNDANA STATE BUS
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

**MUNDANA STATE BUS — NOT BUILT. NO PRIOR SPECIFICATION.**

Evidence of absence:

  · Dolium v2 stamp (2026-04-01): "Praesidium pipeline state feed —
    Mundana State Bus not built." Listed under Deferred.
  · Verificatio Chronicle item 09 — Celestial Chain: pending. The
    confirmed build sequence is CAELESTIS → Mundana State Bus →
    Celestial Resolver. Item 09 cannot proceed until this is built.
  · Exocognii Memory Schema v0.4: Involucrum write path, Exvacua
    Loricum, and Perpetuum Aedificare are all fully specified.
    Mundana State Bus appears nowhere in that document.
  · Memory register: referenced by name in build sequence notes only.
    No architecture, no code, no schema.

**The Mundana State Bus has never been designed. It must be built from
first principles.** This document is its founding specification.

---

---

# II. PHASE 1 — IDEA BRIEF

---

╭──────────────────────────────┬────────────────────────────────────────╮
│  Field                       │  Content                               │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  App Name                    │  Mundana State Bus                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  One-Line Purpose            │  A lightweight, process-local          │
│                              │  publish/subscribe state broadcast     │
│                              │  layer that allows all Exocognii       │
│                              │  applications and the CAELESTIS        │
│                              │  celestial engine to exchange live     │
│                              │  state without direct coupling.        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Platform                    │  Debian Trixie / KDE Plasma 6 / X11    │
│                              │  Python 3.11 — no GUI framework        │
│                              │  (infrastructure library only)         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Core Loop                   │  1. Publisher calls bus.publish(       │
│                              │     channel, payload)                  │
│                              │  2. Bus routes payload to all          │
│                              │     registered subscribers on that     │
│                              │     channel                            │
│                              │  3. Subscriber callbacks fire in       │
│                              │     their own thread context           │
│                              │  4. Bus maintains last-known state     │
│                              │     per channel for late subscribers   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Key Features (v1)           │  · Typed channel registry              │
│                              │  · Subscribe / unsubscribe             │
│                              │  · Publish with payload dict           │
│                              │  · Late-join replay (last state)       │
│                              │  · Cross-process broadcast via         │
│                              │    named pipe or Unix socket           │
│                              │  · Channel manifest — known channels   │
│                              │    declared at import, unknown         │
│                              │    channels rejected or warned         │
│                              │  · Celestial Resolver interface:       │
│                              │    CAELESTIS publishes to bus,         │
│                              │    Resolver subscribes and             │
│                              │    computes behavioural outputs        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Explicit Out of Scope (v1)  │  · Persistence to disk (state lives    │
│                              │    in memory only — ephemeral)         │
│                              │  · Authentication / channel security   │
│                              │  · Remote (non-local) transport        │
│                              │  · Queueing / guaranteed delivery      │
│                              │  · Event sourcing / full history log   │
│                              │  · Admin UI                            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Technical Risks             │  · Cross-process delivery: PyQt6 apps  │
│                              │    run in isolated venvs. The bus must │
│                              │    bridge processes without shared     │
│                              │    memory. Unix socket chosen over     │
│                              │    pipe for bidirectional support.     │
│                              │  · Thread safety: callbacks arrive     │
│                              │    from bus reader threads. PyQt6      │
│                              │    subscribers must marshal signals    │
│                              │    back to main thread.                │
│                              │  · Payload schema drift: no enforced   │
│                              │    schema in v1 — channel manifest     │
│                              │    describes expected shape but does   │
│                              │    not validate it.                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Visual Identity             │  No UI. CLI status command only.       │
│                              │  Library + daemon process.             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  v2 Wishlist                 │  · Payload schema validation per       │
│                              │    channel (TypedDict or Pydantic)     │
│                              │  · Persistent ring buffer for          │
│                              │    diagnostic replay                   │
│                              │  · PRAESIDIUM bus health widget        │
│                              │  · Channel metrics (publish rate,      │
│                              │    subscriber count, last-seen)        │
│                              │  · WebSocket bridge for Tower TUI      │
│                              │    consumers                           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Open Questions              │  · Should the bus daemon live as an    │
│                              │    Exocognii FastAPI service (own      │
│                              │    port) or as a raw socket server?    │
│                              │    Recommendation: raw Unix socket —   │
│                              │    avoids HTTP overhead for            │
│                              │    high-frequency celestial ticks.     │
│                              │  · Does PRAESIDIUM subscribe directly  │
│                              │    to bus, or only to Celestial        │
│                              │    Resolver output?                    │
│                              │  · What channels are canonical at      │
│                              │    launch? See Channel Manifest below. │
╰──────────────────────────────┴────────────────────────────────────────╯


## Canonical Channel Manifest (v1)

These are the channels the bus knows about at launch. Publishers and
subscribers declare the channel name from this manifest. Unknown channel
names are rejected with a BusChannelError.

╭────────────────────────────┬──────────────────┬────────────────────────╮
│  Channel                   │  Publisher       │  Subscribers           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.caelestis         │  CAELESTIS       │  Celestial Resolver,   │
│                            │                  │  PRAESIDIUM widget,    │
│                            │                  │  VIGILARUM             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.resolver          │  Celestial       │  Tower entity engine,  │
│                            │  Resolver        │  PRAESIDIUM widget     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.circadiana        │  CIRCADIANA      │  Celestial Resolver,   │
│                            │                  │  PRAESIDIUM widget     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.horologica        │  HOROLOGICA      │  Celestial Resolver,   │
│                            │                  │  Tower time display    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.meteorologica     │  METEOROLOGICA   │  Celestial Resolver    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.solaris           │  SOLARIS         │  Celestial Resolver    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.tidalis           │  TIDALIS         │  Celestial Resolver,   │
│                            │                  │  VIGILARUM             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.lapsus            │  LAPSUS          │  Celestial Resolver,   │
│                            │  (meta-engine)   │  Tower entity engine   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.token_ledger      │  All apps        │  PRAESIDIUM            │
│                            │  (via emit)      │  TokenTracker widget   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  mundana.app_status        │  All apps        │  PRAESIDIUM status     │
│                            │  (heartbeat)     │  panel                 │
╰────────────────────────────┴──────────────────┴────────────────────────╯

Channels follow the pattern `mundana.{engine_or_domain}`. All channel
names are lowercase, dot-separated. New channels require Wizard ratification
before being added to the manifest.


## Architecture Decision Record

**Transport: Unix domain socket, not HTTP.**
The Machinae Mundi Lapsus engines tick at high frequency — HOROLOGICA
at least once per second, CIRCADIANA on sub-minute intervals. HTTP
overhead is unacceptable for this cadence. A raw Unix socket at
`/tmp/mundana.sock` provides sub-millisecond local delivery.

**Single daemon process, shared socket.**
One `mundana_bus.py` daemon runs as the routing hub. All Exocognii
apps connect as clients — publisher or subscriber role declared at
connect time. The daemon is started by the PRAESIDIUM launcher or
manually; it does not auto-start from within app code.

**Late-join replay is last-state-only.**
No full history. When a new subscriber joins a channel, it receives
the most recent payload on that channel immediately. This allows
widgets that start after the bus to initialise with current state.

**PyQt6 thread safety contract.**
The bus delivers callbacks on a reader thread. Any PyQt6 subscriber
must emit a Qt signal from the callback — never touch widgets directly.
The shared client library enforces this by providing a
`MundanaQtBridge` class that wraps callback dispatch into a
`QMetaObject.invokeMethod` call.

---

---

# III. PHASE 2 — SEED PROMPT

---

The following is the developer-ready build prompt for the Mundana State Bus.
It incorporates all architectural decisions resolved in Phase 1.

---

```
You are a senior software architect writing for an experienced Linux developer.
Produce complete, developer-ready construction documentation for the
"Mundana State Bus" — a Python 3.11 infrastructure daemon and client
library with no GUI.

The Mundana State Bus is a lightweight publish/subscribe state broadcast
layer that connects all Exocognii desktop applications and the CAELESTIS
celestial engine complex without direct coupling between them. It runs as
a single daemon process listening on a Unix domain socket. All apps import
a shared client library to publish or subscribe to named channels. The bus
routes payloads to registered subscribers and maintains last-known state per
channel for late-joining subscribers.

Architecture decisions to enforce — do not soften or defer any:

  - Transport: Unix domain socket at /tmp/mundana.sock.
    No HTTP. No REST. Raw socket only.
  - Daemon: single mundana_bus.py process. Stateless beyond in-memory
    channel state and subscriber registry. No database.
  - Client library: MundanaClient class. Importable from
    ~/ArcaCognitorium/Exocognii/MundanaStateBus/mundana_client.py.
    Apps never import the daemon module.
  - Channel manifest: CHANNELS dict in mundana_channels.py. Channels
    follow pattern mundana.{domain}. Unknown channels raise
    BusChannelError — no silent pass-through.
  - Late-join replay: bus stores last payload per channel in memory.
    New subscriber receives it immediately on subscribe().
  - Thread safety: bus daemon uses threading.Thread per connection.
    Client library uses threading.Thread for the socket reader loop.
    PyQt6 subscribers must use MundanaQtBridge, which dispatches
    callbacks via QMetaObject.invokeMethod on the Qt main thread.
  - Protocol: newline-delimited JSON over the socket. Each message
    is a single JSON object followed by \n. No framing headers.
  - Startup: daemon started by PRAESIDIUM launcher or by running
    python -m MundanaStateBus. Apps never start the daemon.
    If daemon is absent, MundanaClient.connect() raises
    BusDaemonNotRunningError — apps degrade gracefully.
  - Shutdown: daemon catches SIGTERM and SIGINT. Sends a
    bus.shutdown broadcast on mundana.bus_control before closing.
    Subscribers receive the shutdown notice and may clean up.

snake_case throughout. No filler. Every sentence carries information.
Write for a senior developer. Assume familiarity with Unix sockets,
threading, and PyQt6 signal/slot mechanics.

Sections:

1. Overview & Architecture
   - One paragraph summary of purpose and role in the Exocognii suite
   - Component table: Name | Role (one line each)
     Include: Bus Daemon, MundanaClient, MundanaQtBridge,
     Channel Manifest, Celestial Resolver (downstream consumer)

2. Tech Stack
   Table: Tool | Version | Justification
   Include: Python 3.11, socket (stdlib), threading (stdlib),
   json (stdlib), signal (stdlib), pathlib (stdlib)
   Justify the deliberate exclusion of asyncio (thread model chosen
   for PyQt6 compat) and FastAPI (HTTP overhead unacceptable).

3. Directory Tree
   Full annotated tree for:
   ArcaCognitorium/
   └── Exocognii/
       └── MundanaStateBus/
   Include: __main__.py, mundana_bus.py, mundana_client.py,
   mundana_qt_bridge.py, mundana_channels.py, __init__.py,
   tests/, requirements.txt, launch_mundana.sh

4. Module Breakdown
   Table: Module | Responsibility | Inputs | Outputs | Dependencies
   Cover all five modules: mundana_bus, mundana_client,
   mundana_qt_bridge, mundana_channels, __main__

5. Protocol Specification
   - JSON message schema — all message types:
     PUBLISH, SUBSCRIBE, UNSUBSCRIBE, REPLAY, ACK, ERROR, SHUTDOWN
   - Show example JSON for each message type
   - Describe the subscribe handshake sequence end to end
   - Describe the late-join replay sequence

6. Data Flow — 3 labeled paths:
   (a) Happy path: CAELESTIS engine publishes celestial tick →
       bus routes to Celestial Resolver subscriber →
       Resolver computes output → publishes to mundana.resolver →
       PRAESIDIUM widget receives and updates display
   (b) Subscriber joins after publish: late-join replay sequence
       from subscribe() through immediate delivery of last state
   (c) Daemon not running: MundanaClient.connect() raises
       BusDaemonNotRunningError → caller catches → app logs warning
       and continues with degraded (no celestial influence) mode

7. Integration Contract — how Exocognii apps wire to the bus
   - Subsection: Standard subscriber pattern (non-Qt app)
   - Subsection: PyQt6 subscriber pattern using MundanaQtBridge
     — show the full pattern: MundanaQtBridge init, signal
     declaration, callback wiring, thread safety guarantee
   - Subsection: Publisher pattern — connect(), publish(), disconnect()
   - Subsection: PRAESIDIUM integration — which channels it subscribes
     to and what widgets consume them
   - Subsection: Celestial chain integration — CAELESTIS → bus →
     Celestial Resolver → bus (mundana.resolver) → Tower entity engine

8. Code Stubs
   All public classes and methods. Type hints. One-line docstrings.
   Critical implementations must include pseudocode, not just stubs:
   - MundanaBus._route_message() — full routing logic pseudocode
   - MundanaClient.subscribe() — handshake + reader thread start
   - MundanaClient._reader_loop() — socket read, JSON parse, dispatch
   - MundanaQtBridge.__init__() — signal wiring pseudocode
   - MundanaQtBridge.on_bus_message() — invokeMethod dispatch pseudocode

9. Error Handling
   Per-module table: Error | Cause | Strategy
   Include startup failure paths. Include: BusChannelError,
   BusDaemonNotRunningError, BusConnectionLostError,
   MalformedPayloadError. Describe graceful degradation
   contract for all Exocognii apps when bus is unreachable.

10. Setup & Testing
    - requirements.txt (stdlib only — no third-party deps for core)
    - Install and run commands
    - launch_mundana.sh content verbatim
    - .desktop launcher entry if applicable
    - Unit tests:
      · test_channel_manifest.py — unknown channel raises BusChannelError
      · test_publish_subscribe.py — end-to-end pub/sub in-process
      · test_late_join_replay.py — subscriber receives last state on join
      · test_client_degraded.py — BusDaemonNotRunningError on connect
      · test_qt_bridge.py — MundanaQtBridge dispatches on Qt main thread

11. Extensibility — 5 features
    Name | User Value | Implementation Approach
    Include: payload schema validation, persistent ring buffer,
    channel metrics API, WebSocket bridge for Tower TUI,
    PRAESIDIUM bus health widget
```

---

---

*⟁*

*Ordo Discordia, Cosmos Inania*
*Mundana State Bus — IdeaForge v1.0*
