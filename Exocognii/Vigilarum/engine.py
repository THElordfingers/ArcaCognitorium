"""
 ________  ____  _____   ______  _____  ____  _____  ________                     
|_   __  ||_   \|_   _|.' ___  ||_   _||_   \|_   _||_   __  |                    
  | |_ \_|  |   \ | | / .'   \_|  | |    |   \ | |    | |_ \_|   _ .--.   _   __  
  |  _| _   | |\ \| | | |   ____  | |    | |\ \| |    |  _| _   [ '/'`\ \[ \ [  ] 
 _| |__/ | _| |_\   |_\ `.___]  |_| |_  _| |_\   |_  _| |__/ | _ | \__/ | \ '/ /  
|________||_____|\____|`._____.'|_____||_____|\____||________|(_)| ;.__/[\_:  /   
                                                                [__|     \__.'    



VIGILARUM OMNIA — Calculation Engine
All astronomical calculations via Swiss Ephemeris.
"""

import swisseph as swe
import math
from datetime import datetime, timezone

swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANET_IDS = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Uranus":  swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto":   swe.PLUTO,
    "Rahu":    swe.MEAN_NODE,
}

ROMAN = {
    1000:"M",900:"CM",500:"D",400:"CD",100:"C",90:"XC",
    50:"L",40:"XL",10:"X",9:"IX",5:"V",4:"IV",1:"I",
}

def to_roman(n: int) -> str:
    if n <= 0: return "O"
    r = ""
    for val, num in ROMAN.items():
        while n >= val:
            r += num; n -= val
    return r

def now_jd() -> float:
    now = datetime.now(timezone.utc)
    return swe.julday(now.year, now.month, now.day,
                      now.hour + now.minute/60 + now.second/3600)

def get_planet(jd: float, pid: int):
    """Returns (sign_idx, degree_in_sign, retrograde, absolute_lon)"""
    r = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
    lon = r[0]; spd = r[3]
    return int(lon/30) % 12, lon % 30, spd < 0, lon

def get_moon_phase(jd: float):
    """Returns (phase_idx 0-7, illumination 0-100, elongation 0-360)"""
    sun_lon  = swe.calc_ut(jd, swe.SUN,  swe.FLG_SIDEREAL)[0][0]
    moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    angle = (moon_lon - sun_lon) % 360
    illumination = (1 - math.cos(math.radians(angle))) / 2 * 100
    return int(angle / 45) % 8, illumination, angle

def get_nakshatra(lon: float):
    """Returns (nakshatra_idx 0-26, pada 1-4)"""
    sz = 360 / 27
    return int(lon / sz) % 27, int((lon % sz) / (sz / 4)) + 1

def get_tithi(jd: float):
    sun_lon  = swe.calc_ut(jd, swe.SUN,  swe.FLG_SIDEREAL)[0][0]
    moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    diff = (moon_lon - sun_lon) % 360
    tnum = int(diff / 12)
    return tnum, tnum % 15, "Shukla" if tnum < 15 else "Krishna"

def get_yoga(jd: float):
    sun_lon  = swe.calc_ut(jd, swe.SUN,  swe.FLG_SIDEREAL)[0][0]
    moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    return int(((sun_lon + moon_lon) % 360) / (360/27)) % 27

def get_karana(jd: float):
    sun_lon  = swe.calc_ut(jd, swe.SUN,  swe.FLG_SIDEREAL)[0][0]
    moon_lon = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    k = int(((moon_lon - sun_lon) % 360) / 6)
    if k == 0: return 10
    if k >= 57: return [7,8,9,10][min(k-57, 3)]
    return (k - 1) % 7

def get_planetary_hour(now: datetime):
    from data import PLANETARY_HOUR_SEQ, DAY_RULERS
    day_idx   = (now.weekday() + 1) % 7  # Sun=0
    day_ruler = DAY_RULERS[day_idx]
    ruler_idx = PLANETARY_HOUR_SEQ.index(day_ruler)
    hours_since_sunrise = (now.hour + now.minute/60 - 6) % 24
    planet = PLANETARY_HOUR_SEQ[(ruler_idx + int(hours_since_sunrise)) % 7]
    return planet, day_ruler, day_idx

