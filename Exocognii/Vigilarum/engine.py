# engine.py — Vigilarum Omnia v2
import math, datetime
import swisseph as swe
from data import (
    LAT, LON, AYANAMSHA, PLANETS, RAHU_ID, RAHU_SYMBOL, KETU_SYMBOL,
    SIGNS, SIGN_SYMBOLS, NAKSHATRAS, NAKSHATRA_LORDS, NAKSHATRA_SPAN,
    TITHIS, VARAS, VARA_LORDS, YOGAS, KARANAS, RAHU_KALAM_OFFSETS,
    CHALDEAN_ORDER, DAY_RULER_HOUR1, SEASON_REGISTERS, ASPECTS, moon_phase_name,
)

swe.set_sid_mode(AYANAMSHA)
SUNRISE_FALLBACK = 6 * 60

def _jd():
    n = datetime.datetime.utcnow()
    return swe.julday(n.year, n.month, n.day, n.hour + n.minute/60 + n.second/3600)

def _n(d): return d % 360.0
def _si(lon): return int(_n(lon) / 30.0)
def _sd(lon): return _n(lon) % 30.0
def _ni(lon): return int(_n(lon) / NAKSHATRA_SPAN)
def _nd(lon): return _n(lon) % NAKSHATRA_SPAN
def _dms(deg):
    d=int(deg); m=int((deg-d)*60); s=int(((deg-d)*60-m)*60)
    return f"{d}\u00b0 {m}\' {s}\""

def _calc_planets(jd):
    r = {}
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    for pid, name, sym in PLANETS:
        pos, _ = swe.calc_ut(jd, pid, flags)
        lon = _n(pos[0]); retro = pos[3] < 0; k = name.lower()
        r[f"{k}_lon"]=lon; r[f"{k}_sign"]=SIGNS[_si(lon)]
        r[f"{k}_sign_sym"]=SIGN_SYMBOLS[_si(lon)]
        r[f"{k}_sign_deg"]=round(_sd(lon),4)
        r[f"{k}_nakshatra"]=NAKSHATRAS[_ni(lon)]
        r[f"{k}_nak_lord"]=NAKSHATRA_LORDS[_ni(lon)]
        r[f"{k}_nak_deg"]=round(_nd(lon),4)
        r[f"{k}_retrograde"]=retro; r[f"{k}_symbol"]=sym; r[f"{k}_dms"]=_dms(_sd(lon))
    pos, _ = swe.calc_ut(jd, RAHU_ID, flags)
    rl = _n(pos[0])
    r["rahu_lon"]=rl; r["rahu_sign"]=SIGNS[_si(rl)]; r["rahu_sign_sym"]=SIGN_SYMBOLS[_si(rl)]
    r["rahu_sign_deg"]=round(_sd(rl),4); r["rahu_nakshatra"]=NAKSHATRAS[_ni(rl)]
    r["rahu_nak_lord"]=NAKSHATRA_LORDS[_ni(rl)]; r["rahu_nak_deg"]=round(_nd(rl),4)
    r["rahu_retrograde"]=True; r["rahu_symbol"]=RAHU_SYMBOL; r["rahu_dms"]=_dms(_sd(rl))
    kl = _n(rl + 180.0)
    r["ketu_lon"]=kl; r["ketu_sign"]=SIGNS[_si(kl)]; r["ketu_sign_sym"]=SIGN_SYMBOLS[_si(kl)]
    r["ketu_sign_deg"]=round(_sd(kl),4); r["ketu_nakshatra"]=NAKSHATRAS[_ni(kl)]
    r["ketu_nak_lord"]=NAKSHATRA_LORDS[_ni(kl)]; r["ketu_nak_deg"]=round(_nd(kl),4)
    r["ketu_retrograde"]=True; r["ketu_symbol"]=KETU_SYMBOL; r["ketu_dms"]=_dms(_sd(kl))
    return r

def _moon_phase(sun_lon, moon_lon):
    diff = _n(moon_lon - sun_lon)
    illum = (1 - math.cos(math.radians(diff))) / 2 * 100
    return {"moon_phase_angle":round(diff,4),"moon_illumination":round(illum,2),
            "moon_phase_name":moon_phase_name(diff),"moon_waxing":diff < 180.0}

def _moon_distance(jd):
    pos, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
    km = pos[2] * 149_597_870.7
    pct = (km - 356_500) / (406_700 - 356_500) * 100
    return {"moon_distance_km":round(km,0),
            "moon_distance_pct":round(max(0.0,min(100.0,pct)),1),
            "moon_proximity":"Perigee" if km < 384_400 else "Apogee"}

def _panchang(jd, sun_lon, moon_lon):
    ta = _n(moon_lon - sun_lon)
    ti = min(int(ta/12.0), 29); vi = int(jd + 1.5) % 7; ni = _ni(moon_lon)
    yi = int(_n(sun_lon + moon_lon) / NAKSHATRA_SPAN) % 27; ki = int(ta / 6.0) % 11
    return {
        "tithi_index":ti,"tithi_num":ti+1,"tithi_name":TITHIS[ti],
        "tithi_progress":round((ta%12.0)/12.0*100,1),
        "vara_index":vi,"vara_name":VARAS[vi],"vara_lord":VARA_LORDS[vi],
        "nakshatra_index":ni,"nakshatra_name":NAKSHATRAS[ni],
        "nakshatra_lord":NAKSHATRA_LORDS[ni],
        "nakshatra_progress":round((_nd(moon_lon)/NAKSHATRA_SPAN)*100,1),
        "yoga_index":yi,"yoga_name":YOGAS[yi],
        "karana_index":ki,"karana_name":KARANAS[ki],
    }

