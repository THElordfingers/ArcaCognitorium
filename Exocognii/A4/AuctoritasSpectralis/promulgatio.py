# Auctoritas Spectralis — promulgatio.py
# v1.0.0
"""Export engine: theme.json, .qss, and .md palette card."""

import json
from pathlib import Path
from datetime import datetime, timezone

from .schema import ThemePackage
from .auto_render import generate_qss
from .constants import (
    FONT_STACK, FONT_STACK_MONO, TOKEN_LABELS, TOKEN_NAMES,
    BUREAU_LATIN,
)


THEME_PACKAGE_KEYS = {
    'schema_version', 'bureau', 'alliance', 'designator',
    'seal_hash', 'sealed_at', 'base_pair', 'tokens',
    'oklab_tokens', 'contrast_summary', 'font_stack', 'font_stack_mono',
}


def _validate_package(package: dict) -> list[str]:
    """Validate a theme package dict against required keys.

    Returns list of error strings. Empty = valid.
    """
    errors = []
    missing = THEME_PACKAGE_KEYS - set(package.keys())
    extra = set(package.keys()) - THEME_PACKAGE_KEYS
    if missing:
        errors.append(f"Missing keys: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"Unexpected keys: {', '.join(sorted(extra))}")
    return errors


def build_theme_package(tokens: dict, oklab_tokens: dict,
                        base_pair: dict, seal_record: dict,
                        contrast_summary: dict) -> dict:
    """Assemble the complete ThemePackage dict."""
    return {
        'schema_version': '1.0',
        'bureau': 'auctoritas_spectralis',
        'alliance': 'a4',
        'designator': seal_record['designator'],
        'seal_hash': seal_record['seal_hash'],
        'sealed_at': seal_record['sealed_at'],
        'base_pair': base_pair,
        'tokens': tokens,
        'oklab_tokens': oklab_tokens,
        'contrast_summary': contrast_summary,
        'font_stack': FONT_STACK,
        'font_stack_mono': FONT_STACK_MONO,
    }


def export_theme_json(package: dict, export_dir: Path) -> Path:
    """Write theme.json to export directory."""
    errors = _validate_package(package)
    if errors:
        raise ValueError(f"Invalid theme package: {'; '.join(errors)}")

    export_dir.mkdir(parents=True, exist_ok=True)
    path = export_dir / 'theme.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(package, f, indent=2, ensure_ascii=False)
    return path


def export_qss(tokens: dict, export_dir: Path) -> Path:
    """Write theme.qss to export directory."""
    export_dir.mkdir(parents=True, exist_ok=True)
    path = export_dir / 'theme.qss'
    qss = generate_qss(tokens)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(qss)
    return path


def export_palette_card(tokens: dict, designator: str,
                        seal_hash: str, sealed_at: str,
                        contrast_summary: dict,
                        export_dir: Path) -> Path:
    """Write theme.md palette card to export directory."""
    export_dir.mkdir(parents=True, exist_ok=True)
    path = export_dir / 'theme.md'

    lines = [
        f"# {designator}",
        f"### {BUREAU_LATIN} — Palette Card",
        "",
        f"**Sealed:** {sealed_at}",
        f"**Seal:** `{seal_hash[:16]}...`",
        "",
        "## Chromata",
        "",
    ]

    for name in TOKEN_NAMES:
        label = TOKEN_LABELS.get(name, name)
        hex_val = tokens.get(name, '???')
        lines.append(f"- **{label}** (`{name}`): `{hex_val}`")

    lines.extend([
        "",
        "## Compliance",
        "",
        f"- WCAG AA: {'PASS' if contrast_summary.get('passes_aa') else 'FAIL'}",
        f"- WCAG AAA: {'PASS' if contrast_summary.get('passes_aaa') else 'FAIL'}",
        f"- Minimum WCAG ratio: {contrast_summary.get('min_wcag_ratio', 0):.2f}",
        f"- Minimum APCA Lc: {contrast_summary.get('min_apca_lc', 0):.1f}",
        "",
        "---",
        "",
        "*Ordo Discordia, Cosmos Inania*",
    ])

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return path


def export_all(tokens: dict, oklab_tokens: dict, base_pair: dict,
               seal_record: dict, contrast_summary: dict,
               export_dir: Path) -> dict[str, Path]:
    """Export all three formats. Returns dict of format -> path."""
    package = build_theme_package(
        tokens, oklab_tokens, base_pair, seal_record, contrast_summary
    )

    paths = {}
    paths['theme.json'] = export_theme_json(package, export_dir)
    paths['qss'] = export_qss(tokens, export_dir)
    paths['md'] = export_palette_card(
        tokens, seal_record['designator'],
        seal_record['seal_hash'], seal_record['sealed_at'],
        contrast_summary, export_dir
    )
    return paths