def get_inner_planet_phase(jd: float, pid: int):
    sun_lon = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    pla_lon = swe.calc_ut(jd, pid,     swe.FLG_SIDEREAL)[0][0]
    diff    = (pla_lon - sun_lon) % 360
    if diff > 180: diff -= 360
    elong   = abs(diff)
    morning = diff < 0
    return ("Morning Star" if morning else "Evening Star",
            "🌅" if morning else "🌆",
            elong,
            "Rises before the Sun" if morning else "Sets after the Sun")

def get_eclipse_proximity(jd: float):
    sun_lon  = swe.calc_ut(jd, swe.SUN,       swe.FLG_SIDEREAL)[0][0]
    rahu_lon = swe.calc_ut(jd, swe.MEAN_NODE,  swe.FLG_SIDEREAL)[0][0]
    ketu_lon = (rahu_lon + 180) % 360
    d_r = abs((sun_lon - rahu_lon + 180) % 360 - 180)
    d_k = abs((sun_lon - ketu_lon + 180) % 360 - 180)
    dist = min(d_r, d_k)
    return dist < 18, dist, max(0, (18 - dist) / 18 * 100)

def get_moon_distance(jd: float):
    r = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SPEED)[0]
    dist_km = r[2] * 149597870.7
    pct = (dist_km - 384400) / 384400 * 100
    if pct < -3:  return int(dist_km), pct, "Supermoon", "At perigee", "🌕"
    if pct >  3:  return int(dist_km), pct, "Micromoon", "At apogee",  "🔵"
    return int(dist_km), pct, "Average", "Near mean distance", "⚪"

def get_aspects(jd: float):
    planets = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"]
    lons = {n: swe.calc_ut(jd, PLANET_IDS[n], swe.FLG_SIDEREAL)[0][0] for n in planets}
    defs = {"Conj":(0,8),"Opp":(180,8),"Trine":(120,6),"Square":(90,6),"Sextile":(60,4)}
    found = []
    names = list(lons.keys())
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = names[i], names[j]
            diff = abs((lons[a] - lons[b] + 180) % 360 - 180)
            for asp, (target, orb) in defs.items():
                if abs(diff - target) <= orb:
                    found.append((a, b, asp, round(diff, 1)))
    return found

def get_rahu_kalam(now: datetime):
    rahu_part = {0:7, 1:1, 2:6, 3:4, 4:5, 5:3, 6:2}
    part  = rahu_part.get(now.weekday(), 1)
    start = 360 + (part - 1) * 90
    end   = start + 90
    sh, sm = divmod(start, 60)
    eh, em = divmod(end,   60)
    cur = now.hour * 60 + now.minute
    return f"{sh:02d}:{sm:02d}", f"{eh:02d}:{em:02d}", start <= cur < end

def get_sidereal_time(jd: float):
    gst = swe.sidtime(jd)
    h = int(gst) % 24
    m = int((gst - int(gst)) * 60)
    s = int(((gst - int(gst)) * 60 - m) * 60)
    return h, m, s

def get_season(now: datetime):
    mo, dy = now.month, now.day
    if (mo == 12 and dy >= 21) or mo <= 2 or (mo == 3 and dy < 20):
        idx = 0
        target = datetime(now.year + (1 if mo == 12 else 0), 3, 20, tzinfo=timezone.utc)
    elif (mo == 3 and dy >= 20) or mo <= 5 or (mo == 6 and dy < 21):
        idx = 1
        target = datetime(now.year, 6, 21, tzinfo=timezone.utc)
    elif (mo == 6 and dy >= 21) or mo <= 8 or (mo == 9 and dy < 22):
        idx = 2
        target = datetime(now.year, 9, 22, tzinfo=timezone.utc)
    else:
        idx = 3
        target = datetime(now.year, 12, 21, tzinfo=timezone.utc)
    days = max(0, (target.replace(tzinfo=timezone.utc) -
                   now.replace(tzinfo=timezone.utc)).days)
    return idx, days

def days_to_next_phase(jd: float, target: float):
    for d in range(1, 32):
        _, _, angle = get_moon_phase(jd + d)
        if abs(angle - target) < 6:
            return d
    return "?"

def get_all_planet_lons(jd: float) -> dict:
    lons = {}
    for name, pid in PLANET_IDS.items():
        if name == "Ketu": continue
        lons[name] = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)[0][0]
    lons["Ketu"] = (lons["Rahu"] + 180) % 360
    return lons

def make_bar(value: float, total: float, width: int = 28) -> str:
    """░░░░████ — empty left, filled right."""
    pct    = max(0.0, min(1.0, value / total if total else 0))
    filled = int(pct * width)
    return '░' * (width - filled) + '█' * filled

