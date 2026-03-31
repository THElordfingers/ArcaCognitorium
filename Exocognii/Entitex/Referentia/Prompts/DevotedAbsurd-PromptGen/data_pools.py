"""
Data pools for Devoted Absurd Character Prompt Generator.
v2.0 — Medieval-dark-ages overhaul with pseudo-tech layer

IMPORTANT — HOW THESE POOLS ARE USED:
These pools are vocabulary and tonal reference, not a pick list.
Claude reads them to understand the range and register of the project,
then invents characters inspired by them — not copied from them.
The pools define the flavour of each archetype, the kinds of roles
that belong in it, the material textures and prop logic that fit.
Claude synthesises from them freely.

Weighted random selection is retained for the local (non-Claude) generation path only.
"""

import random

# ── LOCKED STYLE DNA ──────────────────────────────────────────────────────────
# This string is embedded in every assembled prompt.
# It is never overridden by archetype.
STYLE_DNA = (
    "Stylized 2D character illustration, bold clean ink outlines, graphic inking style, "
    "clean but expressive linework, not sketchy, not painterly, strong silhouette, "
    "flat cel shading, deeply muted and desaturated palette anchored in shadow register, "
    "dark world — colours are bruised, industrial, aged, stained — not bright or clean, "
    "strong defined shadow shapes, sparse deliberate highlight accents only, "
    "angular but grounded human proportions, "
    "no glossy rendering, no pastels, no bright primaries, no animals, "
    "understated punk influence, medieval-institutional and bureaucratic themes, "
    "dark ages setting with pseudo-mechanical technology — bellows, gears, "
    "waterwheel-driven machinery, alchemical apparatus, hand-cranked mechanisms"
)

# ── ARCHETYPES ─────────────────────────────────────────────────────────────────
# Each archetype contains vocabulary pools.
# Claude uses these as tonal reference — not as a pick list.
# The label, palette_hint, and style_flex set the register.
# roles/garments/props/details/personalities are example vocabulary.

