"""
 ______        _     _________     _                          
|_   _ `.     / \   |  _   _  |   / \                         
  | | `. \   / _ \  |_/ | | \_|  / _ \       _ .--.   _   __  
  | |  | |  / ___ \     | |     / ___ \     [ '/'`\ \[ \ [  ] 
 _| |_.' /_/ /   \ \_  _| |_  _/ /   \ \_  _ | \__/ | \ '/ /  
|______.'|____| |____||_____||____| |____|(_)| ;.__/[\_:  /   
                                            [__|     \__.'  


VIGILARUM OMNIA — Data Tables
All lookup tables, constants, and widget definitions.
"""

PLANET_GLYPHS = {
    "Sun":"☉","Moon":"☽","Mercury":"☿","Venus":"♀","Mars":"♂",
    "Jupiter":"♃","Saturn":"♄","Uranus":"♅","Neptune":"♆","Pluto":"♇",
    "Rahu":"☊","Ketu":"☋",
}

SIGN_GLYPHS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
SIGN_NAMES  = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
               "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

MOON_PHASE_GLYPHS = ["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]
MOON_PHASE_NAMES  = [
    "New Moon","Waxing Crescent","First Quarter","Waxing Gibbous",
    "Full Moon","Waning Gibbous","Last Quarter","Waning Crescent",
]

NAMED_MOONS = {
    1: ("Wolf Moon",       "Midwinter. Isolation. Threshold energy."),
    2: ("Snow Moon",       "Heaviest snows. Endurance. Inner fire."),
    3: ("Worm Moon",       "Earth softens. Something stirs beneath."),
    4: ("Pink Moon",       "First wildflowers. Emergence. Colour returning."),
    5: ("Flower Moon",     "Peak bloom. Creative and generative force."),
    6: ("Strawberry Moon", "Harvest begins. Sweetness earned."),
    7: ("Buck Moon",       "Antlers in velvet. Growth visible and tender."),
    8: ("Sturgeon Moon",   "Ancient fish rise. Deep memory surfaces."),
    9: ("Harvest Moon",    "Light to work by. Accumulated labour made visible."),
    10:("Hunter's Moon",   "Pursuit. Preparation. The long chase."),
    11:("Beaver Moon",     "Final preparations against the coming cold."),
    12:("Cold Moon",       "The longest night. The void at its deepest."),
}

SEASON_NAMES  = ["Winter","Spring","Summer","Autumn"]
SEASON_SPANS  = [
    "Winter Solstice → Spring Equinox",
    "Spring Equinox → Summer Solstice",
    "Summer Solstice → Autumn Equinox",
    "Autumn Equinox → Winter Solstice",
]
SEASON_COLS   = ["blue","green","yellow","red"]
SEASON_GLYPHS = ["❄","🌱","☀","🍂"]

NAKSHATRAS = [
    ("Ashwini",        "Ketu",    "Swift healing. Initiation."),
    ("Bharani",        "Venus",   "Bearing burdens. Transformation."),
    ("Krittika",       "Sun",     "Sharp blade. Purification by fire."),
    ("Rohini",         "Moon",    "Red abundance. Creative fertility."),
    ("Mrigashira",     "Mars",    "Searching deer. Gentle seeking."),
    ("Ardra",          "Rahu",    "Storm and tears. Raw intensity."),
    ("Punarvasu",      "Jupiter", "Return of light. Renewal."),
    ("Pushya",         "Saturn",  "Nourishment. Most auspicious."),
    ("Ashlesha",       "Mercury", "Clinging serpent. Mystical wisdom."),
    ("Magha",          "Ketu",    "Throne of ancestors. Royal authority."),
    ("Purva Phalguni", "Venus",   "Fig tree. Rest and pleasure."),
    ("Uttara Phalguni","Sun",     "Patronage. Stable relationships."),
    ("Hasta",          "Moon",    "The hand. Skilled craft."),
    ("Chitra",         "Mars",    "Bright jewel. Art and brilliance."),
    ("Swati",          "Rahu",    "Independent sword. Self-sufficiency."),
    ("Vishakha",       "Jupiter", "Forked branch. Determined purpose."),
    ("Anuradha",       "Saturn",  "Following Radha. Deep devotion."),
    ("Jyeshtha",       "Mercury", "Eldest. Protective seniority."),
    ("Mula",           "Ketu",    "Root. Dissolution of foundations."),
    ("Purva Ashadha",  "Venus",   "Invincible. Fan and winnowing."),
    ("Uttara Ashadha", "Sun",     "Universal victory. Elephant's tusk."),
    ("Shravana",       "Moon",    "Three footsteps. Listening deeply."),
    ("Dhanishtha",     "Mars",    "Wealthiest. Drum of Shiva."),
    ("Shatabhisha",    "Rahu",    "Hundred healers. Veiled mystery."),
    ("Purva Bhadra",   "Jupiter", "Scorching pair. Fierce purification."),
    ("Uttara Bhadra",  "Saturn",  "Warrior at rest. Deep wisdom."),
    ("Revati",         "Mercury", "Wealthy. Safe journey's end."),
]

TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami",
    "Shashthi","Saptami","Ashtami","Navami","Dashami",
    "Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima",
]
TITHI_QUALITY = ["Nanda","Bhadra","Jaya","Rikta","Purna"] * 3
TITHI_DESC = {
    "Nanda": "Joy. Auspicious for beginnings.",
    "Bhadra":"Good for most activities.",
    "Jaya":  "Victory. Favours conflict.",
    "Rikta": "Void. Avoid important acts.",
    "Purna": "Complete. Powerful results.",
}