def calculate_all(now: datetime) -> dict:
    """Full calculation. Returns state dict ready for JSON serialisation."""
    jd = swe.julday(now.year, now.month, now.day,
                    now.hour + now.minute/60 + now.second/3600)
    d = {
        "ts":  now.isoformat(),
        "jd":  jd,
    }

    # Moon
    ph_idx, illum, angle = get_moon_phase(jd)
    d.update({
        "moon_phase_idx":  ph_idx,
        "illumination":    illum,
        "moon_angle":      angle,
        "moon_cycle_day":  max(1, int(angle / (360/29.5))),
    })

    # Moon & Sun positions
    m_si, m_deg, _, m_lon = get_planet(jd, swe.MOON)
    s_si, s_deg, _, s_lon = get_planet(jd, swe.SUN)
    d.update({
        "moon_sign": m_si, "moon_deg": m_deg, "moon_lon": m_lon,
        "sun_sign":  s_si, "sun_deg":  s_deg, "sun_lon":  s_lon,
    })

    # All planets
    rx_list = []
    for name, pid in PLANET_IDS.items():
        if name in ("Sun","Moon","Rahu","Ketu"): continue
        si, deg, rx, lon = get_planet(jd, pid)
        k = name.lower()
        d[f"{k}_sign"] = si
        d[f"{k}_deg"]  = deg
        d[f"{k}_rx"]   = rx
        d[f"{k}_lon"]  = lon
        if rx: rx_list.append(name)
    d["retrograde_list"] = rx_list

    # Rahu / Ketu
    r_si, r_deg, _, r_lon = get_planet(jd, swe.MEAN_NODE)
    d.update({"rahu_sign": r_si, "rahu_deg": r_deg, "rahu_lon": r_lon})
    d["ketu_sign"] = (r_si + 6) % 12

    # Season
    s_idx, s_days = get_season(now)
    d["season_idx"] = s_idx
    d["season_days"] = s_days

    # Next moon
    d["days_to_next_moon"] = days_to_next_phase(
        jd, 180 if angle < 180 else 350)

    # Panchang
    tnum, tidx, paksha = get_tithi(jd)
    d.update({
        "tithi_num":  tnum,
        "tithi_idx":  tidx,
        "paksha":     paksha,
        "yoga_idx":   get_yoga(jd),
        "karana_idx": get_karana(jd),
    })

    # Planetary hour / day ruler
    planet_h, day_ruler, day_idx = get_planetary_hour(now)
    d["ph_planet"]  = planet_h
    d["day_ruler"]  = day_ruler
    d["day_idx"]    = day_idx

    # Inner planet phases
    merc_phase = get_inner_planet_phase(jd, swe.MERCURY)
    ven_phase  = get_inner_planet_phase(jd, swe.VENUS)
    d["mercury_phase_name"]  = merc_phase[0]
    d["mercury_phase_glyph"] = merc_phase[1]
    d["mercury_elong"]       = merc_phase[2]
    d["mercury_phase_desc"]  = merc_phase[3]
    d["venus_phase_name"]    = ven_phase[0]
    d["venus_phase_glyph"]   = ven_phase[1]
    d["venus_elong"]         = ven_phase[2]
    d["venus_phase_desc"]    = ven_phase[3]

    # Eclipse
    in_ec, ec_dist, ec_pct = get_eclipse_proximity(jd)
    d["eclipse_active"] = in_ec
    d["eclipse_dist"]   = ec_dist
    d["eclipse_pct"]    = ec_pct

    # Moon distance
    mk, mp, ml, mdd, mg = get_moon_distance(jd)
    d["moon_dist_km"]    = mk
    d["moon_dist_pct"]   = mp
    d["moon_dist_label"] = ml
    d["moon_dist_desc"]  = mdd
    d["moon_dist_glyph"] = mg

    # Aspects
    d["aspects"] = get_aspects(jd)

    # Rahu Kalam
    rk_s, rk_e, rk_a = get_rahu_kalam(now)
    d["rahu_kalam_start"]  = rk_s
    d["rahu_kalam_end"]    = rk_e
    d["rahu_kalam_active"] = rk_a

    # Sidereal time
    st_h, st_m, st_s = get_sidereal_time(jd)
    d["sidereal_h"] = st_h
    d["sidereal_m"] = st_m
    d["sidereal_s"] = st_s

    # All longitudes (for visuals)
    d["all_lons"] = get_all_planet_lons(jd)

    return d
