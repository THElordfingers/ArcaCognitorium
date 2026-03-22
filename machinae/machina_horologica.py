#!/usr/bin/env python3
"""
MACHINA HOROLOGICA
════════════════════════════════════════════════════════════════════════════════
Arca Cognitorium — Celestial State Engine

A self-contained astronomical state object. Instantiate once.
Call update() on a timer. Read from anywhere.

Usage (direct):
    from machinae.machina_horologica import MachinaHorologica

    sky = MachinaHorologica()
    sky.update()

    sky.moon.phase_name       # "Waxing Gibbous"
    sky.moon.illumination     # 73.4
    sky.season.saturation     # 0.68
    sky.conditions.mercury_rx # True
    sky.triggers.poll()       # ["mercury_retrograde_began"]

Usage (daemon mode):
    python3 MachinaHorologica.py              # writes ~/ArcaCognitorium/.arca/celestial_state.json
    python3 MachinaHorologica.py --once       # single write, then exit
    python3 MachinaHorologica.py --watch      # pretty-print live state to terminal

Integration in Arca:
    from machinae.machina_horologica import MachinaHorologica
    sky = MachinaHorologica()
    sky.update()

    # Entity compiler reads sky.entities["archivist"].affinity
    # Assessor reads sky.conditions.auspicious
    # Palette system reads sky.season.saturation and sky.season.palette_key
    # Router can check sky.triggers.poll() for ceremony events

════════════════════════════════════════════════════════════════════════════════
"""

import swisseph as swe
import math
import json
import time
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

swe.set_sid_mode(swe.SIDM_LAHIRI)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

VERSION = "1.0.0"

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]
SIGN_GLYPHS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]

MOON_PHASE_NAMES = [
    "New Moon","Waxing Crescent","First Quarter","Waxing Gibbous",
    "Full Moon","Waning Gibbous","Last Quarter","Waning Crescent",
]
MOON_PHASE_GLYPHS = ["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]

NAMED_MOONS = {
    1:"Wolf Moon", 2:"Snow Moon",  3:"Worm Moon",      4:"Pink Moon",
    5:"Flower Moon",6:"Strawberry Moon",7:"Buck Moon",  8:"Sturgeon Moon",
    9:"Harvest Moon",10:"Hunter's Moon",11:"Beaver Moon",12:"Cold Moon",
}

NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
    "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha",
    "Shatabhisha","Purva Bhadra","Uttara Bhadra","Revati",
]
NAKSHATRA_RULERS = [
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
]

TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
]
TITHI_QUALITY = ["Nanda","Bhadra","Jaya","Rikta","Purna"] * 3
AUSPICIOUS_TITHIS = {"Nanda","Bhadra","Jaya","Purna"}

YOGA_NAMES = [
    "Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana",
    "Atiganda","Sukarman","Dhriti","Shula","Ganda",
    "Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
    "Siddhi","Vyatipata","Variyan","Parigha","Shiva",
    "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti",
]
INAUSPICIOUS_YOGAS = {"Vishkumbha","Atiganda","Shula","Ganda","Vyaghata",
                       "Vajra","Vyatipata","Parigha","Vaidhriti"}

VARA_NAMES = [
    "Ravivara","Somavara","Mangalavara","Budhavara",
    "Guruvara","Shukravara","Shanivara",
]
DAY_RULERS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
PLANETARY_HOUR_SEQ = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"]

SEASON_NAMES  = ["Winter","Spring","Summer","Autumn"]
SEASON_SPANS  = [
    "Winter Solstice → Spring Equinox",
    "Spring Equinox → Summer Solstice",
    "Summer Solstice → Autumn Equinox",
    "Autumn Equinox → Winter Solstice",
]
# Palette keys for each season — tower maps these to its own colour system
SEASON_PALETTE_KEYS = ["winter","spring","summer","autumn"]

PLANET_IDS = {
    "Sun":swe.SUN,"Moon":swe.MOON,"Mercury":swe.MERCURY,"Venus":swe.VENUS,
    "Mars":swe.MARS,"Jupiter":swe.JUPITER,"Saturn":swe.SATURN,
    "Uranus":swe.URANUS,"Neptune":swe.NEPTUNE,"Pluto":swe.PLUTO,
    "Rahu":swe.MEAN_NODE,
}

ROMAN = {
    1000:"M",900:"CM",500:"D",400:"CD",100:"C",90:"XC",
    50:"L",40:"XL",10:"X",9:"IX",5:"V",4:"IV",1:"I",
}

