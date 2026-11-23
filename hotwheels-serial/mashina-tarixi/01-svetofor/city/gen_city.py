"""Westminster 1868 city backdrop (2D vector, 1080x1920 vertical), same style as the character sheet.
Layers (parallax): sky -> far (Parliament + clock tower) -> mid (terraced houses across the street) -> road ->
near pavement -> props (gas lamps, Knight's signal) -> foreground. Day and night variants + a staged preview.
The signal is rigged: signal_arm_L/R rotate at the mast (0 = horizontal "STOP", 55 = lowered "GO"),
signal_lamp_red / signal_lamp_green / lamp_flame_* are opacity-toggled glows.
usage: python3 gen_city.py <out_dir>"""
import os, sys, math, random
import sys as _s, os as _o; _s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "..", "characters")); import gen_characters as gen
from gen_characters import P, PF, L, C, E, G, INK, mul, mix, shade

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
W, H = 1080, 1920
R = random.Random(1868)

def grad(gid, stops, x2=0, y2=1):
    gen.DEFS[gid] = f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">' + "".join(
        f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + "</linearGradient>"
    return f"url(#{gid})"

def rect(x, y, w, h, fill, sw=3, rx=0):
    f = fill if fill.startswith("url") else shade(fill)
    s = f' stroke="{INK}" stroke-width="{sw}"' if sw else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{f}"{s}/>'

# ---------------------------------------------------------------- palettes
PAL = {
    "day": dict(sky=[(0, "#7fb3e3"), (0.55, "#b9d6ee"), (1, "#f4e3c0")], haze="#c9d6e6", hazeK=0.42, win="#3d4f6b", winHi="#9fc1e0",
                road="#8d8579", cob="#a39a8c", pave="#cdc4b2", kerb="#a59e90", lit=0.0, ink=INK),
    "night": dict(sky=[(0, "#0d1530"), (0.6, "#26305a"), (1, "#4b4a72")], haze="#2a3358", hazeK=0.5, win="#ffcf6e", winHi="#fff0b8",
                  road="#3e3c45", cob="#4f4c56", pave="#5d5a66", kerb="#4a4752", lit=1.0, ink=INK),
}

def dim(c, p, mode):  # night colour shift for lit-by-moon materials
    return mix(c, "#2b3156", 0.55) if mode == "night" else c

# ---------------------------------------------------------------- sky
def sky(mode):
    p = PAL[mode]
    s = f'<rect width="{W}" height="{H}" fill="{grad("sky_" + mode, p["sky"])}"/>'
    if mode == "day":
        s += f'<circle cx="860" cy="330" r="160" fill="#fff6dc" opacity="0.35"/><circle cx="860" cy="330" r="70" fill="#fff9e8" opacity="0.8"/>'
        for i, (x, y, k) in enumerate([(160, 300, 1.2), (620, 180, 0.9), (420, 520, 0.7), (940, 640, 0.8)]):
            s += f'<g id="cloud_{i}" transform="translate({x},{y}) scale({k})">' + \
                 PF("M -150,40 Q -160,-10 -100,-20 Q -90,-80 -20,-70 Q 30,-120 90,-70 Q 160,-80 160,-10 Q 200,10 170,40 Z", "#fdfaf2", ' opacity="0.95"') + \
                 PF("M -150,40 Q -40,58 170,40 Q 120,60 -110,58 Z", "#dfe7f2", ' opacity="0.9"') + "</g>"
    else:
        s += '<circle cx="820" cy="300" r="120" fill="#e9e6ff" opacity="0.12"/><circle cx="820" cy="300" r="54" fill="#f2efe0"/><circle cx="800" cy="288" r="9" fill="#d8d3c2"/><circle cx="836" cy="318" r="6" fill="#d8d3c2"/>'
        for i in range(90):
            x, y, r = R.uniform(0, W), R.uniform(0, 900), R.choice([1.2, 1.6, 2.2])
            s += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff8e0" opacity="{R.uniform(0.4, 1):.2f}"/>'
    return f'<g id="layer_sky">{s}</g>'

