#╔═════════════════════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    ArcaCognitorium/ui/panes/left_menu.py
#║ ⛨
#╚═════════════════════════════════════════════════════════════════════════════════════════════



from __future__ import annotations

import random
import time
from typing import Dict, List, Optional, Tuple

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.events import Key
from textual.widgets import Static, Input, TextArea


# ── Rune pool — from rune-glyphs.txt ─────────────────────────────────────────
RUNE_POOL = list(
    "ᚡᚢᚣᚤᚥᚦᚧᚨᚩᚪᚫᚬᚭᚮᚹᚺᚻᚼᚽ"
    "ᚯᚰᚱᚲᚳᚴᚵᚶᚷᚸᚾᚿᛀᛁᛂᛃᛄᛅᛆᛇ"
    "ᛉᛊᛋᛌᛗᛘᛙᛚᛛᛍᛎᛏᛐᛑᛒᛓᛔᛕᛖ"
    "ᛝᛞᛟᛠᛡᛦᛧᛨᛩᛰᛱᛲᛳᛴᛵᛶᛷᛸᛮ"
    "ŦΩ⛣🞠🜘"
)

# Nav items — fullwidth label, internal key, app page destination
NAV_ITEMS: List[Tuple[str, str, str]] = [
    ("ＦＩＬＵＭ",                 "filum",            "conversations"),
    ("ＦＯＬＩＡ",                  "folia",             "folia"),
    ("ＴＨＥ ＣＯＵＮＣＩＬ",       "council",           "council"),
    ("ＧＲＩＭＯＩＲＥ",             "grimoire",          "grimoire"),
    ("ＡＲＸ ＡＲＣＡＮＡ",           "arx_arcana",        "arx_arcana"),
    ("ＲＥＦＥＲＥＮＴＩＡ",          "referentia",        "help_index"),
    ("ＮＥＸＵＳ ＡＲＣＨＩＶＵＭ",    "nexus_archivum",    "nexus_archivum"),
    ("ＥＧＯ ＭＡＮＩＦＥＳＴＵＳ",    "ego_manifestus",    "ego_manifestus"),
    ("ＡＲＸ ＣＯＮＦＩＧＵＲＡＴＩＯ",  "arx_configuratio",  "config"),
    ("ＶＩＧＩＬＡＲＵＭ ＯＭＮＩＡ",   "vigilarum_omnia",   "vigilarum_omnia"),
]


def _norm(key: str) -> str:
    return (key or "").strip().lower().replace(" ", "")


def _roman(n: int) -> str:
    glyphs = {12:"Ⅻ",11:"Ⅺ",10:"Ⅹ",9:"Ⅸ",8:"Ⅷ",7:"Ⅶ",6:"Ⅵ",5:"Ⅴ",4:"Ⅳ",3:"Ⅲ",2:"Ⅱ",1:"Ⅰ"}
    if n in glyphs:
        return glyphs[n]
    result = ""
    for val, sym in [(10,"Ⅹ"),(9,"ⅠⅩ"),(5,"Ⅴ"),(4,"ⅠⅤ"),(1,"Ⅰ")]:
        while n >= val:
            result += sym; n -= val
    return result or str(n)


# ── Rune Column ───────────────────────────────────────────────────────────────

class MenuCmdInput(Input):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._keys: Dict[str, str] = {}

    def set_keymap(self, *, focus_left: str, focus_middle: str, focus_right: str) -> None:
        self._keys = {
            "focus_left":   _norm(focus_left),
            "focus_middle": _norm(focus_middle),
            "focus_right":  _norm(focus_right),
        }

    async def on_key(self, event: Key) -> None:
        k = _norm(event.key)
        if k and k == self._keys.get("focus_left"):
            self.app.action_focus_left(); event.stop(); return
        if k and k == self._keys.get("focus_middle"):
            self.app.action_focus_middle(); event.stop(); return
        if k and k == self._keys.get("focus_right"):
            self.app.action_focus_right(); event.stop(); return


# ── Menu Page — navigable content area ───────────────────────────────────────

