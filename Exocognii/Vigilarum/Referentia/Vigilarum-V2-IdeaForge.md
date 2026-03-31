# VIGILARUM OMNIA — v2
### IdeaForge Build Document · PyQt6 Migration
*Arca Cognitorium — Exocognii Suite*
*Prepared: MMXXVI · Tier 6 Migration*

---

## TABLE OF CONTENTS

```
1.  Overview & Architecture
2.  Tech Stack
3.  Directory Tree
4.  Module Breakdown
5.  UI Wireframe
6.  Data Flow
7.  Code Stubs
8.  Error Handling
9.  Setup & Testing
10. Packaging
11. Extensibility
```

---

## 1. OVERVIEW & ARCHITECTURE

Vigilarum Omnia is a standalone PyQt6 desktop application that renders real-time
Vedic sidereal astronomical data from pyswisseph as a collection of interactive
widgets. It is a demonstrative instrument — it makes the sky legible. No Tower
integration. No external service dependencies beyond pyswisseph and the Anthropic
API key it does not use.

The architecture preserves the proven control/display split from v1: a single
Control Panel process calculates sky state and writes it to a shared JSON file;
one or more Display windows read that file and render assigned widgets. The
calculation engine and data tables are carried forward unchanged from v1. All
presentation code is rewritten in PyQt6.

```
╭──────────────────────┬────────────────────────────────────────────╮
│  Component           │  Role                                      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  engine.py           │  pyswisseph calculations. Unchanged from   │
│                      │  v1. Returns state dict from calculate_all │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  data.py             │  Lookup tables, constants, widget registry │
│                      │  Unchanged from v1.                        │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  state.py            │  Shared file IPC. Reads/writes             │
│                      │  ~/.vigilarum/state.json. Unchanged from   │
│                      │  v1 except read_state return type hint.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  control.py          │  PyQt6. Runs engine, writes state, hosts   │
│                      │  widget assignment UI. One instance only.  │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  display.py          │  PyQt6. Renders assigned widgets. N        │
│                      │  instances allowed, one per display ID.    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  widgets.py          │  All QWidget subclasses. One class per     │
│                      │  widget type. Text cards + painted visuals │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  painters.py         │  NEW. All QPainter drawing functions.      │
│                      │  Pure functions: (painter, rect, state)    │
│                      │  → None. No widget logic here.             │
╰──────────────────────┴────────────────────────────────────────────╯
```

---

## 2. TECH STACK

```
╭──────────────────────┬─────────┬───────────────────────────────────╮
│  Tool                │ Version │  Justification                    │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Python              │ 3.11+   │  CastrumDigitos baseline          │
│  PyQt6               │ 6.x     │  Standard Exocognii framework     │
│  pyswisseph          │ local   │  Vedic/sidereal ephemeris         │
│  json                │ stdlib  │  State file IPC                   │
│  pathlib             │ stdlib  │  Path resolution                  │
│  datetime            │ stdlib  │  UTC time handling                │
│  math                │ stdlib  │  Painter geometry                 │
│  threading           │ stdlib  │  Engine worker thread             │
╰──────────────────────┴─────────┴───────────────────────────────────╯
```

No new pip dependencies beyond v1 requirements.

---

## 3. DIRECTORY TREE

```
Exocognii/Vigilarum/
├── control.py              — PyQt6 control panel. Runs engine, writes state.
├── display.py              — PyQt6 display window. Reads state, renders widgets.
├── widgets.py              — All QWidget subclasses. Text cards + visual widgets.
├── painters.py             — NEW. Pure QPainter drawing functions.
├── engine.py               — Unchanged. pyswisseph calculation engine.
├── data.py                 — Unchanged. Lookup tables, widget registry.
├── state.py                — Unchanged (minor type hint fix). File IPC layer.
├── dependencies.sh         — pip install targets.
├── Vigilarum.sh            — Launch script for control panel.
└── Referentia/
    ├── Vigilarum-dux.tome.md     — User manual (produced at completion)
    └── Vigilarum-Expositio.md    — Exposition document (produced at completion)
```

