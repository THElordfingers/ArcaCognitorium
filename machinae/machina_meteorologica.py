#!/usr/bin/env python3
"""
MACHINA METEOROLOGICA
════════════════════════════════════════════════════════════════════════════════
Arca Cognitorium — Local Weather Engine

Real-time local weather via Open-Meteo (https://open-meteo.com).
Free, no API key required, no rate limits for reasonable use.
Updates every 15 minutes.

Usage:
    from machinae.machina_meteorologica import MachinaMeteorologica

    wx = MachinaMeteorologica(lat=51.5, lon=-0.1)
    wx.update()    # network request

    wx.current.temp_c           # float
    wx.current.feels_like_c     # float
    wx.current.description      # "Clear sky" / "Rain" / etc
    wx.current.is_raining       # bool
    wx.current.pressure_hpa     # float
    wx.current.pressure_trend   # "rising" / "falling" / "stable"
    wx.current.uv_index         # float
    wx.current.wind_kph         # float
    wx.conditions.potency       # 0.0-1.0 atmospheric intensity
    wx.conditions.oppressive    # True if high heat + humidity
    wx.conditions.stormy        # True if significant precipitation/wind
    wx.triggers.poll()          # ["rain_began", "pressure_drop", ...]

Daemon mode:
    python3 MachinaMeteorologica.py --lat 51.5 --lon -0.1
    python3 MachinaMeteorologica.py --lat 51.5 --lon -0.1 --watch
    python3 MachinaMeteorologica.py --lat 51.5 --lon -0.1 --once
    python3 MachinaMeteorologica.py --offline    # use cached data

════════════════════════════════════════════════════════════════════════════════
WMO WEATHER CODES → human descriptions
════════════════════════════════════════════════════════════════════════════════
Open-Meteo uses WMO Weather interpretation codes.
0=clear, 1-3=partly cloudy, 45-48=fog, 51-67=drizzle/rain,
71-77=snow, 80-82=showers, 85-86=snow showers, 95=thunderstorm, 96-99=hail
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
STATE_PATH = ARCA_DIR / "machina_meteorologica.json"
CACHE_PATH = ARCA_DIR / "weather_cache.json"

TIMEOUT       = 10
UPDATE_SECS   = 900   # 15 minutes

# Open-Meteo endpoint — no API key
BASE_URL = ("https://api.open-meteo.com/v1/forecast"
            "?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,rain,weather_code,surface_pressure,wind_speed_10m,"
            "wind_direction_10m,cloud_cover,uv_index,is_day"
            "&hourly=surface_pressure"
            "&forecast_days=1"
            "&wind_speed_unit=kmh"
            "&timezone=UTC")

WMO_DESCRIPTIONS = {
    0:"Clear sky", 1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast",
    45:"Fog", 48:"Rime fog",
    51:"Light drizzle", 53:"Moderate drizzle", 55:"Dense drizzle",
    56:"Light freezing drizzle", 57:"Heavy freezing drizzle",
    61:"Slight rain", 63:"Moderate rain", 65:"Heavy rain",
    66:"Light freezing rain", 67:"Heavy freezing rain",
    71:"Slight snow", 73:"Moderate snow", 75:"Heavy snow",
    77:"Snow grains",
    80:"Slight showers", 81:"Moderate showers", 82:"Violent showers",
    85:"Slight snow showers", 86:"Heavy snow showers",
    95:"Thunderstorm", 96:"Thunderstorm with hail", 99:"Thunderstorm heavy hail",
}

RAIN_CODES    = {51,53,55,56,57,61,63,65,66,67,80,81,82}
SNOW_CODES    = {71,73,75,77,85,86}
STORM_CODES   = {95,96,99}
CLEAR_CODES   = {0,1}

# ─────────────────────────────────────────────────────────────────────────────
# FETCH
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_json(url: str) -> dict | None:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ArcaCognitorium/1.0 (+weather_daemon)"}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────────────────────
# STATE OBJECTS
# ─────────────────────────────────────────────────────────────────────────────

class CurrentWeather:
    def __init__(self):
        self.temp_c          = 15.0
        self.feels_like_c    = 15.0
        self.humidity        = 50
        self.precipitation   = 0.0
        self.rain_mm         = 0.0
        self.weather_code    = 0
        self.description     = "Clear sky"
        self.pressure_hpa    = 1013.0
        self.pressure_trend  = "stable"    # "rising" / "falling" / "stable"
        self.wind_kph        = 0.0
        self.wind_direction  = 0
        self.cloud_cover     = 0
        self.uv_index        = 0.0
        self.is_day          = True
        self.is_raining      = False
        self.is_snowing      = False
        self.is_stormy       = False
        self.is_clear        = True
        self.last_updated    = ""
        self.data_fresh      = False
        self._prev_pressure  = 1013.0

    def update(self, raw: dict | None):
        if not raw or "current" not in raw:
            self.data_fresh = False
            return
        try:
            c = raw["current"]
            self._prev_pressure  = self.pressure_hpa
            self.temp_c          = float(c.get("temperature_2m", 15))
            self.feels_like_c    = float(c.get("apparent_temperature", 15))
            self.humidity        = int(c.get("relative_humidity_2m", 50))
            self.precipitation   = float(c.get("precipitation", 0))
            self.rain_mm         = float(c.get("rain", 0))
            self.weather_code    = int(c.get("weather_code", 0))
            self.pressure_hpa    = float(c.get("surface_pressure", 1013))
            self.wind_kph        = float(c.get("wind_speed_10m", 0))
            self.wind_direction  = int(c.get("wind_direction_10m", 0))
            self.cloud_cover     = int(c.get("cloud_cover", 0))
            self.uv_index        = float(c.get("uv_index", 0))
            self.is_day          = bool(c.get("is_day", 1))
            self.description     = WMO_DESCRIPTIONS.get(self.weather_code, "Unknown")
            self.last_updated    = c.get("time", "")

            wc = self.weather_code
            self.is_raining = wc in RAIN_CODES
            self.is_snowing = wc in SNOW_CODES
            self.is_stormy  = wc in STORM_CODES
            self.is_clear   = wc in CLEAR_CODES

            # Pressure trend
            diff = self.pressure_hpa - self._prev_pressure
            if   diff >  1.5: self.pressure_trend = "rising"
            elif diff < -1.5: self.pressure_trend = "falling"
            else:             self.pressure_trend = "stable"

            self.data_fresh = True
        except Exception:
            self.data_fresh = False

    def to_dict(self):
        return {k:v for k,v in self.__dict__.items() if not k.startswith("_")}


class WeatherConditions:
    """Derived conditions for tower use."""
    def __init__(self):
        self.potency       = 0.3   # 0.0-1.0 atmospheric intensity
        self.oppressive    = False  # hot + humid
        self.stormy        = False
        self.pressure_drop = False  # falling pressure (often precedes bad weather)
        self.serene        = False  # clear, mild, calm
        self.description   = ""

    def update(self, current: CurrentWeather):
        # Potency from storm, pressure, UV, wind
        storm_score   = 1.0 if current.is_stormy else (0.5 if current.is_raining else 0.0)
        pressure_score= 0.5 if current.pressure_trend == "falling" else 0.0
        wind_score    = min(1.0, current.wind_kph / 80.0)
        uv_score      = min(1.0, current.uv_index / 10.0) if current.is_day else 0.0

        self.potency = round(
            storm_score * 0.4 + pressure_score * 0.25 +
            wind_score * 0.2 + uv_score * 0.15, 3)

        self.stormy       = current.is_stormy or (current.is_raining
                            and current.wind_kph > 40)
        self.pressure_drop= current.pressure_trend == "falling"
        self.oppressive   = current.temp_c > 28 and current.humidity > 70
        self.serene       = (current.is_clear and current.wind_kph < 20
                             and current.temp_c > 10 and current.temp_c < 25
                             and not current.is_raining)

        if   self.stormy:        self.description = "Storm conditions. High atmospheric intensity."
        elif self.oppressive:    self.description = "Oppressive heat and humidity."
        elif self.pressure_drop: self.description = "Pressure falling. Change approaching."
        elif self.serene:        self.description = "Serene conditions. Clear and calm."
        elif current.is_raining: self.description = "Rain. The world turns inward."
        elif not current.is_day: self.description = "Night conditions."
        else:                    self.description = "Moderate conditions."

    def to_dict(self):
        return self.__dict__


class WeatherTriggers:
    def __init__(self):
        self._pending = []
        self._prev    = {}

    def _edge(self, key, current, label):
        if current and not self._prev.get(key, False):
            self._pending.append(label)
        self._prev[key] = current

    def update(self, current: CurrentWeather, conditions: WeatherConditions):
        self._edge("rain",     current.is_raining,       "rain_began")
        self._edge("storm",    current.is_stormy,        "storm_began")
        self._edge("snow",     current.is_snowing,       "snow_began")
        self._edge("clear",    current.is_clear,         "sky_cleared")
        self._edge("drop",     conditions.pressure_drop,  "pressure_dropping")
        self._edge("opp",      conditions.oppressive,    "oppressive_conditions")
        self._edge("serene",   conditions.serene,        "serene_conditions")

    def poll(self) -> list:
        out = list(self._pending); self._pending.clear(); return out

    def peek(self) -> list:
        return list(self._pending)

    def to_dict(self):
        return {"pending": self._pending}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class MachinaMeteorologica:
    """
    Local weather engine for the Arca Cognitorium.

    wx = MachinaMeteorologica(lat=51.5, lon=-0.1)
    wx.update()

    wx.current.temp_c
    wx.current.description
    wx.current.is_raining
    wx.current.pressure_trend   # "rising" / "falling" / "stable"
    wx.current.uv_index
    wx.conditions.potency
    wx.conditions.stormy
    wx.conditions.serene
    wx.online
    wx.triggers.poll()
    """

    def __init__(self, lat: float = 0.0, lon: float = 0.0,
                 offline: bool = False):
        self.lat         = lat
        self.lon         = lon
        self.offline     = offline
        self.current     = CurrentWeather()
        self.conditions  = WeatherConditions()
        self.triggers    = WeatherTriggers()
        self.online      = False
        self._tick       = 0
        self._last_fetch = 0.0

    def update(self, force: bool = False):
        self._tick += 1
        now = time.time()
        should_fetch = force or (now - self._last_fetch >= UPDATE_SECS)

        if should_fetch and not self.offline:
            self._fetch()
            self._last_fetch = now

        self.conditions.update(self.current)
        self.triggers.update(self.current, self.conditions)

    def _fetch(self):
        url = BASE_URL.format(lat=self.lat, lon=self.lon)
        raw = _fetch_json(url)
        self.current.update(raw)
        self.online = self.current.data_fresh

        if self.online:
            try:
                ARCA_DIR.mkdir(exist_ok=True)
                with open(CACHE_PATH, "w") as f:
                    json.dump({
                        "raw": raw,
                        "cached_at": datetime.now(timezone.utc).isoformat(),
                    }, f)
            except Exception:
                pass
        else:
            self._load_cache()

    def _load_cache(self):
        try:
            with open(CACHE_PATH) as f:
                cache = json.load(f)
            self.current.update(cache.get("raw"))
        except Exception:
            pass

    def to_dict(self) -> dict:
        return {
            "meta": {
                "ts":       datetime.now(timezone.utc).isoformat(),
                "version":  VERSION,
                "tick":     self._tick,
                "online":   self.online,
                "location": {"lat": self.lat, "lon": self.lon},
            },
            "current":    self.current.to_dict(),
            "conditions": self.conditions.to_dict(),
            "triggers":   self.triggers.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def write(self):
        ARCA_DIR.mkdir(exist_ok=True)
        tmp = ARCA_DIR / "machina_meteorologica.tmp"
        with open(tmp, "w") as f:
            f.write(self.to_json())
        tmp.replace(STATE_PATH)

    def summary(self) -> str:
        c = self.current
        return (f"{c.temp_c:.1f}°C (feels {c.feels_like_c:.1f}°C)"
                f"  {c.description}"
                f"  {c.pressure_hpa:.0f}hPa {c.pressure_trend}"
                f"  wind:{c.wind_kph:.0f}kph"
                f"  potency:{self.conditions.potency:.2f}"
                f"  {'ONLINE' if self.online else 'cached'}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _bar(val: float, width: int = 20) -> str:
    filled = int(min(1.0, val) * width)
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

def run_daemon(lat, lon, offline):
    wx = MachinaMeteorologica(lat=lat, lon=lon, offline=offline)
    print(f"WEATHER DAEMON  v{VERSION}")
    print(f"Location: {lat}°N {lon}°E")
    print(f"Writing to: {STATE_PATH}")
    print(f"Mode: {'OFFLINE' if offline else 'ONLINE'}")
    print("Updates every 15 minutes. Ctrl+C to stop.\n")
    wx.update(force=True)
    wx.write()
    print(f"  Initial: {wx.summary()}\n")
    try:
        while True:
            time.sleep(60)
            wx.update()
            wx.write()
            triggers = wx.triggers.poll()
            if triggers:
                for t in triggers:
                    print(f"  [TRIGGER] {t}")
    except KeyboardInterrupt:
        print("\nDaemon stopped.")

def run_watch(lat, lon, offline):
    wx = MachinaMeteorologica(lat=lat, lon=lon, offline=offline)
    try:
        while True:
            wx.update()
            wx.write()
            os.system("clear")
            c  = wx.current
            co = wx.conditions
            print(f"  MACHINA METEOROLOGICA  v{VERSION}  —  {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC")
            print(f"  Location: {lat}° {lon}°  Status: {'ONLINE' if wx.online else 'OFFLINE/CACHED'}")
            print()
            print(f"  CURRENT CONDITIONS")
            print(f"    {c.description}")
            print(f"    temperature:  {c.temp_c:.1f}°C  (feels {c.feels_like_c:.1f}°C)")
            print(f"    humidity:     {c.humidity}%")
            print(f"    pressure:     {c.pressure_hpa:.1f} hPa  [{c.pressure_trend}]")
            print(f"    wind:         {c.wind_kph:.0f} kph @ {c.wind_direction}°")
            print(f"    cloud cover:  {c.cloud_cover}%")
            print(f"    UV index:     {c.uv_index:.1f}")
            print(f"    precipitation:{c.precipitation:.1f} mm")
            print(f"    daytime:      {c.is_day}")
            print()
            print(f"  CONDITIONS")
            print(f"    potency:      {co.potency:.3f}  {_bar(co.potency)}")
            print(f"    stormy:       {co.stormy}")
            print(f"    pressure drop:{co.pressure_drop}")
            print(f"    oppressive:   {co.oppressive}")
            print(f"    serene:       {co.serene}")
            print(f"    {co.description}")
            triggers = wx.triggers.poll()
            if triggers:
                print()
                print(f"  TRIGGERS")
                for t in triggers:
                    print(f"    ◆ {t}")
            eta = max(0, UPDATE_SECS - int(time.time() - wx._last_fetch))
            print(f"\n  Next fetch in ~{eta}s")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nWatch stopped.")

def run_once(lat, lon, offline):
    wx = MachinaMeteorologica(lat=lat, lon=lon, offline=offline)
    wx.update(force=True)
    wx.write()
    print(wx.to_json())


if __name__ == "__main__":
    args    = sys.argv[1:]
    offline = "--offline" in args
    lat, lon = _parse_args()
    if "--watch" in args:
        run_watch(lat, lon, offline)
    elif "--once" in args:
        run_once(lat, lon, offline)
    else:
        run_daemon(lat, lon, offline)
