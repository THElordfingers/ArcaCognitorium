"""
 ____      ____  _____  ______      ______  ________  _________   ______                      
|_  _|    |_  _||_   _||_   _ `.  .' ___  ||_   __  ||  _   _  |.' ____ \                     
  \ \  /\  / /    | |    | | `. \/ .'   \_|  | |_ \_||_/ | | \_|| (___ \_|   _ .--.   _   __  
   \ \/  \/ /     | |    | |  | || |   ____  |  _| _     | |     _.____`.   [ '/'`\ \[ \ [  ] 
    \  /\  /     _| |_  _| |_.' /\ `.___]  |_| |__/ |   _| |_   | \____) | _ | \__/ | \ '/ /  
     \/  \/     |_____||______.'  `._____.'|________|  |_____|   \______.'(_)| ;.__/[\_:  /   
                                                                            [__|     \__.' 



VIGILARUM OMNIA — Widget Renderers
CelWidget: a Textual Static that renders any celestial indicator.
"""

from textual.widgets import Static
from engine import to_roman, make_bar
from data import (
    PLANET_GLYPHS, SIGN_GLYPHS, SIGN_NAMES,
    MOON_PHASE_GLYPHS, MOON_PHASE_NAMES, NAMED_MOONS,
    SEASON_NAMES, SEASON_SPANS, SEASON_COLS, SEASON_GLYPHS,
    NAKSHATRAS, TITHI_NAMES, TITHI_QUALITY, TITHI_DESC,
    YOGA_NAMES, YOGA_QUALITY, KARANA_NAMES,
    VARA_NAMES, VARA_DESC, PLANETARY_HOUR_SEQ,
)
from renderers import (
    render_moon_disc, render_zodiac_wheel, render_moon_arc,
    render_nakshatra_ring, render_tithi_dial,
    render_eclipse_gauge, render_planet_strip,
)
from engine import get_nakshatra


