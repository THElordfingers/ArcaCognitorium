# Vigilarum Omnia v2
### Expositio · Application Identity and Purpose Document

---

## I. IDENTITY

**Name & Version:** Vigilarum Omnia v2

**Tagline:** The sky, made legible.

**Classification:** Standalone desktop instrument. A multi-window, multi-widget
astronomical display system.

**Status:** Active development — v2 migration complete, ready for deployment.

---

## II. PURPOSE

**Problem Statement:** The Tower's Machinae Mundi Lapsus depend on accurate,
real-time Vedic sidereal celestial data. Before that system is wired, there is
no instrument that makes the sky's current state visible and verifiable in
real time. Separately, there is no tool for the Wizard to simply observe the sky
as an ambient presence on secondary monitors without opening the Tower.

**Motivation:** pyswisseph can calculate anything about the sky. The gap is
presentation — turning its numerical output into something watchable, organised,
and beautiful. Vigilarum exists to fill that gap as a standalone demonstrative
instrument.

**Intended Outcome:** One or more secondary monitors continuously display the
current moon phase, planetary positions, panchang elements, and celestial
rhythms. The Wizard can glance and know. The sky is always visible.

**Anti-Purpose:** Vigilarum does not integrate with the Tower, write to any Tower
storage, or influence Tower behaviour in v2. It does not generate alerts or
notifications. It is not a planning tool.

---

## III. AUDIENCE

**Primary Users:** The Wizard (LordFingers). Single-user. Runs across 3 monitors
on CastrumDigitos (Debian Trixie / KDE Plasma 6).

**Assumed Knowledge:** Familiarity with running Python scripts from terminal.
No astronomical background required to run the app; modest knowledge enriches
the reading of the data.

**Out-of-Scope Audiences:** No multi-user scenario. No public distribution.

---

## IV. DESIGN PHILOSOPHY

**Core Principles:**
- Darkness as material. Every surface is void; gold signals the living data.
- The sky needs no explanation. Data is presented, not interpreted.
- Standalone without apology. No Tower coupling. No network calls.
- Graceful in failure. No state file → placeholder. Engine error → last good state persists.
- Composition over monolith. 38 independent widget types composable across 9 displays.

**Tradeoff Positions:**
- Correctness over richness. Lahiri sidereal exclusively. No tropical.
- Readability over density. Each widget has one primary datum.
- Repaints over polling complexity. Widgets repaint on every state update rather
  than diffing — simpler code, invisible cost at 1Hz.

**Aesthetic Direction:** Chromata Arcana. Near-black void backgrounds, gold
primary accent, Georgia serif. The instrument should feel like a carved and
illuminated reference.

**What This Rejects:** System tray integration, browser-based rendering,
notification systems, multi-user API exposure.

---

## V. TECHNICAL CONCEPT

**Mental Model:** Control panel = the engine room. Display windows = instrument
faces. State file = the wire between them. Painter functions = the rendering
logic, completely separate from widget lifecycle.

**Core Abstractions:**

- `ArcaneCard` — base widget. Owns its panel chrome (border, section label).
  Either displays QLabel children (TextCard) or delegates entirely to a painter
  function (VisualCard).
- `EngineWorker` — QThread that wraps `calculate_all()`. Emits finished/error
  signals. Never blocks the main thread.
- `state.json` — the single source of truth for current sky state. Written
  atomically (tmp file → replace). Read on every display poll tick.
- `painters.py` — pure functions. `(QPainter, QRectF, data) → None`. No widget
  references, no side effects beyond drawing. Independently testable.

**Data Flow:** Engine calculates every 60 seconds and writes state. Clock updates
time fields every second without rerunning the engine. Display windows poll every
second, remount widgets if assignment changes, call `update_data(state)` on all
mounted widgets.

**System Boundaries:** Vigilarum owns `~/.vigilarum/`. It reads nothing from the
Tower. The Tower reads nothing from Vigilarum. The only future bridge (Tier 6
extensibility) would be CAELESTIS reading `state.json` as an input source — a
one-way read by an external party, requiring no change to Vigilarum itself.