# Lines containing these strings are keyboard-navigable
NAV_SELECTABLE_MARKERS = ["🟅", "🟁", "╔", "⯇", "⯈"]
# Action items that have a moving selector glyph
ACTION_LABELS = [
    "𝐍 𝐎 𝐕 𝐔 𝐌", "𝐀 𝐃 𝐕 𝐎 𝐂 𝐀", "𝐀 𝐁 𝐎 𝐋 𝐔 𝐒",
    "𝐃 𝐈 𝐂 𝐓 𝐀", "𝐅 𝐈 𝐗 𝐀", "𝐎 𝐑 𝐃 𝐈 𝐍 𝐀",
    "𝐈𝐍 ＦＯＬＩＵＭ", "𝐄𝐗 ＦＯＬＩＵＭ",
]
# Commands that action items dispatch
ACTION_COMMANDS = {
    "𝐍 𝐎 𝐕 𝐔 𝐌":       "/new",
    "𝐀 𝐃 𝐕 𝐎 𝐂 𝐀":      "/load",
    "𝐀 𝐁 𝐎 𝐋 𝐔 𝐒":      "/delete",
    "𝐃 𝐈 𝐂 𝐓 𝐀":        "/rename",
    "𝐅 𝐈 𝐗 𝐀":          "/fixa",
    "𝐎 𝐑 𝐃 𝐈 𝐍 𝐀":      "/ordina",
    "𝐈𝐍 ＦＯＬＩＵＭ":    "/in_folium",
    "𝐄𝐗 ＦＯＬＩＵＭ":    "/ex_folium",
}

# Selector glyphs — left and right of the selected action item
SEL_LEFT  = "【"
SEL_RIGHT = "】"
# Inactive action items — no glyph (space placeholder same width)
INACT_LEFT  = "🟁"
INACT_RIGHT = "🟁"


