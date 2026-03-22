#!/usr/bin/env python3
"""
MACHINA TIDALIS
════════════════════════════════════════════════════════════════════════════════
Arca Cognitorium — Gravitational Tidal Force Engine

Calculates real gravitational tidal forces at your location from the Moon,
Sun, and all major planets using Swiss Ephemeris. No network required.
Pure local calculation.

The tidal force is the differential gravitational pull across a body —
the difference in gravitational acceleration between the near and far side.
For Earth: F_tidal ∝ GM / r³

While ocean tides are most familiar, land tides also exist (Earth's crust
flexes by ~30cm at full moon). These are measurable physical forces.

Usage:
    from machinae.machina_tidalis import MachinaTidalis

    tidal = MachinaTidalis(lat=51.5, lon=-0.1)    # London
    tidal.update()

    tidal.moon.force_relative   # 1.0 = average, >1 = stronger than average
    tidal.moon.direction        # "overhead" / "underfoot" / "rising" / "setting"
    tidal.sun.force_relative
    tidal.combined.force        # total tidal force (Moon + Sun combined)
    tidal.combined.syzygy       # True if Moon/Sun aligned (new/full moon)
    tidal.combined.quadrature   # True if Moon/Sun at 90° (quarter moons)
    tidal.conditions.peak_tidal # True if combined force > 1.5x average
    tidal.conditions.spring_tide # True if syzygy (amplified)
    tidal.conditions.neap_tide   # True if quadrature (dampened)
    tidal.triggers.poll()        # ["spring_tide_began", "peak_tidal", ...]

Daemon mode:
    python3 MachinaTidalis.py                      # daemon, requires --lat and --lon
    python3 MachinaTidalis.py --lat 51.5 --lon -0.1
    python3 MachinaTidalis.py --watch --lat 51.5 --lon -0.1
    python3 MachinaTidalis.py --once  --lat 51.5 --lon -0.1

Location is required for direction calculations (overhead/underfoot).
Force magnitudes are location-independent.

════════════════════════════════════════════════════════════════════════════════
"""

import swisseph as swe
import math
import json
import time
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

swe.set_sid_mode(swe.SIDM_LAHIRI)

VERSION    = "1.0.0"
ARCA_DIR   = Path.home() / ".arca"
STATE_PATH = ARCA_DIR / "machina_tidalis.json"

# Gravitational constants
G      = 6.674e-11   # m³ kg⁻¹ s⁻²
M_MOON = 7.342e22    # kg
M_SUN  = 1.989e30    # kg
M_MARS = 6.39e23
M_JUP  = 1.898e27
M_SAT  = 5.683e26
R_EARTH= 6.371e6     # m

AU_M   = 1.495978707e11  # 1 AU in metres

# Average Moon-Earth distance for normalisation
AVG_MOON_DIST_M = 384400e3

# Tidal force formula: F = 2 * G * M * R_earth / r³
# where r = distance to body, R_earth = Earth radius
# Returns in units of 10⁻⁷ m/s² (same order as known tidal acceleration)
def tidal_force(mass_kg: float, dist_m: float) -> float:
    if dist_m <= 0: return 0.0
    return 2 * G * mass_kg * R_EARTH / (dist_m ** 3)

# Normalise to 1.0 = average moon tidal force
MOON_AVG_FORCE = tidal_force(M_MOON, AVG_MOON_DIST_M)

PLANET_MASSES = {
    "Mars":    M_MARS,
    "Jupiter": M_JUP,
    "Saturn":  M_SAT,
}

# ─────────────────────────────────────────────────────────────────────────────
# DIRECTION CALCULATION
# ─────────────────────────────────────────────────────────────────────────────

