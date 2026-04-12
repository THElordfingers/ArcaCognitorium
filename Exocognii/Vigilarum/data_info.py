
INFO_GENERAL = {
    "Vedic Astrology": (
        "Vigilarum uses Vedic (Jyotish) sidereal astrology exclusively. Unlike Western "
        "tropical astrology which anchors the zodiac to the seasons, Vedic astrology anchors "
        "it to the fixed stars. The difference is the ayanamsha — a correction for the "
        "slow precession of the equinoxes. Vigilarum uses the Lahiri ayanamsha, standard "
        "for Jyotish. Positions here differ from Western tropical charts by roughly 23°."
    ),
    "Planets": (
        "Ten bodies are tracked: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Uranus, "
        "Neptune, Pluto. The classical seven (Sun through Saturn) are the primary Vedic "
        "influences. Uranus, Neptune, Pluto are outer planets — slower, generational. "
        "Each body shows its zodiac sign, nakshatra, degree in sign, and nakshatra lord. "
        "The retrograde marker (℞) means the body appears to move backward from Earth — "
        "considered significant in traditional astrology."
    ),
    "Lunar Nodes": (
        "Rahu (North Node) and Ketu (South Node) are not physical bodies. They are the "
        "two points where the Moon's orbit crosses the ecliptic (the Sun's apparent path). "
        "Eclipses occur when the Moon is near a node at new or full moon. They are always "
        "exactly opposite each other. In Vedic astrology they are shadow planets: Rahu "
        "governs desire and worldly ambition; Ketu governs detachment and liberation. "
        "They move slowly — roughly 18 months per sign."
    ),
    "Panchang": (
        "The Panchang is the Vedic almanac — five elements describing the quality of any "
        "moment. 'Pancha' means five, 'anga' means limb. The five: Tithi (lunar day), "
        "Vara (weekday and ruling planet), Nakshatra (Moon's lunar mansion), Yoga "
        "(luni-solar combination), Karana (half a Tithi). Vedic timing — choosing "
        "auspicious moments — is done by reading the Panchang."
    ),
    "Tithi": (
        "A Tithi is a lunar day: one-thirtieth of the synodic month. Each Tithi = 12° "
        "of Moon-Sun angular separation. Tithis 1-15 are waxing (Shukla Paksha), ending "
        "at Purnima (full moon). Tithis 16-30 are waning (Krishna Paksha), ending at "
        "Amavasya (new moon). Each Tithi has traditional quality and ruling deity."
    ),
    "Vara": (
        "Vara is the Vedic weekday, each ruled by a classical planet: Sunday-Sun, "
        "Monday-Moon, Tuesday-Mars, Wednesday-Mercury, Thursday-Jupiter, Friday-Venus, "
        "Saturday-Saturn. The ruling planet colours the day's quality in Vedic timing."
    ),
    "Nakshatra": (
        "27 Nakshatras are lunar mansions dividing the zodiac into 27 segments of 13°20'. "
        "The Moon traverses one per day approximately. Each has a ruling planet (lord), "
        "presiding deity, symbol, and characteristic quality. The Moon's Nakshatra is "
        "especially significant for timing and temperament in Vedic astrology."
    ),
    "Yoga": (
        "A Yoga in the Panchang is one of 27 luni-solar combinations: Sun longitude + "
        "Moon longitude divided by 13°20'. Each has a name and quality — some auspicious, "
        "some not. Vyatipata and Vaidhriti are most inauspicious. Siddhi and Shubha "
        "are among the best."
    ),
    "Karana": (
        "A Karana is half a Tithi — ~6° of Moon-Sun separation, lasting ~6 hours. "
        "11 Karanas total: seven movable (Bava through Vishti, repeating) and four "
        "fixed (Shakuni, Chatushpada, Naga, Kimstughna). Vishti Karana is traditionally "
        "inauspicious for new beginnings."
    ),
    "Rahu Kalam": (
        "Rahu Kalam is a daily inauspicious period — one-eighth of daylight hours. "
        "Its position shifts each weekday based on Rahu's association with that day's "
        "time division. Important activities are traditionally avoided during this window. "
        "Current implementation uses a fixed 12-hour day; precise times vary by sunrise."
    ),
    "Planetary Hour": (
        "Planetary hours divide the day into 24 periods, each ruled by one of the seven "
        "classical planets in Chaldean order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon. "
        "Hour 1 of each day is ruled by that day's planetary lord (Sunday = Sun). "
        "The sequence then continues through the Chaldean order cyclically."
    ),
    "Aspects": (
        "An aspect is an angular relationship between two bodies considered energetically "
        "significant. Six are tracked: Conjunction (0°), Opposition (180°), Trine (120°), "
        "Square (90°), Sextile (60°), Quincunx (150°). The orb is deviation from exact — "
        "smaller orb means stronger aspect."
    ),
    "Eclipse Proximity": (
        "Eclipses occur when the Moon is near Rahu or Ketu at new or full moon. "
        "The gauge shows how many degrees the Moon is from each node. Within 12° = high "
        "risk for eclipse at next new/full moon. Within 20° = medium risk."
    ),
    "Seasons": (
        "Seasons are tracked via the Sun's sidereal longitude. Spring: Sun at 0° Aries. "
        "Summer: 0° Cancer. Autumn: 0° Libra. Winter: 0° Capricorn. The Sun moves ~1° "
        "per day, so each season spans ~90 days. Season Boundary alerts within 7 days "
        "of a transition."
    ),
    "Moon Phase": (
        "Phase is determined by Moon-Sun angular separation. 0° = new moon (dark). "
        "180° = full moon (fully lit). The synodic cycle takes ~29.5 days. "
        "Illumination percentage is the fraction of the visible face that is lit."
    ),
    "Moon Distance": (
        "The Moon's orbit is elliptical. Perigee (closest) ~356,500 km — Moon appears "
        "larger, tides stronger. Apogee (furthest) ~406,700 km. A full moon at perigee "
        "is often called a supermoon. The gauge shows current position between extremes."
    ),
    "Zodiac Wheel": (
        "Shows all tracked bodies on a 360° circle divided into 12 signs of 30°. "
        "Each body is a dot at its exact longitude. Sign symbols appear in the outer ring. "
        "Bodies close together are in conjunction. Gives immediate visual distribution "
        "of the sky."
    ),
    "Nakshatra Ring": (
        "Divides the zodiac into 27 segments of 13°20'. Moon's current nakshatra is "
        "highlighted gold. Finer view of the Moon's position than the 12-sign zodiac — "
        "useful for daily timing and panchang reading."
    ),
    "Tithi Dial": (
        "Shows the 30-Tithi lunar month as a circular dial. Waxing half (1-15) in teal; "
        "waning half (16-30) in dim gold. Current Tithi is highlighted bright gold with "
        "its progress percentage at centre."
    ),
    "Planet Strip": (
        "Shows all bodies as dots on individual horizontal tracks, each spanning the full "
        "360° zodiac. Sign boundaries are tick marks at every 30°. Allows quick comparison "
        "of positions. Each track is labelled with the body's name and symbol."
    ),
    "Moon Arc": (
        "A gauge showing the Moon's progress through the current synodic cycle. 0° is new "
        "moon, 360° returns to new moon. Arc fills as cycle progresses. Illumination "
        "percentage shown at centre."
    ),
}