State files (runtime, not in repo):
```
~/.vigilarum/
├── state.json              — Shared state. Written by control, read by displays.
└── displays/
    ├── display_1.json      — Widget assignments + column count for display 1.
    └── display_N.json      — One file per display ID.
```

---

## 4. MODULE BREAKDOWN

```
╭───────────────┬────────────────────────────────┬────────────────────────────────┬──────────────────────────────────┬───────────────────────╮
│  Module       │  Responsibility                │  Inputs                        │  Outputs                         │  Dependencies         │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  engine.py    │  All pyswisseph calculations   │  datetime (UTC)                │  state dict (JSON-serialisable)  │  swisseph, math       │
│  data.py      │  Lookup tables, widget defs    │  None (module-level constants) │  Exported constants              │  None                 │
│  state.py     │  File IPC read/write           │  dict / display_id / wid str   │  dict / None                     │  json, pathlib        │
│  control.py   │  Engine runner, assignment UI  │  User clicks, QTimer ticks     │  state.json writes, display cfg  │  All modules, PyQt6   │
│  display.py   │  Widget renderer, state poller │  display_id arg, state.json    │  Painted window                  │  widgets, state, data │
│  widgets.py   │  All widget QWidget classes    │  state dict via update_data()  │  Painted widget surface          │  painters, data, Qt   │
│  painters.py  │  Pure drawing functions        │  QPainter, QRect, state dict   │  None (side effects on painter)  │  PyQt6, math, data    │
╰───────────────┴────────────────────────────────┴────────────────────────────────┴──────────────────────────────────┴───────────────────────╯
```

---

## 5. UI WIREFRAME

### Control Panel

```
╔══════════════════════════════════════════════════════════════════════╗
║  ◈  V I G I L A R U M   O M N I A  ◈                                 ║
║  Control Panel · Assign widgets to displays · Sidereal · Lahiri      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ── WIDGET ASSIGNMENTS ──────────────────────────  ── DISPLAYS ───   ║
║  Click a number to assign widget to that display.                    ║
║                                                                      ║
║  · TEMPORAL ·                                      Display 1         ║
║  Date & Time        [1] [2] [3] [4] [5]...         Cols: [2] [3] [4] ║
║  Season             [1] [2] [3] [4] [5]...                           ║
║  Sidereal Time      [1] [2] [3] [4] [5]...         Display 2         ║
║                                                    Cols: [2] [3] [4] ║
║  · LUNAR ·                                                           ║
║  Moon Phase         [1] [2] [3] [4] [5]...         Display 3         ║
║  Illumination       [1] [2] [3] [4] [5]...         Cols: [2] [3] [4] ║
║  Named Moon         [1] [2] [3] [4] [5]...                           ║
║  Moon Sign          [1] [2] [3] [4] [5]...         ... up to 9       ║
║  [scrollable list of all 38 widgets]                                 ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  XII∶XV  │  ❄ Winter  │  78% lit  │  ℞ 2  │  Writing → state.json    ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Display Window (2-column, 3 widgets shown)

```
╔══════════════════════════════════════════════════════════════════════╗
║   12:15:03  ·  ☉ Pisces  ·  🌔 Waxing Gibbous  ·  ☽ Cancer  ·  ℞×2   ║
╠══════════════════════════════════════════════════════════════════════╣
║  ◈  V I G I L A R U M  ·  D I S P L A Y  1  ◈                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌──────────────────────────┐  ┌──────────────────────────┐          ║
║  │  DATE & TIME             │  │  MOON PHASE              │          ║
║  │                          │  │  [painted disc]          │          ║
║  │  SUNDAY                  │  │                          │          ║
║  │  29 March MMXXVI         │  │  Waxing Gibbous          │          ║
║  │  XII∶XV∶III (UTC)        │  │  78% illuminated         │          ║
║  │  Ravivara                │  │  Day 12 of 29.5          │          ║
║  └──────────────────────────┘  └──────────────────────────┘          ║
║                                                                      ║
║  ┌──────────────────────────────────────────────────────────┐        ║
║  │  ZODIAC WHEEL  [full-width QPainter circular chart]      │        ║
║  │  [planets at correct angles, 12 sign sectors, gold ring] │        ║
║  └──────────────────────────────────────────────────────────┘        ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  Display 1  │  XII∶XV  │  78% lit  │  Pushya  │  Sun's hour          ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Widget Card Anatomy

