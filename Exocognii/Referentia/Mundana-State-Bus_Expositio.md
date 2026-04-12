# MUNDANA STATE BUS
### Expositio — Arca Cognitorium / Exocognii Infrastructure Layer
*v1.0 · 2026-04-08*

---

## I. Identity

**Name & Version:** Mundana State Bus — v1.0

**Tagline:** The nervous system of the Exocognii suite — a silent broker
that lets every application speak without knowing who is listening.

**Classification:** Infrastructure daemon and client library. No GUI.
No user-facing interface beyond a CLI status check. A service that
runs underneath the suite and is never seen directly.

**Status:** Built. Tested. 16/16 tests passing. Awaiting integration
with CAELESTIS and the Celestial Resolver, which are not yet built.

---

## II. Purpose

**Problem Statement:** The Exocognii applications — PRAESIDIUM, The
Dolium, VIGILARUM, the Tower, and others — need to share live state
without holding direct references to each other. The celestial engine
complex (CAELESTIS, CIRCADIANA, HOROLOGICA, and the other Machinae
Mundi Lapsus) needs to broadcast high-frequency ticks to multiple
consumers simultaneously. Before this bus existed, there was no
mechanism for that broadcast — apps were either isolated or required
bespoke wiring between each pair of communicating processes.

**Motivation:** The build sequence for the Machinae Mundi Lapsus is
CAELESTIS → Mundana State Bus → Celestial Resolver. Neither of the
downstream components can be built until the bus exists. Additionally,
PRAESIDIUM requires a pipeline state feed and a token ledger feed that
have no viable path without a cross-process broadcast layer.

**Intended Outcome:** Any Exocognii application can publish or subscribe
to a named channel without knowing which other applications are running.
CAELESTIS publishes a celestial tick; the Celestial Resolver, VIGILARUM,
and PRAESIDIUM all receive it independently. If PRAESIDIUM is not running,
no error occurs. If it starts late, it receives the last-known state
immediately on subscription. The suite breathes as one organism without
any component depending on any other.

**Anti-Purpose:** The bus does not persist state to disk. It does not
queue undelivered messages. It does not authenticate channels or enforce
payload schemas. It does not replace NUNTIUS — which handles Involucrum
observation routing over HTTP. The bus is for high-frequency local state
broadcast only.

---

## III. Audience

**Primary Users:** The Builder, building Exocognii applications that
require live state from other apps or the Machinae engines. The bus is
imported as a library — it is never operated directly by the Wizard
in normal use.

**Secondary Users:** The Wizard, indirectly — every celestial influence
felt in the Tower and every PRAESIDIUM widget that reflects live state
is downstream of this bus.

**Assumed Knowledge:** Python 3.11, Unix sockets, threading, PyQt6
signal/slot mechanics. Any application integrating with the bus must
understand the degraded mode contract.

**Out-of-Scope Audiences:** End users with no technical background.
The bus has no UI. It is infrastructure.

---

## IV. Design Philosophy

**Core Principles:**

*Raw socket over HTTP.* The Machinae engines tick at high frequency —
HOROLOGICA at ≥1 Hz, CIRCADIANA on sub-minute intervals. HTTP framing
overhead is unacceptable at that cadence. A Unix domain socket carries
a payload in a single `sendall()` call with sub-millisecond local
delivery.

*Threading over asyncio.* The PyQt6 event loop is incompatible with
`asyncio.run()`. Threading is explicit, debuggable, and sufficient for
the message rates involved. The `MundanaQtBridge` handles the one hard
threading constraint — callbacks from the reader thread must never
touch Qt widgets directly.

*Manifest over permissiveness.* Unknown channel names raise
`BusChannelError` immediately at the call site. Silent pass-through
would allow typos and schema drift to propagate invisibly through the
suite. Every channel is declared and ratified before it exists.

*Graceful degradation over hard dependency.* No Exocognii application
crashes because the bus is absent. Every app catches
`BusDaemonNotRunningError` on connect and enters a degraded mode with
static defaults. The bus is ambient infrastructure, not a hard
prerequisite.

*Late-join replay over blank initialisation.* When PRAESIDIUM starts
after CAELESTIS has been ticking for ten minutes, it should not display
blank celestial widgets until the next tick arrives. Last-state cache
per channel ensures every late subscriber initialises with current
state.

**Tradeoff Positions:**

Ephemeral over persistent. State lives in memory only. A bus restart
resets the cache. This was chosen deliberately — the Machinae engines
republish immediately on restart, so stale cache is never a problem,
and disk I/O would add latency on every publish.

