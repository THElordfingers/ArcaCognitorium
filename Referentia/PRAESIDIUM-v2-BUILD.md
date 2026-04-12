# PRAESIDIUM
## v2.0 — Construction Document
### Arca Cognitorium — Exocognii Suite
*Overhaul + NUNTIUS Integration · Claude Code Session Brief*

---

## CONTENTS

  I.    Philosophical Brief
  II.   Audit Findings — What Is Broken and Why
  III.  Scope of v2 Work
  IV.   Architecture
  V.    Module Breakdown
  VI.   Bug Fixes — Detailed Specifications
  VII.  New Features — Detailed Specifications
  VIII. Configuus Changes
  IX.   File Map
  X.    Constraints & Non-Negotiables
  XI.   ServicesWidget — Full Specification

---

# I. PHILOSOPHICAL BRIEF

PRAESIDIUM is the Wizard's ambient desktop surface. It lives on the
secondary monitor. It does not demand attention — it rewards it.
It is not a dashboard. It is not a launcher. It is a persistent
ambient canvas of live widgets that collectively represent the
current state of the Cogniverse and the Exocognii suite.

The Wizard should be able to glance at PRAESIDIUM and know: what is
the git state, what is being built, what tokens have been spent, what
is NUNTIUS doing, what is alive. Widgets move, resize, collapse, and
persist between sessions without thought. The canvas remembers itself.

PRAESIDIUM does not initiate — it observes, reflects, and occasionally
receives. The ChatWidget is an exception: it is an active interface.
Everything else is ambient.

The overhaul does not redesign PRAESIDIUM. It fixes what is broken,
wires what is missing, and removes what is dead.

---

# II. AUDIT FINDINGS

## Bug 1 — Duplicate Widgets on Startup

**Root cause:** `layout.json` accumulates stale widget entries from
previous ADD WIDGET sessions. Spawned widgets receive UUIDs like
`chatwidget_a3f2b1`. These persist in `layout.json` across sessions.
On the next launch, `_load_inner()` instantiates every entry in
`layout.json` verbatim — including all accumulated UUID-suffixed
duplicates alongside the canonical named entries (e.g. `chat_main`).
There is no deduplication guard and no cap on how many entries of the
same class can exist.

**Secondary cause:** `_spawn_widget()` in `praesidium_app.py` calls
`register_widget()` which calls `save()` immediately. If the app is
closed before the widget is repositioned, it persists at spawn
coordinates `(40 + offset, 40 + offset)` and loads at those
coordinates next session, visually stacked with other widgets.

**Tertiary cause:** The spawn offset formula `(len(self._widgets) % 8)
* 24` wraps at 8 — the 9th spawned widget lands at exactly the same
offset as the 1st.

## Bug 2 — Stale Port Defaults in Configuus

`configuus.py` falls back to port `8301` for `exvacua_loricum_api`
and `8302` for `perpetuum_aedificare_api`. The correct ports are
`8731` and `8732`. These fallbacks are reached any time the keys
are absent from `config.json`.

## Bug 3 — Dead Status Bar Slot

The `exo` slot in the status bar is declared and labelled
`● EXOCOGNII: —` but is never updated by anything. It remains
permanently at its initial state.

## Bug 4 — ChatWidget / TokenTracker Signal Wiring Fragility

`token_used → record_usage` wiring in `_load_widgets()` succeeds
only if `self._chat_widget` and `self._token_tracker` are both
discovered in `_wire_app_signals()` during the same load pass.
Widget load order follows Python dict iteration order (insertion
order in 3.7+, which matches JSON key order). This is currently
stable but semantically fragile — the wiring depends on iteration
order, not on an explicit post-load connection pass.

## Bug 5 — Spawn Offset Wraps at 8

`offset = (len(self._widgets) % 8) * 24` — after 8 spawned widgets
the 9th lands at `(40, 40)`, directly under the first.

---

# III. SCOPE OF V2 WORK

The following work is in scope. Nothing outside this list is to be
changed, refactored, or improved speculatively.

**Bug fixes:**
- Fix duplicate widget accumulation in layout.json
- Fix stale port defaults in configuus.py
- Fix dead `exo` status bar slot
- Fix ChatWidget / TokenTracker wiring fragility
- Fix spawn offset wrap

**New features:**
- NUNTIUS integration — NuntiusClient wired into PraesidiumApp
- Emission sites: chat completion, token usage, git status change,
  widget spawn, widget close
- NUNTIUS status widget (new: NuntiusStatusWidget) — reads /status,
  shows NUNTIUS uptime and per-consumer last outcome
- `exo` status bar slot driven by NUNTIUS status