```
┌─────────────────────────────────────────────┐
│  [SECTION MICRO-LABEL — UPPERCASE, DIM]      │
│  WIDGET TITLE                                │
│                                              │
│  [Primary content — largest text]            │
│  [Secondary content — body text]             │
│  [Tertiary / descriptor — dim]               │
└─────────────────────────────────────────────┘
```

**Legend:**
- `[1] [2]...` — clickable QPushButton assignment buttons; active = gold bold
- `Cols: [2] [3] [4]` — column count selector per display
- Top bar — celestial summary bar; updates every second
- Bottom status bar — display-specific context; updates every second
- Widget cards — QWidget subclasses with paintEvent or QLabel layout
- --bare mode — removes top bar, title, status bar; single widget fills window

---

## 6. DATA FLOW

### (a) Happy Path — Widget Renders Correctly

```
QTimer(60s) fires
  → EngineWorker.run() [QThread]
      → engine.calculate_all(datetime.now(UTC))
          → pyswisseph calls (Lahiri sidereal)
          → Returns state dict
      → state.write_state(data)         [atomic JSON write to ~/.vigilarum/state.json]
  → EngineWorker.finished signal → ControlApp._update_status()

QTimer(1s) fires in DisplayApp
  → state.read_state()                  [reads state.json]
  → read_display_config(display_id)     [reads display_N.json]
  → for each assigned wid:
      → widget.update_data(state)       [stores state, calls self.update()]
      → paintEvent fires
          → painters.draw_[type](painter, rect, state)
          → Painted to screen
```

### (b) pyswisseph Error

```
EngineWorker.run()
  → swe.calc_ut() raises exception
  → Caught in run(), emits error_signal(str)
  → ControlApp.on_engine_error() receives message
  → Status bar shows: "⚠  Engine error — {msg}"
  → Last good state.json preserved (no write on error)
  → DisplayApp continues polling, renders last good state
  → Next QTimer(60s) tick retries
```

### (c) State File Missing / Corrupt

```
DisplayApp QTimer(1s) fires
  → state.read_state() returns None (file missing or JSON invalid)
  → DisplayApp._poll_state() checks for None
  → Each widget.update_data(None) called
  → Widget paintEvent checks: if state is None → renders "Awaiting data..." placeholder
  → Status bar shows: "⚠  Awaiting state — launch control.py"
  → No crash. Polling continues.
```

---

## 7. CODE STUBS

### painters.py

