#!/usr/bin/env python3
"""
vigilarum_install.py
Run from ~/ArcaCognitorium/Exocognii/Vigilarum/
Writes all source files for Vigilarum Omnia v2.
Usage: python3 vigilarum_install.py
"""
import os, sys

BASE = os.path.dirname(os.path.abspath(__file__))

FILES = {}

# =============================================================================
FILES["engine.py"] = r'''# engine.py — Vigilarum Omnia v2
import math, datetime
import swisseph as swe
from data import (
    LAT, LON, AYANAMSHA, PLANETS, RAHU_ID, RAHU_SYMBOL, KETU_SYMBOL,
    SIGNS, SIGN_SYMBOLS, NAKSHATRAS, NAKSHATRA_LORDS, NAKSHATRA_SPAN,
    TITHIS, VARAS, VARA_LORDS, YOGAS, KARANAS, RAHU_KALAM_OFFSETS,
    CHALDEAN_ORDER, DAY_RULER_HOUR1, SEASON_REGISTERS, ASPECTS, moon_phase_name,
)

swe.set_sid_mode(AYANAMSHA)
SUNRISE_FALLBACK = 6 * 60

def _jd():
    n = datetime.datetime.utcnow()
    return swe.julday(n.year, n.month, n.day, n.hour + n.minute/60 + n.second/3600)

def _n(d): return d % 360.0
def _si(lon): return int(_n(lon) / 30.0)
def _sd(lon): return _n(lon) % 30.0
def _ni(lon): return int(_n(lon) / NAKSHATRA_SPAN)
def _nd(lon): return _n(lon) % NAKSHATRA_SPAN
def _dms(deg):
    d=int(deg); m=int((deg-d)*60); s=int(((deg-d)*60-m)*60)
    return f"{d}\u00b0 {m}\' {s}\""

def _calc_planets(jd):
    r = {}
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    for pid, name, sym in PLANETS:
        pos, _ = swe.calc_ut(jd, pid, flags)
        lon = _n(pos[0]); retro = pos[3] < 0; k = name.lower()
        r[f"{k}_lon"]=lon; r[f"{k}_sign"]=SIGNS[_si(lon)]
        r[f"{k}_sign_sym"]=SIGN_SYMBOLS[_si(lon)]
        r[f"{k}_sign_deg"]=round(_sd(lon),4)
        r[f"{k}_nakshatra"]=NAKSHATRAS[_ni(lon)]
        r[f"{k}_nak_lord"]=NAKSHATRA_LORDS[_ni(lon)]
        r[f"{k}_nak_deg"]=round(_nd(lon),4)
        r[f"{k}_retrograde"]=retro; r[f"{k}_symbol"]=sym; r[f"{k}_dms"]=_dms(_sd(lon))
    pos, _ = swe.calc_ut(jd, RAHU_ID, flags)
    rl = _n(pos[0])
    r["rahu_lon"]=rl; r["rahu_sign"]=SIGNS[_si(rl)]; r["rahu_sign_sym"]=SIGN_SYMBOLS[_si(rl)]
    r["rahu_sign_deg"]=round(_sd(rl),4); r["rahu_nakshatra"]=NAKSHATRAS[_ni(rl)]
    r["rahu_nak_lord"]=NAKSHATRA_LORDS[_ni(rl)]; r["rahu_nak_deg"]=round(_nd(rl),4)
    r["rahu_retrograde"]=True; r["rahu_symbol"]=RAHU_SYMBOL; r["rahu_dms"]=_dms(_sd(rl))
    kl = _n(rl + 180.0)
    r["ketu_lon"]=kl; r["ketu_sign"]=SIGNS[_si(kl)]; r["ketu_sign_sym"]=SIGN_SYMBOLS[_si(kl)]
    r["ketu_sign_deg"]=round(_sd(kl),4); r["ketu_nakshatra"]=NAKSHATRAS[_ni(kl)]
    r["ketu_nak_lord"]=NAKSHATRA_LORDS[_ni(kl)]; r["ketu_nak_deg"]=round(_nd(kl),4)
    r["ketu_retrograde"]=True; r["ketu_symbol"]=KETU_SYMBOL; r["ketu_dms"]=_dms(_sd(kl))
    return r

def _moon_phase(sun_lon, moon_lon):
    diff = _n(moon_lon - sun_lon)
    illum = (1 - math.cos(math.radians(diff))) / 2 * 100
    return {"moon_phase_angle":round(diff,4),"moon_illumination":round(illum,2),
            "moon_phase_name":moon_phase_name(diff),"moon_waxing":diff < 180.0}

def _moon_distance(jd):
    pos, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
    km = pos[2] * 149_597_870.7
    pct = (km - 356_500) / (406_700 - 356_500) * 100
    return {"moon_distance_km":round(km,0),
            "moon_distance_pct":round(max(0.0,min(100.0,pct)),1),
            "moon_proximity":"Perigee" if km < 384_400 else "Apogee"}

def _panchang(jd, sun_lon, moon_lon):
    ta = _n(moon_lon - sun_lon)
    ti = min(int(ta/12.0), 29); vi = int(jd + 1.5) % 7; ni = _ni(moon_lon)
    yi = int(_n(sun_lon + moon_lon) / NAKSHATRA_SPAN) % 27; ki = int(ta / 6.0) % 11
    return {
        "tithi_index":ti,"tithi_num":ti+1,"tithi_name":TITHIS[ti],
        "tithi_progress":round((ta%12.0)/12.0*100,1),
        "vara_index":vi,"vara_name":VARAS[vi],"vara_lord":VARA_LORDS[vi],
        "nakshatra_index":ni,"nakshatra_name":NAKSHATRAS[ni],
        "nakshatra_lord":NAKSHATRA_LORDS[ni],
        "nakshatra_progress":round((_nd(moon_lon)/NAKSHATRA_SPAN)*100,1),
        "yoga_index":yi,"yoga_name":YOGAS[yi],
        "karana_index":ki,"karana_name":KARANAS[ki],
    }

def _rahu_kalam(vi, sm):
    start = sm + (RAHU_KALAM_OFFSETS[vi]-1)*90; end = start+90
    now = datetime.datetime.now(); nm = now.hour*60+now.minute
    def fmt(m): h,mn=divmod(int(m),60); return f"{h:02d}:{mn:02d}"
    return {"rahu_kalam_start":fmt(start),"rahu_kalam_end":fmt(end),"rahu_kalam_active":start<=nm<end}

def _planetary_hour(vi, sm):
    now = datetime.datetime.now(); nm = now.hour*60+now.minute
    hn = max(0,int((nm-sm)/60))%24
    pi = (DAY_RULER_HOUR1.get(VARA_LORDS[vi],0)+hn)%7; hs = sm + hn*60
    def fmt(m): h,mn=divmod(int(m)%1440,60); return f"{h:02d}:{mn:02d}"
    return {"planetary_hour_num":hn+1,"planetary_hour_planet":CHALDEAN_ORDER[pi],
            "planetary_hour_start":fmt(hs),"planetary_hour_end":fmt(hs+60)}

def _sun_times():
    sm=SUNRISE_FALLBACK; ss=sm+720; dl=ss-sm
    def fmt(m): h,mn=divmod(int(m)%1440,60); return f"{h:02d}:{mn:02d}"
    return {"sunrise":fmt(sm),"sunset":fmt(ss),"sunrise_min":sm,
            "day_length":f"{dl//60}h {dl%60}m","day_length_min":dl}

def _aspects(lons):
    keys=["sun","moon","mars","mercury","jupiter","venus","saturn","uranus","neptune","pluto","rahu","ketu"]
    active=[]
    for i,p1 in enumerate(keys):
        for p2 in keys[i+1:]:
            l1,l2=lons.get(f"{p1}_lon"),lons.get(f"{p2}_lon")
            if l1 is None or l2 is None: continue
            diff=abs(_n(l1-l2)); diff=min(diff,360-diff)
            for an,aa,orb in ASPECTS:
                if abs(diff-aa)<=orb:
                    active.append({"p1":p1.capitalize(),"p2":p2.capitalize(),"aspect":an,"orb":round(abs(diff-aa),2)})
    active.sort(key=lambda x:x["orb"])
    parts=[f"{a['p1']} {a['aspect']} {a['p2']} ({a['orb']:.1f}\u00b0)" for a in active[:5]]
    nxt=(f"{active[0]['p1']} {active[0]['aspect']} {active[0]['p2']} \u2014 {active[0]['orb']:.2f}\u00b0 orb"
         if active else "")
    return {"aspects_active":active[:8],
            "aspects_summary":" \u00b7 ".join(parts) if parts else "No major aspects",
            "aspects_next":nxt,"aspects_count":len(active)}

def _eclipse(moon_lon, rahu_lon):
    kl=_n(rahu_lon+180.0)
    dr=abs(_n(moon_lon-rahu_lon)); dr=min(dr,360-dr)
    dk=abs(_n(moon_lon-kl)); dk=min(dk,360-dk); md=min(dr,dk)
    return {"eclipse_dist_rahu":round(dr,2),"eclipse_dist_ketu":round(dk,2),
            "eclipse_nearest":"Rahu" if dr<dk else "Ketu","eclipse_min_dist":round(md,2),
            "eclipse_risk":"High" if md<12 else ("Medium" if md<20 else "Low")}

def _season(sun_lon):
    lon=_n(sun_lon)
    if lon<90:    s,p,ns,dn="Spring",lon/90,"Summer",90-lon
    elif lon<180: s,p,ns,dn="Summer",(lon-90)/90,"Autumn",180-lon
    elif lon<270: s,p,ns,dn="Autumn",(lon-180)/90,"Winter",270-lon
    else:         s,p,ns,dn="Winter",(lon-270)/90,"Spring",360-lon
    return {"season":s,"season_progress":round(p*100,1),"season_next":ns,
            "season_days_to_next":round(dn,1),"season_boundary_near":dn<7,
            "season_register":SEASON_REGISTERS[s]}

def _time_fields():
    now=datetime.datetime.now(); utc=datetime.datetime.utcnow()
    return {"time_local":now.strftime("%H:%M:%S"),"time_date":now.strftime("%Y-%m-%d"),
            "time_weekday":now.strftime("%A"),"time_utc":utc.strftime("%H:%M UTC"),
            "time_timestamp":now.isoformat()}

def calculate_all() -> dict:
    jd=_jd(); planets=_calc_planets(jd)
    sun_lon=planets["sun_lon"]; moon_lon=planets["moon_lon"]; rahu_lon=planets["rahu_lon"]
    mp=_moon_phase(sun_lon,moon_lon); md=_moon_distance(jd)
    pa=_panchang(jd,sun_lon,moon_lon); st=_sun_times()
    rk=_rahu_kalam(pa["vara_index"],st["sunrise_min"])
    ph=_planetary_hour(pa["vara_index"],st["sunrise_min"])
    asp=_aspects(planets); ec=_eclipse(moon_lon,rahu_lon)
    se=_season(sun_lon); tf=_time_fields()
    sky=(f"{SIGNS[_si(sun_lon)]} Sun \u00b7 {mp['moon_phase_name']} \u00b7 "
         f"{pa['nakshatra_name']} \u00b7 {se['season']}")
    state={}
    for d in [planets,mp,md,pa,st,rk,ph,asp,ec,se,tf]: state.update(d)
    state["sky_summary"]=sky
    return state
'''

