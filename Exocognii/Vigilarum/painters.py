# painters.py — Vigilarum Omnia v2
# Pure QPainter functions. (QPainter, QRectF, state|None) -> None
import math
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont,
                          QRadialGradient, QPainterPath)
from data import (SIGNS, SIGN_SYMBOLS, NAKSHATRAS, BODY_COLOURS, BODY_SYMBOLS,
                  C_BG, C_PANEL, C_BORDER, C_GOLD, C_GOLD_DIM,
                  C_TEXT, C_TEXT_DIM, C_TEAL, C_RED, C_GREEN, C_WHITE,
                  FONT_BODY, FONT_SIZE, FONT_SMALL)

AWAIT = "Awaiting data\u2026"

def _cx(r): return r.x() + r.width()/2
def _cy(r): return r.y() + r.height()/2
def _r(r, f=0.45): return min(r.width(), r.height()) * f
def _polar(cx, cy, r, deg):
    rad = math.radians(deg - 90)
    return QPointF(cx + r*math.cos(rad), cy + r*math.sin(rad))
def _pen(p, color, w=1.0):
    pen = QPen(QColor(color)); pen.setWidthF(w); p.setPen(pen)
def _await(p, rect):
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY, FONT_SMALL))
    p.drawText(rect, Qt.AlignmentFlag.AlignCenter, AWAIT)


def draw_moon_disc(p, rect, state):
    if state is None: _await(p, rect); return
    illum  = state.get("moon_illumination", 0.0) / 100.0
    waxing = state.get("moon_waxing", True)
    phase  = state.get("moon_phase_name", "")
    cx = _cx(rect); cy = _cy(rect); r = _r(rect, 0.40)
    disc = QRectF(cx-r, cy-r, r*2, r*2)
    # dark base
    p.setBrush(QBrush(QColor("#1A1A2E")))
    p.setPen(QPen(QColor(C_BORDER), 1.0)); p.drawEllipse(disc)
    p.save()
    clip = QPainterPath(); clip.addEllipse(disc); p.setClipPath(clip)
    grad = QRadialGradient(cx, cy, r)
    grad.setColorAt(0.0, QColor("#F0E8C0")); grad.setColorAt(0.7, QColor("#C8A84B"))
    grad.setColorAt(1.0, QColor("#7A6530"))
    p.setBrush(QBrush(grad)); p.setPen(Qt.PenStyle.NoPen)
    term_x = abs(illum*2-1); term_w = r*2*term_x
    if illum < 0.5:
        lx = cx+r if waxing else cx-r
        p.drawEllipse(QRectF(lx-r, cy-r, r*2, r*2))
        p.setBrush(QBrush(QColor("#1A1A2E")))
        p.drawEllipse(QRectF(cx-term_w/2, cy-r, term_w, r*2))
    else:
        p.drawEllipse(disc)
        dx = cx-r if waxing else cx+r
        p.setBrush(QBrush(QColor("#1A1A2E"))); p.drawEllipse(QRectF(dx, cy-r, r*2, r*2))
        p.setBrush(QBrush(grad)); p.drawEllipse(QRectF(cx-term_w/2, cy-r, term_w, r*2))
    p.restore()
    _pen(p, C_BORDER, 1.0); p.setBrush(Qt.BrushStyle.NoBrush); p.drawEllipse(disc)
    # illumination label inside disc
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY, FONT_SMALL-1))
    p.drawText(QRectF(cx-40, cy-8, 80, 16), Qt.AlignmentFlag.AlignCenter,
               f"{state.get('moon_illumination',0):.0f}% illuminated")
    # phase name below disc with padding
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY, FONT_SMALL))
    p.drawText(QRectF(rect.x(), cy+r+8, rect.width(), 18), Qt.AlignmentFlag.AlignCenter, phase)


