"""
MYTHOTEX — THE LIVING TOWER
Generative lore engine for the Arca Cognitarium.

Architecture:
  MythotexWorker      — QThread: lore generation (GPT) + image generation (SD)
  AnalysisWorker      — QThread: self-refining engine, runs off main thread
  CompendiumTome      — QDialog: vault review and aesthetic rating
  ControlPanel        — QFrame: all GPT + SD parameters, slide-out
  MythotexApp         — QMainWindow: primary interface
"""

import sys
import os
import json
import re
import shutil
import datetime
import torch
import openai

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFrame, QStatusBar, QProgressBar,
    QScrollArea, QDialog, QSlider, QSizePolicy, QComboBox, QSpinBox,
    QTabWidget,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QFont

from diffusers import (
    StableDiffusionPipeline,
    EulerDiscreteScheduler,
    DPMSolverMultistepScheduler,
    LMSDiscreteScheduler,
    PNDMScheduler,
)


# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
BASE_DIR       = os.path.expanduser("~/Mythotex")
VAULT_DIR      = os.path.join(BASE_DIR, "Vault")
REFERENTIA_DIR = os.path.join(BASE_DIR, "Referentia")
DNA_FILE       = os.path.join(BASE_DIR, "aesthetic_dna.json")
IMMUTABLE_LORE = os.path.join(REFERENTIA_DIR, "lore_immutable.md")
MUTABLE_LORE   = os.path.join(REFERENTIA_DIR, "lore_mutable.md")
GENERATION_LOG = os.path.join(BASE_DIR, "generation_log.json")

for _d in (VAULT_DIR, REFERENTIA_DIR):
    os.makedirs(_d, exist_ok=True)


# ---------------------------------------------------------------------------
# CANONICAL ATELIER -> PRODUCT MAP
# ---------------------------------------------------------------------------
ATELIER_PRODUCTS = {
    "The Verba Arcanum":              "a spell, word of power, or arcane incantation rendered as a physical inscription or glyph",
    "The Bureau of Scrollworks":      "a tome, grimoire, scroll, or cryptically bound text of significant arcane import",
    "Arx Opus":                       "an enchanted object, arcane construction, or powerful relic of unknown original purpose",
    "The Hall of Future Antiquities": "a peculiar artifact, strange heirloom, or bewildering curiosity of deeply uncertain provenance",
    "The Stavewrights Annex":         "a wand, staff, or rod of focused magical intent",
    "The Weaver's Loom":              "a ceremonial robe, protective cowl, or piece of wizardry garb",
    "The Biogenica Nexus":            "a mythical entity, familiar, homunculus, or sentient creature of biological or alchemical origin",
    "The Expansum Botanica":          "a rare mystical plant, alchemical reagent, or bottled botanical essence",
    "The Curio Cabinet":              "an eccentric oddity, puzzling contraption, or strange magical toy of obscure function",
    "The Laborum Alchemica":          "a volatile potion, elixir, or magical philtre",
    "The Jeweller's":                 "an enchanted ring, soul-gem amulet, inlaid talisman, or precious arcane adornment",
}

ATELIERS = list(ATELIER_PRODUCTS.keys())

SAMPLERS = {
    "Euler":    EulerDiscreteScheduler,
    "DPM++ 2M": DPMSolverMultistepScheduler,
    "LMS":      LMSDiscreteScheduler,
    "PNDM":     PNDMScheduler,
}

VAULT_THRESHOLD    = 5
PERIODIC_THRESHOLD = 10