# ---------------------------------------------------------------- far: Parliament + clock tower
def far(mode):
    p = PAL[mode]
    stone = mix("#cdb58a", p["haze"], p["hazeK"])
    dark = mul(stone, 0.8)
    roofc = mix("#6f7a86", p["haze"], p["hazeK"])
    winc = mix("#46506a", p["haze"], 0.3) if mode == "day" else "#e8b766"
    base, top = 1300, 700
    s = ""
    # long facade (wider than the frame for parallax)
    s += P(f"M -400,{base} L -400,{top} L 1480,{top} L 1480,{base} Z", stone, 3)
    s += P(f"M -400,{top} L -300,{top-70} L 1380,{top-70} L 1480,{top} Z", roofc, 3)
    for x in range(-400, 1480, 80):
        s += L(f"M {x},{top} L {x},{base}", 2.5, dark)
        for wx in (x + 18, x + 44):
            for wy in (top + 30, top + 140, top + 260):
                s += P(f"M {wx},{wy+80} L {wx},{wy+20} Q {wx+9},{wy} {wx+18},{wy+20} L {wx+18},{wy+80} Z", winc, 2)
    for x in range(-400, 1480, 160):
        s += P(f"M {x-10},{base} L {x-10},{top-30} L {x+10},{top-30} L {x+10},{base} Z", stone, 2.5)
        s += P(f"M {x-12},{top-30} L {x},{top-90} L {x+12},{top-30} Z", stone, 2.5)
    s += L(f"M -400,{top+120} L 1480,{top+120}", 3, dark) + L(f"M -400,{top+240} L 1480,{top+240}", 3, dark)
    # clock tower
    tx, tw = 820, 130
    shaft = P(f"M {tx-tw/2},{base} L {tx-tw/2},470 L {tx+tw/2},470 L {tx+tw/2},{base} Z", stone, 3)
    for k in (-1, 0, 1):
        x0 = tx + k * 38 - 8
        shaft += L(f"M {tx + k*38 - 19},{base} L {tx + k*38 - 19},480", 2, dark)
        for y in range(520, base - 60, 130):
            shaft += P(f"M {x0},{y+90} L {x0},{y+20} Q {x0+8},{y} {x0+16},{y+20} L {x0+16},{y+90} Z", winc, 2)
    stage = P(f"M {tx-82},470 L {tx-82},300 L {tx+82},300 L {tx+82},470 Z", mul(stone, 1.04), 3)
    face_c = "#f6f0dc" if mode == "day" else "#ffe9a8"
    clock = C(tx, 385, 62, "#b98f45", 3) + C(tx, 385, 52, face_c, 3)
    for i in range(12):
        a = i * math.pi / 6
        clock += L(f"M {tx + 42*math.sin(a):.1f},{385 - 42*math.cos(a):.1f} L {tx + 49*math.sin(a):.1f},{385 - 49*math.cos(a):.1f}", 3)
    clock = G("clock_face", tx, 385, f'<g transform="translate({-tx},-385)">{clock}</g>' +
              G("clock_hour_hand", 0, 0, L("M 0,0 L 0,-26", 5)) + G("clock_minute_hand", 0, 0, L("M 0,0 L 0,-40", 3.5), 72) + C(0, 0, 4, INK))
    belfry = P(f"M {tx-74},300 L {tx-74},250 L {tx+74},250 L {tx+74},300 Z", stone, 3)
    for x in range(tx - 60, tx + 60, 30):
        belfry += P(f"M {x},295 L {x},268 Q {x+8},256 {x+16},268 L {x+16},295 Z", mul(stone, 0.6), 2)
    spire = P(f"M {tx-80},250 L {tx},110 L {tx+80},250 Z", roofc, 3) + L(f"M {tx},110 L {tx},250", 2.5, mul(roofc, 1.25))
    for k in (-1, 1):
        spire += P(f"M {tx+k*74-8},252 L {tx+k*74},200 L {tx+k*74+8},252 Z", stone, 2)
    spire += P(f"M {tx-6},112 L {tx},70 L {tx+6},112 Z", "#e2b64a", 2.5) + C(tx, 66, 6, "#e2b64a", 2)
    tower = f'<g id="clock_tower">{shaft}{stage}{clock}{belfry}{spire}</g>'
    return f'<g id="layer_far" data-parallax="0.15">{s}{tower}</g>'