def draw_zodiac_wheel(p, rect, state):
    if state is None: _await(p, rect); return
    cx=_cx(rect); cy=_cy(rect); r=_r(rect, 0.44)
    or_=r; sr=r*0.82; ir=r*0.65; pr=r*0.50
    p.setBrush(QBrush(QColor(C_PANEL))); p.setPen(QPen(QColor(C_BORDER),1.0))
    p.drawEllipse(QRectF(cx-or_,cy-or_,or_*2,or_*2))
    p.setBrush(QBrush(QColor(C_BG))); p.setPen(QPen(QColor(C_GOLD_DIM),0.5))
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    for i in range(12):
        ang = i*30.0
        _pen(p, C_GOLD_DIM, 0.5)
        p.drawLine(_polar(cx,cy,ir,ang), _polar(cx,cy,or_,ang))
        mid = _polar(cx,cy,sr,ang+15)
        p.setPen(QColor(C_GOLD_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
        p.drawText(QRectF(mid.x()-10,mid.y()-8,20,16), Qt.AlignmentFlag.AlignCenter, SIGN_SYMBOLS[i])
    # bodies
    bodies = ["sun","moon","mars","mercury","jupiter","venus","saturn","rahu","ketu",
              "uranus","neptune","pluto"]
    for key in bodies:
        lon = state.get(f"{key}_lon")
        if lon is None: continue
        color = BODY_COLOURS.get(key, C_TEXT_DIM)
        sym   = BODY_SYMBOLS.get(key, "?")
        pt = _polar(cx,cy,pr,lon)
        p.setPen(QColor(color)); p.setBrush(QBrush(QColor(color)))
        p.drawEllipse(QRectF(pt.x()-3,pt.y()-3,6,6))
        p.setFont(QFont(FONT_BODY,FONT_SMALL-2))
        p.drawText(QRectF(pt.x()+4,pt.y()-6,14,12), Qt.AlignmentFlag.AlignLeft, sym)
    # legend note
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-2))
    p.drawText(QRectF(rect.x(),rect.y()+rect.height()-14,rect.width(),14),
               Qt.AlignmentFlag.AlignCenter, "Vedic sidereal \u2014 Lahiri ayanamsha")


def draw_moon_arc(p, rect, state):
    if state is None: _await(p, rect); return
    illum = state.get("moon_illumination", 0.0)
    phase = state.get("moon_phase_name", "")
    angle = state.get("moon_phase_angle", 0.0); pct = angle/360.0
    cx=_cx(rect); cy=_cy(rect); r=_r(rect,0.38)
    start=-210.0; span=240.0
    _pen(p, C_GOLD_DIM, 3.0); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawArc(QRectF(cx-r,cy-r,r*2,r*2), int(start*16), int(span*16))
    _pen(p, C_GOLD, 3.0)
    p.drawArc(QRectF(cx-r,cy-r,r*2,r*2), int(start*16), int(span*pct*16))
    for frac in [0.25, 0.5, 0.75]:
        deg = start + span*frac
        pt  = _polar(cx, cy, r, -deg)
        _pen(p, C_GOLD_DIM, 1.0)
        p.drawEllipse(QRectF(pt.x()-3,pt.y()-3,6,6))
    p.setPen(QColor(C_GOLD)); p.setFont(QFont(FONT_BODY,FONT_SIZE+2,QFont.Weight.Bold))
    p.drawText(QRectF(cx-50,cy-14,100,28), Qt.AlignmentFlag.AlignCenter, f"{illum:.0f}%")
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL))
    p.drawText(QRectF(cx-60,cy+14,120,18), Qt.AlignmentFlag.AlignCenter, "illumination")
    p.drawText(QRectF(cx-60,cy+28,120,18), Qt.AlignmentFlag.AlignCenter, phase)