def body_direction(jd: float, pid: int, lat: float, lon: float) -> str:
    """
    Returns whether the body is overhead, underfoot, rising, or setting
    relative to observer location.
    Uses simplified altitude calculation.
    """
    try:
        # Get body ecliptic position
        r = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)[0]
        body_lon_ec = r[0]
        body_lat_ec = r[1] if len(r) > 1 else 0.0

        # Get local sidereal time
        gst = swe.sidtime(jd)
        lst = (gst + lon/15.0) % 24  # local sidereal time in hours

        # Hour angle of body
        # Body's RA approximation from ecliptic lon (rough)
        ra_approx = body_lon_ec / 15.0  # very rough
        ha = (lst - ra_approx) % 24

        # Altitude rough approximation
        # altitude ≈ sin(lat)*sin(dec) + cos(lat)*cos(dec)*cos(ha*15°)
        dec_approx = body_lat_ec  # rough
        alt = (math.sin(math.radians(lat)) * math.sin(math.radians(dec_approx))
               + math.cos(math.radians(lat)) * math.cos(math.radians(dec_approx))
               * math.cos(math.radians(ha * 15)))
        altitude = math.degrees(math.asin(max(-1, min(1, alt))))

        if   altitude > 60:   return "overhead"
        elif altitude > 10:   return "high"
        elif altitude > -10:  return "rising" if ha > 12 else "setting"
        elif altitude > -60:  return "below_horizon"
        else:                 return "underfoot"
    except Exception:
        return "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# STATE OBJECTS
# ─────────────────────────────────────────────────────────────────────────────

class BodyTidal:
    """Tidal state for a single body."""
    def __init__(self, name: str):
        self.name           = name
        self.force          = 0.0   # absolute tidal acceleration m/s²
        self.force_relative = 1.0   # relative to average Moon tidal force
        self.dist_km        = 0.0
        self.dist_au        = 0.0
        self.direction      = "unknown"
        self.longitude      = 0.0

    def to_dict(self):
        return self.__dict__


class CombinedTidal:
    """Combined tidal state — Moon + Sun interaction."""
    def __init__(self):
        self.force          = 0.0   # combined relative force
        self.moon_sun_angle = 0.0   # angle between Moon and Sun (degrees)
        self.syzygy         = False # new or full moon — Moon/Sun aligned
        self.quadrature     = False # quarter moons — Moon/Sun at 90°
        self.spring_tide    = False # syzygy — amplified
        self.neap_tide      = False # quadrature — dampened

    def update(self, moon: BodyTidal, sun: BodyTidal, moon_angle: float):
        self.force          = moon.force_relative + sun.force_relative
        self.moon_sun_angle = moon_angle
        # Syzygy: Moon/Sun within 20° or 160-200° (new/full moon)
        angle = moon_angle % 360
        self.syzygy     = angle < 20 or angle > 340 or (160 < angle < 200)
        self.quadrature = 70 < angle < 110 or 250 < angle < 290
        self.spring_tide= self.syzygy
        self.neap_tide  = self.quadrature

    def to_dict(self):
        return self.__dict__


class TidalConditions:
    """Derived conditions for tower use."""
    def __init__(self):
        self.peak_tidal     = False   # combined force > 1.5x average
        self.spring_tide    = False
        self.neap_tide      = False
        self.moon_close     = False   # Moon within perigee range
        self.potency        = 0.5     # 0.0-1.0
        self.description    = ""

    def update(self, moon: BodyTidal, combined: CombinedTidal):
        self.spring_tide = combined.spring_tide
        self.neap_tide   = combined.neap_tide
        self.moon_close  = moon.force_relative > 1.15  # >15% stronger than avg
        self.peak_tidal  = combined.force > 1.5

        # Potency: normalise combined force, boost for spring tide
        base = min(1.0, combined.force / 2.5)
        self.potency = round(base, 3)

        if   self.peak_tidal and self.spring_tide:
            self.description = "Peak tidal force. Spring tide with Moon at perigee."
        elif self.spring_tide:
            self.description = "Spring tide. Moon and Sun aligned — amplified pull."
        elif self.neap_tide:
            self.description = "Neap tide. Moon and Sun at quadrature — dampened pull."
        elif self.moon_close:
            self.description = "Moon near perigee. Elevated tidal force."
        else:
            self.description = "Tidal conditions average."

    def to_dict(self):
        return self.__dict__


