#!/usr/bin/env python3
"""
MACHINA SOLARIS
════════════════════════════════════════════════════════════════════════════════
Arca Cognitorium — Solar Activity Engine

Tracks real-time solar and geomagnetic activity via NOAA's free public APIs.
No API key required. Data updates every few minutes at the source.

Monitors:
  - Kp index (geomagnetic storm level, 0-9)
  - Solar wind speed and density
  - Solar flare alerts
  - Geomagnetic storm alerts
  - Derived conditions for tower use

Usage:
    from machinae.machina_solaris import MachinaSolaris

    sol = MachinaSolaris()
    sol.update()    # makes network requests — call every 5-10 minutes

    sol.kp.current              # float, e.g. 3.33
    sol.kp.level                # "quiet" / "unsettled" / "storm_minor" / etc
    sol.kp.storm_active         # bool
    sol.wind.speed_kms          # float km/s
    sol.wind.density            # float protons/cm³
    sol.conditions.potency      # 0.0-1.0 composite solar intensity
    sol.conditions.disruptive   # bool — above storm threshold
    sol.triggers.poll()         # ["storm_began", "flare_detected", ...]

Daemon mode:
    python3 MachinaSolaris.py              # writes ~/ArcaCognitorium/.arca/solar_state.json
    python3 MachinaSolaris.py --watch      # live terminal display
    python3 MachinaSolaris.py --once       # single fetch and exit
    python3 MachinaSolaris.py --offline    # use cached data only (no network)

════════════════════════════════════════════════════════════════════════════════
DATA SOURCES (all free, no authentication)
════════════════════════════════════════════════════════════════════════════════

Kp index (3-hour):
  https://services.swpc.noaa.gov/json/planetary_k_index_1m.json

Solar wind (real-time):
  https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json

Geomagnetic storm alerts:
  https://services.swpc.noaa.gov/products/alerts.json

Update cadence: NOAA updates every 1-5 minutes.
Tower should call sol.update() every 5 minutes maximum.

════════════════════════════════════════════════════════════════════════════════
"""

import json
import time
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

VERSION    = "1.0.0"
ARCA_DIR   = Path.home() / ".arca"
STATE_PATH = ARCA_DIR / "machina_solaris.json"
CACHE_PATH = ARCA_DIR / "solar_cache.json"

# NOAA endpoints
URL_KP    = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
URL_WIND  = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
URL_ALERT = "https://services.swpc.noaa.gov/products/alerts.json"

TIMEOUT = 8  # seconds

# Kp thresholds
KP_LEVELS = [
    (0.0, "quiet"),          # 0-1: normal
    (1.0, "quiet"),
    (2.0, "unsettled"),      # 2-3: slightly elevated
    (3.0, "unsettled"),
    (4.0, "storm_minor"),    # 4: G1 minor storm
    (5.0, "storm_minor"),    # 5: G1
    (6.0, "storm_moderate"), # 6: G2
    (7.0, "storm_strong"),   # 7: G3
    (8.0, "storm_severe"),   # 8: G4
    (9.0, "storm_extreme"),  # 9: G5 — extreme event
]

# ─────────────────────────────────────────────────────────────────────────────
# FETCH HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_json(url: str, timeout: int = TIMEOUT) -> list | dict | None:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ArcaCognitorium/1.0 (+celestial_daemon)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def _kp_level(kp: float) -> str:
    for threshold, level in reversed(KP_LEVELS):
        if kp >= threshold:
            return level
    return "quiet"

# ─────────────────────────────────────────────────────────────────────────────
# STATE OBJECTS
# ─────────────────────────────────────────────────────────────────────────────

