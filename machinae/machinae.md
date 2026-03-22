# MACHINAE
## Arca Cognitorium — Background Variable Engines

Five standalone Python engines that feed live astronomical, atmospheric, circadian, and physical data into the tower. 
Each follows the same pattern: instantiate once, call `update()` on a timer, read properties, poll triggers.

All engines write state to `~/ArcaCognitorium/.arca/` and run standalone for testing.

---

## Installation

```bash
pip install pyswisseph   # required by machina_horologica and machina_tidalis
# no other dependencies — network engines use stdlib urllib
```

---

## Directory

```
~/ArcaCognitorium/machinae/
    __init__.py
    machina_horologica.py
    machina_circadiana.py
    machina_solaris.py
    machina_tidalis.py
    machina_meteorologica.py
```

## Import

```python
from machinae.machina_horologica    import MachinaHorologica
from machinae.machina_circadiana    import MachinaCircadiana
from machinae.machina_solaris       import MachinaSolaris
from machinae.machina_tidalis       import MachinaTidalis
from machinae.machina_meteorologica import MachinaMeteorologica
```

---

## Shared Pattern

Every machina works the same way:

```python
engine = MachinaHorologica()
engine.update()          # run calculations / fetch data
engine.triggers.poll()   # returns list of edge events since last call, then clears
engine.to_json()         # full serialised state
engine.write()           # atomic write to ~/ArcaCognitorium/.arca/<name>.json
engine.summary()         # one-line human-readable string
```

Standalone modes available on every engine:

```bash
python3 machina_horologica.py            # daemon — writes state file continuously
python3 machina_horologica.py --watch    # live terminal readout
python3 machina_horologica.py --once     # single calculation, print JSON, exit
```

---

## MACHINA HOROLOGICA
**Astronomical / Celestial**  
Network: none — Swiss Ephemeris only  
Update cadence: heavy recalc every 60s, clock every 1s  
State file: `~/ArcaCognitorium/.arca/machina_horologica.json`

```python
sky = MachinaHorologica()
sky.update()

# Time
sky.time.utc                    # "14:32:07"
sky.time.roman_date             # "XVII · III · MMXXVI"
sky.time.jd                     # Julian Day float

# Moon
sky.moon.phase_name             # "Waxing Gibbous"
sky.moon.phase_glyph            # "🌔"
sky.moon.illumination           # 73.4  (percent)
sky.moon.elongation             # 135.2  (degrees from Sun)
sky.moon.cycle_day              # 11  (day of 29.5-day cycle)
sky.moon.sign_name              # "Cancer"
sky.moon.nakshatra_name         # "Pushya"
sky.moon.nakshatra_ruler        # "Saturn"
sky.moon.named_moon             # "Harvest Moon" (set near full moon only)
sky.moon.distance_km            # 378000
sky.moon.distance_label         # "Supermoon" / "Micromoon" / "Average"
sky.moon.days_to_full           # int
sky.moon.days_to_new            # int
sky.moon.is_waxing              # bool
sky.moon.is_full                # bool
sky.moon.is_new                 # bool

# Sun
sky.sun.sign_name               # "Scorpio"
sky.sun.sign_glyph              # "♏"
sky.sun.degree                  # 14.7
sky.sun.nakshatra_name          # "Anuradha"
sky.sun.nakshatra_ruler         # "Saturn"

# Nodes
sky.nodes.rahu_sign_name        # "Pisces"
sky.nodes.ketu_sign_name        # "Virgo"
sky.nodes.eclipse_status        # "clear" / "approaching" / "season" / "peak"
sky.nodes.eclipse_dist          # 22.4  (degrees from nearest node)
sky.nodes.eclipse_active        # bool  (Sun within 18° of node)

# Season
sky.season.name                 # "Autumn"
sky.season.palette_key          # "autumn"
sky.season.saturation           # 0.68  (lunar-modulated, 0.4–1.0)
sky.season.days_until           # 34
sky.season.progress             # 0.62  (0.0 = just entered, 1.0 = about to leave)

# Panchang
sky.panchang.tithi_name         # "Ekadashi"
sky.panchang.tithi_quality      # "Nanda" / "Bhadra" / "Jaya" / "Rikta" / "Purna"
sky.panchang.paksha             # "Shukla" (waxing) or "Krishna" (waning)
sky.panchang.yoga_name          # "Siddhi"
sky.panchang.yoga_quality       # "Auspicious" / "Inauspicious"
sky.panchang.karana_name        # "Balava"
sky.panchang.vara_name          # "Guruvara"
sky.panchang.day_ruler          # "Jupiter"
sky.panchang.ph_planet          # "Venus"  (current planetary hour)
sky.panchang.rahu_kalam_start   # "13:30"
sky.panchang.rahu_kalam_end     # "15:00"
sky.panchang.rahu_kalam_active  # bool

# Derived conditions
sky.conditions.potency          # 0.0–1.0 composite celestial intensity
sky.conditions.auspicious       # bool
sky.conditions.mercury_rx       # bool
sky.conditions.retrograde_list  # ["Mercury", "Saturn"]
sky.conditions.retrograde_count # int
sky.conditions.seasonal_palette # "autumn"
sky.conditions.lunar_saturation # 0.68
sky.conditions.eclipse_active   # bool
sky.conditions.named_moon_active# bool

# Entity affinities — based on current sky vs entity sign preferences
sky.entities.get("archivist")   # float  1.0 = neutral, >1.0 = amplified
sky.entities.all()              # dict of all entity scores

# Planets
sky.planets["Mercury"].sign_name    # "Scorpio"
sky.planets["Mercury"].retrograde   # bool
sky.planets["Mercury"].phase_name   # "Morning Star" / "Evening Star" (inner only)
sky.planets["Jupiter"].sign_name    # "Gemini"
sky.planets["Saturn"].retrograde    # bool

# Triggers
sky.triggers.poll()
```

