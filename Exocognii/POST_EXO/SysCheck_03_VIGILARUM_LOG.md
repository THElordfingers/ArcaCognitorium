╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＶＩＧＩＬＡＲＵＭ ＯＭＮＩＡ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ            ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Application  ·  Vigilarum Omnia                                      ║
║    Version      ·  2.0                                                  ║
║    Started      ·  04-01-2026                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
╔═════════════════════╗
║ Verification steps: ║
╚═════════════════════╝

☐  1. Control panel opens — engine status shows calculating


☐  2. `~/.vigilarum/state.json` appears within 60 seconds


☐  3. Open a display window — widgets render without exception


☐  4. Wait 60 seconds — state.json timestamp updates


☐  5. Reassign widget types in control panel — display reflects change






═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Checklist: ║
╚════════════╝


☐  pyswisseph import succeeds — no swisseph error on launch


☐  state.json exists and is valid JSON within first engine cycle


☐  Display window renders at least one widget without ⚠ error card


☐  Engine error does not crash display (last known state persists)


☐  Missing state.json shows placeholder widgets, not an exception


☐  Moon disc, zodiac wheel, nakshatra ring render without crash







═════════════════════════════════════════════════════════════════════════
╔════════════╗
║ Open Items ║
╚════════════╝

Sunrise assumption fixed at 06:00 — location-aware `swe.rise_trans()`
deferred to named session.

Moon disc terminator softness at first/last quarter is a QPainter geometry
constraint — not a bug, logged for awareness.
