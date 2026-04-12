# SYSTEMS CHECK — CELESTIAL CHAIN

### CAELESTIS · MUNDANA STATE BUS · CELESTIAL RESOLVER

*Tower Infrastructure · Arca Cognitorium · MMXXVI*

---

## Summary

Three components built in Tier III as a unified chain. CAELESTIS is the
astrological Machina — it reads live data from MachinaHorologica and
calculates planetary positions, aspects, dignities, and Vimshottari dasha
via pyswisseph with Lahiri ayanamsha. The Mundana State Bus aggregates all
seven Machinae into a unified publish-subscribe data bus with two output
tracks: cosmetic/UI and entity behaviour. The Celestial Resolver translates
raw bus variables into per-entity CelestialContext via `celestial.yaml` config
files, one per Council entity. All 10 entities are profiled. The final wire —
injecting Resolver output into Tower entity system prompt assembly — is not
yet connected.

---

## CAELESTIS

### Summary

Astrological Machina. Follows the same interface as all other Machinae
(`update()`, `triggers.poll()`, `to_json()`, `write()`, `summary()`).
Reads from live MachinaHorologica — does not recalculate positions
independently. Writes to `~/.arca/caelestis.json`. Lahiri ayanamsha,
Vedic/sidereal exclusively.

Calculates: planetary positions (sign, degree, nakshatra), active aspects,
dignity states, composite astrological potency signal, Vimshottari dasha
(current period and sub-period), Mercury retrograde state, lunar phase,
lunar nakshatra, solar ingress flags.

### Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Machinae interface               │  update(), triggers.poll(), to_json(),     │
│                                   │  write(), summary()                        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Planetary positions              │  Sign, degree, nakshatra. Lahiri.          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Aspects                          │  Active major and minor aspects            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Dignity states                   │  Exaltation, debilitation, own sign,       │
│                                   │  enemy sign                                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Potency signal                   │  Composite astrological intensity score    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Vimshottari dasha                │  Current major and sub-period              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Named events                     │  Mercury retrograde state, lunar phase,    │
│                                   │  nakshatra, solar ingress flags            │
╰───────────────────────────────────┴────────────────────────────────────────────╯

### I/O

╭──────────────┬─────────────────────────────────────────────────────────╮
│  Reads       │  MachinaHorologica (live) for planetary positions       │
│              │  pyswisseph ephemeris                                   │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Writes      │  ~/.arca/caelestis.json (current state)                 │
├──────────────┼─────────────────────────────────────────────────────────┤
│  Depends on  │  pyswisseph (local install)                             │
│              │  MachinaHorologica (must be running)                    │
╰──────────────┴─────────────────────────────────────────────────────────╯

---

## MUNDANA STATE BUS

### Summary

Aggregation layer for all seven Machinae. A `MundanaStateBus` class with
publish-subscribe architecture. All Machinae publish their variables; all
entity behavioural systems subscribe to what they need. Two output tracks:
cosmetic/UI effects and entity behavioural influence. In-memory — does not
persist between sessions. Machinae re-publish on startup. CLI: `--lat`,
`--lon`, `--utc` flags. Defaults to Victoria BC.

### Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  publish(source, key, value)      │  Machina writes a reading to the bus       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  get(key)                         │  Consumer reads current value              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  subscribe(key, callback)         │  Consumer registers for updates            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  snapshot()                       │  Full current state as dict (for context   │
│                                   │  injection into entity prompts)            │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  All 7 Machinae wired             │  CAELESTIS, CIRCADIANA, HOROLOGICA,        │
│                                   │  METEOROLOGICA, SOLARIS, TIDALIS, LAPSUS   │
│  Two output tracks                │  Cosmetic/UI + entity behavioural influence│
╰───────────────────────────────────┴────────────────────────────────────────────╯

---

## CELESTIAL RESOLVER

### Summary

Translates raw Machinae variables from the State Bus into per-entity
CelestialContext using `celestial.yaml` config files (one per entity in
`storage/entities/{id}/celestial.yaml`). Output is a dict of named influence
keys with float values between -1.0 and 1.0. PyYAML soft dependency — fallback
parser included. celestial.yaml hot-reload supported. All 10 Council entities
profiled via `deploy_celestial_yamls.py`.

Output example:

```python
{
  "cognitive_clarity":    0.6,
  "emotional_intensity": -0.3,
  "creative_volatility":  0.8,
  "institutional_gravity": 0.2
}
```

### Feature List

╭───────────────────────────────────┬────────────────────────────────────────────╮
│  Feature                          │  Notes                                     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Per-entity CelestialContext      │  celestial.yaml per entity.                │
│                                   │  Affinities, resistances, vulnerabilities, │
│                                   │  special alignment conditions              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Named influence keys             │  Float -1.0 to 1.0. Entities consume       │
│                                   │  these — not raw astro variables.          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  celestial.yaml hot-reload        │  Changes to YAML apply without restart     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  PyYAML soft dependency           │  Fallback parser if PyYAML absent          │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  All 10 entities profiled         │  deploy_celestial_yamls.py splits and      │
│                                   │  installs all entity yamls                 │
╰───────────────────────────────────┴────────────────────────────────────────────╯