def _rahu_kalam(vi, sm):
    start = sm + (RAHU_KALAM_OFFSETS[vi]-1)*90; end = start+90
    now = datetime.datetime.now(); nm = now.hour*60+now.minute
    def fmt(m): h,mn=divmod(int(m),60); return f"{h:02d}:{mn:02d}"
    return {"rahu_kalam_start":fmt(start),"rahu_kalam_end":fmt(end),"rahu_kalam_active":start<=nm<end}

def _planetary_hour(vi, sm):
    now = datetime.datetime.now(); nm = now.hour*60+now.minute
    hn = max(0,int((nm-sm)/60))%24
    pi = (DAY_RULER_HOUR1.get(VARA_LORDS[vi],0)+hn)%7; hs = sm + hn*60
    def fmt(m): h,mn=divmod(int(m)%1440,60); return f"{h:02d}:{mn:02d}"
    return {"planetary_hour_num":hn+1,"planetary_hour_planet":CHALDEAN_ORDER[pi],
            "planetary_hour_start":fmt(hs),"planetary_hour_end":fmt(hs+60)}

def _sun_times():
    sm=SUNRISE_FALLBACK; ss=sm+720; dl=ss-sm
    def fmt(m): h,mn=divmod(int(m)%1440,60); return f"{h:02d}:{mn:02d}"
    return {"sunrise":fmt(sm),"sunset":fmt(ss),"sunrise_min":sm,
            "day_length":f"{dl//60}h {dl%60}m","day_length_min":dl}

def _aspects(lons):
    keys=["sun","moon","mars","mercury","jupiter","venus","saturn","uranus","neptune","pluto","rahu","ketu"]
    active=[]
    for i,p1 in enumerate(keys):
        for p2 in keys[i+1:]:
            l1,l2=lons.get(f"{p1}_lon"),lons.get(f"{p2}_lon")
            if l1 is None or l2 is None: continue
            diff=abs(_n(l1-l2)); diff=min(diff,360-diff)
            for an,aa,orb in ASPECTS:
                if abs(diff-aa)<=orb:
                    active.append({"p1":p1.capitalize(),"p2":p2.capitalize(),"aspect":an,"orb":round(abs(diff-aa),2)})
    active.sort(key=lambda x:x["orb"])
    parts=[f"{a['p1']} {a['aspect']} {a['p2']} ({a['orb']:.1f}\u00b0)" for a in active[:5]]
    nxt=(f"{active[0]['p1']} {active[0]['aspect']} {active[0]['p2']} \u2014 {active[0]['orb']:.2f}\u00b0 orb"
         if active else "")
    return {"aspects_active":active[:8],
            "aspects_summary":" \u00b7 ".join(parts) if parts else "No major aspects",
            "aspects_next":nxt,"aspects_count":len(active)}

def _eclipse(moon_lon, rahu_lon):
    kl=_n(rahu_lon+180.0)
    dr=abs(_n(moon_lon-rahu_lon)); dr=min(dr,360-dr)
    dk=abs(_n(moon_lon-kl)); dk=min(dk,360-dk); md=min(dr,dk)
    return {"eclipse_dist_rahu":round(dr,2),"eclipse_dist_ketu":round(dk,2),
            "eclipse_nearest":"Rahu" if dr<dk else "Ketu","eclipse_min_dist":round(md,2),
            "eclipse_risk":"High" if md<12 else ("Medium" if md<20 else "Low")}

def _season(sun_lon):
    lon=_n(sun_lon)
    if lon<90:    s,p,ns,dn="Spring",lon/90,"Summer",90-lon
    elif lon<180: s,p,ns,dn="Summer",(lon-90)/90,"Autumn",180-lon
    elif lon<270: s,p,ns,dn="Autumn",(lon-180)/90,"Winter",270-lon
    else:         s,p,ns,dn="Winter",(lon-270)/90,"Spring",360-lon
    return {"season":s,"season_progress":round(p*100,1),"season_next":ns,
            "season_days_to_next":round(dn,1),"season_boundary_near":dn<7,
            "season_register":SEASON_REGISTERS[s]}

def _time_fields():
    now=datetime.datetime.now(); utc=datetime.datetime.utcnow()
    return {"time_local":now.strftime("%H:%M:%S"),"time_date":now.strftime("%Y-%m-%d"),
            "time_weekday":now.strftime("%A"),"time_utc":utc.strftime("%H:%M UTC"),
            "time_timestamp":now.isoformat()}

def calculate_all() -> dict:
    jd=_jd(); planets=_calc_planets(jd)
    sun_lon=planets["sun_lon"]; moon_lon=planets["moon_lon"]; rahu_lon=planets["rahu_lon"]
    mp=_moon_phase(sun_lon,moon_lon); md=_moon_distance(jd)
    pa=_panchang(jd,sun_lon,moon_lon); st=_sun_times()
    rk=_rahu_kalam(pa["vara_index"],st["sunrise_min"])
    ph=_planetary_hour(pa["vara_index"],st["sunrise_min"])
    asp=_aspects(planets); ec=_eclipse(moon_lon,rahu_lon)
    se=_season(sun_lon); tf=_time_fields()
    sky=(f"{SIGNS[_si(sun_lon)]} Sun \u00b7 {mp['moon_phase_name']} \u00b7 "
         f"{pa['nakshatra_name']} \u00b7 {se['season']}")
    state={}
    for d in [planets,mp,md,pa,st,rk,ph,asp,ec,se,tf]: state.update(d)
    state["sky_summary"]=sky
    return state
