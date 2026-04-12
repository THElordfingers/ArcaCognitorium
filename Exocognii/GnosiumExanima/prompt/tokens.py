# GNOSIUM EXANIMA — prompt/tokens.py
# v1.0.0
"""Rough token estimator. Not exact — for budget warnings only."""

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """Approximate token count (len // 3.5)."""
    if not text:
        return 0
    return int(len(text) / 3.5)
