"""
Data pools for Devoted Absurd Character Prompt Generator.
Organised by archetype. Style DNA is always locked.
Weighted random selection is supported via combo scoring.
"""

import random

# ── LOCKED STYLE DNA ──────────────────────────────────────────────────────────
STYLE_DNA = (
    "Stylized 2D character illustration, bold clean ink outlines, graphic inking style, "
    "clean but expressive linework, not sketchy, not painterly, strong silhouette, "
    "flat cel shading, rich muted color palette, moderately desaturated but not washed out, "
    "strong midtone presence, defined shadow shapes, subtle highlight accents, "
    "colors remain distinct and readable, no glossy rendering, no animals"
)

# ── ARCHETYPES ─────────────────────────────────────────────────────────────────
ARCHETYPES = {

    "bureaucrat": {
        "label": "Bureaucrat / Official",
        "palette_hint": "dusty greens, institutional teal, dull navy, muted mustard",
        "style_flex": "clean structured lines, pressed uniform details, badge and insignia visible",
        "roles": [
            "Transit Authority Inspector", "Bureau of Standards Clerk",
            "Municipal Parking Warden", "Health & Safety Officer",
            "Regional Tax Compliance Agent", "Building Code Enforcer",
            "Port Authority Customs Officer", "State Records Archivist",
            "Public Works Supervisor", "Licensing Board Examiner",
            "Urban Planning Official", "Water Authority Inspector",
            "Railway Operations Supervisor", "Census Bureau Field Collector",
            "Unemployment Office Case Worker", "Emergency Management Coordinator",
            "Border Checkpoint Officer", "Library Compliance Officer",
            "Noise Ordinance Enforcement Agent", "Zoning Appeals Officer",
        ],
        "personalities": [
            "humorless, procedural, barely tolerating existence",
            "compulsive rule-follower with eroding faith in the system",
            "weary and resigned, going through the motions",
            "quietly furious at everything, professionally suppressed",
            "suspicious of everyone, trusts only paperwork",
            "emotionally hollow, optimised purely for protocol",
            "bitter veteran counting days to retirement",
            "rigidly principled, bewildered by a world that isn't",
            "passive-aggressive compliance as a form of protest",
            "nostalgic for a golden age of bureaucracy that never existed",
        ],
        "garments": [
            "double-breasted trench coat with epaulettes and institutional crest",
            "structured military-cut uniform jacket with rank tabs",
            "full bureaucratic suit with subtle rank insignia",
            "heavy wool overcoat with agency patches at the shoulders",
            "single-breasted service jacket with worn collar and ID lanyard",
            "semi-formal tunic with gold button trim and breast pocket badge",
        ],
        "props": [
            "a thick manila folder under one arm",
            "a worn metal clipboard with accumulated papers",
            "a rubber stamp clipped to the belt",
            "a battered two-way radio",
            "a thermal mug with an agency logo, lid missing",
            "a pen tucked behind the ear, cap chewed",
        ],
        "details": [
            "a worn medal ribbon on the breast pocket",
            "a slightly crooked name badge",
            "a coffee stain on the lapel, unaddressed",
            "mismatched buttons — one recently replaced",
            "an embroidered agency crest, partially fraying",
            "a faded patch stitched over an older patch",
            "scuffed black leather boots, imperfectly polished",
            "a sleeve crease that has long since given up",
        ],
    },

    "street": {
        "label": "Street-Level Civilian",
        "palette_hint": "faded ochre, dusty rose, worn denim blue, concrete grey, tobacco brown",
        "style_flex": "looser ink lines, layered clothing, lived-in textures",
        "roles": [
            "Night-shift convenience store clerk", "Unlicensed street vendor",
            "Retired bus driver, now just rides them", "Chronic queue-joiner",
            "Neighbourhood watch volunteer (self-appointed)", "Pawnshop owner who's seen everything",
            "Diner regular who occupies the same stool daily", "Amateur conspiracy theorist",
            "Obsessive pigeon feeder in the park", "Dog walker for dogs that don't respect him",
            "Lottery ticket hoarder", "Corner newspaper vendor",
            "Man who fixes things that weren't broken", "Off-duty security guard, still in uniform",
            "Retired electrician who offers opinions freely",
        ],
        "personalities": [
            "deeply philosophical about things that don't matter",
            "convinced the city is conspiring against specifically him",
            "aggressively generous in ways nobody asked for",
            "haunted by a minor social mistake from 1987",
            "cheerfully oblivious to all social cues",
            "catalogues every injustice, does nothing about any of them",
            "suspicious of anything introduced after 1995",
            "communicates primarily through meaningful silences",
            "maintains an elaborate personal honour code, publicly",
            "has strong opinions about everything, expertise in nothing",
        ],
        "garments": [
            "oversized windbreaker with too many zipped pockets",
            "heavy flannel shirt over a faded band tee, untucked",
            "puffy vest over a collared shirt, both slightly too small",
            "worn corduroy jacket, elbow patches intact",
            "tracksuit top over dress trousers — a deliberate choice",
            "cable-knit sweater with a suspicious stain near the hem",
            "long coat that was expensive once, bought secondhand",
        ],
        "props": [
            "a plastic bag containing a plastic bag",
            "a newspaper folded to the crossword, never finished",
            "a thermos of something that is definitely not coffee",
            "a lottery ticket scratched halfway",
            "a dog lead with no dog",
            "a broken umbrella, carried anyway",
            "a small transistor radio clipped to a pocket",
        ],
        "details": [
            "reading glasses pushed up on the forehead",
            "one trouser leg slightly higher than the other",
            "a band-aid on a knuckle, origin unknown",
            "keys on a carabiner clipped to a belt loop",
            "a button badge of unclear allegiance",
            "socks visible above low-cut shoes",
            "a permanent ink stain on the index finger",
        ],
    },

    "criminal": {
        "label": "Criminal / Underworld",
        "palette_hint": "deep noir blacks, bruised purple, amber under-light, dirty gold, blood red accents",
        "style_flex": "heavier shadows, more angular ink strokes, high contrast pools of dark",
        "roles": [
            "Retired fixer living too quietly", "Mid-level fence who knows too much",
            "Getaway driver who only does crosswords now", "Debt collector with a philosophy degree",
            "Former safecracker, now locksmith", "Information broker in a dull suit",
            "Smuggler of inexplicably mundane goods", "Forger of slightly incorrect documents",
            "Low-ranking mob accountant, deeply stressed", "Black market pharmacist",
            "Professional alibi provider", "The guy who moves the thing",
            "Insurance fraud consultant", "Semi-retired pickpocket, teaches now",
            "Money launderer who only uses legitimate-seeming businesses",
        ],
        "personalities": [
            "professional and quiet — dangerously so",
            "genuinely believes all of it is victimless",
            "tired of being interesting, wants a normal life",
            "meticulous, methodical, allergic to improvisation",
            "surprisingly principled within a very narrow moral framework",
            "deeply nostalgic for a criminal golden age",
            "paranoid in a way that has so far kept him alive",
            "cheerful in a way that makes everyone uncomfortable",
            "speaks rarely, always specifically",
            "morally flexible but personally very tidy",
        ],
        "garments": [
            "nondescript grey suit, intentionally forgettable",
            "dark overcoat, collar up, no badge of any kind",
            "leather jacket, worn soft, no insignia",
            "loose linen shirt and dark trousers — resort casual, somehow threatening",
            "workwear jacket with a false trade logo",
            "rumpled blazer over a turtleneck, old-fashioned intentionally",
        ],
        "props": [
            "a burner phone in a battered case",
            "a thin envelope slid into an inside pocket",
            "a set of lock picks worn like a bookmark",
            "a glass of something amber, untouched",
            "car keys to an unremarkable car",
            "a small notebook with a rubber band around it",
            "a cigarette, unlit, held but not smoked",
        ],
        "details": [
            "a faint scar along the jawline",
            "a watch that is too nice for the rest of the outfit",
            "shoes that are impeccably polished",
            "a ring that might be a signet, might not be",
            "a collar button undone, tie loosened just enough",
            "hands that are very still",
            "a subtle but visible tension in the jaw",
        ],
    },

    "military": {
        "label": "Military / Paramilitary",
        "palette_hint": "olive drab, military tan, muted camouflage green, faded khaki, steel grey",
        "style_flex": "rigid posture, hard shadow edges, gear details crisp and functional",
        "roles": [
            "Retired sergeant, still acts like one", "Private military contractor, vague portfolio",
            "Demobilised soldier navigating civilian confusion", "Military attaché with nothing to attach",
            "Base security chief who takes it personally", "Logistics officer who controls everything",
            "Bomb disposal tech on administrative leave", "Military police investigator, permanent scowl",
            "Quartermaster who knows where everything is and says nothing",
            "Intelligence analyst who trusts no one including himself",
            "Veteran medic now working in insurance", "Sniper turned birdwatcher",
            "Drill sergeant with nothing left to drill", "Fleet commander without a fleet",
        ],
        "personalities": [
            "mission-oriented in situations that have no mission",
            "built for an emergency that hasn't come yet",
            "treats all civilian chaos as a solvable tactical problem",
            "loyalty as a character flaw in the wrong context",
            "speaks in brief declarative sentences only",
            "hyper-observant, constantly threat-assessing",
            "quietly devastated that peace is this boring",
            "structured to the point of fragility when structure breaks",
            "carries the weight of decisions made years ago",
            "profoundly calm in a way that makes civilians nervous",
        ],
        "garments": [
            "worn field jacket with subdued unit patches",
            "semi-formal dress uniform, several ribbons, impeccably pressed",
            "combat-cut trousers and a plain dark jacket — halfway out",
            "tan tactical shirt tucked hard into belted fatigue trousers",
            "heavy olive overcoat with rank tab on one shoulder only",
            "civilian clothes worn like a uniform anyway",
        ],
        "props": [
            "a folded topographic map, out of date",
            "a military-issue watch, running precisely",
            "a battered metal water bottle",
            "a short-wave radio, switched off",
            "a field notebook, grid-paper, entries in small print",
            "dog tags visible at the collar",
            "a multi-tool clipped to the belt",
        ],
        "details": [
            "unit insignia partially removed — removed, not replaced",
            "boots in perfect condition despite everything",
            "posture so correct it reads as defiant",
            "a fading tattoo on the forearm, partially visible",
            "rank indicated by absence — blank where insignia was",
            "creases pressed into clothing that doesn't require it",
            "a subtle limp that is never mentioned",
        ],
    },

    "scifi": {
        "label": "Sci-fi / Dystopian",
        "palette_hint": "desaturated cyan, institutional beige, toxic yellow accents, dim neon, oxidised copper",
        "style_flex": "clean functional lines with subtle future-decay, corporate insignia, worn tech details",
        "roles": [
            "Zone Compliance Officer, Sector 7-G", "Neural Audit Technician",
            "Decommissioned android, still reporting for duty",
            "Corporate loyalty assessor", "Atmospheric processor maintenance worker",
            "Genetic registration clerk", "Transit pod dispatcher, inner ring",
            "Memory fragmentation specialist", "Off-world labour broker",
            "Synthetic citizen advocate (unlicensed)", "Data quarantine officer",
            "Ration distribution supervisor", "Blackout zone perimeter warden",
            "Behavioural compliance monitor", "Expired permit enforcement agent",
        ],
        "personalities": [
            "faithfully executing a mandate that stopped making sense",
            "aware the system is collapsing, filing the correct forms anyway",
            "loyalty to an institution that dissolved six months ago",
            "quietly malfunctioning in ways only he notices",
            "optimised for efficiency in a world defined by chaos",
            "nostalgic for a version of the future that never arrived",
            "believes the documentation is more real than the events",
            "processes everything through a lens of obsolete protocol",
            "the last true believer in a discredited ideology",
            "performing humanity for systems that no longer require it",
        ],
        "garments": [
            "corporate sector jumpsuit with zone ID strip on the sleeve",
            "institutional uniform with integrated ID panel, flickering",
            "retrofitted bureaucratic suit with data-port seams",
            "environment suit, civilian grade, well past service life",
            "zone warden jacket with defunct authority patches",
            "a long synthetic coat with embedded compliance indicators",
        ],
        "props": [
            "a data tablet showing an error that can't be dismissed",
            "a handheld scanner with a cracked lens",
            "an access card that may or may not still work",
            "a portable printer for citations, out of paper",
            "a respirator clipped to the belt, maybe necessary",
            "a corporate-issue earpiece, one side broken",
            "a laminated permit for something no longer permitted",
        ],
        "details": [
            "a zone ID number stencilled on the back of the collar",
            "a barcode on the wrist, worn but legible",
            "a loyalty indicator pin, colour faded to ambiguous",
            "a patch where a logo was removed, outline still visible",
            "one sleeve rolled up around a subdermal device",
            "footwear that is standard-issue and has never been replaced",
            "a visible seam repair — maintenance, not style",
        ],
    },

    "retro_futurist": {
        "label": "Alternate History / Retro-Futurist",
        "palette_hint": "rich burgundy, brass gold, smoke grey, deep teal, sepia-tinged highlights",
        "style_flex": "art deco angularity in clothing, analogue device details, deliberate period aesthetic",
        "roles": [
            "Aetheric Signal Corps operator", "Ministry of Probability analyst",
            "Steam Transit Authority warden", "Clockwork maintenance overseer",
            "Bureau of Unexplained Phenomena clerk", "Imperial survey cartographer",
            "Pneumatic post supervisor", "Difference Engine technician",
            "Sky-dock customs inspector", "Temporal Continuity Office field agent",
            "Galvanic power station warden", "Colonial cataloguer, reassigned locally",
            "Expedition recovery officer", "Mechanical infantry liason, peacetime",
        ],
        "personalities": [
            "absolutely certain the Empire is still in good shape",
            "devoted to analogue processes in a world going electric",
            "formal to the point of absurdity — the absurdity is invisible to him",
            "catalogues everything, understands none of it",
            "believes in progress deeply, defines it very narrowly",
            "the bureaucracy of a world that almost was, taken seriously",
            "proud of a rank that has no modern equivalent",
            "trusts mechanisms more than people, for good reason",
            "mourning a future that diverged without him",
            "administers rules written for a reality that shifted",
        ],
        "garments": [
            "high-collared officer coat with brass toggle closures",
            "military-cut uniform with analogue instrument panels on the forearm",
            "long ministerial coat with epaulettes and embossed buttons",
            "wool field jacket with map-pocket detailing and brass compass clips",
            "structured tunic with clockwork rank insignia",
            "transit authority coat with route identifiers on the collar",
        ],
        "props": [
            "a pocket watch on a heavy chain, checked frequently",
            "a mechanical calculation device, worn at the hip",
            "rolled survey maps, rubber-banded",
            "a brass speaking tube end clipped to the lapel",
            "a logbook with marbled covers and a ribbon bookmark",
            "goggles pushed up on the forehead, never used",
            "a signal lamp, folded compact, belt-clipped",
        ],
        "details": [
            "exposed gear mechanism at the cuff",
            "ink stains that suggest extensive map annotation",
            "a conductor's punch worn as a lapel pin",
            "an expired expedition medallion, never removed",
            "boot buckles where laces would be expected",
            "a rank sash in a colour whose meaning is lost",
            "collar studs of mismatched metals — a long story",
        ],
    },

    "fantasy_grounded": {
        "label": "Fantasy-Adjacent (Grounded)",
        "palette_hint": "earthy ochre, muted forest green, stone grey, dried blood red, tarnished silver",
        "style_flex": "worn natural materials, hand-stitched details, no magic glows — gritty and tactile",
        "roles": [
            "City watch constable, lowest precinct",
            "Guild tax collector, third district",
            "Harbour master's assistant (the harbour master is never present)",
            "Road toll warden, unpopular bridge",
            "Crown census taker, rural assignment",
            "Market inspector (weights and measures)",
            "Dungeon records clerk (the dungeon is administrative, mostly)",
            "Travel permit officer, northern gate",
            "Healer's guild licensing officer",
            "Cartographers' guild field verifier",
            "Archive monk reassigned to civil duty",
            "Court scribe, between courts",
            "Prison warden, minimum security, maximum tedium",
        ],
        "personalities": [
            "enforces laws older than anyone alive, never questions them",
            "convinced magic is cheating, even when it isn't",
            "deeply loyal to a ruler he has never met",
            "interprets every situation through the lens of guild bylaws",
            "suspicious of adventurers for very good reasons",
            "the only person in the city who does the paperwork correctly",
            "profoundly tired of prophecy and everyone involved in it",
            "treats dragons as a permit issue",
            "pragmatic about the supernatural — it still needs to be taxed",
            "has seen too much to be surprised, not enough to be interesting",
        ],
        "garments": [
            "rough wool tunic under a studded leather vest with office insignia",
            "long travel coat of oiled canvas, city seal on the breast",
            "guard's half-plate, worn and unofficial, over civilian clothes",
            "dark robes with guild colours at the hem and cuffs",
            "layered travelling clothes with document pouches at the belt",
            "simple but structured jerkin over a linen shirt, sealed with wax",
        ],
        "props": [
            "a wax seal stamp on a cord around the neck",
            "a scroll case, always full",
            "a short baton — authority, not weapon",
            "a coin scale and weights in a worn leather pouch",
            "a lantern, oil nearly out",
            "a city map covered in personal annotations",
            "a quill and inkwell, somehow portable",
        ],
        "details": [
            "a guild mark branded or tattooed on the wrist",
            "boots repaired so many times the original is unrecognisable",
            "a belt buckle with a heraldic device, slightly wrong",
            "a scar from a minor bureaucratic altercation",
            "dried mud at the hem, official travel",
            "ink stains on the fingertips",
            "a thin chain with a small official seal, tucked inside the collar",
        ],
    },
}