# ---------------------------------------------------------------------------
# PERSISTENCE
# ---------------------------------------------------------------------------
def load_dna() -> dict:
    default = {"favored": [], "forbidden": []}
    if os.path.exists(DNA_FILE):
        try:
            with open(DNA_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_dna(dna: dict):
    with open(DNA_FILE, "w") as f:
        json.dump(dna, f, indent=4)


def load_gen_log() -> dict:
    default = {"total_generated": 0, "total_sealed": 0,
               "since_last_analysis": 0, "last_analysis_sealed": 0}
    if os.path.exists(GENERATION_LOG):
        try:
            with open(GENERATION_LOG) as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_gen_log(log: dict):
    with open(GENERATION_LOG, "w") as f:
        json.dump(log, f, indent=4)


def read_file(path: str) -> str:
    if os.path.exists(path):
        try:
            with open(path) as f:
                return f.read()
        except Exception:
            pass
    return ""


def append_mutable(content: str):
    ts    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n\n--- Analysis Pass: {ts} ---\n{content}\n"
    with open(MUTABLE_LORE, "a") as f:
        f.write(entry)


def vault_entries() -> list:
    out = []
    if not os.path.isdir(VAULT_DIR):
        return out
    for folder in sorted(os.listdir(VAULT_DIR)):
        fp = os.path.join(VAULT_DIR, folder)
        if not os.path.isdir(fp):
            continue
        files  = os.listdir(fp)
        json_f = next((x for x in files if x.endswith(".json")), None)
        if not json_f:
            continue
        try:
            with open(os.path.join(fp, json_f)) as f:
                out.append(json.load(f))
        except Exception:
            pass
    return out


# ---------------------------------------------------------------------------
# ANALYSIS WORKER
# ---------------------------------------------------------------------------
class AnalysisWorker(QThread):
    status_update = pyqtSignal(str)
    analysis_done = pyqtSignal(str)
    error_signal  = pyqtSignal(str)

    def run(self):
        try:
            self.status_update.emit("  ◈ The engine is reviewing its own work...")

            entries = vault_entries()
            if not entries:
                self.analysis_done.emit("No vault entries to analyse.")
                return

            rated    = [e for e in entries if "style_integrity" in e]
            favored  = [e for e in rated if e.get("style_integrity", 0) >= 4]
            poor     = [e for e in rated if e.get("style_integrity", 0) <= 2]
            unrated  = len([e for e in entries if "style_integrity" not in e])

            lines = []
            for e in entries[-20:]:
                r = e.get("style_integrity", "unrated")
                lines.append(f"- [{r}★] {e.get('title','?')}: {e.get('description','')}")
            summary = "\n".join(lines)

            immutable = read_file(IMMUTABLE_LORE)
            mutable   = read_file(MUTABLE_LORE)

            system_prompt = (
                "You are the analytical intelligence of the Mythotex lore engine. "
                "Review recent vault entries and their ratings. Identify patterns. "
                "Produce a concrete, specific, actionable strategy revision for both "
                "lore generation and Stable Diffusion prompting. "
                "This document is used directly — vague instructions are useless. "
                "Be honest. Reference actual entries. "
                "Tone: esoteric gravity with wry awareness.\n\n"
                "IMMUTABLE FOUNDATION:\n" + immutable[:3500] + "\n\n"
                "CURRENT STRATEGY (you are revising this):\n" + mutable[:2000]
            )

            user_prompt = (
                f"Recent entries:\n{summary}\n\n"
                f"High-rated ({len(favored)}): {[e.get('title') for e in favored]}\n"
                f"Low-rated ({len(poor)}): {[e.get('title') for e in poor]}\n"
                f"Unrated: {unrated}\n\n"
                "Produce two clearly labelled sections:\n"
                "1. LORE GENERATION STRATEGY\n"
                "2. SD PROMPT STRATEGY\n"
                "Be specific. Reference actual titles and patterns."
            )

            client   = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.4,
            )
            result = response.choices[0].message.content
            append_mutable(result)
            self.analysis_done.emit(result)

        except Exception as exc:
            self.error_signal.emit(str(exc))


