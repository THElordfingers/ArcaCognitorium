"""
 _______     ________  ____  _____  ______   ________  _______     ________  _______     ______                      
|_   __ \   |_   __  ||_   \|_   _||_   _ `.|_   __  ||_   __ \   |_   __  ||_   __ \  .' ____ \                     
  | |__) |    | |_ \_|  |   \ | |    | | `. \ | |_ \_|  | |__) |    | |_ \_|  | |__) | | (___ \_|   _ .--.   _   __  
  |  __ /     |  _| _   | |\ \| |    | |  | | |  _| _   |  __ /     |  _| _   |  __ /   _.____`.   [ '/'`\ \[ \ [  ] 
 _| |  \ \_  _| |__/ | _| |_\   |_  _| |_.' /_| |__/ | _| |  \ \_  _| |__/ | _| |  \ \_| \____) | _ | \__/ | \ '/ /  
|____| |___||________||_____|\____||______.'|________||____| |___||________||____| |___|\______.'(_)| ;.__/[\_:  /   
                                                                                                   [__|     \__.'    




VIGILARUM OMNIA — Visual Renderers
Pure Unicode ASCII art renderers. No external graphics.
"""

import math
from data import (SIGN_GLYPHS, SIGN_NAMES, MOON_PHASE_GLYPHS,
                  MOON_PHASE_NAMES, NAKSHATRAS, TITHI_NAMES, PLANET_GLYPHS)


def make_bar(value: float, total: float, width: int = 28) -> str:
    """░░░░████ — empty left, filled right."""
    pct    = max(0.0, min(1.0, value / total if total else 0))
    filled = int(pct * width)
    return '░' * (width - filled) + '█' * filled


def render_moon_disc(angle: float) -> str:
    """
    Correct moon disc with terminator curve.
    angle: elongation 0=new, 90=first quarter, 180=full, 270=last quarter
    Dark side = ░, transition = ▒, lit side = █
    """
    W, H = 25, 15
    cx, cy = 12, 7
    rx, ry = 11, 7
    rows = []
    for py in range(H):
        row = []
        for px in range(W):
            nx = (px - cx) / rx
            ny = (py - cy) / ry
            dist = math.sqrt(nx*nx + ny*ny)
            if dist > 1.0:
                row.append(' ')
                continue

            # Terminator x at this y level.
            # cos(angle): at 0° (new) = +1 (terminator at right edge, all dark)
            #             at 90° (1st qtr) = 0 (terminator at centre)
            #             at 180° (full) = -1 (terminator at left edge, all lit)
            #             at 270° (last qtr) = 0 (terminator at centre)
            term_x = math.cos(math.radians(angle)) * math.sqrt(max(0, 1 - ny*ny))

            waxing = angle <= 180
            # Waxing: lit side is right of terminator (nx > term_x)
            # Waning: lit side is left of terminator (nx < term_x)
            # At new moon (angle=0): term_x = sqrt(1-ny²) = right edge → nothing lit ✓
            # At full moon (angle=180): term_x = -sqrt(1-ny²) = left edge → all lit ✓
            lit = (nx > term_x) if waxing else (nx < term_x)

            if lit:
                row.append('█')
            else:
                dist_t = abs(nx - term_x)
                row.append('▒' if dist_t < 0.22 else '░')
        rows.append(''.join(row))
    return '\n'.join(rows)