```python
#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                              painters.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
import math
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
from PyQt6.QtCore import Qt, QRectF, QPointF

# Colour constants (Chromata Arcana)
C_BG        = QColor("#050507")
C_PANEL     = QColor("#0a0a12")
C_GOLD      = QColor("#d4af37")
C_GOLD_DIM  = QColor("#7a6a2a")
C_GOLD_DARK = QColor("#3a2e10")
C_CRIMSON   = QColor("#8b1a1a")
C_TEAL      = QColor("#1a5a5a")
C_TEXT      = QColor("#c8b88a")
C_WHITE     = QColor("#e8e0cc")
C_SUBTLE    = QColor("#3a3528")


def draw_moon_disc(painter: QPainter, rect: QRectF, angle: float) -> None:
    """
    Render moon disc with correct terminator.
    angle: elongation 0=new, 180=full.
    Lit side rendered with gradient; dark side solid near-black.
    """

def draw_zodiac_wheel(painter: QPainter, rect: QRectF, state: dict) -> None:
    """
    Circular zodiac chart.
    12 equal sectors with sign glyphs on outer ring.
    Planet glyphs positioned at correct sidereal longitudes.
    Gold ring border. Background void.
    """

def draw_moon_arc(painter: QPainter, rect: QRectF, angle: float,
                  cycle_day: int) -> None:
    """
    Horizontal arc gauge showing moon cycle progress.
    Phase glyphs at 8 equidistant positions.
    Progress fill in gold; current position marker.
    """

def draw_nakshatra_ring(painter: QPainter, rect: QRectF,
                        moon_lon: float, sun_lon: float) -> None:
    """
    27-segment ring. Each segment = one nakshatra (13.3°).
    Moon segment highlighted gold. Sun segment highlighted amber.
    Name abbreviations around inner ring.
    """

def draw_tithi_dial(painter: QPainter, rect: QRectF,
                    tithi_num: int, paksha: str) -> None:
    """
    30-division circular dial. Pointer at current tithi.
    Shukla (waxing) half lighter; Krishna (waning) half darker.
    """

def draw_eclipse_gauge(painter: QPainter, rect: QRectF,
                       dist: float, in_season: bool) -> None:
    """
    Radial proximity gauge. 0° = at node (eclipse), 18° = outer edge.
    In-season: crimson highlight. Out of season: dim.
    """

def draw_planet_strip(painter: QPainter, rect: QRectF,
                      lons: dict) -> None:
    """
    Horizontal zodiac strip 0°–360°.
    One lane per planet. Glyph at correct longitude.
    Sign divisions marked at 30° intervals.
    """

def draw_moon_distance_gauge(painter: QPainter, rect: QRectF,
                             dist_km: int, dist_pct: float,
                             label: str) -> None:
    """
    Simple linear gauge: perigee ←——◆——→ apogee.
    Current distance labelled below. Label (Supermoon/Micromoon/Average) above.
    """

def _draw_planet_glyph(painter: QPainter, cx: float, cy: float,
                        glyph: str, color: QColor = None) -> None:
    """Place a planet glyph at (cx, cy). Internal helper."""

def _sector_polygon(cx: float, cy: float, r_inner: float, r_outer: float,
                    angle_start: float, angle_end: float) -> list[QPointF]:
    """Return polygon points for an annular sector. Internal helper."""
```

### widgets.py (key classes)