---

## Launch & Verification

```bash
# Run the State Bus with all Machinae
# (assuming Machinae run from Tower directory)
cd ~/ArcaCognitorium
python -m Tower.machinae.mundana_state_bus --lat 48.43 --lon -123.37

# Verify CAELESTIS is publishing to the bus
# Run a simple subscriber that logs everything
python -c "
from Tower.machinae.mundana_state_bus import MundanaStateBus
bus = MundanaStateBus()
bus.subscribe('*', lambda k, v: print(f'{k}: {v}'))
import time; time.sleep(10)
"

# Verify celestial.yaml files exist for all entities
ls ~/ArcaCognitorium/storage/entities/*/celestial.yaml

# Deploy if missing
python deploy_celestial_yamls.py

# Test Resolver output for one entity
python -c "
from Tower.machinae.celestial_resolver import CelestialResolver
resolver = CelestialResolver(bus, entity_id='luminarious')
ctx = resolver.get_context()
print(ctx)
"
```

Verification steps:

1. State Bus starts — all 7 Machinae begin publishing
2. CAELESTIS writes `~/.arca/caelestis.json` within one cycle
3. caelestis.json contains planetary positions in sidereal (Lahiri)
4. `celestial.yaml` exists for all 10 Council entities
5. Resolver returns a dict with named float values for an entity

Checklist:

- pyswisseph import succeeds
- All 7 Machinae publish to bus without error
- CAELESTIS reads from MachinaHorologica (not recalculating)
- caelestis.json positions match known ephemeris for test date
- celestial.yaml present for: luminarious, the_assessor, the_archivist,
  the_contrarian, the_speculator, the_minimalist, the_pessimist,
  the_toolsmith, the_systems_thinker, the_socratic
- Resolver output values fall between -1.0 and 1.0
- celestial.yaml hot-reload works after a file edit

---

## Open Items

The most consequential open item: the Resolver output is not yet wired into
Tower entity system prompt assembly. The chain exists end-to-end but the final
connection into the entity layer is not made. This is Step 19 in the Cohesion
Respec sequence.

The Socratic entity's interruption/dismissal logic also needs a fix — separate
Tower session.

---

## Claude.ai Collaboration Prompt

```
You are assisting with the CELESTIAL CHAIN — CAELESTIS, the Mundana State
Bus, and the Celestial Resolver — in the Arca Cognitorium Tower.
Python 3.11, pyswisseph, Lahiri ayanamsha exclusively.

Architecture:
- CAELESTIS: follows Machinae interface (update, triggers.poll, to_json,
  write, summary). Reads from MachinaHorologica — does not recalculate.
  Writes to ~/.arca/caelestis.json.
- Mundana State Bus: publish-subscribe. MundanaStateBus class.
  publish(source, key, value) / get(key) / subscribe(key, callback) /
  snapshot() → dict. In-memory only — Machinae republish on startup.
  All 7 Machinae: CAELESTIS, CIRCADIANA, HOROLOGICA, METEOROLOGICA,
  SOLARIS, TIDALIS, LAPSUS.
- Celestial Resolver: reads bus via snapshot(), loads celestial.yaml per
  entity from storage/entities/{entity_id}/celestial.yaml, produces named
  influence dict with float values -1.0 to 1.0.
  PyYAML soft dep — fallback parser included. Hot-reload supported.
- All 10 Council entities have celestial.yaml files.
  deploy_celestial_yamls.py installs them.
- The entity behavioural influence wire (Resolver → system prompt
  assembler) is NOT yet built. That is the current gap.
- Do not touch existing Machinae code unless calculation is demonstrably wrong.
- Sidereal only. No tropical. No tropocal fallback.

Current session focus: [DESCRIBE TASK]
```

---

## Completion Stamp

```
╔═════════════════════════════════════════════════════════════════════════╗
║◤                                                                      ◥ ║
║                                                                         ║
║    ＣＥＬＥＳＴＩＡＬ ＣＨＡＩＮ — ＳＹＳＴＥＭＳ ＣＨＥＣＫ                 ║
║                                                                         ║
║◣                                                                      ◢ ║
╠═════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║    Systems      ·  CAELESTIS · Mundana State Bus · Celestial Resolver  ║
║    Version      ·  1.0                                                  ║
║    Checked      ·  [DATE]                                               ║
║    Verified by  ·  [SESSION]                                            ║
║    Status       ·  ✦ VERIFIED                                           ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

---

*Ordo Discordia, Cosmos Inania*