# =============================================================================
FILES["state.py"] = r'''# state.py — Vigilarum Omnia v2
import json, os, tempfile, pathlib

STATE_DIR    = pathlib.Path.home() / ".vigilarum"
STATE_FILE   = STATE_DIR / "state.json"
DISPLAYS_DIR = STATE_DIR / "displays"

def ensure_dirs():
    STATE_DIR.mkdir(exist_ok=True)
    DISPLAYS_DIR.mkdir(exist_ok=True)

def write_state(data: dict):
    ensure_dirs()
    fd, tmp = tempfile.mkstemp(dir=STATE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, STATE_FILE)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise

def read_state() -> dict | None:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None

def state_mtime() -> float:
    try: return STATE_FILE.stat().st_mtime
    except OSError: return 0.0

def display_path(did: int): return DISPLAYS_DIR / f"display_{did}.json"

def read_display(did: int) -> dict:
    try:
        with open(display_path(did), "r", encoding="utf-8") as f:
            d = json.load(f)
        if not isinstance(d, dict): raise ValueError
        d.setdefault("widgets", []); d.setdefault("columns", 3)
        return d
    except Exception:
        return {"widgets": [], "columns": 3}

def write_display(did: int, cfg: dict):
    ensure_dirs()
    fd, tmp = tempfile.mkstemp(dir=DISPLAYS_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False)
        os.replace(tmp, display_path(did))
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise

def toggle_widget(did: int, wid: str) -> bool:
    cfg = read_display(did)
    if wid in cfg["widgets"]:
        cfg["widgets"].remove(wid); write_display(did, cfg); return False
    else:
        cfg["widgets"].append(wid); write_display(did, cfg); return True

def set_columns(did: int, columns: int):
    from data import VALID_COLUMNS
    if columns not in VALID_COLUMNS: return
    cfg = read_display(did); cfg["columns"] = columns; write_display(did, cfg)

def widget_assignments() -> dict:
    from data import MAX_DISPLAYS
    a = {}
    for d in range(1, MAX_DISPLAYS+1):
        for wid in read_display(d)["widgets"]:
            a.setdefault(wid, []).append(d)
    return a

def display_widget_set(did: int) -> set:
    return set(read_display(did)["widgets"])
'''

