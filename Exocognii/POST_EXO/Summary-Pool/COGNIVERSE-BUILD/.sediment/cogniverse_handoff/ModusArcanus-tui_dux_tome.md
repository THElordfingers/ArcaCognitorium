# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ          ModusArcanus.tui.dux.tome.md   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

# Modus Arcanus — TUI Edition
### Textual & Rich Design System · Arcane Terminal Aesthetic · CastrumDigitos

> Attach this file when commissioning a Textual or Rich terminal application.
> It is the TUI counterpart to ModusArcanus.dux.tome.md.
> The app spec lives elsewhere. This defines colour, layout, widget style,
> CSS, naming, and copy tone for the terminal medium.

---

## I. PHILOSOPHY

The terminal is not a degraded desktop. It is a different instrument entirely —
closer to a scrying mirror than a window. Text is the material. Every character
placed on screen is a deliberate mark.

Under Modus Arcanus, a TUI application should feel like a **manuscript rendered
in phosphor** — structured, legible, atmospheric. The grid is sacred. The border
is architecture. The colour is controlled fire.

- Density is a feature. Terminal space is precious; use it intentionally.
- Every panel has a named purpose. Nothing floats without a frame.
- Animation is ceremony — reserved for transitions that carry meaning.
- The app speaks in the same archaic-declarative voice as its desktop kin.
- Rich markup and Textual CSS share the same palette. They are one system.

---

## II. COLOUR SYSTEM  (Chromata Terminalis)

### Named colour tokens

These map to the exact hues of the desktop system, adjusted for terminal rendering.

```
VOID        #050507    Primary background — the absolute dark
OBSIDIAN    #0a0a12    Panel backgrounds, widget surfaces
AURUM       #d4af37    Primary accent — gold. Titles, borders, focus rings
AURUM_DIM   #7a6a2a    Secondary gold — hints, labels, inactive elements
AURUM_NOX   #3a2e10    Dark gold — panel borders, rule lines, subtle fills
SANGUIS     #8b1a1a    Crimson — warnings, destructive, errors
VIRIDIS     #1a5a5a    Teal — confirmations, success, secondary actions
PARCHMENT   #c8b88a    Body text — warm off-white, all readable content
UMBRA       #3a3528    Very dark warm — inactive borders, backgrounds
VELLUM      #e8e0cc    Near-white — emphasis, highlighted values, headers
```

### Rich markup usage

```python
# Titles and headers
"[bold #d4af37]Section Title[/bold #d4af37]"

# Dimmed labels and hints
"[#7a6a2a]hint text[/#7a6a2a]"

# Body / readable content
"[#c8b88a]paragraph text[/#c8b88a]"

# Emphasis / values
"[bold #e8e0cc]important value[/bold #e8e0cc]"

# Danger / error
"[bold #8b1a1a]✕ Error message[/bold #8b1a1a]"

# Success / confirm
"[#1a5a5a]✦ Operation complete[/#1a5a5a]"

# Keyword / tag / token
"[italic #d4af37]keyword[/italic #d4af37]"
```

### Textual CSS colour vars

```css
/* In your app.css or DEFAULT_CSS */
$void:       #050507;
$obsidian:   #0a0a12;
$aurum:      #d4af37;
$aurum-dim:  #7a6a2a;
$aurum-nox:  #3a2e10;
$sanguis:    #8b1a1a;
$viridis:    #1a5a5a;
$parchment:  #c8b88a;
$umbra:      #3a3528;
$vellum:     #e8e0cc;
```

---

## III. TEXTUAL CSS — BASE SYSTEM

