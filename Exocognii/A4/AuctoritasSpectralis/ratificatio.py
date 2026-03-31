# Auctoritas Spectralis — ratificatio.py
# v1.0.0
"""Palette ratification and seal generation."""

import hashlib
import json
from datetime import datetime, timezone

from .designator_gen import suggest_designator


def generate_seal(tokens: dict, designator: str) -> dict:
    """Generate a SHA-256 ratification seal.

    The seal covers canonical JSON of the token set, ISO 8601
    timestamp (UTC), and the designator string.
    """
    canonical = json.dumps(tokens, sort_keys=True, separators=(',', ':'))
    timestamp = datetime.now(timezone.utc).isoformat()
    seal_input = f"{canonical}|{timestamp}|{designator}"
    seal_hash = hashlib.sha256(seal_input.encode('utf-8')).hexdigest()
    return {
        'seal_hash': seal_hash,
        'sealed_at': timestamp,
        'designator': designator,
        'canonical_json': canonical,
    }


def can_ratify(audit_summary: dict) -> tuple[bool, list[dict]]:
    """Check whether ratification should be allowed.

    Returns (allowed, failing_pairs). If passes_aa is False,
    ratification is blocked unless the Wizard overrides.
    """
    passes = audit_summary.get('passes_aa', False)
    failing = audit_summary.get('failing_pairs', [])
    return passes, failing