def render_zodiac_wheel(lons: dict) -> str:
    """
    Zodiac wheel as a bordered square with signs around the perimeter
    and planets placed inside at their correct angular positions.
    Uses the tower's border vocabulary.
    """
    W, H = 47, 23
    canvas = [[' '] * W for _ in range(H)]

    def plot(x, y, ch):
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < W and 0 <= yi < H:
            canvas[yi][xi] = ch

    # Outer border
    for x in range(W):
        canvas[0][x]   = '─'
        canvas[H-1][x] = '─'
    for y in range(H):
        canvas[y][0]   = '│'
        canvas[y][W-1] = '│'
    canvas[0][0]     = '┌'
    canvas[0][W-1]   = '┐'
    canvas[H-1][0]   = '└'
    canvas[H-1][W-1] = '┘'

    # Inner dashed border
    for x in range(3, W-3):
        canvas[2][x]   = '╌'
        canvas[H-3][x] = '╌'
    for y in range(2, H-2):
        canvas[y][3]   = '┆'
        canvas[y][W-4] = '┊'
    canvas[2][3]     = '┌'
    canvas[2][W-4]   = '┐'
    canvas[H-3][3]   = '└'
    canvas[H-3][W-4] = '┘'

    # Place 12 signs evenly around the inner border perimeter
    # We map each sign to a position on the rectangle perimeter
    # Sign 0 (Aries) = 0°, going counter-clockwise (east on left)
    # Perimeter: top-right corner = 0°, going clockwise in sky terms
    # Standard: Aries at left (9 o'clock), CCW = Taurus above, etc.
    # We'll place them evenly along the inner box perimeter

    # Inner box bounds
    x0, x1 = 3, W-4
    y0, y1 = 2, H-3
    inner_w = x1 - x0  # 40
    inner_h = y1 - y0  # 18
    perimeter = 2 * (inner_w + inner_h)  # 116 chars

    for i, glyph in enumerate(SIGN_GLYPHS):
        # Aries (0) at 9 o'clock = left-middle, going counter-clockwise
        # Map: 0=left-mid, 1=top-left, 2=top-mid, 3=top-right, etc.
        # Angle: 0° = left (180° in standard math), each sign = 30°
        angle_deg = i * 30  # 0=Aries
        # Convert to perimeter position
        # We walk clockwise from left-middle
        # Left side: 0° to 90° CCW = left mid to bottom-left
        # Actually let's just place by angle, CCW from left-middle
        # angle 0 = left mid, 90 = bottom mid, 180 = right mid, 270 = top mid
        # (CCW in standard orientation)
        t = angle_deg / 360.0  # 0..1 around perimeter, starting left-mid, going down-CCW

        # Walk the perimeter clockwise from left-mid:
        # segment 0: left side going UP   (y: mid→top)     length = inner_h/2
        # segment 1: top going RIGHT       length = inner_w
        # segment 2: right going DOWN      length = inner_h
        # segment 3: bottom going LEFT     length = inner_w
        # segment 4: left going UP (rest)  length = inner_h/2

        half_h = inner_h / 2
        segs = [half_h, inner_w, inner_h, inner_w, half_h]
        total_p = sum(segs)
        pos = t * total_p

        # Find which segment
        acc = 0
        for seg_i, seg_len in enumerate(segs):
            if pos <= acc + seg_len:
                frac = (pos - acc) / seg_len
                if seg_i == 0:    # left going up from mid
                    x = x0; y = y0 + half_h - frac * half_h
                elif seg_i == 1:  # top going right
                    x = x0 + frac * inner_w; y = y0
                elif seg_i == 2:  # right going down
                    x = x1; y = y0 + frac * inner_h
                elif seg_i == 3:  # bottom going left
                    x = x1 - frac * inner_w; y = y1
                else:             # left going up (lower half)
                    x = x0; y = y1 - frac * half_h
                plot(x, y, glyph)
                break
            acc += seg_len

    # Place planets inside at angular positions
    cx, cy = W // 2, H // 2
    placed = {}
    order  = ["Sun","Moon","Mercury","Venus","Mars",
              "Jupiter","Saturn","Rahu","Ketu"]

    for name in order:
        if name not in lons: continue
        lon   = lons[name] % 360
        # Map lon to screen angle:
        # Aries (0°) = left (180° math), Libra (180°) = right (0° math)
        # Going CCW: lon increases CCW in the wheel
        math_angle = math.radians(180 - lon)
        base_rx = 14
        base_ry = 7

        x = cx + base_rx * math.cos(math_angle)
        y = cy + base_ry * math.sin(math_angle) * 0.85

        # Collision nudge
        xi, yi = int(round(x)), int(round(y))
        attempts = 0
        while (xi, yi) in placed and attempts < 8:
            nudge = 0.4 * (attempts + 1)
            x2 = cx + (base_rx + nudge) * math.cos(math_angle + nudge * 0.3)
            y2 = cy + (base_ry + nudge) * math.sin(math_angle + nudge * 0.3) * 0.85
            xi, yi = int(round(x2)), int(round(y2))
            attempts += 1
        if attempts < 8:
            x, y = xi, yi

        placed[(int(round(x)), int(round(y)))] = name
        plot(x, y, PLANET_GLYPHS.get(name, '·'))

    return '\n'.join(''.join(row) for row in canvas)


