"""
AUCTORITAS SPECTRALIS — v1.0.0
export/theme_json.py — theme.json export
export/qss.py       — PyQt6 QSS export
export/markdown.py  — Markdown documentation fragment export
export/css.py       — CSS custom properties export

All formats emitted on ratification (and on Promulgare without sealing).
theme.json is the inter-app contract. Bureau I sole writer.
Written to ~/.arca/theme.json on every ratification.
"""

import json
import datetime
from pathlib import Path

from AuctoritasSpectralis.engine.jitter import TOKEN_ORDER
import AuctoritasSpectralis.config as cfg


# ── theme.json ────────────────────────────────────────────────────────────

def write_theme_json(
    palette:    dict[str, str],
    designator: str,
    seal:       str,
    nomina:     dict[str, str] | None = None,
    export_dir: Path | None = None,
) -> Path:
    """
    Write theme.json to ~/.arca/theme.json (suite contract)
    and optionally to export_dir/theme.json.
    Returns the suite contract path.
    """
    payload = {
        "_meta": {
            "designator":   designator,
            "seal":         seal,
            "sealed_at":    datetime.datetime.now().isoformat(timespec="seconds"),
            "bureau":       "I — Auctoritas Spectralis",
            "version":      "1.0.0",
        },
        "tokens": {k: palette.get(k, "") for k in TOKEN_ORDER if k in palette},
        "nomina": nomina or {},
    }

    # Suite contract location
    suite_path = cfg.THEME_JSON
    suite_path.parent.mkdir(parents=True, exist_ok=True)
    suite_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Export copy
    if export_dir:
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        export_path = export_dir / "theme.json"
        export_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return suite_path


def write_signal_file(designator: str) -> None:
    """
    Write ~/.arca/signals/theme_updated — interim broadcast mechanism.
    Plain text: ISO timestamp + designator.
    Downstream consumers poll this file at 2000ms intervals.
    """
    signal_path = Path(cfg.get("signal_file_path", str(cfg.SIGNAL_FILE)))
    signal_path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        f"{datetime.datetime.now().isoformat(timespec='seconds')}\n"
        f"{designator}\n"
    )
    signal_path.write_text(content, encoding="utf-8")


# ── QSS ──────────────────────────────────────────────────────────────────

def write_qss(
    palette:    dict[str, str],
    designator: str,
    export_dir: Path | None = None,
) -> str:
    """
    Generate a QSS stylesheet from the palette tokens.
    Returns the QSS string. Writes to export_dir if provided.
    """
    p = palette

    def t(key: str, fallback: str = "#000000") -> str:
        return p.get(key, fallback)

    qss = f"""/*
  AUCTORITAS SPECTRALIS — Generated Theme
  Designator: {designator}
  Bureau I — Triumviratus Aestheticus Imperialis
  Do not edit manually. Regenerate via Auctoritas Spectralis.
*/

/* ── Token definitions ── */
/* c_bg:        {t("c_bg")} */
/* c_gold:      {t("c_gold")} */
/* c_panel:     {t("c_panel")} */
/* c_subtle:    {t("c_subtle")} */
/* c_gold_dark: {t("c_gold_dark")} */
/* c_gold_dim:  {t("c_gold_dim")} */
/* c_text:      {t("c_text")} */
/* c_white:     {t("c_white")} */
/* c_crimson:   {t("c_crimson")} */
/* c_teal:      {t("c_teal")} */

QWidget {{
    background-color: {t("c_bg")};
    color: {t("c_text")};
    font-family: "IM Fell English", "Georgia", serif;
    font-size: 12px;
    border: none;
    outline: none;
}}

QMainWindow {{
    background-color: {t("c_bg")};
}}

QPushButton {{
    background-color: {t("c_bg")};
    color: {t("c_gold_dim")};
    border: 1px solid {t("c_gold_dark")};
    font-family: "Share Tech Mono", "Courier New", monospace;
    font-size: 9px;
    letter-spacing: 1.5px;
    padding: 5px 12px;
    min-height: 22px;
}}

QPushButton:hover {{
    background-color: {t("c_gold_dark")};
    color: {t("c_gold")};
    border-color: {t("c_gold_dim")};
}}

QPushButton:pressed {{
    background-color: {t("c_gold_dim")};
    color: {t("c_bg")};
}}

QLabel {{
    background: transparent;
    color: {t("c_text")};
}}

QLineEdit {{
    background-color: {t("c_bg")};
    color: {t("c_text")};
    border: 1px solid {t("c_gold_dark")};
    font-family: "Share Tech Mono", monospace;
    font-size: 10px;
    padding: 4px 8px;
    selection-background-color: {t("c_gold_dark")};
    selection-color: {t("c_gold")};
}}

QLineEdit:focus {{
    border-color: {t("c_gold_dim")};
}}

QComboBox {{
    background-color: {t("c_bg")};
    color: {t("c_gold")};
    border: 1px solid {t("c_gold_dark")};
    font-family: "Share Tech Mono", monospace;
    font-size: 9px;
    padding: 4px 8px;
}}

QScrollBar:vertical {{
    background: {t("c_bg")};
    width: 8px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background: {t("c_gold_dark")};
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {t("c_gold_dim")};
}}

QTabBar::tab {{
    background-color: transparent;
    color: {t("c_gold_dim")};
    font-family: "Share Tech Mono", monospace;
    font-size: 9px;
    letter-spacing: 2px;
    padding: 7px 16px;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: {t("c_gold")};
    border-bottom: 2px solid {t("c_gold")};
    background-color: rgba(212, 175, 55, 0.04);
}}

QTableWidget, QTableView {{
    background-color: {t("c_bg")};
    color: {t("c_text")};
    border: 1px solid {t("c_gold_dark")};
    gridline-color: {t("c_gold_dark")};
    font-family: "Share Tech Mono", monospace;
    font-size: 9px;
}}

QHeaderView::section {{
    background-color: {t("c_panel")};
    color: {t("c_gold")};
    border: 1px solid {t("c_gold_dark")};
    font-family: "Share Tech Mono", monospace;
    font-size: 8px;
    padding: 4px 8px;
    font-weight: normal;
}}

QToolTip {{
    background-color: {t("c_panel")};
    color: {t("c_text")};
    border: 1px solid {t("c_gold_dark")};
    font-family: "Share Tech Mono", monospace;
    font-size: 10px;
    padding: 4px 8px;
}}
"""

    if export_dir:
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        (export_dir / "theme.qss").write_text(qss, encoding="utf-8")

    return qss


