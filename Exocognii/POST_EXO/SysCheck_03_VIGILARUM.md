# SYSTEMS CHECK — VIGILARUM OMNIA v2

*Arca Cognitorium · Exocognii Suite · MMXXVI*

---

## Summary

Vedic sidereal celestial display instrument. A background engine thread
calculates the full sky state every 60 seconds via pyswisseph and writes
atomically to state.json. Up to 9 independent display windows each render
a composition of up to 38 widget types assigned from a central control panel.
QPainter visual rendering replaces all Textual terminal constraints. Standalone
— no Tower coupling, no API calls, no network.

---

## Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  EngineWorker (QThread)           │  pyswisseph calculations every 60 seconds. │
│                                   │  Emits finished/error signals. Never       │
│                                   │  blocks main thread.                       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  state.json IPC                   │  Atomic write (tmp → replace). Display     │
│                                   │  windows poll every second. Clock fields   │
│                                   │  update every second without engine recalc.│
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  38 widget types                  │  TextCard (QLabel children) and VisualCard │
│                                   │  (painters.py delegation) subclasses of    │
│                                   │  ArcaneCard base                           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  painters.py                      │  Pure functions: (QPainter, QRectF, data)  │
│                                   │  → None. No widget refs, no side effects.  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Visual widgets                   │  Moon disc, zodiac wheel, nakshatra ring,  │
│                                   │  tithi dial, eclipse gauge, planet strip,  │
│                                   │  moon arc — all QPainter                   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Up to 9 display windows          │  Each independently assigned from control  │
│                                   │  panel. Column count: 2, 3, or 4.          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Graceful failure                 │  Engine error → last known state persists. │
│                                   │  Missing state.json → placeholder widgets. │
│                                   │  paintEvent exception → ⚠ card, not crash. │
╰───────────────────────────────────┴────────────────────────────────────────────╯

Lahiri ayanamsha exclusively. No tropical mode.

---

## I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  pyswisseph ephemeris (engine.py via swisseph lib)      │
│              │  ~/.vigilarum/state.json (display windows poll)         │
│              │  ~/.vigilarum/config.json (display widget assignments)  │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  ~/.vigilarum/state.json (engine, atomic)               │
│              │  ~/.vigilarum/config.json (control panel saves assigns) │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  pyswisseph (local install), PyQt6                      │
│              │  No ClaudeBox, no API calls, no network                 │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## Launch & Verification

```bash
# Control panel
cd ~/ArcaCognitorium/Exocognii/Vigilarum && python control.py

# Display window (separate process)
python display.py
```

Verification steps:

1. Control panel opens — engine status shows calculating
2. `~/.vigilarum/state.json` appears within 60 seconds
3. Open a display window — widgets render without exception
4. Wait 60 seconds — state.json timestamp updates
5. Reassign widget types in control panel — display reflects change

Checklist:

- pyswisseph import succeeds — no swisseph error on launch
- state.json exists and is valid JSON within first engine cycle
- Display window renders at least one widget without ⚠ error card
- Engine error does not crash display (last known state persists)
- Missing state.json shows placeholder widgets, not an exception
- Moon disc, zodiac wheel, nakshatra ring render without crash

---

## Open Items

Sunrise assumption fixed at 06:00 — location-aware `swe.rise_trans()`
deferred to named session.

Moon disc terminator softness at first/last quarter is a QPainter geometry
constraint — not a bug, logged for awareness.

---

## Claude.ai Collaboration Prompt

```
You are assisting with VIGILARUM OMNIA v2 — a celestial display instrument
in the Arca Cognitorium suite. PyQt6, Python 3.11, Debian Trixie.
Standalone — no Tower integration, no ClaudeBox, no network.

Architecture:
- EngineWorker (QThread) calculates every 60 seconds via pyswisseph,
  Lahiri ayanamsha exclusively. No tropical mode.
- state.json at ~/.vigilarum/ is the IPC wire. Atomic write.
  Display windows poll every 1 second.
- ArcaneCard base → TextCard (QLabel children) or VisualCard
  (painters.py delegation)
- painters.py: pure functions (QPainter, QRectF, data) → None
  No widget references. No side effects. Independently testable.
- engine.py and data.py are stable — do not touch unless the
  calculation is demonstrably wrong
- Graceful failure: engine error emits signal, display holds last
  known state. Missing state.json → placeholder, not exception.

Chromata Arcana aesthetic: near-black void, gold accent, Georgia serif.

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＶＩＧＩＬＡＲＵＭ ＯＭＮＩＡ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ              ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  Vigilarum Omnia v2                                   ║
║    Version      ·  2.0                                                  ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