class MenuPageText(TextArea):
    """
    Navigable read-only content area.

    Up/Down: move between selectable lines (blank lines skipped).
    Enter:   activate current line — nav items trigger navigation,
             action items pre-fill the command input.

    Action items display a moving 【 】selector on the currently highlighted
    item. They replaces the 🟁 flanking glyphs when that item is selected.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.read_only = True
        self.show_line_numbers = False
        self.wrap = True
        self._keys: Dict[str, str] = {}
        self._selectable: List[int] = []
        self._cursor_line: int = -1
        self._raw_content: str = ""   # Content without selector state baked in

    def set_keymap(self, *, focus_left: str, focus_middle: str, focus_right: str) -> None:
        self._keys = {
            "focus_left":   _norm(focus_left),
            "focus_middle": _norm(focus_middle),
            "focus_right":  _norm(focus_right),
        }

    def set_content(self, text: str) -> None:
        """Set page content and rebuild selectable line index."""
        self._raw_content = text or ""
        self._cursor_line = -1
        self._rebuild_selectable()
        self.text = self._render_with_selector()

    def _rebuild_selectable(self) -> None:
        lines = self._raw_content.split("\n")
        self._selectable = [
            i for i, line in enumerate(lines)
            if line.strip() and any(m in line for m in NAV_SELECTABLE_MARKERS)
        ]

    def _render_with_selector(self) -> str:
        """Return content with 🟆 on the currently selected action item."""
        if self._cursor_line < 0 or not self._raw_content:
            return self._raw_content
        lines = self._raw_content.split("\n")
        result = []
        for i, line in enumerate(lines):
            if i == self._cursor_line:
                # Replace 🟁 with 🟆 on the selected line
                result.append(line.replace(INACT_LEFT, SEL_LEFT, 1)
                                   .replace(INACT_RIGHT, SEL_RIGHT, 1))
            else:
                result.append(line)
        return "\n".join(result)

    def _move_cursor(self, direction: int) -> None:
        if not self._selectable:
            return
        if self._cursor_line not in self._selectable:
            self._cursor_line = self._selectable[0] if direction > 0 else self._selectable[-1]
        else:
            idx = self._selectable.index(self._cursor_line)
            idx = max(0, min(len(self._selectable) - 1, idx + direction))
            self._cursor_line = self._selectable[idx]
        self.text = self._render_with_selector()
        try:
            self.move_cursor((self._cursor_line, 0))
        except Exception:
            pass

    def _activate(self) -> None:
        if self._cursor_line < 0:
            return
        lines = self._raw_content.split("\n")
        if self._cursor_line >= len(lines):
            return
        line = lines[self._cursor_line]

        # Nav items
        for label, key, dest in NAV_ITEMS:
            if label in line:
                try:
                    self.app._go_left_page(dest)
                except Exception:
                    pass
                return

        # Action items — pre-fill command input
        for action_label, cmd in ACTION_COMMANDS.items():
            if action_label in line:
                try:
                    self.app.left.cmd.value = cmd + " "
                    self.app.left.cmd.focus()
                except Exception:
                    pass
                return

        # Navigation arrows
        if "⯇" in line:
            try: self.app._back_left_page()
            except Exception: pass
            return

    async def on_key(self, event: Key) -> None:
        k = _norm(event.key)
        if k == "up":
            self._move_cursor(-1); event.stop(); return
        if k == "down":
            self._move_cursor(1); event.stop(); return
        if k == "enter":
            self._activate(); event.stop(); return
        if k and k == self._keys.get("focus_left"):
            self.app.action_focus_left(); event.stop(); return
        if k and k == self._keys.get("focus_middle"):
            self.app.action_focus_middle(); event.stop(); return
        if k and k == self._keys.get("focus_right"):
            self.app.action_focus_right(); event.stop(); return

    def on_focus(self) -> None:
        self._rebuild_selectable()
        if self._selectable and self._cursor_line not in self._selectable:
            self._cursor_line = self._selectable[0]
            self.text = self._render_with_selector()
            try:
                self.move_cursor((self._cursor_line, 0))
            except Exception:
                pass


# ── Page Builders ─────────────────────────────────────────────────────────────

def _build_home_nav(council_lines=None) -> str:
    """
    Home navigation -- all items selectable with 🟅 prefix.
    Matches wireframe. THE COUNCIL is a nav item like the rest.
    The 【】selector highlight is applied by MenuPageText._render_with_selector
    when the cursor lands on a line.
    """
    return (
        "      🟅   ＦＩＬＵＭ\n"
        "\n"
        "      🟅   ＦＯＬＩＡ\n"
        "\n"
        "      🟅   ＴＨＥ ＣＯＵＮＣＩＬ\n"
        "\n"
        "      🟅   ＧＲＩＭＯＩＲＥ\n"
        "\n"
        "      🟅   ＡＲＸ ＡＲＣＡＮＡ\n"
        "\n"
        "      🟅   ＲＥＦＥＲＥＮＴＩＡ\n"
        "\n"
        "      🟅   ＮＥＸＵＳ ＡＲＣＨＩＶＵＭ\n"
        "\n"
        "      🟅   ＥＧＯ ＭＡＮＩＦＥＳＴＵＳ\n"
        "\n"
        "      🟅   ＡＲＸ ＣＯＮＦＩＧＵＲＡＴＩＯ\n"
        "\n"
        "      🟅   ＶＩＧＩＬＡＲＵＭ ＯＭＮＩＡ\n"
    )

def _thread_row(t: Dict, idx: int, active_id: Optional[str], sticky: bool = False) -> str:
    marker = "⏵" if t["id"] == active_id else " "
    end    = " ⏴" if t["id"] == active_id else "  "
    title  = t.get("title") or "(untitled)"
    title  = (title[:41] + "…") if len(title) > 41 else title
    pin    = "◈ " if sticky else "  "
    return f"   │  {marker} {_roman(idx)}  {pin}{title:<43}{end}│"


def _project_row(p: Dict, idx: int, active_id: Optional[str]) -> str:
    marker = "⏵" if p["id"] == active_id else " "
    end    = " ⏴" if p["id"] == active_id else "  "
    name   = p.get("name") or "(unnamed)"
    name   = (name[:44] + "…") if len(name) > 44 else name
    return f"   │  {marker} {_roman(idx)}  {name:<46}{end}│"


def _divider() -> List[str]:
    return [
        "",
        "   ▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂",
        "   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░",
        "   🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂🮂",
    ]


def _actions_filum() -> List[str]:
    # 🟁 flanks are inactive selectors; 【】replaces them when that line is focused
    return [
        "",
        "                🟁  𝐍 𝐎 𝐕 𝐔 𝐌  🟁",
        "",
        "               🟁  𝐀 𝐃 𝐕 𝐎 𝐂 𝐀  🟁",
        "",
        "               🟁  𝐀 𝐁 𝐎 𝐋 𝐔 𝐒  🟁",
        "",
        "                 🟁  𝐅 𝐈 𝐗 𝐀  🟁",
        "",
        "                🟁  𝐃 𝐈 𝐂 𝐓 𝐀  🟁",
        "",
        "               🟁  𝐎 𝐑 𝐃 𝐈 𝐍 𝐀  🟁",
        "",
        "             🟁  𝐈𝐍 ＦＯＬＩＵＭ  🟁",
    ]


def _actions_folia() -> List[str]:
    return [
        "",
        "                🟁  𝐍 𝐎 𝐕 𝐔 𝐌  🟁",
        "",
        "               🟁  𝐀 𝐃 𝐕 𝐎 𝐂 𝐀  🟁",
        "",
        "               🟁  𝐀 𝐁 𝐎 𝐋 𝐔 𝐒  🟁",
        "",
        "                🟁  𝐃 𝐈 𝐂 𝐓 𝐀  🟁",
    ]


def _actions_folium() -> List[str]:
    return [
        "",
        "                🟁  𝐍 𝐎 𝐕 𝐔 𝐌  🟁",
        "",
        "               🟁  𝐀 𝐃 𝐕 𝐎 𝐂 𝐀  🟁",
        "",
        "               🟁  𝐀 𝐁 𝐎 𝐋 𝐔 𝐒  🟁",
        "",
        "                🟁  𝐃 𝐈 𝐂 𝐓 𝐀  🟁",
        "",
        "                 🟁  𝐅 𝐈 𝐗 𝐀  🟁",
        "",
        "               🟁  𝐎 𝐑 𝐃 𝐈 𝐍 𝐀  🟁",
        "",
       "             🟁  𝐄𝐗 ＦＯＬＩＵＭ  🟁",
    ]


def _list_block(rows: List[str]) -> List[str]:
    lines = ["   ╭─────────────────────────────────────────────────╮"]
    if not rows:
        lines.append("   │   (empty)                                       │")
    else:
        lines.extend(rows)
    lines.append("   ╰─────────────────────────────────────────────────╯")
    return lines


def _build_filum_index(threads: List[Dict], active_id: Optional[str] = None) -> str:
    """
    FILUM page -- matches wireframe 01-filum------------menu-WF.txt.
    """
    # ── INDEX FILORUM header ──────────────────────────────────────────────
    header = [
        "            ▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂            ",
        " ▁▁▁▁▁▁▁▁▁▁▁█◤                            ◥█▁▁▁▁▁▁▁▁▁▁▁ ",
        "🞇░░░░░░░░░░█  ＩＮＤＥＸ ＦＩＬＯＲＵＭ  █░░░░░░░░░░▎",
        " ‾‾‾‾‾‾‾‾‾‾‾█◣                            ◢█‾‾‾‾‾‾‾‾‾‾‾ ",
        "            🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂🞂            ",
    ]

    # ── Thread list box ───────────────────────────────────────────────────
    box = ["   ╭─────────────────────────────────────────────────────╮"]
    if not threads:
        box.append("   │   (no threads)                                       │")
    else:
        stickied   = [t for t in threads if t.get("sticky")]
        unstickied = [t for t in threads if not t.get("sticky")]
        gi = 1
        for t in stickied:
            box.append(_thread_row(t, gi, active_id, sticky=True));  gi += 1
        if stickied and unstickied:
            box.append("   ├╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┤")
        for t in unstickied:
            box.append(_thread_row(t, gi, active_id, sticky=False)); gi += 1
    box.append("   ╰─────────────────────────────────────────────────────╯")

    # ── Action items (🟁 = inactive selector glyph) ────────────────────────
    actions = [
        "",
        "                🟁  🆁 🆎 🆗 🇮 🇲  🟁",
        "",
        "               🟁  🄀 🄃 🆗 🆎 🄂 🄀  🟁",
        "",
        "               🟁  🄀 🄁 🆎 🆚 🇮 🇸  🟁",
        "",
        "                🟁  🄃 🆗 🄂 🇴 🄀  🟁",
        "",
        "             🟁  🆗🇳 ＦＯＬＩＵＭ  🟁",
    ]

    # ── Nav buttons ───────────────────────────────────────────────────────
    nav = [
        "",
        "               ╏━━━╏ ╏━━━━━━━━━━━━╏ ╏━━━╏",
        "               ╏ ⧇ ╏ ╏ ＦＯＬＩＡ ╏ ╏ ⧈ ╏",
        "               ╏━━━╏ ╏━━━━━━━━━━━━╏ ╏━━━╏",
    ]

    return "\n".join(header + [""] + box + actions + nav)

def _build_folia_index(projects: List[Dict], active_id: Optional[str] = None) -> str:
    # Header: ＦＯＬＩＡ (not FOLIOS)
    lines = [" ▒▒▒▒▒【  ＦＯＬＩＡ   】▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", ""]
    rows = [_project_row(p, i+1, active_id) for i, p in enumerate(projects)]
    lines.extend(_list_block(rows))
    lines.extend(_divider())
    lines.extend(_actions_folia())
    lines.extend(_divider())
    lines += ["", "     ╔═══╗ ╔════════════╗ ╔═══╗",
                  "     ║ ⯇ ║ ║ ＦＩＬＵＭ ║ ║ ⯈ ║",
                  "     ╚═══╝ ╚════════════╝ ╚═══╝"]
    return "\n".join(lines)


def _build_folium_page(project: Dict, threads: List[Dict], active_id: Optional[str] = None) -> str:
    name  = project.get("name") or "(unnamed)"
    named = (name[:49] + "…") if len(name) > 49 else name
    lines = [" ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒【  ＦＯＬＩＵＭ   】▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒", ""]
    lines += ["    ╭─────────────────────────────────────────────────╮",
              f"   │ 󰯁 {named:<49}                                   │", 
               "   ├─────────────────────────────────────────────────┤"]
    stickied   = [t for t in threads if t.get("sticky")]
    unstickied = [t for t in threads if not t.get("sticky")]
    gi = 1
    for t in stickied:
        lines.append(_thread_row(t, gi, active_id, sticky=True)); gi += 1
    if stickied and unstickied:
        lines.append("   ├╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┤")
    for t in unstickied:
        lines.append(_thread_row(t, gi, active_id, sticky=False)); gi += 1
    if not threads:
        lines.append("   │   (no threads in this folio)                   │")
    lines.append("   ╰─────────────────────────────────────────────────╯")
    lines.extend(_divider())
    lines.extend(_actions_folium())
    lines.extend(_divider())
    lines += ["", "               ╔═══╗           ╔═══╗",
                  "               ║ ⯇ ║           ║ ⯈ ║",
                  "               ╚═══╝           ╚═══╝"]
    return "\n".join(lines)


# ── Logo Header Pane ──────────────────────────────────────────────────────────

class LogoHeader(Static):
    """
    Arca Cognitorium logo pane.
    overflow: hidden — never wraps, never breaks layout.
    Gold colour. Bottom border separates from content area.
    """

    LOGO = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░┃\n"
        "┃                                                               ┃\n"
        "┃ ╭───────────────────────────────────────────────────────────╮ ┃\n"
        "┃ │┏━━━┓               ┏━━━┑             ┒                    │ ┃\n"
        "┃ │┃   ┃               ┃                ✦┃          ✦         │ ┃\n"
        "┃ │┣━━━┫┏━━┑┏━━┑┍━━┓   ┃    ┏━━┓┏━━┓┏━━┓┒┣━┙┏━━┓┏━━┑┒┒  ┒┏━┳━┓│ ┃\n"
        "┃ │┃   ┃┃   ┃   ┏━━┫   ┃    ┃  ┃┃  ┃┃  ┃┃┃  ┃  ┃┃   ┃┃  ┃┃ ┃ ┃│ ┃\n"
        "┃ │┚   ┖┚   ┗━━┙┗━━┛   ┗━━━┙┗━━┛┗━━┫┚  ┖┖┗━┙┗━━┛┚   ┖┗━━┛┚ ┖ ┖│ ┃\n"
        "┃ ╰─────────────────────────────┃──┃──────────────────────────╯ ┃\n"
        "┃                               ┗━━┛                            ┃\n"
        "┃░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░┃\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
    )

    DEFAULT_CSS = """
    LogoHeader {
        height: auto;
        width: 1fr;
        color: #C9A84C;
        border-bottom: solid #C9A84C;
        padding: 0;
        overflow: hidden hidden;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(self.LOGO, markup=False, **kwargs)

class LeftMenuPane(Vertical):
    """
    Left navigation pane.

    Layout (top to bottom):
      LogoHeader    — separate non-breaking logo widget
      legend        — debug strip (hidden by default)
      date_bar      — MMXVII strip
      content_row   — [RuneColumn | MenuPageText | RuneColumn]
      menu_cmd      — command input

    Rune columns: gold colour, gold borders.
    """

    DEFAULT_CSS = """
    LeftMenuPane { layout: vertical; }
    #legend {
        height: auto;
        padding: 0 1;
        color: #5A6070;
        border-bottom: solid #2A2535;
    }
    #date_bar {
        height: 1;
        color: #5A6070;
        padding: 0 1;
        border-bottom: solid #2A2535;
    }
    #content_row {
        layout: horizontal;
        height: 1fr;
        border-top: solid #C9A84C;
        border-bottom: solid #C9A84C;
    }
    #left_rune {
        width: 3;
        color: #C9A84C;
        padding: 0;
        border-right: solid #C9A84C;
    }
    #right_rune {
        width: 3;
        color: #C9A84C;
        padding: 0;
        border-left: solid #C9A84C;
    }
    #menu_page {
        width: 1fr; height: 1fr;
        padding: 0 1;
        color: #D4C8A8;
        background: #0D0B0E;
    }
    #menu_cmd {
        height: 3;
        border: solid #C9A84C;
        background: #161218;
        color: #D4C8A8;
        padding: 0 1;
    }
    #menu_cmd:focus { border: solid #C68B2A; }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._council_lines: List[str] = []
        self._debug_visible: bool = False
        self._current_page: str = "home"

    def compose(self) -> ComposeResult:
        yield LogoHeader()
        self.legend = Static("", id="legend", markup=False)
        yield self.legend
        yield Static(
            "  ▴    ▴     ▴    ⯨  𝐌 𝐌 𝐗 𝐕 𝐈 𝐈 ⯩    ▴    ▴    ▴",
            id="date_bar",
            markup=False,
        )
        with Horizontal(id="content_row"):
            self.page = MenuPageText(id="menu_page")
            yield self.page
        self.cmd = MenuCmdInput(placeholder="⨊ :", id="menu_cmd")
        yield self.cmd

    def on_mount(self) -> None:
        self.page.set_content(_build_home_nav(self._council_lines))
        self.legend.display = False

    # ── Page setters ──────────────────────────────────────────────────

    def set_home(self, council_lines: Optional[List[str]] = None) -> None:
        if council_lines is not None:
            self._council_lines = council_lines
        self._current_page = "home"
        self.page.set_content(_build_home_nav(self._council_lines))

    def set_filum_page(self, threads: List[Dict], active_id: Optional[str] = None) -> None:
        self._current_page = "filum"
        self.page.set_content(_build_filum_index(threads, active_id))

    def set_folia_page(self, projects: List[Dict], active_id: Optional[str] = None) -> None:
        self._current_page = "folia"
        self.page.set_content(_build_folia_index(projects, active_id))

    def set_folium_page(self, project: Dict, threads: List[Dict], active_id: Optional[str] = None) -> None:
        self._current_page = "folium"
        self.page.set_content(_build_folium_page(project, threads, active_id))

    def set_page(self, text: str) -> None:
        """Fallback — arbitrary text. Legacy app.py routing."""
        self.page.set_content(text or "")

    def set_council(self, council_lines) -> None:
        """
        Store emerged entity names for the Council page.
        THE COUNCIL is a destination -- not injected into home nav.
        """
        self._council_lines = council_lines or []

    def set_legend(self, text: str) -> None:
        """Update debug legend content. Only visible when debug mode is on."""
        self.legend.update(text or "")

    def toggle_debug(self) -> bool:
        """
        Toggle debug legend visibility.
        Returns True if now visible, False if now hidden.
        """
        self._debug_visible = not self._debug_visible
        self.legend.display = self._debug_visible
        return self._debug_visible

    def focus_input(self) -> None:
        self.cmd.focus()