**Configuus changes:**
- Fix port fallbacks
- Add `nuntius_api` property

- ServicesWidget — unified background service launcher and monitor
  covering NUNTIUS, Exvacua Loricum, Perpetuum Aedificare, and
  Mundana State Bus. Per-service start button, live status, toggleable
  detail panel.
- Referentia port fix — `configuus.praesidium_api` query in
  `referentia_aggregator.py` replaced with correct per-service URLs

**Not in scope:**
- Redesigning any existing widget
- Adding new non-NUNTIUS widgets
- Changing the canvas, topbar, or statusbar layout
- Migrating away from PyQt6
- Any change to `widget_base.py` or `theme.py`

---

# IV. ARCHITECTURE

PRAESIDIUM's architecture does not change in v2. The additions slot
into the existing structure cleanly.

```
PraesidiumApp (QMainWindow)
 ├── TopBar (42px) — buttons: ADD WIDGET, SAVE DEFAULT, CONFIG
 ├── Canvas (QWidget, free-float) — all ArcaneWidget instances live here
 │    ├── ArcaneWidget subclasses (loaded by LayoutManager)
 │    └── NuntiusStatusWidget (new — loaded via LayoutManager)
 ├── StatusBar (28px) — git / chat / token / exo slots
 ├── LayoutManager — persistence, signal wiring, dedup (fixed)
 ├── WidgetRegistry — instantiation factory (NuntiusStatusWidget added)
 └── NuntiusClient — instantiated once at app startup, passed to
                     emission sites via PraesidiumApp._nuntius
```

NuntiusClient is instantiated in `PraesidiumApp.__init__` after
`Configuus` is loaded. It is stored as `self._nuntius`. Emission
calls are fire-and-forget, wrapped in try/except
`NuntiusDaemonNotRunningError` at each site. PRAESIDIUM's function
is never gated on NUNTIUS availability.

---

# V. MODULE BREAKDOWN

## praesidium_app.py — changes

- Import `NuntiusClient`, `NuntiusDaemonNotRunningError` from
  `Exocognii.Nuntius.nuntius_client`
- Instantiate `self._nuntius = NuntiusClient()` in `__init__` after
  config load. Catch `NuntiusConfigError` and set `self._nuntius =
  None` — graceful degradation.
- Add `_emit(payload: dict)` private method — wraps the emit call
  with the try/except and the None guard.
- Wire emission sites (see Section VII).
- Fix `_spawn_widget()` offset formula.
- Fix ChatWidget/TokenTracker post-load wiring pass.
- Drive `exo` status slot from NUNTIUS status poll.

## layout_manager.py — changes

- Add deduplication in `_load_inner()`: after building the widget
  list, check for multiple entries of the same `cls`. Keep only the
  first (oldest by JSON order). Log and purge duplicates.
- Optionally: add a `max_per_class` dict to `DEFAULT_LAYOUT` — but
  the simpler fix (keep first, purge rest) is sufficient for v2.

## configuus.py — changes

- Fix `exvacua_loricum_api` fallback: `8731`
- Fix `perpetuum_aedificare_api` fallback: `8732`
- Add `nuntius_api` property:
  `return self._data.get("nuntius_api", {"host": "127.0.0.1",
  "port": 8730})`
- Add `nuntius_url` computed property:
  `return f"http://{d['host']}:{d['port']}"` where `d =
  self.nuntius_api`

## widget_registry.py — changes

- Add `NuntiusStatusWidget` to `WIDGET_MANIFEST`:
  `"NuntiusStatusWidget": "widgets.nuntius_status_widget"`
- Add construction case in `_construct()`:
  `NuntiusStatusWidget(widget_id=widget_id, configuus=self._cfg,
  parent=parent)`

## widgets/nuntius_status_widget.py — new file

See Section VII for full specification.

---

# VI. BUG FIXES — DETAILED SPECIFICATIONS

## Fix 1 — Duplicate Widget Deduplication

**File:** `layout_manager.py`, method `_load_inner()`

After the widget instantiation loop completes, add a deduplication
pass before the synchronous write:

```python
# Deduplication: keep only the first entry per cls.
# Duplicates accumulate from ADD WIDGET sessions. Purge all but the
# canonical (first) entry of each class found in load order.
seen_classes: dict[str, str] = {}  # cls → first widget_id
dup_ids: list[str] = []
for wid, entry in list(self._layout.items()):
    cls = entry["cls"]
    if cls in seen_classes:
        print(
            f"[LayoutManager] Dedup: purging {wid!r} "
            f"(duplicate of {seen_classes[cls]!r} [{cls}])"
        )
        dup_ids.append(wid)
    else:
        seen_classes[cls] = wid

for wid in dup_ids:
    del self._layout[wid]
    # Also destroy the instantiated widget object
    w_to_destroy = next((w for w in widgets if w.widget_id == wid), None)
    if w_to_destroy:
        w_to_destroy.deleteLater()
        widgets.remove(w_to_destroy)

if dup_ids:
    print(f"[LayoutManager] Dedup removed {len(dup_ids)} duplicate(s).")
```