YOGA_NAMES = [
    "Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana",
    "Atiganda","Sukarman","Dhriti","Shula","Ganda",
    "Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
    "Siddhi","Vyatipata","Variyan","Parigha","Shiva",
    "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti",
]
YOGA_QUALITY = [
    "Inauspicious","Auspicious","Auspicious","Auspicious","Auspicious",
    "Inauspicious","Auspicious","Auspicious","Inauspicious","Inauspicious",
    "Auspicious","Auspicious","Inauspicious","Auspicious","Inauspicious",
    "Auspicious","Inauspicious","Auspicious","Inauspicious","Auspicious",
    "Auspicious","Auspicious","Auspicious","Auspicious","Auspicious",
    "Auspicious","Inauspicious",
]

KARANA_NAMES = [
    "Bava","Balava","Kaulava","Taitila","Garaja",
    "Vanija","Vishti","Shakuni","Chatushpada","Naga","Kimstughna",
]

PLANETARY_HOUR_SEQ = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"]
DAY_RULERS         = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
VARA_NAMES         = [
    "Ravivara","Somavara","Mangalavara","Budhavara",
    "Guruvara","Shukravara","Shanivara",
]
VARA_DESC = [
    "Sun's day. Authority and vitality.",
    "Moon's day. Emotion and intuition.",
    "Mars's day. Action and courage.",
    "Mercury's day. Communication and commerce.",
    "Jupiter's day. Wisdom and expansion.",
    "Venus's day. Beauty and pleasure.",
    "Saturn's day. Discipline and long labour.",
]

ROMAN = {
    1000:"M",900:"CM",500:"D",400:"CD",100:"C",90:"XC",
    50:"L",40:"XL",10:"X",9:"IX",5:"V",4:"IV",1:"I",
}

# Widget registry — (id, label, section)
WIDGET_DEFS = [
    ("datetime",       "Date & Time",       "TEMPORAL"),
    ("season",         "Season",            "TEMPORAL"),
    ("sidereal_time",  "Sidereal Time",     "TEMPORAL"),
    ("moon_phase",     "Moon Phase",        "LUNAR"),
    ("illumination",   "Illumination",      "LUNAR"),
    ("named_moon",     "Named Moon",        "LUNAR"),
    ("moon_sign",      "Moon Sign",         "LUNAR"),
    ("moon_nakshatra", "Moon Nakshatra",    "LUNAR"),
    ("moon_distance",  "Moon Distance",     "LUNAR"),
    ("next_moon",      "Next Moon Event",   "LUNAR"),
    ("sun_sign",       "Sun Sign",          "SOLAR"),
    ("sun_nakshatra",  "Sun Nakshatra",     "SOLAR"),
    ("mercury",        "Mercury",           "PLANETS"),
    ("mercury_phase",  "Mercury Phase",     "PLANETS"),
    ("venus",          "Venus",             "PLANETS"),
    ("venus_phase",    "Venus Phase",       "PLANETS"),
    ("mars",           "Mars",              "PLANETS"),
    ("jupiter",        "Jupiter",           "PLANETS"),
    ("saturn",         "Saturn",            "PLANETS"),
    ("outer_planets",  "Outer Planets",     "PLANETS"),
    ("retrograde",     "Retrograde",        "PLANETS"),
    ("aspects",        "Aspects",           "PLANETS"),
    ("rahu_ketu",      "Rahu & Ketu",       "NODES"),
    ("eclipse_prox",   "Eclipse Proximity", "NODES"),
    ("panchang",       "Panchang",          "PANCHANG"),
    ("tithi",          "Tithi",             "PANCHANG"),
    ("vara",           "Vara",              "PANCHANG"),
    ("yoga",           "Yoga",              "PANCHANG"),
    ("karana",         "Karana",            "PANCHANG"),
    ("rahu_kalam",     "Rahu Kalam",        "PANCHANG"),
    ("planetary_hour", "Planetary Hour",    "PANCHANG"),
    ("day_ruler",      "Day Ruler",         "PANCHANG"),
    ("zodiac_wheel",   "Zodiac Wheel",      "VISUAL"),
    ("moon_disc",      "Moon Disc",         "VISUAL"),
    ("moon_arc",       "Moon Cycle Arc",    "VISUAL"),
    ("nakshatra_ring", "Nakshatra Ring",    "VISUAL"),
    ("tithi_dial",     "Tithi Dial",        "VISUAL"),
    ("eclipse_gauge",  "Eclipse Gauge",     "VISUAL"),
    ("planet_strip",   "Planet Strip",      "VISUAL"),
    ("palette",        "Seasonal Palette",  "AESTHETIC"),
]