# =============================================================================
FILES["widgets.py"] = r'''# widgets.py — Vigilarum Omnia v2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QDrag, QPixmap
import painters
from data import (
    C_BG, C_PANEL, C_BORDER, C_GOLD, C_GOLD_DIM,
    C_TEXT, C_TEXT_DIM, C_TEAL, C_RED, C_GREEN, C_WHITE,
    FONT_BODY, FONT_SIZE, FONT_SMALL, FONT_LARGE, FONT_TITLE,
    BODY_NAMES,
)

AWAIT = "Awaiting data\u2026"
_LTO = 22   # label top offset px


class ArcaneCard(QWidget):
    SECTION_LABEL = ""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(160, 120)
        self._state = None

    def update_data(self, state):
        self._state = state; self._on_state(state)

    def _on_state(self, state): pass

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(C_PANEL))
        pen = QPen(QColor(C_BORDER)); pen.setWidth(1); p.setPen(pen)
        p.drawRect(self.rect().adjusted(0,0,-1,-1))
        if self.SECTION_LABEL:
            p.setFont(QFont(FONT_BODY, FONT_SMALL-1)); p.setPen(QColor(C_GOLD_DIM))
            p.drawText(self.rect().adjusted(6,4,-6,0),
                       Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft,
                       self.SECTION_LABEL.upper())
        p.end()


class TextCard(ArcaneCard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._content = QWidget(self)
        self._cl = QVBoxLayout(self._content)
        self._cl.setContentsMargins(8, _LTO, 8, 8); self._cl.setSpacing(3)
        self._build_labels()

    def _build_labels(self): pass

    def resizeEvent(self, e):
        self._content.setGeometry(self.rect()); super().resizeEvent(e)

    def _lbl(self, text="", size=FONT_SIZE, color=C_TEXT, bold=False):
        l = QLabel(text)
        l.setFont(QFont(FONT_BODY, size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        l.setStyleSheet(f"color:{color};background:transparent;"); l.setWordWrap(True)
        return l

    def _field(self, label_text, value_text=""):
        """Returns a row QHBoxLayout with a dim label and a value label."""
        row = QHBoxLayout(); row.setSpacing(6)
        lbl = self._lbl(label_text, FONT_SMALL, C_TEXT_DIM)
        lbl.setFixedWidth(110)
        val = self._lbl(value_text, FONT_SMALL, C_TEXT)
        row.addWidget(lbl); row.addWidget(val, stretch=1)
        return row, val

    def _dim(self, t=""): return self._lbl(t, FONT_SMALL, C_TEXT_DIM)
    def _gold(self, t=""): return self._lbl(t, FONT_LARGE, C_GOLD, bold=True)


class VisualCard(ArcaneCard):
    def __init__(self, parent=None): super().__init__(parent)

    def _draw_content(self, painter, rect, state): pass

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, _LTO, -2, -2)
        try: self._draw_content(p, rect, self._state)
        except Exception as e:
            p.setPen(QColor(C_RED)); p.setFont(QFont(FONT_BODY, FONT_SMALL))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"\u26a0 {e}")
        p.end()

    def _on_state(self, state): self.update()


# --- Planet card base ---
class _PlanetCard(TextCard):
    PLANET_KEY = "sun"
    IS_NODE = False

    def _build_labels(self):
        self._val = self._gold()
        self._cl.addWidget(self._val)
        rows = [
            ("Sign:", ""),("Degree in sign:", ""),
            ("Nakshatra:", ""),("Nakshatra lord:", ""),
            ("Nakshatra degree:", ""),
        ]
        self._fields = {}
        for label, _ in rows:
            row, val = self._field(label)
            self._cl.addLayout(row)
            self._fields[label] = val
        self._retro = self._lbl("", FONT_SMALL, C_TEAL)
        self._cl.addWidget(self._retro)
        self._cl.addStretch()

    def _on_state(self, s):
        if not s: self._val.setText(AWAIT); return
        k = self.PLANET_KEY
        sign = s.get(f"{k}_sign","—"); sym = s.get(f"{k}_symbol","")
        self._val.setText(f"{sym}  {sign}")
        self._fields["Sign:"].setText(sign)
        self._fields["Degree in sign:"].setText(s.get(f"{k}_dms","—"))
        self._fields["Nakshatra:"].setText(s.get(f"{k}_nakshatra","—"))
        self._fields["Nakshatra lord:"].setText(s.get(f"{k}_nak_lord","—"))
        self._fields["Nakshatra degree:"].setText(f"{s.get(f'{k}_nak_deg',0):.2f}\u00b0")
        retro = s.get(f"{k}_retrograde", False)
        self._retro.setText("\u211e Retrograde" if retro else "")

def _make_planet(key, name, is_node=False):
    return type(f"Card_{name}", (_PlanetCard,), {
        "PLANET_KEY": key, "SECTION_LABEL": name, "IS_NODE": is_node
    })

PlanetSun     = _make_planet("sun",     "Sun")
PlanetMoon    = _make_planet("moon",    "Moon")
PlanetMars    = _make_planet("mars",    "Mars")
PlanetMercury = _make_planet("mercury", "Mercury")
PlanetJupiter = _make_planet("jupiter", "Jupiter")
PlanetVenus   = _make_planet("venus",   "Venus")
PlanetSaturn  = _make_planet("saturn",  "Saturn")
PlanetUranus  = _make_planet("uranus",  "Uranus")
PlanetNeptune = _make_planet("neptune", "Neptune")
PlanetPluto   = _make_planet("pluto",   "Pluto")
NodeRahu      = _make_planet("rahu",    "Rahu \u2014 North Node", is_node=True)
NodeKetu      = _make_planet("ketu",    "Ketu \u2014 South Node", is_node=True)


# --- Panchang ---
class PanchangTithi(TextCard):
    SECTION_LABEL = "Tithi"
    def _build_labels(self):
        self._val = self._gold()
        self._cl.addWidget(self._val)
        _, self._num  = self._field("Tithi number:")
        self._cl.addLayout(_)
        _, self._prog = self._field("Progress:")
        self._cl.addLayout(_)
        self._cl.addWidget(self._dim("A lunar day \u2014 1/30th of the synodic month"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._val.setText(AWAIT); return
        self._val.setText(s.get("tithi_name","—"))
        self._num.setText(f"{s.get('tithi_num','—')} of 30")
        self._prog.setText(f"{s.get('tithi_progress',0):.1f}% elapsed")

class PanchangVara(TextCard):
    SECTION_LABEL = "Vara"
    def _build_labels(self):
        self._val = self._gold()
        self._cl.addWidget(self._val)
        _, self._lord = self._field("Ruling planet:")
        self._cl.addLayout(_)
        self._cl.addWidget(self._dim("Vedic weekday"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._val.setText(AWAIT); return
        self._val.setText(s.get("vara_name","—"))
        self._lord.setText(s.get("vara_lord","—"))

class PanchangNakshatra(TextCard):
    SECTION_LABEL = "Nakshatra"
    def _build_labels(self):
        self._val = self._gold()
        self._cl.addWidget(self._val)
        _, self._lord = self._field("Lord:")
        self._cl.addLayout(_)
        _, self._prog = self._field("Progress:")
        self._cl.addLayout(_)
        self._cl.addWidget(self._dim("Moon\u2019s current lunar mansion"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._val.setText(AWAIT); return
        self._val.setText(s.get("nakshatra_name","—"))
        self._lord.setText(s.get("nakshatra_lord","—"))
        self._prog.setText(f"{s.get('nakshatra_progress',0):.1f}% elapsed")

class PanchangYoga(TextCard):
    SECTION_LABEL = "Yoga"
    def _build_labels(self):
        self._val = self._gold()
        self._cl.addWidget(self._val)
        _, self._idx = self._field("Number:")
        self._cl.addLayout(_)
        self._cl.addWidget(self._dim("Luni-solar combination (Sun + Moon longitude)"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._val.setText(AWAIT); return
        self._val.setText(s.get("yoga_name","—"))
        self._idx.setText(f"{s.get('yoga_index',0)+1} of 27")

class PanchangKarana(TextCard):
    SECTION_LABEL = "Karana"
    def _build_labels(self):
        self._val = self._gold()
        self._cl.addWidget(self._val)
        self._cl.addWidget(self._dim("Half a Tithi \u2014 6\u00b0 of Moon-Sun separation"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._val.setText(AWAIT); return
        self._val.setText(s.get("karana_name","—"))


# --- Time & Rhythm ---
class TimeCurrentCard(TextCard):
    SECTION_LABEL = "Current Time"
    def _build_labels(self):
        self._time = self._lbl("", FONT_TITLE, C_GOLD, bold=True)
        self._cl.addWidget(self._time)
        _, self._date = self._field("Date:"); self._cl.addLayout(_)
        _, self._day  = self._field("Day:"); self._cl.addLayout(_)
        _, self._utc  = self._field("UTC:"); self._cl.addLayout(_)
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._time.setText(AWAIT); return
        self._time.setText(s.get("time_local","—"))
        self._date.setText(s.get("time_date",""))
        self._day.setText(s.get("time_weekday",""))
        self._utc.setText(s.get("time_utc",""))

class RahuKalamCard(TextCard):
    SECTION_LABEL = "Rahu Kalam"
    def _build_labels(self):
        self._val = self._gold()
        self._cl.addWidget(self._val)
        self._active = self._lbl()
        self._cl.addWidget(self._active)
        self._cl.addWidget(self._dim("Daily inauspicious window \u2014 avoid starting important activities"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._val.setText(AWAIT); return
        start = s.get("rahu_kalam_start","—"); end = s.get("rahu_kalam_end","—")
        self._val.setText(f"{start} \u2014 {end}")
        active = s.get("rahu_kalam_active", False)
        self._active.setText("\u2691 Active now" if active else "Currently inactive")
        self._active.setStyleSheet(
            f"color:{C_RED};background:transparent;" if active
            else f"color:{C_TEXT_DIM};background:transparent;")

class PlanetaryHourCard(TextCard):
    SECTION_LABEL = "Planetary Hour"
    def _build_labels(self):
        self._planet = self._gold()
        self._cl.addWidget(self._planet)
        _, self._window = self._field("Window:"); self._cl.addLayout(_)
        _, self._num    = self._field("Hour number:"); self._cl.addLayout(_)
        self._cl.addWidget(self._dim("Current ruling planet in Chaldean order"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._planet.setText(AWAIT); return
        self._planet.setText(s.get("planetary_hour_planet","—"))
        self._window.setText(f"{s.get('planetary_hour_start','')} \u2014 {s.get('planetary_hour_end','')}")
        self._num.setText(f"{s.get('planetary_hour_num','—')} of 24")

class SunriseSunsetCard(TextCard):
    SECTION_LABEL = "Sunrise / Sunset"
    def _build_labels(self):
        _, self._rise = self._field("Sunrise:"); self._cl.addLayout(_)
        _, self._set  = self._field("Sunset:");  self._cl.addLayout(_)
        self._cl.addWidget(self._dim("Approximate \u2014 location-aware calc deferred"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._rise.setText(AWAIT); return
        self._rise.setText(s.get("sunrise","—"))
        self._set.setText(s.get("sunset","—"))

class DayLengthCard(TextCard):
    SECTION_LABEL = "Day Length"
    def _build_labels(self):
        self._val = self._gold(); self._cl.addWidget(self._val)
        self._cl.addWidget(self._dim("Hours of daylight (approximate)"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._val.setText(AWAIT); return
        self._val.setText(s.get("day_length","—"))


# --- Lunar Detail ---
class MoonPhaseTextCard(TextCard):
    SECTION_LABEL = "Moon Phase"
    def _build_labels(self):
        self._phase = self._gold(); self._cl.addWidget(self._phase)
        _, self._illum  = self._field("Illumination:"); self._cl.addLayout(_)
        _, self._waxing = self._field("Direction:"); self._cl.addLayout(_)
        _, self._angle  = self._field("Moon\u2013Sun angle:"); self._cl.addLayout(_)
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._phase.setText(AWAIT); return
        self._phase.setText(s.get("moon_phase_name","—"))
        self._illum.setText(f"{s.get('moon_illumination',0):.1f}%")
        self._waxing.setText("Waxing \u2014 growing" if s.get("moon_waxing") else "Waning \u2014 diminishing")
        self._angle.setText(f"{s.get('moon_phase_angle',0):.2f}\u00b0")

class MoonSignCard(TextCard):
    SECTION_LABEL = "Moon Sign"
    def _build_labels(self):
        self._sign = self._gold(); self._cl.addWidget(self._sign)
        _, self._deg = self._field("Degree in sign:"); self._cl.addLayout(_)
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._sign.setText(AWAIT); return
        self._sign.setText(f"{s.get('moon_sign_sym','')}  {s.get('moon_sign','—')}")
        self._deg.setText(s.get("moon_dms","—"))

class MoonNakshatraCard(TextCard):
    SECTION_LABEL = "Moon Nakshatra"
    def _build_labels(self):
        self._nak = self._gold(); self._cl.addWidget(self._nak)
        _, self._lord = self._field("Nakshatra lord:"); self._cl.addLayout(_)
        _, self._prog = self._field("Progress:"); self._cl.addLayout(_)
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._nak.setText(AWAIT); return
        self._nak.setText(s.get("moon_nakshatra","—"))
        self._lord.setText(s.get("moon_nak_lord","—"))
        self._prog.setText(f"{s.get('moon_nak_deg',0):.2f}\u00b0 into nakshatra")


# --- Aspects ---
class CurrentAspectsCard(TextCard):
    SECTION_LABEL = "Current Aspects"
    def _build_labels(self):
        self._lines = [self._lbl("", FONT_SMALL, C_TEXT_DIM) for _ in range(6)]
        for l in self._lines: self._cl.addWidget(l)
        _, self._count = self._field("Total active:"); self._cl.addLayout(_)
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._lines[0].setText(AWAIT); return
        aspects = s.get("aspects_active", [])
        for i, lbl in enumerate(self._lines):
            if i < len(aspects):
                a = aspects[i]
                lbl.setText(f"{a['p1']} {a['aspect']} {a['p2']}  \u2014  {a['orb']:.1f}\u00b0 orb")
            else: lbl.setText("")
        self._count.setText(str(s.get("aspects_count",0)))

class NextAspectCard(TextCard):
    SECTION_LABEL = "Tightest Aspect"
    def _build_labels(self):
        self._val = self._gold(); self._cl.addWidget(self._val)
        self._cl.addWidget(self._dim("Closest aspect currently active"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._val.setText(AWAIT); return
        self._val.setText(s.get("aspects_next","") or "None active")


# --- Seasons ---
class SeasonCurrentCard(TextCard):
    SECTION_LABEL = "Season"
    def _build_labels(self):
        self._season = self._gold(); self._cl.addWidget(self._season)
        self._reg = self._lbl(); self._cl.addWidget(self._reg)
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._season.setText(AWAIT); return
        self._season.setText(s.get("season","—"))
        self._reg.setText(s.get("season_register",""))

class SeasonProgressCard(TextCard):
    SECTION_LABEL = "Season Progress"
    def _build_labels(self):
        self._pct = self._gold(); self._cl.addWidget(self._pct)
        _, self._next = self._field("Next season:"); self._cl.addLayout(_)
        _, self._days = self._field("Days to transition:"); self._cl.addLayout(_)
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._pct.setText(AWAIT); return
        self._pct.setText(f"{s.get('season_progress',0):.1f}% through season")
        self._next.setText(s.get("season_next","—"))
        self._days.setText(f"~{s.get('season_days_to_next','—')} days")

class SeasonBoundaryCard(TextCard):
    SECTION_LABEL = "Season Boundary"
    def _build_labels(self):
        self._status = self._gold(); self._cl.addWidget(self._status)
        _, self._days = self._field("Transition in:"); self._cl.addLayout(_)
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._status.setText(AWAIT); return
        near = s.get("season_boundary_near", False)
        days = s.get("season_days_to_next","—"); nxt = s.get("season_next","—")
        self._status.setText("\u2691 Boundary approaching" if near else "Stable")
        self._status.setStyleSheet(
            f"color:{C_TEAL};font-size:{FONT_LARGE}pt;background:transparent;" if near
            else f"color:{C_GOLD};font-size:{FONT_LARGE}pt;background:transparent;")
        self._days.setText(f"~{days} days until {nxt}")


# --- Summaries ---
class SkySummaryCard(TextCard):
    SECTION_LABEL = "Sky Summary"
    def _build_labels(self):
        self._summary = self._lbl("", FONT_SIZE, C_TEXT)
        self._summary.setWordWrap(True); self._cl.addWidget(self._summary)
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._summary.setText(AWAIT); return
        self._summary.setText(s.get("sky_summary","—"))

class PanchangSummaryCard(TextCard):
    SECTION_LABEL = "Panchang Summary"
    def _build_labels(self):
        self._labels = {}
        for f in ["Tithi","Vara","Nakshatra","Yoga","Karana"]:
            row, val = self._field(f"{f}:"); self._cl.addLayout(row)
            self._labels[f] = val
        self._cl.addStretch()
    def _on_state(self, s):
        if not s:
            for l in self._labels.values(): l.setText(AWAIT)
            return
        self._labels["Tithi"].setText(f"{s.get('tithi_name','—')} ({s.get('tithi_num','—')} of 30)")
        self._labels["Vara"].setText(s.get("vara_name","—"))
        self._labels["Nakshatra"].setText(s.get("nakshatra_name","—"))
        self._labels["Yoga"].setText(s.get("yoga_name","—"))
        self._labels["Karana"].setText(s.get("karana_name","—"))

class EclipseProximityCard(TextCard):
    SECTION_LABEL = "Eclipse Proximity"
    def _build_labels(self):
        self._risk = self._gold(); self._cl.addWidget(self._risk)
        _, self._rahu = self._field("Distance to Rahu:"); self._cl.addLayout(_)
        _, self._ketu = self._field("Distance to Ketu:"); self._cl.addLayout(_)
        self._cl.addWidget(self._dim("High risk: Moon within 12\u00b0 of a node at lunation"))
        self._cl.addStretch()
    def _on_state(self, s):
        if not s: self._risk.setText(AWAIT); return
        risk = s.get("eclipse_risk","—")
        color = C_RED if risk=="High" else (C_TEAL if risk=="Medium" else C_GOLD)
        self._risk.setText(f"Eclipse risk: {risk}")
        self._risk.setStyleSheet(f"color:{color};font-size:{FONT_LARGE}pt;font-weight:bold;background:transparent;")
        self._rahu.setText(f"{s.get('eclipse_dist_rahu',0):.1f}\u00b0 \u2014 North Node (Rahu)")
        self._ketu.setText(f"{s.get('eclipse_dist_ketu',0):.1f}\u00b0 \u2014 South Node (Ketu)")


# --- Visual ---
class MoonDiscCard(VisualCard):
    SECTION_LABEL = "Moon Disc"
    def _draw_content(self, p, rect, s): painters.draw_moon_disc(p, rect, s)

class ZodiacWheelCard(VisualCard):
    SECTION_LABEL = "Zodiac Wheel"
    def _draw_content(self, p, rect, s): painters.draw_zodiac_wheel(p, rect, s)

class MoonArcCard(VisualCard):
    SECTION_LABEL = "Moon Arc"
    def _draw_content(self, p, rect, s): painters.draw_moon_arc(p, rect, s)

class NakshatraRingCard(VisualCard):
    SECTION_LABEL = "Nakshatra Ring"
    def _draw_content(self, p, rect, s): painters.draw_nakshatra_ring(p, rect, s)

class TithiDialCard(VisualCard):
    SECTION_LABEL = "Tithi Dial"
    def _draw_content(self, p, rect, s): painters.draw_tithi_dial(p, rect, s)

class EclipseGaugeCard(VisualCard):
    SECTION_LABEL = "Eclipse Gauge"
    def _draw_content(self, p, rect, s): painters.draw_eclipse_gauge(p, rect, s)

class PlanetStripCard(VisualCard):
    SECTION_LABEL = "Planet Strip"
    def _draw_content(self, p, rect, s): painters.draw_planet_strip(p, rect, s)

class MoonDistanceGaugeCard(VisualCard):
    SECTION_LABEL = "Moon Distance"
    def _draw_content(self, p, rect, s): painters.draw_moon_distance_gauge(p, rect, s)


WIDGET_CLASSES = {
    "planet_sun":PlanetSun,"planet_moon":PlanetMoon,"planet_mars":PlanetMars,
    "planet_mercury":PlanetMercury,"planet_jupiter":PlanetJupiter,
    "planet_venus":PlanetVenus,"planet_saturn":PlanetSaturn,
    "planet_uranus":PlanetUranus,"planet_neptune":PlanetNeptune,
    "planet_pluto":PlanetPluto,
    "node_rahu":NodeRahu,"node_ketu":NodeKetu,
    "panchang_tithi":PanchangTithi,"panchang_vara":PanchangVara,
    "panchang_nakshatra":PanchangNakshatra,"panchang_yoga":PanchangYoga,
    "panchang_karana":PanchangKarana,
    "time_current":TimeCurrentCard,"time_rahu_kalam":RahuKalamCard,
    "time_planetary_hour":PlanetaryHourCard,"time_sunrise_set":SunriseSunsetCard,
    "time_day_length":DayLengthCard,
    "lunar_phase_text":MoonPhaseTextCard,"lunar_sign":MoonSignCard,
    "lunar_nakshatra":MoonNakshatraCard,
    "aspects_current":CurrentAspectsCard,"aspects_next":NextAspectCard,
    "season_current":SeasonCurrentCard,"season_progress":SeasonProgressCard,
    "season_boundary":SeasonBoundaryCard,
    "summary_sky":SkySummaryCard,"summary_panchang":PanchangSummaryCard,
    "summary_eclipse":EclipseProximityCard,
    "moon_disc":MoonDiscCard,"zodiac_wheel":ZodiacWheelCard,
    "moon_arc":MoonArcCard,"nakshatra_ring":NakshatraRingCard,
    "tithi_dial":TithiDialCard,"eclipse_gauge":EclipseGaugeCard,
    "planet_strip":PlanetStripCard,"moon_distance_gauge":MoonDistanceGaugeCard,
}

def make_widget(widget_id, parent=None):
    cls = WIDGET_CLASSES.get(widget_id)
    if cls is None:
        w = TextCard.__new__(TextCard); TextCard.__init__(w, parent)
        w.SECTION_LABEL = widget_id; return w
    return cls(parent)
'''