class KpState:
    """Planetary K-index — geomagnetic activity."""
    def __init__(self):
        self.current      = 0.0
        self.level        = "quiet"
        self.storm_active = False
        self.storm_level  = 0       # 0=none, 1=G1, 2=G2, 3=G3, 4=G4, 5=G5
        self.description  = "Geomagnetic conditions quiet."
        self.last_updated = ""
        self.data_fresh   = False

    def update(self, raw: list | None):
        if not raw:
            self.data_fresh = False
            return
        try:
            # Most recent reading
            recent = [r for r in raw if r.get("kp_index") is not None]
            if not recent:
                return
            latest = recent[-1]
            self.current      = float(latest.get("kp_index", 0))
            self.level        = _kp_level(self.current)
            self.storm_active = self.current >= 5.0
            self.storm_level  = max(0, int(self.current) - 4) if self.current >= 5 else 0
            self.last_updated = latest.get("time_tag", "")
            self.data_fresh   = True

            descs = {
                "quiet":           "Geomagnetic conditions quiet. Low solar influence.",
                "unsettled":       "Slightly elevated geomagnetic activity. Unsettled.",
                "storm_minor":     "G1 minor geomagnetic storm active.",
                "storm_moderate":  "G2 moderate geomagnetic storm. Elevated influence.",
                "storm_strong":    "G3 strong geomagnetic storm. Significant disruption.",
                "storm_severe":    "G4 severe geomagnetic storm. Major event.",
                "storm_extreme":   "G5 EXTREME geomagnetic storm. Rare and powerful.",
            }
            self.description = descs.get(self.level, "")
        except Exception:
            self.data_fresh = False

    def to_dict(self):
        return self.__dict__


class SolarWindState:
    """Real-time solar wind data from L1 point."""
    def __init__(self):
        self.speed_kms     = 400.0  # typical baseline ~400 km/s
        self.density       = 5.0    # protons/cm³
        self.temperature   = 0.0
        self.bz            = 0.0    # southward magnetic field component
        self.bz_negative   = False  # negative Bz = more geoeffective
        self.pressure      = 0.0    # nPa dynamic pressure
        self.last_updated  = ""
        self.data_fresh    = False

    def update(self, raw: list | None):
        if not raw:
            self.data_fresh = False
            return
        try:
            recent = [r for r in raw
                      if r.get("speed") is not None
                      and r.get("speed") != -9999.9]
            if not recent:
                return
            latest = recent[-1]
            self.speed_kms    = float(latest.get("speed", 400))
            self.density      = float(latest.get("density", 5))
            self.temperature  = float(latest.get("temperature", 0))
            self.bz           = float(latest.get("bz_gsm", 0) or 0)
            self.bz_negative  = self.bz < -5.0
            # Dynamic pressure nPa: P = 1.67e-6 * n * v²
            n = max(0, self.density); v = max(0, self.speed_kms)
            self.pressure     = round(1.67e-6 * n * v*v, 3)
            self.last_updated = latest.get("time_tag", "")
            self.data_fresh   = True
        except Exception:
            self.data_fresh = False

    def to_dict(self):
        return self.__dict__


class AlertState:
    """Active NOAA space weather alerts."""
    def __init__(self):
        self.active_alerts   = []
        self.storm_alerts    = []
        self.flare_alerts    = []
        self.alert_count     = 0
        self.last_updated    = ""
        self.data_fresh      = False

    def update(self, raw: list | None):
        if not raw:
            self.data_fresh = False
            return
        try:
            self.active_alerts = []
            self.storm_alerts  = []
            self.flare_alerts  = []
            for alert in raw[:20]:   # most recent 20
                msg = alert.get("message","")
                prod= alert.get("product_id","")
                entry = {
                    "product":  prod,
                    "message":  msg[:200],
                    "issued":   alert.get("issue_datetime",""),
                }
                self.active_alerts.append(entry)
                if "Geomagnetic Storm" in msg or "K-index" in msg:
                    self.storm_alerts.append(entry)
                if "Solar Flare" in msg or "X-ray" in msg:
                    self.flare_alerts.append(entry)
            self.alert_count  = len(self.active_alerts)
            self.data_fresh   = True
            self.last_updated = datetime.now(timezone.utc).isoformat()
        except Exception:
            self.data_fresh = False

    def to_dict(self):
        return self.__dict__


class SolarConditions:
    """Derived conditions for tower use."""
    def __init__(self):
        self.potency       = 0.0    # 0.0-1.0 composite solar intensity
        self.disruptive    = False  # True if storm or high wind pressure
        self.quiet         = True   # True if everything calm
        self.flare_recent  = False
        self.level_name    = "quiet"
        self.description   = ""

    def update(self, kp: KpState, wind: SolarWindState, alerts: AlertState):
        # Potency from Kp
        kp_score = min(1.0, self.potency_from_kp(kp.current))

        # Wind speed contribution (baseline 400, elevated >600, extreme >800)
        wind_score = min(1.0, max(0, (wind.speed_kms - 300) / 600))

        # Negative Bz is geoeffective
        bz_score = 0.2 if wind.bz_negative else 0.0

        self.potency    = round(kp_score * 0.6 + wind_score * 0.3 + bz_score, 3)
        self.disruptive = kp.storm_active or wind.speed_kms > 700
        self.quiet      = kp.current < 2.0 and wind.speed_kms < 450
        self.flare_recent= len(alerts.flare_alerts) > 0
        self.level_name = kp.level

        if   self.potency > 0.8: self.description = "Intense solar influence. The field is charged."
        elif self.potency > 0.5: self.description = "Elevated solar activity. Disruption possible."
        elif self.potency > 0.2: self.description = "Moderate solar conditions."
        else:                    self.description = "Solar conditions quiet. The field is still."

    @staticmethod
    def potency_from_kp(kp: float) -> float:
        return min(1.0, kp / 9.0)

    def to_dict(self):
        return self.__dict__