This runs after the main instantiation loop and before the
synchronous write, so the clean deduplicated layout is written
immediately.

**Note:** The dedup strategy is "keep first, purge rest" — the
canonical named entries (`chat_main`, `git_main`, etc.) appear
first in JSON, so they are always preserved. UUID-suffixed entries
from ADD WIDGET sessions appear later and are purged.

## Fix 2 — Configuus Port Fallbacks

**File:** `configuus.py`

```python
@property
def exvacua_loricum_api(self) -> str:
    return self._data.get("exvacua_loricum_api", "http://localhost:8731")

@property
def perpetuum_aedificare_api(self) -> str:
    return self._data.get("perpetuum_aedificare_api", "http://localhost:8732")
```

## Fix 3 — Spawn Offset Wrap

**File:** `praesidium_app.py`, method `_spawn_widget()`

Replace:
```python
offset = (len(self._widgets) % 8) * 24
w.move(40 + offset, 40 + offset)
```

With a running counter that does not wrap:
```python
# Use a non-wrapping counter stored on the instance
if not hasattr(self, "_spawn_count"):
    self._spawn_count = 0
offset = self._spawn_count * 24
self._spawn_count += 1
w.move(min(40 + offset, 400), min(40 + offset, 400))
```

The `min(... 400)` cap prevents widgets spawning off-canvas.
Reset `_spawn_count` to 0 in `__init__`.

## Fix 4 — ChatWidget / TokenTracker Wiring

**File:** `praesidium_app.py`, method `_load_widgets()`

After the loop that calls `_wire_app_signals(w)` for each widget,
add an explicit post-load wiring pass that does not depend on
iteration order:

```python
# Post-load: wire inter-widget signals explicitly, order-independent
chat = next(
    (w for w in self._widgets if type(w).__name__ == "ChatWidget"), None
)
token = next(
    (w for w in self._widgets if type(w).__name__ == "TokenTracker"), None
)
if chat and token:
    try:
        chat.token_used.connect(token.record_usage)
    except RuntimeError:
        pass  # already connected — double-connection guard
if token:
    try:
        token.usage_recorded.connect(self._on_token_usage)
    except RuntimeError:
        pass
self._chat_widget   = chat
self._token_tracker = token
```

Remove the fragile discovery-during-loop pattern from
`_wire_app_signals()` — that method should only handle per-widget
app-level signals (git status, widget status), not inter-widget
wiring.

---

# VII. NEW FEATURES — DETAILED SPECIFICATIONS

## NuntiusClient Integration

**Instantiation in `praesidium_app.py`:**

```python
# In __init__, after Configuus is loaded:
try:
    from pathlib import Path as _Path
    import sys as _sys
    _sys.path.insert(0, str(self._cfg.arca_repo_path / "Exocognii"))
    from Nuntius.nuntius_client import (
        NuntiusClient, NuntiusDaemonNotRunningError
    )
    self._nuntius = NuntiusClient()
    self._NuntiusDaemonNotRunningError = NuntiusDaemonNotRunningError
except Exception as e:
    print(f"[PRAESIDIUM] NuntiusClient unavailable: {e}")
    self._nuntius = None
    self._NuntiusDaemonNotRunningError = Exception
```

**`_emit()` helper:**

```python
def _emit(self, payload: dict) -> None:
    """Fire-and-forget Involucrum emission. Silently degrades if NUNTIUS absent."""
    if self._nuntius is None:
        return
    try:
        self._nuntius.emit(payload)
    except self._NuntiusDaemonNotRunningError:
        pass  # NUNTIUS not running — observation dropped silently
```

**Involucrum helper:**

```python
def _involucrum(self, hint: str, body: dict) -> dict:
    from datetime import datetime, timezone
    return {
        "source_app": "Praesidium",
        "source_version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hint": hint,
        "body": body,
    }
```

## Emission Sites

**Chat completion** — in `_on_widget_status()`, when status is `ok`
and widget is a chat widget, after updating the status bar label:

```python
if widget_id.startswith("chat") and status == "ok":
    self._emit(self._involucrum("chat_complete", {
        "widget_id": widget_id,
        "event": "response_complete",
    }))
```

**Token usage** — in `_on_token_usage()`, after updating the label:

```python
self._emit(self._involucrum("token_usage", {
    "model": model,
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "session_id": session_id,
    "total": input_tokens + output_tokens,
}))
```

**Git status change** — in `_on_git_status()`, after updating label:

```python
self._emit(self._involucrum("git_status", {
    "widget_id": widget_id,
    "status": status,
}))
```

**Widget spawn** — in `_spawn_widget()`, after `register_widget()`:

```python
self._emit(self._involucrum("widget_spawn", {
    "widget_id": widget_id,
    "cls": cls_name,
}))
```

**Widget close** — `ArcaneWidget._on_close()` already emits
`visibility_changed`. Wire a handler in `_wire_app_signals()`:

```python
if hasattr(w, "visibility_changed"):
    w.visibility_changed.connect(self._on_widget_visibility)
```

```python
def _on_widget_visibility(self, widget_id: str, visible: bool) -> None:
    if not visible:
        self._emit(self._involucrum("widget_close", {
            "widget_id": widget_id,
        }))
```

## NuntiusStatusWidget

**File:** `widgets/nuntius_status_widget.py`

A new ArcaneWidget subclass. Polls `GET /status` on a 5-second
timer. Displays NUNTIUS uptime and per-consumer last outcome.
Also drives the `exo` status bar slot via a new signal.

**Signal:**
```python
nuntius_status_changed = pyqtSignal(str, str)
# (status: 'ok' | 'warn' | 'error' | 'idle', summary: str)
```

**Constructor:**
```python
def __init__(self, widget_id: str, configuus: Configuus, parent=None):
```

**Polling:**
- `QTimer` at 5000ms interval
- `httpx.get(nuntius_url + "/status", timeout=2.0)` in a
  `QThread` worker (do not block the UI thread)
- On success: parse response, update display, emit
  `nuntius_status_changed("ok", summary_string)`
- On failure (connection error, timeout): display "NUNTIUS offline",
  emit `nuntius_status_changed("error", "offline")`

**Display layout:**

```
┌─ NUNTIUS STATUS ────────────────── ● ─┐
│  Status: ok    Uptime: 3721s           │
│  exvacua_loricum     ✓  2026-04-08...  │
│  perpetuum_aedificare ✓  2026-04-08... │
└────────────────────────────────────────┘
```

Use `QLabel` rows. Style with `C_GOLD_DIM` for labels, `C_STATUS_OK`
/ `C_STATUS_ERROR` for outcome indicators. No QTableWidget — labels
only, laid out with QVBoxLayout + QHBoxLayout rows.

**`exo` slot wiring in `PraesidiumApp`:**

In `_wire_app_signals()`:
```python
if cls == "NuntiusStatusWidget":
    w.nuntius_status_changed.connect(self._on_nuntius_status)
```

```python
def _on_nuntius_status(self, status: str, summary: str) -> None:
    lbl = self._status_labels.get("exo")
    if not lbl:
        return
    colour_map = {
        "ok":    C_STATUS_OK,
        "warn":  "#d4af37",
        "error": "#8b1a1a",
        "idle":  C_STATUS_IDLE,
    }
    text_map = {
        "ok":    f"● NUNTIUS: {summary}",
        "warn":  f"● NUNTIUS: {summary}",
        "error": "● NUNTIUS: Offline",
        "idle":  "● NUNTIUS: —",
    }
    lbl.setText(text_map.get(status, "● NUNTIUS: —"))
    lbl.setStyleSheet(
        f"color: {colour_map.get(status, C_STATUS_IDLE)}; "
        "font-family: Georgia, serif; font-size: 10px; background: transparent;"
    )
```

Also rename the `exo` status bar label to read `● NUNTIUS: —`
initially (was `● EXOCOGNII: —`).

Add `NuntiusStatusWidget` to `DEFAULT_LAYOUT` in `layout_manager.py`:

```python
"nuntius_main": {
    "cls": "NuntiusStatusWidget",
    "x": 1360, "y": 8, "w": 240, "h": 160,
    "visible": True, "locked": False, "docked": False, "extra": {},
},
```

---

# VIII. CONFIGUUS CHANGES

The following properties must be present in `configuus.py` after v2.
Show all changes as complete method replacements, not patches.

```python
@property
def exvacua_loricum_api(self) -> str:
    return self._data.get("exvacua_loricum_api", "http://localhost:8731")

@property
def perpetuum_aedificare_api(self) -> str:
    return self._data.get("perpetuum_aedificare_api", "http://localhost:8732")

@property
def nuntius_api(self) -> dict:
    """Returns the nuntius_api block from Configuus."""
    return self._data.get("nuntius_api", {"host": "127.0.0.1", "port": 8730})

@property
def nuntius_url(self) -> str:
    """Computed NUNTIUS base URL from nuntius_api block."""
    d = self.nuntius_api
    return f"http://{d.get('host', '127.0.0.1')}:{d.get('port', 8730)}"
```