```python
#!/usr/bin/env python3
# ╌╌╌ header ╌╌╌
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPalette, QColor, QFont
from painters import *


class ArcaneCard(QWidget):
    """
    Base class for all Vigilarum widget cards.
    Draws the gold-border panel background via paintEvent.
    Subclasses either override paintEvent for visual widgets
    or add QLabel children for text widgets.
    """
    def __init__(self, wid: str, label: str, section: str, parent=None):
        """Initialise with widget id, display label, section name."""

    def update_data(self, state: dict | None) -> None:
        """Receive new state dict. Store and trigger repaint."""

    def paintEvent(self, event) -> None:
        """Draw panel background, border, section micro-label, title."""

    def _draw_placeholder(self, painter: QPainter) -> None:
        """Render 'Awaiting data...' when state is None."""


class TextCard(ArcaneCard):
    """
    Text-content widget. Manages a QVBoxLayout of QLabels.
    Subclasses populate self._labels in _build_layout().
    """
    def _build_layout(self) -> None:
        """Called once on init. Subclass overrides to add labels."""

    def _update_labels(self, state: dict) -> None:
        """Called by update_data when state is not None. Update label text."""


class VisualCard(ArcaneCard):
    """
    Painter-content widget. Delegates drawing to painters.py.
    Subclasses set self._draw_fn to the appropriate painter function.
    """
    def paintEvent(self, event) -> None:
        """Call super for background, then self._draw_fn(painter, rect, state)."""


# --- Text card implementations ---

class DateTimeCard(TextCard):
    """TEMPORAL · Date & Time. Weekday, date in Modus Arcanus style, UTC time."""

class SeasonCard(TextCard):
    """TEMPORAL · Season. Name, glyph, days to transition, span label."""

class SiderealTimeCard(TextCard):
    """TEMPORAL · Sidereal Time. GST in hours:minutes:seconds."""

class MoonPhaseCard(TextCard):
    """LUNAR · Moon Phase. Phase name, glyph, illumination percent."""

class IlluminationCard(TextCard):
    """LUNAR · Illumination. Numeric % with simple text bar."""

class NamedMoonCard(TextCard):
    """LUNAR · Named Moon. Monthly moon name and descriptor."""

class MoonSignCard(TextCard):
    """LUNAR · Moon Sign. Sign name, glyph, degrees, nakshatra."""

class MoonNakshatraCard(TextCard):
    """LUNAR · Moon Nakshatra. Name, ruler, pada, descriptor."""

class NextMoonCard(TextCard):
    """LUNAR · Next Moon Event. Days to next new or full moon."""

class SunSignCard(TextCard):
    """SOLAR · Sun Sign. Sign, degrees, nakshatra."""

class SunNakshatraCard(TextCard):
    """SOLAR · Sun Nakshatra. Name, ruler, pada, descriptor."""

class PlanetCard(TextCard):
    """PLANETS · Single planet. Sign, degrees, Rx indicator."""
    def __init__(self, planet_name: str, **kwargs): ...

class MercuryPhaseCard(TextCard):
    """PLANETS · Mercury Phase. Morning/Evening star, elongation."""

class VenusPhaseCard(TextCard):
    """PLANETS · Venus Phase. Morning/Evening star, elongation."""

class OuterPlanetsCard(TextCard):
    """PLANETS · Outer planets summary. Uranus, Neptune, Pluto signs."""

class RetrogradeCard(TextCard):
    """PLANETS · Retrograde. List of currently Rx planets."""

class AspectsCard(TextCard):
    """PLANETS · Aspects. Active aspects with orbs."""

class RahuKetuCard(TextCard):
    """NODES · Rahu & Ketu. Sign positions, axis description."""

class PanchangCard(TextCard):
    """PANCHANG · Full Panchang summary. Tithi, vara, yoga, karana."""

class TithiCard(TextCard):
    """PANCHANG · Tithi. Name, number, paksha, quality."""

class VaraCard(TextCard):
    """PANCHANG · Vara. Day ruler, vara name, descriptor."""

class YogaCard(TextCard):
    """PANCHANG · Yoga. Name, quality."""

class KaranaCard(TextCard):
    """PANCHANG · Karana. Name."""

class RahuKalamCard(TextCard):
    """PANCHANG · Rahu Kalam. Time window, active indicator."""

class PlanetaryHourCard(TextCard):
    """PANCHANG · Planetary Hour. Current ruling planet."""

class DayRulerCard(TextCard):
    """PANCHANG · Day Ruler. Planet and vara."""

class SeasonalPaletteCard(TextCard):
    """AESTHETIC · Seasonal Palette. Season colour swatches as filled rects."""


# --- Visual card implementations ---

class MoonDiscCard(VisualCard):
    """VISUAL · Moon Disc. Painted ellipse with terminator gradient."""

class MoonArcCard(VisualCard):
    """VISUAL · Moon Cycle Arc. Horizontal arc gauge, phase markers."""

class ZodiacWheelCard(VisualCard):
    """VISUAL · Zodiac Wheel. Circular chart with sectors and planet glyphs."""

class NakshatraRingCard(VisualCard):
    """VISUAL · Nakshatra Ring. 27-segment annular ring chart."""

class TithiDialCard(VisualCard):
    """VISUAL · Tithi Dial. 30-division circular dial with pointer."""

class EclipseGaugeCard(VisualCard):
    """VISUAL · Eclipse Gauge. Proximity gauge to nearest node."""

class PlanetStripCard(VisualCard):
    """VISUAL · Planet Strip. Horizontal zodiac lanes per planet."""

class MoonDistanceCard(VisualCard):
    """VISUAL · Moon Distance. Linear gauge perigee→apogee."""

class EclipseProximityCard(TextCard):
    """NODES · Eclipse Proximity. Text summary + active warning."""


# Widget factory
WIDGET_CLASS_MAP: dict[str, type[ArcaneCard]] = {
    "datetime":       DateTimeCard,
    "season":         SeasonCard,
    "sidereal_time":  SiderealTimeCard,
    "moon_phase":     MoonPhaseCard,
    "illumination":   IlluminationCard,
    "named_moon":     NamedMoonCard,
    "moon_sign":      MoonSignCard,
    "moon_nakshatra": MoonNakshatraCard,
    "next_moon":      NextMoonCard,
    "sun_sign":       SunSignCard,
    "sun_nakshatra":  SunNakshatraCard,
    "mercury":        PlanetCard,
    "mercury_phase":  MercuryPhaseCard,
    "venus":          PlanetCard,
    "venus_phase":    VenusPhaseCard,
    "mars":           PlanetCard,
    "jupiter":        PlanetCard,
    "saturn":         PlanetCard,
    "outer_planets":  OuterPlanetsCard,
    "retrograde":     RetrogradeCard,
    "aspects":        AspectsCard,
    "rahu_ketu":      RahuKetuCard,
    "eclipse_prox":   EclipseProximityCard,
    "panchang":       PanchangCard,
    "tithi":          TithiCard,
    "vara":           VaraCard,
    "yoga":           YogaCard,
    "karana":         KaranaCard,
    "rahu_kalam":     RahuKalamCard,
    "planetary_hour": PlanetaryHourCard,
    "day_ruler":      DayRulerCard,
    "zodiac_wheel":   ZodiacWheelCard,
    "moon_disc":      MoonDiscCard,
    "moon_arc":       MoonArcCard,
    "nakshatra_ring": NakshatraRingCard,
    "tithi_dial":     TithiDialCard,
    "eclipse_gauge":  EclipseGaugeCard,
    "planet_strip":   PlanetStripCard,
    "palette":        SeasonalPaletteCard,
}

def make_widget(wid: str, parent=None) -> ArcaneCard:
    """Instantiate the correct ArcaneCard subclass for a given widget id."""
```