ARCHETYPES = {

    "guild_civic": {
        "label": "Guild Official / Civic Enforcer",
        "palette_hint": (
            "soot black, tarnished iron grey, dried-blood burgundy, "
            "aged parchment yellow, deep forest green — all heavily shadowed"
        ),
        "style_flex": (
            "worn natural materials — rough wool, oiled leather, riveted straps — "
            "guild insignia in hammered metal or wax seal, documents and ledgers as weapons of authority, "
            "hand-forged mechanical devices: gear-driven toll counters, bellows-powered stamp presses"
        ),
        "era_notes": (
            "Medieval-proto-industrial. Guilds, toll roads, city gates, market inspection. "
            "Bureaucracy enforced through parchment, wax, and blunt authority. "
            "Early mechanical devices serve the guild — lever-operated weighing machines, "
            "chain-driven archive lifts, waterwheel-powered mint presses."
        ),
        "roles": [
            "Market Weights and Measures Inspector, lower quarter",
            "Guild Tax Collector, Third District — the district nobody wants",
            "Harbour Master's Deputy (the Harbour Master is never present)",
            "Road Toll Warden, the unpopular bridge",
            "Crown Census Taker, reassigned to the outer parishes",
            "City Gate Permit Officer, north wall",
            "Dungeon Records Clerk (administrative dungeon, mostly paperwork)",
            "Healer's Guild Licensing Officer — no one heals without his seal",
            "Cartographers' Guild Field Verifier, disputed borders",
            "Archive Monk reassigned to civil enforcement against his will",
            "Prison Warden, minimum security, maximum tedium",
            "Forge Guild Compliance Inspector — checks every anvil in the ward",
            "Mill Levy Collector, disputed jurisdiction between two lords",
            "City Watch Constable, lowest precinct, night shift",
            "Court Scribe between courts, indefinitely reassigned",
            "Gear-Works Patent Registrar — logs every cog and cam",
            "Aqueduct Flow Warden — controls the sluice gates",
            "Guild Seal Authenticator — the forgers hate him specifically",
        ],
        "personalities": [
            "enforces laws older than anyone alive, never questions them",
            "interprets every situation through the lens of guild bylaws written in dead dialect",
            "suspicious of anything that cannot be taxed, weighed, or stamped",
            "deeply loyal to a crown he has never been close to",
            "pragmatic about the supernatural — it still needs to be registered",
            "profoundly tired of everyone who thinks their case is exceptional",
            "treats dragons as a permit violation and acts accordingly",
            "the only person in the precinct who does the paperwork correctly",
            "a minor bureaucratic grievance has defined the last decade of his life",
            "quietly furious at a system he nonetheless serves without question",
            "believes that mechanisms are more honest than men, and acts on it",
            "mourns the old hand-written registers, despises the new gear-printed ones",
        ],
        "garments": [
            "rough wool tabard over a padded linen undershirt, guild badge riveted at the chest",
            "long oiled canvas travel coat with city seal pressed into the breast leather",
            "layered travelling clothes, document pouches stitched into the belt lining",
            "dark robes with guild colours at the hem and cuffs, heavily stained at the knees",
            "guard's worn half-plate over civilian clothes, neither fish nor fowl",
            "heavy wool coat with rank-tab at the collar, mismatched toggles from two different uniforms",
            "structured leather jerkin over a linen shirt, sealed with cracked wax at the shoulder",
            "chainmail shirt visible under a stained civic surcoat, more habit than necessity",
        ],
        "props": [
            "wax seal stamp on a cord at the neck, used constantly",
            "scroll case always at capacity, leather cracking",
            "short baton of authority — never a weapon, almost never",
            "coin scale and weights in a worn leather pouch, calibrated weekly",
            "city map on vellum covered in personal grievance annotations",
            "quill in a belt loop, ink on the fingers permanently",
            "lantern, oil almost gone, wick trimmed with a small knife",
            "a bundle of overdue notices tied with hempen cord",
            "a hand-cranked counter mechanism clipped to the belt, tallying something",
            "a brass guild compass, needle trembling, magnetic lodestone cracked",
        ],
        "details": [
            "guild mark branded on the wrist, partially faded",
            "boots repaired so many times the original leather is a rumour",
            "a belt buckle carrying a heraldic device that is subtly wrong",
            "dried mud at the hem — official travel, not pleasure",
            "a thin chain with a small official seal tucked inside the collar",
            "ink stains on the right-hand fingertips, deep and permanent",
            "a scar from a minor bureaucratic altercation, never explained",
            "a gear-tooth pendant — guild of mechanists, junior rank",
        ],
    },

    "manufactory": {
        "label": "Forge-Works / Proto-Industrial",
        "palette_hint": (
            "coal black, deep rust orange, tarnished brass, dark engine-room green, "
            "smoked brown — palette of furnace light and shadow, no brightness"
        ),
        "style_flex": (
            "heavy forge detail — rivets, bellows gauges, soot-stained fabric, "
            "waterwheel-driven mechanicals, furnace-glow ambience, "
            "hand-hammered brass fittings and gear assemblies, woodcut typography sensibility"
        ),
        "era_notes": (
            "Medieval forge-industrial. Foundries, charcoal kilns, waterwheel-powered workshops, "
            "bellows-driven forge complexes, canal lock systems, early gear-works manufactories. "
            "Steam exists but is crude — sealed copper boilers, hand-riveted, prone to failure. "
            "Print exists as woodblock and hand-set moveable type. Technology is heavy, dark, "
            "mechanical, and old — not shiny or decorative."
        ),
        "roles": [
            "Boiler Inspection Officer, second foundry district",
            "Bellows Authority Warden — regulates forge air supply",
            "Print Works Night Foreman, woodblock division",
            "Furnace Lamp Maintenance Supervisor, deep shift",
            "Pneumatic Post Routing Clerk — bellows-driven capsule mail",
            "Canal Lock Dispatch Coordinator",
            "Foundry Quality Control Agent — tests every ingot",
            "Dock Authority Cargo Manifest Officer, river trade",
            "Charcoal Levy Collector, kiln-side operations",
            "Mechanical Licensing Examiner — no gear turns without his mark",
            "Broadside Censorship Bureau Field Agent",
            "Forge Safety Inspector (enforcement, not prevention)",
            "Difference Engine Maintenance Technician — the oak-framed kind",
            "Semaphore Tower Operator, overnight shift",
            "Mine Survey and Compliance Officer, tunnel division",
            "Waterwheel Power Allocation Warden",
            "Gear-Cutter's Guild Master, retired but still showing up",
        ],
        "personalities": [
            "devoted to hand-craft process in a world going mechanical",
            "catalogues every mechanism, understands only some of them",
            "believes in progress, defines it very narrowly and defensively",
            "trusts mechanisms more than people, for documented reasons",
            "formal to the point where the formality itself becomes the problem",
            "administers rules written for a technology that has since changed twice",
            "proud of a rank that means something different than it used to",
            "the bureaucracy of forge expansion, taken completely seriously",
            "mourning a craft tradition while enforcing the thing that replaced it",
            "absolutely certain the current gear-works are sound, despite the noises",
            "smells permanently of charcoal and hot brass, has stopped noticing",
        ],
        "garments": [
            "high-collared inspector's coat with brass toggle closures, soot at the cuffs",
            "long forge-master's coat with epaulettes and embossed buttons, worn at the elbows",
            "wool field jacket with map-pocket detailing and tarnished brass compass clips",
            "structured leather apron over a formal waistcoat — caught between two worlds",
            "heavy canvas work coat over chainmail links at the collar — old habit",
            "military-cut uniform with a small gear-driven instrument panel strapped at the forearm",
            "soot-darkened surcoat with foundry guild insignia in punched copper",
        ],
        "props": [
            "pocket sundial on a heavy chain, checked and re-checked against the bell tower",
            "mechanical calculation device worn at the hip, dented, hand-cranked",
            "rolled survey maps on vellum secured with a leather thong",
            "a logbook with marbled covers and a ribbon bookmark, filled in charcoal pencil",
            "a signal lantern, folded compact, belt-clipped, smelling of tallow",
            "a small boiler pressure gauge removed as evidence of negligence",
            "a printed citation form — woodblock, smudged — half-filled",
            "a speaking tube end clipped at the lapel, connecting to nothing now",
            "a hand-forged caliper with guild marks on both jaws",
        ],
        "details": [
            "ink stains suggesting extensive map annotation and revision",
            "a conductor's punch worn as a lapel pin, guild tradition",
            "an expired expedition medallion, never removed",
            "boot buckles where laces would be expected — forge-district fashion",
            "collar studs of mismatched metals — salvage, not fashion",
            "burn mark on the left cuff from a boiler inspection gone wrong",
            "a rank sash in a colour whose meaning has been reclassified twice",
            "exposed gear mechanism at the cuff, ornamental now but once functional",
            "calluses specific to bellows operation — thick at the heel of the palm",
        ],
    },

    "feudal_administration": {
        "label": "Feudal Administration / Crown Clerk",
        "palette_hint": (
            "deep monastery brown, faded ecclesiastical purple, aged vellum cream darkened to umber, "
            "iron-gall ink black, tarnished silver — shadowed, solemn, the colour of power held in parchment"
        ),
        "style_flex": (
            "structured clerical robes and administrative vestments, wax-sealed authority, "
            "the aesthetic of feudal power exercised through literacy and record-keeping, "
            "mechanical filing apparatus — gear-driven scroll racks, lever-operated archive lifts"
        ),
        "era_notes": (
            "Feudal administration in decay. Castle record-keepers, crown clerks, tithe collectors, "
            "magistrate's scribes, parish registrars. The entire apparatus of feudal governance "
            "executed through parchment, seal, and increasingly through mechanical filing systems "
            "that nobody fully understands anymore. Waterwheel-powered document presses stamp "
            "edicts by the hundred. Gear-driven archive retrieval systems creak and jam."
        ),
        "roles": [
            "Crown Tithe Collector, rural parishes — never welcome",
            "Castle Records Keeper, tower archive, alone with the dust",
            "Magistrate's Scribe, circuit court — rides between towns",
            "Parish Birth and Death Registrar, three villages",
            "Exchequer Clerk, coin-counting division",
            "Royal Seal Bearer, minor court — carries authority he cannot use",
            "Land Survey Officer, disputed boundaries between two lords",
            "Heraldic Registry Clerk — verifies every crest, corrects every pretender",
            "Monastery Ledger Auditor — the monks resent him specifically",
            "Feudal Debt Recorder — knows who owes what to whom, says nothing",
            "Bailiff's Correspondence Secretary — writes the letters nobody wants to receive",
            "Writ of Passage Clerk, border crossing — stamps and questions",
            "Archive Mechanism Operator — feeds documents into the gear-driven filing engine",
            "Seal Wax Procurement Officer — a job that matters more than it sounds",
            "Judicial Torture Record Keeper (clerical role, not operational, he insists)",
        ],
        "personalities": [
            "literate in a world where that is power, and wields it quietly",
            "believes the parchment record is more real than the event it describes",
            "loyal to the institution of the crown, not to whoever wears it",
            "has read every charter in the archive and trusts none of them",
            "genuinely believes that good record-keeping prevents wars",
            "treats every peasant complaint as a filing exercise",
            "haunted by a clerical error made seven years ago that may have changed a border",
            "incorruptible — not from virtue but from an inability to deviate from procedure",
            "despises the new mechanical filing systems but admits they are faster",
            "knows the old tongue, reads it in documents no one else can, tells no one what they say",
            "has outlasted four lords, two plagues, and one attempted reform of the tax code",
        ],
        "garments": [
            "long dark clerical robe with administrative rank-cord at the waist, ink-stained hem",
            "heavy travelling cloak over a structured tunic, document case built into the lining",
            "formal vestment of the exchequer, threadbare at the elbows, never replaced",
            "layered scholar's robes with fur trim — the fur is older than the wearer",
            "administrative surcoat bearing the lesser crown seal, faded to near-invisibility",
            "plain dark wool habit with a single brass clasp denoting rank within the registry",
            "castle clerk's half-robe over practical travelling clothes, mud at the boots",
        ],
        "props": [
            "iron-gall ink horn stoppered with wax, chained to the belt",
            "wax seal matrix bearing the lesser crown device, warm from recent use",
            "leather document case with multiple compartments, never out of reach",
            "quill knife worn at the hip — sharpens quills, occasionally threatens",
            "a hand-cranked document numbering stamp, gear-driven, heavy",
            "vellum scroll of authority, unrolled only when absolutely necessary",
            "a tally stick notched with debts owed, thick as a forearm",
            "a brass key to an archive nobody else is permitted to enter",
            "sand-shaker for drying ink, nearly empty, irreplaceable",
        ],
        "details": [
            "fingers permanently stained with iron-gall ink, deep blue-black",
            "a chain of office so tarnished it reads as decorative rope",
            "squint lines from decades of reading by candlelight",
            "a wax seal impression pressed into the leather of the belt as personal mark",
            "robes hemmed shorter on one side from years of climbing archive ladders",
            "a small burn scar from a candle accident in the scriptorium",
            "calluses on the middle finger from a lifetime of quill pressure",
            "a saint's medallion tucked inside the collar — superstition, not faith",
        ],
    },

    "shadow_guild": {
        "label": "Shadow Guild / Thieves' Quarter",
        "palette_hint": (
            "deep noir black, bruised plum, dark amber under-light from tallow flame, "
            "dirty tarnished gold, dried blood red — shadow as profession"
        ),
        "style_flex": (
            "heavier shadows, more angular ink strokes, "
            "high contrast pools of dark, clothing chosen to disappear in, "
            "concealed tools and lock-picks, forged guild seals, alchemical residue"
        ),
        "era_notes": (
            "Medieval underworld — smugglers at city gates, fence-masters in market cellars, "
            "forgers of guild seals, unlicensed alchemists, black-market relic dealers, "
            "sewer-route couriers, lock-breakers for hire. Criminal infrastructure that mirrors "
            "the legitimate guild system — shadow guilds with their own ranks, codes, and "
            "mechanical contraptions: hidden compartment mechanisms, gear-locked strongboxes, "
            "alchemical smoke devices, spring-loaded concealment rigs."
        ),
        "roles": [
            "Fence-Master, cathedral quarter — moves relics, no questions",
            "Forger of guild seals and writs of passage, impeccable work",
            "Unlicensed alchemist, back-alley distillation, mostly poisons",
            "Black-market relic dealer — saints' bones a specialty",
            "Sewer-route courier, knows every drain and culvert in the old city",
            "Lock-breaker for hire — guild-trained, guild-expelled",
            "Smuggler at the river gate, bribes the night watch regularly",
            "Contraband ledger keeper, impeccable handwriting, no names",
            "Debt collector for the shadow guild — persuasion, then other methods",
            "Information broker in the market square, sells to all sides",
            "Tunnel-digger, specialty: under walls and into vaults",
            "Counterfeit coin-clipper, silver specialty",
            "Professional alibi witness — sworn testimony, reasonable rates",
            "Thieves' Quarter quartermaster — supplies the tools of the trade",
            "Poison-taster for hire — tests food for the paranoid wealthy",
        ],
        "personalities": [
            "professional and quiet — dangerously so",
            "genuinely believes all of it is victimless, or at least victim-deserving",
            "tired of being interesting, wants a quiet shop somewhere legitimate",
            "meticulous, methodical, allergic to improvisation of any kind",
            "surprisingly principled within a very narrow moral framework",
            "deeply nostalgic for a criminal golden age under the old king",
            "paranoid in a way that has, so far, kept him alive through two purges",
            "cheerful in a way that makes everyone uncomfortable and suspicious",
            "speaks rarely, always specifically, remembers everything",
            "morally flexible but personally very tidy about his workspace",
            "treats his craft — forgery — as a higher art than the originals",
        ],
        "garments": [
            "nondescript dark wool cloak, intentionally forgettable in every detail",
            "hooded travelling coat, no guild marks, no heraldry, nothing to remember",
            "leather jerkin worn soft through years of use, blade-scored at the ribs",
            "loose dark linen shirt and breeches — tavern casual, somehow threatening",
            "workman's coat with a false trade badge, faded beyond identification",
            "layered dark clothing with hidden pockets sewn into every seam",
            "monk's habit worn as disguise — convincing until you see the boots",
        ],
        "props": [
            "a set of lock-picks rolled in oiled cloth, worn smooth at the handles",
            "a thin-bladed knife designed for prying, not fighting",
            "a forged guild seal, still wet with wax",
            "a glass vial of something that should not be carried openly",
            "a purse of clipped coins, each one a fraction lighter than legal",
            "a tallow candle stub and a striker — he works in the dark",
            "a small spring-loaded compartment mechanism, palm-sized, for concealment",
            "a knotted rope with a grapple, coiled at the hip",
            "a coded tally-stick that means nothing to anyone except the right person",
        ],
        "details": [
            "a faint scar along the jawline, old, from a deal gone wrong",
            "fingers stained with alchemical reagents — silver nitrate, probably",
            "boots with soft soles — made for silence, not for distance",
            "a ring that might be a signet of a guild that does not officially exist",
            "clothing deliberately worn loose to conceal movement",
            "hands that are very still, always, even when the rest of him is not",
            "a visible tension in the jaw, controlled but permanent",
            "a brand mark on the palm — punishment, worn as credential",
        ],
    },

    "garrison_military": {
        "label": "Garrison / Levy / Mercenary Company",
        "palette_hint": (
            "deep olive drab, dark military earth, muted iron grey, faded gambeson tan, "
            "cold steel — weathered, functional, no shine, no polish"
        ),
        "style_flex": (
            "rigid posture, hard shadow edges, armour and gear details worn and functional, "
            "clothing worn as defence even when it is not armour — padded, layered, reinforced. "
            "Siege engineering hardware, crossbow mechanisms, gear-driven winches"
        ),
        "era_notes": (
            "Medieval military — disbanded knights, siege engineers, castle garrison watch, "
            "border wardens, crossbow companies gone mercenary, levy soldiers who never went home. "
            "Military technology is mechanical and brutal: counterweight trebuchets, "
            "gear-cranked crossbow windlasses, siege tower mechanisms, waterwheel-powered "
            "bolt forges. War machines are made of oak, iron, rope, and ingenuity."
        ),
        "roles": [
            "Retired sergeant-at-arms, still conducts himself as one",
            "Mercenary company quartermaster, vague loyalties",
            "Demobilised levy soldier, never given leave to return home",
            "Castle garrison watch captain, night shift, skeleton crew",
            "Siege engineer without a siege, maintaining equipment nobody will use",
            "Border warden at a crossing nobody uses anymore",
            "Crossbow company sergeant, the company disbanded but he kept the rank",
            "Military logistics officer who controls supply routes quietly",
            "Siege engine maintenance technician — keeps the trebuchets greased",
            "Castle guard investigator, permanent expression of suspicion",
            "Quartermaster who knows where every barrel and bolt is and tells nobody",
            "Scout-captain with nothing left to scout, walks the perimeter anyway",
            "Veteran field surgeon now patching civilians, poorly",
            "Drill master with no recruits, drills himself at dawn",
            "Garrison armourer — sharpens blades for men who will not fight",
            "Toll-bridge guard, military posting, civilian reality",
        ],
        "personalities": [
            "mission-oriented in situations that have no mission",
            "built for a siege that has not come and probably will not",
            "treats all civilian chaos as a solvable tactical problem",
            "loyalty as a character flaw when there is no lord to be loyal to",
            "speaks only in brief declarative sentences, expects compliance",
            "hyper-observant, constantly assessing threats in market squares",
            "quietly devastated that peace is this tedious and this poorly administered",
            "structured to the point of fragility when the structure breaks down",
            "carries the weight of a decision made at a ford five years ago",
            "profoundly calm in a way that makes civilians nervous and magistrates uneasy",
            "still wearing the gambeson because nothing else fits right anymore",
        ],
        "garments": [
            "worn gambeson with subdued company patches, riveted at the shoulders",
            "half-plate over civilian clothes — halfway out of service, never fully",
            "military surcoat with faded heraldry, no lord to serve but still wearing it",
            "chainmail hauberk under a plain dark travelling cloak, weight visible in the posture",
            "padded arming jacket worn as daily clothing, sword belt empty",
            "heavy wool military cloak with iron clasp, rank indicated by its absence",
            "leather brigandine with steel plates showing through worn fabric",
        ],
        "props": [
            "hand-drawn map on hide, terrain marked from memory, out of date",
            "a whetstone carried like a talisman, worn to a sliver",
            "battered water skin, military issue, still serviceable",
            "field notebook on wax tablet, entries in very small scratched letters",
            "dog tags — metal identity discs on a leather cord at the collar",
            "a heavy key to a garrison armoury that may or may not still exist",
            "crossbow windlass at the belt, functional but unused",
            "a dented helm carried rather than worn, one more dent than is safe",
        ],
        "details": [
            "company insignia partially scraped off — removed, not replaced",
            "boots in impeccable condition despite everything else falling apart",
            "posture so correct it reads as defiance in a civilian context",
            "a fading tattoo on the forearm — company mark, partially visible",
            "rank indicated by absence — blank where insignia was removed",
            "a subtle limp that is never acknowledged and never explained",
            "a sword callus on the right hand, no sword",
            "chainmail showing at the collar — underneath everything, always",
        ],
    },

    "collapsed_order": {
        "label": "Collapsed Order / Fallen Apparatus",
        "palette_hint": (
            "desaturated verdigris green, deep charcoal, toxic alchemical yellow accent, "
            "oxidised copper, dim bruised cyan — "
            "the palette of mechanisms that used to work and colours that used to be brighter"
        ),
        "style_flex": (
            "structured lines with visible decay, institutional insignia on everything, "
            "worn and failing mechanical devices, documentation as ritual rather than function. "
            "This is where the pseudo-tech lives heaviest — gear-driven automata still performing "
            "duties nobody assigned, clockwork filing systems grinding on empty"
        ),
        "era_notes": (
            "The remnants of a once-great bureaucratic order, now running on inertia and "
            "broken mechanisms. This was a medieval empire that built magnificent mechanical "
            "systems — gear-driven census engines, waterwheel-powered document presses, "
            "clockwork messengers, pneumatic tube networks driven by bellows, automaton sentries "
            "wound by key. The empire collapsed. The mechanisms did not stop. They grind on, "
            "purposeless, tended by officials who no longer understand what they serve. "
            "The pseudo-tech here is at its densest and most melancholy."
        ),
        "roles": [
            "Automaton Winding Officer, third ward — winds the sentries that guard nothing",
            "Gear Census Engine Operator — feeds names into a machine, the machine does unknown things",
            "Pneumatic Capsule Routing Clerk — the bellows-mail still runs, mostly to empty offices",
            "Clockwork Messenger Maintenance Warden — repairs couriers whose destinations no longer exist",
            "Decommissioned Order Clerk, still reporting for duty by habit",
            "Collapsed Authority Loyalty Assessor — assesses loyalty to a dissolved institution",
            "Atmospheric Bellows Processor Maintenance Warden — keeps the forge-air flowing",
            "Registry Mechanism Operator — the gear-driven filing engine still sorts, nobody retrieves",
            "Ration Distribution Supervisor — distributes from stockpiles laid down by the old order",
            "Perimeter Warden, abandoned zone — patrols a boundary that exists on no current map",
            "Expired Mandate Enforcement Agent — enforces edicts from a court that dissolved",
            "Mechanical Census Advocate — argues on behalf of citizens the census engine has lost",
            "Seal Verification Technician — authenticates seals of an authority that no longer issues them",
            "Archive Engine Stoker — feeds coal to the machine that reads nothing",
            "Bell Tower Automation Keeper — the bells ring on schedule, the schedule is wrong",
        ],
        "personalities": [
            "faithfully executing a mandate that stopped making sense decades ago",
            "aware the order collapsed, filing the correct forms anyway out of devotion",
            "loyalty to an institution that dissolved before he was born, inherited like debt",
            "quietly malfunctioning in ways only he notices, like the mechanisms he tends",
            "optimised for efficiency in a world defined by entropy and rust",
            "nostalgic for a version of the order that existed only in the chronicles",
            "believes the documentation is more real than the events it once described",
            "processes everything through a lens of protocol that is three rulers out of date",
            "the last true believer in an order that was discredited before the plague",
            "performs the rituals of administration for their own sake, beautifully",
            "finds genuine comfort in the sound of gears turning, even purposelessly",
        ],
        "garments": [
            "order-issue surcoat with zone identification strip on the sleeve, faded past reading",
            "institutional uniform with an integrated brass rank-plate, tarnished green",
            "retrofitted administrative robe with sealed seams and defunct mechanical ports",
            "heavy warden's coat with authority patches from a dissolved bureau, still sewn on",
            "long coat of treated canvas with mechanism maintenance loops, tools mostly missing",
            "formal vestment of the old order, moth-eaten at the hem, pressed with care",
            "mechanic's apron over clerical robes — the hybrid dress of the apparatus keeper",
        ],
        "props": [
            "a gear-driven filing device showing a persistent jam that cannot be cleared",
            "a hand-cranked scanner mechanism with a cracked lens, still calibrated",
            "a brass key-card for a mechanism that may or may not still engage",
            "a portable citation stamp, gear-driven, out of ink but still stamping",
            "a bellows-maintenance toolkit in an oiled roll, every tool accounted for",
            "a laminated writ of authority for something no longer within anyone's authority",
            "a clockwork messenger pigeon, wound down, carried like a dead pet",
            "an automaton winding key, heavy brass, worn smooth at the grip",
            "a tally of mechanisms still operational — the list gets shorter every season",
        ],
        "details": [
            "zone identification number stencilled on the back of the collar, faded",
            "a gear-tooth brand on the wrist — order initiation mark, still legible",
            "an authority indicator pin whose colour has faded to ambiguous",
            "a patch where an order insignia was removed, outline still visible in the fabric",
            "one sleeve rolled up around a brass mechanism interface, non-functional",
            "boots that are order-issue and have never been replaced because nothing else fits",
            "grease under the fingernails — mechanism maintenance, permanent",
            "a distant look when the gears turn — listening for something in the rhythm",
        ],
    },

    "common_quarter": {
        "label": "Common Quarter / Market Folk",
        "palette_hint": (
            "faded ochre, worn tobacco brown, dark hearth-smoke grey, "
            "deep dyed wool blue, stained rust — the palette of things used until they give out"
        ),
        "style_flex": (
            "looser ink lines, layered clothing, lived-in textures, nothing new, "
            "mended and re-mended, functional and familiar. Everyday medieval — "
            "woodsmoke, leather, tallow, damp wool, cobblestones, market stalls"
        ),
        "era_notes": (
            "Medieval common folk. Market porters, canal boatmen, wall-menders, "
            "alehouse regulars, parish bell-ringers, charcoal burners, tanners, "
            "night-soil collectors, street criers. The ordinary people of a dark world "
            "that smells of woodsmoke, leather, and wet stone. Their technology is simple "
            "and practical — block and tackle, hand-bellows, treadwheel cranes, "
            "lever presses, and the occasional gear mechanism they do not fully trust."
        ),
        "roles": [
            "Market porter, dawn shift — carries what others will not",
            "Canal boatman, night freight, asks no questions about cargo",
            "Wall-mender, city fortifications — never runs out of work",
            "Alehouse keeper, the one near the gate — hears everything",
            "Parish bell-ringer, three churches — the only one who can reach all three in time",
            "Charcoal burner, forest edge — comes to market smelling of smoke and solitude",
            "Tanner's apprentice, middle-aged — never promoted, never left",
            "Night-soil collector, philosophical about the work",
            "Street crier, official — reads proclamations nobody listens to",
            "Market stall holder, candles and tallow — knows everyone's business by lamplight",
            "Cobbler who repairs more than shoes, discreetly",
            "Lamplighter, tallow and oil — walks the same route every dusk",
            "Grave-digger, parish grounds — counts his work by the season",
            "Ferryman at the low crossing — one boat, two oars, no hurry",
            "Rat-catcher, licensed — the license cost more than the rats",
        ],
        "personalities": [
            "deeply philosophical about things that do not matter to anyone else",
            "convinced the city council is conspiring against specifically him and his lane",
            "aggressively generous in ways nobody asked for and cannot refuse",
            "haunted by a minor social mistake at the harvest festival three years ago",
            "cheerfully oblivious to all social distinctions, treats lords like neighbours",
            "catalogues every injustice from the guild masters, acts on none of them",
            "suspicious of anything introduced after the old king died",
            "communicates primarily through meaningful silences and loaded grunts",
            "maintains an elaborate personal honour code that nobody else recognises",
            "strong opinions on everything, expertise in nothing except his one trade",
            "knows every shortcut, every back alley, every loose stone in the wall",
        ],
        "garments": [
            "oversized wool cloak with too many sewn-in pockets, all full of something",
            "heavy linen shirt over a patched undershirt, untucked deliberately",
            "worn leather jerkin, inherited from someone larger",
            "long coat that was fine once, bought from a pawnbroker years ago",
            "layered work clothing in various stages of retirement and repair",
            "rough-spun hood and travelling cloak, no dye, no embellishment",
            "apron over everyday clothes — trade-stained, never removed in public",
        ],
        "props": [
            "a sack containing a smaller sack containing something wrapped in cloth",
            "a clay pipe, unlit, held between the teeth as punctuation",
            "a leather flask of something that is not water",
            "a walking stick with notches — counting something, won't say what",
            "a small hand-bell, cracked, still rung at the appointed hour",
            "a net of root vegetables, carried everywhere, offered to no one",
            "a hand-lantern with a tallow candle, smelling of animal fat",
            "a worn coin purse with very few coins, counted often",
        ],
        "details": [
            "squint from years of smoky rooms and poor light",
            "one trouser leg hemmed shorter than the other, permanently",
            "a rough bandage on a knuckle, origin unimportant",
            "a ring of keys on a cord at the belt, most of them for doors that still exist",
            "a pilgrim's badge pinned to the hat — the pilgrimage was short and local",
            "permanent charcoal smudge at the temple, wiped and reappearing",
            "hands roughened by rope, or oar, or stone — the calluses tell the trade",
            "a tooth missing in a way that suggests a story he is tired of telling",
        ],
    },
}