# =============================================================================
FILES["painters.py"] = r'''# painters.py — Vigilarum Omnia v2
# Pure QPainter functions. (QPainter, QRectF, state|None) -> None
import math
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont,
                          QRadialGradient, QPainterPath)
from data import (SIGNS, SIGN_SYMBOLS, NAKSHATRAS, BODY_COLOURS, BODY_SYMBOLS,
                  C_BG, C_PANEL, C_BORDER, C_GOLD, C_GOLD_DIM,
                  C_TEXT, C_TEXT_DIM, C_TEAL, C_RED, C_GREEN, C_WHITE,
                  FONT_BODY, FONT_SIZE, FONT_SMALL)

AWAIT = "Awaiting data\u2026"

def _cx(r): return r.x() + r.width()/2
def _cy(r): return r.y() + r.height()/2
def _r(r, f=0.45): return min(r.width(), r.height()) * f
def _polar(cx, cy, r, deg):
    rad = math.radians(deg - 90)
    return QPointF(cx + r*math.cos(rad), cy + r*math.sin(rad))
def _pen(p, color, w=1.0):
    pen = QPen(QColor(color)); pen.setWidthF(w); p.setPen(pen)
def _await(p, rect):
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY, FONT_SMALL))
    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, AWAIT)


def draw_moon_disc(p, rect, state):
    if state is None: _await(p, rect); return
    illum  = state.get("moon_illumination", 0.0) / 100.0
    waxing = state.get("moon_waxing", True)
    phase  = state.get("moon_phase_name", "")
    cx = _cx(rect); cy = _cy(rect); r = _r(rect, 0.40)
    disc = QRectF(cx-r, cy-r, r*2, r*2)
    # dark base
    p.setBrush(QBrush(QColor("#1A1A2E")))
    p.setPen(QPen(QColor(C_BORDER), 1.0)); p.drawEllipse(disc)
    p.save()
    clip = QPainterPath(); clip.addEllipse(disc); p.setClipPath(clip)
    grad = QRadialGradient(cx, cy, r)
    grad.setColorAt(0.0, QColor("#F0E8C0")); grad.setColorAt(0.7, QColor("#C8A84B"))
    grad.setColorAt(1.0, QColor("#7A6530"))
    p.setBrush(QBrush(grad)); p.setPen(Qt.PenStyle.NoPen)
    term_x = abs(illum*2-1); term_w = r*2*term_x
    if illum < 0.5:
        lx = cx+r if waxing else cx-r
        p.drawEllipse(QRectF(lx-r, cy-r, r*2, r*2))
        p.setBrush(QBrush(QColor("#1A1A2E")))
        p.drawEllipse(QRectF(cx-term_w/2, cy-r, term_w, r*2))
    else:
        p.drawEllipse(disc)
        dx = cx-r if waxing else cx+r
        p.setBrush(QBrush(QColor("#1A1A2E"))); p.drawEllipse(QRectF(dx, cy-r, r*2, r*2))
        p.setBrush(QBrush(grad)); p.drawEllipse(QRectF(cx-term_w/2, cy-r, term_w, r*2))
    p.restore()
    _pen(p, C_BORDER, 1.0); p.setBrush(Qt.BrushStyle.NoBrush); p.drawEllipse(disc)
    # illumination label inside disc
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY, FONT_SMALL-1))
    p.drawText(QRectF(cx-40, cy-8, 80, 16), Qt.AlignmentFlag.AlignCenter,
               f"{state.get('moon_illumination',0):.0f}% illuminated")
    # phase name below disc with padding
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY, FONT_SMALL))
    p.drawText(QRectF(rect.x(), cy+r+8, rect.width(), 18), Qt.AlignmentFlag.AlignCenter, phase)


def draw_zodiac_wheel(p, rect, state):
    if state is None: _await(p, rect); return
    cx=_cx(rect); cy=_cy(rect); r=_r(rect, 0.44)
    or_=r; sr=r*0.82; ir=r*0.65; pr=r*0.50
    p.setBrush(QBrush(QColor(C_PANEL))); p.setPen(QPen(QColor(C_BORDER),1.0))
    p.drawEllipse(QRectF(cx-or_,cy-or_,or_*2,or_*2))
    p.setBrush(QBrush(QColor(C_BG))); p.setPen(QPen(QColor(C_GOLD_DIM),0.5))
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    for i in range(12):
        ang = i*30.0
        _pen(p, C_GOLD_DIM, 0.5)
        p.drawLine(_polar(cx,cy,ir,ang), _polar(cx,cy,or_,ang))
        mid = _polar(cx,cy,sr,ang+15)
        p.setPen(QColor(C_GOLD_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
        p.drawText(QRectF(mid.x()-10,mid.y()-8,20,16), Qt.AlignmentFlag.AlignCenter, SIGN_SYMBOLS[i])
    # bodies
    bodies = ["sun","moon","mars","mercury","jupiter","venus","saturn","rahu","ketu",
              "uranus","neptune","pluto"]
    for key in bodies:
        lon = state.get(f"{key}_lon")
        if lon is None: continue
        color = BODY_COLOURS.get(key, C_TEXT_DIM)
        sym   = BODY_SYMBOLS.get(key, "?")
        pt = _polar(cx,cy,pr,lon)
        p.setPen(QColor(color)); p.setBrush(QBrush(QColor(color)))
        p.drawEllipse(QRectF(pt.x()-3,pt.y()-3,6,6))
        p.setFont(QFont(FONT_BODY,FONT_SMALL-2))
        p.drawText(QRectF(pt.x()+4,pt.y()-6,14,12), Qt.AlignmentFlag.AlignLeft, sym)
    # legend note
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-2))
    p.drawText(QRectF(rect.x(),rect.y()+rect.height()-14,rect.width(),14),
               Qt.AlignmentFlag.AlignCenter, "Vedic sidereal \u2014 Lahiri ayanamsha")


def draw_moon_arc(p, rect, state):
    if state is None: _await(p, rect); return
    illum = state.get("moon_illumination", 0.0)
    phase = state.get("moon_phase_name", "")
    angle = state.get("moon_phase_angle", 0.0); pct = angle/360.0
    cx=_cx(rect); cy=_cy(rect); r=_r(rect,0.38)
    start=-210.0; span=240.0
    _pen(p, C_GOLD_DIM, 3.0); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(QRectF(cx-r,cy-r,r*2,r*2), int(start*16), int(span*16))
    _pen(p, C_GOLD, 3.0)
    p.drawArc(QRectF(cx-r,cy-r,r*2,r*2), int(start*16), int(span*pct*16))
    for frac in [0.25, 0.5, 0.75]:
        deg = start + span*frac
        pt  = _polar(cx, cy, r, -deg)
        _pen(p, C_GOLD_DIM, 1.0)
        p.drawEllipse(QRectF(pt.x()-3,pt.y()-3,6,6))
    p.setPen(QColor(C_GOLD)); p.setFont(QFont(FONT_BODY,FONT_SIZE+2,QFont.Weight.Bold))
    p.drawText(QRectF(cx-50,cy-14,100,28), Qt.AlignmentFlag.AlignCenter, f"{illum:.0f}%")
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL))
    p.drawText(QRectF(cx-60,cy+14,120,18), Qt.AlignmentFlag.AlignCenter, "illumination")
    p.drawText(QRectF(cx-60,cy+28,120,18), Qt.AlignmentFlag.AlignCenter, phase)


def draw_nakshatra_ring(p, rect, state):
    if state is None: _await(p, rect); return
    ni = state.get("nakshatra_index", 0)
    cx=_cx(rect); cy=_cy(rect); r=_r(rect,0.44); ir=r*0.62
    seg = 360.0/27.0
    for i in range(27):
        c = QColor(C_GOLD if i==ni else C_GOLD_DIM)
        c.setAlpha(200 if i==ni else 60)
        p.setBrush(QBrush(c)); _pen(p, C_BG, 1.0)
        path = QPainterPath()
        path.moveTo(QPointF(cx,cy))
        path.arcTo(QRectF(cx-r,cy-r,r*2,r*2), 90-i*seg, -seg)
        path.closeSubpath(); p.drawPath(path)
    p.setBrush(QBrush(QColor(C_BG))); p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    _pen(p, C_BORDER, 1.0); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    p.setPen(QColor(C_GOLD)); p.setFont(QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
    p.drawText(QRectF(cx-ir,cy-10,ir*2,20), Qt.AlignmentFlag.AlignCenter, NAKSHATRAS[ni])
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
    p.drawText(QRectF(cx-ir,cy+10,ir*2,14), Qt.AlignmentFlag.AlignCenter, "Moon\u2019s nakshatra")


def draw_tithi_dial(p, rect, state):
    if state is None: _await(p, rect); return
    ti = state.get("tithi_index",0); tn = state.get("tithi_name","—")
    tp = state.get("tithi_progress",0.0)
    cx=_cx(rect); cy=_cy(rect); r=_r(rect,0.44); ir=r*0.55
    seg=360.0/30.0
    for i in range(30):
        if i==ti: color,alpha=C_GOLD,220
        elif i<15: color,alpha=C_TEAL,50
        else: color,alpha=C_GOLD_DIM,50
        c=QColor(color); c.setAlpha(alpha)
        p.setBrush(QBrush(c)); _pen(p, C_BG, 1.0)
        path=QPainterPath(); path.moveTo(QPointF(cx,cy))
        path.arcTo(QRectF(cx-r,cy-r,r*2,r*2),90-i*seg,-seg)
        path.closeSubpath(); p.drawPath(path)
    p.setBrush(QBrush(QColor(C_BG))); p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    _pen(p, C_BORDER, 1.0); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    p.setPen(QColor(C_GOLD)); p.setFont(QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
    p.drawText(QRectF(cx-ir,cy-16,ir*2,18), Qt.AlignmentFlag.AlignCenter, tn)
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
    p.drawText(QRectF(cx-ir,cy+2,ir*2,16), Qt.AlignmentFlag.AlignCenter, f"{tp:.0f}% elapsed")
    p.drawText(QRectF(cx-ir,cy+16,ir*2,14), Qt.AlignmentFlag.AlignCenter, "Lunar day")


def draw_eclipse_gauge(p, rect, state):
    if state is None: _await(p, rect); return
    dr = state.get("eclipse_dist_rahu",90.0); dk = state.get("eclipse_dist_ketu",90.0)
    risk = state.get("eclipse_risk","Low"); nearest = state.get("eclipse_nearest","Rahu")
    cx=_cx(rect); cy=_cy(rect)
    bw=rect.width()*0.78; bh=14; bx=cx-bw/2; by=cy-bh/2
    rc = C_RED if risk=="High" else (C_TEAL if risk=="Medium" else C_GOLD_DIM)
    p.setBrush(QBrush(QColor(C_PANEL))); _pen(p, C_GOLD_DIM, 1.0)
    p.drawRect(QRectF(bx,by,bw,bh))
    md=min(dr,dk); dp=max(0.0,min(1.0,1.0-(md/30.0))); fw=bw*dp
    c=QColor(rc); c.setAlpha(160)
    p.setBrush(QBrush(c)); p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(bx,by,fw,bh))
    tx=bx+bw*(1.0-12.0/30.0); _pen(p, C_GOLD_DIM, 1.0)
    p.drawLine(QPointF(tx,by-2),QPointF(tx,by+bh+2))
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL))
    p.drawText(QRectF(bx-50,by,48,bh), Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter,
               f"Rahu \u2212 {dr:.1f}\u00b0")
    p.drawText(QRectF(bx+bw+2,by,50,bh), Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,
               f"{dk:.1f}\u00b0 \u2212 Ketu")
    p.setPen(QColor(rc)); p.setFont(QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
    p.drawText(QRectF(cx-80,by+bh+6,160,18), Qt.AlignmentFlag.AlignCenter,
               f"{risk} eclipse risk \u00b7 Moon {md:.1f}\u00b0 from {nearest}")
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
    p.drawText(QRectF(cx-80,by+bh+22,160,14), Qt.AlignmentFlag.AlignCenter,
               "High risk < 12\u00b0 \u00b7 Medium < 20\u00b0")


def draw_planet_strip(p, rect, state):
    if state is None: _await(p, rect); return
    bodies = ["sun","moon","mars","mercury","jupiter","venus","saturn",
              "uranus","neptune","pluto","rahu","ketu"]
    n=len(bodies); lh=rect.height()/n; bm=48; bx=rect.x()+bm; bw=rect.width()-bm-8
    for i,key in enumerate(bodies):
        lon=state.get(f"{key}_lon")
        if lon is None: continue
        yc=rect.y()+lh*i+lh/2
        color=BODY_COLOURS.get(key,C_TEXT_DIM); sym=BODY_SYMBOLS.get(key,"?")
        name=key.capitalize()
        _pen(p, C_GOLD_DIM, 0.5)
        p.drawLine(QPointF(bx,yc),QPointF(bx+bw,yc))
        for deg in range(0,361,30):
            mx=bx+(deg/360.0)*bw
            p.drawLine(QPointF(mx,yc-3),QPointF(mx,yc+3))
        dx=bx+(lon/360.0)*bw
        p.setBrush(QBrush(QColor(color))); _pen(p,color,1.0)
        p.drawEllipse(QRectF(dx-4,yc-4,8,8))
        # name label left
        p.setPen(QColor(color)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
        p.drawText(QRectF(rect.x(),yc-8,bm-6,16),
                   Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter, name)
        # degree label right of dot
        si=int(lon/30); di=lon%30
        retro=state.get(f"{key}_retrograde",False)
        lbl=f"{SIGN_SYMBOLS[si]}{di:.1f}\u00b0{' \u211e' if retro else ''}"
        p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-2))
        p.drawText(QRectF(dx+6,yc-8,60,16),
                   Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter, lbl)


def draw_moon_distance_gauge(p, rect, state):
    if state is None: _await(p, rect); return
    pct=state.get("moon_distance_pct",50.0)/100.0
    dist_km=state.get("moon_distance_km",384400)
    proximity=state.get("moon_proximity","—")
    cx=_cx(rect); gh=rect.height()*0.60; gw=18
    gx=cx-gw/2; gy=rect.y()+rect.height()*0.15
    p.setBrush(QBrush(QColor(C_PANEL))); _pen(p,C_GOLD_DIM,1.0)
    p.drawRect(QRectF(gx,gy,gw,gh))
    fh=gh*pct; fy=gy+gh-fh
    c=QColor(C_GOLD); c.setAlpha(140)
    p.setBrush(QBrush(c)); p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(gx,fy,gw,fh))
    _pen(p,C_GOLD,2.0); p.drawLine(QPointF(gx-6,fy),QPointF(gx+gw+6,fy))
    mid_y=gy+gh*0.5; _pen(p,C_GOLD_DIM,0.5)
    p.drawLine(QPointF(gx,mid_y),QPointF(gx+gw,mid_y))
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL))
    p.drawText(QRectF(cx-40,gy-18,80,16), Qt.AlignmentFlag.AlignCenter, "Apogee (far)")
    p.drawText(QRectF(cx-40,gy+gh+2,80,16), Qt.AlignmentFlag.AlignCenter, "Perigee (close)")
    p.setPen(QColor(C_GOLD)); p.setFont(QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
    p.drawText(QRectF(cx-55,fy-20,110,18), Qt.AlignmentFlag.AlignCenter,
               f"{int(dist_km):,} km")
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
    p.drawText(QRectF(cx-40,gy+gh+18,80,16), Qt.AlignmentFlag.AlignCenter,
               f"Currently: {proximity}")
'''