# ---------------------------------------------------------------- mid: terraced houses across the street
HOUSE_COLS = ["#a8553e", "#e2cfa8", "#b8653e", "#d9c39a", "#8f4a3a", "#e7d9bc"]
def house(i, x, w, h, base, mode):
    p = PAL[mode]
    col = dim(HOUSE_COLS[i % len(HOUSE_COLS)], p, mode)
    brick = i % 2 == 0
    top = base - h
    s = rect(x, top, w, h, col, 3)
    if brick:
        for y in range(int(top) + 14, base, 14):
            s += L(f"M {x+3},{y} L {x+w-3},{y}", 1.2, mul(col, 0.82))
    # roof, parapet + chimneys
    roof = dim("#5d6673", p, mode)
    s += P(f"M {x-6},{top} L {x+16},{top-60} L {x+w-16},{top-60} L {x+w+6},{top} Z", roof, 3)
    s += rect(x + w * 0.42, top - 56, 34, 40, dim("#e7dcc6", p, mode), 2.5)  # dormer
    s += rect(x + w * 0.42 + 7, top - 48, 20, 26, p["win"], 2)
    for cx in (x + 18, x + w - 52):
        s += rect(cx, top - 100, 34, 48, dim("#9a5a44", p, mode), 3) + rect(cx - 4, top - 106, 42, 9, dim("#c9b9a1", p, mode), 2.5)
        for k in (0, 1):
            s += rect(cx + 4 + k * 14, top - 124, 10, 20, dim("#c26a48", p, mode), 2)
        if mode == "day":
            s += PF(f"M {cx+12},{top-128} Q {cx+2},{top-160} {cx+22},{top-178} Q {cx+40},{top-196} {cx+30},{top-226}", "none") + \
                 L(f"M {cx+12},{top-128} Q {cx+2},{top-160} {cx+22},{top-178} Q {cx+40},{top-196} {cx+30},{top-226}", 10, "#e7e2da", ' opacity="0.55"')
    s += rect(x - 4, top + 2, w + 8, 14, dim("#efe3c8", p, mode), 2.5)  # cornice
    # windows: 3 floors
    cols = 3 if w > 190 else 2
    for fl in range(3):
        wy = top + 40 + fl * (h - 140) / 3
        for c in range(cols):
            wx = x + (c + 0.5) * w / cols - 20
            if fl == 2 and c == cols // 2:  # ground floor door
                s += rect(wx - 2, base - 118, 44, 118, dim("#2f4a3a" if i % 3 else "#6e2a2a", p, mode), 3)
                s += P(f"M {wx-2},{base-118} Q {wx+20},{base-146} {wx+42},{base-118} Z", p["win"], 2.5)
                s += C(wx + 32, base - 60, 3, "#c99a3e", 1.2) + rect(wx - 10, base - 8, 60, 8, dim("#cfc6b4", p, mode), 2)
                continue
            lit = mode == "night" and (i * 7 + fl * 3 + c) % 3 != 0
            gl = p["win"] if (mode == "day" or lit) else "#1f2440"
            s += rect(wx - 4, wy - 6, 48, 8, dim("#efe3c8", p, mode), 2)  # lintel
            s += rect(wx, wy, 40, 66, gl, 3)
            if mode == "day":
                s += PF(f"M {wx+4},{wy+4} L {wx+16},{wy+4} L {wx+4},{wy+26} Z", p["winHi"], ' opacity="0.6"')
            else:
                if lit: s += f'<rect x="{wx-14}" y="{wy-14}" width="68" height="94" fill="#ffcf6e" opacity="0.18" rx="20"/>'
            s += L(f"M {wx+20},{wy} L {wx+20},{wy+66} M {wx},{wy+33} L {wx+40},{wy+33}", 2.5, dim("#f3ead8", p, mode))
            s += rect(wx - 4, wy + 66, 48, 7, dim("#efe3c8", p, mode), 2)  # sill
            if (i + c + fl) % 4 == 1:
                s += PF(f"M {wx+2},{wy+2} Q {wx+10},{wy+30} {wx+4},{wy+64} L {wx+2},{wy+64} Z", "#c25a5a" if mode == "day" else "#e88a5a", ' opacity="0.8"')
    # one shop front with a striped awning
    if i == 3:
        s += rect(x + 10, base - 120, w - 20, 120, dim("#2f5a4a", p, mode), 3)
        s += rect(x + 20, base - 104, w - 40, 80, p["win"], 2.5)
        for k in range(8):
            fill = dim("#c8352f" if k % 2 else "#f3ead8", p, mode)
            s += P(f"M {x+10 + k*(w-20)/8:.1f},{base-150} L {x+10 + (k+1)*(w-20)/8:.1f},{base-150} L {x+10 + (k+1)*(w-20)/8 + 4:.1f},{base-118} L {x+10 + k*(w-20)/8 + 4:.1f},{base-118} Z", fill, 2)
    return G(f"house_{i}", 0, 0, s)

