"""
models.py — Dolium v2
Idea, ChamberLog, CullRecord dataclasses with to_dict / from_dict.
No UI dependency. No external imports beyond stdlib.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Chamber constants ─────────────────────────────────────────────────────────

CHAMBER_FOMENTARY   = 1
CHAMBER_CULTIVATION = 2
CHAMBER_VESTIBULE   = 3
CHAMBER_CODEX       = 4

CHAMBER_NAMES = {
    1: "I · The Fomentary",
    2: "II · The Cultivation House",
    3: "III · The Vestibule",
    4: "IV · The Codex",
}


# ── ChamberLog ────────────────────────────────────────────────────────────────

@dataclass
class ChamberLog:
    """Records a single chamber transition."""
    from_chamber: int
    to_chamber:   int
    timestamp:    str = field(default_factory=lambda: _now())
    note:         str = ""

    def to_dict(self) -> dict:
        return {
            "from_chamber": self.from_chamber,
            "to_chamber":   self.to_chamber,
            "timestamp":    self.timestamp,
            "note":         self.note,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ChamberLog:
        return cls(
            from_chamber = d["from_chamber"],
            to_chamber   = d["to_chamber"],
            timestamp    = d.get("timestamp", ""),
            note         = d.get("note", ""),
        )


# ── CullRecord ────────────────────────────────────────────────────────────────

@dataclass
class CullRecord:
    """Records a cull event for an idea."""
    idea_id:   str
    reason:    str
    timestamp: str = field(default_factory=lambda: _now())
    chamber:   int = 1

    def to_dict(self) -> dict:
        return {
            "idea_id":   self.idea_id,
            "reason":    self.reason,
            "timestamp": self.timestamp,
            "chamber":   self.chamber,
        }

    @classmethod
    def from_dict(cls, d: dict) -> CullRecord:
        return cls(
            idea_id   = d["idea_id"],
            reason    = d["reason"],
            timestamp = d.get("timestamp", ""),
            chamber   = d.get("chamber", 1),
        )


# ── ConversationTurn ──────────────────────────────────────────────────────────

@dataclass
class ConversationTurn:
    """A single turn in the idea's conversation history."""
    role:      str   # "user" | "assistant"
    content:   str
    timestamp: str = field(default_factory=lambda: _now())
    is_whisper: bool = False  # True for ambient whisper turns

    def to_dict(self) -> dict:
        return {
            "role":       self.role,
            "content":    self.content,
            "timestamp":  self.timestamp,
            "is_whisper": self.is_whisper,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ConversationTurn:
        return cls(
            role       = d["role"],
            content    = d["content"],
            timestamp  = d.get("timestamp", ""),
            is_whisper = d.get("is_whisper", False),
        )


# ── Idea ──────────────────────────────────────────────────────────────────────

@dataclass
class Idea:
    """
    The primary domain object. Flows through four chambers.
    All fields are strings; gate logic checks content, not type.
    """

    # Identity
    id:      str = field(default_factory=lambda: str(uuid.uuid4()))
    title:   str = ""
    chamber: int = CHAMBER_FOMENTARY
    created: str = field(default_factory=lambda: _now())
    updated: str = field(default_factory=lambda: _now())
    culled:  bool = False

    # Chamber I — The Fomentary
    body:       str = ""
    motivation: str = ""

    # Chamber II — The Cultivation House
    elaboration:   str = ""
    obstacles:     str = ""
    first_step:    str = ""

    # Chamber III — The Vestibule
    refined_form:  str = ""
    open_problems: str = ""
    next_actions:  str = ""

    # Chamber IV — The Codex
    declaration:   str = ""
    summary:       str = ""
    tags:          list[str] = field(default_factory=list)

    # History
    chamber_log:   list[ChamberLog]       = field(default_factory=list)
    conversation:  list[ConversationTurn] = field(default_factory=list)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def touch(self) -> None:
        self.updated = _now()

    def chamber_name(self) -> str:
        return CHAMBER_NAMES.get(self.chamber, f"Chamber {self.chamber}")

    def word_count(self, text: str) -> int:
        return len(text.split()) if text.strip() else 0

    def char_count(self, text: str) -> int:
        return len(text.strip())

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "title":         self.title,
            "chamber":       self.chamber,
            "created":       self.created,
            "updated":       self.updated,
            "culled":        self.culled,
            "body":          self.body,
            "motivation":    self.motivation,
            "elaboration":   self.elaboration,
            "obstacles":     self.obstacles,
            "first_step":    self.first_step,
            "refined_form":  self.refined_form,
            "open_problems": self.open_problems,
            "next_actions":  self.next_actions,
            "declaration":   self.declaration,
            "summary":       self.summary,
            "tags":          self.tags,
            "chamber_log":   [e.to_dict() for e in self.chamber_log],
            "conversation":  [t.to_dict() for t in self.conversation],
        }

    @classmethod
    def from_dict(cls, d: dict) -> Idea:
        idea = cls(
            id            = d.get("id",            str(uuid.uuid4())),
            title         = d.get("title",         ""),
            chamber       = d.get("chamber",       CHAMBER_FOMENTARY),
            created       = d.get("created",       _now()),
            updated       = d.get("updated",       _now()),
            culled        = d.get("culled",        False),
            body          = d.get("body",          ""),
            motivation    = d.get("motivation",    ""),
            elaboration   = d.get("elaboration",   ""),
            obstacles     = d.get("obstacles",     ""),
            first_step    = d.get("first_step",    ""),
            refined_form  = d.get("refined_form",  ""),
            open_problems = d.get("open_problems", ""),
            next_actions  = d.get("next_actions",  ""),
            declaration   = d.get("declaration",   ""),
            summary       = d.get("summary",       ""),
            tags          = d.get("tags",          []),
        )
        idea.chamber_log  = [ChamberLog.from_dict(e)       for e in d.get("chamber_log",  [])]
        idea.conversation = [ConversationTurn.from_dict(t) for t in d.get("conversation", [])]
        return idea