**Trigger events:**
`full_moon` · `new_moon` · `supermoon` · `named_moon:<name>` · `mercury_retrograde_began` · `venus_retrograde_began` · `mars_retrograde_began` · `eclipse_season_entered` · `eclipse_peak` · `solar_ingress:<sign>` · `lunar_ingress:<sign>` · `season_entered:<season>` · `rahu_kalam_began` · `planetary_hour:<planet>` · `inauspicious_window`

---

## MACHINA CIRCADIANA
**Entity Circadian Rhythms**  
Network: none — pure math  
Update cadence: every 60s  
State file: `~/ArcaCognitorium/.arca/machina_circadiana.json`

Each Council entity has a unique rhythm curve modelled as summed Gaussian peaks. Position runs 0.0 (trough) to 1.0 (peak). `entity_weight()` returns a 0.5–1.5 multiplier ready for the entity compiler.

| Entity | Peak Hours | Character |
|---|---|---|
| Archivist | 22:00–02:00 | Nocturnal scholar |
| Assessor | 06:00, 18:00 | Dawn and dusk — liminal hours |
| Contrarian | 14:00–15:00 | Counter-rhythmic — peaks when others trough |
| Luminarious | 11:00–15:00 | Solar — follows the sun |
| Minimalist | 07:00–10:00 | Flat, consistent — gentle morning preference |
| Pessimist | 15:00–17:00, 03:00 | Afternoon dread and dark night |
| Socratic | 08:00, 01:00 | Morning inquiry and late night recursion |
| Speculator | 00:00, 13:30 | Narrow midnight spike and early afternoon flash |
| Systems Thinker | 09:00–16:00 | Long sustained working-day peak |
| Toolsmith | 08:00–13:00 | Morning build hours |

```python
circ = MachinaCircadiana(utc_offset_hours=-8)  # your local UTC offset
circ.update()

# Per-entity rhythm
circ.entities["archivist"].position    # 0.0–1.0
circ.entities["archivist"].phase_name  # "peak" / "rising" / "stable" / "falling" / "trough"
circ.entities["archivist"].peak        # bool
circ.entities["archivist"].trough      # bool
circ.entities["archivist"].rising      # bool
circ.entities["archivist"].falling     # bool
circ.entities["archivist"].position_1h # predicted position one hour from now

# Entity compiler multiplier
circ.entity_weight("archivist")        # 0.5–1.5  (maps position to multiplier)

# Human baseline
circ.human.alertness                   # 0.0–1.0
circ.human.phase_name                  # "sleep" / "rising" / "alert" / "trough" / "evening"
circ.human.sleep_likely                # bool

# Council-wide conditions
circ.conditions.most_active            # entity name at highest position right now
circ.conditions.least_active           # entity name at lowest position right now
circ.conditions.peaks_active           # list of entities currently at peak
circ.conditions.troughs_active         # list of entities currently at trough
circ.conditions.average_position       # float — mean across all entities
circ.conditions.council_coherence      # 0.0–1.0 (1.0 = all in sync, 0.0 = divergent)

# Triggers
circ.triggers.poll()
```

