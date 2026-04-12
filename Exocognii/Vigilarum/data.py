# data.py — Vigilarum Omnia v2
import swisseph as swe

LAT, LON = 48.3852, -123.5358
LOCATION_NAME = "Victoria, BC"
AYANAMSHA = swe.SIDM_LAHIRI

PLANETS = [
    (swe.SUN,     "Sun",     "☉"),
    (swe.MOON,    "Moon",    "☽"),
    (swe.MARS,    "Mars",    "♂"),
    (swe.MERCURY, "Mercury", "☿"),
    (swe.JUPITER, "Jupiter", "♃"),
    (swe.VENUS,   "Venus",   "♀"),
    (swe.SATURN,  "Saturn",  "♄"),
    (swe.URANUS,  "Uranus",  "⛢"),
    (swe.NEPTUNE, "Neptune", "♆"),
    (swe.PLUTO,   "Pluto",   "♇"),
]

RAHU_ID, RAHU_NAME, RAHU_SYMBOL = swe.MEAN_NODE, "Rahu", "☊"
KETU_NAME, KETU_SYMBOL = "Ketu", "☋"

ALL_BODY_KEYS = [
    "sun","moon","mars","mercury","jupiter","venus","saturn",
    "uranus","neptune","pluto","rahu","ketu",
]

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
SIGN_SYMBOLS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
    "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
    "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati",
]
NAKSHATRA_LORDS = [
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
]
NAKSHATRA_SPAN = 360.0 / 27.0

TITHIS = [
    "Pratipada","Dvitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dvadashi","Trayodashi","Chaturdashi","Purnima",
    "Pratipada","Dvitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dvadashi","Trayodashi","Chaturdashi","Amavasya",
]
VARAS = ["Ravivara","Somavara","Mangalavara","Budhavara","Guruvara","Shukravara","Shanivara"]
VARA_LORDS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
YOGAS = [
    "Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma",
    "Dhriti","Shula","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
    "Siddhi","Vyatipata","Variyan","Parigha","Shiva","Siddha","Sadhya","Shubha",
    "Shukla","Brahma","Indra","Vaidhriti",
]
KARANAS = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti",
           "Shakuni","Chatushpada","Naga","Kimstughna"]
RAHU_KALAM_OFFSETS = {0:7,1:1,2:6,3:4,4:5,5:3,6:2}
CHALDEAN_ORDER = ["Saturn","Jupiter","Mars","Sun","Venus","Mercury","Moon"]
DAY_RULER_HOUR1 = {"Sun":3,"Moon":6,"Mars":2,"Mercury":5,"Jupiter":1,"Venus":4,"Saturn":0}

SEASONS = ["Spring","Summer","Autumn","Winter"]
SEASON_SOLAR_ENTRY = {"Spring":0.0,"Summer":90.0,"Autumn":180.0,"Winter":270.0}
SEASON_REGISTERS = {
    "Spring":"Waking. Something returning.",
    "Summer":"Full. Dense. Overgrown.",
    "Autumn":"Burning down. Ochre and shadow.",
    "Winter":"Sparse. High contrast. Minimal.",
}

ASPECTS = [
    ("Conjunction",0.0,8.0),("Opposition",180.0,8.0),("Trine",120.0,7.0),
    ("Square",90.0,7.0),("Sextile",60.0,5.0),("Quincunx",150.0,3.0),
]

def moon_phase_name(a: float) -> str:
    a = a % 360
    if a < 22.5:  return "New Moon"
    if a < 67.5:  return "Waxing Crescent"
    if a < 112.5: return "First Quarter"
    if a < 157.5: return "Waxing Gibbous"
    if a < 202.5: return "Full Moon"
    if a < 247.5: return "Waning Gibbous"
    if a < 292.5: return "Last Quarter"
    if a < 337.5: return "Waning Crescent"
    return "New Moon"