def draw_nakshatra_ring(p, rect, state):
    if state is None: _await(p, rect); return
    ni = state.get("nakshatra_index", 0)
    cx=_cx(rect); cy=_cy(rect); r=_r(rect,0.44); ir=r*0.62
    seg = 360.0/27.0
    for i in range(27):
        c = QColor(C_GOLD if i==ni else C_GOLD_DIM)
        c.setAlpha(200 if i==ni else 60)
        p.setBrush(QBrush(c)); _pen(p, C_BG, 1.0)
        path = QPainterPath()
        path.moveTo(QPointF(cx,cy))
        path.arcTo(QRectF(cx-r,cy-r,r*2,r*2), 90-i*seg, -seg)
        path.closeSubpath(); p.drawPath(path)
    p.setBrush(QBrush(QColor(C_BG))); p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    _pen(p, C_BORDER, 1.0); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    p.setPen(QColor(C_GOLD)); p.setFont(QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
    p.drawText(QRectF(cx-ir,cy-10,ir*2,20), Qt.AlignmentFlag.AlignCenter, NAKSHATRAS[ni])
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
    p.drawText(QRectF(cx-ir,cy+10,ir*2,14), Qt.AlignmentFlag.AlignCenter, "Moon\u2019s nakshatra")


def draw_tithi_dial(p, rect, state):
    if state is None: _await(p, rect); return
    ti = state.get("tithi_index",0); tn = state.get("tithi_name","—")
    tp = state.get("tithi_progress",0.0)
    cx=_cx(rect); cy=_cy(rect); r=_r(rect,0.44); ir=r*0.55
    seg=360.0/30.0
    for i in range(30):
        if i==ti: color,alpha=C_GOLD,220
        elif i<15: color,alpha=C_TEAL,50
        else: color,alpha=C_GOLD_DIM,50
        c=QColor(color); c.setAlpha(alpha)
        p.setBrush(QBrush(c)); _pen(p, C_BG, 1.0)
        path=QPainterPath(); path.moveTo(QPointF(cx,cy))
        path.arcTo(QRectF(cx-r,cy-r,r*2,r*2),90-i*seg,-seg)
        path.closeSubpath(); p.drawPath(path)
    p.setBrush(QBrush(QColor(C_BG))); p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    _pen(p, C_BORDER, 1.0); p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
    p.drawEllipse(QRectF(cx-ir,cy-ir,ir*2,ir*2))
    p.setPen(QColor(C_GOLD)); p.setFont(QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
    p.drawText(QRectF(cx-ir,cy-16,ir*2,18), Qt.AlignmentFlag.AlignCenter, tn)
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
    p.drawText(QRectF(cx-ir,cy+2,ir*2,16), Qt.AlignmentFlag.AlignCenter, f"{tp:.0f}% elapsed")
    p.drawText(QRectF(cx-ir,cy+16,ir*2,14), Qt.AlignmentFlag.AlignCenter, "Lunar day")


def draw_eclipse_gauge(p, rect, state):
    if state is None: _await(p, rect); return
    dr = state.get("eclipse_dist_rahu",90.0); dk = state.get("eclipse_dist_ketu",90.0)
    risk = state.get("eclipse_risk","Low"); nearest = state.get("eclipse_nearest","Rahu")
    cx=_cx(rect); cy=_cy(rect)
    bw=rect.width()*0.78; bh=14; bx=cx-bw/2; by=cy-bh/2
    rc = C_RED if risk=="High" else (C_TEAL if risk=="Medium" else C_GOLD_DIM)
    p.setBrush(QBrush(QColor(C_PANEL))); _pen(p, C_GOLD_DIM, 1.0)
    p.drawRect(QRectF(bx,by,bw,bh))
    md=min(dr,dk); dp=max(0.0,min(1.0,1.0-(md/30.0))); fw=bw*dp
    c=QColor(rc); c.setAlpha(160)
    p.setBrush(QBrush(c)); p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(bx,by,fw,bh))
    tx=bx+bw*(1.0-12.0/30.0); _pen(p, C_GOLD_DIM, 1.0)
    p.drawLine(QPointF(tx,by-2),QPointF(tx,by+bh+2))
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL))
    p.drawText(QRectF(bx-50,by,48,bh), Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter,
               f"Rahu \u2212 {dr:.1f}\u00b0")
    p.drawText(QRectF(bx+bw+2,by,50,bh), Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,
               f"{dk:.1f}\u00b0 \u2212 Ketu")
    p.setPen(QColor(rc)); p.setFont(QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
    p.drawText(QRectF(cx-80,by+bh+6,160,18), Qt.AlignmentFlag.AlignCenter,
               f"{risk} eclipse risk \u00b7 Moon {md:.1f}\u00b0 from {nearest}")
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
    p.drawText(QRectF(cx-80,by+bh+22,160,14), Qt.AlignmentFlag.AlignCenter,
               "High risk < 12\u00b0 \u00b7 Medium < 20\u00b0")


def draw_planet_strip(p, rect, state):
    if state is None: _await(p, rect); return
    bodies = ["sun","moon","mars","mercury","jupiter","venus","saturn",
              "uranus","neptune","pluto","rahu","ketu"]
    n=len(bodies); lh=rect.height()/n; bm=48; bx=rect.x()+bm; bw=rect.width()-bm-8
    for i,key in enumerate(bodies):
        lon=state.get(f"{key}_lon")
        if lon is None: continue
        yc=rect.y()+lh*i+lh/2
        color=BODY_COLOURS.get(key,C_TEXT_DIM); sym=BODY_SYMBOLS.get(key,"?")
        name=key.capitalize()
        _pen(p, C_GOLD_DIM, 0.5)
        p.drawLine(QPointF(bx,yc),QPointF(bx+bw,yc))
        for deg in range(0,361,30):
            mx=bx+(deg/360.0)*bw
            p.drawLine(QPointF(mx,yc-3),QPointF(mx,yc+3))
        dx=bx+(lon/360.0)*bw
        p.setBrush(QBrush(QColor(color))); _pen(p,color,1.0)
        p.drawEllipse(QRectF(dx-4,yc-4,8,8))
        # name label left
        p.setPen(QColor(color)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
        p.drawText(QRectF(rect.x(),yc-8,bm-6,16),
                   Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter, name)
        # degree label right of dot
        si=int(lon/30); di=lon%30
        retro=state.get(f"{key}_retrograde",False)
        retro_str = ' ℞' if retro else ''
        lbl=f"{SIGN_SYMBOLS[si]}{di:.1f}\u00b0{retro_str}"
        p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-2))
        p.drawText(QRectF(dx+6,yc-8,60,16),
                   Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter, lbl)


