"""
AUCTORITAS SPECTRALIS — v1.0.0
app.py — Application orchestrator

Wires all features into the A4 shell.
Owns the ratification pipeline, CONFIGURATIO modal,
Inductio Chromatica ceremony, and live Specularium updates.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer

import AuctoritasSpectralis.config as cfg
from AuctoritasSpectralis.shell import AuctoritasShell
from AuctoritasSpectralis.features.colores      import ColoresFeature
from AuctoritasSpectralis.features.scrutinium   import ScrutiniumFeature
from AuctoritasSpectralis.features.specularium  import SpeculariumFeature
from AuctoritasSpectralis.features.bibliotheca  import BibliothecaFeature
from AuctoritasSpectralis.features.registrum    import RegistrumFeature
from AuctoritasSpectralis.features.configuratio import ConfiguratioModal

import AuctoritasSpectralis.registry.db as db
from AuctoritasSpectralis.engine.seal import compute_seal, assign_designator, make_ratification_record
from AuctoritasSpectralis.engine.nomen import generate_nomina
from AuctoritasSpectralis.export.theme_json import ratification_export, write_theme_json
from AuctoritasSpectralis.nuntius_emit import emit_event

# ── QSS loader ───────────────────────────────────────────────────────────

def _load_base_qss() -> str:
    from pathlib import Path
    qss_path = Path(__file__).parent / "assets" / "styles" / "base.qss"
    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""


# ── Main application class ───────────────────────────────────────────────

class AuctoritasSpectralisApp(AuctoritasShell):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Apply base stylesheet
        qss = _load_base_qss()
        if qss:
            QApplication.instance().setStyleSheet(qss)

        # Initialise DB
        db.initialise()

        # Build features
        self._colores     = ColoresFeature()
        self._scrutinium  = ScrutiniumFeature()
        self._specularium = SpeculariumFeature()
        self._bibliotheca = BibliothecaFeature()
        self._registrum   = RegistrumFeature()

        # Add to canvas in correct order (matches Feature Codex)
        self.add_feature(self._colores)      # 0
        self.add_feature(self._scrutinium)   # 1
        self.add_feature(self._specularium)  # 2
        self.add_feature(self._bibliotheca)  # 3
        self.add_feature(self._registrum)    # 4

        # CONFIGURATIO modal — parented to canvas
        self._configuratio = ConfiguratioModal(self.canvas)
        self._configuratio.resize(self.canvas.size())

        # Wire all signals
        self._wire_signals()

        # Set initial Fascia buttons for feature 0 (COLORES)
        self._update_fascia(0)

        # Initial palette push to all consumers
        initial_palette = self._colores.get_palette()
        self._push_palette(initial_palette)

        # Update theme state in Titulum
        designator = assign_designator(initial_palette)
        seal_trunc = compute_seal(initial_palette)[:8] + "…"
        self.update_theme_state(designator, seal_trunc)
        self.set_status("Colores", "Auctoritas Spectralis · v1.0.0")

        # Ceremony check — defer slightly for window to settle
        QTimer.singleShot(200, self._check_ceremony)

    # ── Signal wiring ──────────────────────────────────────────────────

    def _wire_signals(self) -> None:
        # Feature selection
        self.feature_changed.connect(self._update_fascia)

        # LAT/EN toggle — propagate to all features and re-register fascia
        self.titulum.lang_changed.connect(self._on_lang_changed)

        # COLORES signals
        self._colores.palette_changed.connect(self._on_palette_changed)
        self._colores.ratify_requested.connect(self._on_ratify)
        self._colores.export_requested.connect(self._on_promulgate)
        self._colores.save_requested.connect(self._on_save_draft)
        self._colores.load_requested.connect(self._on_load_from_bibliotheca)
        self._colores.new_requested.connect(self._on_new_palette)
        self._colores.status_message.connect(self.set_status)

        # SCRUTINIUM signals
        self._scrutinium.status_message.connect(self.set_status)
        self._scrutinium.export_requested.connect(self._on_export_contrast_report)

        # SPECULARIUM signals
        self._specularium.status_message.connect(self.set_status)

        # BIBLIOTHECA signals
        self._bibliotheca.load_requested.connect(self._on_bibliotheca_load)
        self._bibliotheca.fork_requested.connect(self._on_bibliotheca_fork)
        self._bibliotheca.compare_requested.connect(self._on_bibliotheca_compare)
        self._bibliotheca.status_message.connect(self.set_status)

        # REGISTRUM signals
        self._registrum.export_requested.connect(self._on_export_registry)
        self._registrum.status_message.connect(self.set_status)

        # CONFIGURATIO signals
        self.fascia.config_requested.connect(self._on_config_requested)
        self._configuratio.saved.connect(self._on_config_saved)
        self._configuratio.closed.connect(self._on_config_closed)

        # Canvas resize → resize modal overlay
        self.canvas.resized = self._on_canvas_resize  # type: ignore

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize the configuratio overlay to match canvas
        if hasattr(self, "_configuratio"):
            self._configuratio.setGeometry(self.canvas.rect())

    # ── Fascia management ──────────────────────────────────────────────

    def _update_fascia(self, feature_index: int) -> None:
        mode = self.titulum.lang
        feature_map = {
            0: self._colores,
            1: self._scrutinium,
            2: self._specularium,
            3: self._bibliotheca,
            4: self._registrum,
        }
        feature = feature_map.get(feature_index)
        if feature and hasattr(feature, "get_fascia_buttons"):
            self.register_feature_buttons(feature_index, feature.get_fascia_buttons(mode))

        from AuctoritasSpectralis.shell import FEATURE_KEYS
        key = FEATURE_KEYS[feature_index] if feature_index < len(FEATURE_KEYS) else FEATURE_KEYS[0]
        self.fascia.switch_to(key)

        status_map = {
            0: ("Colores",      "Palette Forge"),
            1: ("Observatory",  "Contrast Audit"),
            2: ("Specularium",  "Live Preview"),
            3: ("Bibliotheca",  f"{db.count()} palettes"),
            4: ("Registrum",    "Read Only · Permanent Ledger"),
        }
        left, right = status_map.get(feature_index, ("—", ""))
        self.set_status(left, right)

        if feature_index == 3:
            self._bibliotheca.refresh(self._colores.get_palette())

    # ── Language toggle ────────────────────────────────────────────────

    def _on_lang_changed(self, mode: str) -> None:
        """Propagate LAT/EN mode to all features, re-register active fascia buttons."""
        # Update all feature canvas widgets
        for feature in [self._colores, self._scrutinium, self._specularium,
                        self._bibliotheca, self._registrum]:
            if hasattr(feature, "set_mode"):
                feature.set_mode(mode)

        # Update configuratio modal
        if hasattr(self, "_configuratio") and hasattr(self._configuratio, "set_mode"):
            self._configuratio.set_mode(mode)

        # Re-register fascia buttons for the active feature with new mode
        active_index = self.canvas.currentIndex()
        self._update_fascia(active_index)

    # ── Palette propagation ────────────────────────────────────────────

    def _push_palette(self, palette: dict[str, str]) -> None:
        """Push palette update to all consuming features."""
        self._scrutinium.set_palette(palette)
        self._specularium.set_palette(palette)
        self._bibliotheca.set_current_palette(palette)

    def _on_palette_changed(self, palette: dict[str, str]) -> None:
        self._push_palette(palette)

    # ── Ratification pipeline ──────────────────────────────────────────

    def _on_ratify(self, palette: dict[str, str]) -> None:
        """Full ratification: seal → designator → export → registry."""
        record     = make_ratification_record(palette)
        designator = record["designator"]
        seal       = record["seal"]
        nomina     = record["nomina"]
        seal_trunc = seal[:8] + "…"

        # Check for duplicate seal before attempting insert
        existing = db.fetch_by_seal(seal)
        if existing:
            self.set_status(
                f"Already ratified  ·  {existing['designator']}  ·  {seal_trunc}",
                "This palette is already in the Registry — Promulgare to re-export.",
            )
            self.update_theme_state(existing["designator"], seal_trunc)
            return

        try:
            db.insert_palette(record)
        except Exception as e:
            self.set_status(f"⚑ Registry error: {e}", "")
            return

        # Full export
        try:
            paths = ratification_export(palette, designator, seal, nomina)
        except Exception as e:
            self.set_status(f"⚑ Export error: {e}", "")
            return

        # Update Titulum
        seal_trunc = seal[:8] + "…"
        self.update_theme_state(designator, seal_trunc)

        # Update status
        self.set_status(
            f"Ratificatio  ·  {designator}  ·  {seal_trunc}",
            f"theme.json written · {paths['export_dir']}",
        )

        # Refresh registry
        self._registrum.refresh()

        # Emit to NUNTIUS
        emit_event("theme_ratified", {
            "designator": designator,
            "seal": seal,
            "seal_truncated": seal_trunc,
            "tokens": palette,
        })

    def _on_promulgate(self, palette: dict[str, str]) -> None:
        """Export without sealing — no registry entry."""
        from AuctoritasSpectralis.export.theme_json import (
            write_qss, write_markdown, write_css
        )
        from pathlib import Path

        designator = assign_designator(palette)
        seal       = compute_seal(palette)
        nomina     = generate_nomina(palette)
        export_dir = Path(cfg.get("export_directory", str(Path.home() / "exports")))

        write_qss(palette, designator, export_dir)
        write_markdown(palette, designator, seal, nomina, export_dir)
        write_css(palette, designator, export_dir)

        self.set_status(f"Promulgare  ·  {designator}  (not ratified)", str(export_dir))

    # ── Save / Load ────────────────────────────────────────────────────

    def _on_save_draft(self, palette: dict[str, str]) -> None:
        # Write to temp draft file
        import json
        from pathlib import Path
        draft = cfg.ARCA_DIR / "colores_draft.json"
        draft.write_text(json.dumps(palette, indent=2), encoding="utf-8")
        self.set_status("Servare  ·  Draft saved.", str(draft))

    def _on_load_from_bibliotheca(self) -> None:
        """Switch to Bibliotheca for the Wizard to pick a palette."""
        self.select_feature(3)
        self._bibliotheca.refresh(self._colores.get_palette())
        self.set_status("Select a palette from the Bibliotheca to load.", "")

    def _on_new_palette(self) -> None:
        from AuctoritasSpectralis.features.colores import DEFAULT_PALETTE
        self._colores.load_palette(dict(DEFAULT_PALETTE))
        self.set_status("Novum  ·  New palette.", "")

    # ── Bibliotheca actions ────────────────────────────────────────────

    def _on_bibliotheca_load(self, tokens: dict[str, str]) -> None:
        if not tokens:
            return
        self._colores.load_palette(tokens)
        self._push_palette(tokens)
        self.select_feature(0)
        self.set_status("Onerare  ·  Palette loaded into Colores.", "")

    def _on_bibliotheca_fork(self, tokens: dict[str, str]) -> None:
        if not tokens:
            return
        # Load base pair only; let Colores re-derive
        fork = {"c_bg": tokens.get("c_bg", "#050507"),
                "c_gold": tokens.get("c_gold", "#d4af37")}
        from AuctoritasSpectralis.features.colores import DEFAULT_PALETTE
        forked = dict(DEFAULT_PALETTE)
        forked.update(fork)
        self._colores.load_palette(forked)
        self.select_feature(0)
        self.set_status("Ramificare  ·  Forked. Lead Pair preserved. Re-derive to continue.", "")

    def _on_bibliotheca_compare(self, selected: dict, current: dict) -> None:
        # Push selected to Scrutinium for side-by-side reference
        # (Full compare UI is a future scope item)
        self.set_status(
            "Comparare  ·  Selected palette pushed to Scrutinium.",
            "Full compare surface: future scope.",
        )
        if selected.get("tokens"):
            self._scrutinium.set_palette(selected["tokens"])
        self.select_feature(1)

    # ── Export helpers ─────────────────────────────────────────────────

    def _on_export_contrast_report(self, palette: dict[str, str]) -> None:
        from AuctoritasSpectralis.engine.contrast import score_matrix
        from pathlib import Path
        import datetime

        matrix  = score_matrix(palette)
        export_dir = Path(cfg.get("export_directory", str(Path.home() / "exports")))
        export_dir.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# Contrast Report",
            f"Generated: {datetime.datetime.now().isoformat(timespec='seconds')}",
            f"",
            f"| FG | BG | WCAG 2.1 | AA | AAA | APCA Lc | ΔE | Lum | Chroma Δ | Hue Δ |",
            f"|---|---|---|---|---|---|---|---|---|---|",
        ]
        for (fg, bg), scores in matrix.items():
            lines.append(
                f"| {fg} | {bg} | {scores['wcag21']:.2f} | "
                f"{'✓' if scores['wcag21_aa'] else '✗'} | "
                f"{'✓' if scores['wcag21_aaa'] else '✗'} | "
                f"{scores['apca_lc']:.1f} | {scores['delta_e']:.1f} | "
                f"{scores['luminance_ratio']:.2f} | {scores['chroma_distance']:.4f} | "
                f"{scores['hue_distance']:.1f}° |"
            )

        report_path = export_dir / "contrast_report.md"
        report_path.write_text("\n".join(lines), encoding="utf-8")
        self.set_status(f"Contrast report exported.", str(report_path))

    def _on_export_registry(self) -> None:
        from pathlib import Path
        import csv, datetime

        export_dir = Path(cfg.get("export_directory", str(Path.home() / "exports")))
        export_dir.mkdir(parents=True, exist_ok=True)
        records = db.fetch_all()

        # CSV export
        csv_path = export_dir / "chromatic_registry.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "designator", "sealed_at", "seal",
                             "wcag_min", "apca_min", "aa_pass", "aaa_pass", "notes"])
            for r in records:
                writer.writerow([
                    r["id"], r["designator"], r["sealed_at"], r["seal"][:16] + "…",
                    r["wcag_min"], r["apca_min"],
                    "✓" if r["aa_pass"] else "✗",
                    "✓" if r["aaa_pass"] else "✗",
                    r.get("notes", ""),
                ])

        self.set_status(f"Registry exported — {len(records)} records.", str(csv_path))

    # ── CONFIGURATIO ──────────────────────────────────────────────────

    def _on_config_requested(self) -> None:
        self._configuratio.setGeometry(self.canvas.geometry())
        self._configuratio.open_modal()

    def _on_config_saved(self, updated: dict) -> None:
        self.set_status("Configuratio saved.", "")

    def _on_config_closed(self) -> None:
        pass

    def _on_canvas_resize(self, event) -> None:
        if hasattr(self, "_configuratio"):
            self._configuratio.resize(self.canvas.size())

    # ── Inductio Chromatica ────────────────────────────────────────────

    def _check_ceremony(self) -> None:
        if not cfg.inductio_completed():
            self._run_ceremony()

    def _run_ceremony(self) -> None:
        from AuctoritasSpectralis.ceremony.inductio import InductioDirector

        # Collect Titulum labels for fade-in
        titulum_labels = [
            self.titulum._title_lbl,
            self.titulum._english_lbl,
            self.titulum._motto_lbl,
        ]

        # Hide all token rows initially
        self._colores.hide_all_token_rows()

        director = InductioDirector(titulum_labels, self)
        director.codex_light.connect(self._ceremony_light_codex)
        director.show_canvas.connect(self._ceremony_show_canvas)
        director.token_appear.connect(self._colores.reveal_token_row)
        director.ceremony_complete.connect(self._ceremony_complete)

        director.begin()
        self._ceremony_director = director  # keep alive

    def _ceremony_light_codex(self, index: int) -> None:
        """Light up codex items one by one during ceremony."""
        pass  # The codex items are always visible; ceremony effect is additive

    def _ceremony_show_canvas(self) -> None:
        self.select_feature(0)

    def _ceremony_complete(self) -> None:
        self.set_status("✦ Inductio Chromatica — complete.", "Auctoritas Spectralis · v1.0.0")