# =============================================================================
FILES["control.py"] = r'''# control.py — Vigilarum Omnia v2
import sys, datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy, QStatusBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from data import (
    WIDGET_REGISTRY, WIDGET_CATEGORIES, MAX_DISPLAYS, VALID_COLUMNS,
    C_BG, C_PANEL, C_BORDER, C_GOLD, C_GOLD_DIM,
    C_TEXT, C_TEXT_DIM, C_TEAL, C_RED, C_GREEN,
    FONT_BODY, FONT_SIZE, FONT_SMALL, FONT_LARGE, FONT_TITLE,
)
from engine import calculate_all
from state import write_state, toggle_widget, set_columns, widget_assignments, read_display

SS = f"""
QMainWindow,QWidget{{background:{C_BG};color:{C_TEXT};font-family:Georgia;font-size:11pt;}}
QScrollArea{{border:none;background:{C_BG};}}
QScrollBar:vertical{{background:{C_BG};width:8px;border:none;}}
QScrollBar::handle:vertical{{background:{C_GOLD_DIM};border-radius:4px;min-height:20px;}}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0px;}}
QFrame#div{{background:{C_GOLD_DIM};}}
QStatusBar{{background:{C_PANEL};color:{C_TEXT_DIM};font-size:9pt;border-top:1px solid {C_GOLD_DIM};}}
"""

def _lbl(text, size=FONT_SIZE, color=C_TEXT, bold=False):
    l = QLabel(text)
    l.setFont(QFont(FONT_BODY, size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color};background:transparent;")
    return l

def _make_btn(text, active=False):
    bg = C_GOLD if active else C_GOLD_DIM
    fg = C_BG  if active else C_TEXT
    b = QPushButton(text); b.setFont(QFont(FONT_BODY, FONT_SMALL))
    b.setFixedSize(28, 22)
    b.setProperty("active", active)
    b.setStyleSheet(f"""
        QPushButton{{background:{bg};color:{fg};border:1px solid {C_GOLD_DIM};border-radius:3px;}}
        QPushButton:hover{{background:{C_GOLD};color:{C_BG};}}
    """)
    return b

def _set_btn_active(btn, active):
    btn.setProperty("active", active)
    bg = C_GOLD if active else C_GOLD_DIM; fg = C_BG if active else C_TEXT
    btn.setStyleSheet(f"""
        QPushButton{{background:{bg};color:{fg};border:1px solid {C_GOLD_DIM};border-radius:3px;}}
        QPushButton:hover{{background:{C_GOLD};color:{C_BG};}}
    """)


class EngineWorker(QThread):
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)
    def run(self):
        try: self.finished.emit(calculate_all())
        except Exception as e: self.error.emit(str(e))


class WidgetRow(QWidget):
    def __init__(self, wid, name, ctype, category, assignments, parent=None):
        super().__init__(parent)
        self.wid = wid; self._btns = {}
        row = QHBoxLayout(self); row.setContentsMargins(6,3,6,3); row.setSpacing(4)
        badge_color = C_TEAL if ctype=="visual" else C_GOLD_DIM
        badge_text  = "Vis" if ctype=="visual" else "Txt"
        badge = _lbl(badge_text, FONT_SMALL-1, badge_color); badge.setFixedWidth(24)
        row.addWidget(badge)
        name_lbl = _lbl(name, FONT_SIZE); name_lbl.setMinimumWidth(180)
        row.addWidget(name_lbl); row.addStretch()
        assigned = assignments.get(wid, [])
        for d in range(1, MAX_DISPLAYS+1):
            btn = _make_btn(str(d), active=(d in assigned))
            btn.clicked.connect(lambda checked, did=d: self._toggle(did))
            self._btns[d] = btn; row.addWidget(btn)

    def _toggle(self, did):
        now_on = toggle_widget(did, self.wid)
        _set_btn_active(self._btns[did], now_on)

    def refresh(self, assignments):
        assigned = assignments.get(self.wid, [])
        for d, btn in self._btns.items():
            _set_btn_active(btn, d in assigned)


class ColPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._col_btns = {}
        vl = QVBoxLayout(self); vl.setContentsMargins(12,12,12,12); vl.setSpacing(12)
        vl.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = _lbl("COLUMNS", FONT_SMALL, C_GOLD_DIM, bold=True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter); vl.addWidget(title)
        for d in range(1, MAX_DISPLAYS+1):
            cfg = read_display(d); cur = cfg["columns"]
            block = QWidget(); bl = QVBoxLayout(block)
            bl.setContentsMargins(0,0,0,0); bl.setSpacing(2)
            bl.addWidget(_lbl(f"Display {d}", FONT_SMALL, C_TEXT_DIM))
            br = QHBoxLayout(); br.setSpacing(3)
            self._col_btns[d] = {}
            for c in VALID_COLUMNS:
                btn = _make_btn(str(c), active=(c==cur))
                btn.clicked.connect(lambda checked,did=d,col=c: self._set(did,col))
                self._col_btns[d][c] = btn; br.addWidget(btn)
            bl.addLayout(br); vl.addWidget(block)

    def _set(self, did, columns):
        set_columns(did, columns)
        for c, btn in self._col_btns[did].items():
            _set_btn_active(btn, c==columns)


class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vigilarum Omnia — Control")
        self.setMinimumSize(900, 660)
        self._last_state = None; self._engine_running = False
        self._build_ui(); self.setStyleSheet(SS)
        self._start_engine()

    def _build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        root.addWidget(self._build_header())
        div = QFrame(); div.setObjectName("div"); div.setFixedHeight(1); root.addWidget(div)
        body = QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        body.addWidget(self._build_list(), stretch=1)
        rdiv = QFrame(); rdiv.setObjectName("div"); rdiv.setFixedWidth(1); body.addWidget(rdiv)
        self._col_panel = ColPanel(); self._col_panel.setFixedWidth(185); body.addWidget(self._col_panel)
        root.addLayout(body, stretch=1)
        self._statusbar = QStatusBar(); self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("Initialising engine\u2026")

    def _build_header(self):
        hdr = QWidget(); hdr.setFixedHeight(52)
        hdr.setStyleSheet(f"background:{C_PANEL};")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(16,0,16,0)
        hl.addWidget(_lbl("VIGILARUM OMNIA", FONT_TITLE, C_GOLD, bold=True))
        hl.addStretch()
        self._engine_lbl = _lbl("\u25cf Calculating\u2026", FONT_SMALL, C_GOLD_DIM)
        hl.addWidget(self._engine_lbl)
        self._sky_lbl = _lbl("", FONT_SMALL, C_TEXT_DIM)
        self._sky_lbl.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        hl.addWidget(self._sky_lbl)
        return hdr

    def _build_list(self):
        container = QWidget(); vl = QVBoxLayout(container)
        vl.setContentsMargins(0,0,0,0); vl.setSpacing(0)
        # column header
        hdr = QWidget(); hdr.setFixedHeight(26); hdr.setStyleSheet(f"background:{C_PANEL};")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(6,0,6,0); hl.setSpacing(4)
        hl.addWidget(_lbl("Type", FONT_SMALL, C_GOLD_DIM, bold=True))
        hl.addWidget(_lbl("Widget", FONT_SMALL, C_GOLD_DIM, bold=True))
        hl.addStretch()
        for d in range(1, MAX_DISPLAYS+1):
            l = _lbl(str(d), FONT_SMALL, C_GOLD_DIM, bold=True)
            l.setFixedWidth(28); l.setAlignment(Qt.AlignmentFlag.AlignCenter); hl.addWidget(l)
        vl.addWidget(hdr)
        hdiv = QFrame(); hdiv.setObjectName("div"); hdiv.setFixedHeight(1); vl.addWidget(hdiv)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget(); cl = QVBoxLayout(content)
        cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)
        assignments = widget_assignments()
        self._rows = []
        # group by category
        by_cat = {}
        for wid,name,ctype,cat in WIDGET_REGISTRY:
            by_cat.setdefault(cat,[]).append((wid,name,ctype,cat))
        row_idx = 0
        for cat in WIDGET_CATEGORIES:
            items = by_cat.get(cat,[])
            if not items: continue
            # category header
            cat_hdr = QWidget(); cat_hdr.setFixedHeight(24)
            cat_hdr.setStyleSheet(f"background:#14142A;")
            ch = QHBoxLayout(cat_hdr); ch.setContentsMargins(8,0,8,0)
            ch.addWidget(_lbl(cat.upper(), FONT_SMALL, C_GOLD_DIM, bold=True))
            cl.addWidget(cat_hdr)
            for wid,name,ctype,_ in items:
                row = WidgetRow(wid,name,ctype,cat,assignments)
                bg = C_BG if row_idx%2==0 else C_PANEL
                row.setStyleSheet(f"background:{bg};")
                cl.addWidget(row); self._rows.append(row); row_idx+=1
        cl.addStretch(); scroll.setWidget(content); vl.addWidget(scroll)
        return container

    def _start_engine(self):
        self._run_engine()
        self._etimer = QTimer(self); self._etimer.setInterval(60_000)
        self._etimer.timeout.connect(self._run_engine); self._etimer.start()
        self._ctimer = QTimer(self); self._ctimer.setInterval(1_000)
        self._ctimer.timeout.connect(self._clock_tick); self._ctimer.start()

    def _run_engine(self):
        if self._engine_running: return
        self._engine_running = True
        self._worker = EngineWorker()
        self._worker.finished.connect(self._done)
        self._worker.error.connect(self._err)
        self._worker.start()

    def _done(self, state):
        self._engine_running = False; self._last_state = state
        write_state(state)
        self._engine_lbl.setText("\u25cf Live")
        self._engine_lbl.setStyleSheet(f"color:{C_GREEN};background:transparent;")
        self._sky_lbl.setText(state.get("sky_summary",""))
        self._statusbar.showMessage(
            f"Engine updated \u00b7 {state.get('time_local','')} \u00b7 "
            f"{state.get('aspects_count',0)} aspects \u00b7 "
            f"{state.get('season','')} \u00b7 {state.get('moon_phase_name','')}")

    def _err(self, msg):
        self._engine_running = False
        self._engine_lbl.setText("\u25cf Error")
        self._engine_lbl.setStyleSheet(f"color:{C_RED};background:transparent;")
        self._statusbar.showMessage(f"Engine error: {msg}")

    def _clock_tick(self):
        if self._last_state is None: return
        now = datetime.datetime.now()
        self._last_state["time_local"]     = now.strftime("%H:%M:%S")
        self._last_state["time_timestamp"] = now.isoformat()
        write_state(self._last_state)


def main():
    app = QApplication(sys.argv)
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,      QColor(C_BG))
    pal.setColor(QPalette.ColorRole.WindowText,  QColor(C_TEXT))
    pal.setColor(QPalette.ColorRole.Base,        QColor(C_PANEL))
    pal.setColor(QPalette.ColorRole.Text,        QColor(C_TEXT))
    app.setPalette(pal)
    w = ControlPanel(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
'''

