#!/usr/bin/env python3
"""
   ______    ___   ____  _____  _________  _______      ___   _____                        
 .' ___  | .'   `.|_   \|_   _||  _   _  ||_   __ \   .'   `.|_   _|                       
/ .'   \_|/  .-.  \ |   \ | |  |_/ | | \_|  | |__) | /  .-.  \ | |        _ .--.   _   __  
| |       | |   | | | |\ \| |      | |      |  __ /  | |   | | | |   _   [ '/'`\ \[ \ [  ] 
\ `.___.'\\  `-'  /_| |_\   |_    _| |_    _| |  \ \_\  `-'  /_| |__/ | _ | \__/ | \ '/ /  
 `.____ .' `.___.'|_____|\____|  |_____|  |____| |___|`.___.'|________|(_)| ;.__/[\_:  /   
                                                                         [__|     \__.'  





VIGILARUM OMNIA — Control Panel
Run this first. It calculates the sky and writes state.
Assign widgets to display terminals from here.

Usage:  python3 control.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from textual.app import App, ComposeResult
from textual.widgets import Static, Label
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual import work
from datetime import datetime, timezone

from data import WIDGET_DEFS, SEASON_COLS, SEASON_GLYPHS, SEASON_NAMES
from engine import calculate_all, to_roman
from state import (write_state, read_display_config, write_display_config,
                   assign_widget, get_widget_display, list_displays,
                   set_display_columns, ensure_dirs)


MAX_DISPLAYS = 9

CSS = """
Screen {
    background: #0D0B0E;
    color: #c8b89a;
}

#header {
    background: #0D0B0E;
    color: #c8a84b;
    text-align: center;
    height: 4;
    border-bottom: solid #2a2030;
    padding: 0 1;
}

#body {
    layout: horizontal;
    height: 1fr;
}

#left_col {
    width: 1fr;
    padding: 1 2;
    overflow-y: auto;
}

#right_col {
    width: 30;
    background: #100e13;
    border-left: solid #2a2030;
    padding: 1 2;
    overflow-y: auto;
}

#status_bar {
    background: #08060a;
    color: #5a4a6a;
    height: 1;
    border-top: solid #1a1520;
    padding: 0 2;
    dock: bottom;
}

.section_hdr {
    color: #4a3a5a;
    text-style: bold;
    margin-top: 1;
    margin-bottom: 0;
}

.widget_row {
    layout: horizontal;
    height: 1;
    margin-bottom: 1;
}

.wid_label {
    width: 22;
    color: #9a8a7a;
}

.disp_btn {
    width: 3;
    color: #3a2a4a;
}

.disp_btn_active {
    width: 3;
    color: #c8a84b;
    text-style: bold;
}

.display_hdr {
    color: #c8a84b;
    text-style: bold;
    margin-top: 1;
}

.col_row {
    layout: horizontal;
    height: 1;
    margin-bottom: 1;
}

.col_opt {
    width: 4;
    color: #3a2a4a;
}