def mid(mode):
    base, s, x, i = 1322, "", -260, 0
    while x < 1340:
        w = 180 + (i * 47) % 60
        h = 340 + (i * 71) % 110
        s += house(i, x, w, h, base, mode)
        x += w + 2; i += 1
    p = PAL[mode]
    s += rect(-300, base, 1700, 26, p["pave"], 3) + rect(-300, base + 26, 1700, 10, p["kerb"], 2.5)
    # small far-side lamps
    for lx in range(-200, 1340, 260):
        s += rect(lx - 3, base - 150, 6, 150, "#2f3a33", 2) + rect(lx - 12, base - 176, 24, 28, "#ffd98a" if mode == "night" else "#e9e3cf", 2.5)
        if mode == "night": s += f'<circle cx="{lx}" cy="{base-162}" r="40" fill="#ffcf6e" opacity="0.25"/>'
    return f'<g id="layer_mid" data-parallax="0.45">{s}</g>'

# ---------------------------------------------------------------- road + pavement
def ground(mode):
    p = PAL[mode]
    gen.DEFS["cobbles_" + mode] = (f'<pattern id="cobbles_{mode}" width="56" height="34" patternUnits="userSpaceOnUse">'
        f'<rect width="56" height="34" fill="{p["road"]}"/>'
        f'<ellipse cx="14" cy="9" rx="12" ry="7" fill="{p["cob"]}" stroke="{mul(p["road"], 0.75)}" stroke-width="2"/>'
        f'<ellipse cx="42" cy="9" rx="12" ry="7" fill="{mul(p["cob"], 0.95)}" stroke="{mul(p["road"], 0.75)}" stroke-width="2"/>'
        f'<ellipse cx="0" cy="26" rx="12" ry="7" fill="{mul(p["cob"], 1.03)}" stroke="{mul(p["road"], 0.75)}" stroke-width="2"/>'
        f'<ellipse cx="28" cy="26" rx="12" ry="7" fill="{p["cob"]}" stroke="{mul(p["road"], 0.75)}" stroke-width="2"/>'
        f'<ellipse cx="56" cy="26" rx="12" ry="7" fill="{mul(p["cob"], 1.03)}" stroke="{mul(p["road"], 0.75)}" stroke-width="2"/></pattern>')
    road = f'<rect id="road" x="-200" y="1358" width="1480" height="360" fill="url(#cobbles_{mode})"/>'
    road += f'<rect x="-200" y="1358" width="1480" height="360" fill="{grad("roadshade_" + mode, [(0, "#000000"), (1, "#000000")])}" opacity="0"/>'
    road += PF("M 560,1560 Q 700,1540 820,1566 Q 760,1596 600,1590 Z", "#9cc0e0" if mode == "day" else "#5a6aa0", ' opacity="0.55"')  # puddle
    road += L("M -200,1470 Q 540,1460 1280,1476 M -200,1610 Q 540,1600 1280,1618", 6, mul(p["road"], 0.85), ' opacity="0.6"')  # wheel ruts
    road += PF("M 300,1500 q 10,-8 20,0 q -6,8 -20,0 Z", "#6b5a3a", ' opacity="0.7"')
    kerb = rect(-200, 1708, 1480, 22, p["kerb"], 3)
    slabs = rect(-200, 1728, 1480, 260, p["pave"], 3)
    for x in range(-200, 1280, 150):
        slabs += L(f"M {x},1730 L {x-40},1920", 2.5, mul(p["pave"], 0.82))
    slabs += L("M -200,1820 L 1280,1820", 2.5, mul(p["pave"], 0.82))
    return f'<g id="layer_ground" data-parallax="0.8">{road}</g><g id="layer_near" data-parallax="1">{kerb}{slabs}</g>'