# ---------------------------------------------------------------------------
# GENERATION WORKER
# ---------------------------------------------------------------------------
class MythotexWorker(QThread):
    finished      = pyqtSignal(dict)
    status_update = pyqtSignal(str)
    progress_val  = pyqtSignal(int)
    error_signal  = pyqtSignal(str)

    def __init__(self, atelier, pipe, settings, reforge=False, lore=None):
        super().__init__()
        self.atelier  = atelier
        self.pipe     = pipe
        self.settings = settings
        self.reforge  = reforge
        self.lore     = lore

    def _lore_system_prompt(self) -> str:
        immutable = read_file(IMMUTABLE_LORE)
        mutable   = read_file(MUTABLE_LORE)
        dna       = load_dna()

        dna_hint = ""
        if dna["favored"]:
            dna_hint = (
                "\n\nAESTHETIC DNA — FAVOURED (qualities from Wizard-approved outputs):\n"
                + "\n".join(f"- {d}" for d in dna["favored"][-5:])
            )

        return (
            "You are the generative oracle of the Mythotex lore engine. "
            "Your purpose: manifest arcane objects as wiki-style lore entries "
            "for the Arca Cognitarium.\n\n"
            "FOUNDATION:\n" + immutable[:4000] + "\n\n"
            "CURRENT ENGINE STRATEGY:\n" + mutable[:2000]
            + dna_hint
            + "\n\nReturn ONLY valid JSON with exactly four keys: "
            "title, description (one sentence), history (2-4 sentences), aura (brief). "
            "No preamble. No markdown. No extra keys."
        )

    def _sd_prompts(self, lore: dict) -> tuple:
        mutable = read_file(MUTABLE_LORE)
        dna     = load_dna()

        neg = (
            "modern, photorealistic, photograph, photo, 3d render, CGI, "
            "plastic, shiny, blurry, low quality, watermark, signature, text, "
            "human figure, face, vibrant colors, neon, saturated, "
            "cartoon, anime, deformed, distorted, bad anatomy"
        )
        if dna["forbidden"]:
            neg += ", " + ", ".join(dna["forbidden"][-5:])

        pos = (
            f"Isolated single object, {lore['title']}, {lore['description']}, "
            "centered on aged parchment, fine copperplate etching, "
            "17th century alchemical illustration, esoteric engraving style, "
            "intricate linework, sharp focus, masterwork, antiquarian"
        )
        return pos, neg

    def _generate_lore(self) -> dict:
        product = ATELIER_PRODUCTS.get(self.atelier, "a mysterious arcane artifact")
        client  = openai.OpenAI()
        resp    = client.chat.completions.create(
            model=self.settings.get("gpt_model", "gpt-4o"),
            messages=[
                {"role": "system", "content": self._lore_system_prompt()},
                {"role": "user",   "content": (
                    f"Manifest {product} from {self.atelier}. "
                    "Make it specific, strange, and genuinely novel. "
                    "Avoid generic fantasy tropes. Avoid heroic framing. "
                    "The object should feel discovered, not designed."
                )},
            ],
            response_format={"type": "json_object"},
            temperature=self.settings.get("gpt_temperature", 1.0),
        )
        return json.loads(resp.choices[0].message.content)

    def _generate_image(self, lore: dict) -> tuple:
        pos, neg = self._sd_prompts(lore)

        sampler_cls = SAMPLERS.get(self.settings.get("sampler", "Euler"), EulerDiscreteScheduler)
        self.pipe.scheduler = sampler_cls.from_config(self.pipe.scheduler.config)

        steps  = self.settings.get("steps",  25)
        cfg    = self.settings.get("cfg",    7.0)
        width  = self.settings.get("width",  512)
        height = self.settings.get("height", 512)
        seed   = self.settings.get("seed",   -1)

        actual_seed = torch.seed() if seed == -1 else int(seed)
        generator   = torch.Generator("cpu").manual_seed(actual_seed)

        def _cb(step, timestep, latents):
            self.progress_val.emit(int((step / steps) * 100))

        image = self.pipe(
            prompt=pos,
            negative_prompt=neg,
            num_inference_steps=steps,
            guidance_scale=cfg,
            width=width,
            height=height,
            generator=generator,
            callback=_cb,
            callback_steps=1,
        ).images[0]

        tmp = os.path.join(BASE_DIR, "temp_manifest.png")
        image.save(tmp)
        return tmp, actual_seed

    def run(self):
        try:
            if not self.reforge:
                self.status_update.emit(f"  Consulting {self.atelier}...")
                self.lore = self._generate_lore()

            self.status_update.emit(f"  Forging {self.lore.get('title', '...')}...")
            img_path, used_seed = self._generate_image(self.lore)

            log = load_gen_log()
            log["total_generated"]     = log.get("total_generated", 0) + 1
            log["since_last_analysis"] = log.get("since_last_analysis", 0) + 1
            save_gen_log(log)

            self.finished.emit({"path": img_path, "lore": self.lore, "seed": used_seed})

        except Exception as exc:
            self.error_signal.emit(str(exc))