def render_moon_arc(angle: float, cycle_day: int) -> str:
    """
    Moon cycle arc. Phase glyphs on top row, progress bar below.
    Both exactly W characters wide (accounting for emoji width).
    Uses single-char phase markers to avoid emoji width issues.
    """
    W = 32
    # Single-char phase markers at correct positions
    phase_chars = ['N', 'c', 'D', 'G', 'F', 'g', 'C', 'n']
    phase_label = ['NM', 'WxC', 'FQ', 'WxG', 'FM', 'WnG', 'LQ', 'WnC']

    # Glyph row — 8 markers evenly spaced across W
    glyph_row = [' '] * W
    for i, ph in enumerate(MOON_PHASE_GLYPHS):
        pos = int(i / 8 * W)
        if pos < W:
            glyph_row[pos] = ph

    # But emoji are 2-wide in terminal — use the actual glyphs but accept
    # the row will be visually wider. Label row instead:
    label_row = [' '] * W
    for i, lbl in enumerate(phase_label):
        pos = int(i / 8 * W)
        for j, c in enumerate(lbl):
            if pos + j < W:
                label_row[pos + j] = c

    # Progress bar — exactly W chars
    bar = list('░' * W)
    cur = int(angle / 360 * W)
    cur = max(0, min(W-1, cur))
    for i in range(cur):
        bar[i] = '▓'
    bar[cur] = '◆'

    return '\n'.join([
        ''.join(glyph_row),
        ''.join(bar),
        f"[dim]Day {cycle_day} of 29.5  ·  {angle:.1f}°[/dim]",
        f"[dim]◄ New {'─'*10} Full {'─'*10} New ►[/dim]",
    ])


def render_nakshatra_ring(moon_lon: float, sun_lon: float) -> str:
    W = 27
    seg = 360 / 27
    moon_idx = int(moon_lon / seg) % 27
    sun_idx  = int(sun_lon  / seg) % 27
    top = []
    for i in range(27):
        if i == moon_idx:   top.append('☽')
        elif i == sun_idx:  top.append('☉')
        else:               top.append('·')
    bot = [NAKSHATRAS[i][0][0] for i in range(27)]
    return '\n'.join([
        ''.join(top),
        ''.join(bot),
        f"[dim]☽ {NAKSHATRAS[moon_idx][0]}  ·  ☉ {NAKSHATRAS[sun_idx][0]}[/dim]",
        f"[dim]27 nakshatras · 13.3° each · sidereal[/dim]",
    ])


def render_tithi_dial(tithi_num: int, paksha: str) -> str:
    W     = 30
    shukla = (paksha == "Shukla")
    bar   = []
    for i in range(W):
        if i == tithi_num:    bar.append('◆')
        elif i < 15:          bar.append('▓' if shukla else '░')
        else:                 bar.append('░' if shukla else '▓')
    tname = TITHI_NAMES[tithi_num % 15]
    return '\n'.join([
        ''.join(bar),
        f"[dim]{'▓'*5} Shukla (waxing)   {'░'*5} Krishna (waning)[/dim]",
        f"[yellow]Tithi {tithi_num+1} · {paksha} · {tname}[/yellow]",
        f"[dim]30 lunar days · ◆ = today[/dim]",
    ])


def render_eclipse_gauge(dist: float, in_season: bool) -> str:
    W   = 32
    bar = list(make_bar(max(0, 18 - dist), 18, W))
    # Mark threshold
    thresh = W - 1  # full bar = right at node
    status = "[bold yellow]⚠ ECLIPSE SEASON[/bold yellow]" if in_season \
             else "[dim]Outside eclipse season[/dim]"
    return '\n'.join([
        status,
        ''.join(bar),
        f"[dim]Sun {dist:.1f}° from nearest node (Rahu/Ketu)[/dim]",
        f"[dim]Full bar = at node · eclipses within 18°[/dim]",
    ])


def render_planet_strip(lons: dict) -> str:
    W = 36
    lines = [
        "[dim]♈        ♋        ♎        ♑       ♈[/dim]",
        "[dim]0°       90°      180°     270°    360°[/dim]",
    ]
    order = [("Sun","☉"),("Moon","☽"),("Mercury","☿"),("Venus","♀"),
             ("Mars","♂"),("Jupiter","♃"),("Saturn","♄"),
             ("Rahu","☊"),("Ketu","☋")]
    for name, glyph in order:
        if name not in lons: continue
        lon = lons[name] % 360
        pos = int(lon / 360 * W)
        row = list('┄' * W)
        row[pos] = glyph
        si  = int(lon / 30) % 12
        deg = lon % 30
        lines.append(
            f"{''.join(row)} [dim]{SIGN_NAMES[si][:3]} {deg:.0f}°[/dim]")
    return '\n'.join(lines)