### control.py (skeleton)

```python
#!/usr/bin/env python3
# ╌╌╌ header ╌╌╌
import sys, os
from pathlib import Path
from datetime import datetime, timezone
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QScrollArea, QPushButton, QLabel,
                              QFrame, QStatusBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from engine import calculate_all, to_roman
from state import (write_state, read_display_config, assign_widget,
                   get_widget_display, set_display_columns, ensure_dirs)
from data import WIDGET_DEFS, SEASON_GLYPHS, SEASON_NAMES

MAX_DISPLAYS = 9


class EngineWorker(QThread):
    """Runs calculate_all off the main thread."""
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def run(self) -> None:
        """Call calculate_all, emit finished or error."""


class AssignButton(QPushButton):
    """Single display assignment button. Gold when active, dim otherwise."""
    def __init__(self, wid: str, disp_id: int, parent=None):
        """Store wid and disp_id. Connect clicked to _on_click."""

    def refresh_state(self) -> None:
        """Check current assignment; update style accordingly."""

    def _on_click(self) -> None:
        """Toggle assignment. If already assigned here, unassign (0)."""


class ColButton(QPushButton):
    """Column count selector for a display. Gold when active."""
    def __init__(self, disp_id: int, cols: int, parent=None): ...
    def refresh_state(self) -> None: ...


class ControlWindow(QMainWindow):
    """Main control panel window."""
    def __init__(self):
        """Build layout. Start engine timer (60s). Start clock timer (1s)."""

    def _build_ui(self) -> None:
        """Construct left (widget list) + right (display config) panels."""

    def _start_engine(self) -> None:
        """Fire EngineWorker immediately, then every 60s via QTimer."""

    def _on_engine_finished(self, data: dict) -> None:
        """Receive state dict from worker. write_state(). Update status bar."""

    def _on_engine_error(self, msg: str) -> None:
        """Display error in status bar. Do not write state."""

    def _tick_clock(self) -> None:
        """Update now_dt in last state, write_state, update status bar."""

    def refresh_widget_row(self, wid: str) -> None:
        """Refresh all AssignButtons for a given widget id."""

    def refresh_col_row(self, disp_id: int) -> None:
        """Refresh all ColButtons for a given display id."""
```

