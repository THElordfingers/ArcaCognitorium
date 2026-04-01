#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widgets/referentia_aggregator.py                               ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/referentia_aggregator.py
# Lore/build node search surface.
# Primary: Exocognii FastAPI service (/lore/search, /build/nodi)
# Fallback: local file search against repo Referentia/ and entity files.
# version: 1.0.0

import json
import threading
from pathlib import Path

from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QLineEdit, QScrollArea, QWidget, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from widget_base import ArcaneWidget
from configuus import Configuus
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_PANEL,
    C_TEAL, C_CRIMSON, C_WHITE,
    arcane_button, micro_label,
)


# ---------------------------------------------------------------------------
# Signal relay for thread safety
# ---------------------------------------------------------------------------

class _Relay(QObject):
    results_ready = pyqtSignal(list)    # list of result dicts
    error         = pyqtSignal(str)


# ---------------------------------------------------------------------------
# ReferentiaAggregator
# ---------------------------------------------------------------------------

class ReferentiaAggregator(ArcaneWidget):
    """
    Search surface for Referentia files and Exocognii lore/build nodes.

    When the Exocognii FastAPI service is available (configuus.praesidium_api),
    queries are forwarded to /lore/search and /build/nodi.

    When the service is offline, falls back to local file search:
    - repo/Referentia/**/*.{md,txt,wiz,yaml,json}
    - repo/entities/**/*.yaml
    """

    result_selected = pyqtSignal(str, str)   # title, content

    def __init__(self, widget_id: str, configuus: Configuus, parent=None):
        super().__init__(widget_id, "Referentia", parent)
        self._cfg    = configuus
        self._relay  = _Relay()
        self._relay.results_ready.connect(self._show_results)
        self._relay.error.connect(self._show_error)
        self._build_body()
        self.set_status("idle", "")

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Search input
        row = QHBoxLayout()
        row.setSpacing(6)
        self._input = QLineEdit()
        self._input.setPlaceholderText("Search lore, nodes, referentia…")
        self._input.setStyleSheet(
            f"QLineEdit {{ background: {C_BG}; color: {C_TEXT};"
            f"  border: 1px solid {C_GOLD_DARK}; font-family: Georgia, serif;"
            f"  font-size: 11px; padding: 5px 8px; }}"
            f"QLineEdit:focus {{ border-color: {C_GOLD}; }}"
        )
        self._input.returnPressed.connect(self._do_search)
        row.addWidget(self._input, 1)

        btn_search = arcane_button("⚙ SEARCH")
        btn_search.setFixedHeight(26)
        btn_search.clicked.connect(self._do_search)
        row.addWidget(btn_search)
        L.addLayout(row)

        # Service status indicator
        self._svc_lbl = QLabel("● local")
        self._svc_lbl.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: 9px;"
        )
        L.addWidget(self._svc_lbl)
        L.addWidget(self._sep())

        # Results area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: {C_BG}; }}"
        )
        self._results_widget = QWidget()
        self._results_widget.setStyleSheet(f"background: {C_BG};")
        self._results_layout = QVBoxLayout(self._results_widget)
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(2)
        self._results_layout.addStretch()
        self._scroll.setWidget(self._results_widget)
        L.addWidget(self._scroll, 1)

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    # ------------------------------------------------------------------
    # Search dispatch
    # ------------------------------------------------------------------

    def _do_search(self) -> None:
        query = self._input.text().strip()
        if not query:
            return

        self.set_status("warn", "Searching…")
        self._clear_results()

        # Try service first, fall back to local
        svc_url = self._cfg.praesidium_api
        threading.Thread(
            target=self._search_thread,
            args=(query, svc_url),
            daemon=True,
        ).start()

    def _search_thread(self, query: str, svc_url: str) -> None:
        results = []

        # Try Exocognii service
        service_ok = False
        try:
            import urllib.request
            import urllib.parse
            q = urllib.parse.quote(query)

            # Query Perpetuum Aedificare — build nodes
            perp_url = self._cfg.perpetuum_aedificare_api
            pa_url = f"{perp_url}/nodi?limit=10"
            with urllib.request.urlopen(pa_url, timeout=3) as resp:
                data = json.loads(resp.read())
                for item in data.get("results", [])[:10]:
                    title = item.get("title", "—")
                    nodifex = item.get("nodifex", "")
                    if query.lower() in title.lower() or query.lower() in nodifex.lower():
                        results.append({
                            "title":   f"[node] {title}",
                            "snippet": nodifex[:200] if nodifex else item.get("nodicum", ""),
                            "source":  "perpetuum",
                            "path":    item.get("id", ""),
                        })

            # Query Exvacua Loricum — lore fragments
            exv_url = self._cfg.exvacua_loricum_api
            el_url = f"{exv_url}/lorixii?limit=10&status=consumed"
            with urllib.request.urlopen(el_url, timeout=3) as resp:
                data = json.loads(resp.read())
                for item in data.get("results", [])[:10]:
                    raw = item.get("raw_content", "")
                    if query.lower() in raw.lower():
                        idx = raw.lower().find(query.lower())
                        start = max(0, idx - 60)
                        snippet = "…" + raw[start:start+180].strip() + "…"
                        results.append({
                            "title":   f"[lore] {item.get('source_ref', '—')}",
                            "snippet": snippet,
                            "source":  "exvacua",
                            "path":    item.get("id", ""),
                        })

            service_ok = bool(results) or True  # connected even if no hits
        except Exception:
            pass

        # Local fallback
        if not service_ok:
            results = self._local_search(query)

        self._relay.results_ready.emit(results)
        status = "perpetuum/exvacua" if service_ok else "local"
        # Update indicator from main thread via signal
        self._relay.error.emit(f"__STATUS__{status}")

    def _local_search(self, query: str) -> list[dict]:
        results = []
        repo = self._cfg.arca_repo_path
        query_lower = query.lower()

        search_roots = [
            repo / "Referentia",
            repo / "entities",
            repo / "memory",
        ]
        extensions = {".md", ".txt", ".yaml", ".json", ".wiz"}

        for root in search_roots:
            if not root.exists():
                continue
            for p in root.rglob("*"):
                if p.suffix not in extensions:
                    continue
                if p.stat().st_size > 500_000:
                    continue
                try:
                    text = p.read_text(errors="replace")
                except Exception:
                    continue

                if query_lower not in text.lower():
                    continue

                # Find snippet around match
                idx    = text.lower().find(query_lower)
                start  = max(0, idx - 60)
                end    = min(len(text), idx + 120)
                snippet = "…" + text[start:end].strip() + "…"

                results.append({
                    "title":   p.name,
                    "snippet": snippet,
                    "source":  "local",
                    "path":    str(p),
                })

                if len(results) >= 30:
                    break
            if len(results) >= 30:
                break

        return results

    # ------------------------------------------------------------------
    # Results display
    # ------------------------------------------------------------------

    def _clear_results(self) -> None:
        while self._results_layout.count() > 1:
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_results(self, results: list) -> None:
        self._clear_results()
        self.set_status("ok", f"{len(results)} result(s)")

        if not results:
            lbl = QLabel("— no results —")
            lbl.setStyleSheet(
                f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
                "font-size: 10px; font-style: italic;"
            )
            self._results_layout.insertWidget(0, lbl)
            return

        for i, r in enumerate(results):
            card = self._make_result_card(r)
            self._results_layout.insertWidget(i, card)

    def _show_error(self, msg: str) -> None:
        if msg.startswith("__STATUS__"):
            status = msg[len("__STATUS__"):]
            colour = C_TEAL if status == "service" else C_GOLD_DIM
            self._svc_lbl.setText(f"● {status}")
            self._svc_lbl.setStyleSheet(
                f"color: {colour}; font-family: Georgia, serif; font-size: 9px;"
            )
            return
        self.set_status("error", msg[:60])

    def _make_result_card(self, r: dict) -> QWidget:
        card = QWidget()
        card.setStyleSheet(
            f"QWidget {{ background: {C_PANEL}; border: 1px solid {C_GOLD_DARK}; }}"
            f"QWidget:hover {{ border-color: {C_GOLD}; }}"
        )
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(8, 6, 8, 6)
        vbox.setSpacing(2)

        # Title row
        title_row = QHBoxLayout()
        title_lbl = QLabel(r["title"])
        title_lbl.setStyleSheet(
            f"color: {C_GOLD}; font-family: Georgia, serif; "
            "font-size: 10px; font-weight: bold;"
        )
        title_row.addWidget(title_lbl)
        title_row.addStretch()

        src_colour = C_TEAL if r.get("source") == "service" else C_GOLD_DIM
        src_lbl = QLabel(r.get("source", ""))
        src_lbl.setStyleSheet(
            f"color: {src_colour}; font-family: Georgia, serif; font-size: 9px;"
        )
        title_row.addWidget(src_lbl)
        vbox.addLayout(title_row)

        # Snippet
        if r.get("snippet"):
            snip = QLabel(r["snippet"][:200])
            snip.setWordWrap(True)
            snip.setStyleSheet(
                f"color: {C_TEXT}; font-family: Georgia, serif; font-size: 10px;"
            )
            vbox.addWidget(snip)

        # Path (if local)
        if r.get("path") and r.get("source") == "local":
            path_lbl = QLabel(r["path"])
            path_lbl.setStyleSheet(
                f"color: {C_GOLD_DARK}; font-family: 'Courier New', monospace; font-size: 9px;"
            )
            vbox.addWidget(path_lbl)

        # Click → emit result_selected
        path_str    = r.get("path", "")
        title_str   = r["title"]
        snippet_str = r.get("snippet", "")

        def on_click(event, t=title_str, c=snippet_str):
            self.result_selected.emit(t, c)

        card.mousePressEvent = on_click

        return card