---

# IX. FILE MAP

Files touched in v2. All others are read-only.

```
Exocognii/Praesidium/
├── praesidium_app.py        — NuntiusClient wiring, emission sites,
│                              spawn fix, post-load wiring pass,
│                              exo → nuntius status handler
├── layout_manager.py        — deduplication pass in _load_inner(),
│                              NuntiusStatusWidget in DEFAULT_LAYOUT
├── configuus.py             — port fallback fixes, nuntius_api,
│                              nuntius_url properties
├── widget_registry.py       — NuntiusStatusWidget registration
└── widgets/
    ├── nuntius_status_widget.py   — new file (full implementation)
    └── services_widget.py         — new file (full implementation)
```

Files that must NOT be touched:

```
widget_base.py
theme.py
run.py
widgets/chat_widget.py
widgets/token_tracker.py
widgets/git_widget.py
widgets/todo_board.py
widgets/app_launcher.py
widgets/style_reference.py
widgets/status_legend.py
widgets/display_panel.py
widgets/diff_viewer.py
widgets/repo_activity.py
widgets/quick_file_drop.py
widgets/referentia_aggregator.py
widgets/art_widget.py
widgets/glyph_browser.py
```

---

# X. CONSTRAINTS & NON-NEGOTIABLES

- PyQt6 exclusively. No PySide6.
- No new dependencies beyond httpx (already in venv-PRAESIDIUM via
  the existing stack).
- NuntiusClient import path:
  `sys.path.insert(0, str(arca_repo_path / "Exocognii"))`
  then `from Nuntius.nuntius_client import NuntiusClient`.
- All NuntiusClient emit calls are fire-and-forget. PRAESIDIUM must
  never block on NUNTIUS.
- NuntiusStatusWidget HTTP calls must run off the UI thread.
  Use a QThread worker — not QTimer + blocking call.
- Deduplication strategy: keep first occurrence of each cls,
  purge subsequent. Log every purge. Never silently drop the
  canonical named widget.
- `layout.json` must be in a valid, deduplicated state after every
  successful load, before the window is shown.
- Token constants (C_GOLD, C_STATUS_OK, etc.) are used everywhere.
  Never hardcode hex values in new widget code.
- `ARCA_API_KEY` → `CLAUDE_API_KEY`. Not relevant here but noted.
- Version headers: every modified file gets its version bumped.
  New file starts at v1.0.0.
- Full file rewrites preferred over surgical patches for
  `praesidium_app.py` and `layout_manager.py` given the scope
  of changes. `configuus.py` and `widget_registry.py` can be
  patched.

---

*⟁*

*Ordo Discordia, Cosmos Inania*
*PRAESIDIUM v2 — Construction Document*

---

# XI. SERVICEWIDGET — FULL SPECIFICATION

## Purpose

A single unified widget that launches, monitors, and optionally
inspects the four background services of the Exocognii suite.
The Wizard should be able to glance at it and know which services
are alive, and start any that are not — without leaving PRAESIDIUM.

## Services Registry

Four services. All metadata is defined in a static list inside the
widget — not in Configuus, as these are not user-configurable.

╭─────────────────────────┬────────────────────────────────────────────────────────────┬────────╮
│  Name                   │  Launcher                                                  │  Health │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┤
│  NUNTIUS                │  Exocognii/Nuntius/launch_nuntius.sh                       │  HTTP  │
│                         │  cwd: ~/ArcaCognitorium                                    │  8730  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┤
│  Exvacua Loricum        │  Exocognii/ExvacuaLoricum/Exvacua.sh                       │  HTTP  │
│                         │  cwd: ~/ArcaCognitorium/Exocognii/ExvacuaLoricum           │  8731  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┤
│  Perpetuum Aedificare   │  Exocognii/PerpetuumAedificare/Perpetuum.sh                │  HTTP  │
│                         │  cwd: ~/ArcaCognitorium/Exocognii/PerpetuumAedificare      │  8732  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┤
│  Mundana State Bus      │  Exocognii/MundanaStateBus/launch_mundana.sh               │  SOCK  │
│                         │  cwd: ~/ArcaCognitorium                                    │  unix  │
╰─────────────────────────┴────────────────────────────────────────────────────────────┴────────╯