# ── SHARED POOLS ───────────────────────────────────────────────────────────────
# Used by local (non-Claude) generation path.
# Claude reads these as vocabulary reference only.

BODY_TYPES = [
    "lean and angular, all sharp lines and hard edges",
    "stocky and solid, low centre of gravity, built for labour",
    "tall and slightly stooped, as if apologising for the height",
    "average build, completely unremarkable by design",
    "broad-shouldered but soft-edged, strength going to seed",
    "wiry and compact, coiled energy, quick hands",
    "heavyset with authority, takes up the right amount of space",
    "slight and precise, every gesture economical",
    "barrel-chested and unhurried, built for endurance not speed",
    "rangy, long-limbed, moves like something unfolded from a cramped space",
]

AGES = [
    "early 30s — young enough to still care, old enough to start doubting",
    "mid 40s — peak competence, peak disillusionment",
    "late 50s — past caring about the right things, still showing up",
    "early 60s — one foot out, holding the door for no one",
    "late 20s — hasn't been ground down yet, process clearly beginning",
    "mid 30s — recently realised this is permanent",
    "50s — the decade when the system finally admitted what it was",
]

GENDERS = [
    "man", "woman", "person", "man", "woman",
]

MOODS = [
    "emotionally detached, blank thousand-yard stare",
    "smoldering barely-contained fury held under rigid discipline",
    "deep bone-tired exhaustion, eyes carrying decades of disappointment",
    "suspicious narrowed eyes, perpetually expects rule infractions or worse",
    "bitter resigned contempt for the absurdity of everything",
    "muted defiance — knows the system is broken, serves it anyway",
    "quiet satisfaction at a minor procedural victory, the only kind available",
    "haunted look of someone who remembers when this all made sense",
    "studied neutrality masking complete internal chaos",
    "the particular blankness of someone copying a ledger entry for the hundredth time",
    "cold professional calm that has replaced all previous emotions",
    "the look of a person who has stopped expecting anything from anyone",
]