class SolarTriggers:
    def __init__(self):
        self._pending = []
        self._prev    = {}

    def update(self, kp: KpState, conditions: SolarConditions, alerts: AlertState):
        self._edge("storm",    kp.storm_active,       "geomagnetic_storm_began")
        self._edge("extreme",  kp.current >= 8.0,     "extreme_storm_event")
        self._edge("disrupt",  conditions.disruptive,  "solar_disruption_active")
        self._edge("quiet",    conditions.quiet,       "solar_conditions_quiet")
        self._edge("flare",    conditions.flare_recent,"solar_flare_detected")
        self._edge("bz_neg",   False, "")  # placeholder

    def _edge(self, key: str, current: bool, label: str):
        if not label: return
        if current and not self._prev.get(key, False):
            self._pending.append(label)
        self._prev[key] = current

    def poll(self) -> list:
        out = list(self._pending); self._pending.clear(); return out

    def peek(self) -> list:
        return list(self._pending)

    def to_dict(self):
        return {"pending": self._pending}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class MachinaSolaris:
    """
    Solar activity engine for the Arca Cognitorium.

    sol = MachinaSolaris()
    sol.update()    # fetches NOAA data — call every 5-10 minutes

    sol.kp.current              # 0-9 Kp index
    sol.kp.storm_active         # bool
    sol.kp.level                # "quiet" / "storm_minor" / "storm_extreme" etc
    sol.wind.speed_kms          # solar wind speed
    sol.wind.bz_negative        # True = southward field, more geoeffective
    sol.alerts.storm_alerts     # list of active storm alert dicts
    sol.conditions.potency      # 0.0-1.0
    sol.conditions.disruptive   # bool
    sol.triggers.poll()         # edge events
    sol.online                  # bool — last fetch succeeded
    """

    def __init__(self, offline: bool = False):
        self.offline     = offline
        self.kp          = KpState()
        self.wind        = SolarWindState()
        self.alerts      = AlertState()
        self.conditions  = SolarConditions()
        self.triggers    = SolarTriggers()
        self.online      = False
        self._tick       = 0
        self._last_fetch = 0.0

    def update(self, force: bool = False):
        self._tick += 1
        now = time.time()

        # Fetch every 5 minutes unless forced
        should_fetch = force or (now - self._last_fetch >= 300)

        if should_fetch and not self.offline:
            self._fetch()
            self._last_fetch = now

        # Derived conditions always update
        self.conditions.update(self.kp, self.wind, self.alerts)
        self.triggers.update(self.kp, self.conditions, self.alerts)

    def _fetch(self):
        kp_raw    = _fetch_json(URL_KP)
        wind_raw  = _fetch_json(URL_WIND)
        alert_raw = _fetch_json(URL_ALERT)

        self.kp.update(kp_raw)
        self.wind.update(wind_raw)
        self.alerts.update(alert_raw)

        self.online = any([self.kp.data_fresh,
                           self.wind.data_fresh,
                           self.alerts.data_fresh])

        # Cache to disk for offline fallback
        if self.online:
            try:
                cache = {
                    "kp":    kp_raw,
                    "wind":  wind_raw,
                    "alerts":alert_raw,
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                }
                ARCA_DIR.mkdir(exist_ok=True)
                with open(CACHE_PATH, "w") as f:
                    json.dump(cache, f)
            except Exception:
                pass
        else:
            # Try cache
            self._load_cache()

    def _load_cache(self):
        try:
            with open(CACHE_PATH) as f:
                cache = json.load(f)
            self.kp.update(cache.get("kp"))
            self.wind.update(cache.get("wind"))
            self.alerts.update(cache.get("alerts"))
        except Exception:
            pass

    def to_dict(self) -> dict:
        return {
            "meta": {
                "ts":      datetime.now(timezone.utc).isoformat(),
                "version": VERSION,
                "tick":    self._tick,
                "online":  self.online,
                "offline_mode": self.offline,
            },
            "kp":         self.kp.to_dict(),
            "wind":       self.wind.to_dict(),
            "alerts":     self.alerts.to_dict(),
            "conditions": self.conditions.to_dict(),
            "triggers":   self.triggers.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def write(self):
        ARCA_DIR.mkdir(exist_ok=True)
        tmp = ARCA_DIR / "machina_solaris.tmp"
        with open(tmp, "w") as f:
            f.write(self.to_json())
        tmp.replace(STATE_PATH)

    def summary(self) -> str:
        return (f"Kp:{self.kp.current:.1f} {self.kp.level}"
                f"  wind:{self.wind.speed_kms:.0f}km/s"
                f"  Bz:{self.wind.bz:.1f}nT"
                f"  potency:{self.conditions.potency:.2f}"
                f"  {'STORM' if self.kp.storm_active else 'quiet'}"
                f"  {'ONLINE' if self.online else 'cached'}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _bar(val: float, width: int = 20) -> str:
    filled = int(val * width)
    return "█" * filled + "░" * (width - filled)

def run_daemon(offline: bool):
    sol = MachinaSolaris(offline=offline)
    print(f"SOLAR DAEMON  v{VERSION}")
    print(f"Writing to: {STATE_PATH}")
    print(f"Mode: {'OFFLINE (cached)' if offline else 'ONLINE'}")
    print("Updates every 5 minutes. Ctrl+C to stop.\n")
    sol.update(force=True)
    sol.write()
    print(f"  Initial: {sol.summary()}\n")
    try:
        while True:
            time.sleep(60)
            sol.update()
            sol.write()
            triggers = sol.triggers.poll()
            if triggers:
                for t in triggers:
                    print(f"  [TRIGGER] {t}")
    except KeyboardInterrupt:
        print("\nDaemon stopped.")

def run_watch(offline: bool):
    sol = MachinaSolaris(offline=offline)
    try:
        while True:
            sol.update()
            sol.write()
            os.system("clear")
            print(f"  MACHINA SOLARIS  v{VERSION}  —  {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC")
            print(f"  Status: {'ONLINE' if sol.online else 'OFFLINE/CACHED'}")
            print()
            print(f"  KP INDEX")
            print(f"    current:  {sol.kp.current:.2f}  {_bar(sol.kp.current/9)}")
            print(f"    level:    {sol.kp.level}")
            print(f"    storm:    {'YES — ' + str(sol.kp.storm_level) + 'G' if sol.kp.storm_active else 'no'}")
            print(f"    desc:     {sol.kp.description}")
            print()
            print(f"  SOLAR WIND  (L1 point)")
            print(f"    speed:    {sol.wind.speed_kms:.0f} km/s")
            print(f"    density:  {sol.wind.density:.1f} p/cm³")
            print(f"    Bz:       {sol.wind.bz:.2f} nT  {'← SOUTHWARD' if sol.wind.bz_negative else ''}")
            print(f"    pressure: {sol.wind.pressure:.2f} nPa")
            print()
            print(f"  CONDITIONS")
            print(f"    potency:    {sol.conditions.potency:.3f}  {_bar(sol.conditions.potency)}")
            print(f"    disruptive: {sol.conditions.disruptive}")
            print(f"    quiet:      {sol.conditions.quiet}")
            print(f"    flare:      {sol.conditions.flare_recent}")
            print(f"    {sol.conditions.description}")
            if sol.alerts.storm_alerts:
                print()
                print(f"  ACTIVE ALERTS ({len(sol.alerts.storm_alerts)})")
                for a in sol.alerts.storm_alerts[:3]:
                    print(f"    {a['message'][:80]}")
            triggers = sol.triggers.poll()
            if triggers:
                print()
                print(f"  TRIGGERS")
                for t in triggers:
                    print(f"    ◆ {t}")
            print(f"\n  Next fetch in ~{max(0, 300 - int(time.time() - sol._last_fetch))}s")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nWatch stopped.")

def run_once(offline: bool):
    sol = MachinaSolaris(offline=offline)
    sol.update(force=True)
    sol.write()
    print(sol.to_json())


if __name__ == "__main__":
    args    = sys.argv[1:]
    offline = "--offline" in args
    if "--watch" in args:
        run_watch(offline)
    elif "--once" in args:
        run_once(offline)
    else:
        run_daemon(offline)
