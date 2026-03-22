#!/usr/bin/env python3
"""
 ______   _____   ______   _______  _____          _     ____  ____                   
|_   _ `.|_   _|.' ____ \ |_   __ \|_   _|        / \   |_  _||_  _|                  
  | | `. \ | |  | (___ \_|  | |__) | | |         / _ \    \ \  / /   _ .--.   _   __  
  | |  | | | |   _.____`.   |  ___/  | |   _    / ___ \    \ \/ /   [ '/'`\ \[ \ [  ] 
 _| |_.' /_| |_ | \____) | _| |_    _| |__/ | _/ /   \ \_  _|  |_  _ | \__/ | \ '/ /  
|______.'|_____| \______.'|_____|  |________||____| |____||______|(_)| ;.__/[\_:  /   
                                                                    [__|     \__.'   



VIGILARUM OMNIA — Display Terminal
A pure renderer. Reads state written by control.py.

Usage:
  python3 display.py <display_id>            # normal mode — bars + title
  python3 display.py <display_id> --bare     # bare mode — zero chrome, widget fills terminal

Examples:
  python3 display.py 1                       # Display 1, full chrome
  python3 display.py 2 --bare               # Display 2, no chrome — single widget fills window

Assign widgets to this display from the control panel.
The display polls ~/.vigilarum/state.json every second.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import ScrollableContainer, Horizontal
from datetime import datetime, timezone

from data import WIDGET_DEFS, MOON_PHASE_GLYPHS, MOON_PHASE_NAMES, SIGN_NAMES, TITHI_NAMES
from engine import to_roman
from widgets import CelWidget
from state import read_state, read_display_config, write_display_config


CSS_NORMAL = """
Screen {
    background: #0D0B0E;
    color: #c8b89a;
}
#celestial_bar {
    background: #08060a;
    color: #5a4a6a;
    height: 1;
    border-bottom: solid #1a1520;
    padding: 0 2;
    dock: top;
}
#display_title {
    background: #0D0B0E;
    color: #c8a84b;
    text-align: center;
    height: 2;
    border-bottom: solid #2a2030;
    padding: 0 1;
}
#widget_scroll { width: 1fr; height: 1fr; }
#widget_grid {
    width: 1fr;
    padding: 1 2;
    layout: grid;
    grid-size: 3;
    grid-gutter: 1 2;
}
.cel_widget {
    background: #100e13;
    border: solid #1e1b22;
    padding: 1 2;
}
.cel_widget_selected {
    background: #1a1228;
    border: solid #c8a84b;
    padding: 1 2;
}
.cel_widget:hover { border: solid #4a3a6a; background: #130f16; }
#status_bar {
    background: #08060a;
    color: #5a4a6a;
    height: 1;
    border-top: solid #1a1520;
    padding: 0 2;
    dock: bottom;
}
#no_widgets { color: #4a3a5a; text-align: center; padding: 4 8; }
"""

CSS_BARE = """
Screen {
    background: #0D0B0E;
    color: #c8b89a;
    padding: 0;
    margin: 0;
}
#widget_scroll {
    width: 1fr;
    height: 1fr;
    padding: 0;
    margin: 0;
}
#widget_grid {
    width: 1fr;
    height: 1fr;
    padding: 0;
    margin: 0;
    layout: grid;
    grid-size: 1;
    grid-gutter: 0;
}
.cel_widget {
    background: #100e13;
    border: solid #1e1b22;
    padding: 1 2;
    width: 1fr;
    height: 1fr;
}
.cel_widget_selected {
    background: #1a1228;
    border: solid #c8a84b;
    padding: 1 2;
    width: 1fr;
    height: 1fr;
}
.cel_widget:hover { border: solid #4a3a6a; background: #130f16; }
#no_widgets {
    color: #4a3a5a;
    text-align: center;
    padding: 2 4;
    width: 1fr;
    height: 1fr;
}
"""

WID_INFO = {wid: (label, section) for wid, label, section in WIDGET_DEFS}


class DisplayApp(App):

    def __init__(self, display_id: int, bare: bool = False):
        super().__init__()
        self.display_id = display_id
        self.bare       = bare
        self.CSS        = CSS_BARE if bare else CSS_NORMAL
        self.TITLE      = f"VIGILARUM · {display_id}"
        self._state:    dict = {}
        self._widgets:  list = []
        self._selected: str  = ""

    def compose(self) -> ComposeResult:
        if not self.bare:
            yield Static("", id="celestial_bar")
            yield Static(
                f"◈  V I G I L A R U M  ·  D I S P L A Y  {self.display_id}  ◈\n"
                f"[dim]Assign widgets from the control panel[/dim]",
                id="display_title"
            )
        with ScrollableContainer(id="widget_scroll"):
            yield Horizontal(id="widget_grid")
        if not self.bare:
            yield Static("", id="status_bar")

    def on_mount(self):
        self._poll_state()
        self.set_interval(1, self._poll_state)

    def _poll_state(self):
        state = read_state()
        cfg   = read_display_config(self.display_id)
        wids  = cfg.get("widgets", [])

        if not self.bare:
            cols = cfg.get("columns", 3)
            try:
                self.query_one("#widget_grid").styles.grid_size_columns = cols
            except Exception:
                pass

        if wids != self._widgets:
            self._remount_widgets(wids)

        if state:
            self._state = state
            self._update_widgets(state)
            if not self.bare:
                self._update_bars(state)

    def _remount_widgets(self, new_wids: list):
        try:
            grid = self.query_one("#widget_grid")
            for child in list(grid.children):
                child.remove()
            if not new_wids:
                grid.mount(Static(
                    f"[dim]No widgets assigned to Display {self.display_id}.\n"
                    f"Open control.py and click [{self.display_id}] next to a widget.[/dim]",
                    id="no_widgets"
                ))
            else:
                for wid in new_wids:
                    if wid not in WID_INFO:
                        continue
                    label, section = WID_INFO[wid]
                    grid.mount(CelWidget(wid, label, section, id=f"wgt_{wid}"))
            self._widgets = list(new_wids)
            if self._state:
                self.call_after_refresh(lambda: self._update_widgets(self._state))
        except Exception:
            pass

    def _update_widgets(self, state: dict):
        for wid in self._widgets:
            try:
                self.query_one(f"#wgt_{wid}", CelWidget).update_data(state)
            except Exception:
                pass

    def _update_bars(self, d: dict):
        now_dt = d.get("now_dt", {})
        h24    = f"{now_dt.get('h',0):02d}:{now_dt.get('m',0):02d}:{now_dt.get('s',0):02d}"
        ph_g   = MOON_PHASE_GLYPHS[d.get("moon_phase_idx", 0)]
        ph_n   = MOON_PHASE_NAMES[d.get("moon_phase_idx", 0)]
        sun_s  = SIGN_NAMES[d.get("sun_sign", 0)]
        moo_s  = SIGN_NAMES[d.get("moon_sign", 0)]
        rx_c   = len(d.get("retrograde_list", []))
        rx_s   = f"℞×{rx_c}" if rx_c else "direct"
        in_ec  = d.get("eclipse_active", False)
        rk_a   = d.get("rahu_kalam_active", False)
        rk_s   = d.get("rahu_kalam_start", "")
        ec     = "  ⚠ ECLIPSE" if in_ec else ""
        rk     = f"  ⚠ RAHU KALAM {rk_s}" if rk_a else ""
        cel    = (f"  {h24}  ·  ☉ {sun_s}  ·  {ph_g} {ph_n}  ·  "
                  f"☽ {moo_s}  ·  {rx_s}  ·  "
                  f"☊ {SIGN_NAMES[d.get('rahu_sign', 0)]}{ec}{rk}")
        try:
            self.query_one("#celestial_bar", Static).update(cel)
        except Exception:
            pass
        h     = to_roman(now_dt.get("h", 0)) if now_dt.get("h", 0) > 0 else "XII"
        m     = to_roman(now_dt.get("m", 0)) if now_dt.get("m", 0) > 0 else "O"
        hp    = d.get("ph_planet", "Sun")
        tname = TITHI_NAMES[min(d.get("tithi_idx", 0), 14)]
        status = (f"  Display {self.display_id}  │  {h}∶{m}  │  "
                  f"{d.get('illumination', 0):.0f}% lit  │  {tname}  │  "
                  f"{hp}'s hour")
        try:
            self.query_one("#status_bar", Static).update(status)
        except Exception:
            pass

    def widget_clicked(self, wid: str):
        if not self._selected:
            self._selected = wid
            try:
                self.query_one(f"#wgt_{wid}", CelWidget).set_selected(True)
            except Exception:
                pass
        elif self._selected == wid:
            self._selected = ""
            try:
                self.query_one(f"#wgt_{wid}", CelWidget).set_selected(False)
            except Exception:
                pass
        else:
            a, b = self._selected, wid
            try:
                grid = self.query_one("#widget_grid")
                wa   = self.query_one(f"#wgt_{a}", CelWidget)
                wb   = self.query_one(f"#wgt_{b}", CelWidget)
                grid.move_child(wa, before=wb)
                wa.set_selected(False)
                cfg  = read_display_config(self.display_id)
                wids = cfg.get("widgets", [])
                if a in wids and b in wids:
                    ia, ib = wids.index(a), wids.index(b)
                    wids[ia], wids[ib] = wids[ib], wids[ia]
                    cfg["widgets"] = wids
                    write_display_config(self.display_id, cfg)
                    self._widgets = list(wids)
            except Exception:
                try:
                    self.query_one(f"#wgt_{a}", CelWidget).set_selected(False)
                except Exception:
                    pass
            self._selected = ""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 display.py <display_id> [--bare]")
        print()
        print("  python3 display.py 1          normal mode — bars + title")
        print("  python3 display.py 1 --bare   bare mode — zero chrome, widget fills terminal")
        sys.exit(1)
    try:
        display_id = int(sys.argv[1])
    except ValueError:
        print(f"Display ID must be a number, got: {sys.argv[1]}")
        sys.exit(1)
    bare = "--bare" in sys.argv
    DisplayApp(display_id, bare=bare).run()
