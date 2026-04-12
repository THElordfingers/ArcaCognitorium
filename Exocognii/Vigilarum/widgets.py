# widgets.py — Vigilarum Omnia v2
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