# =============================================================================
FILES["display.py"] = r'''# display.py — Vigilarum Omnia v2
# Usage: python3 display.py <N> [--bare]
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QFrame,
)
from PyQt6.QtCore import Qt, QTimer, QMimeData, QPoint
from PyQt6.QtGui import QColor, QPalette, QFont, QDrag, QPixmap

from data import (MAX_DISPLAYS, DEFAULT_COLS, C_BG, C_PANEL, C_GOLD, C_GOLD_DIM,
                  C_TEXT, C_TEXT_DIM, C_TEAL, FONT_BODY, FONT_SIZE, FONT_SMALL)
from state import read_state, read_display, write_display
from widgets import make_widget, ArcaneCard

POLL_MS = 1_000


class DraggableCard(QWidget):
    """Wrapper that makes an ArcaneCard draggable within the grid."""
    def __init__(self, widget_id, card, parent=None):
        super().__init__(parent)
        self.widget_id = widget_id
        self._card = card
        vl = QVBoxLayout(self); vl.setContentsMargins(0,0,0,0)
        vl.addWidget(card)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def update_data(self, state):
        self._card.update_data(state)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton): return
        if (event.pos() - self._drag_start).manhattanLength() < 10: return
        drag = QDrag(self)
        mime = QMimeData(); mime.setText(self.widget_id)
        drag.setMimeData(mime)
        px = QPixmap(self.size()); self.render(px)
        drag.setPixmap(px); drag.setHotSpot(event.pos())
        drag.exec(Qt.DropAction.MoveAction)


class WidgetGrid(QWidget):
    def __init__(self, display_id, parent=None):
        super().__init__(parent)
        self._did = display_id
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(4,4,4,4); self._layout.setSpacing(4)
        self._cards: list[DraggableCard] = []
        self._ids: list[str] = []
        self._columns = DEFAULT_COLS
        self.setAcceptDrops(True)

    def mount(self, widget_ids, columns):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._cards.clear(); self._ids = list(widget_ids); self._columns = columns
        for col in range(columns): self._layout.setColumnStretch(col, 1)
        for i, wid in enumerate(widget_ids):
            row = i // columns; col = i % columns
            card = make_widget(wid, self)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            dc = DraggableCard(wid, card, self)
            self._layout.addWidget(dc, row, col)
            self._layout.setRowStretch(row, 1)
            self._cards.append(dc)

    def push_state(self, state):
        for dc in self._cards: dc.update_data(state)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): event.acceptProposedAction()

    def dropEvent(self, event):
        src_id = event.mimeData().text()
        if src_id not in self._ids: return
        pos = event.position().toPoint()
        target = self.childAt(pos)
        while target and not isinstance(target, DraggableCard):
            target = target.parent()
        if target is None or target.widget_id == src_id: return
        si = self._ids.index(src_id); ti = self._ids.index(target.widget_id)
        self._ids[si], self._ids[ti] = self._ids[ti], self._ids[si]
        cfg = read_display(self._did); cfg["widgets"] = self._ids
        write_display(self._did, cfg)
        self.mount(self._ids, self._columns)
        event.acceptProposedAction()


class SummaryBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet(f"background:{C_PANEL};border-bottom:1px solid {C_GOLD_DIM};")
        hl = QHBoxLayout(self); hl.setContentsMargins(12,0,12,0); hl.setSpacing(16)
        self._sky  = self._l("", C_TEXT_DIM)
        self._time = self._l("", C_GOLD_DIM)
        hl.addWidget(self._sky, stretch=1); hl.addWidget(self._time)

    def _l(self, t, c):
        l=QLabel(t); l.setFont(QFont(FONT_BODY,FONT_SMALL))
        l.setStyleSheet(f"color:{c};background:transparent;"); return l

    def update_state(self, state):
        if not state: self._sky.setText("Awaiting engine\u2026"); self._time.setText(""); return
        self._sky.setText(state.get("sky_summary","")); self._time.setText(state.get("time_local",""))


class StatusLine(QWidget):
    def __init__(self, did, parent=None):
        super().__init__(parent)
        self._did = did; self.setFixedHeight(20)
        self.setStyleSheet(f"background:{C_PANEL};border-top:1px solid {C_GOLD_DIM};")
        hl = QHBoxLayout(self); hl.setContentsMargins(12,0,12,0)
        self._msg = QLabel(f"Display {did}  \u00b7  Awaiting state\u2026")
        self._msg.setFont(QFont(FONT_BODY,FONT_SMALL-1))
        self._msg.setStyleSheet(f"color:{C_TEXT_DIM};background:transparent;")
        hl.addWidget(self._msg)

    def update_state(self, state, n):
        if not state: self._msg.setText(f"Display {self._did}  \u00b7  No state"); return
        self._msg.setText(
            f"Display {self._did}  \u00b7  {n} widget{'s' if n!=1 else ''}  \u00b7  "
            f"{state.get('time_local','')}  \u00b7  {state.get('season','')}  \u00b7  "
            f"{state.get('moon_phase_name','')}")


class DisplayWindow(QMainWindow):
    def __init__(self, did, bare=False):
        super().__init__()
        self._did=did; self._bare=bare
        self._last_ids=[]; self._last_cols=DEFAULT_COLS; self._last_state=None
        self.setWindowTitle(f"Vigilarum \u2014 Display {did}" + (" (bare)" if bare else ""))
        self.setMinimumSize(400,300)
        self._build_ui()
        self.setStyleSheet(f"QMainWindow,QWidget{{background:{C_BG};color:{C_TEXT};font-family:Georgia;font-size:11pt;}}")
        pal=QPalette(); pal.setColor(QPalette.ColorRole.Window,QColor(C_BG)); self.setPalette(pal)
        t=QTimer(self); t.setInterval(POLL_MS); t.timeout.connect(self._poll); t.start()
        self._poll()

    def _build_ui(self):
        c=QWidget(); self.setCentralWidget(c)
        root=QVBoxLayout(c); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        if not self._bare:
            self._sumbar=SummaryBar(); root.addWidget(self._sumbar)
        self._grid=WidgetGrid(self._did); root.addWidget(self._grid,stretch=1)
        if not self._bare:
            self._statline=StatusLine(self._did); root.addWidget(self._statline)

    def _poll(self):
        cfg=read_display(self._did)
        ids=cfg.get("widgets",[]); cols=cfg.get("columns",DEFAULT_COLS)
        if ids!=self._last_ids or cols!=self._last_cols:
            self._grid.mount(ids,cols); self._last_ids=list(ids); self._last_cols=cols
        state=read_state(); self._last_state=state
        self._grid.push_state(state)
        if not self._bare:
            self._sumbar.update_state(state); self._statline.update_state(state,len(ids))


def main():
    args=sys.argv[1:]; bare="--bare" in args; args=[a for a in args if a!="--bare"]
    if not args: print("Usage: python3 display.py <N> [--bare]"); sys.exit(1)
    try:
        did=int(args[0])
        if not (1<=did<=MAX_DISPLAYS): raise ValueError
    except ValueError: print(f"Display ID must be 1-{MAX_DISPLAYS}"); sys.exit(1)
    app=QApplication(sys.argv)
    pal=QPalette(); pal.setColor(QPalette.ColorRole.Window,QColor(C_BG))
    pal.setColor(QPalette.ColorRole.WindowText,QColor(C_TEXT)); app.setPalette(pal)
    w=DisplayWindow(did,bare=bare); w.show(); sys.exit(app.exec())

if __name__=="__main__":
    main()
'''

