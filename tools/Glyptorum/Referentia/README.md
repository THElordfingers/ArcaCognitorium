# GLYPTORUM
### Glyph Arrangement Studio — User Guide  `v5`

---

```
 ██████╗ ██╗  ██╗   ██╗██████╗ ████████╗ ██████╗ ██████╗ ██╗   ██╗███╗   ███╗
██╔════╝ ██║  ╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗██║   ██║████╗ ████║
██║  ███╗██║   ╚████╔╝ ██████╔╝   ██║   ██║   ██║██████╔╝██║   ██║██╔████╔██║
██║   ██║██║    ╚██╔╝  ██╔═══╝    ██║   ██║   ██║██╔══██╗██║   ██║██║╚██╔╝██║
╚██████╔╝███████╗██║   ██║        ██║   ╚██████╔╝██║  ██║╚██████╔╝██║ ╚═╝ ██║
 ╚═════╝ ╚══════╝╚═╝   ╚═╝        ╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝
```

---

## Overview

Glyptorum is a desktop tool for composing glyph-based typographic art. You build **glyph sets** — curated collections of Unicode characters — browse them in tabbed **panes**, assemble **line widgets** to construct rows of glyphs, and print them onto a freeform **canvas**. Finished compositions save as plain text. Reusable arrangements save as **shapes** and recall instantly from the shape library.

Everything persists between sessions automatically, including your exact window layout.

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10 or newer |
| PyQt6 | 6.4 or newer |

```bash
pip install PyQt6
python glyptorum.py
```

---

## File & Directory Structure

Created automatically on first launch:

```
~/Glyptorum/
    Storage/
        Glyph-Sets/     ← sets saved as .json
        Canvas/         ← canvas output saved as .txt
        Shapes/         ← shape library entries saved as .gshape
    Session/
        session.json    ← window geometry, dock layout, font settings
```

---

## Interface — Dockable Panels

Glyptorum is built entirely around `QDockWidget`. Every panel is an independent floating window that can be placed anywhere you want.