POSTURES = [
    "hands in pockets, slouched but somehow commanding",
    "arms crossed, weight shifted to one foot, waiting for an excuse",
    "hands clasped behind the back, rigid parade rest",
    "one hand resting on a belt item, scanning the crowd slowly",
    "slight forward lean, stillness as subtle threat",
    "standing very still in a way that suggests readiness for anything",
    "weight evenly distributed, no tells, no fidgeting",
    "one shoulder slightly higher — a long-standing asymmetry from old labour",
    "feet planted wide, immovable by design and by temperament",
]

# ── BACKGROUNDS ────────────────────────────────────────────────────────────────
# All backgrounds are dark. No pastels. No light backgrounds.
# These are flat colour fields — near-black, deep industrial, bruised.
BACKGROUNDS = [
    "flat near-black void",
    "flat deep charcoal, almost black",
    "flat dark forge-smoke grey",
    "flat deep bruised slate",
    "flat dark furnace-shadow green",
    "flat deep soot brown",
    "flat dark institutional teal, heavily shadowed",
    "flat deep rust-stained umber",
    "flat dark olive-black",
    "flat cold iron grey",
    "flat very dark midnight blue, near-black",
    "flat deep coal black with slight warm hearth undertone",
]

SETTINGS = [
    None, None, None,
    "shadow of iron bars across the lower background",
    "faint suggestion of tallow lamp glow above, amber and dim",
    "worn stone floor plane visible at the feet, flagstone",
    "distant queue implied by shadow shapes, waiting",
    "muted archway geometry behind the figure, dark stone",
    "chain-link or iron fence shadow across a dark background",
    "suggestion of forge ironwork in deep shadow behind",
    "cobblestone ground plane, wet with rain, dark",
    "heavy wooden door frame behind, iron-banded, slightly ajar",
]


