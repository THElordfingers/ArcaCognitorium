# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                      ModusArcanus.dux.tome.md   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

# Modus Arcanus — The Arcane Desktop Style Guide
### Visual & Thematic Design System · PyQt6 · CastrumDigitos

> Attach this file when commissioning a new desktop application.
> It defines the complete aesthetic language: colour, type, widgets, naming, tone.
> The app spec lives elsewhere. This is purely *how it looks and feels*.

---

## I. PHILOSOPHY

Every application built under this system is a **crafted instrument**, not a utility.
The interface is the atelier — each widget a component of a larger arcane apparatus.

- Darkness is not absence. It is material, weighty, intentional.
- Gold signals authority, interactivity, and structure. It is not decorative excess.
- The UI should feel like it was bound in leather and illuminated by candlelight,
  then rendered in pixels.
- Restraint over ornamentation. Every embellishment must earn its place.
- The app has an inner world. Its names, labels, and copy reflect that world.

---

## II. COLOUR SYSTEM  (Chromata Arcana)

```python
C_BG        = "#050507"   # Void — primary background, near-black with blue undertone
C_PANEL     = "#0a0a12"   # Obsidian — panels, cards, dialogs, input fields
C_GOLD      = "#d4af37"   # Aurum — primary accent, active text, titles, borders
C_GOLD_DIM  = "#7a6a2a"   # Aurum Dimmus — hints, subtitles, inactive labels
C_GOLD_DARK = "#3a2e10"   # Aurum Nox — panel borders, separator lines, hover fill
C_CRIMSON   = "#8b1a1a"   # Sanguis — destructive actions, warnings, delete
C_TEAL      = "#1a5a5a"   # Viridis — confirmations, saves, secondary actions
C_TEXT      = "#c8b88a"   # Parchment — body text, field content
C_SUBTLE    = "#3a3528"   # Umbra — very dark warm tone, inactive borders
C_WHITE     = "#e8e0cc"   # Vellum — emphasis text, highlighted values
```

**Rules:**
- Never use pure `#ffffff` or `#000000`. Every neutral carries warmth.
- No cool greys. The palette runs warm throughout.
- Background hierarchy: `C_BG` → `C_PANEL` → `C_SUBTLE`. Never lighter than `C_PANEL` for containers.
- Gold is the *only* bright colour. Everything else defers to it.
- `C_CRIMSON` and `C_TEAL` are accent punctuation — use sparingly and intentionally.

---

## III. TYPOGRAPHY

```
Font stack:   Georgia, Constantia, serif
              (no sans-serif anywhere in primary UI)

Window/dialog title:    16px, bold, C_GOLD
Section headers:        13–14px, bold, C_GOLD
Form labels / hints:    10–11px, normal, C_GOLD_DIM
Body / text fields:     11px, normal, C_TEXT
Micro labels (caps):    9px, letter-spacing: 2px, C_GOLD_DIM, UPPERCASE
Status bar:             10px, C_GOLD_DIM
Button text:            11px, letter-spacing: 1px, colour = accent
```

**The micro-label pattern** — uppercase + letter-spacing — is the signature typographic
move of this system. Use it on field labels above text inputs:
`DESCRIPTION`, `HISTORY`, `AURA`, `STATUS`, `ANALYSIS`.
It reads as engraved, not printed.

---

## IV. WIDGET PATTERNS

### The arcane_button factory
```python
def arcane_button(text: str, accent: str = C_GOLD) -> QPushButton:
    btn = QPushButton(text)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {C_PANEL};
            color: {accent};
            border: 1px solid {C_GOLD_DARK};
            font-family: Georgia, serif;
            font-size: 11px;
            padding: 6px 14px;
            letter-spacing: 1px;
        }}
        QPushButton:hover  {{ background: {C_GOLD_DARK}; border-color: {accent}; }}
        QPushButton:pressed {{ background: {C_SUBTLE}; }}
        QPushButton:disabled {{ color: {C_GOLD_DARK}; border-color: {C_SUBTLE}; }}
    """)
    return btn
```

Accent by intent: `C_GOLD` = primary/neutral · `C_TEAL` = confirm/save · `C_CRIMSON` = destroy/remove

### Label factories
```python
def gold_label(text, size=11, bold=False) -> QLabel   # Headers, section titles
def dim_label(text, size=10) -> QLabel                # Hints, subtitles, form labels
```

### Sliders
Groove: `C_SUBTLE`, 4px. Handle: `C_GOLD`, 12×12px circle. Sub-page fill: `C_GOLD_DIM`.