class TidalTriggers:
    def __init__(self):
        self._pending = []
        self._prev    = {}

    def _edge(self, key, current, label):
        if current and not self._prev.get(key, False):
            self._pending.append(label)
        self._prev[key] = current

    def update(self, conditions: TidalConditions, combined: CombinedTidal):
        self._edge("spring",  combined.spring_tide,    "spring_tide_began")
        self._edge("neap",    combined.neap_tide,      "neap_tide_began")
        self._edge("peak",    conditions.peak_tidal,   "peak_tidal_force")
        self._edge("close",   conditions.moon_close,   "moon_at_perigee")

    def poll(self) -> list:
        out = list(self._pending); self._pending.clear(); return out

    def peek(self) -> list:
        return list(self._pending)

    def to_dict(self):
        return {"pending": self._pending}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class MachinaTidalis:
    """
    Gravitational tidal force engine. No network. Pure Swiss Ephemeris.

    tidal = MachinaTidalis(lat=51.5, lon=-0.1)
    tidal.update()

    tidal.moon.force_relative       # 1.0 = average
    tidal.moon.direction            # "overhead" / "underfoot" / etc
    tidal.sun.force_relative
    tidal.combined.force            # Moon + Sun combined
    tidal.combined.spring_tide      # bool
    tidal.combined.neap_tide        # bool
    tidal.conditions.potency        # 0.0-1.0
    tidal.planets["Jupiter"].force_relative
    tidal.triggers.poll()
    """

    def __init__(self, lat: float = 0.0, lon: float = 0.0):
        self.lat  = lat
        self.lon  = lon

        self.moon       = BodyTidal("Moon")
        self.sun        = BodyTidal("Sun")
        self.planets    = {name: BodyTidal(name) for name in PLANET_MASSES}
        self.combined   = CombinedTidal()
        self.conditions = TidalConditions()
        self.triggers   = TidalTriggers()

        self._tick       = 0
        self._last_heavy = 0.0

    def update(self, force: bool = False):
        self._tick += 1
        now = datetime.now(timezone.utc)
        jd  = swe.julday(now.year, now.month, now.day,
                         now.hour + now.minute/60 + now.second/3600)

        heavy = force or (time.time() - self._last_heavy >= 300)  # every 5 min

        if heavy:
            self._last_heavy = time.time()
            self._calculate(jd)

        self.combined.update(self.moon, self.sun, self._moon_sun_angle(jd))
        self.conditions.update(self.moon, self.combined)
        self.triggers.update(self.conditions, self.combined)

    def _moon_sun_angle(self, jd: float) -> float:
        sun_lon  = swe.calc_ut(jd, swe.SUN,  swe.FLG_SIDEREAL)[0][0]
        moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
        return (moon_lon - sun_lon) % 360

    def _calculate(self, jd: float):
        # Moon
        r = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
        moon_dist_au = r[2]
        moon_dist_m  = moon_dist_au * AU_M
        moon_force   = tidal_force(M_MOON, moon_dist_m)
        self.moon.force          = moon_force
        self.moon.force_relative = round(moon_force / MOON_AVG_FORCE, 4)
        self.moon.dist_km        = round(moon_dist_m / 1000, 0)
        self.moon.dist_au        = round(moon_dist_au, 6)
        self.moon.longitude      = round(r[0], 3)
        self.moon.direction      = body_direction(jd, swe.MOON, self.lat, self.lon)

        # Sun
        r = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
        sun_dist_m  = r[2] * AU_M
        sun_force   = tidal_force(M_SUN, sun_dist_m)
        self.sun.force          = sun_force
        self.sun.force_relative = round(sun_force / MOON_AVG_FORCE, 4)
        self.sun.dist_km        = round(sun_dist_m / 1000, 0)
        self.sun.dist_au        = round(r[2], 6)
        self.sun.longitude      = round(r[0], 3)
        self.sun.direction      = body_direction(jd, swe.SUN, self.lat, self.lon)

        # Planets
        planet_ids = {
            "Mars":    swe.MARS,
            "Jupiter": swe.JUPITER,
            "Saturn":  swe.SATURN,
        }
        for name, pid in planet_ids.items():
            r = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)[0]
            dist_m = r[2] * AU_M
            force  = tidal_force(PLANET_MASSES[name], dist_m)
            p = self.planets[name]
            p.force          = force
            p.force_relative = round(force / MOON_AVG_FORCE, 6)
            p.dist_km        = round(dist_m / 1000, 0)
            p.dist_au        = round(r[2], 4)
            p.longitude      = round(r[0], 3)

    def to_dict(self) -> dict:
        return {
            "meta": {
                "ts":       datetime.now(timezone.utc).isoformat(),
                "version":  VERSION,
                "tick":     self._tick,
                "location": {"lat": self.lat, "lon": self.lon},
            },
            "moon":       self.moon.to_dict(),
            "sun":        self.sun.to_dict(),
            "planets":    {n: p.to_dict() for n, p in self.planets.items()},
            "combined":   self.combined.to_dict(),
            "conditions": self.conditions.to_dict(),
            "triggers":   self.triggers.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def write(self):
        ARCA_DIR.mkdir(exist_ok=True)
        tmp = ARCA_DIR / "machina_tidalis.tmp"
        with open(tmp, "w") as f:
            f.write(self.to_json())
        tmp.replace(STATE_PATH)

    def summary(self) -> str:
        return (f"Moon:{self.moon.force_relative:.3f}x"
                f"  dir:{self.moon.direction}"
                f"  Sun:{self.sun.force_relative:.3f}x"
                f"  combined:{self.combined.force:.3f}"
                f"  {'SPRING' if self.combined.spring_tide else 'NEAP' if self.combined.neap_tide else 'normal'}"
                f"  potency:{self.conditions.potency:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _bar(val: float, width: int = 20) -> str:
    filled = int(min(1.0, val/2) * width)
    return "█" * filled + "░" * (width - filled)

def _parse_args():
    args = sys.argv[1:]
    lat = 0.0; lon = 0.0
    if "--lat" in args:
        idx = args.index("--lat")
        try: lat = float(args[idx+1])
        except: pass
    if "--lon" in args:
        idx = args.index("--lon")
        try: lon = float(args[idx+1])
        except: pass
    return lat, lon

def run_daemon(lat, lon):
    tidal = MachinaTidalis(lat=lat, lon=lon)
    print(f"TIDAL DAEMON  v{VERSION}")
    print(f"Location: {lat}°N {lon}°E")
    print(f"Writing to: {STATE_PATH}")
    print("Updates every 5 minutes. Ctrl+C to stop.\n")
    tidal.update(force=True)
    tidal.write()
    print(f"  Initial: {tidal.summary()}\n")
    try:
        while True:
            time.sleep(60)
            tidal.update()
            tidal.write()
            triggers = tidal.triggers.poll()
            if triggers:
                for t in triggers:
                    print(f"  [TRIGGER] {t}")
    except KeyboardInterrupt:
        print("\nDaemon stopped.")

def run_watch(lat, lon):
    tidal = MachinaTidalis(lat=lat, lon=lon)
    try:
        while True:
            tidal.update()
            tidal.write()
            os.system("clear")
            print(f"  MACHINA TIDALIS  v{VERSION}  —  {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC")
            print(f"  Location: {lat}° {lon}°  (no network — pure Swiss Ephemeris)")
            print()
            print(f"  MOON")
            print(f"    force:    {tidal.moon.force_relative:.4f}x average  {_bar(tidal.moon.force_relative)}")
            print(f"    distance: {tidal.moon.dist_km:,.0f} km")
            print(f"    direction:{tidal.moon.direction}")
            print()
            print(f"  SUN")
            print(f"    force:    {tidal.sun.force_relative:.4f}x average  {_bar(tidal.sun.force_relative)}")
            print(f"    distance: {tidal.sun.dist_au:.4f} AU")
            print(f"    direction:{tidal.sun.direction}")
            print()
            print(f"  COMBINED")
            print(f"    total force:  {tidal.combined.force:.4f}  {_bar(tidal.combined.force/2)}")
            print(f"    moon-sun angle: {tidal.combined.moon_sun_angle:.1f}°")
            print(f"    spring tide:  {tidal.combined.spring_tide}")
            print(f"    neap tide:    {tidal.combined.neap_tide}")
            print()
            print(f"  PLANETS  (relative to avg Moon force)")
            for name, p in tidal.planets.items():
                print(f"    {name:<10} {p.force_relative:.6f}x  dist:{p.dist_au:.2f} AU")
            print()
            print(f"  CONDITIONS")
            print(f"    potency:    {tidal.conditions.potency:.3f}  {_bar(tidal.conditions.potency)}")
            print(f"    peak:       {tidal.conditions.peak_tidal}")
            print(f"    {tidal.conditions.description}")
            triggers = tidal.triggers.poll()
            if triggers:
                print()
                print(f"  TRIGGERS")
                for t in triggers:
                    print(f"    ◆ {t}")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nWatch stopped.")

def run_once(lat, lon):
    tidal = MachinaTidalis(lat=lat, lon=lon)
    tidal.update(force=True)
    tidal.write()
    print(tidal.to_json())


if __name__ == "__main__":
    args       = sys.argv[1:]
    lat, lon   = _parse_args()
    if "--watch" in args:
        run_watch(lat, lon)
    elif "--once" in args:
        run_once(lat, lon)
    else:
        run_daemon(lat, lon)