# ── WEIGHTED RANDOM SELECTION ──────────────────────────────────────────────────

def weighted_pick(items: list, weights: dict) -> str:
    if not weights:
        return random.choice(items)
    w = [weights.get(item, 1.0) for item in items]
    return random.choices(items, weights=w, k=1)[0]


def build_character(archetype_key: str = None, overrides: dict = None,
                    combo_weights: dict = None) -> dict:
    """
    Build a full character dict for local (non-Claude) generation.
    Claude generation uses generate_character_async in claude_worker.py instead.
    overrides: any keys to force
    combo_weights: dict of item -> float from the learning system
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
        "era_notes": arch.get("era_notes", ""),
        "name": ov.get("name", ""),
        "extra": ov.get("extra", ""),
    }
    return char


def assemble_prompt(char: dict) -> str:
    """Turn a character dict into a full image generation prompt."""
    name_line = f"Character is {char['name']}, a " if char["name"] else "Character is a "
    name_line += f"{char['age']} {char['gender']} working as a {char['role']}."

    personality_line = f"Personality informs appearance: {char['personality']}."

    costume_line = (
        f"Wearing {char['garment']}, {char['style_flex']}, "
        f"with {char['detail']}. Carries {char['prop']}."
    )

    body_line = f"Build: {char['body_type']}."
    pose_line = f"Pose: {char['posture']}."
    mood_line = f"Expression: {char['mood']}."

    bg_line = f"{char['background']} background"
    if char["setting_hint"]:
        bg_line += f", {char['setting_hint']}"
    bg_line += "."

    palette_line = (
        f"Palette anchored in shadow register: {char['palette_hint']}. "
        "Dark world — colours are bruised, aged, stained. No pastels. No bright tones."
    )

    style_line = STYLE_DNA + "."

    extra_line = f"Additional notes: {char['extra']}." if char["extra"] else ""

    parts = [
        style_line, palette_line, name_line, personality_line,
        costume_line, body_line, pose_line, mood_line, bg_line,
    ]
    if extra_line:
        parts.append(extra_line)

    return "\n".join(parts)


def get_archetype_vocabulary(archetype_key: str) -> str:
    """
    Return a formatted string of the archetype's vocabulary pools
    for use as Claude context. Claude reads this as inspiration reference,
    not as a pick list.
    """
    if archetype_key not in ARCHETYPES:
        return ""
    arch = ARCHETYPES[archetype_key]
    lines = [
        f"ARCHETYPE: {arch['label']}",
        f"ERA/CONTEXT: {arch.get('era_notes', '')}",
        f"PALETTE DIRECTION: {arch['palette_hint']}",
        f"STYLE FLEX: {arch['style_flex']}",
        "",
        "ROLE VOCABULARY (reference only — invent freely within this register):",
        *[f"  • {r}" for r in arch["roles"]],
        "",
        "PERSONALITY REGISTER (examples — do not copy, draw from):",
        *[f"  • {p}" for p in arch["personalities"]],
        "",
        "GARMENT VOCABULARY:",
        *[f"  • {g}" for g in arch["garments"]],
        "",
        "PROP VOCABULARY:",
        *[f"  • {p}" for p in arch["props"]],
        "",
        "DETAIL VOCABULARY:",
        *[f"  • {d}" for d in arch["details"]],
    ]
    return "\n".join(lines)