# ── SHARED POOLS ───────────────────────────────────────────────────────────────

BODY_TYPES = [
    "lean and angular, all sharp lines",
    "stocky and solid, low centre of gravity",
    "tall and slightly stooped, as if apologising for height",
    "average build, completely unremarkable by design",
    "broad-shouldered but soft-edged, let himself go",
    "wiry and compact, coiled energy",
    "heavyset with authority, takes up the right amount of space",
    "slight and precise, every gesture economical",
]

AGES = [
    "early 30s — young enough to still care, old enough to start doubting",
    "mid 40s — peak competence, peak disillusionment",
    "late 50s — past caring, still showing up",
    "early 60s — one foot out, holding the door for no one",
    "late 20s — hasn't been ground down yet, process beginning",
    "mid 30s — recently realised this is permanent",
]

GENDERS = [
    "man", "woman", "person", "man", "woman",  # weighted toward variety
]

MOODS = [
    "emotionally detached, blank thousand-yard stare",
    "smoldering barely-contained fury held under rigid professionalism",
    "deep bone-tired exhaustion, eyes carrying decades of disappointment",
    "suspicious narrowed eyes, perpetually expects rule infractions",
    "bitter resigned contempt for the absurdity of everything",
    "muted defiance — knows the system is broken, enforces it anyway",
    "quiet satisfaction at a minor procedural victory",
    "haunted look of someone who remembers when this made sense",
    "studied neutrality masking complete internal chaos",
    "the particular blankness of someone filling in a form",
]