Single daemon over distributed. One `mundana_bus.py` process handles
all routing. This is simpler, lower latency, and sufficient for a
local desktop suite. It is not designed for network deployment.

**Aesthetic Direction:** The bus is invisible. It has no aesthetic
register of its own. Its presence is felt in the behaviour of the
applications it connects — the celestial drift of entity mood, the
live token count in PRAESIDIUM, the circadian colour shift. The bus
earns no credit for these effects. It simply does not fail.

**What This Philosophy Rejects:** WebSockets (HTTP overhead, overkill
for local IPC), Redis/ZMQ (external dependencies, unnecessary for
desktop scale), asyncio (PyQt6 incompatibility), guaranteed delivery
queuing (the Machinae republish; queueing old ticks is harmful, not
helpful).

---

## V. Technical Concept

**Mental Model:** A post office with no memory. Publishers drop
envelopes at the desk; the desk copies them to every registered
subscriber for that channel and caches the last envelope in case
anyone asks. The post office does not care what is in the envelopes.
It does not store them. It simply routes.

**Core Abstractions:**

*Channel* — a named broadcast lane, declared in the manifest. Follows
the pattern `mundana.{engine_or_domain}`. New channels require Wizard
ratification. Unknown names are rejected.

*Publisher* — any connected client that calls `publish(channel,
payload)`. Sends one JSON message; the daemon routes it.

*Subscriber* — any connected client that calls `subscribe(channel,
callback)`. Receives a callback invocation for every publish on that
channel, plus an immediate REPLAY of the last-known state on subscribe.

*Late-join replay* — when a subscriber joins a channel that has already
received a publish, it receives the last payload immediately. Enables
cold-start initialisation.

*MundanaQtBridge* — a PyQt6-aware wrapper that interposes a
`QueuedConnection` signal between the bus reader thread and the
application slot. Guarantees that subscriber callbacks reach the Qt
main thread.

**Data Flow Overview:**

```
Publisher app
  └── MundanaClient.publish(channel, payload)
        └── JSON line → /tmp/mundana.sock
              └── MundanaBus._handle_publish()
                    ├── updates last_state[channel]
                    └── _route_message() → each subscriber socket
                          └── MundanaClient._reader_loop() → callback(payload)
```

For PyQt6 subscribers:

```
callback(payload)
  └── MundanaQtBridge.on_bus_message(payload)
        └── _relay.emit(payload)   [QueuedConnection]
              └── Qt event loop → qt_signal.emit(payload)
                    └── widget slot — main thread guaranteed
```

**System Boundaries:** The bus owns the socket at `/tmp/mundana.sock`,
the subscriber registry, and the last-state cache. It owns nothing
else. Payload schemas are the responsibility of the publishing
application. Channel ratification is the Wizard's prerogative.

**Key Technical Decisions:**

*`signal.signal()` is called only from the main thread.* Python's
signal module refuses signal handler installation from non-main threads.
`install_signal_handlers()` is separated from `start()` and called
exclusively in `__main__`. Test fixtures call `stop()` directly instead.

*`MundanaQtBridge` uses `_relay` as an internal signal, not direct
`emit()`.* Calling `qt_signal.emit()` from a background thread causes
undefined behaviour in Qt. The internal `_relay` signal with
`QueuedConnection` posts the call to the event queue, which the main
thread picks up safely.

*`__init__.py` guards the PyQt6 import.* `MundanaQtBridge` is
available as `None` if PyQt6 is not installed, with `_QT_AVAILABLE`
flag. This allows the core library to be imported in non-Qt contexts
(CLI tools, tests, Tower) without error.

---

## VI. Functional Scope

**Core Capabilities:**

- Publish/subscribe routing over Unix domain socket
- Named channel manifest with validation and rejection of unknown names
- Last-state cache per channel with immediate replay on subscribe
- Cross-process delivery: each Exocognii app connects as an independent
  client from its own venv
- `MundanaQtBridge` for thread-safe PyQt6 integration
- Graceful degradation: all apps continue if the bus is absent
- Clean shutdown: SIGTERM/SIGINT broadcast to all subscribers before
  socket close

**Supporting Capabilities:**

- `--check` dry-run mode in the installer
- `launch_mundana.sh` for PRAESIDIUM-managed startup
- PID file at `/tmp/mundana.pid` for process management
- Log file at `~/.local/share/exocognii/mundana.log`
- 16 unit tests covering: channel validation, pub/sub round-trip,
  late-join replay, degraded mode, Qt bridge thread safety

**Explicit Exclusions:**

- No disk persistence — state lives in memory only
- No authentication or channel security
- No payload schema validation (v1)
- No guaranteed delivery or message queuing
- No remote or network transport
- No admin UI
- No event history or ring buffer (v1)
- Does not replace NUNTIUS — HTTP Involucrum routing is out of scope