Health check details:
- NUNTIUS: `GET http://localhost:8730/status` — timeout 2s
- Exvacua Loricum: `GET http://localhost:8731/status` — timeout 2s
- Perpetuum Aedificare: `GET http://localhost:8732/status` — timeout 2s
- Mundana State Bus: check `/tmp/mundana.sock` exists as a socket file
  (`Path("/tmp/mundana.sock").exists()` and `stat.S_ISSOCK(...)`)

All launcher scripts are run relative to `configuus.arca_repo_path`.
Launcher path construction: `arca_repo_path / relative_script_path`.


## Layout

```
┌─ SERVICES ─────────────────────────────────── ● ─┐
│                                                    │
│  ● NUNTIUS                 [ok]       [▶ START]   │
│  ● Exvacua Loricum         [ok]       [▶ START]   │
│  ● Perpetuum Aedificare    [offline]  [▶ START]   │
│  ● Mundana State Bus       [ok]       [▶ START]   │
│                                                    │
│  [▾ DETAIL]                                        │
│ ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌  │
│  [detail panel — collapsed by default]             │
└────────────────────────────────────────────────────┘
```

Each service row: status dot + name label (left-aligned), status
badge (ok/offline/starting), START button (right-aligned).

START button label changes:
- Service offline → `▶ START`
- Service starting (process launched, health not yet confirmed) →
  `… STARTING` (disabled, gold dim)
- Service online → `■ RUNNING` (disabled, C_STATUS_OK)

The detail panel is a collapsible QWidget below the service rows,
toggled by the `▾ DETAIL` / `▲ DETAIL` button. It shows a scrolling
log of recent launch output (stdout/stderr from the most recently
launched service process). Collapsed by default.


## Constructor

```python
class ServicesWidget(ArcaneWidget):
    def __init__(
        self,
        widget_id: str,
        configuus: Configuus,
        parent=None,
    ):
```

Service list is defined as a module-level constant — not derived
from Configuus. `configuus` is passed only for `arca_repo_path`.


## Service Record Dataclass

```python
@dataclass
class _ServiceDef:
    name: str           # display name
    script: str         # path relative to arca_repo_path
    health_type: str    # 'http' | 'socket'
    health_target: str  # URL for http, socket path for socket
```


## Polling

A single `QTimer` at 5000ms polls all four services on each tick.
Each HTTP check uses `httpx.get(..., timeout=2.0)` in a `QThread`
worker — not on the UI thread. The socket check is synchronous and
cheap (stat call only — no connection).

On each poll cycle, fire one worker thread that checks all four
services sequentially and emits a single signal with all results.
Do not fire four separate threads.

```python
class _HealthWorker(QThread):
    results_ready = pyqtSignal(list)
    # list of (service_name: str, alive: bool)
```


## Launch Mechanism

Each START button click:
1. Sets service state to `starting` — button becomes disabled,
   label shows `… STARTING`.
2. Launches the script via `subprocess.Popen`:

```python
proc = subprocess.Popen(
    ["bash", str(script_path)],
    cwd=str(arca_repo_path),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
```

3. Spawns a `QThread` that reads stdout line by line and emits
   each line to the detail panel log.
4. Next poll cycle confirms the service is alive and updates the
   button to `■ RUNNING`.

PRAESIDIUM does not manage service shutdown. START only. The Wizard
kills services independently.

If a service is already `online` or `starting`, the START button is
disabled — clicking it does nothing.


## Detail Panel

A `QFrame` containing a `QTextEdit` (read-only, monospaced, dark
background). Shows stdout/stderr lines from the most recently
launched process — not a historical log, just the current session's
launch output. Cleared on each new launch.

Toggle button label: `▾ DETAIL` when collapsed, `▲ DETAIL` when
expanded. Uses `QPropertyAnimation` on `maximumHeight`, matching
the pattern in `ArcaneWidget._collapse()` / `_expand()`.

Detail panel default height when expanded: 120px.


## Status Dot Colours

The widget-level status dot in the ArcaneWidget header reflects the
aggregate state of all services:
- All online → `C_STATUS_OK`
- Any starting → `C_STATUS_WARN` (gold)
- Any offline → `C_STATUS_ERROR`

Per-service status dots in the rows use the same colour mapping.


## Widget Registration

Add to `WIDGET_MANIFEST` in `widget_registry.py`:
```python
"ServicesWidget": "widgets.services_widget"
```

Add to `_construct()`:
```python
if name == "ServicesWidget":
    return cls(widget_id=widget_id, configuus=self._cfg, parent=parent)
```

Add to `DEFAULT_LAYOUT` in `layout_manager.py`:
```python
"services_main": {
    "cls": "ServicesWidget",
    "x": 1360, "y": 176, "w": 280, "h": 220,
    "visible": True, "locked": False, "docked": False, "extra": {},
},
```