### display.py (skeleton)

```python
#!/usr/bin/env python3
# ╌╌╌ header ╌╌╌
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                              QScrollArea, QGridLayout, QLabel, QStatusBar)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPalette, QColor

from state import read_state, read_display_config, write_display_config
from widgets import make_widget, ArcaneCard
from data import WIDGET_DEFS, MOON_PHASE_GLYPHS, MOON_PHASE_NAMES, SIGN_NAMES, TITHI_NAMES
from engine import to_roman


class DisplayWindow(QMainWindow):
    """Single display window. Polls state, renders assigned widgets."""

    def __init__(self, display_id: int, bare: bool = False):
        """Store display_id, bare flag. Build UI. Start poll timer (1s)."""

    def _build_ui(self) -> None:
        """
        Normal mode: celestial bar (dock top) + title + grid + status bar.
        Bare mode: grid fills entire window, no chrome.
        """

    def _poll_state(self) -> None:
        """
        Read state.json and display config.
        If widget list changed: remount widgets.
        Call update_data on all mounted widgets.
        Update chrome bars.
        """

    def _remount_widgets(self, new_wids: list[str]) -> None:
        """
        Clear grid. Instantiate widgets from WIDGET_CLASS_MAP.
        Handle empty list (show placeholder label).
        """

    def _update_bars(self, state: dict) -> None:
        """Format and set celestial bar and status bar text."""
```

---

## 8. ERROR HANDLING

```
╭────────────────────────┬──────────────────────────────────────┬────────────────────────────────────────╮
│  Module / Scope        │  Error                               │  Strategy                              │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  EngineWorker.run()    │  pyswisseph raises any exception     │  Catch all, emit error_signal(str).    │
│                        │                                      │  Do not write state. Status bar shows  │
│                        │                                      │  ⚠ message. Retry next tick.           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  state.read_state()    │  File missing, JSON decode error     │  Returns None. Caller checks. No       │
│                        │                                      │  crash. Display shows placeholder.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  state.write_state()   │  Disk full, permissions error        │  Log to stderr. Do not raise. Last     │
│                        │                                      │  good state remains on disk.           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  painters.py           │  Division by zero in geometry        │  Guard all divisions: if total == 0    │
│                        │                                      │  return early or use safe default.     │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  ArcaneCard.paintEvent │  Exception during painting           │  Wrap in try/except. Draw error        │
│                        │                                      │  glyph (⚠) in card centre. No crash.   │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  display._poll_state() │  Widget not found in grid (stale id) │  Catch LookupError, remount.           │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Startup               │  pyswisseph not importable           │  ImportError caught in control.py      │
│                        │                                      │  main(). Print message to stderr.      │
│                        │                                      │  sys.exit(1). Do not launch window.    │
╰────────────────────────┴──────────────────────────────────────┴────────────────────────────────────────╯
```

---

## 9. SETUP & TESTING

### requirements.txt

```
PyQt6>=6.4.0
pyswisseph
```

### Install

```bash
pip install PyQt6 --break-system-packages
pip install pyswisseph --break-system-packages
```

### Run

```bash
# Control panel (run first)
python3 control.py

# Display window (run one or more)
python3 display.py 1
python3 display.py 2 --bare
```

