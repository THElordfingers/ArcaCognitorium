#╔══════════════════════════════════════════════════════════════════════════════
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨⛨⛨⛨
#║ ⛨⛨⛨⛨⛨
#║ ⛨⛨⛨
#║ ⛨⛨
#║ ⛨
#║ ⛨    The Dolium / models.py
#║ ⛨
#╚══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _uuid() -> str:
    return str(uuid.uuid4())


# ── ChamberLog ────────────────────────────────────────────────────────────────

@dataclass
class ChamberLog:
    """
    One entry per chamber transition.
    Appended to Idea.log on every advance or return.
    """
    from_chamber: int
    to_chamber:   int
    timestamp:    str = field(default_factory=_now)
    note:         str = ""

    def to_dict(self) -> dict:
        return {
            "from_chamber": self.from_chamber,
            "to_chamber":   self.to_chamber,
            "timestamp":    self.timestamp,
            "note":         self.note,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ChamberLog":
        return cls(
            from_chamber = int(d.get("from_chamber", 0)),
            to_chamber   = int(d.get("to_chamber",   0)),
            timestamp    = d.get("timestamp", _now()),
            note         = d.get("note", ""),
        )


# ── Idea ──────────────────────────────────────────────────────────────────────

@dataclass
class Idea:
    """
    The central object. One instance per idea, regardless of chamber.
    All fields are always present — optional fields default to empty string.
    """

    # Identity
    id:         str = field(default_factory=_uuid)
    title:      str = ""
    chamber:    int = 1
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    # Core content — available from chamber 1
    body:       str = ""
    motivation: str = ""
    tags:       list = field(default_factory=list)

    # Cultivation fields — gated to chamber 2+
    scope_in:   str = ""
    scope_out:  str = ""
    system_map: str = ""

    # Vestibule fields — gated to chamber 3+
    dependencies:    str = ""
    build_sequence:  str = ""
    open_questions:  str = ""
    aesthetic_notes: str = ""

    # Declaration — chamber 4
    declaration:  str = ""
    declared_at:  Optional[str] = None

    # History
    log:          list = field(default_factory=list)          # list[ChamberLog]
    conversation: list = field(default_factory=list)          # list[dict] role/content

    def touch(self) -> None:
        """Update updated_at to now."""
        self.updated_at = _now()

    def to_dict(self) -> dict:
        return {
            "id":              self.id,
            "title":           self.title,
            "chamber":         self.chamber,
            "created_at":      self.created_at,
            "updated_at":      self.updated_at,
            "body":            self.body,
            "motivation":      self.motivation,
            "tags":            self.tags,
            "scope_in":        self.scope_in,
            "scope_out":       self.scope_out,
            "system_map":      self.system_map,
            "dependencies":    self.dependencies,
            "build_sequence":  self.build_sequence,
            "open_questions":  self.open_questions,
            "aesthetic_notes": self.aesthetic_notes,
            "declaration":     self.declaration,
            "declared_at":     self.declared_at,
            "log":             [e.to_dict() for e in self.log],
            "conversation":    self.conversation,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Idea":
        idea = cls(
            id             = d.get("id",              _uuid()),
            title          = d.get("title",           ""),
            chamber        = int(d.get("chamber",     1)),
            created_at     = d.get("created_at",      _now()),
            updated_at     = d.get("updated_at",      _now()),
            body           = d.get("body",            ""),
            motivation     = d.get("motivation",      ""),
            tags           = d.get("tags",            []),
            scope_in       = d.get("scope_in",        ""),
            scope_out      = d.get("scope_out",       ""),
            system_map     = d.get("system_map",      ""),
            dependencies   = d.get("dependencies",    ""),
            build_sequence = d.get("build_sequence",  ""),
            open_questions = d.get("open_questions",  ""),
            aesthetic_notes= d.get("aesthetic_notes", ""),
            declaration    = d.get("declaration",     ""),
            declared_at    = d.get("declared_at",     None),
            conversation   = d.get("conversation",    []),
        )
        idea.log = [ChamberLog.from_dict(e) for e in d.get("log", [])]
        return idea


# ── CullRecord ────────────────────────────────────────────────────────────────

@dataclass
class CullRecord:
    """
    Written to culled.json when an idea is culled.
    The idea is removed from ideas.json.
    Epitaph is required — no epitaph, no cull.
    """
    id:              str = field(default_factory=_uuid)
    title:           str = ""
    chamber_at_cull: int = 1
    culled_at:       str = field(default_factory=_now)
    epitaph:         str = ""
    body_snapshot:   str = ""

    def to_dict(self) -> dict:
        return {
            "id":              self.id,
            "title":           self.title,
            "chamber_at_cull": self.chamber_at_cull,
            "culled_at":       self.culled_at,
            "epitaph":         self.epitaph,
            "body_snapshot":   self.body_snapshot,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CullRecord":
        return cls(
            id              = d.get("id",              _uuid()),
            title           = d.get("title",           ""),
            chamber_at_cull = int(d.get("chamber_at_cull", 1)),
            culled_at       = d.get("culled_at",       _now()),
            epitaph         = d.get("epitaph",         ""),
            body_snapshot   = d.get("body_snapshot",   ""),
        )


# ── Chamber name register ─────────────────────────────────────────────────────

CHAMBER_NAMES = {
    1: ("The Fomentary",       "Officina Fermentationis"),
    2: ("The Cultivation House","Domus Culturae"),
    3: ("The Vestibule",       "Atrium Iudicii"),
    4: ("The Codex Paratum",   "Codex Paratum"),
}

CHAMBER_COLORS = {
    1: "#A98FD4",   # violet
    2: "#7EC8C8",   # teal
    3: "#C87941",   # ember
    4: "#E8C96A",   # gold
}

def chamber_name(n: int) -> str:
    return CHAMBER_NAMES.get(n, ("Unknown", ""))[0]

def chamber_latin(n: int) -> str:
    return CHAMBER_NAMES.get(n, ("", "Unknown"))[1]

def chamber_color(n: int) -> str:
    return CHAMBER_COLORS.get(n, "#D4C8A8")