```css
/* ── Root & Screen ─────────────────────────────────────────────────── */

Screen {
    background: $void;
    color: $parchment;
}

/* ── Panels & Containers ────────────────────────────────────────────── */

Vertical, Horizontal, Container {
    background: $void;
}

/* Named panel surfaces — use these widget classes */
.panel {
    background: $obsidian;
    border: tall $aurum-nox;
    padding: 1 2;
}

.panel-inset {
    background: $void;
    border: round $umbra;
    padding: 1;
}

.panel--focused {
    border: tall $aurum;
}

/* ── Headers & Titles ───────────────────────────────────────────────── */

.header {
    background: $obsidian;
    border-bottom: tall $aurum-nox;
    padding: 0 2;
    height: 3;
}

.title {
    color: $aurum;
    text-style: bold;
}

.subtitle {
    color: $aurum-dim;
}

/* ── Status Bar ─────────────────────────────────────────────────────── */

.statusbar {
    background: $obsidian;
    border-top: tall $aurum-nox;
    height: 1;
    padding: 0 2;
    color: $aurum-dim;
}

/* ── Buttons ────────────────────────────────────────────────────────── */

Button {
    background: $obsidian;
    color: $aurum;
    border: tall $aurum-nox;
    padding: 0 3;
    text-style: none;
    min-width: 16;
}

Button:hover {
    background: $aurum-nox;
    border: tall $aurum;
    color: $vellum;
}

Button:focus {
    border: tall $aurum;
    text-style: bold;
}

Button.-confirm {
    color: $viridis;
    border: tall $viridis;
}

Button.-confirm:hover {
    background: $viridis;
    color: $vellum;
}

Button.-danger {
    color: $sanguis;
    border: tall $sanguis;
}

Button.-danger:hover {
    background: $sanguis;
    color: $vellum;
}

/* ── Input ──────────────────────────────────────────────────────────── */

Input {
    background: $void;
    color: $parchment;
    border: tall $umbra;
    padding: 0 2;
}

Input:focus {
    border: tall $aurum;
    color: $vellum;
}

Input.-invalid {
    border: tall $sanguis;
}

/* ── TextArea ───────────────────────────────────────────────────────── */

TextArea {
    background: $void;
    color: $parchment;
    border: tall $umbra;
    padding: 1 2;
    scrollbar-color: $aurum-nox;
    scrollbar-color-hover: $aurum-dim;
}

TextArea:focus {
    border: tall $aurum;
}

/* ── Select / OptionList ────────────────────────────────────────────── */

Select {
    background: $obsidian;
    color: $aurum;
    border: tall $aurum-nox;
}

Select:focus {
    border: tall $aurum;
}

SelectOverlay {
    background: $obsidian;
    border: tall $aurum-nox;
}

Option {
    color: $parchment;
    padding: 0 2;
}

Option:hover {
    background: $aurum-nox;
    color: $aurum;
}

Option.-selected {
    background: $aurum-nox;
    color: $aurum;
    text-style: bold;
}

/* ── ListView / DataTable ───────────────────────────────────────────── */

ListView {
    background: $void;
    border: tall $umbra;
}

ListItem {
    background: $void;
    color: $parchment;
    padding: 0 2;
}

ListItem:hover {
    background: $obsidian;
}

ListItem.-selected {
    background: $aurum-nox;
    color: $aurum;
}

DataTable {
    background: $void;
    color: $parchment;
}

DataTable > .datatable--header {
    background: $obsidian;
    color: $aurum;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: $aurum-nox;
    color: $vellum;
}

DataTable > .datatable--fixed {
    color: $aurum-dim;
}

/* ── Progress Bar ───────────────────────────────────────────────────── */

ProgressBar {
    color: $aurum;
    background: $umbra;
}

ProgressBar > .bar--complete {
    color: $viridis;
}

/* ── Scrollbar ──────────────────────────────────────────────────────── */

ScrollBar {
    background: $obsidian;
    color: $aurum-nox;
}

ScrollBar:hover {
    color: $aurum-dim;
}

/* ── Rule / Divider ─────────────────────────────────────────────────── */

Rule {
    color: $aurum-nox;
}

Rule.-heavy {
    color: $aurum-dim;
}

/* ── Tooltip ────────────────────────────────────────────────────────── */

Tooltip {
    background: $obsidian;
    color: $aurum;
    border: tall $aurum-nox;
    padding: 0 2;
}

/* ── Tabs ───────────────────────────────────────────────────────────── */

TabbedContent > TabPane {
    background: $void;
    border: tall $aurum-nox;
    padding: 1 2;
}

Tabs {
    background: $obsidian;
    border-bottom: tall $aurum-nox;
}

Tab {
    color: $aurum-dim;
    background: $obsidian;
    padding: 0 3;
}

Tab:hover {
    color: $aurum;
    background: $aurum-nox;
}

Tab.-active {
    color: $aurum;
    background: $void;
    text-style: bold;
    border-top: tall $aurum;
}

/* ── Log / RichLog ──────────────────────────────────────────────────── */

RichLog {
    background: $void;
    color: $parchment;
    border: tall $umbra;
    scrollbar-color: $aurum-nox;
}

/* ── Modal / ModalScreen ────────────────────────────────────────────── */

ModalScreen {
    background: $void 80%;
    align: center middle;
}

.modal-dialog {
    background: $obsidian;
    border: tall $aurum;
    padding: 2 4;
    width: 60;
    max-height: 80vh;
}

.modal-title {
    color: $aurum;
    text-style: bold;
    text-align: center;
}
```

