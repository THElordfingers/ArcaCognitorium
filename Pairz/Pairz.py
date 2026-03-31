import customtkinter as ctk
import tkinter as tk
import random
import requests
import colour
import numpy as np
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

try:
    import pyfiglet
    PYFIGLET_OK = True
except ImportError:
    PYFIGLET_OK = False

ctk.set_appearance_mode("Dark")

# ── DIRECTORY & FILE CONSTANTS ─────────────────────────────────────────────────
BASE_DIR         = Path.home() / "Pairz"
COLOUR_PAIRS_DIR = BASE_DIR / "ColourPairs"
SLIDER_DIR       = BASE_DIR / "SliderSettings"
SAMPLE_TEXT_DIR  = str(Path.home() / "Pairz" / "SampleText")
FIGLET_FONT_DIR  = str(Path.home() / "Pairz" / "FigletFonts")
COLOUR_PAIRS_TXT = COLOUR_PAIRS_DIR / "ColourPairs.txt"
CURRENT_PRESET   = SLIDER_DIR / "current.json"

for d in [COLOUR_PAIRS_DIR, SLIDER_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── SLIDER VISUAL STATES ───────────────────────────────────────────────────────
SLIDER_ACTIVE   = {"button_color": "#8e44ad", "button_hover_color": "#6c3483",
                   "progress_color": "#6c3483", "fg_color": "#3a3a3a"}
SLIDER_DISABLED = {"button_color": "#2a2a2a", "button_hover_color": "#2a2a2a",
                   "progress_color": "#222222", "fg_color": "#1e1e1e"}

# ── ROMAN NUMERAL HELPER ───────────────────────────────────────────────────────
_ROMAN = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),
          (50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]

def to_roman(n):
    result = ""
    for val, sym in _ROMAN:
        while n >= val:
            result += sym
            n -= val
    return result

# ── ALGORITHM DESCRIPTIONS ─────────────────────────────────────────────────────
ALGO_INFO = {
    "WCAG 2.1": (
        "Web Content Accessibility Guidelines 2.1\n\n"
        "The most widely used accessibility standard. Measures luminance ratio\n"
        "between two colours. 1:1 = no contrast, 21:1 = black on white.\n\n"
        "Recommended thresholds:\n"
        "  \u2022 AA Normal text:   \u2265 4.5\n"
        "  \u2022 AA Large text:    \u2265 3.0\n"
        "  \u2022 AAA Normal text:  \u2265 7.0\n"
        "  \u2022 AAA Large text:   \u2265 4.5"
    ),
    "APCA": (
        "Advanced Perceptual Contrast Algorithm\n\n"
        "Next-generation contrast model. Accounts for polarity\n"
        "(light-on-dark vs dark-on-light) and spatial frequency.\n\n"
        "Recommended thresholds:\n"
        "  \u2022 Minimum readable:  \u2265 45\n"
        "  \u2022 Body text:         \u2265 60\n"
        "  \u2022 Fluent reading:    \u2265 75"
    ),
    "Michelson": (
        "Michelson Contrast\n\n"
        "Originally for periodic patterns. Calculates contrast as\n"
        "(max \u2212 min) / (max + min). Simple and symmetric.\n\n"
        "Recommended thresholds:\n"
        "  \u2022 Low contrast:      \u2265 0.5\n"
        "  \u2022 Medium contrast:   \u2265 0.7\n"
        "  \u2022 High contrast:     \u2265 0.9"
    ),
    "Weber": (
        "Weber Contrast\n\n"
        "From Weber's Law in psychophysics. Difference relative to\n"
        "background luminance. Best for targets on uniform backgrounds.\n\n"
        "Recommended thresholds:\n"
        "  \u2022 Noticeable:        \u2265 1.0\n"
        "  \u2022 Clear:             \u2265 5.0\n"
        "  \u2022 High legibility:   \u2265 15.0"
    ),
    "Delta Phi": (
        "Delta Phi Star (\u0394\u03a6*)\n\n"
        "Perceptual contrast on the phi (\u03a6) lightness scale.\n"
        "More uniform than WCAG across mid-tones.\n\n"
        "Recommended thresholds:\n"
        "  \u2022 Minimum:           \u2265 10\n"
        "  \u2022 Good readability:  \u2265 18\n"
        "  \u2022 Excellent:         \u2265 28"
    ),
    "L* Distance": (
        "CIE L* Lightness Distance\n\n"
        "Raw perceptual lightness difference in CIELAB space.\n"
        "Equal numeric steps = equal perceived differences.\n\n"
        "Recommended thresholds:\n"
        "  \u2022 Minimum visible:   \u2265 20\n"
        "  \u2022 Comfortable read:  \u2265 40\n"
        "  \u2022 High contrast:     \u2265 60"
    )
}


class ColorDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pairz v3.0")
        self.geometry("1600x950")

        self.algo_configs = {
            "WCAG 2.1":   {"min": 1.0,  "max": 21.0,  "default": 7.0},
            "APCA":       {"min": 0.0,  "max": 108.0, "default": 75.0},
            "Michelson":  {"min": 0.0,  "max": 1.0,   "default": 0.9},
            "Weber":      {"min": 0.0,  "max": 20.0,  "default": 15.0},
            "Delta Phi":  {"min": 0.0,  "max": 50.0,  "default": 18.0},
            "L* Distance":{"min": 0.0,  "max": 100.0, "default": 50.0}
        }

        self.bg_hex, self.fg_hex, self.accent_hex = "#120908", "#f37673", "#73f3e1"
        self.bg_name, self.fg_name, self.accent_name = "FOUNDATION", "FOREGROUND", "TERTIARY"
        self.current_metrics = {}
        self.current_oklch   = {}
        self.is_locked       = False

        self.fg_mode_var  = ctk.StringVar(value="manual")
        self.acc_mode_var = ctk.StringVar(value="manual")

        # ── Sample Text state — verbatim Ipsumator names ───────────────────────
        self.body_font_size     = 10
        self.title_font_size    = 10
        self.title_render_width = 250
        self.current_font_name  = "standard"
        self.justifications     = ["left", "center", "right"]
        self.just_index         = 1

        # Verbatim from Ipsumator
        try:
            self.pyfiglet_base     = os.path.dirname(pyfiglet.__file__)
            self.internal_font_dir = os.path.join(self.pyfiglet_base, "fonts")
        except Exception:
            self.internal_font_dir = ""

        self.setup_ui()
        self.load_settings()
        self.generate_new_pair()

    # ══════════════════════════════════════════════════════════════════════════
    # UI SETUP
    # ══════════════════════════════════════════════════════════════════════════
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar shell ─────────────────────────────────────────────────────
        self.sidebar_container = ctk.CTkFrame(self, width=340, corner_radius=0,
                                              fg_color="#0f0f0f")
        self.sidebar_container.grid(row=0, column=0, sticky="nsew")
        self.sidebar_container.grid_propagate(False)
        self.sidebar_container.grid_rowconfigure(0, weight=0)
        self.sidebar_container.grid_rowconfigure(1, weight=1)
        self.sidebar_container.grid_rowconfigure(2, weight=0)
        self.sidebar_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.sidebar_container, text="PAIRZ v3.0",
                     font=("Impact", 26), text_color="#cccccc").grid(
            row=0, column=0, pady=(14, 4))

        # ── Slider subtabs ────────────────────────────────────────────────────
        self.slider_tabs = ctk.CTkTabview(
            self.sidebar_container, corner_radius=8, fg_color="#141414",
            segmented_button_fg_color="#0f0f0f",
            segmented_button_selected_color="#8e44ad",
            segmented_button_unselected_color="#0f0f0f",
            segmented_button_selected_hover_color="#6c3483")
        self.slider_tabs.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 4))

        self._build_algo_tab(self.slider_tabs.add("Algo"))
        self._build_bg_tab(self.slider_tabs.add("BG"))
        self._build_fg_tab(self.slider_tabs.add("FG"))
        self._build_tertiary_tab(self.slider_tabs.add("Tertiary"))

        self._build_control_bay()

        # ── Main tabview ──────────────────────────────────────────────────────
        self.tab_view = ctk.CTkTabview(self, corner_radius=15, fg_color="#020202",
                                       segmented_button_selected_color="#8e44ad")
        self.tab_view.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

        self.tab_core   = self.tab_view.add("Core Engine")
        self.tab_sample = self.tab_view.add("Sample Text")
        self.tab_stats  = self.tab_view.add("Advanced Stats")

        # ── Core Engine canvas ────────────────────────────────────────────────
        self.canvas = tk.Canvas(self.tab_core, bg="#020202", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw_graphic())

        # ── Sample Text tab — exact Ipsumator widget structure ─────────────────
        # parent swapped from self → self.tab_sample; colours wired to live values
        self.content_frame = ctk.CTkScrollableFrame(
            self.tab_sample, fg_color="transparent", corner_radius=0,
            scrollbar_fg_color="#020202",
            scrollbar_button_color="#020202",
            scrollbar_button_hover_color="#020202")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 0))
        self.content_frame._scrollbar.configure(width=0)

        self.title_display = ctk.CTkLabel(
            self.content_frame, text="",
            font=("Courier New", self.title_font_size), justify="center")
        self.title_display.pack(pady=(40, 30), fill="x", expand=True)

        self.body_display = ctk.CTkTextbox(
            self.content_frame, fg_color="transparent", border_width=0,
            activate_scrollbars=False, wrap="word")
        self.body_display.pack(pady=10, anchor="center")

        # ── Live text controls panel ──────────────────────────────────────────
        self._controls_visible = False
        self._controls_panel = ctk.CTkFrame(
            self.tab_sample, fg_color="#111111", corner_radius=0)
        # Not packed yet — toggled on demand

        ctrl_inner = ctk.CTkFrame(self._controls_panel, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=12, pady=8)
        ctrl_inner.grid_columnconfigure(1, weight=1)
        ctrl_inner.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(ctrl_inner, text="TITLE", font=("Courier New", 9, "bold"),
                     text_color="#666").grid(row=0, column=0, padx=(0, 6), sticky="w")
        self.live_title_entry = ctk.CTkEntry(
            ctrl_inner, font=("Courier New", 11), height=28,
            placeholder_text="override title...")
        self.live_title_entry.grid(row=0, column=1, sticky="ew", padx=(0, 16))
        self.live_title_entry.bind("<KeyRelease>", lambda e: self._on_live_title())

        ctk.CTkLabel(ctrl_inner, text="BODY", font=("Courier New", 9, "bold"),
                     text_color="#666").grid(row=0, column=2, padx=(0, 6), sticky="w")
        self.live_body_entry = ctk.CTkEntry(
            ctrl_inner, font=("Courier New", 11), height=28,
            placeholder_text="override body text...")
        self.live_body_entry.grid(row=0, column=3, sticky="ew", padx=(0, 16))
        self.live_body_entry.bind("<KeyRelease>", lambda e: self._on_live_body())

        ctk.CTkLabel(ctrl_inner, text="FONT", font=("Courier New", 9, "bold"),
                     text_color="#666").grid(row=0, column=4, padx=(0, 6), sticky="w")
        self.live_font_var = ctk.StringVar(value="standard")
        self.live_font_menu = ctk.CTkOptionMenu(
            ctrl_inner, variable=self.live_font_var,
            values=self._get_figlet_font_list(),
            command=self._on_live_font,
            font=("Courier New", 10), width=140, height=28)
        self.live_font_menu.grid(row=0, column=5)

        # Hint bar with toggle button
        hint = ctk.CTkFrame(self.tab_sample, fg_color="#0a0a0a",
                            height=36, corner_radius=0)
        hint.pack(fill="x", side="bottom")
        hint.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hint,
                     text="Shift+Space: new text  |  \u2190\u2192: justify  |  \u2191\u2193: body size  |  Ctrl+scroll: body  |  Shift+scroll: title",
                     font=("Courier New", 9), text_color="#444").grid(
            row=0, column=0, pady=8)
        ctk.CTkButton(hint, text="✎ EDIT", width=60, height=22,
                      fg_color="#1a1a1a", hover_color="#2a2a2a",
                      font=("Courier New", 9), border_width=1,
                      border_color="#333",
                      command=self._toggle_controls).grid(
            row=0, column=1, padx=8, pady=6)

        # ── Stats tab ─────────────────────────────────────────────────────────
        self.stats_scroll = ctk.CTkScrollableFrame(self.tab_stats,
                                                   fg_color="transparent")
        self.stats_scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Keybindings ───────────────────────────────────────────────────────
        self.bind_all("<space>",              lambda e: self._on_space(e))
        self.bind_all("<Return>",             lambda e: self.save_pair())
        # Tab cycles main tabs — bind_all + return "break" prevents CTk focus cycling
        self.bind_all("<Tab>",                lambda e: (self._cycle_main_tab(1), "break")[1])
        # ISO_Left_Tab is what X11 actually sends for Shift+Tab on Linux
        self.bind_all("<ISO_Left_Tab>",       lambda e: (self._cycle_sidebar_tab(1), "break")[1])
        self.bind_all("<Shift-space>",        lambda e: self._on_shift_space(e))
        # Left/Right on root only — avoids X11 fabricated key events from scroll
        self.bind("<Left>",                   lambda e: self.change_justification(-1))
        self.bind("<Right>",                  lambda e: self.change_justification(1))
        self.bind_all("<Up>",                 lambda e: self._on_up_down(1))
        self.bind_all("<Down>",               lambda e: self._on_up_down(-1))
        self.bind("<Control-MouseWheel>",     self.scale_body_mouse)
        self.bind("<Control-Button-4>",       self.scale_body_mouse)
        self.bind("<Control-Button-5>",       self.scale_body_mouse)
        self.bind("<Shift-MouseWheel>",       self.scale_title_mouse)
        self.bind("<Shift-Button-4>",         self.scale_title_mouse)
        self.bind("<Shift-Button-5>",         self.scale_title_mouse)

    # ── TAB BUILDERS ──────────────────────────────────────────────────────────
    def _build_algo_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                        scrollbar_button_color="#333",
                                        scrollbar_button_hover_color="#555")
        scroll.pack(fill="both", expand=True)
        ctk.CTkLabel(scroll, text="ALGORITHM", font=("Impact", 13),
                     text_color="#888").pack(pady=(10, 2))
        self.algo_var = ctk.StringVar(value="WCAG 2.1")
        self.algo_menu = ctk.CTkOptionMenu(
            scroll, values=list(self.algo_configs.keys()),
            command=self.update_slider_range, variable=self.algo_var, width=200)
        self.algo_menu.pack(pady=4, padx=14)
        self.thresh_label = ctk.CTkLabel(scroll, text="Threshold: 7.0",
                                         font=("Courier New", 11, "bold"))
        self.thresh_label.pack()
        self.thresh_slider = self._make_slider(scroll, None, 1, 21, 7.0, is_meta=True)
        self.algo_info_box = ctk.CTkTextbox(
            scroll, font=("Courier New", 10), fg_color="#0a0a0a",
            text_color="#aaaaaa", border_width=1, border_color="#2a2a2a",
            activate_scrollbars=False, wrap="word", height=180)
        self.algo_info_box.pack(fill="x", padx=10, pady=(12, 6))
        self._update_algo_info("WCAG 2.1")

    def _build_bg_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                        scrollbar_button_color="#333",
                                        scrollbar_button_hover_color="#555")
        scroll.pack(fill="both", expand=True)
        ctk.CTkLabel(scroll, text="FOUNDATION", font=("Impact", 13),
                     text_color="#888").pack(pady=(10, 6))
        self.bg_h_min = self._make_slider(scroll, "HUE MIN",   0,   360, 0)
        self.bg_h_max = self._make_slider(scroll, "HUE MAX",   0,   360, 360)
        self.bg_l_min = self._make_slider(scroll, "LIGHT MIN", 0.0, 1.0, 0.05)
        self.bg_l_max = self._make_slider(scroll, "LIGHT MAX", 0.0, 1.0, 0.25)

    def _build_fg_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                        scrollbar_button_color="#333",
                                        scrollbar_button_hover_color="#555")
        scroll.pack(fill="both", expand=True)
        ctk.CTkLabel(scroll, text="FOREGROUND", font=("Impact", 13),
                     text_color="#888").pack(pady=(10, 4))
        mode_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkRadioButton(mode_frame, text="Manual", variable=self.fg_mode_var,
                           value="manual", command=self._on_fg_mode_change,
                           font=("Courier New", 10)).pack(side="left", padx=6)
        ctk.CTkRadioButton(mode_frame, text="Complementary of BG",
                           variable=self.fg_mode_var, value="complementary",
                           command=self._on_fg_mode_change,
                           font=("Courier New", 10)).pack(side="left", padx=6)
        self.fg_slider_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.fg_slider_frame.pack(fill="x")
        self.fg_h_min   = self._make_slider(self.fg_slider_frame, "HUE MIN",    0,    360, 0)
        self.fg_h_max   = self._make_slider(self.fg_slider_frame, "HUE MAX",    0,    360, 360)
        self.fg_l_min   = self._make_slider(self.fg_slider_frame, "LIGHT MIN",  0.0,  1.0, 0.70)
        self.fg_l_max   = self._make_slider(self.fg_slider_frame, "LIGHT MAX",  0.0,  1.0, 0.95)
        self.chroma_max = self._make_slider(self.fg_slider_frame, "CHROMA PEAK",0.01, 0.4, 0.15)

    def _build_tertiary_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                        scrollbar_button_color="#333",
                                        scrollbar_button_hover_color="#555")
        scroll.pack(fill="both", expand=True)
        ctk.CTkLabel(scroll, text="TERTIARY", font=("Impact", 13),
                     text_color="#888").pack(pady=(10, 4))
        self.accent_opt_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(scroll, text="ENABLE TERTIARY",
                        variable=self.accent_opt_var, command=self.on_param_change,
                        font=("Impact", 12)).pack(pady=(0, 8))
        mode_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        mode_frame.pack(fill="x", padx=6, pady=(0, 8))
        for txt, val in [("Manual","manual"),
                         ("Complementary of BG","complementary"),
                         ("Average BG+FG","average")]:
            ctk.CTkRadioButton(mode_frame, text=txt, variable=self.acc_mode_var,
                               value=val, command=self._on_acc_mode_change,
                               font=("Courier New", 10)).pack(anchor="w", padx=8, pady=1)
        self.acc_slider_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.acc_slider_frame.pack(fill="x")
        self.acc_offset = self._make_slider(self.acc_slider_frame, "HUE OFFSET", 0,    360, 120)
        self.acc_chroma = self._make_slider(self.acc_slider_frame, "CHROMA",     0.01, 0.4, 0.20)
        self.acc_light  = self._make_slider(self.acc_slider_frame, "LIGHTNESS",  0.0,  1.0, 0.80)

    def _build_control_bay(self):
        bay = ctk.CTkFrame(self.sidebar_container, corner_radius=0, fg_color="#1a1a1a")
        bay.grid(row=2, column=0, sticky="ew")
        bay.grid_columnconfigure(0, weight=1)

        btn_frame = ctk.CTkFrame(bay, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(12, 6))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.generate_btn = ctk.CTkButton(
            btn_frame, text="GENERATE", fg_color="#34495e",
            font=("Impact", 16), command=self.generate_new_pair)
        self.generate_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.accept_btn = ctk.CTkButton(
            btn_frame, text="ACCEPT", fg_color="#2ecc71",
            font=("Impact", 16), command=self.save_pair)
        self.accept_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        ctk.CTkFrame(bay, height=1, fg_color="#2a2a2a").pack(fill="x", padx=10, pady=4)

        preset_load_frame = ctk.CTkFrame(bay, fg_color="transparent")
        preset_load_frame.pack(fill="x", padx=16, pady=(4, 2))
        preset_load_frame.grid_columnconfigure(0, weight=1)
        self.preset_var = ctk.StringVar(value="-- load preset --")
        self.preset_dropdown = ctk.CTkOptionMenu(
            preset_load_frame, variable=self.preset_var,
            values=self._get_preset_list(),
            command=self._load_preset_from_dropdown,
            font=("Courier New", 10), width=200, height=28)
        self.preset_dropdown.grid(row=0, column=0, sticky="ew")

        preset_save_frame = ctk.CTkFrame(bay, fg_color="transparent")
        preset_save_frame.pack(fill="x", padx=16, pady=(2, 12))
        preset_save_frame.grid_columnconfigure(0, weight=1)
        self.preset_name_entry = ctk.CTkEntry(
            preset_save_frame, placeholder_text="preset name...",
            font=("Courier New", 10), height=28)
        self.preset_name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(preset_save_frame, text="SAVE", width=60, height=28,
                      fg_color="#8e44ad", font=("Impact", 12),
                      command=self._save_named_preset).grid(row=0, column=1)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDER FACTORY & VISUAL STATE
    # ══════════════════════════════════════════════════════════════════════════
    def _make_slider(self, parent, label, start, end, default, is_meta=False):
        if label:
            ctk.CTkLabel(parent, text=label, font=("Courier New", 10, "bold"),
                         text_color="gray").pack(pady=(4, 0))
        s = ctk.CTkSlider(parent, from_=start, to=end,
                          command=lambda v: self.on_slider_move(v, is_meta),
                          **SLIDER_ACTIVE)
        s.set(default)
        s.pack(pady=2, padx=16)
        return s

    def _set_slider_group_state(self, frame, enabled: bool):
        style = SLIDER_ACTIVE if enabled else SLIDER_DISABLED
        for w in frame.winfo_children():
            if isinstance(w, ctk.CTkSlider):
                w.configure(state="normal" if enabled else "disabled", **style)
            elif isinstance(w, ctk.CTkLabel):
                w.configure(text_color="gray" if enabled else "#333333")

    def on_slider_move(self, val, is_meta):
        if is_meta:
            self.thresh_label.configure(text=f"Threshold: {round(val, 2)}")
        self.save_settings()
        if self.is_locked:
            self.generate_new_pair()

    def on_param_change(self):
        self.save_settings()
        self.generate_new_pair()

    # ── Lockout ───────────────────────────────────────────────────────────────
    def _set_locked(self, locked: bool):
        self.is_locked = locked
        if locked:
            self.generate_btn.configure(text="NO MATCH", fg_color="#7b241c",
                                        hover_color="#922b21")
            self.accept_btn.configure(state="disabled", fg_color="#1a472a")
        else:
            self.generate_btn.configure(text="GENERATE", fg_color="#34495e",
                                        hover_color="#2c3e50")
            self.accept_btn.configure(state="normal", fg_color="#2ecc71")

    # ── Mode change handlers ──────────────────────────────────────────────────
    def _on_fg_mode_change(self):
        self._set_slider_group_state(self.fg_slider_frame,
                                     self.fg_mode_var.get() == "manual")
        self.on_param_change()

    def _on_acc_mode_change(self):
        self._set_slider_group_state(self.acc_slider_frame,
                                     self.acc_mode_var.get() == "manual")
        self.on_param_change()

    def _update_algo_info(self, algo_name):
        info = ALGO_INFO.get(algo_name, "")
        self.algo_info_box.configure(state="normal")
        self.algo_info_box.delete("1.0", "end")
        self.algo_info_box.insert("1.0", info)
        self.algo_info_box.configure(state="disabled")

    # ── Tab cycling & keybinding handlers ────────────────────────────────────
    def _on_space(self, event):
        if str(self.focus_get()) == str(self.preset_name_entry):
            return
        self.generate_new_pair()
        return "break"

    def _on_shift_space(self, event):
        if str(self.focus_get()) == str(self.preset_name_entry):
            return
        if self.tab_view.get() == "Sample Text":
            self.load_sample()
        return "break"

    def _on_up_down(self, delta):
        if self.tab_view.get() == "Sample Text":
            self.adjust_body_font(delta)
        return "break"

    def _cycle_main_tab(self, direction):
        names   = list(self.tab_view._tab_dict.keys())
        current = self.tab_view.get()
        idx     = (names.index(current) + direction) % len(names)
        self.tab_view.set(names[idx])
        return "break"

    def _cycle_sidebar_tab(self, direction):
        names   = list(self.slider_tabs._tab_dict.keys())
        current = self.slider_tabs.get()
        idx     = (names.index(current) + direction) % len(names)
        self.slider_tabs.set(names[idx])
        return "break"

    # ══════════════════════════════════════════════════════════════════════════
    # COLOUR GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    def generate_new_pair(self):
        attempts = 0
        while attempts < 4000:
            attempts += 1
            bg_l = random.uniform(self.bg_l_min.get(), self.bg_l_max.get())
            bg_h = random.uniform(self.bg_h_min.get(), self.bg_h_max.get())
            bg_c = 0.02

            b_hex = colour.notation.RGB_to_HEX(
                np.clip(colour.convert([bg_l, bg_c, bg_h], 'Oklch', 'sRGB'), 0, 1))

            fg_mode = self.fg_mode_var.get()
            if fg_mode == "complementary":
                fg_h = (bg_h + 180) % 360
                fg_l = 1.0 - bg_l
                fg_c = self.chroma_max.get()
            else:
                fg_l = random.uniform(self.fg_l_min.get(), self.fg_l_max.get())
                fg_h = random.uniform(self.fg_h_min.get(), self.fg_h_max.get())
                fg_c = self.chroma_max.get()

            f_hex = colour.notation.RGB_to_HEX(
                np.clip(colour.convert([fg_l, fg_c, fg_h], 'Oklch', 'sRGB'), 0, 1))

            rgb_bg = np.array([int(b_hex.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4)])
            rgb_fg = np.array([int(f_hex.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4)])
            srgb   = colour.models.RGB_COLOURSPACE_sRGB
            Y_bg   = colour.models.RGB_luminance(rgb_bg, srgb.primaries, srgb.whitepoint)
            Y_fg   = colour.models.RGB_luminance(rgb_fg, srgb.primaries, srgb.whitepoint)

            self.current_metrics = {
                "WCAG 2.1":   round((max(Y_bg,Y_fg)+0.05)/(min(Y_bg,Y_fg)+0.05), 2),
                "APCA":       round((Y_fg**0.6 - Y_bg**0.6)*100, 1),
                "Michelson":  round(abs(Y_fg-Y_bg)/(Y_fg+Y_bg+0.0001), 3),
                "Weber":      round(abs(Y_fg-Y_bg)/(min(Y_bg,Y_fg)+0.0001), 2),
                "L* Distance":round(abs(
                    colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb_fg))[0] -
                    colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb_bg))[0]), 2)
            }

            if self.current_metrics.get(self.algo_var.get(), 0) >= self.thresh_slider.get():
                self.bg_hex, self.fg_hex = b_hex, f_hex

                acc_mode = self.acc_mode_var.get()
                if acc_mode == "complementary":
                    acc_h = (bg_h + 180) % 360
                    acc_l = self.acc_light.get()
                    acc_c = self.acc_chroma.get()
                elif acc_mode == "average":
                    acc_h = ((bg_h + fg_h) / 2) % 360
                    acc_l = (bg_l + fg_l) / 2
                    acc_c = (bg_c + fg_c) / 2
                else:
                    acc_h = (fg_h + self.acc_offset.get()) % 360
                    acc_l = self.acc_light.get()
                    acc_c = self.acc_chroma.get()

                self.accent_hex = colour.notation.RGB_to_HEX(
                    np.clip(colour.convert([acc_l, acc_c, acc_h], 'Oklch', 'sRGB'), 0, 1))

                self.current_oklch = {
                    "bg":  {"L": round(bg_l,4), "C": round(bg_c,4), "h": round(bg_h,2)},
                    "fg":  {"L": round(fg_l,4), "C": round(fg_c,4), "h": round(fg_h,2)},
                    "acc": {"L": round(acc_l,4),"C": round(acc_c,4),"h": round(acc_h,2)}
                }

                self._set_locked(False)
                self.update_names_async()
                self.refresh_all_tabs()
                return

        self._set_locked(True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB RENDERING
    # ══════════════════════════════════════════════════════════════════════════
    def refresh_all_tabs(self):
        self.draw_graphic()
        self.update_sample_tab()
        self.update_stats_tab()

    def draw_graphic(self):
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        # Fall back to sensible defaults before first layout pass
        if w < 10: w = 900
        if h < 10: h = 700

        self.canvas.delete("all")

        # Size blobs relative to canvas dimensions
        bg_size = min(w, h) * 0.28

        # BG blob: upper-left quadrant
        bx, by = w * 0.35, h * 0.38
        # FG blob: lower-right quadrant
        fx, fy = w * 0.62, h * 0.62
        # Accent blob: centre overlap
        ax, ay = w * 0.50, h * 0.50

        self.create_blob(self.canvas, bx, by, bg_size,        self.bg_hex,     True)
        self.create_blob(self.canvas, fx, fy, bg_size * 0.85, self.fg_hex,     False)
        if self.accent_opt_var.get():
            self.create_blob(self.canvas, ax, ay, bg_size * 0.55, self.accent_hex, False)

        # Label font scales with canvas size too
        font_size = max(18, int(min(w, h) * 0.042))
        self.draw_legible_text(20,        20,      self.bg_name.upper(), self.bg_hex, "nw", font_size)
        self.draw_legible_text(w - 20,    h - 20,  self.fg_name.upper(), self.fg_hex, "se", font_size)

    def update_sample_tab(self):
        """Called on every new colour pair — update background + live colours."""
        bg = self.bg_hex
        self.tab_sample.configure(fg_color=bg)
        self.content_frame.configure(
            fg_color=bg,
            scrollbar_fg_color=bg,
            scrollbar_button_color=bg,
            scrollbar_button_hover_color=bg)
        # Recolour existing content if loaded, otherwise load first sample
        if hasattr(self, 'current_data'):
            title_color = self.accent_hex if self.accent_opt_var.get() else self.fg_hex
            self.title_display.configure(text_color=title_color)
            self.body_display.configure(text_color=self.fg_hex)
        else:
            self.load_sample()

    def update_stats_tab(self):
        for child in self.stats_scroll.winfo_children():
            child.destroy()
        f = self.stats_scroll

        ctk.CTkLabel(f, text="CONTRAST METRICS", font=("Impact", 24),
                     text_color="#8e44ad").pack(anchor="w", pady=10)
        for k, v in self.current_metrics.items():
            ctk.CTkLabel(f, text=f"{k}: {v}",
                         font=("Courier New", 16, "bold")).pack(anchor="w")

        ctk.CTkLabel(f, text="\nCIE LAB ANALYSIS", font=("Impact", 24),
                     text_color="#f39c12").pack(anchor="w", pady=10)
        for name, hx in [("BG", self.bg_hex), ("FG", self.fg_hex)]:
            rgb = np.array([int(hx.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4)])
            lab = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb))
            ctk.CTkLabel(f, text=f"{name}: L* {round(lab[0],1)} | "
                                 f"a* {round(lab[1],1)} | b* {round(lab[2],1)}",
                         font=("Courier New", 14)).pack(anchor="w")

        ctk.CTkLabel(f, text="\nHEX TELEMETRY", font=("Impact", 24),
                     text_color="#2ecc71").pack(anchor="w", pady=10)
        ctk.CTkLabel(f, text=f"Foundation: {self.bg_hex}", font=("Courier New", 16)).pack(anchor="w")
        ctk.CTkLabel(f, text=f"Foreground: {self.fg_hex}", font=("Courier New", 16)).pack(anchor="w")
        ctk.CTkLabel(f, text=f"Tertiary:   {self.accent_hex}", font=("Courier New", 16)).pack(anchor="w")

    # ══════════════════════════════════════════════════════════════════════════
    # SAMPLE TEXT — VERBATIM IPSUMATOR METHODS
    # Only change: self.current_fg → self.fg_hex
    #              self.current_accent → self.accent_hex (guarded by accent_opt_var)
    # ══════════════════════════════════════════════════════════════════════════
    def load_sample(self):
        try:
            if not os.path.isdir(SAMPLE_TEXT_DIR):
                self._sample_show_error(f"Sample dir not found:\n{SAMPLE_TEXT_DIR}")
                return
            sample_files = [f for f in os.listdir(SAMPLE_TEXT_DIR)
                            if f.endswith('.json')]
            if not sample_files:
                self._sample_show_error(f"No .json files in:\n{SAMPLE_TEXT_DIR}")
                return
            with open(os.path.join(SAMPLE_TEXT_DIR,
                                   random.choice(sample_files)), "r") as f:
                self.current_data = json.load(f)

            if PYFIGLET_OK and os.path.isdir(FIGLET_FONT_DIR):
                font_files = [f for f in os.listdir(FIGLET_FONT_DIR)
                              if f.endswith(('.flf', '.tlf'))]
                if font_files:
                    selected_file = random.choice(font_files)
                    self.current_font_name = os.path.splitext(selected_file)[0]
                    dest_path = os.path.join(self.internal_font_dir, selected_file)
                    if not os.path.exists(dest_path):
                        shutil.copy2(os.path.join(FIGLET_FONT_DIR, selected_file),
                                     dest_path)

            self.body_display.configure(state="normal")
            self.body_display.delete("1.0", "end")
            self.body_display.insert("1.0", self.current_data.get("TEXT", ""))
            self.body_display.configure(
                width=self.current_data.get("WIDTH", 700),
                text_color=self.fg_hex)
            self.body_display.pack_configure(
                padx=self.current_data.get("PADDING", 30))
            self.update_ui_elements()
        except Exception as e:
            self._sample_show_error(str(e))
            print(f"load_sample error: {e}")

    def _sample_show_error(self, msg):
        self.title_display.configure(text="⚠  SAMPLE TEXT", text_color="#e74c3c",
                                     font=("Courier New", 14))
        self.body_display.configure(state="normal")
        self.body_display.delete("1.0", "end")
        self.body_display.insert("1.0", msg)
        self.body_display.configure(text_color="#e74c3c", state="disabled")

    def update_ui_elements(self, update_title=True, update_body=True):
        if not hasattr(self, 'current_data'):
            return
        mode = self.justifications[self.just_index]

        if update_title:
            raw_title   = self.current_data.get("TITLE", "UNTITLED")
            title_color = self.accent_hex if self.accent_opt_var.get() else self.fg_hex
            rendered = False
            if PYFIGLET_OK:
                try:
                    fig_text = pyfiglet.figlet_format(
                        raw_title, font=self.current_font_name,
                        width=self.title_render_width)
                    self.title_display.configure(
                        text=fig_text, text_color=title_color,
                        font=("Courier New", self.title_font_size))
                    rendered = True
                except Exception:
                    pass
            if not rendered:
                self.title_display.configure(
                    text=raw_title.upper(), text_color=title_color,
                    font=("Courier New", self.title_font_size * 3))

        if update_body:
            json_width   = self.current_data.get("WIDTH", 700)
            json_font    = self.current_data.get("FONT_FAMILY", "Helvetica")
            text_content = self.current_data.get("TEXT", "")
            lines        = text_content.count('\n') + \
                           (len(text_content) // (json_width // 6)) + 4
            dynamic_height = max(100, lines * (self.body_font_size + 8))

            self.body_display.configure(state="normal")
            self.body_display.configure(
                font=(json_font, self.body_font_size),
                height=dynamic_height)
            self.body_display.tag_add("align", "1.0", "end")
            self.body_display.tag_config("align", justify=mode)
            self.body_display.configure(state="disabled")

    def change_justification(self, direction):
        if self.tab_view.get() != "Sample Text":
            return
        self.just_index = (self.just_index + direction) % len(self.justifications)
        self.update_ui_elements(update_title=False)

    def adjust_body_font(self, amount):
        self.body_font_size = max(6, self.body_font_size + amount)
        self.update_ui_elements(update_title=False)

    def scale_body_mouse(self, event):
        if self.tab_view.get() != "Sample Text":
            return
        delta = 1 if (event.num == 4 or event.delta > 0) else -1
        self.adjust_body_font(delta)

    def scale_title_mouse(self, event):
        if self.tab_view.get() != "Sample Text":
            return
        delta = 1 if (event.num == 4 or event.delta > 0) else -1
        self.title_font_size = max(4, self.title_font_size + delta)
        self.title_render_width = max(50, self.title_render_width + (delta * 5))
        self.update_ui_elements(update_body=False)

    # ══════════════════════════════════════════════════════════════════════════
    # SAVE PAIR
    # ══════════════════════════════════════════════════════════════════════════
    def save_pair(self):
        if self.is_locked:
            return
        has_tertiary = self.accent_opt_var.get()
        bg_clean  = self.bg_name.replace(" ", "")
        fg_clean  = self.fg_name.replace(" ", "")
        base_stem = f"{bg_clean}-{fg_clean}"

        header_line  = f"[{bg_clean}&{fg_clean}]"
        detail_parts = [f"Background: {self.bg_hex}", f"Foreground: {self.fg_hex}"]
        if has_tertiary:
            detail_parts.append(f"Tertiary: {self.accent_hex}")
        with open(COLOUR_PAIRS_TXT, "a") as txt:
            txt.write(f"{header_line}\n{', '.join(detail_parts)}\n\n")

        def hex_to_lab(hx):
            rgb = np.array([int(hx.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4)])
            lab = colour.XYZ_to_Lab(colour.sRGB_to_XYZ(rgb))
            return {"L*": round(lab[0],3), "a*": round(lab[1],3), "b*": round(lab[2],3)}

        def hex_to_rgb(hx):
            return {"R": int(hx[1:3],16), "G": int(hx[3:5],16), "B": int(hx[5:7],16)}

        payload = {
            "saved_at":       datetime.now().isoformat(timespec="seconds"),
            "algorithm_used": self.algo_var.get(),
            "threshold":      round(self.thresh_slider.get(), 3),
            "fg_mode":        self.fg_mode_var.get(),
            "tertiary_mode":  self.acc_mode_var.get(),
            "background": {"name": self.bg_name, "hex": self.bg_hex,
                           "rgb": hex_to_rgb(self.bg_hex), "lab": hex_to_lab(self.bg_hex),
                           "oklch": self.current_oklch.get("bg", {})},
            "foreground": {"name": self.fg_name, "hex": self.fg_hex,
                           "rgb": hex_to_rgb(self.fg_hex), "lab": hex_to_lab(self.fg_hex),
                           "oklch": self.current_oklch.get("fg", {})},
            "tertiary": None,
            "contrast_metrics": self.current_metrics
        }
        if has_tertiary:
            payload["tertiary"] = {
                "name": self.accent_name, "hex": self.accent_hex,
                "rgb": hex_to_rgb(self.accent_hex), "lab": hex_to_lab(self.accent_hex),
                "oklch": self.current_oklch.get("acc", {})}

        json_path = self._resolve_json_path(base_stem, payload)
        with open(json_path, "w") as jf:
            json.dump(payload, jf, indent=2)

        self.generate_new_pair()

    def _resolve_json_path(self, base_stem, new_payload):
        candidate = COLOUR_PAIRS_DIR / f"{base_stem}.json"
        if not candidate.exists():
            return candidate
        try:
            with open(candidate) as f:
                existing = json.load(f)
            if (existing.get("background",{}).get("hex") == new_payload["background"]["hex"] and
                existing.get("foreground",{}).get("hex") == new_payload["foreground"]["hex"] and
                (existing.get("tertiary") or {}).get("hex") == (new_payload.get("tertiary") or {}).get("hex")):
                return candidate
        except Exception:
            pass
        n = 2
        while True:
            suffixed = COLOUR_PAIRS_DIR / f"{base_stem}_{to_roman(n)}.json"
            if not suffixed.exists():
                return suffixed
            try:
                with open(suffixed) as f:
                    existing = json.load(f)
                if (existing.get("background",{}).get("hex") == new_payload["background"]["hex"] and
                    existing.get("foreground",{}).get("hex") == new_payload["foreground"]["hex"] and
                    (existing.get("tertiary") or {}).get("hex") == (new_payload.get("tertiary") or {}).get("hex")):
                    return suffixed
            except Exception:
                pass
            n += 1

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDER SETTINGS & PRESETS
    # ══════════════════════════════════════════════════════════════════════════
    def _slider_state(self):
        return {
            "algo":           self.algo_var.get(),
            "thresh":         self.thresh_slider.get(),
            "bg_h_min":       self.bg_h_min.get(),
            "bg_h_max":       self.bg_h_max.get(),
            "bg_l_min":       self.bg_l_min.get(),
            "bg_l_max":       self.bg_l_max.get(),
            "fg_h_min":       self.fg_h_min.get(),
            "fg_h_max":       self.fg_h_max.get(),
            "fg_l_min":       self.fg_l_min.get(),
            "fg_l_max":       self.fg_l_max.get(),
            "chroma_max":     self.chroma_max.get(),
            "acc_off":        self.acc_offset.get(),
            "acc_chr":        self.acc_chroma.get(),
            "acc_l":          self.acc_light.get(),
            "accent_enabled": self.accent_opt_var.get(),
            "fg_mode":        self.fg_mode_var.get(),
            "acc_mode":       self.acc_mode_var.get()
        }

    def _apply_slider_state(self, d):
        self.algo_var.set(d.get("algo", "WCAG 2.1"))
        self.thresh_slider.set(d.get("thresh", 7.0))
        self.thresh_label.configure(text=f"Threshold: {round(d.get('thresh', 7.0), 2)}")
        self.bg_h_min.set(d.get("bg_h_min", 0))
        self.bg_h_max.set(d.get("bg_h_max", 360))
        self.bg_l_min.set(d.get("bg_l_min", 0.05))
        self.bg_l_max.set(d.get("bg_l_max", 0.25))
        self.fg_h_min.set(d.get("fg_h_min", 0))
        self.fg_h_max.set(d.get("fg_h_max", 360))
        self.fg_l_min.set(d.get("fg_l_min", 0.70))
        self.fg_l_max.set(d.get("fg_l_max", 0.95))
        self.chroma_max.set(d.get("chroma_max", 0.15))
        self.acc_offset.set(d.get("acc_off", 120))
        self.acc_chroma.set(d.get("acc_chr", 0.20))
        self.acc_light.set(d.get("acc_l", 0.80))
        self.accent_opt_var.set(d.get("accent_enabled", True))
        self.fg_mode_var.set(d.get("fg_mode", "manual"))
        self.acc_mode_var.set(d.get("acc_mode", "manual"))
        self._update_algo_info(d.get("algo", "WCAG 2.1"))
        self._set_slider_group_state(self.fg_slider_frame,
                                     d.get("fg_mode", "manual") == "manual")
        self._set_slider_group_state(self.acc_slider_frame,
                                     d.get("acc_mode", "manual") == "manual")

    def save_settings(self, preset_name=None):
        state = self._slider_state()
        with open(CURRENT_PRESET, "w") as f:
            json.dump(state, f, indent=2)
        if preset_name:
            with open(SLIDER_DIR / f"{preset_name}.json", "w") as f:
                json.dump(state, f, indent=2)

    def load_settings(self, preset_name=None):
        path = SLIDER_DIR / f"{preset_name}.json" if preset_name else CURRENT_PRESET
        if not path.exists():
            return
        try:
            with open(path) as f:
                self._apply_slider_state(json.load(f))
        except Exception:
            pass

    def _get_figlet_font_list(self):
        """Return sorted list of available figlet font stems."""
        fonts = ["standard"]
        if os.path.isdir(FIGLET_FONT_DIR):
            extras = [os.path.splitext(f)[0]
                      for f in os.listdir(FIGLET_FONT_DIR)
                      if f.endswith(('.flf', '.tlf'))]
            fonts = sorted(set(fonts + extras))
        return fonts if fonts else ["standard"]

    def _toggle_controls(self):
        self._controls_visible = not self._controls_visible
        if self._controls_visible:
            self._controls_panel.pack(fill="x", side="bottom", before=self.content_frame)
            # Populate font dropdown fresh each time
            self.live_font_menu.configure(values=self._get_figlet_font_list())
            # Pre-fill with current values
            if hasattr(self, 'current_data'):
                t = self.current_data.get("TITLE", "")
                self.live_title_entry.delete(0, "end")
                self.live_title_entry.insert(0, t)
        else:
            self._controls_panel.pack_forget()

    def _on_live_title(self):
        text = self.live_title_entry.get().strip()
        if text and hasattr(self, 'current_data'):
            self.current_data["TITLE"] = text
            self.update_ui_elements(update_title=True, update_body=False)

    def _on_live_body(self):
        text = self.live_body_entry.get().strip()
        if text and hasattr(self, 'current_data'):
            self.current_data["TEXT"] = text
            # Re-insert into body display
            self.body_display.configure(state="normal")
            self.body_display.delete("1.0", "end")
            self.body_display.insert("1.0", text)
            self.body_display.configure(state="disabled")
            self.update_ui_elements(update_title=False, update_body=True)

    def _on_live_font(self, choice):
        self.current_font_name = choice
        # Copy font to pyfiglet internals if needed
        if os.path.isdir(FIGLET_FONT_DIR) and self.internal_font_dir:
            for ext in ('.flf', '.tlf'):
                src = os.path.join(FIGLET_FONT_DIR, choice + ext)
                if os.path.exists(src):
                    dest = os.path.join(self.internal_font_dir, choice + ext)
                    if not os.path.exists(dest):
                        shutil.copy2(src, dest)
                    break
        self.update_ui_elements(update_title=True, update_body=False)

    def _get_preset_list(self):
        presets = [p.stem for p in SLIDER_DIR.glob("*.json") if p.stem != "current"]
        return presets if presets else ["-- no presets --"]

    def _refresh_preset_dropdown(self):
        self.preset_dropdown.configure(values=self._get_preset_list())
        self.preset_var.set("-- load preset --")

    def _load_preset_from_dropdown(self, choice):
        if choice in ("-- load preset --", "-- no presets --"):
            return
        self.load_settings(preset_name=choice)
        self.generate_new_pair()

    def _save_named_preset(self):
        name = self.preset_name_entry.get().strip()
        if not name:
            return
        safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
        self.save_settings(preset_name=safe)
        self.preset_name_entry.delete(0, "end")
        self._refresh_preset_dropdown()

    # ══════════════════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════════════════
    def draw_legible_text(self, x, y, text, color, anchor, font_size=42):
        shadow = "#ffffff" if self.is_dark(color) else "#000000"
        for dx, dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
            self.canvas.create_text(x+dx, y+dy, text=text,
                                    font=("Impact", font_size),
                                    fill=shadow, anchor=anchor)
        self.canvas.create_text(x, y, text=text,
                                font=("Impact", font_size),
                                fill=color, anchor=anchor)

    def is_dark(self, hex_color):
        rgb = [int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
        return (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) < 128

    def create_blob(self, canvas, x, y, size, color, outline):
        pts = []
        for i in range(32):
            angle = (i / 32) * 2 * np.pi
            r = size * random.uniform(0.9, 1.1)
            pts.extend([x + r * np.cos(angle), y + r * np.sin(angle)])
        canvas.create_polygon(pts, fill=color,
                              outline=self.fg_hex if outline else "",
                              width=4 if outline else 0, smooth=True)

    def update_names_async(self):
        try:
            r_bg  = requests.get(f"https://www.thecolorapi.com/id?hex={self.bg_hex.lstrip('#')}",     timeout=1).json()
            r_fg  = requests.get(f"https://www.thecolorapi.com/id?hex={self.fg_hex.lstrip('#')}",     timeout=1).json()
            r_acc = requests.get(f"https://www.thecolorapi.com/id?hex={self.accent_hex.lstrip('#')}", timeout=1).json()
            self.bg_name     = r_bg['name']['value']
            self.fg_name     = r_fg['name']['value']
            self.accent_name = r_acc['name']['value']
        except Exception:
            self.bg_name     = self.bg_hex
            self.fg_name     = self.fg_hex
            self.accent_name = self.accent_hex

    def update_slider_range(self, choice):
        config = self.algo_configs[choice]
        self.thresh_slider.configure(from_=config["min"], to=config["max"])
        self._update_algo_info(choice)
        self.on_param_change()


if __name__ == "__main__":
    app = ColorDashboard()
    app.mainloop()