class CelWidget(Static):
    def __init__(self, wid: str, label: str, category: str, **kwargs):
        super().__init__(**kwargs)
        self.wid       = wid
        self.label     = label
        self.category  = category
        self._selected = False
        self.add_class("cel_widget")

    def header(self) -> str:
        return f"[dim]{self.label}  ·  {self.category}[/dim]\n"

    def render_content(self, d: dict) -> str:
        try:
            m = getattr(self, f"_r_{self.wid}", None)
            if m:
                return self.header() + m(d)
            return self.header() + "[dim]─[/dim]"
        except Exception as e:
            return self.header() + f"[red]err: {e}[/red]"

    def update_data(self, d: dict):
        self.update(self.render_content(d))

    def set_selected(self, sel: bool):
        self._selected = sel
        if sel:
            self.remove_class("cel_widget")
            self.add_class("cel_widget_selected")
        else:
            self.remove_class("cel_widget_selected")
            self.add_class("cel_widget")

    def on_click(self):
        self.app.widget_clicked(self.wid)

    # ── TEMPORAL ──────────────────────────────────────────────────────────────

    def _r_datetime(self, d):
        ts  = d["now_str"]
        now = d["now_dt"]
        h24 = f"{now['h']:02d}:{now['m']:02d}:{now['s']:02d}"
        h   = to_roman(now['h']) if now['h'] > 0 else "XII"
        m   = to_roman(now['m']) if now['m'] > 0 else "O"
        s   = to_roman(now['s']) if now['s'] > 0 else "O"
        return (f"[white]{h24}  UTC[/white]\n"
                f"[yellow]{h} ∶ {m} ∶ {s}[/yellow]\n"
                f"[white]{to_roman(now['day'])} · {to_roman(now['mo'])} · {to_roman(now['yr'])}[/white]\n"
                f"[dim]{now['weekday']}, {now['day']:02d} {now['month_name']} {now['yr']}[/dim]")

    def _r_season(self, d):
        idx  = d["season_idx"]; days = d["season_days"]
        col  = SEASON_COLS[idx]; g = SEASON_GLYPHS[idx]
        return (f"[{col}]{g}  {SEASON_NAMES[idx].upper()}[/{col}]\n"
                f"[dim]{SEASON_SPANS[idx]}[/dim]\n"
                f"[white]{to_roman(days)} days to next turning[/white]\n"
                f"[dim]Solar calendar[/dim]")

    def _r_sidereal_time(self, d):
        h, m, s = d["sidereal_h"], d["sidereal_m"], d["sidereal_s"]
        return (f"[yellow]{to_roman(h)} ∶ {to_roman(m)} ∶ {to_roman(s)}[/yellow]\n"
                f"[dim]{h:02d}:{m:02d}:{s:02d} GST[/dim]\n"
                f"[white]Greenwich Sidereal Time[/white]\n"
                f"[dim]Earth's rotation vs fixed stars[/dim]")

    # ── LUNAR ─────────────────────────────────────────────────────────────────

    def _r_moon_phase(self, d):
        idx  = d["moon_phase_idx"]
        g    = MOON_PHASE_GLYPHS[idx]
        name = MOON_PHASE_NAMES[idx]
        day  = d["moon_cycle_day"]
        cols = ["blue","cyan","green","green","yellow","cyan","cyan","blue"]
        desc = ["Dark. Seed time.","Growth beginning.","Decision point.",
                "Building to fullness.","Peak. Culmination.","Releasing.",
                "Reflection.","Returning to dark."]
        return (f"[{cols[idx]}]{g}  {name}[/{cols[idx]}]\n"
                f"[dim]Day {day} of 29.5-day cycle[/dim]\n"
                f"[white]{desc[idx]}[/white]\n"
                f"[dim]{d['moon_angle']:.1f}° elongation from Sun[/dim]")

    def _r_illumination(self, d):
        pct = d["illumination"]
        bar = make_bar(pct, 100, 28)
        return (f"[yellow]{pct:.1f}% illuminated[/yellow]\n"
                f"{bar}\n"
                f"[dim]0% = New Moon · 100% = Full Moon[/dim]\n"
                f"[dim]Fraction of lunar face lit by Sun[/dim]")

    def _r_named_moon(self, d):
        mo   = d["now_dt"]["mo"]
        name, desc = NAMED_MOONS.get(mo, ("─","─"))
        month = d["now_dt"]["month_name"]
        return (f"[yellow]☽  {name}[/yellow]\n"
                f"[dim]{month} full moon[/dim]\n"
                f"[white]{desc}[/white]\n"
                f"[dim]Traditional North American name[/dim]")

    def _r_moon_sign(self, d):
        si = d["moon_sign"]; deg = d["moon_deg"]
        return (f"[yellow]{SIGN_GLYPHS[si]}  {SIGN_NAMES[si]}[/yellow]\n"
                f"[dim]{deg:.2f}° within sign[/dim]\n"
                f"[white]Changes sign every ~2.5 days[/white]\n"
                f"[dim]Sidereal · Lahiri Ayanamsha[/dim]")

    def _r_moon_nakshatra(self, d):
        idx, pada = get_nakshatra(d["moon_lon"])
        name, ruler, desc = NAKSHATRAS[idx]
        return (f"[yellow]☽  {name}[/yellow]  Pada {to_roman(pada)}\n"
                f"[dim]Ruled by {ruler} · #{idx+1} of 27[/dim]\n"
                f"[white]{desc}[/white]\n"
                f"[dim]Vedic lunar mansion · ~13.3° each[/dim]")

    def _r_moon_distance(self, d):
        km   = d["moon_dist_km"]; pct = d["moon_dist_pct"]
        label= d["moon_dist_label"]; desc = d["moon_dist_desc"]
        g    = d["moon_dist_glyph"]
        sign = "+" if pct >= 0 else ""
        col  = "yellow" if abs(pct) > 3 else "white"
        bar  = make_bar(abs(pct), 10, 28)
        return (f"[{col}]{g}  {label}[/{col}]\n"
                f"[dim]{km:,} km  ({sign}{pct:.1f}%)[/dim]\n"
                f"{bar}\n"
                f"[dim]Avg: 384,400 km · {desc}[/dim]")

    def _r_next_moon(self, d):
        angle = d["moon_angle"]
        event, g = ("Full Moon","🌕") if angle < 180 else ("New Moon","🌑")
        days  = d.get("days_to_next_moon","?")
        return (f"[yellow]{g}  {event}[/yellow]\n"
                f"[white]~{days} day(s) away[/white]\n"
                f"[dim]{angle:.1f}° current elongation[/dim]\n"
                f"[dim]Full=180° · New=0° from Sun[/dim]")

    # ── SOLAR ─────────────────────────────────────────────────────────────────

    def _r_sun_sign(self, d):
        si = d["sun_sign"]; deg = d["sun_deg"]
        return (f"[yellow]{SIGN_GLYPHS[si]}  {SIGN_NAMES[si]}[/yellow]\n"
                f"[dim]{deg:.2f}° within sign[/dim]\n"
                f"[white]Sun moves ~1° per day[/white]\n"
                f"[dim]Sidereal · ~23° behind Western[/dim]")

    def _r_sun_nakshatra(self, d):
        idx, pada = get_nakshatra(d["sun_lon"])
        name, ruler, desc = NAKSHATRAS[idx]
        return (f"[yellow]☉  {name}[/yellow]  Pada {to_roman(pada)}\n"
                f"[dim]Ruled by {ruler} · #{idx+1} of 27[/dim]\n"
                f"[white]{desc}[/white]\n"
                f"[dim]Sun takes ~13 days per nakshatra[/dim]")

    # ── PLANETS ───────────────────────────────────────────────────────────────

    def _planet(self, d, name):
        k = name.lower()
        if f"{k}_sign" not in d:
            return f"[dim]{name}: no data[/dim]"
        si  = d[f"{k}_sign"]; deg = d[f"{k}_deg"]; rx = d[f"{k}_rx"]
        g   = PLANET_GLYPHS.get(name, "·")
        rxs = "[red]℞ Retrograde[/red]" if rx else "[green]→ Direct[/green]"
        descs = {
            "Mercury": "Thought, communication, commerce",
            "Venus":   "Beauty, desire, creativity",
            "Mars":    "Drive, courage, conflict",
            "Jupiter": "Expansion, wisdom, fortune",
            "Saturn":  "Discipline, limits, long time",
        }
        return (f"[yellow]{g}  {name} in {SIGN_NAMES[si]}[/yellow]\n"
                f"[dim]{deg:.2f}°  {rxs}\n"
                f"[white]{descs.get(name,'')}[/white]\n"
                f"[dim]Sidereal · Lahiri[/dim]")

    def _r_mercury(self, d): return self._planet(d, "Mercury")
    def _r_venus(self,   d): return self._planet(d, "Venus")
    def _r_mars(self,    d): return self._planet(d, "Mars")
    def _r_jupiter(self, d): return self._planet(d, "Jupiter")
    def _r_saturn(self,  d): return self._planet(d, "Saturn")

    def _inner_phase(self, d, name, key):
        phase = d[f"{key}_phase_name"]
        g     = d[f"{key}_phase_glyph"]
        elong = d[f"{key}_elong"]
        desc  = d[f"{key}_phase_desc"]
        bar   = make_bar(elong, 47, 28)
        return (f"[yellow]{g}  {name}: {phase}[/yellow]\n"
                f"{bar}\n"
                f"[dim]{elong:.1f}° elongation of 47° max[/dim]\n"
                f"[dim]{desc}[/dim]")

    def _r_mercury_phase(self, d): return self._inner_phase(d, "Mercury", "mercury")
    def _r_venus_phase(self,   d): return self._inner_phase(d, "Venus",   "venus")

    def _r_outer_planets(self, d):
        lines = []
        for name in ["Uranus","Neptune","Pluto"]:
            k   = name.lower()
            si  = d.get(f"{k}_sign", 0)
            deg = d.get(f"{k}_deg",  0)
            rx  = d.get(f"{k}_rx",   False)
            rxs = "[red]℞[/red]" if rx else "[green]→[/green]"
            lines.append(
                f"[yellow]{PLANET_GLYPHS[name]}[/yellow]"
                f" {SIGN_NAMES[si][:6]} {deg:.0f}° {rxs}")
        return '\n'.join(lines) + "\n[dim]Generational forces · decades per sign[/dim]"

    def _r_retrograde(self, d):
        rx = d.get("retrograde_list", [])
        if not rx:
            return "[green]All planets direct[/green]\n[dim]No retrogrades active[/dim]"
        body = "\n".join(
            f"[red]{PLANET_GLYPHS.get(p,'·')} {p}[/red]" for p in rx)
        return body + f"\n[dim]{len(rx)} currently retrograde[/dim]"

    def _r_aspects(self, d):
        aspects = d.get("aspects", [])
        if not aspects:
            return "[dim]No major aspects active[/dim]"
        lines = []
        for a, b, asp, diff in aspects[:5]:
            ga = PLANET_GLYPHS.get(a,'·'); gb = PLANET_GLYPHS.get(b,'·')
            lines.append(
                f"[yellow]{ga}{gb}[/yellow] [white]{asp}[/white] [dim]{diff}°[/dim]")
        return '\n'.join(lines) + f"\n[dim]{len(aspects)} active[/dim]"

    # ── NODES ─────────────────────────────────────────────────────────────────

    def _r_rahu_ketu(self, d):
        r_si  = d.get("rahu_sign", 0)
        r_deg = d.get("rahu_deg",  0)
        k_si  = (r_si + 6) % 12
        return (f"[yellow]☊  Rahu in {SIGN_NAMES[r_si]}[/yellow]  {r_deg:.1f}°\n"
                f"[yellow]☋  Ketu in {SIGN_NAMES[k_si]}[/yellow]\n"
                f"[white]Karmic axis · lunar nodes[/white]\n"
                f"[dim]Always opposite · ~18-month cycle[/dim]")

    def _r_eclipse_prox(self, d):
        in_s = d["eclipse_active"]; dist = d["eclipse_dist"]
        bar  = make_bar(max(0, 18 - dist), 18, 28)
        col  = "bold yellow" if in_s else "dim"
        stat = "⚠ ECLIPSE SEASON" if in_s else "Outside eclipse season"
        return (f"[{col}]{stat}[/{col}]\n"
                f"{bar}\n"
                f"[dim]Sun {dist:.1f}° from nearest node[/dim]\n"
                f"[dim]Eclipses occur within 18°[/dim]")

    # ── PANCHANG ──────────────────────────────────────────────────────────────

    def _r_panchang(self, d):
        tname = TITHI_NAMES[min(d["tithi_idx"], 14)]
        vara  = VARA_NAMES[d["day_idx"]]
        m_nak_idx, _ = get_nakshatra(d["moon_lon"])
        nak   = NAKSHATRAS[m_nak_idx][0]
        yoga  = YOGA_NAMES[d["yoga_idx"]]
        kar   = KARANA_NAMES[min(d["karana_idx"], 10)]
        return (f"[yellow]T[/yellow] [white]{tname}[/white]  "
                f"[yellow]V[/yellow] [white]{vara[:8]}[/white]\n"
                f"[yellow]N[/yellow] [white]{nak[:12]}[/white]  "
                f"[yellow]Y[/yellow] [white]{yoga[:10]}[/white]\n"
                f"[yellow]K[/yellow] [white]{kar}[/white]\n"
                f"[dim]Five limbs of Vedic timekeeping[/dim]")

    def _r_tithi(self, d):
        tnum    = d["tithi_num"]; tidx = d["tithi_idx"]; paksha = d["paksha"]
        name    = TITHI_NAMES[min(tidx, 14)]
        quality = TITHI_QUALITY[min(tidx, 14)]
        desc    = TITHI_DESC.get(quality, "")
        col     = "green" if quality in ("Nanda","Bhadra","Jaya","Purna") else "red"
        return (f"[yellow]{name}[/yellow]\n"
                f"[dim]{paksha} Paksha · #{tnum+1} of 30[/dim]\n"
                f"[{col}]{quality} — {desc}[/{col}]\n"
                f"[dim]Lunar day · Moon 12° from Sun[/dim]")

    def _r_vara(self, d):
        g = PLANET_GLYPHS.get(d["day_ruler"], "·")
        return (f"[yellow]{g}  {VARA_NAMES[d['day_idx']]}[/yellow]\n"
                f"[dim]Ruled by {d['day_ruler']}[/dim]\n"
                f"[white]{VARA_DESC[d['day_idx']]}[/white]\n"
                f"[dim]Vedic weekday[/dim]")

    def _r_yoga(self, d):
        yidx    = d["yoga_idx"]; quality = YOGA_QUALITY[yidx]
        col     = "green" if quality == "Auspicious" else "red"
        return (f"[yellow]{YOGA_NAMES[yidx]}[/yellow]\n"
                f"[{col}]{quality}[/{col}]\n"
                f"[dim]#{yidx+1} of 27 · ☉ + ☽ sum[/dim]\n"
                f"[dim]Changes as planets move[/dim]")

    def _r_karana(self, d):
        name = KARANA_NAMES[min(d["karana_idx"], 10)]
        return (f"[yellow]{name}[/yellow]\n"
                f"[dim]#{d['karana_idx']+1} · Half a Tithi[/dim]\n"
                f"[white]Changes approximately twice daily[/white]\n"
                f"[dim]11 types · 7 movable · 4 fixed[/dim]")

    def _r_rahu_kalam(self, d):
        start  = d["rahu_kalam_start"]; end = d["rahu_kalam_end"]
        active = d["rahu_kalam_active"]
        col    = "bold yellow" if active else "dim"
        stat   = "⚠  ACTIVE NOW" if active else "Inactive"
        return (f"[{col}]{stat}[/{col}]\n"
                f"[white]{start} – {end}[/white]\n"
                f"[dim]Inauspicious daily window[/dim]\n"
                f"[dim]Avoid important beginnings[/dim]")

    def _r_planetary_hour(self, d):
        planet = d["ph_planet"]
        g      = PLANET_GLYPHS.get(planet, "·")
        now    = d["now_dt"]
        descs  = {
            "Sun":    "Authority","Moon":   "Intuition",
            "Mercury":"Communication","Venus":"Beauty",
            "Mars":   "Action","Jupiter":"Wisdom","Saturn":"Discipline",
        }
        return (f"[yellow]{g}  {planet}'s Hour[/yellow]\n"
                f"[dim]Hour {to_roman(now['h'])} of the day[/dim]\n"
                f"[white]{descs.get(planet,'')}[/white]\n"
                f"[dim]24 planetary hours per day[/dim]")

    def _r_day_ruler(self, d):
        g = PLANET_GLYPHS.get(d["day_ruler"], "·")
        return (f"[yellow]{g}  {d['day_ruler']}[/yellow]\n"
                f"[dim]{VARA_NAMES[d['day_idx']]}[/dim]\n"
                f"[white]{VARA_DESC[d['day_idx']]}[/white]\n"
                f"[dim]Planetary day ruler[/dim]")

    # ── VISUAL ────────────────────────────────────────────────────────────────

    def _r_zodiac_wheel(self, d):
        return render_zodiac_wheel(d.get("all_lons", {}))

    def _r_moon_disc(self, d):
        angle = d.get("moon_angle", 0)
        disc  = render_moon_disc(angle)
        phase = MOON_PHASE_NAMES[d.get("moon_phase_idx", 0)]
        illum = d.get("illumination", 0)
        return f"{disc}\n[dim]{phase} · {illum:.1f}% lit[/dim]"

    def _r_moon_arc(self, d):
        return render_moon_arc(
            d.get("moon_angle", 0), d.get("moon_cycle_day", 1))

    def _r_nakshatra_ring(self, d):
        return render_nakshatra_ring(d.get("moon_lon", 0), d.get("sun_lon", 0))

    def _r_tithi_dial(self, d):
        return render_tithi_dial(d.get("tithi_num", 0), d.get("paksha","Shukla"))

    def _r_eclipse_gauge(self, d):
        return render_eclipse_gauge(d["eclipse_dist"], d["eclipse_active"])

    def _r_planet_strip(self, d):
        return render_planet_strip(d.get("all_lons", {}))

    # ── AESTHETIC ─────────────────────────────────────────────────────────────

    def _r_palette(self, d):
        idx   = d["season_idx"]; illum = d["illumination"]
        sat   = 0.4 + (illum / 100) * 0.6
        col   = SEASON_COLS[idx]; g = SEASON_GLYPHS[idx]
        name  = SEASON_NAMES[idx]
        bar   = make_bar(sat, 1.0, 28)
        return (f"[{col}]{g} {name.upper()}[/{col}]  [dim]sat {sat:.0%}[/dim]\n"
                f"[dim]Void[/dim]  [{col}]▒▒▒▒[/{col}]  [{col}]████[/{col}]\n"
                f"{bar}\n"
                f"[dim]{SEASON_SPANS[idx]}[/dim]")                                                                            
