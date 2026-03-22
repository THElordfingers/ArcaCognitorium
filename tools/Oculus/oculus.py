"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈   ██████   ██████ ██    ██ ██      ██    ██ ███████  ▍
🮈  ██    ██ ██      ██    ██ ██      ██    ██ ██       ▍
🮈  ██    ██ ██      ██    ██ ██      ██    ██ ███████  ▍
🮈  ██    ██ ██      ██    ██ ██      ██    ██      ██  ▍
🮈   ██████   ██████  ██████  ███████  ██████  ███████  ▍
🮈                                                      ▍
🮈                                                      ▍
🮈                    Python Script                     ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
"""

#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════════════════
# ║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
# ║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
# ║ ⛨⛨⛨⛨⛨⛨⛨⛨
# ║ ⛨⛨⛨⛨⛨
# ║ ⛨⛨⛨
# ║ ⛨⛨
# ║ ⛨
# ║ ⛨    ArcaCognitorium / tools / oculus.py
# ║ ⛨    The Oculus — System Debug Monitor          v1.0
# ║ ⛨
# ║ ⛨    Standalone Textual app. Run from the ArcaCognitorium project root:
# ║ ⛨        python tools/oculus.py
# ║ ⛨
# ║ ⛨    Reads live system state: logs, memory files, council persistence,
# ║ ⛨    reflection records, and entity signal data — without touching
# ║ ⛨    the running application. Safe to run concurrently.
# ║ ⛨
# ╚══════════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple

# ── Textual ─────────────────────────────────────────────────────────────────────
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Footer, Header, Label, Static, RichLog


# ════════════════════════════════════════════════════════════════════════════════
#  PATHS  (relative to project root)
# ════════════════════════════════════════════════════════════════════════════════

ROOT = Path(".")

PATHS = {
    "assessor_diag":    ROOT / "storage/logs/assessor_diag.log",
    "archivist_diag":   ROOT / "storage/logs/archivist_diag.log",
    "emergence_diag":   ROOT / "storage/logs/emergence_diag.log",
    "interruption_diag":ROOT / "storage/logs/interruption_diag.log",
    "entity_memory":    ROOT / "storage/logs/entity_memory_diag.log",
    "immutable":        ROOT / "storage/logs/immutable.jsonl",
    "reflections":      ROOT / "storage/logs/reflections.jsonl",
    "council_emerged":  ROOT / "storage/council/emerged.json",
    "vectors":          ROOT / "storage/vectors/vectors.pkl",
    "conversations_dir":ROOT / "storage/conversations",
    "grimoire":         ROOT / "storage/grimoire.json",
}

ENTITY_COLORS: Dict[str, str] = {
    "luminarious":    "#C9A84C",
    "archivist":      "#6A8FAF",
    "contrarian":     "#A05C5C",
    "minimalist":     "#7A9E7E",
    "speculator":     "#8B6BAE",
    "pessimist":      "#8A7060",
    "toolsmith":      "#5E8A8A",
    "systems_thinker":"#7E7E9E",
    "socratic":       "#AF8C5A",
    "assessor":       "#5A7A6A",
}

ENTITY_SIGILS: Dict[str, str] = {
    "luminarious":    "⬡",
    "archivist":      "◈",
    "contrarian":     "◇",
    "minimalist":     "◻",
    "speculator":     "◎",
    "pessimist":      "▲",
    "toolsmith":      "⬟",
    "systems_thinker":"⬠",
    "socratic":       "◉",
    "assessor":       "⛨",
}

INTERRUPTION_PRESENCE: Dict[str, float] = {
    "archivist":       0.70,
    "contrarian":      0.65,
    "speculator":      0.45,
    "pessimist":       0.55,
    "toolsmith":       0.40,
    "systems_thinker": 0.50,
    "socratic":        0.35,
    "minimalist":      0.50,
}

EMERGENCE_THRESHOLD = 1.0
MAX_SIGNAL = 3.0


# ════════════════════════════════════════════════════════════════════════════════
#  READERS  —  pure filesystem, no app imports
# ════════════════════════════════════════════════════════════════════════════════

def _read_jsonl(path: Path, max_lines: int = 200) -> List[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    out = []
    for line in lines[-max_lines:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append({"_raw": line})
    return out


def _read_plain_log(path: Path, max_lines: int = 200) -> List[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-max_lines:]


def _read_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def _file_size_kb(path: Path) -> str:
    if not path.exists():
        return "—"
    return f"{path.stat().st_size / 1024:.1f} KB"


def _file_mtime(path: Path) -> str:
    if not path.exists():
        return "—"
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S")


def _count_conversations() -> int:
    d = PATHS["conversations_dir"]
    if not d.exists():
        return 0
    return sum(1 for f in d.iterdir() if f.suffix == ".json")


def _grimoire_entry_count() -> int:
    data = _read_json(PATHS["grimoire"])
    if not data:
        return 0
    entries = data.get("entries", [])
    return len(entries) if isinstance(entries, list) else 0


def _parse_emergence_signals() -> Dict[str, float]:
    """Re-derive signal strengths from reflection log — mirrors EmergenceEngine logic."""
    ENTITY_DOMAINS: Dict[str, List[str]] = {
        "archivist":      ["retrieve","history","past","remember","archive","search","chronicle"],
        "contrarian":     ["assume","wrong","challenge","disagree","but","however","alternative"],
        "minimalist":     ["simple","brief","short","essential","distill","core","just","only"],
        "speculator":     ["imagine","what if","possible","explore","future","potential","could"],
        "pessimist":      ["risk","problem","fail","wrong","danger","concern","downside","issue"],
        "toolsmith":      ["abstract","pattern","reuse","tool","build","function","class","system"],
        "systems_thinker":["system","constraint","dependency","flow","architecture","whole","map"],
        "socratic":       ["why","question","purpose","understand","meaning","what is","how does"],
    }
    SIGNAL_DECAY = 0.02

    signals = {eid: 0.0 for eid in ENTITY_DOMAINS}
    records = _read_jsonl(PATHS["reflections"])

    for record in records:
        topics = {t.lower() for t in record.get("dominant_topics", [])}
        code_present = record.get("code_present", False)
        question_count = record.get("question_count", 0)

        for entity_id, strength in signals.items():
            domain = set(ENTITY_DOMAINS[entity_id])
            matches = len(topics & domain)
            if matches > 0:
                signals[entity_id] = min(MAX_SIGNAL, strength + 0.15 * matches)
            else:
                signals[entity_id] = max(0.0, strength - SIGNAL_DECAY)

            if entity_id in ("toolsmith", "systems_thinker") and code_present:
                signals[entity_id] = min(MAX_SIGNAL, signals[entity_id] + 0.05)
            if entity_id == "socratic" and question_count >= 3:
                signals[entity_id] = min(MAX_SIGNAL, signals[entity_id] + 0.08)

    return signals


def _get_emerged_entities() -> List[str]:
    data = _read_json(PATHS["council_emerged"])
    if not data:
        return []
    return data.get("emerged", [])


def _last_reflection_ts() -> str:
    records = _read_jsonl(PATHS["reflections"])
    for rec in reversed(records):
        if rec.get("type") == "self_analytics":
            ts = rec.get("ts", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    return dt.strftime("%H:%M:%S")
                except Exception:
                    return ts[:19]
    return "—"


def _count_chronicle_vectors() -> int:
    vpath = PATHS["vectors"]
    if not vpath.exists():
        return 0
    # Approximate: file size heuristic (each vector ~1.5 KB avg)
    kb = vpath.stat().st_size / 1024
    return int(kb / 1.5)


def _last_assessor_entry() -> str:
    lines = _read_plain_log(PATHS["assessor_diag"])
    for line in reversed(lines):
        if line.strip():
            return line.strip()[-80:]
    return "—"


def _last_archivist_entry() -> str:
    lines = _read_plain_log(PATHS["archivist_diag"])
    for line in reversed(lines):
        if line.strip():
            return line.strip()[-80:]
    return "—"


# ════════════════════════════════════════════════════════════════════════════════
#  SIGNAL BAR
# ════════════════════════════════════════════════════════════════════════════════

def _signal_bar(value: float, max_val: float = MAX_SIGNAL, width: int = 12) -> str:
    ratio = min(1.0, value / max_val) if max_val > 0 else 0.0
    filled = int(ratio * width)
    empty = width - filled

    if ratio >= EMERGENCE_THRESHOLD / max_val:
        bar_char = "█"
        color = "bright_green"
    elif ratio >= 0.4:
        bar_char = "▓"
        color = "yellow"
    elif ratio >= 0.15:
        bar_char = "▒"
        color = "dim yellow"
    else:
        bar_char = "░"
        color = "bright_black"

    bar = f"[{color}]{bar_char * filled}[/][bright_black]{'░' * empty}[/]"
    return bar


# ════════════════════════════════════════════════════════════════════════════════
#  PANELS
# ════════════════════════════════════════════════════════════════════════════════

class SectionHeader(Static):
    DEFAULT_CSS = """
    SectionHeader {
        color: #5A5068;
        background: #110F14;
        border-bottom: solid #2A2535;
        padding: 0 1;
        height: 1;
        text-style: bold;
    }
    """
    def __init__(self, title: str, sigil: str = "⛨"):
        super().__init__(f" {sigil} {title.upper()} ", markup=False)


class CouncilPanel(Static):
    """Entity Council — emerged status + signal strengths + presence weights."""

    DEFAULT_CSS = """
    CouncilPanel {
        height: auto;
        padding: 0 1;
    }
    """

    def render_council(self) -> str:
        emerged = set(_get_emerged_entities())
        signals = _parse_emergence_signals()

        all_entities = [
            "luminarious", "archivist", "contrarian", "minimalist",
            "speculator", "pessimist", "toolsmith", "systems_thinker", "socratic",
        ]

        lines = []
        for eid in all_entities:
            color = ENTITY_COLORS.get(eid, "#888888")
            sigil = ENTITY_SIGILS.get(eid, "·")
            is_emerged = eid in emerged or eid == "luminarious"
            emerged_marker = "[bright_green]●[/]" if is_emerged else "[bright_black]○[/]"

            signal = signals.get(eid, 0.0)
            bar = _signal_bar(signal)
            pres = INTERRUPTION_PRESENCE.get(eid, 0.0)
            pres_str = f"{pres:.2f}" if pres > 0 else "  — "

            name = eid.replace("_", " ").upper()
            line = (
                f" {emerged_marker} [{color}]{sigil}[/] "
                f"[{color}]{name:<16}[/] "
                f"{bar} {signal:4.2f}/{MAX_SIGNAL:.1f}  "
                f"[dim]pres:[/][white]{pres_str}[/]"
            )
            lines.append(line)

        return "\n".join(lines)

    def on_mount(self) -> None:
        self.update(self.render_council())

    def refresh_data(self) -> None:
        self.update(self.render_council())


class SystemStatusPanel(Static):
    """Storage sizes, file mtimes, counts, config-derived intervals."""

    DEFAULT_CSS = """
    SystemStatusPanel {
        height: auto;
        padding: 0 1;
    }
    """

    def render_status(self) -> str:
        rows = []

        def row(label: str, value: str, color: str = "white") -> str:
            return f"  [dim]{label:<26}[/][{color}]{value}[/]"

        # ── Memory ───────────────────────────────────────────────
        grimoire_count = _grimoire_entry_count()
        vectors_est = _count_chronicle_vectors()
        conv_count = _count_conversations()

        rows.append(row("Grimoire entries",      str(grimoire_count),    "bright_yellow"))
        rows.append(row("Chronicle vectors (est)",str(vectors_est),      "bright_yellow"))
        rows.append(row("Conversations stored",  str(conv_count),        "white"))

        # ── Files ────────────────────────────────────────────────
        rows.append("")
        rows.append("  [dim]── Log Files ──────────────────────────────[/]")
        for key, path in PATHS.items():
            if not path.is_file():
                continue
            rows.append(
                f"  [dim]{path.name:<26}[/]"
                f"[white]{_file_size_kb(path):>8}[/]  "
                f"[bright_black]mod {_file_mtime(path)}[/]"
            )

        # ── Background systems ───────────────────────────────────
        rows.append("")
        rows.append("  [dim]── Background Systems ──────────────────────[/]")
        last_ref = _last_reflection_ts()
        rows.append(row("Last reflection",        last_ref,              "bright_cyan"))
        rows.append(row("Last assessor entry",    _last_assessor_entry()[:40], "dim"))
        rows.append(row("Last archivist entry",   _last_archivist_entry()[:40], "dim"))

        return "\n".join(rows)

    def on_mount(self) -> None:
        self.update(self.render_status())

    def refresh_data(self) -> None:
        self.update(self.render_status())


class ReflectionPanel(Static):
    """Last N reflection records from reflections.jsonl."""

    DEFAULT_CSS = """
    ReflectionPanel {
        height: auto;
        padding: 0 1;
    }
    """

    MAX_SHOW = 4

    def render_reflections(self) -> str:
        records = _read_jsonl(PATHS["reflections"])
        analytics = [r for r in records if r.get("type") == "self_analytics"]
        signals   = [r for r in records if "dominant_topics" in r]

        lines = []

        if signals:
            latest_sig = signals[-1]
            topics = latest_sig.get("dominant_topics", [])
            turn_count = latest_sig.get("turn_count", "?")
            msg_len = latest_sig.get("message_length_avg", 0)
            code = "[bright_green]yes[/]" if latest_sig.get("code_present") else "[bright_black]no[/]"
            q_count = latest_sig.get("question_count", 0)

            lines.append(f"  [dim]Latest routing signal  (turn {turn_count})[/]")
            lines.append(f"  [dim]topics:[/]   [bright_cyan]{', '.join(topics) or '—'}[/]")
            lines.append(f"  [dim]avg len:[/]  [white]{msg_len:.1f}[/]  "
                         f"[dim]code:[/] {code}  "
                         f"[dim]questions:[/] [white]{q_count}[/]")
            lines.append("")

        if analytics:
            lines.append(f"  [dim]── Last {self.MAX_SHOW} Reflection Suggestions ──────────────[/]")
            for rec in analytics[-self.MAX_SHOW:]:
                ts = rec.get("ts", "")[:19]
                suggestions = rec.get("suggestions", "")
                # Show first 2 lines of suggestions
                slines = [s.strip() for s in suggestions.splitlines() if s.strip()][:2]
                lines.append(f"  [bright_black]{ts}[/]")
                for s in slines:
                    lines.append(f"  [dim]  {s[:72]}[/]")
                lines.append("")
        else:
            lines.append("  [bright_black]No analytics records yet.[/]")

        return "\n".join(lines)

    def on_mount(self) -> None:
        self.update(self.render_reflections())

    def refresh_data(self) -> None:
        self.update(self.render_reflections())


class ImmutableLogPanel(RichLog):
    """Live tail of immutable.jsonl — last N message events."""

    DEFAULT_CSS = """
    ImmutableLogPanel {
        height: 1fr;
        border: solid #2A2535;
        background: #0D0B0E;
        padding: 0 1;
    }
    """

    _last_line_count: int = 0

    def on_mount(self) -> None:
        self.border_title = "IMMUTABLE LOG"
        self._render_all()

    def _render_all(self) -> None:
        self.clear()
        records = _read_jsonl(PATHS["immutable"], max_lines=80)
        self._last_line_count = len(records)
        for rec in records:
            self._write_record(rec)

    def _write_record(self, rec: dict) -> None:
        if "_raw" in rec:
            self.write(f"[bright_black]{rec['_raw'][:100]}[/]")
            return

        ts = (rec.get("ts") or "")[:19]
        role = rec.get("role", "?")
        model = (rec.get("model") or "")
        model_short = model.split("-")[1] if "-" in model else model
        conv = (rec.get("conversation_id") or "")[:8]
        content = (rec.get("content") or "")[:60].replace("\n", " ")
        usage = rec.get("usage") or {}
        tokens = usage.get("output_tokens") or usage.get("input_tokens") or ""

        role_color = "bright_cyan" if role == "user" else "bright_yellow"
        token_str = f"[dim] {tokens}t[/]" if tokens else ""

        self.write(
            f"[bright_black]{ts}[/] "
            f"[{role_color}]{role:<9}[/]"
            f"[dim]{conv}[/] "
            f"[bright_black]{model_short:<10}[/]"
            f"[white]{content}[/]"
            f"{token_str}"
        )

    def refresh_data(self) -> None:
        records = _read_jsonl(PATHS["immutable"], max_lines=80)
        if len(records) != self._last_line_count:
            self._render_all()
            self.scroll_end()


class DiagLogPanel(RichLog):
    """Live tail of a plain diagnostic log file."""

    DEFAULT_CSS = """
    DiagLogPanel {
        height: 1fr;
        border: solid #2A2535;
        background: #0D0B0E;
        padding: 0 1;
    }
    """

    def __init__(self, log_key: str, title: str, **kwargs):
        super().__init__(**kwargs)
        self._log_key = log_key
        self._title = title
        self._last_line_count: int = 0

    def on_mount(self) -> None:
        self.border_title = self._title
        self._render_all()

    def _render_all(self) -> None:
        self.clear()
        lines = _read_plain_log(PATHS[self._log_key])
        self._last_line_count = len(lines)
        for line in lines:
            self._write_line(line)

    def _write_line(self, line: str) -> None:
        line = line.strip()
        if not line:
            return

        color = "white"
        if "ERROR" in line or "FAIL" in line:
            color = "bright_red"
        elif "WARN" in line:
            color = "bright_yellow"
        elif "emerged" in line.lower() or "fired" in line.lower():
            color = "bright_green"
        elif "skip" in line.lower() or "no " in line.lower():
            color = "bright_black"
        elif "[ASSESSOR" in line or "[ARCHIVIST" in line:
            color = "bright_cyan"

        self.write(f"[{color}]{line[:120]}[/]")

    def refresh_data(self) -> None:
        lines = _read_plain_log(PATHS[self._log_key])
        if len(lines) != self._last_line_count:
            new_count = len(lines) - self._last_line_count
            self._last_line_count = len(lines)
            if new_count > 0:
                for line in lines[-new_count:]:
                    self._write_line(line)
                self.scroll_end()


# ════════════════════════════════════════════════════════════════════════════════
#  PULSE INDICATOR  (top right — shows last tick time)
# ════════════════════════════════════════════════════════════════════════════════

class PulseBar(Static):
    DEFAULT_CSS = """
    PulseBar {
        height: 1;
        background: #110F14;
        border-bottom: solid #2A2535;
        padding: 0 2;
        color: #5A5068;
    }
    """

    _tick: int = 0

    def pulse(self) -> None:
        self._tick += 1
        ts = datetime.now().strftime("%H:%M:%S")
        dot = "◉" if self._tick % 2 == 0 else "○"
        # Entity memory file sizes
        em_path = PATHS["entity_memory"]
        em = f"entity_mem {_file_size_kb(em_path)}" if em_path.exists() else ""
        self.update(
            f" {dot} OCULUS  ·  {ts}  ·  tick {self._tick}  ·  {em}"
        )


# ════════════════════════════════════════════════════════════════════════════════
#  THE OCULUS APP
# ════════════════════════════════════════════════════════════════════════════════

class OculusApp(App):
    """The Oculus — Arca Cognitorium Debug Monitor."""

    TITLE = "OCULUS"
    CSS = """
    Screen {
        background: #0D0B0E;
    }

    #root {
        layout: vertical;
        height: 100%;
        background: #0D0B0E;
    }

    #columns {
        layout: horizontal;
        height: 1fr;
    }

    /* ── Left column — Council + Reflection ────────────────────── */
    #col_left {
        width: 44;
        layout: vertical;
        border-right: solid #2A2535;
        background: #0D0B0E;
    }

    /* ── Middle column — System Status + Immutable Log ─────────── */
    #col_mid {
        width: 1fr;
        layout: vertical;
        border-right: solid #2A2535;
        background: #0D0B0E;
    }

    /* ── Right column — Diag Logs ──────────────────────────────── */
    #col_right {
        width: 52;
        layout: vertical;
        background: #0D0B0E;
    }

    #council_scroll {
        height: auto;
        max-height: 22;
        overflow-y: auto;
    }

    #reflection_scroll {
        height: 1fr;
        overflow-y: auto;
    }

    #status_scroll {
        height: auto;
        max-height: 28;
        overflow-y: auto;
    }

    #immutable_panel {
        height: 1fr;
    }

    #diag_assessor {
        height: 1fr;
    }

    #diag_archivist {
        height: 1fr;
    }

    SectionHeader {
        color: #5A5068;
        background: #110F14;
        border-bottom: solid #2A2535;
        padding: 0 1;
        height: 1;
        text-style: bold;
    }

    Footer {
        background: #110F14;
        color: #5A5068;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "force_refresh", "Refresh Now"),
    ]

    REFRESH_INTERVAL = 3.0   # seconds between auto-refresh

    def compose(self) -> ComposeResult:
        yield PulseBar(id="pulse")

        with Horizontal(id="columns"):
            # ── Left: Council + Reflection ───────────────────────────
            with Vertical(id="col_left"):
                yield SectionHeader("Council", "⬡")
                with ScrollableContainer(id="council_scroll"):
                    yield CouncilPanel(id="council_panel")
                yield SectionHeader("Reflection Engine", "◎")
                with ScrollableContainer(id="reflection_scroll"):
                    yield ReflectionPanel(id="reflection_panel")

            # ── Middle: Status + Immutable Log ───────────────────────
            with Vertical(id="col_mid"):
                yield SectionHeader("System State", "⛨")
                with ScrollableContainer(id="status_scroll"):
                    yield SystemStatusPanel(id="status_panel")
                yield ImmutableLogPanel(id="immutable_panel", highlight=True, markup=True)

            # ── Right: Diagnostic Logs ───────────────────────────────
            with Vertical(id="col_right"):
                yield DiagLogPanel("assessor_diag",    "ASSESSOR DIAG",    id="diag_assessor",  highlight=True, markup=True)
                yield DiagLogPanel("archivist_diag",   "ARCHIVIST DIAG",   id="diag_archivist", highlight=True, markup=True)

        yield Footer()

    def on_mount(self) -> None:
        self._timer: Timer = self.set_interval(self.REFRESH_INTERVAL, self._tick)

    def _tick(self) -> None:
        self.query_one(PulseBar).pulse()
        self.query_one("#council_panel",    CouncilPanel).refresh_data()
        self.query_one("#status_panel",     SystemStatusPanel).refresh_data()
        self.query_one("#reflection_panel", ReflectionPanel).refresh_data()
        self.query_one("#immutable_panel",  ImmutableLogPanel).refresh_data()
        self.query_one("#diag_assessor",    DiagLogPanel).refresh_data()
        self.query_one("#diag_archivist",   DiagLogPanel).refresh_data()

    def action_force_refresh(self) -> None:
        self._tick()

    def action_quit(self) -> None:
        self.exit()


# ════════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Allow running from project root or from tools/
    if Path("config.yaml").exists():
        pass  # Already at project root
    elif Path("../config.yaml").exists():
        os.chdir("..")
    else:
        print("ERROR: Run from the ArcaCognitorium project root.", file=sys.stderr)
        sys.exit(1)

    OculusApp().run()