**Key Technical Decisions:**
- File IPC over socket IPC — simpler, survives process restarts, displays
  degrade to last known state rather than crashing.
- QThread for engine — pyswisseph calls take ~100ms under load. Main thread
  must not block.
- painters.py separation — painter functions are independently testable and
  swappable. Widget classes stay thin.
- Unchanged engine.py and data.py — the v1 calculation layer was correct.
  Migration risk was entirely in the presentation layer.

---

## VI. FUNCTIONAL SCOPE

**Core Capabilities:**
- Calculate full Vedic sidereal sky state from pyswisseph (60s cadence).
- Display real-time astronomical data across up to 9 independent display windows.
- Assign any of 38 widget types to any display from a central control panel.
- Render visual widgets using QPainter (moon disc, zodiac wheel, ring charts,
  gauges) without the constraint of terminal grid alignment.

**Supporting Capabilities:**
- Column count configuration per display (2, 3, or 4).
- Bare mode for single-widget full-screen display fills.
- Graceful null-state handling across all widgets.
- Atomic state file writes (no partial reads possible).

**Explicit Exclusions:**
- Tower integration (explicitly deferred).
- Location-aware sunrise/sunset (fixed 06:00 offset; extensibility note logged).
- Notification or alert system.
- Historical data or chart comparison.
- Network access of any kind.

---

## VII. CONSTRAINTS & CONTEXT

**Technical Constraints:**
- Python 3.11+, PyQt6, pyswisseph — all required.
- Lahiri ayanamsha exclusively. No tropical mode.
- xclip clipboard (X11). KDE Plasma 6.
- Not PyInstaller-packaged. Script-launched for internal use.

**External Dependencies:**
- pyswisseph — local install. Risk: if pyswisseph breaks, the engine emits an
  error signal and displays hold last known state.
- PyQt6 — standard installation.

---

## VIII. SUCCESS CRITERIA

**Functional Success:** Control panel launches, calculates sky state within 5
seconds, and writes a valid state.json. At least one display window opens,
reads state.json, and renders assigned widgets within 2 seconds of state write.

**User Success:** The Wizard can launch the control panel, assign widgets to a
display in under 30 seconds, and see live astronomical data on screen without
any configuration beyond the initial pip install.

**Quality Benchmarks:** Engine error does not crash display. Missing state file
shows placeholder, not exception. Widget paintEvent exception draws ⚠ rather
than crashing.

**Failure Conditions:** The application has failed if the engine runs but
displays show incorrect data (wrong ayanamsha, wrong sign for current date),
or if a display window crashes on receiving a valid state dict.

---

## IX. GLOSSARY

| Term | Definition in this application |
|------|-------------------------------|
| Sidereal | Zodiac measured against fixed stars. Lahiri ayanamsha. Not tropical. |
| Nakshatra | One of 27 lunar mansions. 13.3° each. Moon traverses one per ~day. |
| Tithi | Lunar day. 30 per synodic month. Current tithi determines panchang quality. |
| Panchang | Five-element Vedic almanac: Tithi, Vara, Nakshatra, Yoga, Karana. |
| Vara | Day of the week as understood in Vedic astrology, with ruling planet. |
| Yoga | One of 27 luni-solar combinations. Calculated from Sun + Moon longitude. |
| Karana | Half a Tithi. Finer-grained daily division. |
| Rahu Kalam | Inauspicious daily time window. Different each day of the week. |
| ArcaneCard | Base class for all Vigilarum widget types. |
| TextCard | ArcaneCard subclass that manages QLabel children for text display. |
| VisualCard | ArcaneCard subclass that delegates drawing to a painters.py function. |
| state.json | Shared JSON file. Written by control panel, read by display windows. |

---

## X. REVISION NOTES

| Date | Change | Reason |
|------|--------|--------|
| MMXXVI March 29 | v2 — full PyQt6 migration from Textual TUI | Terminal rendering limitations broke visual widgets; emoji widths unreliable; QPainter removes all constraints |

---

*Expositio · Vigilarum Omnia v2 · MMXXVI*
*Ordo Discordia, Cosmos Inania*