**Trigger events:**
`<entity>_peak_entered` · `<entity>_trough_entered` · `<entity>_rising` · `human_sleep_window`

---

## MACHINA SOLARIS
**Solar & Geomagnetic Activity**  
Network: NOAA free APIs — no key required  
Update cadence: every 5 minutes  
State file: `~/.arca/machina_solaris.json`  
Cache file: `~/.arca/solar_cache.json`

Data sources: Kp index, solar wind speed/density/Bz field, active space weather alerts.

```bash
python3 machina_solaris.py --offline   # use cached data, no network
```

```python
sol = MachinaSolaris()
sol.update()

# Kp index — geomagnetic activity 0–9
sol.kp.current              # float  e.g. 3.67
sol.kp.level                # "quiet" / "unsettled" / "storm_minor" /
                            # "storm_moderate" / "storm_strong" /
                            # "storm_severe" / "storm_extreme"
sol.kp.storm_active         # bool  (Kp ≥ 5)
sol.kp.storm_level          # int 0–5  (0 = none, 1 = G1 ... 5 = G5)
sol.kp.description          # human-readable string

# Solar wind — measured at L1 point (~1.5M km from Earth)
sol.wind.speed_kms          # float  baseline ~400, elevated >600, extreme >800
sol.wind.density            # float  protons/cm³
sol.wind.bz                 # float  southward field component nT
sol.wind.bz_negative        # bool   True = southward = more geoeffective
sol.wind.pressure           # float  dynamic pressure nPa

# Active alerts
sol.alerts.storm_alerts     # list of active geomagnetic storm alert dicts
sol.alerts.flare_alerts     # list of active solar flare alert dicts
sol.alerts.alert_count      # int

# Derived conditions
sol.conditions.potency      # 0.0–1.0
sol.conditions.disruptive   # bool  (storm active or wind > 700 km/s)
sol.conditions.quiet        # bool  (Kp < 2 and wind < 450 km/s)
sol.conditions.flare_recent # bool
sol.conditions.description  # human-readable string

sol.online                  # bool — last fetch succeeded

# Triggers
sol.triggers.poll()
```

**Kp levels:** G1 minor (≥5) · G2 moderate (≥6) · G3 strong (≥7) · G4 severe (≥8) · G5 extreme (9)

**Trigger events:**
`geomagnetic_storm_began` · `extreme_storm_event` · `solar_disruption_active` · `solar_conditions_quiet` · `solar_flare_detected`

---

## MACHINA TIDALIS
**Gravitational Tidal Forces**  
Network: none — Swiss Ephemeris only  
Update cadence: every 5 minutes  
State file: `~/.arca/machina_tidalis.json`

Real gravitational tidal force calculations for Moon, Sun, Mars, Jupiter, and Saturn. Force values normalised to 1.0 = average Moon tidal force. Location is required for directional calculations.

```python
tidal = MachinaTidalis(lat=48.4, lon=-123.3)
tidal.update()

# Moon
tidal.moon.force_relative   # float  1.0 = average. ~1.1 near perigee.
tidal.moon.direction        # "overhead" / "high" / "rising" /
                            # "setting" / "below_horizon" / "underfoot"
tidal.moon.dist_km          # int  e.g. 378000

# Sun
tidal.sun.force_relative    # float  ~0.46 (Sun's tidal force ~46% of average Moon)
tidal.sun.direction

# Combined Moon + Sun
tidal.combined.force        # float  Moon + Sun combined
tidal.combined.moon_sun_angle  # float  degrees
tidal.combined.spring_tide  # bool  Moon/Sun aligned (new/full moon) — amplified
tidal.combined.neap_tide    # bool  Moon/Sun at 90° (quarter moons) — dampened

# Planets (small but real)
tidal.planets["Jupiter"].force_relative
tidal.planets["Saturn"].force_relative
tidal.planets["Mars"].force_relative

# Derived conditions
tidal.conditions.potency    # 0.0–1.0
tidal.conditions.peak_tidal # bool  combined > 1.5x average
tidal.conditions.spring_tide
tidal.conditions.neap_tide
tidal.conditions.moon_close # bool  Moon at perigee (>15% stronger than avg)
tidal.conditions.description

# Triggers
tidal.triggers.poll()
```

**Typical combined force values:**
Average: ~1.46 · Spring tide: ~1.4–1.6 · Spring + perigee: ~1.7–2.0 · Neap tide: ~0.6–0.8