# Entity affinity map — which signs/nakshatras each entity resonates with
# Affinity sign index, friction sign index
# These are the starting defaults — the tower can override via entity YAML
ENTITY_AFFINITY = {
    "archivist":     {"affinity_signs":[5,9],  "friction_signs":[1,7]},   # Virgo, Capricorn
    "assessor":      {"affinity_signs":[6,10], "friction_signs":[0,3]},   # Libra, Aquarius
    "contrarian":    {"affinity_signs":[1,8],  "friction_signs":[4,11]},  # Taurus, Sagittarius
    "luminarious":   {"affinity_signs":[4,0],  "friction_signs":[7,10]},  # Leo, Aries
    "minimalist":    {"affinity_signs":[9,6],  "friction_signs":[2,5]},   # Capricorn, Libra
    "pessimist":     {"affinity_signs":[7,3],  "friction_signs":[0,4]},   # Scorpio, Cancer
    "socratic":      {"affinity_signs":[2,6],  "friction_signs":[8,11]},  # Gemini, Libra
    "speculator":    {"affinity_signs":[8,11], "friction_signs":[5,2]},   # Sagittarius, Pisces
    "systems_thinker":{"affinity_signs":[10,6],"friction_signs":[3,9]},   # Aquarius, Libra
    "toolsmith":     {"affinity_signs":[2,5],  "friction_signs":[8,11]},  # Gemini, Virgo
}

# Output path
ARCA_DIR   = Path.home() / ".arca"
STATE_PATH = ARCA_DIR / "machina_horologica.json"

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def to_roman(n: int) -> str:
    if n <= 0: return "O"
    r = ""
    for val, num in ROMAN.items():
        while n >= val:
            r += num; n -= val
    return r

def now_jd(dt: datetime) -> float:
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute/60 + dt.second/3600)

def get_lon(jd: float, pid: int) -> tuple:
    """Returns (sign_idx, degree_in_sign, retrograde, absolute_lon, speed)"""
    r = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
    return int(r[0]/30)%12, r[0]%30, r[3]<0, r[0], r[3]

# ─────────────────────────────────────────────────────────────────────────────
# SUB-OBJECTS
# ─────────────────────────────────────────────────────────────────────────────

class TimeState:
    """Current time in multiple formats."""
    def __init__(self):
        self.utc         = ""
        self.iso         = ""
        self.hour        = 0
        self.minute      = 0
        self.second      = 0
        self.day         = 1
        self.month       = 1
        self.year        = 2024
        self.weekday     = ""
        self.month_name  = ""
        self.roman_hour  = ""
        self.roman_minute= ""
        self.roman_date  = ""
        self.jd          = 0.0

    def update(self, now: datetime):
        self.utc         = now.strftime("%H:%M:%S")
        self.iso         = now.isoformat()
        self.hour        = now.hour
        self.minute      = now.minute
        self.second      = now.second
        self.day         = now.day
        self.month       = now.month
        self.year        = now.year
        self.weekday     = now.strftime("%A")
        self.month_name  = now.strftime("%B")
        self.roman_hour  = to_roman(now.hour) if now.hour > 0 else "XII"
        self.roman_minute= to_roman(now.minute) if now.minute > 0 else "O"
        self.roman_date  = (f"{to_roman(now.day)} · "
                            f"{to_roman(now.month)} · "
                            f"{to_roman(now.year)}")
        self.jd = now_jd(now)

    def to_dict(self):
        return self.__dict__


