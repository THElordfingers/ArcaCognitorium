# info.py — Vigilarum Omnia v2
# Floating info window. Tree on left, text display on right.
# General system writeups + live widget context.
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QTreeWidget, QTreeWidgetItem, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from data import (
    WIDGET_REGISTRY, WIDGET_CATEGORIES, WIDGET_BY_ID, INFO_GENERAL,
    C_BG, C_PANEL, C_BORDER, C_GOLD, C_GOLD_DIM,
    C_TEXT, C_TEXT_DIM, C_TEAL, FONT_BODY, FONT_SIZE, FONT_SMALL, FONT_TITLE,
)
from state import read_state, read_display, widget_assignments
from data import MAX_DISPLAYS

SS = f"""
QMainWindow,QWidget{{background:{C_BG};color:{C_TEXT};font-family:Georgia;font-size:10pt;}}
QTreeWidget{{background:{C_PANEL};border:none;color:{C_TEXT};}}
QTreeWidget::item{{padding:3px;}}
QTreeWidget::item:selected{{background:{C_GOLD_DIM};color:{C_TEXT};}}
QTreeWidget::item:hover{{background:#1A1A2A;}}
QScrollArea{{border:none;background:{C_BG};}}
QScrollBar:vertical{{background:{C_BG};width:8px;border:none;}}
QScrollBar::handle:vertical{{background:{C_GOLD_DIM};border-radius:4px;min-height:20px;}}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}
"""


def _lbl(text, size=FONT_SIZE, color=C_TEXT, bold=False):
    l=QLabel(text); l.setFont(QFont(FONT_BODY,size,QFont.Weight.Bold if bold else QFont.Weight.Normal))
    l.setStyleSheet(f"color:{color};background:transparent;"); l.setWordWrap(True)
    return l


class InfoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vigilarum Omnia \u2014 Information")
        self.setMinimumSize(780, 560)
        self._last_assignments = {}
        self._build_ui(); self.setStyleSheet(SS)
        self._populate_tree()
        t=QTimer(self); t.setInterval(2_000); t.timeout.connect(self._refresh_live); t.start()

    def _build_ui(self):
        central=QWidget(); self.setCentralWidget(central)
        root=QVBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        # header
        hdr=QWidget(); hdr.setFixedHeight(48); hdr.setStyleSheet(f"background:{C_PANEL};")
        hl=QHBoxLayout(hdr); hl.setContentsMargins(16,0,16,0)
        hl.addWidget(_lbl("VIGILARUM INFORMATION", 14, C_GOLD, bold=True)); hl.addStretch()
        root.addWidget(hdr)
        div=QFrame(); div.setFixedHeight(1); div.setStyleSheet(f"background:{C_GOLD_DIM};")
        root.addWidget(div)
        # body
        body=QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        # tree
        self._tree=QTreeWidget(); self._tree.setHeaderHidden(True)
        self._tree.setFixedWidth(260); self._tree.setIndentation(14)
        self._tree.currentItemChanged.connect(self._on_select)
        body.addWidget(self._tree)
        vdiv=QFrame(); vdiv.setFixedWidth(1); vdiv.setStyleSheet(f"background:{C_GOLD_DIM};")
        body.addWidget(vdiv)
        # text pane
        right=QWidget(); rl=QVBoxLayout(right); rl.setContentsMargins(0,0,0,0); rl.setSpacing(0)
        self._title_lbl=_lbl("", 14, C_GOLD, bold=True)
        self._title_lbl.setContentsMargins(16,12,16,4); right.layout().addWidget(self._title_lbl)
        tdiv=QFrame(); tdiv.setFixedHeight(1); tdiv.setStyleSheet(f"background:{C_GOLD_DIM};")
        right.layout().addWidget(tdiv)
        scroll=QScrollArea(); scroll.setWidgetResizable(True)
        self._text_widget=QWidget(); tl=QVBoxLayout(self._text_widget)
        tl.setContentsMargins(16,12,16,16); tl.setSpacing(8); tl.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._text_labels=[]
        for _ in range(20):
            l=_lbl("",FONT_SIZE,C_TEXT); self._text_labels.append(l); tl.addWidget(l)
        tl.addStretch()
        scroll.setWidget(self._text_widget); right.layout().addWidget(scroll)
        body.addWidget(right, stretch=1)
        root.addLayout(body, stretch=1)

    def _populate_tree(self):
        self._tree.clear()
        # General systems
        general_root=QTreeWidgetItem(self._tree,["General Information"])
        general_root.setFont(0,QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
        general_root.setForeground(0,QColor(C_GOLD))
        for title in INFO_GENERAL:
            item=QTreeWidgetItem(general_root,[title])
            item.setData(0,Qt.ItemDataRole.UserRole,("general",title))
            item.setForeground(0,QColor(C_TEXT_DIM))
        general_root.setExpanded(True)
        # Widget categories
        widget_root=QTreeWidgetItem(self._tree,["Widgets"])
        widget_root.setFont(0,QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
        widget_root.setForeground(0,QColor(C_GOLD))
        by_cat={}
        for wid,name,ctype,cat in WIDGET_REGISTRY:
            by_cat.setdefault(cat,[]).append((wid,name))
        for cat in WIDGET_CATEGORIES:
            items=by_cat.get(cat,[])
            if not items: continue
            cat_item=QTreeWidgetItem(widget_root,[cat])
            cat_item.setForeground(0,QColor(C_TEAL))
            cat_item.setFont(0,QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
            for wid,name in items:
                w=QTreeWidgetItem(cat_item,[name])
                w.setData(0,Qt.ItemDataRole.UserRole,("widget",wid))
                w.setForeground(0,QColor(C_TEXT_DIM))
        widget_root.setExpanded(True)
        # Live assignments
        self._live_root=QTreeWidgetItem(self._tree,["Currently Displayed"])
        self._live_root.setFont(0,QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
        self._live_root.setForeground(0,QColor(C_GOLD))
        self._tree.addTopLevelItem(self._live_root)
        self._refresh_live()

    def _refresh_live(self):
        assignments=widget_assignments()
        if assignments==self._last_assignments: return
        self._last_assignments=assignments
        while self._live_root.childCount():
            self._live_root.removeChild(self._live_root.child(0))
        state=read_state()
        for wid,displays in sorted(assignments.items(),key=lambda x:x[0]):
            entry=WIDGET_BY_ID.get(wid)
            if not entry: continue
            name=entry[1]
            disp_str=", ".join(f"D{d}" for d in displays)
            item=QTreeWidgetItem(self._live_root,[f"{name}  \u2014  {disp_str}"])
            item.setData(0,Qt.ItemDataRole.UserRole,("widget_live",wid))
            item.setForeground(0,QColor(C_TEAL))
        self._live_root.setExpanded(bool(assignments))

    def _on_select(self, current, _):
        if current is None: return
        data=current.data(0,Qt.ItemDataRole.UserRole)
        if data is None: return
        kind,key=data
        if kind=="general":
            self._show_general(key)
        elif kind in ("widget","widget_live"):
            self._show_widget(key)

    def _show_general(self, title):
        self._title_lbl.setText(title)
        text=INFO_GENERAL.get(title,"No information available.")
        self._set_text([text])

    def _show_widget(self, wid):
        entry=WIDGET_BY_ID.get(wid)
        if not entry: return
        _,name,ctype,cat=entry
        self._title_lbl.setText(name)
        state=read_state()
        lines=[]
        lines.append(f"Category: {cat}")
        lines.append(f"Type: {'Visual (painted)' if ctype=='visual' else 'Text (labels)'}")
        lines.append(f"Widget ID: {wid}")
        lines.append("")
        # General description from INFO_GENERAL if available
        for key in INFO_GENERAL:
            if key.lower() in name.lower() or name.lower() in key.lower():
                lines.append(INFO_GENERAL[key]); lines.append("")
                break
        # Live state context
        if state:
            lines.append("\u2500 Live State \u2500")
            lines.append(self._live_context(wid, state))
        else:
            lines.append("No live state available \u2014 control panel not running.")
        self._set_text(lines)

    def _live_context(self, wid, state) -> str:
        if wid.startswith("planet_"):
            k=wid.replace("planet_","")
            sign=state.get(f"{k}_sign","—"); dms=state.get(f"{k}_dms","—")
            nak=state.get(f"{k}_nakshatra","—"); lord=state.get(f"{k}_nak_lord","—")
            retro=state.get(f"{k}_retrograde",False)
            r=" (retrograde)" if retro else ""
            return f"{k.capitalize()} is in {sign} at {dms}{r}. Nakshatra: {nak}, ruled by {lord}."
        if wid.startswith("node_"):
            k="rahu" if "rahu" in wid else "ketu"
            sign=state.get(f"{k}_sign","—"); dms=state.get(f"{k}_dms","—")
            nak=state.get(f"{k}_nakshatra","—")
            node_name="Rahu (North Node)" if k=="rahu" else "Ketu (South Node)"
            return f"{node_name} is in {sign} at {dms}. Nakshatra: {nak}. Always retrograde."
        if wid=="panchang_tithi":
            return (f"Current Tithi: {state.get('tithi_name','—')} ({state.get('tithi_num','—')} of 30). "
                    f"{state.get('tithi_progress',0):.1f}% elapsed. "
                    f"{'Waxing (Shukla Paksha)' if state.get('tithi_num',1)<=15 else 'Waning (Krishna Paksha)'}.")
        if wid=="panchang_vara":
            return (f"Today is {state.get('vara_name','—')}, ruled by {state.get('vara_lord','—')}.")
        if wid=="panchang_nakshatra":
            return (f"Moon is in {state.get('nakshatra_name','—')}, ruled by {state.get('nakshatra_lord','—')}. "
                    f"{state.get('nakshatra_progress',0):.1f}% through this nakshatra.")
        if wid=="panchang_yoga":
            return f"Current Yoga: {state.get('yoga_name','—')} ({state.get('yoga_index',0)+1} of 27)."
        if wid=="panchang_karana":
            return f"Current Karana: {state.get('karana_name','—')}."
        if wid=="time_rahu_kalam":
            active=state.get("rahu_kalam_active",False)
            s=state.get("rahu_kalam_start","—"); e=state.get("rahu_kalam_end","—")
            return (f"Today's Rahu Kalam window: {s} \u2014 {e}. "
                    ('Currently ACTIVE — inauspicious period.' if active else 'Currently inactive.'))
        if wid=="time_planetary_hour":
            return (f"Current planetary hour is ruled by {state.get('planetary_hour_planet','—')} "
                    f"({state.get('planetary_hour_start','')} \u2014 {state.get('planetary_hour_end','')}). "
                    f"Hour {state.get('planetary_hour_num','—')} of 24.")
        if wid=="time_sunrise_set":
            return f"Sunrise: {state.get('sunrise','—')}. Sunset: {state.get('sunset','—')}. Day length: {state.get('day_length','—')}."
        if wid=="lunar_phase_text":
            return (f"Moon is {state.get('moon_phase_name','—')} at {state.get('moon_illumination',0):.1f}% illumination. "
                    f"{'Waxing' if state.get('moon_waxing') else 'Waning'}. "
                    f"Moon\u2013Sun angle: {state.get('moon_phase_angle',0):.2f}\u00b0.")
        if wid=="summary_eclipse":
            risk=state.get("eclipse_risk","—"); nd=state.get("eclipse_nearest","—")
            md=state.get("eclipse_min_dist",0)
            return (f"Eclipse risk: {risk}. Moon is {md:.1f}\u00b0 from {nd}. "
                    f"High risk occurs when Moon is within 12\u00b0 of a node at a new or full moon.")
        if wid=="season_current":
            return (f"Currently {state.get('season','—')}. {state.get('season_register','')} "
                    f"Approximately {state.get('season_days_to_next','—')} days until {state.get('season_next','—')}.")
        if wid=="moon_distance_gauge":
            return (f"Moon is {int(state.get('moon_distance_km',0)):,} km away. "
                    f"Currently near {'perigee (closest)' if state.get('moon_proximity')=='Perigee' else 'apogee (furthest)'}. "
                    f"{state.get('moon_distance_pct',0):.1f}% of the way from perigee to apogee.")
        return "Live data available \u2014 see widget for current values."

    def _set_text(self, lines):
        for i, lbl in enumerate(self._text_labels):
            if i < len(lines):
                lbl.setText(lines[i])
                color = C_TEXT_DIM if (lines[i].startswith("\u2500") or lines[i].startswith("Category:") or lines[i].startswith("Type:")) else C_TEXT
                lbl.setStyleSheet(f"color:{color};background:transparent;")
            else:
                lbl.setText("")


def main():
    app=QApplication(sys.argv)
    pal=QPalette(); pal.setColor(QPalette.ColorRole.Window,QColor(C_BG))
    pal.setColor(QPalette.ColorRole.WindowText,QColor(C_TEXT)); app.setPalette(pal)
    w=InfoWindow(); w.show(); sys.exit(app.exec())

if __name__=="__main__":
    main()