Add to the ADD WIDGET picker labels in `praesidium_app.py`:
```python
"ServicesWidget": "⚙  Services",
```


## Referentia Port Fix

`referentia_aggregator.py` currently queries `configuus.praesidium_api`
(port 8300) for `/lore/search` and `/build/nodi`. This is wrong.
The correct endpoints are:

- Lore search: `configuus.exvacua_loricum_api + "/lore/search"`
- Build nodes: `configuus.perpetuum_aedificare_api + "/build/nodi"`

This is a two-line fix in `referentia_aggregator.py` — the only
change to that file. It is now in scope for v2 since Exvacua Loricum
and Perpetuum Aedificare are confirmed running.

`referentia_aggregator.py` is added to the touched files list. The
change is a surgical patch — only the two URL construction lines.


## Additional Constraint

- `subprocess.Popen` for service launch must use `bash` explicitly.
  The launcher scripts use bash-specific syntax (`source`, process
  substitution in `launch_mundana.sh`). `sh` will fail on these.
- Mundana socket check: use `os.path.exists` + `stat.S_ISSOCK` —
  do not attempt to connect to the socket. Connection is the
  MundanaClient's job, not PRAESIDIUM's.
- Detail panel log is cleared on each START press. It does not
  persist across sessions.

---

# XI. SERVICES WIDGET — ServicesWidget

## Overview

A single unified ArcaneWidget that displays the status of all
background Exocognii services and allows the Wizard to launch each
one individually. The widget is always visible on the canvas. It does
not stop services — launch only. Monitoring is passive (poll-based).
Log tail is toggleable per service.

**File:** `widgets/services_widget.py`
**Registry entry:** `"ServicesWidget": "widgets.services_widget"`
**DEFAULT_LAYOUT entry:**

```python
"services_main": {
    "cls": "ServicesWidget",
    "x": 1360, "y": 176, "w": 260, "h": 340,
    "visible": True, "locked": False, "docked": False, "extra": {},
},
```

---

## Service Registry

Four services are hardcoded in the widget. They are not configurable
via Configuus in v1 — the paths, ports, and health strategies are
fixed. New services require a code change.

╭──────────────────────────┬────────────────────────────────────────────┬────────────────────────────────────────╮
│  Service                 │  Launcher Path (relative to arca_repo)     │  Health Strategy                       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  NUNTIUS                 │  Exocognii/Nuntius/launch_niuntius.sh      │  GET http://127.0.0.1:8730/status      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Exvacua Loricum         │  Exocognii/ExvacuaLoricum/Exvacua.sh       │  GET http://127.0.0.1:8731/status      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Perpetuum Aedificare    │  Exocognii/PerpetuumAedificare/Perpetuum.sh│  GET http://127.0.0.1:8732/status      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Mundana State Bus       │  Exocognii/MundanaStateBus/launch_mundana.sh│ Socket exists: /tmp/mundana.sock      │
╰──────────────────────────┴────────────────────────────────────────────┴────────────────────────────────────────╯

Health checks run every 5 seconds via a QTimer. Each check runs in
a QThread worker — never on the UI thread.

---

## Display Layout

Each service occupies one row. Rows are stacked in QVBoxLayout.
Below the service rows is a collapsible log tail panel (one per
service, toggled independently).

```
┌─ SERVICES ─────────────────────────────── ● ─┐
│                                               │
│  ● NUNTIUS              [RUNNING]  [▶ LAUNCH] │
│    [▼ LOG]                                    │
│  ┌─────────────────────────────────────────┐  │
│  │ 2026-04-08  emit ok  exvacua_loricum    │  │
│  │ 2026-04-08  emit ok  perpetuum_aed...   │  │
│  └─────────────────────────────────────────┘  │
│                                               │
│  ● EXVACUA LORICUM      [RUNNING]  [▶ LAUNCH] │
│    [▼ LOG]                                    │
│                                               │
│  ● PERPETUUM AEDIFICARE [RUNNING]  [▶ LAUNCH] │
│    [▼ LOG]                                    │
│                                               │
│  ● MUNDANA STATE BUS    [OFFLINE]  [▶ LAUNCH] │
│    [▼ LOG]                                    │
│                                               │
└───────────────────────────────────────────────┘
```

Status indicator colours:
- RUNNING — `C_STATUS_OK`
- OFFLINE — `C_STATUS_ERROR`
- STARTING — `C_STATUS_WARN` (set immediately on LAUNCH click,
  cleared by next health poll)
- UNKNOWN — `C_STATUS_IDLE` (initial state before first poll)