**Future Scope:**

- Payload schema validation per channel (TypedDict / Pydantic)
- Persistent ring buffer for diagnostic replay
- Channel metrics API (publish rate, subscriber count, last-seen)
- WebSocket bridge for Tower TUI consumers
- PRAESIDIUM bus health widget

---

## VII. Constraints & Context

**Technical Constraints:** Unix domain sockets are Linux/macOS only.
This is by design — the Exocognii suite targets Debian Trixie / KDE
Plasma 6 / X11 exclusively. Porting to Windows is not a goal.

Python 3.11 required. The `match` statement, `tomllib`, and
`missing_ok=True` on `Path.unlink()` are used throughout.

**External Dependencies:** None beyond Python stdlib for the core
daemon and client. PyQt6 is a dependency of the consuming application
venvs, not the bus library itself. The `MundanaQtBridge` import is
guarded so the core library loads cleanly in any Python environment.

**Infrastructure Dependencies:** The bus daemon must be running for
any cross-process state exchange to occur. CAELESTIS (not yet built)
is the primary publisher for the celestial channels. The Celestial
Resolver (not yet built) is the primary downstream consumer of
`mundana.caelestis`. All dependent functionality degrades gracefully
to static defaults when the bus is absent.

**Build Sequence Dependency:** The confirmed sequence is CAELESTIS →
Mundana State Bus → Celestial Resolver. Verificatio Chronicle item 09
(Celestial Chain) is unblocked by this build.

---

## VIII. Success Criteria

**Functional Success:** The daemon starts, the socket appears at
`/tmp/mundana.sock`, a publisher sends a payload, every registered
subscriber receives it within 200ms on the same machine, and a
late-joining subscriber receives the last payload on subscribe.
All 16 tests pass.

**User Success:** An Exocognii application integrates with the bus in
under twenty lines of code. PRAESIDIUM widgets reflect live celestial
state without any direct import of CAELESTIS modules. An app that
starts with the bus absent logs a single warning and continues without
crashing.

**Quality Benchmarks:** 16/16 tests passing. All modules parse with
`ast.parse()` clean. Socket delivery latency under 200ms local. No
PyQt6 thread safety violations under test.

**Failure Conditions:** Any Exocognii application crashes with an
unhandled exception because the bus is not running. A widget update
triggers a `QObject: Cannot create children for a parent that is in a
different thread` error. A publish to an unknown channel silently
succeeds.

---

## IX. Glossary

**Channel** — A named broadcast lane registered in `mundana_channels.py`.
Follows the pattern `mundana.{engine_or_domain}`. Only channels in the
manifest may be used. New channels require Wizard ratification.

**MundanaClient** — The sole interface Exocognii apps use to interact
with the bus. Handles connect, publish, subscribe, unsubscribe, and
disconnect. Runs a background reader thread after `connect()`.

**MundanaQtBridge** — PyQt6 wrapper around `MundanaClient`. Ensures
subscriber callbacks reach the Qt main thread via `QueuedConnection`.

**Late-join replay** — The behaviour where a new subscriber immediately
receives the last published payload on a channel, enabling cold-start
widget initialisation.

**Degraded mode** — The operational state of an Exocognii app when the
bus daemon is not running. `BusDaemonNotRunningError` is caught at
connect; all bus-dependent features fall back to static defaults. The
app does not crash.

**CHANNELS** — The dict in `mundana_channels.py` declaring all valid
channel names and their descriptions. The manifest is the single source
of truth. Unknown names raise `BusChannelError`.

**Machinae Mundi Lapsus** — The seven celestial engine components
(CAELESTIS, CIRCADIANA, HOROLOGICA, METEOROLOGICA, SOLARIS, TIDALIS,
LAPSUS) that publish live environmental and astronomical state to the
bus for downstream consumption by the Celestial Resolver and
application widgets.

**Celestial Resolver** — Not yet built. Subscribes to `mundana.caelestis`
and other Machinae channels; computes behavioural outputs for Tower
entities; publishes results to `mundana.resolver`.

---

## X. Revision Notes

╭──────────────┬──────────────────────────────────────────────────────────╮
│  Date        │  Note                                                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  2026-04-08  │  v1.0 initial expositio. Built from IdeaForge v1.0.     │
│              │  16/16 tests passing. Awaiting CAELESTIS integration.   │
╰──────────────┴──────────────────────────────────────────────────────────╯

---

*⟁*

*Ordo Discordia, Cosmos Inania*
*Mundana State Bus — Expositio v1.0*
