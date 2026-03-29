#!/usr/bin/env python3
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                       crystalizer.py   ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
"""
Loretic Crystalizer — post-ratification compendium engine.

Triggered after every Sacramentum Finalitus.
Surgically updates the Loricum Ratifex with new canon entries.
Skips or flags Wizard-authored sections.
"""

import re
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from db import get_db, row_to_dict
from config import get as get_cfg

log = logging.getLogger("crystalizer")

_WIZARD_PROVENANCE = re.compile(r"<!--\s*wizard:")
_CRYSTALIZER_MARKER = "<!-- crystalizer:"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ratifex_path() -> Path:
    cfg   = get_cfg()
    store = Path(cfg["exvacua_loricum_store"])
    return store / "loricum_ratifex.md"


def _read_ratifex() -> str:
    p = _ratifex_path()
    return p.read_text() if p.exists() else ""


def _write_ratifex(content: str):
    p = _ratifex_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def _section_is_wizard_authored(section_body: str) -> bool:
    """Return True if the section contains a wizard provenance comment."""
    return bool(_WIZARD_PROVENANCE.search(section_body))


def _build_entry(card: dict) -> str:
    """Format a new Ratifex entry from a Loridex Card."""
    title   = card.get("title", "Untitled")
    tags    = card.get("tags", [])
    tags_str = ", ".join(tags) if tags else "—"
    summary = ""
    # Try to get summary from exloricum if bound
    if card.get("exloricum_id"):
        try:
            with get_db() as conn:
                ex = conn.execute(
                    "SELECT file_path FROM exlorica WHERE id = ?",
                    (card["exloricum_id"],)
                ).fetchone()
            if ex and ex["file_path"]:
                body = Path(ex["file_path"]).read_text()
                # First paragraph after frontmatter
                parts = body.split("---", 2)
                prose = parts[2].strip() if len(parts) >= 3 else body
                summary = prose.split("\n\n")[0][:400]
        except Exception:
            pass

    now_date = _now()[:10]
    return (
        f"## {title}\n"
        f"{_CRYSTALIZER_MARKER} {now_date} -->\n"
        f"**Tags:** {tags_str}  \n"
        f"**Canon ID:** `{card['id']}`\n\n"
        f"{summary}\n"
    )


def _get_or_create_section(body: str, domain: str) -> tuple[str, bool]:
    """
    Return (section_body, found).
    section_body is the content under the domain H1 heading.
    """
    pattern = re.compile(
        r'^# ' + re.escape(domain.upper()) + r'\s*\n(.*?)(?=^# |\Z)',
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    m = pattern.search(body)
    if m:
        return m.group(1), True
    return "", False


def _replace_section(body: str, domain: str, new_section_content: str) -> str:
    header  = f"# {domain.upper()}\n"
    pattern = re.compile(
        r'^# ' + re.escape(domain.upper()) + r'\s*\n(.*?)(?=^# |\Z)',
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    replacement = header + new_section_content + "\n"
    if pattern.search(body):
        return pattern.sub(replacement, body)
    # Append new section
    return body.rstrip() + "\n\n" + header + new_section_content + "\n"


def run_crystalizer(card_id: str):
    """
    Update the Loricum Ratifex with the newly ratified card.
    Called synchronously from the Judicium commit background task.
    """
    try:
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM loridex_cards WHERE id = ?", (card_id,)
            ).fetchone()
            if not row:
                log.warning(f"Crystalizer: card {card_id} not found")
                return
            card = row_to_dict(row)

        domain = card.get("domain", "").strip()
        if not domain:
            log.warning(f"Crystalizer: card {card_id} has no domain — skipping")
            return

        body = _read_ratifex()
        section_content, found = _get_or_create_section(body, domain)

        # If section is wizard-authored, flag rather than overwrite
        if found and _section_is_wizard_authored(section_content):
            log.info(
                f"Crystalizer: domain '{domain}' is wizard-authored — "
                f"appending entry below wizard content"
            )
            new_entry      = _build_entry(card)
            new_section    = section_content.rstrip() + "\n\n" + new_entry
        else:
            new_entry   = _build_entry(card)
            new_section = (section_content.rstrip() + "\n\n" + new_entry
                           if section_content.strip()
                           else new_entry)

        new_body = _replace_section(body, domain, new_section)
        _write_ratifex(new_body)

        now = _now()
        with get_db() as conn:
            conn.execute("""
                UPDATE loricum_ratifex
                SET last_crystalized_at = ?, version = version + 1 WHERE id = 1
            """, (now,))

        log.info(f"Crystalizer: updated domain '{domain}' with card '{card['title']}'")

    except Exception as e:
        log.error(f"Crystalizer failed for card {card_id}: {e}")