POSTURES = [
    "hands in pockets, slouched but somehow commanding",
    "arms crossed, weight shifted to one foot",
    "hands clasped behind the back, rigid parade rest",
    "one hand resting on a belt item, scanning slowly",
    "slight forward lean, stillness as subtle threat",
    "standing very still in a way that suggests readiness",
    "weight evenly distributed, no tells whatsoever",
    "one shoulder slightly higher, a long-standing asymmetry",
]

BACKGROUNDS = [
    "flat mint green", "flat pale cream", "flat ash grey",
    "flat warm beige", "flat dusty sage", "flat cool grey",
    "flat institutional off-white", "flat muted teal",
    "flat faded ochre", "flat soft slate",
]

SETTINGS = [
    # ambient setting hints (no full scene)
    None, None, None,  # most stay plain bg
    "shadow of a chain-link fence across the lower background",
    "faint suggestion of fluorescent strip lighting above",
    "worn linoleum floor plane visible at the feet",
    "a distant queue implied by shadow shapes",
    "muted doorframe geometry behind the figure",
]


# ── WEIGHTED RANDOM SELECTION ──────────────────────────────────────────────────

def weighted_pick(items: list, weights: dict) -> str:
    """Pick from items, boosting items that appear in weights dict."""
    if not weights:
        return random.choice(items)
    w = [weights.get(item, 1.0) for item in items]
    return random.choices(items, weights=w, k=1)[0]