WIDGET_REGISTRY = [
    ("planet_sun","Sun","text","Planets"),
    ("planet_moon","Moon","text","Planets"),
    ("planet_mars","Mars","text","Planets"),
    ("planet_mercury","Mercury","text","Planets"),
    ("planet_jupiter","Jupiter","text","Planets"),
    ("planet_venus","Venus","text","Planets"),
    ("planet_saturn","Saturn","text","Planets"),
    ("planet_uranus","Uranus","text","Planets"),
    ("planet_neptune","Neptune","text","Planets"),
    ("planet_pluto","Pluto","text","Planets"),
    ("node_rahu","Rahu — North Node","text","Lunar Nodes"),
    ("node_ketu","Ketu — South Node","text","Lunar Nodes"),
    ("panchang_tithi","Tithi","text","Panchang"),
    ("panchang_vara","Vara","text","Panchang"),
    ("panchang_nakshatra","Nakshatra","text","Panchang"),
    ("panchang_yoga","Yoga","text","Panchang"),
    ("panchang_karana","Karana","text","Panchang"),
    ("time_current","Current Time","text","Time & Rhythm"),
    ("time_rahu_kalam","Rahu Kalam","text","Time & Rhythm"),
    ("time_planetary_hour","Planetary Hour","text","Time & Rhythm"),
    ("time_sunrise_set","Sunrise / Sunset","text","Time & Rhythm"),
    ("time_day_length","Day Length","text","Time & Rhythm"),
    ("lunar_phase_text","Moon Phase","text","Lunar Detail"),
    ("lunar_sign","Moon Sign","text","Lunar Detail"),
    ("lunar_nakshatra","Moon Nakshatra","text","Lunar Detail"),
    ("aspects_current","Current Aspects","text","Aspects"),
    ("aspects_next","Next Aspect","text","Aspects"),
    ("season_current","Season","text","Seasons"),
    ("season_progress","Season Progress","text","Seasons"),
    ("season_boundary","Season Boundary","text","Seasons"),
    ("summary_sky","Sky Summary","text","Summaries"),
    ("summary_panchang","Panchang Summary","text","Summaries"),
    ("summary_eclipse","Eclipse Proximity","text","Summaries"),
    ("moon_disc","Moon Disc","visual","Visual"),
    ("zodiac_wheel","Zodiac Wheel","visual","Visual"),
    ("moon_arc","Moon Arc","visual","Visual"),
    ("nakshatra_ring","Nakshatra Ring","visual","Visual"),
    ("tithi_dial","Tithi Dial","visual","Visual"),
    ("eclipse_gauge","Eclipse Gauge","visual","Visual"),
    ("planet_strip","Planet Strip","visual","Visual"),
    ("moon_distance_gauge","Moon Distance","visual","Visual"),
]
WIDGET_BY_ID = {w[0]: w for w in WIDGET_REGISTRY}
WIDGET_CATEGORIES = [
    "Planets","Lunar Nodes","Panchang","Time & Rhythm",
    "Lunar Detail","Aspects","Seasons","Summaries","Visual",
]

MAX_DISPLAYS, VALID_COLUMNS, DEFAULT_COLS = 9, [2,3,4], 3

C_BG="#0A0A0F"; C_PANEL="#0F0F1A"; C_BORDER="#C8A84B"; C_GOLD="#C8A84B"
C_GOLD_DIM="#7A6530"; C_TEXT="#E8DEB8"; C_TEXT_DIM="#7A7260"; C_TEAL="#4ABFBF"
C_RED="#C84B4B"; C_GREEN="#4BC87A"; C_WHITE="#F0EAD6"; C_VIOLET="#9B7EC8"

BODY_COLOURS = {
    "sun":C_GOLD,"moon":C_WHITE,"mars":C_RED,"mercury":C_TEAL,
    "jupiter":C_GREEN,"venus":"#C87FC8","saturn":C_TEXT_DIM,
    "uranus":"#7EC8C8","neptune":"#7B9EC8","pluto":C_VIOLET,
    "rahu":C_GOLD_DIM,"ketu":C_GOLD_DIM,
}
BODY_SYMBOLS = {
    "sun":"☉","moon":"☽","mars":"♂","mercury":"☿","jupiter":"♃","venus":"♀",
    "saturn":"♄","uranus":"⛢","neptune":"♆","pluto":"♇","rahu":"☊","ketu":"☋",
}
BODY_NAMES = {
    "sun":"Sun","moon":"Moon","mars":"Mars","mercury":"Mercury","jupiter":"Jupiter",
    "venus":"Venus","saturn":"Saturn","uranus":"Uranus","neptune":"Neptune","pluto":"Pluto",
    "rahu":"Rahu (North Node)","ketu":"Ketu (South Node)",
}

FONT_BODY="Georgia"; FONT_SIZE=11; FONT_SMALL=9; FONT_LARGE=14; FONT_TITLE=16