### Default layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  [Font toolbar — movable, floatable]                                     │
├────────────────────────┬─────────────────────────┬───────────────────────┤
│  GLYPH SETS & PANES    │                         │   SHAPE LIBRARY       │
│  (left dock)           │      CANVAS             │   (right dock)        │
│                        │   (central widget)      │                       │
│                        │                         │                       │
├────────────────────────┴─────────────────────────┴───────────────────────┤
│  LINE EDITOR  (bottom dock)                                               │
└──────────────────────────────────────────────────────────────────────────┘
```

The **Canvas** is the central widget — it stays fixed as the anchor. Everything else docks around it or floats freely.

### Moving panels

Grab any panel's **title bar** and drag it to:
- any edge of the main window to dock it there
- another dock's title bar to **tab them together**
- open space to **float it** as a standalone window

### Resizing

Drag the edges of any docked or floating panel. Docked panels share splitter handles with their neighbours.

### Hiding and showing

Use the **View** menu to toggle any panel or toolbar on and off. Keyboard shortcut panels can also be closed with their title bar × button and reopened from View.

### Reset Layout

**View → Reset Layout** snaps all panels back to the default arrangement. Useful if a panel goes off-screen.

### Session persistence

On close, Glyptorum saves your complete dock layout using Qt's `saveState()` / `restoreState()`. Next launch restores every panel to exactly where you left it — docked, floating, tabbed, or hidden.

---

## Font Toolbar

A movable toolbar, docked at the top by default. Drag its handle to move it, or float it as its own window.

| Control | Effect |
|---|---|
| **Font** dropdown | All system font families, filtered by the mode selector. Applies to the canvas, glyph cells, and line widget slots. |
| **Filter** dropdown | *Monospace only* (default) — only fixed-pitch fonts. *All fonts* — everything. *Exclude Noto* — all fonts except the Noto family. |
| **Size** spinbox | Art font point size, 6–72pt. |
| **Spacing %** slider | Canvas line height as a percentage of the font's natural spacing, 60–200%. Drag left to tighten rows, right to open them up. |

All font settings persist in session. Ctrl+scroll on the canvas also adjusts font size live and syncs back to the Size spinbox.

---

## GLYPH SETS & PANES  (left dock)

### Ⅰ — Glyph Set List

Shows every set loaded or created this session. Sets in `~/Glyptorum/Storage/Glyph-Sets/` are loaded automatically on startup.

**Right-click** any entry to edit or delete it directly from the list.

### Ⅱ — Manage Sets

| Button | Action |
|---|---|
| **Load** | Open a `.json` or `.txt` file as a glyph set. Auto-saved to `Glyph-Sets/`. |
| **Create** | Dialog: name the set and paste glyphs in. Duplicates stripped. Auto-saved to `Glyph-Sets/`. |
| **Edit** | Edit the set currently **highlighted in the list** — rename it, add or remove glyphs. |
| **Save** | Save the active tab's set to `Glyph-Sets/` (or choose a path). |
| **Delete** | Delete the set currently **highlighted in the list**. If the set is open in any pane tab, a warning lists which tabs before asking to confirm. Confirming closes those tabs and removes the file from disk. |

**Supported load formats:**
- **JSON** — `{ "name": "…", "glyphs": ["☽","☾","⛤"] }` — native format
- **Plain text** — every unique non-whitespace character becomes one glyph, in order

### Ⅲ — Glyph Panes

Each pane is a tab widget displaying one glyph set at a time. Glyphs are shown in a **10-column grid** using the current art font. Multiple panes stack vertically.

**Navigating tabs** — use the **◀ / ▶ arrows** above each pane, or click a tab directly. The label between the arrows shows `TabName  [2/5]`.

**Using a glyph** — click a glyph cell to send it immediately to the active slot in the active line widget. No separate confirmation needed.

**Rearranging glyphs** — drag any glyph cell onto another to reorder within the set. The grid updates live.

**Removing a glyph** — right-click a glyph cell → **Remove**.

**Tab context menu** (right-click the tab bar):

| Option | Effect |
|---|---|
| Rename tab… | Rename the tab label (also updates the set name). |
| Edit glyph set… | Full in-place editor for this tab's set. |
| Remove this tab | Close this tab from the pane. |

### Ⅳ — Pane Controls

The **Pane** dropdown selects which pane is the target for the four buttons below it.

| Button | Action |
|---|---|
| **+ Tab** | Add a tab to the selected pane. Choose which glyph set from a picker. |
| **− Tab** | Remove the **currently active (visible) tab** from the selected pane. No picker needed — whatever tab is showing goes. |
| **+ Pane** | Add a new empty pane below the existing ones. |
| **− Pane** | Remove the pane **selected in the Pane dropdown**. The last pane cannot be removed. |

---

## LINE EDITOR  (bottom dock)

Each **line widget** is one row of output. Build as many as needed.

```
[Print Line]  [·SPC][·SPC][☽][⛤][☾][·SPC]  [+][−]
                1     1    1   3   1   2