# ── Markdown ──────────────────────────────────────────────────────────────

def write_markdown(
    palette:    dict[str, str],
    designator: str,
    seal:       str,
    nomina:     dict[str, str] | None = None,
    export_dir: Path | None = None,
) -> str:
    """
    Generate a Markdown documentation fragment.
    Returns the Markdown string.
    """
    nomina = nomina or {}
    now    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {designator}",
        f"",
        f"**Bureau I — Auctoritas Spectralis** · Sealed {now}",
        f"",
        f"Seal: `{seal}`",
        f"",
        f"## Tokens",
        f"",
    ]

    # Build a box-drawing table
    header = "┌──────────────┬──────────┬────────────────────────────┐"
    row_hd = "│ Token        │ Hex      │ Nomen                      │"
    div    = "├──────────────┼──────────┼────────────────────────────┤"
    footer = "└──────────────┴──────────┴────────────────────────────┘"

    lines.append("```")
    lines.append(header)
    lines.append(row_hd)
    lines.append(div)
    for key in TOKEN_ORDER:
        hex_val = palette.get(key, "#000000")
        nomen   = nomina.get(key, "—")
        lines.append(
            f"│ {key:<12} │ {hex_val:<8} │ {nomen:<26} │"
        )
    lines.append(footer)
    lines.append("```")
    lines.append("")
    lines.append("*Codexium Chromaticus · Sequentiae Umbrarum*")

    md = "\n".join(lines)

    if export_dir:
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        (export_dir / "theme.md").write_text(md, encoding="utf-8")

    return md


# ── CSS ───────────────────────────────────────────────────────────────────

def write_css(
    palette:    dict[str, str],
    designator: str,
    export_dir: Path | None = None,
) -> str:
    """
    Generate CSS custom properties for web consumption.
    Returns the CSS string.
    """
    css_lines = [
        f"/* {designator} */",
        f"/* Bureau I — Auctoritas Spectralis */",
        f"",
        f":root {{",
    ]
    for key in TOKEN_ORDER:
        css_var = key.replace("_", "-")
        hex_val = palette.get(key, "#000000")
        css_lines.append(f"  --{css_var}: {hex_val};")
    css_lines.append("}")
    css = "\n".join(css_lines)

    if export_dir:
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        (export_dir / "theme.css").write_text(css, encoding="utf-8")

    return css


# ── Full ratification export ──────────────────────────────────────────────

def ratification_export(
    palette:    dict[str, str],
    designator: str,
    seal:       str,
    nomina:     dict[str, str] | None = None,
) -> dict[str, Path | str]:
    """
    Run the full four-format export for a ratified palette.
    Writes to configured export_directory.
    Returns dict of format → path/content.
    """
    export_dir = Path(cfg.get("export_directory", str(Path.home() / "exports")))

    # Sub-directory per designator (slugified)
    slug = designator.replace(" ", "_").lower()
    dest = export_dir / slug
    dest.mkdir(parents=True, exist_ok=True)

    json_path = write_theme_json(palette, designator, seal, nomina, dest)
    write_signal_file(designator)
    qss   = write_qss(palette, designator, dest)
    md    = write_markdown(palette, designator, seal, nomina, dest)
    css   = write_css(palette, designator, dest)

    return {
        "theme_json": json_path,
        "qss":        dest / "theme.qss",
        "markdown":   dest / "theme.md",
        "css":        dest / "theme.css",
        "export_dir": dest,
    }