INFO_GENERAL = {
    "Vedic Astrology": (
        "Vigilarum uses Vedic (Jyotish) sidereal astrology. Unlike Western tropical astrology "
        "which anchors the zodiac to the seasons, Vedic astrology anchors it to the fixed stars. "
        "The correction is the ayanamsha — Vigilarum uses Lahiri, the Jyotish standard. "
        "Positions here differ from Western charts by roughly 23 degrees."
    ),
    "Planets": (
        "Ten bodies are tracked: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Uranus, "
        "Neptune, Pluto. The classical seven (Sun through Saturn) are the primary Vedic "
        "influences. The outer three are generational. Each shows its current sign, nakshatra, "
        "and degree. Retrograde (R) means the body appears to move backward from Earth."
    ),
    "Lunar Nodes": (
        "Rahu (North Node) and Ketu (South Node) are not physical bodies. They are the points "
        "where the Moon's orbit crosses the ecliptic. When the Moon is near a node at a new or "
        "full moon, an eclipse occurs. In Vedic astrology they are shadow planets. Rahu governs "
        "desire and ambition. Ketu governs detachment and liberation. Always opposite each other."
    ),
    "Panchang": (
        "The Vedic almanac — five elements: Tithi (lunar day), Vara (weekday and ruling planet), "
        "Nakshatra (Moon's lunar mansion), Yoga (luni-solar combination), Karana (half a Tithi). "
        "Traditional Vedic timing uses the Panchang to select auspicious moments."
    ),
    "Tithi": (
        "A lunar day — one of 30 divisions of the synodic month. Each covers 12 degrees of "
        "Moon-Sun separation. Tithis 1-15 are waxing (Pratipada to Purnima). 16-30 are waning."
    ),
    "Vara": (
        "The Vedic weekday: Sunday (Sun), Monday (Moon), Tuesday (Mars), Wednesday (Mercury), "
        "Thursday (Jupiter), Friday (Venus), Saturday (Saturn)."
    ),
    "Nakshatra": (
        "27 lunar mansions of 13 degrees 20 minutes each. The Moon traverses one roughly per day. "
        "Each has a ruling planet (lord), a deity, and characteristic quality."
    ),
    "Yoga": (
        "One of 27 luni-solar combinations from the sum of Sun and Moon longitudes divided by "
        "13 degrees 20 minutes. Some auspicious, some not. Vyatipata and Vaidhriti are most inauspicious."
    ),
    "Karana": (
        "Half a Tithi — 6 degrees of Moon-Sun separation. Eleven Karanas: seven movable, four fixed."
    ),
    "Rahu Kalam": (
        "A daily inauspicious window — one-eighth of the day, position shifting each weekday. "
        "Important activities traditionally avoided during this time."
    ),
    "Planetary Hour": (
        "24 daily periods each ruled by a planet in Chaldean order: Saturn, Jupiter, Mars, Sun, "
        "Venus, Mercury, Moon. The first hour belongs to the day's ruling planet."
    ),
    "Aspects": (
        "Angular relationships between bodies: Conjunction (0), Opposition (180), Trine (120), "
        "Square (90), Sextile (60), Quincunx (150). Orb is deviation from exact — smaller is stronger."
    ),
    "Eclipse Proximity": (
        "Within 12 degrees of a node is high eclipse risk at the next lunation. Within 20 is medium."
    ),
    "Seasons": (
        "Tracked via Sun's sidereal longitude. Spring 0 Aries, Summer 0 Cancer, Autumn 0 Libra, "
        "Winter 0 Capricorn. Each season roughly 90 days."
    ),
    "Moon Phase": "Angular separation between Moon and Sun. 0 degrees = new, 180 = full. Cycle 29.5 days.",
    "Moon Distance": "Perigee ~356,500 km, apogee ~406,700 km. Gauge shows current position between these.",
    "Zodiac Wheel": "All bodies on a 360-degree circle divided into 12 signs.",
    "Nakshatra Ring": "Zodiac divided into 27 nakshatra segments. Moon's current nakshatra highlighted.",
    "Tithi Dial": "Moon-Sun separation in 30 segments. Waxing teal, waning dim gold. Current highlighted.",
    "Planet Strip": "Each body on its own track across the full 360 degrees.",
    "Moon Arc": "Moon's progress through the synodic cycle. Fills from new to full and back.",
}