```

### Line widget anatomy

| Element | Description |
|---|---|
| **Print Line** | Renders this line to the canvas at the current cursor row. The cursor advances one row automatically after printing. |
| **Glyph slots** | Each slot holds one glyph (or a space) and a repeat count shown in the spinbox below. |
| **·SPC** | An empty slot. Renders as one or more space characters. |
| **+ / −** | Add or remove slots from this line. |

### Working with slots

- **Click a slot** to select it (purple highlight).
- With a slot selected, **click any glyph** in the panes — it fills the slot and the selection automatically advances to the next slot to the right.
- **← →** arrow keys move the selection between slots within the active line.
- **↑ ↓** arrow keys move between lines.
- **Space**, **Backspace**, or **Delete** clears the selected slot back to `·SPC`.

### Active line

Click anywhere on a line widget to make it **active** (gold border). Glyph clicks always target the active slot of the active line.

### Line editor toolbar

| Button | Shortcut | Action |
|---|---|---|
| **+ Line** | — | Add a new line widget. |
| **− Line** | — | Remove the last line widget. |
| **Save Shape** | `Ctrl+Shift+S` | Capture the current line editor state as a named shape. |
| **▶ Print All** | `Ctrl+Enter` | Render every line widget to the canvas in order from the current cursor row. |

---

## CANVAS  (central widget)

A plain-text editor where printed output appears.

### Printing

- **Click any row** to position the cursor — this is where the next print lands.
- **Print Line** (on any line widget) writes that line to the cursor row and advances one row.
- **▶ Print All** writes all line widgets sequentially from the cursor row down, then moves the cursor below the last printed line.
- The canvas is **directly editable** — type, delete, cut, paste, rearrange freely at any time.

### Font size

- **Ctrl+scroll** on the canvas adjusts the art font size live. The Font toolbar's Size spinbox updates to match.

### Line spacing

- The **Spacing %** slider in the Font toolbar controls line height. Values below 100% tighten rows; above 100% opens them up. Useful for making box-drawing characters join correctly, or for pixel-art style dense grids.

### Canvas toolbar

| Button | Shortcut | Action |
|---|---|---|
| **New Canvas** | — | Clear the canvas. Line widgets are kept. Prompts for confirmation. |
| **Save Canvas** | `Ctrl+S` | Save the canvas text to `~/Glyptorum/Storage/Canvas/` (or choose any path). |

---

## SHAPE LIBRARY  (right dock)

A **shape** is a complete snapshot of the line editor — all line widgets, all slots, all glyphs and counts. Shapes save to `~/Glyptorum/Storage/Shapes/` as `.gshape` files and reload on startup automatically.

### Using shapes

- **Double-click** a shape to load it into the line editor immediately.
- **Single-click** to select it, then use the buttons below.

### Shape library buttons

| Button | Action |
|---|---|
| **↓ Load into Editor** | Replace the current line editor contents with the selected shape. |
| **Rename** | Rename the selected shape (renames the file on disk too). |
| **Delete** | Delete the shape **currently highlighted in the list** from the library and disk. |
| **Export…** | Save a copy of the selected shape as a `.gshape` file anywhere on disk. |
| **Import…** | Load a `.gshape` file from disk and add it to the library. |

Right-click any shape for the full context menu.

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+L` | Load a glyph set from file |
| `Ctrl+N` | Open Create Glyph Set dialog |
| `Ctrl+S` | Save the canvas to a file |
| `Ctrl+Enter` | Print all line widgets to canvas |
| `Ctrl+Shift+S` | Save current line editor state as a shape |
| `←` / `→` | Move slot selection left / right within active line |
| `↑` / `↓` | Move active line up / down |
| `Space` / `Backspace` / `Delete` | Clear the selected slot |
| `Ctrl+Scroll` | Adjust canvas font size |

---

## File Formats

### Glyph Set  `.json`

```json
{
  "name": "Arcane Sigils",
  "glyphs": ["☽", "☾", "⛤", "♆", "⚸", "☿", "♀", "♁", "♂"]
}
```

UTF-8 JSON. Can be created by hand or exported from within the app. Loading a plain `.txt` file is also supported.

### Shape  `.gshape`

```json
{
  "name": "Top Border",
  "lines": [
    { "slots": [
        { "glyph": "┌", "count": 1 },
        { "glyph": "─", "count": 20 },
        { "glyph": "┐", "count": 1 }
    ]}
  ]
}
```

UTF-8 JSON. Portable — share them freely, version-control them, edit by hand.

### Session  `session.json`

Stores Qt `saveGeometry()` and `saveState()` blobs (base64), plus font family, size, spacing, and filter mode. Written on every close, read on every launch.

---

## Tips

**Box-drawing alignment** — gaps between box characters are a font issue, not a Glyptorum issue. Fonts that render box glyphs at full cell width with no gap include **Iosevka**, **Cascadia Mono**, **PxPlus IBM VGA**, and most bitmap-derived monospace fonts. Set Spacing % to exactly 100 and use one of these fonts for seamless joins.

**Building a border frame** — load a Box Drawing set, add three line widgets (top, fill, bottom), set corners and fill glyphs, adjust repeat counts for width, hit Print All, then Save Shape as "Box Frame" for instant reuse.

**Working with many sets at once** — use multiple panes, each with different tabs. All panes route glyph clicks to the same active slot. Float the Glyph Sets & Panes dock to a second monitor if you have one.

**Dense pixel-art rows** — drag Spacing % down to 70–80% to close the gap between canvas rows and make the output feel like a grid.

**Sharing work** — Export shapes as `.gshape` for collaborators. Save canvas as `.txt` for any plain-text consumer. Both formats are fully portable and human-readable.

---

## License

Glyptorum is provided as a single Python script. Do with it as you will.