---

## Service Row Widget

Each row is a `_ServiceRow(QFrame)` — not an ArcaneWidget subclass,
just a plain QFrame used internally by ServicesWidget.

```python
class _ServiceRow(QFrame):
    launch_requested = pyqtSignal(str)   # service_id
    log_toggled      = pyqtSignal(str)   # service_id
```

Layout per row:

```
[● dot]  [Name label]  [Status label]  [▶ LAUNCH button]
[▼ LOG button]
[log_panel QTextEdit — hidden by default]
```

The `▼ LOG` button toggles `log_panel.setVisible(not visible)`.
The `log_panel` is a read-only `QTextEdit`, 80px tall when visible,
styled with `C_BG` background and `C_GOLD_DIM` text, monospace font.
When hidden the row height collapses to ~52px. When visible ~134px.
The parent ServicesWidget does not need to know about this — the row
manages its own collapse. ServicesWidget height will expand/contract
naturally since rows are in a QVBoxLayout with a QScrollArea wrapper.

---

## Launch Behaviour

On `▶ LAUNCH` click:

1. Set row status to STARTING (`C_STATUS_WARN`).
2. Disable the LAUNCH button.
3. Run `subprocess.Popen(["/bin/bash", launcher_path], ...)` with
   `stdout=PIPE`, `stderr=STDOUT`. The process is detached — PRAESIDIUM
   does not own it. PRAESIDIUM does not track its PID.
4. Capture the first 20 lines of stdout into the row's log panel via
   a `QThread` worker that reads line-by-line and emits a signal back
   to the main thread.
5. After 3 seconds, re-enable the LAUNCH button regardless of outcome.
   Status will be corrected by the next health poll.

**Important:** PRAESIDIUM never stops a service. No stop button.
The Wizard kills services from the terminal.

---

## Health Check Worker

```python
class _HealthWorker(QObject):
    result = pyqtSignal(str, str)  # service_id, 'running'|'offline'|'unknown'
```

One worker per service, run in a `QThread`. On each poll tick:

- HTTP services: `httpx.get(status_url, timeout=1.5)`. If 200 →
  `running`. If connection error or timeout → `offline`.
- Mundana: `Path("/tmp/mundana.sock").exists()` → `running` if True,
  `offline` if False. No connection attempt — existence check only.

All workers share a single 5-second `QTimer` in ServicesWidget that
triggers all four checks simultaneously via `asyncio`-free threading
(one `QThread` per service, reused across polls).

---

## Log Tail — NUNTIUS

NUNTIUS is the only service with a structured log API (`GET /log`).
When its log panel is visible and the service is RUNNING, poll
`GET http://127.0.0.1:8730/log?limit=10` every 5 seconds and
display the 10 most recent emission records as formatted lines:

```
{timestamp}  {source_app}  {hint}  {consumer_name}  {outcome}
```

For Exvacua, Perpetuum, and Mundana — the log panel shows launch
stdout only (captured at launch time). It does not live-update after
launch. The `▼ LOG` label reflects this:

- NUNTIUS: `▼ LIVE LOG`
- Others: `▼ LAUNCH LOG`

---

## Constructor

```python
class ServicesWidget(ArcaneWidget):
    def __init__(
        self,
        widget_id: str,
        configuus: Configuus,
        parent=None,
    ) -> None:
```

`configuus` is needed for `arca_repo_path` to resolve launcher paths.

---

## Widget Registry Update

In `widget_registry.py`, add to `WIDGET_MANIFEST`:

```python
"ServicesWidget": "widgets.services_widget",
```

Add construction case in `_construct()`:

```python
if name == "ServicesWidget":
    return cls(widget_id=widget_id, configuus=self._cfg, parent=parent)
```

---

## NuntiusStatusWidget — Disposition

With ServicesWidget now covering NUNTIUS health and log display,
the standalone `NuntiusStatusWidget` scoped in Section VII is
**retired**. The `exo` / NUNTIUS status bar slot is instead driven
by ServicesWidget emitting a signal when NUNTIUS health changes:

```python
# In ServicesWidget:
nuntius_status_changed = pyqtSignal(str, str)
# (status: 'running'|'offline'|'starting'|'unknown', detail: str)
```

Wire in `PraesidiumApp._wire_app_signals()`:

```python
if cls == "ServicesWidget":
    w.nuntius_status_changed.connect(self._on_nuntius_status)
```

Remove `NuntiusStatusWidget` from DEFAULT_LAYOUT, WIDGET_MANIFEST,
and widget_registry._construct(). It is not built.

---

*⟁*
*ServicesWidget — Addendum to PRAESIDIUM v2 Build Document*