.col_opt_active {
    width: 4;
    color: #c8a84b;
    text-style: bold;
}
"""


class DispBtn(Static):
    """Single display assignment button for a widget."""
    def __init__(self, wid: str, disp_id: int, **kwargs):
        super().__init__(**kwargs)
        self.wid     = wid
        self.disp_id = disp_id

    def refresh_state(self):
        current = get_widget_display(self.wid)
        if current == self.disp_id:
            self.update(f"[yellow bold][{self.disp_id}][/yellow bold]")
            self.remove_class("disp_btn")
            self.add_class("disp_btn_active")
        else:
            self.update(f"[dim] {self.disp_id} [/dim]")
            self.remove_class("disp_btn_active")
            self.add_class("disp_btn")

    def on_mount(self):
        self.refresh_state()

    def on_click(self):
        current = get_widget_display(self.wid)
        if current == self.disp_id:
            assign_widget(0, self.wid)  # unassign
        else:
            assign_widget(self.disp_id, self.wid)
        # Refresh all buttons for this widget row
        self.app.refresh_widget_row(self.wid)


class ColBtn(Static):
    """Column count button for a display."""
    def __init__(self, disp_id: int, cols: int, **kwargs):
        super().__init__(**kwargs)
        self.disp_id = disp_id
        self.cols    = cols

    def refresh_state(self):
        cfg = read_display_config(self.disp_id)
        current = cfg.get("columns", 3)
        if current == self.cols:
            self.update(f"[yellow bold][{self.cols}][/yellow bold]")
        else:
            self.update(f"[dim] {self.cols} [/dim]")

    def on_mount(self):
        self.refresh_state()

    def on_click(self):
        set_display_columns(self.disp_id, self.cols)
        self.app.refresh_col_row(self.disp_id)


class ControlApp(App):
    CSS = CSS
    TITLE = "VIGILARUM — CONTROL"

    _last_state: dict = {}

    def compose(self) -> ComposeResult:
        yield Static(
            "◈  V I G I L A R U M   O M N I A  ◈\n"
            "[dim]Control Panel · Assign widgets to displays · Sidereal · Lahiri[/dim]\n"
            "[dim]Launch displays:  python3 display.py <N>[/dim]",
            id="header"
        )
        with Horizontal(id="body"):
            with ScrollableContainer(id="left_col"):
                yield Static("[yellow bold]── WIDGET ASSIGNMENTS ──[/yellow bold]\n"
                             "[dim]Click a number to assign widget to that display.[/dim]")
                current_section = None
                for wid, label, section in WIDGET_DEFS:
                    if section != current_section:
                        current_section = section
                        yield Static(f"· {section} ·", classes="section_hdr")
                    with Horizontal(classes="widget_row", id=f"row_{wid}"):
                        yield Static(label, classes="wid_label")
                        for d_id in range(1, MAX_DISPLAYS + 1):
                            yield DispBtn(wid, d_id, id=f"db_{wid}_{d_id}")

            with Vertical(id="right_col"):
                yield Static("[yellow bold]── DISPLAYS ──[/yellow bold]",
                             classes="display_hdr")
                for d_id in range(1, MAX_DISPLAYS + 1):
                    yield Static(f"Display {d_id}", classes="display_hdr",
                                 id=f"dh_{d_id}")
                    with Horizontal(classes="col_row", id=f"cr_{d_id}"):
                        yield Static("Cols:", classes="wid_label")
                        for cols in (2, 3, 4):
                            yield ColBtn(d_id, cols, id=f"cb_{d_id}_{cols}")

        yield Static("", id="status_bar")

    def on_mount(self):
        ensure_dirs()
        # Ensure all displays have a config
        for d_id in range(1, MAX_DISPLAYS + 1):
            read_display_config(d_id)
        self.run_engine()
        self.set_interval(60, self.run_engine)
        self.set_interval(1,  self.tick_clock)

    def refresh_widget_row(self, wid: str):
        for d_id in range(1, MAX_DISPLAYS + 1):
            try:
                self.query_one(f"#db_{wid}_{d_id}", DispBtn).refresh_state()
            except Exception:
                pass

    def refresh_col_row(self, disp_id: int):
        for cols in (2, 3, 4):
            try:
                self.query_one(f"#cb_{disp_id}_{cols}", ColBtn).refresh_state()
            except Exception:
                pass

    @work(thread=True)
    def run_engine(self):
        now  = datetime.now(timezone.utc)
        data = calculate_all(now)
        # Add now_dt for display
        data["now_str"] = now.isoformat()
        data["now_dt"]  = {
            "h": now.hour, "m": now.minute, "s": now.second,
            "day": now.day, "mo": now.month, "yr": now.year,
            "weekday": now.strftime("%A"),
            "month_name": now.strftime("%B"),
        }
        write_state(data)
        self._last_state = data
        self.call_from_thread(self._update_status, data)

    def tick_clock(self):
        now = datetime.now(timezone.utc)
        if self._last_state:
            self._last_state["now_str"] = now.isoformat()
            self._last_state["now_dt"] = {
                "h": now.hour, "m": now.minute, "s": now.second,
                "day": now.day, "mo": now.month, "yr": now.year,
                "weekday": now.strftime("%A"),
                "month_name": now.strftime("%B"),
            }
            write_state(self._last_state)
        self._update_status(self._last_state)

    def _update_status(self, d: dict):
        if not d:
            return
        now_dt = d.get("now_dt", {})
        h = to_roman(now_dt.get("h", 0)) if now_dt.get("h", 0) > 0 else "XII"
        m = to_roman(now_dt.get("m", 0)) if now_dt.get("m", 0) > 0 else "O"
        s_idx = d.get("season_idx", 0)
        illum = d.get("illumination", 0)
        rx_c  = len(d.get("retrograde_list", []))
        status = (f"  {h}∶{m}  │  "
                  f"{SEASON_GLYPHS[s_idx]} {SEASON_NAMES[s_idx]}  │  "
                  f"{illum:.0f}% lit  │  "
                  f"℞ {rx_c}  │  "
                  f"Writing → {str(STATE_FILE_PATH)}")
        try:
            self.query_one("#status_bar", Static).update(status)
        except Exception:
            pass


# expose path for status bar
from state import STATE_FILE as STATE_FILE_PATH

if __name__ == "__main__":
    app = ControlApp()
    app.run()