def build_character(archetype_key: str = None, overrides: dict = None,
                    combo_weights: dict = None) -> dict:
    """
    Build a full character dict, ready for prompt assembly.
    overrides: any keys to force (role, mood, garment, color, etc.)
    combo_weights: dict of item -> float, from the learning system
    """
    if archetype_key is None or archetype_key == "random":
        archetype_key = random.choice(list(ARCHETYPES.keys()))

    arch = ARCHETYPES[archetype_key]
    ov = overrides or {}
    cw = combo_weights or {}

    char = {
        "archetype_key": archetype_key,
        "archetype_label": arch["label"],
        "role": ov.get("role") or weighted_pick(arch["roles"], cw),
        "personality": ov.get("personality") or weighted_pick(arch["personalities"], cw),
        "garment": ov.get("garment") or weighted_pick(arch["garments"], cw),
        "prop": ov.get("prop") or weighted_pick(arch["props"], cw),
        "detail": ov.get("detail") or weighted_pick(arch["details"], cw),
        "mood": ov.get("mood") or weighted_pick(MOODS, cw),
        "posture": ov.get("posture") or weighted_pick(POSTURES, cw),
        "body_type": ov.get("body_type") or weighted_pick(BODY_TYPES, cw),
        "age": ov.get("age") or weighted_pick(AGES, cw),
        "gender": ov.get("gender") or random.choice(GENDERS),
        "background": ov.get("background") or random.choice(BACKGROUNDS),
        "setting_hint": ov.get("setting_hint") or random.choice(SETTINGS),
        "palette_hint": arch["palette_hint"],
        "style_flex": arch["style_flex"],
        "name": ov.get("name", ""),
        "extra": ov.get("extra", ""),
    }
    return char