class MoonState:
    """Everything about the Moon."""
    def __init__(self):
        self.phase_idx       = 0
        self.phase_name      = "New Moon"
        self.phase_glyph     = "🌑"
        self.illumination    = 0.0
        self.elongation      = 0.0
        self.cycle_day       = 1
        self.sign_idx        = 0
        self.sign_name       = "Aries"
        self.sign_glyph      = "♈"
        self.degree          = 0.0
        self.longitude       = 0.0
        self.nakshatra_idx   = 0
        self.nakshatra_name  = "Ashwini"
        self.nakshatra_ruler = "Ketu"
        self.nakshatra_pada  = 1
        self.named_moon      = ""        # "Harvest Moon" etc, set at full moon
        self.is_full         = False
        self.is_new          = False
        self.is_waxing       = False
        self.distance_km     = 384400
        self.distance_pct    = 0.0      # % from average
        self.distance_label  = "Average"
        self.days_to_full    = 0
        self.days_to_new     = 0

    def update(self, jd: float, now: datetime):
        sun_lon  = swe.calc_ut(jd, swe.SUN,  swe.FLG_SIDEREAL)[0][0]
        moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
        angle    = (moon_lon - sun_lon) % 360

        self.elongation   = angle
        self.illumination = (1 - math.cos(math.radians(angle))) / 2 * 100
        self.phase_idx    = int(angle / 45) % 8
        self.phase_name   = MOON_PHASE_NAMES[self.phase_idx]
        self.phase_glyph  = MOON_PHASE_GLYPHS[self.phase_idx]
        self.cycle_day    = max(1, int(angle / (360/29.5)))
        self.is_full      = self.phase_idx == 4
        self.is_new       = self.phase_idx == 0
        self.is_waxing    = angle <= 180

        si, deg, _, lon, _ = get_lon(jd, swe.MOON)
        self.sign_idx    = si
        self.sign_name   = SIGN_NAMES[si]
        self.sign_glyph  = SIGN_GLYPHS[si]
        self.degree      = deg
        self.longitude   = lon

        nak_sz = 360 / 27
        nak_i  = int(lon / nak_sz) % 27
        pada   = int((lon % nak_sz) / (nak_sz / 4)) + 1
        self.nakshatra_idx   = nak_i
        self.nakshatra_name  = NAKSHATRA_NAMES[nak_i]
        self.nakshatra_ruler = NAKSHATRA_RULERS[nak_i]
        self.nakshatra_pada  = pada

        # Named moon — applies in the full moon window (phase_idx 3,4,5)
        if self.phase_idx in (3, 4, 5):
            self.named_moon = NAMED_MOONS.get(now.month, "")
        else:
            self.named_moon = ""

        # Distance
        r = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
        dist_km = r[2] * 149597870.7
        pct = (dist_km - 384400) / 384400 * 100
        self.distance_km    = int(dist_km)
        self.distance_pct   = round(pct, 2)
        self.distance_label = ("Supermoon" if pct < -3
                               else "Micromoon" if pct > 3
                               else "Average")

        # Days to next phase
        def days_to(target):
            for d in range(1, 32):
                future_jd  = jd + d
                s_lon = swe.calc_ut(future_jd, swe.SUN,  swe.FLG_SIDEREAL)[0][0]
                m_lon = swe.calc_ut(future_jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
                a = (m_lon - s_lon) % 360
                if abs(a - target) < 6: return d
            return 15
        self.days_to_full = days_to(180) if angle < 180 else 0
        self.days_to_new  = days_to(350) if angle > 10  else 0

    def to_dict(self):
        return self.__dict__


class SunState:
    """Everything about the Sun."""
    def __init__(self):
        self.sign_idx       = 0
        self.sign_name      = "Aries"
        self.sign_glyph     = "♈"
        self.degree         = 0.0
        self.longitude      = 0.0
        self.nakshatra_idx  = 0
        self.nakshatra_name = "Ashwini"
        self.nakshatra_ruler= "Ketu"
        self.nakshatra_pada = 1

    def update(self, jd: float):
        si, deg, _, lon, _ = get_lon(jd, swe.SUN)
        self.sign_idx    = si
        self.sign_name   = SIGN_NAMES[si]
        self.sign_glyph  = SIGN_GLYPHS[si]
        self.degree      = deg
        self.longitude   = lon
        nak_sz = 360 / 27
        nak_i  = int(lon / nak_sz) % 27
        pada   = int((lon % nak_sz) / (nak_sz / 4)) + 1
        self.nakshatra_idx   = nak_i
        self.nakshatra_name  = NAKSHATRA_NAMES[nak_i]
        self.nakshatra_ruler = NAKSHATRA_RULERS[nak_i]
        self.nakshatra_pada  = pada

    def to_dict(self):
        return self.__dict__


class PlanetState:
    """State of a single planet."""
    def __init__(self, name: str):
        self.name        = name
        self.sign_idx    = 0
        self.sign_name   = "Aries"
        self.sign_glyph  = "♈"
        self.degree      = 0.0
        self.longitude   = 0.0
        self.retrograde  = False
        self.speed       = 0.0
        # Inner planets only
        self.elongation       = None
        self.phase_name       = None
        self.phase_glyph      = None
        self.morning_star     = None

    def update(self, jd: float, pid: int):
        si, deg, rx, lon, spd = get_lon(jd, pid)
        self.sign_idx   = si
        self.sign_name  = SIGN_NAMES[si]
        self.sign_glyph = SIGN_GLYPHS[si]
        self.degree     = round(deg, 3)
        self.longitude  = round(lon, 3)
        self.retrograde = rx
        self.speed      = round(spd, 4)

        # Phase for inner planets
        if self.name in ("Mercury","Venus"):
            sun_lon = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
            diff = (lon - sun_lon) % 360
            if diff > 180: diff -= 360
            elong = abs(diff)
            self.elongation   = round(elong, 2)
            self.morning_star = diff < 0
            self.phase_name   = "Morning Star" if diff < 0 else "Evening Star"
            self.phase_glyph  = "🌅" if diff < 0 else "🌆"

    def to_dict(self):
        return self.__dict__


class NodesState:
    """Rahu and Ketu."""
    def __init__(self):
        self.rahu_sign_idx  = 0
        self.rahu_sign_name = "Aries"
        self.rahu_degree    = 0.0
        self.rahu_longitude = 0.0
        self.ketu_sign_idx  = 6
        self.ketu_sign_name = "Libra"
        self.ketu_degree    = 0.0
        self.ketu_longitude = 180.0
        self.eclipse_active = False
        self.eclipse_dist   = 90.0
        self.eclipse_pct    = 0.0
        self.eclipse_status = "clear"  # "clear"/"approaching"/"season"/"peak"

    def update(self, jd: float):
        si, deg, _, lon, _ = get_lon(jd, swe.MEAN_NODE)
        self.rahu_sign_idx  = si
        self.rahu_sign_name = SIGN_NAMES[si]
        self.rahu_degree    = round(deg, 3)
        self.rahu_longitude = round(lon, 3)
        k_lon = (lon + 180) % 360
        k_si  = int(k_lon / 30) % 12
        self.ketu_sign_idx  = k_si
        self.ketu_sign_name = SIGN_NAMES[k_si]
        self.ketu_degree    = round(k_lon % 30, 3)
        self.ketu_longitude = round(k_lon, 3)

        sun_lon = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
        d_r = abs((sun_lon - lon     + 180) % 360 - 180)
        d_k = abs((sun_lon - k_lon   + 180) % 360 - 180)
        dist = min(d_r, d_k)
        self.eclipse_dist   = round(dist, 2)
        self.eclipse_pct    = round(max(0, (18 - dist) / 18 * 100), 1)
        self.eclipse_active = dist < 18

        if   dist > 45:  self.eclipse_status = "clear"
        elif dist > 18:  self.eclipse_status = "approaching"
        elif dist > 8:   self.eclipse_status = "season"
        else:            self.eclipse_status = "peak"

    def to_dict(self):
        return self.__dict__


class SeasonState:
    """Current season, palette state, and turning points."""
    def __init__(self):
        self.name           = "Winter"
        self.span           = ""
        self.idx            = 0
        self.days_until     = 0
        self.progress       = 0.0   # 0.0=just entered, 1.0=about to leave
        self.palette_key    = "winter"
        self.saturation     = 0.4   # lunar-modulated 0.4-1.0
        self.next_event     = ""
        self.next_event_days= 0

    def update(self, now: datetime, moon_illumination: float):
        mo, dy = now.month, now.day
        if   (mo==12 and dy>=21) or mo<=2 or (mo==3 and dy<20):
            idx=0; dur=90
            target=datetime(now.year+(1 if mo==12 else 0),3,20,tzinfo=timezone.utc)
        elif (mo==3 and dy>=20) or mo<=5 or (mo==6 and dy<21):
            idx=1; dur=92
            target=datetime(now.year,6,21,tzinfo=timezone.utc)
        elif (mo==6 and dy>=21) or mo<=8 or (mo==9 and dy<22):
            idx=2; dur=93
            target=datetime(now.year,9,22,tzinfo=timezone.utc)
        else:
            idx=3; dur=90
            target=datetime(now.year,12,21,tzinfo=timezone.utc)

        days_left = max(0,(target.replace(tzinfo=timezone.utc)-
                           now.replace(tzinfo=timezone.utc)).days)
        days_in   = max(0, dur - days_left)

        self.idx         = idx
        self.name        = SEASON_NAMES[idx]
        self.span        = SEASON_SPANS[idx]
        self.palette_key = SEASON_PALETTE_KEYS[idx]
        self.days_until  = days_left
        self.progress    = round(days_in / dur, 3)

        # Lunar saturation: new moon = 0.4 (muted), full moon = 1.0 (rich)
        self.saturation  = round(0.4 + (moon_illumination / 100) * 0.6, 3)

        next_names = ["Spring Equinox","Summer Solstice","Autumn Equinox","Winter Solstice"]
        self.next_event      = next_names[idx]
        self.next_event_days = days_left

    def to_dict(self):
        return self.__dict__


class PanchangState:
    """Vedic five-limb timekeeping."""
    def __init__(self):
        self.tithi_num    = 0
        self.tithi_idx    = 0
        self.tithi_name   = "Pratipada"
        self.tithi_quality= "Nanda"
        self.paksha       = "Shukla"
        self.yoga_idx     = 0
        self.yoga_name    = "Vishkumbha"
        self.yoga_quality = "Inauspicious"
        self.karana_idx   = 0
        self.karana_name  = "Bava"
        self.vara_idx     = 0
        self.vara_name    = "Ravivara"
        self.day_ruler    = "Sun"
        self.ph_planet    = "Sun"
        self.ph_idx       = 0
        self.rahu_kalam_start  = "07:30"
        self.rahu_kalam_end    = "09:00"
        self.rahu_kalam_active = False

    def update(self, jd: float, now: datetime):
        sun_lon  = swe.calc_ut(jd, swe.SUN,  swe.FLG_SIDEREAL)[0][0]
        moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
        diff     = (moon_lon - sun_lon) % 360

        tnum = int(diff / 12)
        tidx = tnum % 15
        self.tithi_num    = tnum
        self.tithi_idx    = tidx
        self.tithi_name   = TITHI_NAMES[min(tidx, 14)]
        self.tithi_quality= TITHI_QUALITY[min(tidx, 14)]
        self.paksha       = "Shukla" if tnum < 15 else "Krishna"

        yoga_val = (sun_lon + moon_lon) % 360
        yidx = int(yoga_val / (360/27)) % 27
        self.yoga_idx     = yidx
        self.yoga_name    = YOGA_NAMES[yidx]
        self.yoga_quality = ("Inauspicious" if YOGA_NAMES[yidx] in INAUSPICIOUS_YOGAS
                             else "Auspicious")

        k = int(diff / 6)
        if k == 0: kidx = 10
        elif k >= 57: kidx = [7,8,9,10][min(k-57,3)]
        else: kidx = (k-1) % 7
        karana_names = ["Bava","Balava","Kaulava","Taitila","Garaja",
                        "Vanija","Vishti","Shakuni","Chatushpada","Naga","Kimstughna"]
        self.karana_idx  = kidx
        self.karana_name = karana_names[min(kidx, 10)]

        day_idx   = (now.weekday() + 1) % 7
        self.vara_idx  = day_idx
        self.vara_name = VARA_NAMES[day_idx]
        self.day_ruler = DAY_RULERS[day_idx]

        ruler_idx = PLANETARY_HOUR_SEQ.index(self.day_ruler)
        hours_since_sunrise = (now.hour + now.minute/60 - 6) % 24
        ph_idx = (ruler_idx + int(hours_since_sunrise)) % 7
        self.ph_planet = PLANETARY_HOUR_SEQ[ph_idx]
        self.ph_idx    = ph_idx

        rahu_part = {0:7,1:1,2:6,3:4,4:5,5:3,6:2}
        part  = rahu_part.get(now.weekday(), 1)
        start = 360 + (part-1)*90; end = start+90
        sh,sm = divmod(start,60); eh,em = divmod(end,60)
        cur   = now.hour*60+now.minute
        self.rahu_kalam_start  = f"{sh:02d}:{sm:02d}"
        self.rahu_kalam_end    = f"{eh:02d}:{em:02d}"
        self.rahu_kalam_active = bool(start <= cur < end)

    def to_dict(self):
        return self.__dict__


class ConditionsState:
    """
    Derived boolean and scalar conditions.
    These are what the tower's systems actually act on.
    """
    def __init__(self):
        # Planetary
        self.mercury_rx       = False
        self.venus_rx         = False
        self.mars_rx          = False
        self.jupiter_rx       = False
        self.saturn_rx        = False
        self.retrograde_count = 0
        self.retrograde_list  = []

        # Lunar
        self.moon_waxing      = False
        self.moon_full        = False
        self.moon_new         = False
        self.moon_supermoon   = False
        self.named_moon_active= False
        self.named_moon       = ""

        # Eclipse
        self.eclipse_active   = False
        self.eclipse_status   = "clear"

        # Panchang
        self.auspicious       = True    # tithi quality is auspicious
        self.yoga_auspicious  = True
        self.rahu_kalam_now   = False

        # Seasonal
        self.seasonal_palette = "autumn"
        self.lunar_saturation = 0.7     # 0.0 - 1.0

        # Potency — composite 0.0-1.0 describing overall celestial intensity
        # High: full moon + auspicious + no rx + eclipse approaching
        # Low: new moon + inauspicious + many rx
        self.potency          = 0.5

    def update(self, planets: dict, moon: MoonState, nodes: NodesState,
               season: SeasonState, panchang: PanchangState):
        rx = [name for name, p in planets.items() if p.retrograde
              and name not in ("Rahu","Ketu","Sun","Moon")]
        self.retrograde_list  = rx
        self.retrograde_count = len(rx)
        self.mercury_rx       = "Mercury" in rx
        self.venus_rx         = "Venus"   in rx
        self.mars_rx          = "Mars"    in rx
        self.jupiter_rx       = "Jupiter" in rx
        self.saturn_rx        = "Saturn"  in rx

        self.moon_waxing      = moon.is_waxing
        self.moon_full        = moon.is_full
        self.moon_new         = moon.is_new
        self.moon_supermoon   = moon.distance_label == "Supermoon"
        self.named_moon_active= bool(moon.named_moon)
        self.named_moon       = moon.named_moon

        self.eclipse_active   = nodes.eclipse_active
        self.eclipse_status   = nodes.eclipse_status

        self.auspicious       = panchang.tithi_quality in AUSPICIOUS_TITHIS
        self.yoga_auspicious  = panchang.yoga_quality == "Auspicious"
        self.rahu_kalam_now   = panchang.rahu_kalam_active

        self.seasonal_palette = season.palette_key
        self.lunar_saturation = season.saturation

        # Potency calculation
        score = 0.5
        score += (moon.illumination / 100) * 0.2   # full moon raises potency
        score -= self.retrograde_count * 0.04       # each rx lowers slightly
        score += 0.1 if self.auspicious else -0.1
        score += 0.05 if nodes.eclipse_status == "approaching" else 0
        score += 0.15 if nodes.eclipse_status in ("season","peak") else 0
        score -= 0.1 if self.rahu_kalam_now else 0
        self.potency = round(max(0.0, min(1.0, score)), 3)

    def to_dict(self):
        return {**self.__dict__}


class EntityAffinities:
    """
    Per-entity affinity scores based on current sky.
    1.0 = neutral, >1.0 = amplified, <1.0 = muted.
    Tower uses these to modulate entity behavior weights.
    """
    def __init__(self):
        self._scores = {name: 1.0 for name in ENTITY_AFFINITY}

    def update(self, sun: SunState, moon: MoonState, conditions: ConditionsState):
        for entity, config in ENTITY_AFFINITY.items():
            score = 1.0
            # Sun sign affinity
            if sun.sign_idx in config["affinity_signs"]:
                score += 0.25
            if sun.sign_idx in config["friction_signs"]:
                score -= 0.20
            # Moon sign affinity (stronger — moon moves faster, more immediate)
            if moon.sign_idx in config["affinity_signs"]:
                score += 0.35
            if moon.sign_idx in config["friction_signs"]:
                score -= 0.25
            # Full moon amplifies all entities slightly
            if conditions.moon_full:
                score += 0.10
            # Rahu Kalam is disruptive — slight friction for all
            if conditions.rahu_kalam_now:
                score -= 0.10
            self._scores[entity] = round(max(0.1, min(2.0, score)), 3)

    def get(self, entity: str) -> float:
        return self._scores.get(entity, 1.0)

    def all(self) -> dict:
        return dict(self._scores)

    def to_dict(self):
        return self._scores


class TriggerEngine:
    """
    Edge-event detection. Fires named triggers when threshold conditions
    are crossed. poll() returns the list of triggers since last call,
    then clears it.
    """
    def __init__(self):
        self._pending:  list = []
        self._prev:     dict = {}

    def _edge(self, key: str, current: bool, label: str):
        """Fire label if current became True and was previously False."""
        if current and not self._prev.get(key, False):
            self._pending.append(label)
        self._prev[key] = current

    def _changed(self, key: str, current, label_fn):
        """Fire label if value changed."""
        prev = self._prev.get(key)
        if prev is not None and prev != current:
            self._pending.append(label_fn(prev, current))
        self._prev[key] = current

    def update(self, conditions: ConditionsState, moon: MoonState,
               sun: SunState, panchang: PanchangState,
               season: SeasonState, planets: dict):

        # Moon phase transitions
        self._edge("moon_full",    conditions.moon_full,    "full_moon")
        self._edge("moon_new",     conditions.moon_new,     "new_moon")
        self._edge("moon_super",   conditions.moon_supermoon,"supermoon")
        if conditions.named_moon_active:
            self._edge(f"named_{conditions.named_moon}",
                       True, f"named_moon:{conditions.named_moon}")

        # Retrograde events
        self._edge("mercury_rx", conditions.mercury_rx, "mercury_retrograde_began")
        self._edge("venus_rx",   conditions.venus_rx,   "venus_retrograde_began")
        self._edge("mars_rx",    conditions.mars_rx,    "mars_retrograde_began")

        # Eclipse
        self._edge("eclipse_season", conditions.eclipse_active, "eclipse_season_entered")
        self._edge("eclipse_peak",
                   conditions.eclipse_status == "peak", "eclipse_peak")

        # Sign ingress — sun changing sign
        self._changed("sun_sign", sun.sign_idx,
                      lambda p,c: f"solar_ingress:{SIGN_NAMES[c]}")

        # Moon sign ingress
        self._changed("moon_sign", moon.sign_idx,
                      lambda p,c: f"lunar_ingress:{SIGN_NAMES[c]}")

        # Season change
        self._changed("season", season.idx,
                      lambda p,c: f"season_entered:{SEASON_NAMES[c]}")

        # Rahu Kalam
        self._edge("rahu_kalam", conditions.rahu_kalam_now, "rahu_kalam_began")

        # Planetary hour change
        self._changed("ph_planet", panchang.ph_planet,
                      lambda p,c: f"planetary_hour:{c}")

        # Auspiciousness flip
        self._edge("inauspicious", not conditions.auspicious, "inauspicious_window")

    def poll(self) -> list:
        """Returns triggers since last poll, then clears."""
        out = list(self._pending)
        self._pending.clear()
        return out

    def peek(self) -> list:
        """Returns triggers without clearing."""
        return list(self._pending)

    def to_dict(self):
        return {"pending": self._pending, "history_size": len(self._prev)}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class MachinaHorologica:
    """
    The sky, bundled.

    sky = MachinaHorologica()
    sky.update()

    # Accessors
    sky.time.utc
    sky.moon.phase_name
    sky.moon.illumination
    sky.sun.sign_name
    sky.planets["Mercury"].retrograde
    sky.planets["Jupiter"].sign_name
    sky.nodes.eclipse_status
    sky.season.saturation
    sky.season.palette_key
    sky.panchang.tithi_name
    sky.panchang.rahu_kalam_active
    sky.conditions.mercury_rx
    sky.conditions.potency
    sky.conditions.auspicious
    sky.entities.get("archivist")      # affinity score
    sky.entities.all()                 # all scores dict
    sky.triggers.poll()                # edge events since last poll
    sky.to_json()                      # full serialised state
    sky.write()                        # write to ~/ArcaCognitorium/.arca/celestial_state.json
    """

    def __init__(self):
        self.time       = TimeState()
        self.moon       = MoonState()
        self.sun        = SunState()
        self.nodes      = NodesState()
        self.season     = SeasonState()
        self.panchang   = PanchangState()
        self.conditions = ConditionsState()
        self.entities   = EntityAffinities()
        self.triggers   = TriggerEngine()

        self.planets: dict[str, PlanetState] = {}
        for name, pid in PLANET_IDS.items():
            if name != "Rahu":
                self.planets[name] = PlanetState(name)
        # Ketu is derived from Rahu — add as a pseudo-planet
        self.planets["Ketu"] = PlanetState("Ketu")

        self._cycle     = 0
        self._tick      = 0
        self._last_heavy= 0.0  # unix timestamp of last heavy recalc

    def update(self, force: bool = False):
        """
        Full update. Calculates everything from Swiss Ephemeris.
        Call this every second from your timer.
        Heavy calculations (planets, panchang) run every 60s.
        Clock and derived conditions run every tick.
        """
        now = datetime.now(timezone.utc)
        self._tick += 1

        # Always update time
        self.time.update(now)
        jd = self.time.jd

        heavy = force or (time.time() - self._last_heavy >= 59)

        if heavy:
            self._cycle += 1
            self._last_heavy = time.time()

            # Moon & Sun
            self.moon.update(jd, now)
            self.sun.update(jd)
            self.nodes.update(jd)

            # All planets
            for name, pid in PLANET_IDS.items():
                if name in ("Rahu","Ketu"): continue
                self.planets[name].update(jd, pid)

            # Ketu — mirror of Rahu
            self.planets["Ketu"].sign_idx   = (self.nodes.rahu_sign_idx + 6) % 12
            self.planets["Ketu"].sign_name  = SIGN_NAMES[self.planets["Ketu"].sign_idx]
            self.planets["Ketu"].sign_glyph = SIGN_GLYPHS[self.planets["Ketu"].sign_idx]
            self.planets["Ketu"].longitude  = self.nodes.ketu_longitude
            self.planets["Ketu"].degree     = self.nodes.ketu_degree

            # Panchang
            self.panchang.update(jd, now)

            # Season
            self.season.update(now, self.moon.illumination)

        # Conditions always derived fresh (cheap)
        self.conditions.update(
            self.planets, self.moon, self.nodes, self.season, self.panchang)

        # Entity affinities
        self.entities.update(self.sun, self.moon, self.conditions)

        # Trigger detection
        self.triggers.update(
            self.conditions, self.moon, self.sun,
            self.panchang, self.season, self.planets)

    def to_dict(self) -> dict:
        """Full serialisable state."""
        return {
            "meta": {
                "ts":               self.time.iso,
                "daemon_version":   VERSION,
                "calculation_cycle":self._cycle,
                "tick":             self._tick,
            },
            "time":       self.time.to_dict(),
            "moon":       self.moon.to_dict(),
            "sun":        self.sun.to_dict(),
            "nodes":      self.nodes.to_dict(),
            "season":     self.season.to_dict(),
            "panchang":   self.panchang.to_dict(),
            "conditions": self.conditions.to_dict(),
            "entities":   self.entities.to_dict(),
            "triggers":   self.triggers.to_dict(),
            "planets":    {name: p.to_dict() for name,p in self.planets.items()},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def write(self):
        """Atomic write to ~/ArcaCognitorium/.arca/celestial_state.json"""
        ARCA_DIR.mkdir(exist_ok=True)
        tmp = ARCA_DIR / "machina_horologica.tmp"
        with open(tmp, "w") as f:
            f.write(self.to_json())
        tmp.replace(STATE_PATH)

    def summary(self) -> str:
        """One-line human-readable summary."""
        return (
            f"☉ {self.sun.sign_name[:3]}  "
            f"{MOON_PHASE_GLYPHS[self.moon.phase_idx]} {self.moon.phase_name}  "
            f"{self.moon.illumination:.0f}%  "
            f"☽ {self.moon.sign_name[:3]}  "
            f"{'℞ ' + str(self.conditions.retrograde_count) if self.conditions.retrograde_count else '→ direct'}  "
            f"{self.season.name}  sat:{self.season.saturation:.2f}  "
            f"potency:{self.conditions.potency:.2f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DAEMON / CLI
# ─────────────────────────────────────────────────────────────────────────────

def run_daemon():
    """Write state every second. Runs until killed."""
    sky = MachinaHorologica()
    print(f"CELESTIAL DAEMON  v{VERSION}")
    print(f"Writing to: {STATE_PATH}")
    print("Ctrl+C to stop.\n")

    try:
        while True:
            sky.update()
            sky.write()
            triggers = sky.triggers.poll()
            if triggers:
                ts = sky.time.utc
                for t in triggers:
                    print(f"  [{ts}] TRIGGER: {t}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDaemon stopped.")


def run_once():
    """Single calculation, write, print summary."""
    sky = MachinaHorologica()
    sky.update(force=True)
    sky.write()
    print(sky.to_json())


def run_watch():
    """Pretty-print live state to terminal."""
    sky = MachinaHorologica()
    try:
        while True:
            sky.update()
            sky.write()
            os.system("clear")
            print(f"  MACHINA HOROLOGICA  v{VERSION}  —  {sky.time.utc} UTC")
            print(f"  {sky.summary()}")
            print()
            print(f"  MOON    {sky.moon.phase_glyph} {sky.moon.phase_name}"
                  f"  ·  {sky.moon.illumination:.1f}%"
                  f"  ·  {sky.moon.sign_name}"
                  f"  ·  {sky.moon.nakshatra_name}"
                  f"  ·  {sky.moon.distance_label}")
            print(f"  SUN     ☉ {sky.sun.sign_name}  ·  {sky.sun.nakshatra_name}")
            print(f"  NODES   ☊ {sky.nodes.rahu_sign_name}"
                  f"  ·  eclipse: {sky.nodes.eclipse_status}"
                  f"  ({sky.nodes.eclipse_dist:.1f}°)")
            print(f"  SEASON  {sky.season.name}"
                  f"  ·  {sky.season.days_until}d until {sky.season.next_event}"
                  f"  ·  sat {sky.season.saturation:.2f}")
            print()
            print(f"  TITHI   {sky.panchang.tithi_name}"
                  f"  ·  {sky.panchang.paksha}"
                  f"  ·  {sky.panchang.tithi_quality}")
            print(f"  VARA    {sky.panchang.vara_name}"
                  f"  ·  ruled by {sky.panchang.day_ruler}")
            print(f"  YOGA    {sky.panchang.yoga_name}"
                  f"  ·  {sky.panchang.yoga_quality}")
            print(f"  HOUR    {sky.panchang.ph_planet}'s hour"
                  f"  ·  Rahu Kalam: "
                  f"{'ACTIVE' if sky.panchang.rahu_kalam_active else sky.panchang.rahu_kalam_start+'-'+sky.panchang.rahu_kalam_end}")
            print()
            print(f"  CONDITIONS")
            print(f"    potency:    {sky.conditions.potency:.3f}")
            print(f"    auspicious: {sky.conditions.auspicious}")
            print(f"    rx count:   {sky.conditions.retrograde_count}"
                  + (f"  ({', '.join(sky.conditions.retrograde_list)})"
                     if sky.conditions.retrograde_list else ""))
            print(f"    palette:    {sky.conditions.seasonal_palette}"
                  f"  ·  saturation: {sky.conditions.lunar_saturation:.3f}")
            print()
            print(f"  ENTITY AFFINITIES")
            for name, score in sorted(sky.entities.all().items()):
                bar_len = int((score - 0.5) * 20)
                bar = ("+" * max(0, bar_len)) if score >= 1.0 else ("-" * max(0, -bar_len))
                print(f"    {name:<18} {score:.3f}  {bar}")
            print()
            print(f"  PLANETS")
            for name, p in sky.planets.items():
                if name in ("Uranus","Neptune","Pluto","Ketu"): continue
                rx = " ℞" if p.retrograde else "  "
                phase = f"  {p.phase_name}" if p.phase_name else ""
                print(f"    {name:<10} {p.sign_name:<14}{rx}{phase}")

            triggers = sky.triggers.poll()
            if triggers:
                print()
                print(f"  TRIGGERS")
                for t in triggers:
                    print(f"    ◆ {t}")

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nWatch stopped.")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--once" in args:
        run_once()
    elif "--watch" in args:
        run_watch()
    else:
        run_daemon()