---

## IV. TEXTUAL APP SKELETON

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Rule
from textual.containers import Horizontal, Vertical, Container


class [AppName]App(App):

    CSS = """
    /* paste relevant rules from section III */
    """

    TITLE    = "✦  [APP NAME]  ✦"
    SUB_TITLE = "[tagline in Latin or arcane English]"

    BINDINGS = [
        ("q",   "quit",        "Exire"),
        ("?",   "help",        "Auxilium"),
        ("ctrl+p", "panel",    "Gubernaculum"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield [SidePanel]()          # slide-out or persistent left panel
            with Vertical(id="main"):
                yield [PrimaryView]()    # primary content area
        yield Footer()

    def on_mount(self) -> None:
        self.title     = "✦  [APP NAME]  ✦"
        self.sub_title = "[tagline]"
```

**Header & Footer** inherit theme automatically via CSS.
**Footer** key bindings use Latin verbs (see section VI).

---

## V. RICH CONSOLE PATTERNS

For non-Textual scripts using Rich directly:

```python
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

ARCANE_THEME = Theme({
    "title":    "bold #d4af37",
    "subtitle": "#7a6a2a",
    "body":     "#c8b88a",
    "emphasis": "bold #e8e0cc",
    "gold":     "#d4af37",
    "dim":      "#7a6a2a",
    "danger":   "bold #8b1a1a",
    "success":  "#1a5a5a",
    "keyword":  "italic #d4af37",
    "border":   "#3a2e10",
})

console = Console(theme=ARCANE_THEME)

# Section header
console.rule("[title]✦  SECTION NAME  ✦[/title]", style="#3a2e10")

# Panel
console.print(Panel(
    "[body]Content goes here.[/body]",
    title="[title]Titulus[/title]",
    border_style="#3a2e10",
    padding=(1, 2),
))

# Status line
console.print("[dim]⚙  Processing…[/dim]")
console.print("[success]✦  Complete.[/success]")
console.print("[danger]✕  Failed: reason[/danger]")
```

---

## VI. ORNAMENTS & COPY TONE

### Symbolic prefixes for actions and status

```
⚗   Generate / manifest / produce
🜲   Save / seal / commit
⚙   Process / analyse / configure
✦   Complete / success / section marker
✕   Error / delete / close / discard
⌬   Warning / caution
☿   Transform / convert / transmute
🝓   Lock / protect / seal
◈   Selected / active item
·   List separator (inline): "iron  ·  bone  ·  obsidian"
─   Horizontal rule (inline ASCII fallback)
```

### Section dividers (Rich Rule)

```python
console.rule("[#7a6a2a]✦  Referentia  ✦[/#7a6a2a]", style="#3a2e10")
```

### Status messages — voice and register

Write status copy as declarative archaic English, not terse system output.

```
✗ "Ready."                          → "The apparatus awaits."
✗ "Processing..."                   → "⚙  Consulting the Arca Cognitarium…"
✗ "Done."                           → "✦  Manifestation complete."
✗ "Error: connection failed"        → "✕  The link could not be forged."
✗ "Saving..."                       → "🜲  Sealing to the vault…"
✗ "Deleted."                        → "The artifact has been unbound."
✗ "Loading"                         → "Summoning from the Referentia…"
```

Precision still required — append the specific object or detail:
`"✦  Artifact manifested: The Osseous Mandible of Verath"`
not just `"✦  Manifestation complete."`

### Textual Footer bindings — Latin verb labels

```python
BINDINGS = [
    ("q",      "quit",    "Exire"),        # Exit
    ("n",      "new",     "Novum"),        # New
    ("s",      "save",    "Sigillare"),    # Seal/Save
    ("d",      "delete",  "Dissolvere"),   # Dissolve/Delete
    ("a",      "analyse", "Analytica"),    # Analyse
    ("r",      "refresh", "Renovare"),     # Renew/Refresh
    ("?",      "help",    "Auxilium"),     # Help
    ("ctrl+p", "panel",   "Gubernaculum"), # Control panel
    ("escape", "back",    "Revertere"),    # Return
    ("enter",  "select",  "Eligere"),      # Select/Choose
]
```

---

## VII. WIDGET NAMING CONVENTIONS  (Nomina Terminalia)

Widget IDs and class names follow the same Latin vocabulary as the desktop system.

```python
# IDs — lowercase, hyphenated
id="specularium"       # preview / display pane
id="classis"           # list / collection browser
id="arbor"             # file tree
id="codex"             # code or text output panel
id="referentia"        # reference / docs pane
id="vigilia"           # status / log pane
id="gubernaculum"      # control / settings sidebar
id="armarium"          # vault / storage browser
id="fabrica"           # generation / creation panel
id="analytica"         # analysis output panel

# CSS classes — dot-prefixed, hyphenated
.panel
.panel--active
.panel--dim
.label-field          # micro uppercase label above an input
.status-line
.card                 # list item card
.card--selected
.tag                  # inline keyword/tag chip
```

---

## VIII. LAYOUT PATTERNS

### Three-pane (most common)
```
┌──────────────┬────────────────────────┬──────────────┐
│  Classis     │  Specularium           │  Codex       │
│  (list/tree) │  (primary view)        │  (output)    │
│              │                        │              │
└──────────────┴────────────────────────┴──────────────┘
```

### Two-pane with sidebar
```
┌──────────────┬────────────────────────────────────────┐
│ Gubernaculum │  Primary Content                       │
│ (controls)   │                                        │
│              │                                        │
└──────────────┴────────────────────────────────────────┘
```

### Header anatomy
```
┌────────────────────────────────────────────────────────┐
│ ✦  APP NAME  ✦                          [sub_title]    │
│ border-bottom: $aurum-nox                              │
└────────────────────────────────────────────────────────┘
```

### Card pattern (in ListViews / OptionLists)
```
┌─────────────────────────────────────────────────────┐
│  [bold $aurum]Title of Item[/]                      │
│  [dim]Category · Tag · Tag[/dim]                    │
│  [body]One-line description of the item.[/body]     │
└─────────────────────────────────────────────────────┘
```

---

## IX. FILE HEADER

```python
#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                              filename.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
```

*(No docstring block — terminal apps use the `#` header directly.)*

---

## X. RUNTIME CONTEXT

```
OS:        Debian Trixie / KDE Plasma 6 / X11
Terminal:  Konsole (supports 24-bit colour — use full hex, no 256-colour fallbacks)
User:      lordfingers @ CastrumDigitos
Framework: Textual (primary) or Rich (scripts/logging)
Python:    3.11+
Paths:     Always Path.home() — never hardcode /home/lordfingers
Clipboard: xclip only (X11)
API:       CLAUDE_API_KEY env var
```

**Konsole trusts 24-bit colour.** Never degrade to `color1`–`color256` aliases.
Use full hex `#rrggbb` throughout — the terminal can handle it.

---

*Finis Tomi · Modus Arcanus Terminalis · ＭＭＸＸＶＩ*