**Trigger events:**
`spring_tide_began` · `neap_tide_began` · `peak_tidal_force` · `moon_at_perigee`

---

## MACHINA METEOROLOGICA
**Local Weather**  
Network: Open-Meteo — free, no API key  
Update cadence: every 15 minutes  
State file: `~/ArcaCognitorium/.arca/machina_meteorologica.json`  
Cache file: `~/ArcaCognitorium/.arca/weather_cache.json`

```bash
python3 machina_meteorologica.py --lat 48.4 --lon -123.3 --watch
python3 machina_meteorologica.py --lat 48.4 --lon -123.3 --offline
```

```python
wx = MachinaMeteorologica(lat=48.4, lon=-123.3)
wx.update()

# Current conditions
wx.current.temp_c           # float
wx.current.feels_like_c     # float
wx.current.humidity         # int  percent
wx.current.description      # "Clear sky" / "Moderate rain" / "Thunderstorm" etc
wx.current.pressure_hpa     # float  e.g. 1013.2
wx.current.pressure_trend   # "rising" / "falling" / "stable"
wx.current.wind_kph         # float
wx.current.wind_direction   # int  degrees
wx.current.cloud_cover      # int  percent
wx.current.uv_index         # float
wx.current.precipitation    # float  mm
wx.current.is_day           # bool
wx.current.is_raining       # bool
wx.current.is_snowing       # bool
wx.current.is_stormy        # bool
wx.current.is_clear         # bool

# Derived conditions
wx.conditions.potency       # 0.0–1.0  atmospheric intensity
wx.conditions.stormy        # bool
wx.conditions.pressure_drop # bool  falling pressure
wx.conditions.oppressive    # bool  hot + humid (temp > 28°C and humidity > 70%)
wx.conditions.serene        # bool  clear, mild, calm, no rain
wx.conditions.description

wx.online                   # bool

# Triggers
wx.triggers.poll()
```

**Trigger events:**
`rain_began` · `storm_began` · `snow_began` · `sky_cleared` · `pressure_dropping` · `oppressive_conditions` · `serene_conditions`

---

## USING THE MACHINAE IN THE ARCA

All five together in the main loop:

```python
from machinae.machina_horologica    import MachinaHorologica
from machinae.machina_circadiana    import MachinaCircadiana
from machinae.machina_solaris       import MachinaSolaris
from machinae.machina_tidalis       import MachinaTidalis
from machinae.machina_meteorologica import MachinaMeteorologica

# Instantiate once at startup
sky   = MachinaHorologica()
circ  = MachinaCircadiana(utc_offset_hours=-8)
sol   = MachinaSolaris()
tidal = MachinaTidalis(lat=48.4, lon=-123.3)
wx    = MachinaMeteorologica(lat=48.4, lon=-123.3)

# In main loop — call every second
# Each engine internally rate-limits its heavy work
sky.update()
circ.update()
sol.update()
tidal.update()
wx.update()

# Entity weight for compiler
def get_entity_weight(name: str) -> float:
    return round(
        sky.entities.get(name)    * 0.40 +  # astronomical affinity
        circ.entity_weight(name)  * 0.40 +  # circadian position
        (1.0 - sol.conditions.potency * 0.1) * 0.10 +  # solar dampening
        (1.0 + (tidal.combined.force - 1.0) * 0.05) * 0.10,  # tidal boost
    4)

# Ceremony trigger watching
for event in sky.triggers.poll():
    handle_celestial_event(event)
for event in sol.triggers.poll():
    handle_solar_event(event)
```

---

## NOTES

**Vedic / Sidereal** — MachinaHorologica and MachinaTidalis use Lahiri Ayanamsha. Sign positions differ from Western tropical astrology by ~23–24°.

**Timezone** — MachinaCircadiana accepts `utc_offset_hours` for accurate circadian curves. Victoria BC = `-8` (PST) or `-7` (PDT).

**Location** — MachinaTidalis and MachinaMeteorologica require `lat` and `lon`. Victoria BC = `lat=48.4, lon=-123.3`.

**Offline resilience** — MachinaSolaris and MachinaMeteorologica cache their last successful fetch to disk. They serve cached data when offline. MachinaHorologica and MachinaTidalis never need a network connection.

**Schumann Resonance** — intentionally absent. No reliable programmatic real-time feed exists at time of writing. Architecture is open for it when one becomes available.