# =============================================================================
FILES["info.py"] = r'''# info.py — Vigilarum Omnia v2
# Floating info window. Tree on left, text display on right.
# General system writeups + live widget context.
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QTreeWidget, QTreeWidgetItem, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from data import (
    WIDGET_REGISTRY, WIDGET_CATEGORIES, WIDGET_BY_ID, INFO_GENERAL,
    C_BG, C_PANEL, C_BORDER, C_GOLD, C_GOLD_DIM,
    C_TEXT, C_TEXT_DIM, C_TEAL, FONT_BODY, FONT_SIZE, FONT_SMALL, FONT_TITLE,
)
from state import read_state, read_display, widget_assignments
from data import MAX_DISPLAYS

SS = f"""
QMainWindow,QWidget{{background:{C_BG};color:{C_TEXT};font-family:Georgia;font-size:10pt;}}
QTreeWidget{{background:{C_PANEL};border:none;color:{C_TEXT};}}
QTreeWidget::item{{padding:3px;}}
QTreeWidget::item:selected{{background:{C_GOLD_DIM};color:{C_TEXT};}}
QTreeWidget::item:hover{{background:#1A1A2A;}}
QScrollArea{{border:none;background:{C_BG};}}
QScrollBar:vertical{{background:{C_BG};width:8px;border:none;}}
QScrollBar::handle:vertical{{background:{C_GOLD_DIM};border-radius:4px;min-height:20px;}}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
"""


def _lbl(text, size=FONT_SIZE, color=C_TEXT, bold=False):
    l=QLabel(text); l.setFont(QFont(FONT_BODY,size,QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color};background:transparent;"); l.setWordWrap(True)
    return l


class InfoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vigilarum Omnia \u2014 Information")
        self.setMinimumSize(780, 560)
        self._last_assignments = {}
        self._build_ui(); self.setStyleSheet(SS)
        self._populate_tree()
        t=QTimer(self); t.setInterval(2_000); t.timeout.connect(self._refresh_live); t.start()

    def _build_ui(self):
        central=QWidget(); self.setCentralWidget(central)
        root=QVBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        # header
        hdr=QWidget(); hdr.setFixedHeight(48); hdr.setStyleSheet(f"background:{C_PANEL};")
        hl=QHBoxLayout(hdr); hl.setContentsMargins(16,0,16,0)
        hl.addWidget(_lbl("VIGILARUM INFORMATION", 14, C_GOLD, bold=True)); hl.addStretch()
        root.addWidget(hdr)
        div=QFrame(); div.setFixedHeight(1); div.setStyleSheet(f"background:{C_GOLD_DIM};")
        root.addWidget(div)
        # body
        body=QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        # tree
        self._tree=QTreeWidget(); self._tree.setHeaderHidden(True)
        self._tree.setFixedWidth(260); self._tree.setIndentation(14)
        self._tree.currentItemChanged.connect(self._on_select)
        body.addWidget(self._tree)
        vdiv=QFrame(); vdiv.setFixedWidth(1); vdiv.setStyleSheet(f"background:{C_GOLD_DIM};")
        body.addWidget(vdiv)
        # text pane
        right=QWidget(); rl=QVBoxLayout(right); rl.setContentsMargins(0,0,0,0); rl.setSpacing(0)
        self._title_lbl=_lbl("", 14, C_GOLD, bold=True)
        self._title_lbl.setContentsMargins(16,12,16,4); right.layout().addWidget(self._title_lbl)
        tdiv=QFrame(); tdiv.setFixedHeight(1); tdiv.setStyleSheet(f"background:{C_GOLD_DIM};")
        right.layout().addWidget(tdiv)
        scroll=QScrollArea(); scroll.setWidgetResizable(True)
        self._text_widget=QWidget(); tl=QVBoxLayout(self._text_widget)
        tl.setContentsMargins(16,12,16,16); tl.setSpacing(8); tl.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._text_labels=[]
        for _ in range(20):
            l=_lbl("",FONT_SIZE,C_TEXT); self._text_labels.append(l); tl.addWidget(l)
        tl.addStretch()
        scroll.setWidget(self._text_widget); right.layout().addWidget(scroll)
        body.addWidget(right, stretch=1)
        root.addLayout(body, stretch=1)

    def _populate_tree(self):
        self._tree.clear()
        # General systems
        general_root=QTreeWidgetItem(self._tree,["General Information"])
        general_root.setFont(0,QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
        general_root.setForeground(0,QColor(C_GOLD))
        for title in INFO_GENERAL:
            item=QTreeWidgetItem(general_root,[title])
            item.setData(0,Qt.ItemDataRole.UserRole,("general",title))
            item.setForeground(0,QColor(C_TEXT_DIM))
        general_root.setExpanded(True)
        # Widget categories
        widget_root=QTreeWidgetItem(self._tree,["Widgets"])
        widget_root.setFont(0,QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
        widget_root.setForeground(0,QColor(C_GOLD))
        by_cat={}
        for wid,name,ctype,cat in WIDGET_REGISTRY:
            by_cat.setdefault(cat,[]).append((wid,name))
        for cat in WIDGET_CATEGORIES:
            items=by_cat.get(cat,[])
            if not items: continue
            cat_item=QTreeWidgetItem(widget_root,[cat])
            cat_item.setForeground(0,QColor(C_TEAL))
            cat_item.setFont(0,QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
            for wid,name in items:
                w=QTreeWidgetItem(cat_item,[name])
                w.setData(0,Qt.ItemDataRole.UserRole,("widget",wid))
                w.setForeground(0,QColor(C_TEXT_DIM))
        widget_root.setExpanded(True)
        # Live assignments
        self._live_root=QTreeWidgetItem(self._tree,["Currently Displayed"])
        self._live_root.setFont(0,QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
        self._live_root.setForeground(0,QColor(C_GOLD))
        self._tree.addTopLevelItem(self._live_root)
        self._refresh_live()

    def _refresh_live(self):
        assignments=widget_assignments()
        if assignments==self._last_assignments: return
        self._last_assignments=assignments
        while self._live_root.childCount():
            self._live_root.removeChild(self._live_root.child(0))
        state=read_state()
        for wid,displays in sorted(assignments.items(),key=lambda x:x[0]):
            entry=WIDGET_BY_ID.get(wid)
            if not entry: continue
            name=entry[1]
            disp_str=", ".join(f"D{d}" for d in displays)
            item=QTreeWidgetItem(self._live_root,[f"{name}  \u2014  {disp_str}"])
            item.setData(0,Qt.ItemDataRole.UserRole,("widget_live",wid))
            item.setForeground(0,QColor(C_TEAL))
        self._live_root.setExpanded(bool(assignments))

    def _on_select(self, current, _):
        if current is None: return
        data=current.data(0,Qt.ItemDataRole.UserRole)
        if data is None: return
        kind,key=data
        if kind=="general":
            self._show_general(key)
        elif kind in ("widget","widget_live"):
            self._show_widget(key)

    def _show_general(self, title):
        self._title_lbl.setText(title)
        text=INFO_GENERAL.get(title,"No information available.")
        self._set_text([text])

    def _show_widget(self, wid):
        entry=WIDGET_BY_ID.get(wid)
        if not entry: return
        _,name,ctype,cat=entry
        self._title_lbl.setText(name)
        state=read_state()
        lines=[]
        lines.append(f"Category: {cat}")
        lines.append(f"Type: {'Visual (painted)' if ctype=='visual' else 'Text (labels)'}")
        lines.append(f"Widget ID: {wid}")
        lines.append("")
        # General description from INFO_GENERAL if available
        for key in INFO_GENERAL:
            if key.lower() in name.lower() or name.lower() in key.lower():
                lines.append(INFO_GENERAL[key]); lines.append("")
                break
        # Live state context
        if state:
            lines.append("\u2500 Live State \u2500")
            lines.append(self._live_context(wid, state))
        else:
            lines.append("No live state available \u2014 control panel not running.")
        self._set_text(lines)

    def _live_context(self, wid, state) -> str:
        if wid.startswith("planet_"):
            k=wid.replace("planet_","")
            sign=state.get(f"{k}_sign","—"); dms=state.get(f"{k}_dms","—")
            nak=state.get(f"{k}_nakshatra","—"); lord=state.get(f"{k}_nak_lord","—")
            retro=state.get(f"{k}_retrograde",False)
            r=" (retrograde)" if retro else ""
            return f"{k.capitalize()} is in {sign} at {dms}{r}. Nakshatra: {nak}, ruled by {lord}."
        if wid.startswith("node_"):
            k="rahu" if "rahu" in wid else "ketu"
            sign=state.get(f"{k}_sign","—"); dms=state.get(f"{k}_dms","—")
            nak=state.get(f"{k}_nakshatra","—")
            node_name="Rahu (North Node)" if k=="rahu" else "Ketu (South Node)"
            return f"{node_name} is in {sign} at {dms}. Nakshatra: {nak}. Always retrograde."
        if wid=="panchang_tithi":
            return (f"Current Tithi: {state.get('tithi_name','—')} ({state.get('tithi_num','—')} of 30). "
                    f"{state.get('tithi_progress',0):.1f}% elapsed. "
                    f"{'Waxing (Shukla Paksha)' if state.get('tithi_num',1)<=15 else 'Waning (Krishna Paksha)'}.")
        if wid=="panchang_vara":
            return (f"Today is {state.get('vara_name','—')}, ruled by {state.get('vara_lord','—')}.")
        if wid=="panchang_nakshatra":
            return (f"Moon is in {state.get('nakshatra_name','—')}, ruled by {state.get('nakshatra_lord','—')}. "
                    f"{state.get('nakshatra_progress',0):.1f}% through this nakshatra.")
        if wid=="panchang_yoga":
            return f"Current Yoga: {state.get('yoga_name','—')} ({state.get('yoga_index',0)+1} of 27)."
        if wid=="panchang_karana":
            return f"Current Karana: {state.get('karana_name','—')}."
        if wid=="time_rahu_kalam":
            active=state.get("rahu_kalam_active",False)
            s=state.get("rahu_kalam_start","—"); e=state.get("rahu_kalam_end","—")
            return (f"Today's Rahu Kalam window: {s} \u2014 {e}. "
                    f"{'Currently ACTIVE \u2014 inauspicious period.' if active else 'Currently inactive.'}")
        if wid=="time_planetary_hour":
            return (f"Current planetary hour is ruled by {state.get('planetary_hour_planet','—')} "
                    f"({state.get('planetary_hour_start','')} \u2014 {state.get('planetary_hour_end','')}). "
                    f"Hour {state.get('planetary_hour_num','—')} of 24.")
        if wid=="time_sunrise_set":
            return f"Sunrise: {state.get('sunrise','—')}. Sunset: {state.get('sunset','—')}. Day length: {state.get('day_length','—')}."
        if wid=="lunar_phase_text":
            return (f"Moon is {state.get('moon_phase_name','—')} at {state.get('moon_illumination',0):.1f}% illumination. "
                    f"{'Waxing' if state.get('moon_waxing') else 'Waning'}. "
                    f"Moon\u2013Sun angle: {state.get('moon_phase_angle',0):.2f}\u00b0.")
        if wid=="summary_eclipse":
            risk=state.get("eclipse_risk","—"); nd=state.get("eclipse_nearest","—")
            md=state.get("eclipse_min_dist",0)
            return (f"Eclipse risk: {risk}. Moon is {md:.1f}\u00b0 from {nd}. "
                    f"High risk occurs when Moon is within 12\u00b0 of a node at a new or full moon.")
        if wid=="season_current":
            return (f"Currently {state.get('season','—')}. {state.get('season_register','')} "
                    f"Approximately {state.get('season_days_to_next','—')} days until {state.get('season_next','—')}.")
        if wid=="moon_distance_gauge":
            return (f"Moon is {int(state.get('moon_distance_km',0)):,} km away. "
                    f"Currently near {'perigee (closest)' if state.get('moon_proximity')=='Perigee' else 'apogee (furthest)'}. "
                    f"{state.get('moon_distance_pct',0):.1f}% of the way from perigee to apogee.")
        return "Live data available \u2014 see widget for current values."

    def _set_text(self, lines):
        for i, lbl in enumerate(self._text_labels):
            if i < len(lines):
                lbl.setText(lines[i])
                color = C_TEXT_DIM if (lines[i].startswith("\u2500") or lines[i].startswith("Category:") or lines[i].startswith("Type:")) else C_TEXT
                lbl.setStyleSheet(f"color:{color};background:transparent;")
            else:
                lbl.setText("")


def main():
    app=QApplication(sys.argv)
    pal=QPalette(); pal.setColor(QPalette.ColorRole.Window,QColor(C_BG))
    pal.setColor(QPalette.ColorRole.WindowText,QColor(C_TEXT)); app.setPalette(pal)
    w=InfoWindow(); w.show(); sys.exit(app.exec())

if __name__=="__main__":
    main()
'''

# =============================================================================
def write(filename, content):
    path = os.path.join(BASE, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote {filename}")

if __name__ == "__main__":
    print(f"\nVigilarum Omnia v2 — installer")
    print(f"Target: {BASE}\n")
    for filename, content in FILES.items():
        write(filename, content)
    print(f"\nDone. {len(FILES)} files written.")
    print("Run:  python3 control.py")
    print("      python3 display.py 1")
    print("      python3 info.py\n")
