"""
Learning engine for Devoted Absurd.
v1.1 — Fixed update_user_score delta bug

Stores every session's prompts, scores, Claude reasoning, weaknesses,
and combo performance. Gradually shifts generation weights toward
high-scoring combinations, while preserving exploration randomness.
"""

import json
import os
import uuid
import time
from pathlib import Path
from typing import Optional


HISTORY_FILE = Path.home() / ".devoted_absurd" / "history.json"
HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

# How strongly high scores pull the weights (0=no learning, 1=strong pull)
LEARNING_RATE = 0.15
# Minimum weight floor — no item ever falls below this
MIN_WEIGHT = 0.4
# Maximum weight ceiling
MAX_WEIGHT = 3.5
# Exploration factor: fraction of selections that ignore weights entirely
EXPLORATION_RATE = 0.25


def _load() -> dict:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "entries": [],
        "combo_scores": {},   # item_string -> {"total": float, "count": int}
        "weights": {},        # item_string -> float
        "weakness_freq": {},  # weakness_tag -> int
        "meta": {
            "total_generated": 0,
            "total_rated": 0,
            "avg_user_score": None,
            "avg_claude_score": None,
            "disagreements": 0,
        }
    }


def _save(data: dict):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _update_weights(data: dict, char: dict, score: float):
    """
    Nudge weights for every field value in this character based on score.
    Score expected 1-10. Neutral = 5.5. Above → weight up. Below → weight down.
    """
    delta = (score - 5.5) * LEARNING_RATE
    fields = [
        char.get("role"), char.get("personality"), char.get("garment"),
        char.get("prop"), char.get("detail"), char.get("mood"),
        char.get("posture"), char.get("body_type"), char.get("age"),
        char.get("archetype_key"),
    ]
    for item in fields:
        if not item:
            continue
        current = data["weights"].get(item, 1.0)
        new_val = max(MIN_WEIGHT, min(MAX_WEIGHT, current + delta))
        data["weights"][item] = round(new_val, 4)

        # Also update combo_scores
        if item not in data["combo_scores"]:
            data["combo_scores"][item] = {"total": 0.0, "count": 0}
        data["combo_scores"][item]["total"] += score
        data["combo_scores"][item]["count"] += 1


def _reverse_weights(data: dict, char: dict, score: float):
    """
    Reverse a previous weight update. Used when user_score replaces
    a previous final_score — we undo the old learning before applying new.
    """
    delta = (score - 5.5) * LEARNING_RATE
    fields = [
        char.get("role"), char.get("personality"), char.get("garment"),
        char.get("prop"), char.get("detail"), char.get("mood"),
        char.get("posture"), char.get("body_type"), char.get("age"),
        char.get("archetype_key"),
    ]
    for item in fields:
        if not item:
            continue
        current = data["weights"].get(item, 1.0)
        # Reverse the delta
        new_val = max(MIN_WEIGHT, min(MAX_WEIGHT, current - delta))
        data["weights"][item] = round(new_val, 4)

        # Reverse combo_scores
        if item in data["combo_scores"]:
            data["combo_scores"][item]["total"] -= score
            data["combo_scores"][item]["count"] -= 1
            if data["combo_scores"][item]["count"] <= 0:
                del data["combo_scores"][item]


def record_entry(
    char: dict,
    prompt: str,
    claude_score: float,
    claude_reasoning: str,
    claude_refined_prompt: str,
    weaknesses: list[str],
    user_score: Optional[float] = None,
) -> str:
    """
    Persist a generation event. Returns the entry ID.
    Final score = user_score if provided, else claude_score.
    Learning is triggered immediately.
    """
    data = _load()
    entry_id = str(uuid.uuid4())[:8]

    final_score = user_score if user_score is not None else claude_score
    disagreement = (
        user_score is not None and abs(user_score - claude_score) >= 2.0
    )

    entry = {
        "id": entry_id,
        "timestamp": time.time(),
        "archetype": char.get("archetype_key"),
        "char_snapshot": char,
        "original_prompt": prompt,
        "refined_prompt": claude_refined_prompt,
        "claude_score": claude_score,
        "user_score": user_score,
        "final_score": final_score,
        "claude_reasoning": claude_reasoning,
        "weaknesses": weaknesses,
        "disagreement": disagreement,
    }

    data["entries"].append(entry)
    _update_weights(data, char, final_score)

    # Record weaknesses
    for w in weaknesses:
        data["weakness_freq"][w] = data["weakness_freq"].get(w, 0) + 1

    # Update meta
    m = data["meta"]
    m["total_generated"] += 1
    if user_score is not None:
        m["total_rated"] += 1
    if disagreement:
        m["disagreements"] += 1

    all_claude = [e["claude_score"] for e in data["entries"] if e["claude_score"]]
    all_user = [e["user_score"] for e in data["entries"] if e["user_score"] is not None]
    m["avg_claude_score"] = round(sum(all_claude) / len(all_claude), 2) if all_claude else None
    m["avg_user_score"] = round(sum(all_user) / len(all_user), 2) if all_user else None

    _save(data)
    return entry_id


def update_user_score(entry_id: str, user_score: float):
    """
    Apply or update user rating for an existing entry.
    Properly reverses the old weight update and applies a new one
    based on the absolute user_score, not a delta-of-deltas.
    """
    data = _load()
    for entry in data["entries"]:
        if entry["id"] == entry_id:
            old_final = entry["final_score"]
            char = entry["char_snapshot"]

            # Reverse the learning from the old final score
            _reverse_weights(data, char, old_final)

            # Apply new learning from the user score
            entry["user_score"] = user_score
            entry["final_score"] = user_score
            entry["disagreement"] = abs(user_score - entry["claude_score"]) >= 2.0

            _update_weights(data, char, user_score)

            # Update meta
            m = data["meta"]
            if old_final == entry["claude_score"]:
                # This is the first user rating for this entry
                m["total_rated"] = m.get("total_rated", 0) + 1

            all_user = [e["user_score"] for e in data["entries"] if e["user_score"] is not None]
            m["avg_user_score"] = round(sum(all_user) / len(all_user), 2) if all_user else None
            m["disagreements"] = sum(1 for e in data["entries"] if e.get("disagreement"))

            break
    _save(data)


def get_weights() -> dict:
    """Return current weights dict for use in weighted_pick."""
    return _load().get("weights", {})


def get_stats() -> dict:
    data = _load()
    m = data["meta"].copy()
    m["top_weaknesses"] = sorted(
        data["weakness_freq"].items(), key=lambda x: -x[1]
    )[:10]
    m["top_combos"] = sorted(
        [
            (k, round(v["total"] / v["count"], 2))
            for k, v in data["combo_scores"].items()
            if v["count"] >= 2
        ],
        key=lambda x: -x[1],
    )[:15]
    m["worst_combos"] = sorted(
        [
            (k, round(v["total"] / v["count"], 2))
            for k, v in data["combo_scores"].items()
            if v["count"] >= 2
        ],
        key=lambda x: x[1],
    )[:10]
    return m


def get_history(limit: int = 50) -> list:
    data = _load()
    return list(reversed(data["entries"]))[:limit]


def clear_history():
    _save({
        "entries": [],
        "combo_scores": {},
        "weights": {},
        "weakness_freq": {},
        "meta": {
            "total_generated": 0,
            "total_rated": 0,
            "avg_user_score": None,
            "avg_claude_score": None,
            "disagreements": 0,
        }
    })
