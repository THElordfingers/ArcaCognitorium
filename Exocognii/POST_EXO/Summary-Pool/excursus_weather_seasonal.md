# ::EXCURSUS — Weather & Seasonal Variables
*Flagged: 2026-03-29 · Vigilarum v2 Migration Session*

---

## Idea

Add local weather data and expanded seasonal variables as inputs to both
the Vigilarum widget set and the Machinae Caelestiae — specifically
METEOROLOGICA and CIRCADIANA.

---

## Vigilarum Scope

New widget types surfacing live weather alongside the existing celestial data:

- Current conditions (temperature, sky state, wind)
- Daylight hours (sunrise/sunset — which also resolves the planetary hour
  and Rahu Kalam fixed-offset problem flagged in the v2 review)
- UV index / solar intensity
- Moon-visible conditions (cloud cover, visibility)
- A combined seasonal context card — season + weather + daylight as one widget

Weather source: local API (wttr.in or OpenWeatherMap) or system weather
service. Pulled on the same 60-second engine tick. Failure degrades
gracefully — widget shows last known or placeholder, no crash.

---

## Machinae Caelestiae Scope

METEOROLOGICA is already named in the Machinae family and awaits wirification.
Weather data is the natural input feed for it.

CIRCADIANA already tracks circadian rhythms — actual local sunrise/sunset
from `swe.rise_trans()` (with lat/lon from `~/.arca/config.json`) would
make its output genuinely location-aware rather than fixed-offset.

Relevant Machinae:

- **METEOROLOGICA** — weather variables as behavioural influence inputs
- **CIRCADIANA** — replace fixed 06:00 sunrise with `swe.rise_trans()` output
- **SOLARIS** — UV / solar activity data as additional variable layer

---

## Dependencies Before Action

- `~/.arca/config.json` needs `lat` and `lon` keys (Victoria, BC)
- CAELESTIS must be built first — it is the celestial variable bus
  that METEOROLOGICA feeds into
- Vigilarum weather widgets can be built independently of the Machinae
  integration and are not blocked

---

## Carry Forward To

Tier 3 — CAELESTIS build session.
Vigilarum weather widgets can be a standalone Tier 6 addendum session
before or after Tier 3.

---

*Ordo Discordia, Cosmos Inania*