# ---------------------------------------------------------------------------
# COMPENDIUM TOME
# ---------------------------------------------------------------------------
class CompendiumTome(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MYTHOTEX  //  COMPENDIUM TOME")
        self.setMinimumSize(1060, 750)
        self.setStyleSheet(
            "QDialog  { background: #050507; }"
            "QLabel   { color: #d4af37; font-family: 'Constantia', serif; }"
            "QPushButton { background: #0e0e16; color: #d4af37; border: 1px solid #1e1e2a; "
            "              padding: 6px 10px; font-size: 11px; }"
            "QPushButton:hover { background: #14141e; border-color: #d4af37; }"
            "QScrollArea { border: none; background: transparent; }"
        )
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.list_lay = QVBoxLayout(content)
        self.list_lay.setSpacing(0)
        self.list_lay.setContentsMargins(0, 0, 0, 0)
        self._populate()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _populate(self):
        while self.list_lay.count():
            item = self.list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not os.path.isdir(VAULT_DIR):
            return
        for folder in sorted(os.listdir(VAULT_DIR), reverse=True):
            path = os.path.join(VAULT_DIR, folder)
            if os.path.isdir(path):
                self._add_entry(path)
        self.list_lay.addStretch()

    def _add_entry(self, fp):
        files  = os.listdir(fp)
        json_f = next((x for x in files if x.endswith(".json")), None)
        png_f  = next((x for x in files if x.endswith(".png")),  None)
        if not (json_f and png_f):
            return
        try:
            with open(os.path.join(fp, json_f)) as f:
                data = json.load(f)
        except Exception:
            return

        row = QFrame()
        row.setStyleSheet(
            "QFrame { border-bottom: 1px solid #0e0e14; padding: 14px; background: #050507; }"
        )
        h = QHBoxLayout(row)
        h.setSpacing(20)

        thumb = QLabel()
        pix   = QPixmap(os.path.join(fp, png_f)).scaled(
            210, 210, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        thumb.setPixmap(pix)
        thumb.setFixedSize(210, 210)
        thumb.setStyleSheet("border: 1px solid #16161e;")

        info = QVBoxLayout()
        info.setSpacing(5)

        t = QLabel(data.get("title", "Unknown Relic"))
        t.setFont(QFont("Constantia", 13, QFont.Weight.Bold))
        t.setStyleSheet("color: #d4af37;")

        d = QLabel(data.get("description", ""))
        d.setWordWrap(True)
        d.setStyleSheet("color: #6a5a40; font-size: 12px; font-style: italic;")

        a = QLabel(f"◈  {data.get('aura','')}")
        a.setStyleSheet("color: #3a3a2e; font-size: 11px;")

        rl = QLabel("Rate the stylistic integrity — visual tone only, not lore quality:")
        rl.setStyleSheet("color: #2e2e2e; font-size: 10px; margin-top: 10px;")

        stars = QHBoxLayout()
        cur   = data.get("style_integrity", 0)
        for i in range(1, 6):
            btn = QPushButton(str(i))
            btn.setFixedSize(34, 34)
            if i <= cur:
                btn.setStyleSheet(
                    "background:#d4af37; color:#000; border-radius:17px; "
                    "font-weight:bold; border:none; font-size:12px;"
                )
            else:
                btn.setStyleSheet(
                    "background:#0a0a12; color:#333; border-radius:17px; "
                    "border:1px solid #1e1e28; font-size:12px;"
                )
            btn.clicked.connect(
                lambda _c, v=i, f=fp, jf=json_f: self._save_rating(f, jf, v)
            )
            stars.addWidget(btn)
        stars.addStretch()

        for w in (t, d, a, rl):
            info.addWidget(w)
        info.addLayout(stars)
        info.addStretch()

        h.addWidget(thumb)
        h.addLayout(info, 1)
        self.list_lay.addWidget(row)

    def _save_rating(self, fp, json_f, value):
        full = os.path.join(fp, json_f)
        try:
            with open(full, "r+") as f:
                data = json.load(f)
                data["style_integrity"] = value
                f.seek(0); json.dump(data, f, indent=4); f.truncate()
        except Exception:
            return
        dna  = load_dna()
        desc = data.get("description", "")
        if value >= 4:
            dna["favored"].append(desc)
        elif value <= 2:
            dna["forbidden"].append(desc)
        save_dna(dna)
        self._populate()


# ---------------------------------------------------------------------------
# CONTROL PANEL
# ---------------------------------------------------------------------------
class ControlPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ControlPanel")
        self.setMinimumWidth(0)
        self.setMaximumWidth(0)
        self._build()

    def _sty_label(self):
        return "color: #555; font-size: 10px; margin-top: 5px;"

    def _sty_section(self):
        return (
            "color: #3a3a2a; font-size: 9px; letter-spacing: 2px; "
            "padding: 5px 0 3px 0; border-bottom: 1px solid #111118;"
        )

    def _sty_combo(self):
        return (
            "QComboBox { background:#0a0a12; color:#c4a030; border:1px solid #1e1e2a; "
            "            padding:4px 8px; font-size:11px; }"
            "QComboBox::drop-down { border:none; }"
            "QComboBox QAbstractItemView { background:#0a0a12; color:#c4a030; "
            "                              border:1px solid #1e1e2a; }"
        )

    def _sty_spin(self):
        return (
            "QSpinBox { background:#0a0a12; color:#c4a030; border:1px solid #1e1e2a; "
            "           padding:4px 8px; font-size:11px; }"
        )

    def _sty_slider(self):
        return (
            "QSlider::groove:horizontal { background:#111118; height:3px; border-radius:2px; }"
            "QSlider::handle:horizontal { background:#c4a030; width:10px; height:10px; "
            "                             margin:-4px 0; border-radius:5px; }"
        )

    def _add_slider(self, lay, name, lo, hi, default, step=1):
        lbl = QLabel(f"{name}:  {default}")
        lbl.setStyleSheet(self._sty_label())
        sld = QSlider(Qt.Orientation.Horizontal)
        sld.setRange(lo, hi); sld.setValue(default); sld.setSingleStep(step)
        sld.valueChanged.connect(lambda v, l=lbl, n=name: l.setText(f"{n}:  {v}"))
        sld.setStyleSheet(self._sty_slider())
        lay.addWidget(lbl); lay.addWidget(sld)
        return sld

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 14, 10, 14)
        outer.setSpacing(0)

        tabs = QTabWidget()
        tabs.setStyleSheet(
            "QTabWidget::pane { border:1px solid #111118; background:#07070c; }"
            "QTabBar::tab { background:#050508; color:#3a3a3a; padding:6px 10px; "
            "               border:1px solid #0e0e18; font-size:10px; }"
            "QTabBar::tab:selected { background:#09090e; color:#c4a030; "
            "                        border-bottom:1px solid #09090e; }"
        )

        # ---- SD tab -------------------------------------------------------
        sw  = QWidget()
        sl  = QVBoxLayout(sw)
        sl.setSpacing(6); sl.setContentsMargins(8, 10, 8, 8)

        sec = QLabel("STABLE DIFFUSION"); sec.setStyleSheet(self._sty_section())
        sl.addWidget(sec)

        self.step_sld   = self._add_slider(sl, "Steps",    10, 80,  25)
        self.cfg_sld    = self._add_slider(sl, "CFG",       1, 20,   7)
        self.width_sld  = self._add_slider(sl, "Width",   256, 768, 512, step=64)
        self.height_sld = self._add_slider(sl, "Height",  256, 768, 512, step=64)

        sl.addWidget(QLabel("Sampler")).setStyleSheet if False else None
        lbl_s = QLabel("Sampler"); lbl_s.setStyleSheet(self._sty_label()); sl.addWidget(lbl_s)
        self.sampler_box = QComboBox()
        self.sampler_box.addItems(list(SAMPLERS.keys()))
        self.sampler_box.setStyleSheet(self._sty_combo())
        sl.addWidget(self.sampler_box)

        lbl_seed = QLabel("Seed  (-1 = random)"); lbl_seed.setStyleSheet(self._sty_label())
        sl.addWidget(lbl_seed)
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(-1, 2**31 - 1); self.seed_spin.setValue(-1)
        self.seed_spin.setStyleSheet(self._sty_spin())
        sl.addWidget(self.seed_spin)
        sl.addStretch()
        tabs.addTab(sw, "SD FORGE")

        # ---- GPT tab ------------------------------------------------------
        gw  = QWidget()
        gl  = QVBoxLayout(gw)
        gl.setSpacing(6); gl.setContentsMargins(8, 10, 8, 8)

        sec2 = QLabel("GPT ORACLE"); sec2.setStyleSheet(self._sty_section()); gl.addWidget(sec2)

        lbl_m = QLabel("Model"); lbl_m.setStyleSheet(self._sty_label()); gl.addWidget(lbl_m)
        self.model_box = QComboBox()
        self.model_box.addItems(["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"])
        self.model_box.setStyleSheet(self._sty_combo())
        gl.addWidget(self.model_box)

        self.temp_sld = self._add_slider(gl, "Temperature (×0.1)", 0, 20, 10)

        sec3 = QLabel("ANALYSIS ENGINE"); sec3.setStyleSheet(self._sty_section()); gl.addWidget(sec3)

        lbl_vt = QLabel("Vault threshold (every N seals)"); lbl_vt.setStyleSheet(self._sty_label())
        gl.addWidget(lbl_vt)
        self.vault_thresh = QSpinBox()
        self.vault_thresh.setRange(1, 50); self.vault_thresh.setValue(VAULT_THRESHOLD)
        self.vault_thresh.setStyleSheet(self._sty_spin())
        gl.addWidget(self.vault_thresh)

        lbl_pt = QLabel("Periodic threshold (every N generated)"); lbl_pt.setStyleSheet(self._sty_label())
        gl.addWidget(lbl_pt)
        self.periodic_thresh = QSpinBox()
        self.periodic_thresh.setRange(1, 100); self.periodic_thresh.setValue(PERIODIC_THRESHOLD)
        self.periodic_thresh.setStyleSheet(self._sty_spin())
        gl.addWidget(self.periodic_thresh)

        gl.addStretch()
        tabs.addTab(gw, "GPT ORACLE")

        outer.addWidget(tabs)

    def settings(self) -> dict:
        return {
            "steps":              self.step_sld.value(),
            "cfg":                self.cfg_sld.value(),
            "width":              self.width_sld.value(),
            "height":             self.height_sld.value(),
            "sampler":            self.sampler_box.currentText(),
            "seed":               self.seed_spin.value(),
            "gpt_model":          self.model_box.currentText(),
            "gpt_temperature":    self.temp_sld.value() / 10.0,
            "vault_threshold":    self.vault_thresh.value(),
            "periodic_threshold": self.periodic_thresh.value(),
        }


# ---------------------------------------------------------------------------
# MAIN APPLICATION
# ---------------------------------------------------------------------------
class MythotexApp(QMainWindow):

    def __init__(self, pipe):
        super().__init__()
        self.pipe            = pipe
        self.latest_data     = None
        self.worker          = None
        self.analysis_worker = None
        self._panel_open     = False

        self.setWindowTitle("MYTHOTEX  //  THE LIVING TOWER")
        self.setMinimumSize(1300, 920)
        self.setStyleSheet(self._styles())
        self._build_ui()
        self._maybe_analyse(on_save=False)

    def _styles(self):
        return """
        QMainWindow, QWidget#Root { background: #050507; }
        QFrame#Sidebar {
            background: #06060a;
            border-right: 1px solid #111118;
        }
        QLabel { color: #d4af37; font-family: 'Constantia', 'Georgia', serif; }
        QPushButton {
            background: #080810;
            color: #b09030;
            border: 1px solid #18182a;
            padding: 10px 12px;
            font-family: 'Constantia', 'Georgia', serif;
            font-size: 11px;
            font-weight: bold;
            text-align: left;
        }
        QPushButton:hover {
            background: #0e0e1a;
            border-color: #d4af37;
            color: #d4af37;
        }
        QPushButton:disabled { color: #252525; border-color: #0e0e14; }
        QPushButton#Action {
            text-align: center;
            padding: 10px 24px;
            border-color: #1e1e2a;
        }
        QProgressBar {
            border: 1px solid #111118;
            background: #020203;
            height: 4px;
        }
        QProgressBar::chunk { background: #6a5018; }
        QTextEdit {
            background: #020203;
            color: #907858;
            border: 1px solid #0a0a10;
            font-family: 'Constantia', 'Georgia', serif;
            font-size: 13px;
            padding: 10px;
        }
        QStatusBar {
            background: #030304;
            color: #2e2e2e;
            font-size: 11px;
            border-top: 1px solid #0a0a10;
        }
        QFrame#ControlPanel {
            background: #06060a;
            border-left: 1px solid #111118;
        }
        """

    def _build_ui(self):
        root = QWidget(); root.setObjectName("Root")
        rl   = QHBoxLayout(root); rl.setSpacing(0); rl.setContentsMargins(0,0,0,0)
        self.setCentralWidget(root)

        # SIDEBAR
        sidebar = QFrame(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(218)
        sl = QVBoxLayout(sidebar); sl.setContentsMargins(0,14,0,8); sl.setSpacing(0)

        hdr = QLabel("  ◆  THE ATELIERS")
        hdr.setStyleSheet("color:#2a2a1c; font-size:9px; letter-spacing:4px; "
                          "padding:0 0 10px 0; border-bottom:1px solid #0e0e14;")
        sl.addWidget(hdr)

        sc  = QScrollArea(); sc.setWidgetResizable(True)
        sc.setStyleSheet("border:none; background:transparent;")
        scw = QWidget(); scl = QVBoxLayout(scw)
        scl.setSpacing(1); scl.setContentsMargins(4,6,4,4)
        for atelier in ATELIERS:
            btn = QPushButton(f"  {atelier}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _c, a=atelier: self._begin_ritual(a))
            scl.addWidget(btn)
        scl.addStretch(); sc.setWidget(scw); sl.addWidget(sc, 1)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#0a0a10; max-height:1px; border:none;")
        sl.addWidget(sep)

        self.comp_btn   = QPushButton("  ◎  COMPENDIUM TOME")
        self.params_btn = QPushButton("  ⚙  RITUAL PARAMETERS")
        self.comp_btn.clicked.connect(lambda: CompendiumTome(self).exec())
        self.params_btn.clicked.connect(self._toggle_panel)
        sl.addWidget(self.comp_btn); sl.addWidget(self.params_btn)

        # VIEWPORT
        vl = QVBoxLayout(); vl.setContentsMargins(22,20,22,10); vl.setSpacing(8)

        self.img_lbl = QLabel("The Tower is Silent.")
        self.img_lbl.setFixedSize(768, 768)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setStyleSheet(
            "border:1px solid #0e0e16; background:#020203; "
            "color:#1c1c1c; font-size:16px; font-family:'Constantia',serif;"
        )

        self.progress = QProgressBar()
        self.progress.setValue(0); self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)

        self.lore_txt = QTextEdit(); self.lore_txt.setReadOnly(True)
        self.lore_txt.setFixedHeight(178)

        self.seed_lbl = QLabel("")
        self.seed_lbl.setStyleSheet("color:#1e1e1e; font-size:10px;")
        self.seed_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        ar = QHBoxLayout()
        self.seal_btn    = QPushButton("SEAL IN VAULT")
        self.reforge_btn = QPushButton("REFORGE VISUAL")
        for b in (self.seal_btn, self.reforge_btn):
            b.setObjectName("Action"); b.setEnabled(False)
        self.seal_btn.clicked.connect(self._seal)
        self.reforge_btn.clicked.connect(self._reforge)
        ar.addWidget(self.seal_btn); ar.addWidget(self.reforge_btn)

        vl.addWidget(self.img_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        vl.addWidget(self.progress)
        vl.addWidget(self.lore_txt)
        vl.addWidget(self.seed_lbl)
        vl.addLayout(ar)

        # CONTROL PANEL
        self.ctrl = ControlPanel()

        rl.addWidget(sidebar)
        rl.addLayout(vl, 1)
        rl.addWidget(self.ctrl)

        self.status_bar = QStatusBar(); self.setStatusBar(self.status_bar)

    # -----------------------------------------------------------------------
    def _toggle_panel(self):
        self._panel_open = not self._panel_open
        target = 270 if self._panel_open else 0
        self._anim = QPropertyAnimation(self.ctrl, b"maximumWidth")
        self._anim.setDuration(240); self._anim.setEndValue(target)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad); self._anim.start()

    def _begin_ritual(self, atelier):
        if self.worker and self.worker.isRunning():
            self.status_bar.showMessage("  A ritual is already in progress..."); return
        self._lock(False)
        self.progress.setValue(0); self.lore_txt.clear()
        self.img_lbl.setPixmap(QPixmap()); self.img_lbl.setText("Communing with the Aether...")
        self.seed_lbl.setText("")
        self.worker = MythotexWorker(atelier, self.pipe, self.ctrl.settings())
        self.worker.status_update.connect(self.status_bar.showMessage)
        self.worker.progress_val.connect(self.progress.setValue)
        self.worker.finished.connect(self._on_done)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _reforge(self):
        if not self.latest_data or (self.worker and self.worker.isRunning()): return
        self._lock(False); self.progress.setValue(0)
        self.img_lbl.setPixmap(QPixmap()); self.img_lbl.setText("Reforging the Visual...")
        self.worker = MythotexWorker("", self.pipe, self.ctrl.settings(),
                                     reforge=True, lore=self.latest_data["lore"])
        self.worker.status_update.connect(self.status_bar.showMessage)
        self.worker.progress_val.connect(self.progress.setValue)
        self.worker.finished.connect(self._on_done)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_done(self, data):
        self.latest_data = data
        self._lock(True); self.progress.setValue(100)
        pix = QPixmap(data["path"]).scaled(
            768, 768, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.img_lbl.setPixmap(pix)
        l = data["lore"]
        self.lore_txt.setHtml(
            "<center>"
            f"<h2 style='color:#d4af37;margin-bottom:2px;letter-spacing:1px;'>{l.get('title','')}</h2>"
            f"<p style='color:#5a4a30;margin-top:0;font-style:italic;'>{l.get('description','')}</p>"
            "</center>"
            f"<div style='margin:4px 24px;line-height:1.65;color:#806848;'>{l.get('history','')}</div>"
            f"<p style='text-align:center;margin-top:8px;'>"
            f"<span style='color:#252518;'>◈</span>  "
            f"<span style='color:#3a3828;'>{l.get('aura','')}</span></p>"
        )
        self.seed_lbl.setText(f"seed  {data.get('seed','')}")
        self.status_bar.showMessage(f"  {l.get('title','')}  —  manifested.")
        self._maybe_analyse(on_save=False)

    def _on_error(self, msg):
        self._lock(False)
        self.img_lbl.setText("The ritual failed.")
        self.lore_txt.setPlainText(f"The Forge encountered an error:\n\n{msg}")
        self.status_bar.showMessage(f"  The ritual failed  —  {msg[:90]}")

    def _seal(self):
        if not self.latest_data: return
        title = self.latest_data["lore"].get("title", "unknown_relic")
        slug  = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")[:60]
        dest  = os.path.join(VAULT_DIR, slug); os.makedirs(dest, exist_ok=True)
        ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        src   = self.latest_data["path"]
        if os.path.exists(src):
            shutil.move(src, os.path.join(dest, f"relic_{ts}.png"))
        entry = dict(self.latest_data["lore"])
        entry["seed"] = self.latest_data.get("seed", -1)
        with open(os.path.join(dest, f"relic_{ts}.json"), "w") as f:
            json.dump(entry, f, indent=4)
        log = load_gen_log()
        log["total_sealed"] = log.get("total_sealed", 0) + 1
        save_gen_log(log)
        self.status_bar.showMessage(f"  Bound to Vault:  {slug}")
        self.seal_btn.setEnabled(False)
        self._maybe_analyse(on_save=True)

    def _maybe_analyse(self, on_save: bool):
        if self.analysis_worker and self.analysis_worker.isRunning(): return
        log    = load_gen_log()
        setts  = self.ctrl.settings()
        vt     = setts.get("vault_threshold",    VAULT_THRESHOLD)
        pt     = setts.get("periodic_threshold", PERIODIC_THRESHOLD)
        sealed = log.get("total_sealed",         0)
        since  = log.get("since_last_analysis",  0)
        last   = log.get("last_analysis_sealed", 0)
        v_trig = on_save  and (sealed - last) >= vt
        p_trig = not on_save and since >= pt
        if v_trig or p_trig:
            reason = "vault threshold" if v_trig else "periodic threshold"
            self.status_bar.showMessage(f"  ◈ Analysis pass triggered  ({reason})...")
            self.analysis_worker = AnalysisWorker()
            self.analysis_worker.status_update.connect(self.status_bar.showMessage)
            self.analysis_worker.analysis_done.connect(
                lambda _r, s=sealed: self._on_analysis(_r, s))
            self.analysis_worker.error_signal.connect(
                lambda e: self.status_bar.showMessage(f"  Analysis error:  {e[:80]}"))
            self.analysis_worker.start()

    def _on_analysis(self, _result: str, sealed_at: int):
        log = load_gen_log()
        log["last_analysis_sealed"] = sealed_at
        log["since_last_analysis"]  = 0
        save_gen_log(log)
        self.status_bar.showMessage("  ◈ Engine strategy updated.")

    def _lock(self, enabled: bool):
        self.seal_btn.setEnabled(enabled)
        self.reforge_btn.setEnabled(enabled)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    print("Initialising the Stable Diffusion pipeline — please wait...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float32,
    ).to("cpu")
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.enable_attention_slicing()
    pipe.vae.enable_slicing()
    print("Pipeline ready. The Tower awakens.")

    window = MythotexApp(pipe)
    window.show()
    sys.exit(app.exec())