### ComboBoxes
Background `C_BG` · text `C_GOLD` · border `C_GOLD_DARK`
Dropdown view: background `C_PANEL` · selection `C_GOLD_DARK`

### Text fields (read-only lore / data display)
Background `C_BG` · text `C_TEXT` · border `C_SUBTLE` · padding 6px · Georgia 11px

### Separators
`QFrame.Shape.HLine` · `setStyleSheet(f"color: {C_GOLD_DARK};")`
Use to divide logical regions. Never use blank space alone as a divider.

### ScrollArea / ScrollBar
Background `C_BG` · 8px width · handle `C_GOLD_DARK` · no arrow buttons

### Global stylesheet base
```python
GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: Georgia, Constantia, serif;
}}
QScrollBar:vertical {{
    background: {C_PANEL}; width: 8px; border: none;
}}
QScrollBar::handle:vertical {{
    background: {C_GOLD_DARK}; border-radius: 4px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
    background: {C_PANEL}; height: 8px; border: none;
}}
QScrollBar::handle:horizontal {{
    background: {C_GOLD_DARK}; border-radius: 4px;
}}
QToolTip {{
    background: {C_PANEL}; color: {C_GOLD};
    border: 1px solid {C_GOLD_DARK};
    font-family: Georgia, serif; padding: 4px;
}}
"""
```

---

## V. LAYOUT ARCHITECTURE

```
QMainWindow
├── ControlPanel     (QFrame, slide-out left, fixed 280px, starts collapsed)
└── Content
    ├── TopBar       (QFrame, 52px, C_PANEL, border-bottom C_GOLD_DARK)
    │   ├── ☰ toggle (left)
    │   ├── App title (gold, bold, centre-left)
    │   └── Action buttons (right-aligned)
    ├── Body         (primary content, margins 16px, spacing 16px)
    └── StatusBar    (QFrame, 28px, C_PANEL, border-top C_GOLD_DARK)
        ├── Status message (left, dim)
        └── Context label  (right, dim)
```

**ControlPanel slide animation (220ms, InOutQuad):**
```python
anim = QPropertyAnimation(self, b"maximumWidth", self)
anim.setDuration(220)
anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
anim.setStartValue(start); anim.setEndValue(end)
anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
```

---

## VI. NAMING CONVENTIONS  (Nomina Arcana)

Names in this system are **Latin or Latin-adjacent**, noun-first, nominative case.
They should feel like they were coined by a medieval cartographer or alchemist.

**Class names:**
- Main window: `[App]App` — `MythotexApp`, `SonorumApp`, `FenestriumApp`
- Worker thread: `[Function]Worker` — `GenerationWorker`, `AnalysisWorker`
- Vault/review dialog: `[Name]Tome` — `CompendiumTome`, `ArchiviumTome`
- Slide-out panel: always `ControlPanel`

**UI label vocabulary:**
```
Storage/Collection:  Thesaurus · Armarium · Repositorium · Arcanum · Compendium
Analysis/Logic:      Analytica · Cogitatio · Ratio · Machina
Generation/Output:   Fabrica · Genesis · Manifestatio · Productio
Display/View:        Specularium · Fenestra · Visio · Perspiculum
Control:             Machina Controli · Gubernaculum · Regimen
Reference/Docs:      Referentia · Codex · Liber · Memoria · Tomis
Worker/Process:      Operarius · Faber · Artifex · Magister
Settings:            Configuratio · Dispositio · Ordinatio
Status:              Vigilia · Status · Notitia
Files/Tree:          Arbor · Sylva · Radix
```

**In-UI copy tone:**
- Buttons use symbolic prefixes: `⚗ Manifest`, `🜲 Seal`, `⚙ Analyse`, `✕ Discard`
- Section dividers use `✦` as ornament: `✦  Section Name  ✦`
- Status messages are declarative and slightly archaic:
  `"The Arca Cognitarium awaits your command."` not `"Ready."`
  `"Artifact manifested: The Glaive of Sorrow"` not `"Done."`

---

## VII. FILE HEADER

Every `.py` file begins with:

```
#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      [APP NAME / ASCII LOGO]                                                     ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                              filename.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
```

---

## VIII. RUNTIME CONTEXT

```
OS:        Debian Trixie / KDE Plasma 6 / X11
User:      lordfingers @ CastrumDigitos
Framework: PyQt6
Paths:     Always Path.home() — never hardcode /home/lordfingers
Clipboard: xclip only (X11)
API:       CLAUDE_API_KEY env var
```

---

*Finis Tomi · Modus Arcanus · ＭＭＸＸＶＩ*
