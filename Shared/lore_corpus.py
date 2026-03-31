#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                          lore_corpus.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
#
# LORE CORPUS — Read Layer
# v1.0
#
# Read-only interface to the Lore Corpus.
# No write methods. No Claude calls. No side effects.
# Missing files return None — never raise on absent content.
#
# Consumed by:
#   Tower   — via Scribae, Luminarious, The Builder
#   Exocognii — any app that needs ratified lore
#
# Write authority: Exvacua Loricum only.
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

import json
import logging
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

log = logging.getLogger(__name__)


# ── Path resolution ───────────────────────────────────────────────────────────

def _corpus_root() -> Path:
    """Resolve the Lore Corpus root from config or fallback."""
    config_path = Path.home() / ".arca" / "config.json"
    try:
        with config_path.open() as f:
            cfg = json.load(f)
        repo = Path(cfg.get("arca_repo_path", Path.home() / "ArcaCognitorium"))
    except (OSError, json.JSONDecodeError):
        repo = Path.home() / "ArcaCognitorium"
    return repo / "Shared" / "Lore"


def _require_yaml() -> bool:
    """Return True if PyYAML is available, log warning if not."""
    if yaml is None:
        log.warning("lore_corpus: PyYAML not installed — corpus unavailable.")
        return False
    return True


# ── Register ──────────────────────────────────────────────────────────────────

def get_register() -> list[dict]:
    """
    Return all entries from register.yaml as a list of dicts.
    Returns empty list on any read or parse failure.
    """
    if not _require_yaml():
        return []
    register_path = _corpus_root() / "register.yaml"
    try:
        with register_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("entries", []) if isinstance(data, dict) else []
    except (OSError, yaml.YAMLError) as e:
        log.warning("lore_corpus: could not read register.yaml — %s", e)
        return []


def get_entry(entry_id: str) -> dict | None:
    """
    Return a single register entry by UUID.
    Returns None if not found or on read failure.
    """
    for entry in get_register():
        if entry.get("id") == entry_id:
            return entry
    return None


# ── Corpus files ──────────────────────────────────────────────────────────────

def get_card(entry_id: str) -> dict | None:
    """
    Return the Loridex Card JSON for the given UUID.
    Returns None if the entry or file does not exist.
    """
    entry = get_entry(entry_id)
    if not entry:
        return None
    card_rel = entry.get("card")
    if not card_rel:
        return None
    card_path = _corpus_root() / card_rel
    try:
        with card_path.open(encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        log.warning("lore_corpus: could not read card %s — %s", card_path, e)
        return None


def get_exloricum(entry_id: str) -> str | None:
    """
    Return the raw prose .md text for the given UUID.
    Returns None if the entry or file does not exist.
    """
    entry = get_entry(entry_id)
    if not entry:
        return None
    exl_rel = entry.get("exloricum")
    if not exl_rel:
        return None
    exl_path = _corpus_root() / exl_rel
    try:
        return exl_path.read_text(encoding="utf-8")
    except OSError as e:
        log.warning("lore_corpus: could not read exloricum %s — %s", exl_path, e)
        return None


# ── Filtering ─────────────────────────────────────────────────────────────────

def list_by_domain(domain: str) -> list[dict]:
    """
    Return all register entries whose domain matches the given string (exact).
    """
    return [e for e in get_register() if e.get("domain") == domain]


def list_by_tag(tag: str) -> list[dict]:
    """
    Return all register entries that carry the given tag.
    """
    return [e for e in get_register() if tag in e.get("tags", [])]


def list_by_status(status: str) -> list[dict]:
    """
    Return all register entries with the given status.
    Typical values: 'ratified', 'flagged_for_revision'.
    """
    return [e for e in get_register() if e.get("status") == status]


# ── Taxonomy ──────────────────────────────────────────────────────────────────

def list_all_domains() -> list[str]:
    """
    Return all domain names from taxonomy/domains.yaml.
    Returns empty list on failure.
    """
    if not _require_yaml():
        return []
    domains_path = _corpus_root() / "taxonomy" / "domains.yaml"
    try:
        with domains_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return [d["name"] for d in data.get("domains", []) if "name" in d]
    except (OSError, yaml.YAMLError) as e:
        log.warning("lore_corpus: could not read domains.yaml — %s", e)
        return []


def get_domain_info(domain: str) -> dict | None:
    """
    Return the full domain record from domains.yaml for the given domain name.
    Returns None if not found.
    """
    if not _require_yaml():
        return None
    domains_path = _corpus_root() / "taxonomy" / "domains.yaml"
    try:
        with domains_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for d in data.get("domains", []):
            if d.get("name") == domain:
                return d
    except (OSError, yaml.YAMLError) as e:
        log.warning("lore_corpus: could not read domains.yaml — %s", e)
    return None


# ── Health ────────────────────────────────────────────────────────────────────

def corpus_status() -> dict:
    """
    Return a status dict for the corpus.
    Used by Praesidium read layer and diagnostic tooling.

    Returns:
        {
            "root": str,
            "register_readable": bool,
            "entry_count": int,
            "taxonomy_readable": bool,
            "domain_count": int,
        }
    """
    root = _corpus_root()
    register = get_register()
    domains  = list_all_domains()
    return {
        "root":               str(root),
        "register_readable":  bool(register) or (root / "register.yaml").exists(),
        "entry_count":        len(register),
        "taxonomy_readable":  bool(domains),
        "domain_count":       len(domains),
    }