# ---------------------------------------------------------------- props
def gas_lamp(gid, x, y, k, mode):
    on = mode == "night"
    post = P("M -10,0 L -8,-330 L 8,-330 L 10,0 Z", "#2f3a33", 3) + rect(-22, -24, 44, 24, "#2f3a33", 3) + L("M -8,-200 L 8,-200 M -8,-120 L 8,-120", 3, "#c9a04a")
    bar = L("M -36,-330 L 36,-330", 5, "#2f3a33")
    head = P("M -24,-334 L 24,-334 L 30,-390 L -30,-390 Z", "#fff2c0" if on else "#e9eef0", 3) + P("M -36,-390 L 36,-390 L 0,-414 Z", "#2f3a33", 3) + C(0, -418, 6, "#2f3a33", 2)
    flame = G(f"{gid}_flame", 0, -360, (f'<circle r="90" fill="#ffcf6e" opacity="0.28"/><circle r="40" fill="#ffe8a8" opacity="0.6"/>' if on else "") +
              PF("M 0,-14 Q 9,0 0,12 Q -9,0 0,-14 Z", "#ffb347"), extra=f' opacity="{1 if on else 0}"')
    return G(gid, x, y, f'<g transform="scale({k})">{post}{bar}{head}{flame}</g>')

def signal(mode, x=230, y=1790, k=1.0):
    """J. P. Knight's 1868 signal: plinth, fluted cast-iron pillar (green + gold), two semaphore arms, gas lantern"""
    on = mode == "night"
    g = "#2f5a3f"; gold = "#d9a845"
    plinth = rect(-70, -70, 140, 70, "#b9b2a6", 3) + rect(-80, -82, 160, 16, "#cfc8ba", 3)
    pillar = P("M -30,-82 L -22,-760 L 22,-760 L 30,-82 Z", g)
    for fx in (-10, 0, 10):
        pillar += L(f"M {fx},-100 L {fx*0.75:.1f},-740", 2, mul(g, 0.7))
    for yb in (-140, -420, -700):
        pillar += rect(-34, yb - 10, 68, 20, gold, 2.5)
    pillar += P("M -40,-760 L 40,-760 L 30,-800 L -30,-800 Z", gold, 3)
    pillar += G("signal_door", 0, -300, rect(-14, -40, 28, 80, mul(g, 0.85), 2.5) + C(6, 0, 3, gold, 1.2))
    arms = ""
    for side, s in (("L", 1), ("R", -1)):
        arm = P(f"M 0,-10 L {s*230},-12 L {s*236},10 L 0,12 Z", "#c8352f") + L(f"M {s*190},-10 L {s*190},10", 6, "#f3ead8")
        arms += G(f"signal_arm_{side}", s * 24, -800, arm, 0, ' data-states="0=stop(horizontal),55=go(lowered)"')
    mast = rect(-16, -900, 32, 110, g, 3) + C(0, -905, 14, gold, 2.5)
    lantern = rect(-46, -1010, 92, 96, "#1f2a24", 3)
    red = G("signal_lamp_red", 0, -962, (f'<circle r="120" fill="#ff4a3a" opacity="0.3"/>' if on else "") + E(0, 0, 30, 34, "#e8322a", 3), extra=' opacity="1"')
    green = G("signal_lamp_green", 0, -962, (f'<circle r="120" fill="#3aff8a" opacity="0.3"/>' if on else "") + E(0, 0, 30, 34, "#2fb36a", 3), extra=' opacity="0"')
    roof = P("M -60,-1010 L 60,-1010 L 0,-1070 Z", "#1f2a24", 3) + C(0, -1076, 8, gold, 2.5)
    leak = G("signal_gas_leak", 26, -880, PF("M 0,0 Q 30,-40 10,-90 Q 50,-120 30,-170", "none") +
             L("M 0,0 Q 30,-40 10,-90 Q -10,-130 30,-170", 16, "#b5e0a0", ' opacity="0.5"'), extra=' opacity="0"')
    shadow = '<ellipse cx="20" cy="0" rx="120" ry="14" fill="#2a2018" opacity="0.22"/>'
    return G("knight_signal", x, y, f'<g transform="scale({k})">{shadow}{plinth}{pillar}{mast}{arms}{lantern}{red}{green}{roof}{leak}</g>')

def railing(mode):
    s = ""
    for xx in range(560, 1100, 26):
        s += L(f"M {xx},1760 L {xx},1680", 4, "#22262b") + PF(f"M {xx-5},1680 L {xx},1666 L {xx+5},1680 Z", "#c9a04a")
    s += L("M 556,1690 L 1100,1690 M 556,1750 L 1100,1750", 5, "#22262b")
    return f'<g id="railing">{s}</g>'