def assemble_prompt(char: dict) -> str:
    """Turn a character dict into a full image generation prompt."""
    name_line = f"Character is {char['name']}, a " if char["name"] else "Character is a "
    name_line += f"{char['age']} {char['gender']} working as a {char['role']}."

    personality_line = f"Personality: {char['personality']}."

    costume_line = (
        f"Wearing a {char['garment']}, {char['style_flex']}, "
        f"with {char['detail']}. Carries {char['prop']}."
    )

    body_line = f"Build: {char['body_type']}."
    pose_line = f"Pose: {char['posture']}."
    mood_line = f"Expression: {char['mood']}."

    bg_line = f"{char['background']} background"
    if char["setting_hint"]:
        bg_line += f", {char['setting_hint']}"
    bg_line += "."

    palette_line = f"Color palette: {char['palette_hint']}."

    style_line = (
        "Stylized 2D character illustration, bold clean ink outlines, graphic inking style, "
        "clean but expressive linework, not sketchy, not painterly, strong silhouette, "
        "flat cel shading, moderately desaturated but not washed out, strong midtone presence, "
        "defined shadow shapes, subtle highlight accents, angular but grounded proportions, "
        "understated punk influence, minimal absurd symbolic elements, restrained dark humour, "
        "subtle surface wear inside shapes only, no animals, no glossy rendering."
    )

    extra_line = f"Additional notes: {char['extra']}." if char["extra"] else ""

    parts = [
        style_line, palette_line, name_line, personality_line,
        costume_line, body_line, pose_line, mood_line, bg_line,
    ]
    if extra_line:
        parts.append(extra_line)

    return "\n".join(parts)