def draw_moon_distance_gauge(p, rect, state):
    if state is None: _await(p, rect); return
    pct=state.get("moon_distance_pct",50.0)/100.0
    dist_km=state.get("moon_distance_km",384400)
    proximity=state.get("moon_proximity","—")
    cx=_cx(rect); gh=rect.height()*0.60; gw=18
    gx=cx-gw/2; gy=rect.y()+rect.height()*0.15
    p.setBrush(QBrush(QColor(C_PANEL))); _pen(p,C_GOLD_DIM,1.0)
    p.drawRect(QRectF(gx,gy,gw,gh))
    fh=gh*pct; fy=gy+gh-fh
    c=QColor(C_GOLD); c.setAlpha(140)
    p.setBrush(QBrush(c)); p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(gx,fy,gw,fh))
    _pen(p,C_GOLD,2.0); p.drawLine(QPointF(gx-6,fy),QPointF(gx+gw+6,fy))
    mid_y=gy+gh*0.5; _pen(p,C_GOLD_DIM,0.5)
    p.drawLine(QPointF(gx,mid_y),QPointF(gx+gw,mid_y))
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL))
    p.drawText(QRectF(cx-40,gy-18,80,16), Qt.AlignmentFlag.AlignCenter, "Apogee (far)")
    p.drawText(QRectF(cx-40,gy+gh+2,80,16), Qt.AlignmentFlag.AlignCenter, "Perigee (close)")
    p.setPen(QColor(C_GOLD)); p.setFont(QFont(FONT_BODY,FONT_SMALL,QFont.Weight.Bold))
    p.drawText(QRectF(cx-55,fy-20,110,18), Qt.AlignmentFlag.AlignCenter,
               f"{int(dist_km):,} km")
    p.setPen(QColor(C_TEXT_DIM)); p.setFont(QFont(FONT_BODY,FONT_SMALL-1))
    p.drawText(QRectF(cx-40,gy+gh+18,80,16), Qt.AlignmentFlag.AlignCenter,
               f"Currently: {proximity}")