def cab(cid="hansom_cab"):
    """hansom cab (side view, facing right), local origin = ground under the axle"""
    body_c, trim = "#2a2a30", "#c9a04a"
    wheel = C(0, -140, 140, "none", 10) + C(0, -140, 128, "none", 3)
    for i in range(14):
        a = i * math.pi / 7
        wheel += L(f"M {14*math.cos(a):.1f},{-140 + 14*math.sin(a):.1f} L {126*math.cos(a):.1f},{-140 + 126*math.sin(a):.1f}", 5, "#6b4a2a")
    wheel += C(0, -140, 18, trim, 3)
    wheel = G(f"{cid}_wheel", 0, 0, f'<g transform="translate(0,0)">{wheel}</g>')
    body = P("M -170,-200 L -170,-430 Q -160,-470 -110,-470 L 80,-470 Q 120,-460 130,-410 L 150,-250 Q 150,-200 110,-200 Z", body_c)
    body += rect(-120, -430, 160, 110, "#4a6a8a", 3) + L("M -40,-430 L -40,-320", 3)
    body += P("M 40,-320 L 140,-320 L 150,-250 L 40,-250 Z", mul(body_c, 1.3), 3)  # folding doors
    body += L("M -170,-300 L 150,-300", 3, trim)
    seat = rect(-210, -560, 70, 22, "#3a2a20", 3) + L("M -180,-540 L -170,-470", 6, body_c)
    shafts = L("M 110,-230 Q 300,-260 470,-300", 10, "#6b4a2a")
    lamp = rect(130, -440, 24, 34, "#ffe08a", 2.5)
    return G(cid, 0, 0, shafts + body + seat + lamp + wheel)

def foreground(mode):
    return f'<g id="layer_foreground" data-parallax="1.2">{railing(mode)}</g>'

def scene(mode, cast=False):
    gen.DEFS.clear()
    parts = [sky(mode), far(mode), mid(mode), ground(mode)]
    props = gas_lamp("gas_lamp_1", 620, 1736, 1.0, mode) + gas_lamp("gas_lamp_2", 1020, 1736, 1.0, mode)
    parts.append(f'<g id="layer_props">{props}</g>')
    parts.append(foreground(mode))
    parts.append(signal(mode))
    if cast:
        people = ""
        # horse + hansom cab on the road (cab behind the horse), cabbie up on the seat
        hs = 0.42
        hg = gen.horse("ot")
        cg, _ = gen.person("aravakash", gen.CABBIE, dict(gen.POSES["aravakash"], upper_arm_L=16, forearm_L=78, hand_L=10, upper_arm_R=-16, forearm_R=-78, hand_R=-10))
        people += f'<g id="stage_cab" transform="translate(470,1630) scale({hs})">' + \
                  f'<g transform="translate(-110,-445) scale(0.62)">{cg}</g>' + cab() + \
                  f'<g transform="translate(700,0)">{hg}</g></g>'
        pg, gp = gen.person("politsiyachi", gen.POL, gen.POSES["politsiyachi"])
        people += f'<g id="stage_police" transform="translate(410,{1800 - gp*0.36:.1f}) scale(0.36)">{pg}</g>'
        lg, gl = gen.person("piyoda_xonim", gen.LADY, gen.POSES["piyoda_xonim"])
        people += f'<g id="stage_lady" transform="translate(860,{1850 - gl*0.33:.1f}) scale(0.33)">{lg}</g>'
        parts.append(f'<g id="layer_cast">{people}</g>')
    body = "".join(parts)
    vign = f'<rect width="{W}" height="{H}" fill="url(#vig_{mode})" pointer-events="none"/>'
    gen.DEFS[f"vig_{mode}"] = (f'<radialGradient id="vig_{mode}" cx="0.5" cy="0.45" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/>'
                               f'<stop offset="1" stop-color="#1a1020" stop-opacity="{0.35 if mode == "night" else 0.18}"/></radialGradient>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<title>Westminster 1868 ({mode})</title>{gen.defs()}{body}{vign}</svg>')

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for mode in ("day", "night"):
        name = {"day": "kunduzi", "night": "kechasi"}[mode]
        open(os.path.join(OUT, f"shahar_{name}.svg"), "w").write(scene(mode))
        open(os.path.join(OUT, f"sahna_{name}_qahramonlar.svg"), "w").write(scene(mode, cast=True))
    print("ok")