### Test stubs

```python
# tests/test_engine.py
def test_calculate_all_returns_expected_keys():
    """calculate_all should return dict with moon_phase_idx, sun_sign, etc."""

def test_to_roman():
    """to_roman(12) == 'XII', to_roman(0) == 'O'"""

# tests/test_state.py
def test_write_read_roundtrip(tmp_path, monkeypatch):
    """write_state then read_state returns equivalent dict."""

def test_read_state_missing_file_returns_none(tmp_path, monkeypatch):
    """read_state returns None when file does not exist."""

def test_assign_widget_moves_between_displays():
    """Assigning wid to display 2 removes it from display 1."""

# tests/test_painters.py
def test_draw_moon_disc_does_not_raise():
    """draw_moon_disc completes without exception for angles 0–360."""

def test_draw_zodiac_wheel_handles_empty_lons():
    """draw_zodiac_wheel with empty lons dict does not crash."""
```

---

## 10. PACKAGING

```bash
# .desktop file
[Desktop Entry]
Name=Vigilarum Omnia
Comment=Vedic sidereal astronomical display
Exec=python3 /home/lordfingers/ArcaCognitorium/Exocognii/Vigilarum/control.py
Icon=vigilarum
Terminal=false
Type=Application
Categories=Utility;Science;
```

Application is script-launched, not bundled. No PyInstaller needed for internal use.

---

## 11. EXTENSIBILITY

```
╭────────────────────────────┬───────────────────────────────────────┬──────────────────────────────────────────────────────────────────────╮
│  Feature                   │  User Value                           │  Implementation Approach                                             │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Machinae Integration      │  Vigilarum state.json becomes input   │  Add a read path from ~/.vigilarum/state.json into the Machinae      │
│                            │  source for CAELESTIS. One-way bridge │  CAELESTIS module once built. Vigilarum writes; CAELESTIS reads.     │
│                            │  from demonstration to Tower input.   │  No change to Vigilarum itself — Vigilarum remains standalone.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Location-aware Sunrise    │  Rahu Kalam and planetary hour        │  Add lat/lon to ~/.arca/config.json. Pass to engine. Use             │
│                            │  calculated from actual local sunrise │  swe.rise_trans() for local sunrise/sunset. Replace fixed 06:00      │ 
│                            │  rather than fixed 06:00 assumption.  │  offset in get_planetary_hour() and get_rahu_kalam().                │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Widget Layout Persistence │  Display layout survives restart      │  Already handled by display_N.json. Add drag-to-reorder in grid.     │
│                            │  and can be rearranged by drag.       │  QDrag + dropEvent on widget cards. Write new order to config.       │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Gochara / Transit Alerts  │  Notify when significant transits     │  Add a transit_checker module. On each engine tick, compare current  │
│                            │  occur — sign changes, conjunctions.  │  positions against previous. Emit QSystemTrayIcon notification.      │
├┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┼┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┤
│  Praesidium Widget         │  Add a Vigilarum-sourced celestial    │  New Praesidium widget that reads ~/.vigilarum/state.json directly.  │
│                            │  summary widget to the Praesidium     │  Displays moon phase glyph, current Nakshatra, active Rx. Read-only  │
│                            │  dashboard.                           │  consumer. No coupling to Vigilarum code.                            │
╰────────────────────────────┴───────────────────────────────────────┴──────────────────────────────────────────────────────────────────────╯
```

---

## COMPLETION STAMP

```
╭─────────────────────────────────────────────────────────────╮
│  VIGILARUM V2 — IdeaForge Build Document                    │
│  Status:   COMPLETE                                         │
│  Date:     MMXXVI · March 29                                │
│  Phase:    ::THEORY Complete — Ready for ::BUILD            │
│  Author:   The Builder                                      │
╰─────────────────────────────────────────────────────────────╯
```

*Ordo Discordia, Cosmos Inania*
