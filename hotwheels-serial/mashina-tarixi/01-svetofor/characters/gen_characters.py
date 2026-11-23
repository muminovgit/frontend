"""Rigged 2D vector character sheet for "Portlagan svetofor" (1868 London gas traffic light).
Every character is a <g id="<char>"> with nested joint groups. Each joint group is translated to its pivot, so an
animator only appends rotate(angle) to the group's transform (pivot = the group's local origin, also stored in
data-pivot). L/R = the character's own left/right (L is on the viewer's right for front-facing people).
usage: python3 gen.py <out_dir>"""
import os, sys, math

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
INK = "#221d1a"
BG = "#f3ead8"
SW = 4  # outline width

# ---------------------------------------------------------------- colour helpers + gradient defs
def _rgb(h): h = h.lstrip("#"); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]
def _hex(c): return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)
def mul(h, k): return _hex([v * k for v in _rgb(h)])
def mix(a, b, t): A, B = _rgb(a), _rgb(b); return _hex([A[i] * (1 - t) + B[i] * t for i in range(3)])

DEFS = {}
def shade(h, kind="h"):
    """directional vector shading: soft shadow on the left / underside, subtle highlight on the right"""
    key = f"g{kind}_{h.lstrip('#')}"
    if key not in DEFS:
        sh, hi = mix(mul(h, 0.72), "#3a2f4a", 0.12), mix(h, "#fff6e6", 0.16)
        if kind == "h":   # left shadow -> base -> right highlight
            DEFS[key] = f'<linearGradient id="{key}" x1="0" y1="0" x2="1" y2="0.25"><stop offset="0" stop-color="{sh}"/><stop offset="0.38" stop-color="{h}"/><stop offset="0.82" stop-color="{h}"/><stop offset="1" stop-color="{hi}"/></linearGradient>'
        else:             # "v": top highlight -> base -> underside shadow
            DEFS[key] = f'<linearGradient id="{key}" x1="0.2" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{hi}"/><stop offset="0.35" stop-color="{h}"/><stop offset="0.75" stop-color="{h}"/><stop offset="1" stop-color="{sh}"/></linearGradient>'
    return f"url(#{key})"

def P(d, fill, sw=SW, extra=""):
    f = fill if (fill.startswith("url") or fill == "none") else shade(fill)
    return f'<path d="{d}" fill="{f}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{extra}/>'
def PF(d, fill, extra=""):  # flat, no outline
    return f'<path d="{d}" fill="{fill}"{extra}/>'
def L(d, sw=3, col=INK, extra=""):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'
def C(x, y, r, fill, sw=0, extra=""):
    s = f' stroke="{INK}" stroke-width="{sw}"' if sw else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{s}{extra}/>'
def E(x, y, rx, ry, fill, sw=0, rot=0, extra=""):
    s = f' stroke="{INK}" stroke-width="{sw}"' if sw else ""
    t = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx}" ry="{ry}" fill="{fill}"{s}{t}{extra}/>'

def G(gid, x, y, body, rot=0, extra=""):
    r = f" rotate({rot})" if rot else ""
    return f'<g id="{gid}" data-pivot="{x:.1f},{y:.1f}" transform="translate({x:.1f},{y:.1f}){r}"{extra}>{body}</g>'

def limb(Lh, w0, w1, bulge=1.08, k=0.42):
    """capsule-like limb along +y from (0,0) to (0,Lh), half widths w0 (top) and w1 (bottom)"""
    m = max(w0, w1) * bulge
    return (f"M {w0},0 Q {m:.1f},{Lh * k:.1f} {w1},{Lh} A {w1} {w1} 0 0 1 {-w1},{Lh} "
            f"Q {-m:.1f},{Lh * k:.1f} {-w0},0 A {w0} {w0} 0 0 1 {w0},0 Z")

# ---------------------------------------------------------------- body parts
def hand(cid, side, skin, glove=None):
    s = 1 if side == "L" else -1
    col = glove or skin
    thumb = P(f"M {-s*4},6 Q {-s*20},10 {-s*19},24 Q {-s*17},32 {-s*9},26 Z", col, 3)
    palm = P("M -12,0 Q -16,18 -12,34 Q -6,44 2,44 Q 12,42 14,30 Q 16,14 12,0 Z", col, 3.5)
    fingers = L(f"M -5,30 L -5,40 M 2,31 L 2,42 M 8,30 L 8,38", 1.6, mul(col, 0.6))
    return thumb + palm + fingers

def foot(side, col, shoe="boot"):
    s = 1 if side == "L" else -1
    if shoe == "sneaker":
        d = f"M {-s*15},-6 L {s*14},-6 Q {s*24},6 {s*40},10 Q {s*50},16 {s*46},26 L {-s*18},26 Q {-s*22},8 {-s*15},-6 Z"
        sole = L(f"M {-s*18},22 L {s*46},22", 4, "#d6d9de")
        return P(d, col, 3.5) + sole + L(f"M {s*2},2 L {s*16},6", 2, "#9aa3ad")
    if shoe == "heel":
        d = f"M {-s*9},-8 L {s*10},-8 Q {s*16},4 {s*28},12 Q {s*33},18 {s*28},22 L {-s*4},22 L {-s*6},30 L {-s*12},30 L {-s*12},20 Q {-s*13},4 {-s*9},-8 Z"
        return P(d, col, 3)
    d = f"M {-s*16},-14 L {s*15},-14 Q {s*22},6 {s*38},12 Q {s*48},18 {s*44},28 L {-s*19},28 Q {-s*23},6 {-s*16},-14 Z"
    shine = L(f"M {s*20},10 Q {s*30},12 {s*36},16", 2.5, mix(col, "#ffffff", 0.45))
    return P(d, col, 3.5) + shine + L(f"M {-s*19},24 L {s*44},24", 3, mul(col, 0.6))

def leg(cid, side, hipx, c, pose):
    """thigh -> shin -> foot. c: dict(pants, boot, shoe, thigh, shin, bootTop)"""
    th, sh = c.get("thigh", 185), c.get("shin", 190)
    tw0, tw1, sw1 = c.get("tw", 25), c.get("tw1", 18), c.get("sw1", 14)
    pants = c["pants"]
    shin_body = P(limb(sh, tw1, sw1), pants)
    if c.get("bootTop"):  # tall boot over the lower shin
        bt = c["bootTop"]
        shin_body += P(f"M {-sw1-3},{sh-bt} L {sw1+3},{sh-bt} L {sw1+2},{sh} L {-sw1-2},{sh} Z", c["boot"], 3.5)
    else:
        shin_body += L(f"M {-sw1-1},{sh-8} Q 0,{sh-2} {sw1+1},{sh-8}", 2.5, mul(pants, 0.6))  # trouser hem crease
    ft = G(f"{cid}_foot_{side}", 0, sh, foot(side, c["boot"], c.get("shoe", "boot")), pose.get(f"foot_{side}", 0))
    shin = G(f"{cid}_shin_{side}", 0, th, shin_body + ft, pose.get(f"shin_{side}", 0))
    crease = L(f"M {(-1 if side=='R' else 1)*6},20 Q {(-1 if side=='R' else 1)*2},{th*0.5} {(-1 if side=='R' else 1)*5},{th-20}", 2, mul(pants, 0.62))
    return G(f"{cid}_thigh_{side}", hipx, 0, P(limb(th, tw0, tw1), pants) + crease + shin, pose.get(f"thigh_{side}", 0))

def arm(cid, side, shx, shy, c, pose):
    ua, fa = c.get("upper", 150), c.get("fore", 135)
    sleeve = c["sleeve"]
    cuff = c.get("cuff")
    fore_body = P(limb(fa, 15, 12), sleeve)
    if cuff: fore_body += P(f"M -14,{fa-14} L 14,{fa-14} L 13,{fa+2} L -13,{fa+2} Z", cuff, 3)
    for b in c.get("cuffButtons", []): fore_body += C(b, fa - 6, 2.6, "#c99a3e", 1.2)
    hd = G(f"{cid}_hand_{side}", 0, fa + (2 if cuff else 0), hand(cid, side, c["skin"], c.get("glove")), pose.get(f"hand_{side}", 0))
    fore = G(f"{cid}_forearm_{side}", 0, ua, fore_body + hd, pose.get(f"forearm_{side}", 0))
    wrinkle = L(f"M -8,{ua-12} Q 0,{ua-6} 8,{ua-12}", 2, mul(sleeve, 0.6))
    return G(f"{cid}_upper_arm_{side}", shx, shy, P(limb(ua, 19, 16), sleeve) + wrinkle + fore, pose.get(f"upper_arm_{side}", 0))

# ---------------------------------------------------------------- heads / faces / hats
HEAD = "M 0,-64 C 36,-64 54,-40 54,-6 C 54,28 38,60 0,62 C -38,60 -54,28 -54,-6 C -54,-40 -36,-64 0,-64 Z"

def eye(cid, side, kind, x, y, skin="#e8be9c"):
    s = 1 if side == "L" else -1
    g = []
    if kind in ("open", "stern", "wide", "half", "smile"):
        rx, ry = (11, 8) if kind != "wide" else (13, 12)
        g.append(E(x, y, rx, ry, "#ffffff", 2.5))
        ir = 6 if kind != "wide" else 5
        iy = y + (1 if kind == "stern" else 0)
        g.append(C(x + s * 0.5, iy, ir, "#4a3426"))
        g.append(C(x + s * 0.5, iy, ir * 0.5, "#140f0d"))
        g.append(C(x + 2.2, iy - 2.4, 1.9 if kind != "wide" else 2.4, "#ffffff"))
        if kind == "half":  # heavy upper lid
            g.append(P(f"M {x-12},{y-1} Q {x},{y-10} {x+12},{y-1} L {x+12},{y-9} L {x-12},{y-9} Z", skin, 2.5))
            g.append(L(f"M {x-12},{y-1} Q {x},{y-4} {x+12},{y-1}", 3))
        if kind == "stern":
            g.append(L(f"M {x-12},{y-3} Q {x},{y-7} {x+12},{y-3}", 3))
        if kind == "smile":  # lower lid pushed up by the grin
            g.append(PF(f"M {x-12},{y+3} Q {x},{y-3} {x+12},{y+3} L {x+12},{y+10} L {x-12},{y+10} Z", skin))
            g.append(L(f"M {x-11},{y+3} Q {x},{y-2} {x+11},{y+3}", 2.5))
    elif kind == "spiral":
        g.append(E(x, y, 13, 12, "#f1ece4", 2.5))
        pts = []
        for i in range(40):
            a = i * 0.45 * s; r = 1 + i * 0.27
            pts.append(f"{x + r*math.cos(a):.1f},{y + r*math.sin(a):.1f}")
        g.append(L("M " + " L ".join(pts), 2))
    return G(f"{cid}_eye_{side}", 0, 0, "".join(g))

def face(cid, skin, expr, moustache=None, sideburns=None, cheeks=None, nose_col=None, soot=False):
    parts = []
    # ears behind the head outline
    for s in (-1, 1):
        parts.append(G(f"{cid}_ear_{'L' if s>0 else 'R'}", s * 53, -4, P(f"M 0,-12 Q {s*14},-14 {s*14},2 Q {s*13},16 0,14 Z", skin, 3)))
    parts.append(P(HEAD, skin, SW))
    if soot:
        parts.append(PF("M -40,-30 Q -10,-50 30,-36 Q 52,-10 40,30 Q 10,58 -30,44 Q -52,10 -40,-30 Z", "url(#soot)", ' opacity="0.85"'))
    if cheeks:
        for s in (-1, 1): parts.append(E(s * 30, 18, 11, 7, cheeks, 0, 0, ' opacity="0.55"'))
    if sideburns:
        for s in (-1, 1): parts.append(P(f"M {s*50},-30 Q {s*56},-6 {s*50},18 Q {s*44},22 {s*42},10 L {s*44},-28 Z", sideburns, 2.5))
    E_ = {"stern": ("stern", "stern"), "smile": ("smile", "smile"), "shock": ("wide", "wide"), "nervous": ("open", "open"),
          "bored": ("half", "half"), "dizzy": ("spiral", "spiral")}[expr]
    parts.append(eye(cid, "L", E_[0], 20, -6, skin)); parts.append(eye(cid, "R", E_[1], -20, -6, skin))
    # brows
    brow = {"stern": ("M 8,-22 Q 20,-26 32,-30", "M -8,-22 Q -20,-26 -32,-30", 5.5),
            "smile": ("M 8,-26 Q 20,-34 32,-28", "M -8,-26 Q -20,-34 -32,-28", 4.5),
            "shock": ("M 8,-32 Q 20,-42 32,-36", "M -8,-32 Q -20,-42 -32,-36", 4.5),
            "nervous": ("M 8,-28 Q 18,-34 30,-26", "M -8,-28 Q -18,-34 -30,-26", 4),
            "bored": ("M 8,-22 L 32,-22", "M -8,-22 L -32,-22", 4.5)}.get(expr)
    if brow:
        bc = "#2e211b" if not nose_col else "#3a2a20"
        if expr == "stern":  # furrow
            parts.append(L("M -4,-24 L -2,-16 M 4,-24 L 2,-16", 2, mul(skin, 0.7)))
        parts.append(G(f"{cid}_brow_L", 0, 0, L(brow[0], brow[2], bc)))
        parts.append(G(f"{cid}_brow_R", 0, 0, L(brow[1], brow[2], bc)))
    # nose
    nc = nose_col or mul(skin, 0.82)
    parts.append(G(f"{cid}_nose", 0, 14, P("M -2,-10 Q 8,2 6,8 Q 0,12 -6,8", nc, 2.5) if nose_col else L("M -1,-8 Q 7,4 4,8 Q 0,10 -5,8", 2.8)))
    # mouth
    m = {"stern": L("M -14,34 Q 0,30 14,34", 3.5),
         "smile": P("M -20,28 Q 0,32 20,28 Q 16,48 0,48 Q -16,48 -20,28 Z", "#6e2a2a", 3) + PF("M -15,31 Q 0,34 15,31 L 14,36 Q 0,38 -14,36 Z", "#ffffff"),
         "shock": E(0, 38, 9, 12, "#5a1e28", 3) + E(0, 44, 5, 4, "#e86e78"),
         "nervous": L("M -9,36 Q -6,32 -3,36 Q 0,40 3,36 Q 6,32 9,36", 2.8),
         "bored": L("M -10,36 L 10,35", 3.2),
         "dizzy": L("M -16,38 Q -10,32 -5,38 Q 0,44 5,38 Q 10,32 16,38", 3)}[expr]
    parts.append(G(f"{cid}_mouth", 0, 0, m))
    if moustache:
        parts.append(G(f"{cid}_moustache", 0, 0, P("M 0,22 Q 12,16 24,22 Q 30,28 22,30 Q 12,26 0,28 Q -12,26 -22,30 Q -30,28 -24,22 Q -12,16 0,22 Z", moustache, 2.5)))
    return "".join(parts)

def hat(kind, col, extra=None):
    e = extra or {}
    if kind == "helmet":  # Victorian custodian helmet + star badge + chin strap
        strap = L("M -50,-20 Q -46,30 -24,56 M 50,-20 Q 46,30 24,56", 3.5, "#1a1a1d")
        dome = P("M -58,-36 Q -62,-110 -30,-150 Q 0,-176 30,-150 Q 62,-110 58,-36 Z", col)
        ridge = L("M 0,-170 Q 4,-110 0,-46", 2.5, mul(col, 1.5))
        brim = P("M -66,-36 Q 0,-20 66,-36 Q 70,-28 60,-24 Q 0,-10 -60,-24 Q -70,-28 -66,-36 Z", mul(col, 0.8))
        star = []
        for i in range(16):
            r = 15 if i % 2 == 0 else 6.5; a = i * math.pi / 8
            star.append(f"{r*math.sin(a):.1f},{-88 - r*math.cos(a):.1f}")
        badge = f'<polygon points="{" ".join(star)}" fill="{shade(e.get("badge", "#d8dee9"))}" stroke="{INK}" stroke-width="2"/>' + C(0, -88, 5, "#9aa3b0", 1.5)
        knob = C(0, -172, 7, "#d8dee9", 2.5)
        return strap + dome + ridge + knob + brim + badge
    if kind == "tophat":
        crown = P("M -44,-52 L -48,-196 Q 0,-206 48,-196 L 44,-52 Z", col)
        band = P("M -44,-60 L -45,-84 Q 0,-90 45,-84 L 44,-60 Q 0,-54 -44,-60 Z", e.get("band", "#3d3533"), 3)
        top = E(0, -197, 48, 8, mul(col, 1.15), 3)
        brim = P("M -72,-50 Q -70,-62 -44,-60 Q 0,-52 44,-60 Q 70,-62 72,-50 Q 0,-34 -72,-50 Z", mul(col, 0.85))
        sheen = L("M 26,-188 L 24,-96", 4, mix(col, "#ffffff", 0.25))
        return crown + sheen + band + top + brim
    if kind == "flatcap":
        body = P("M -58,-26 Q -64,-72 -20,-82 Q 30,-90 56,-60 Q 64,-40 58,-26 Q 0,-34 -58,-26 Z", col)
        tweed = "".join(L(f"M {x},-78 L {x+10},-30", 1.5, mul(col, 0.7)) for x in range(-44, 50, 12))
        peak = P("M -54,-30 Q 0,-44 60,-30 Q 70,-18 54,-14 Q 0,-22 -50,-16 Q -64,-20 -54,-30 Z", mul(col, 0.85))
        return body + tweed + peak + C(-6, -84, 4, mul(col, 0.8), 2)
    if kind == "bonnet":
        hair = P("M -46,-40 Q -48,-70 -10,-74 Q 30,-76 46,-50 Q 50,-36 44,-28 Q 20,-46 -6,-44 Q -30,-42 -46,-28 Z", e["hair"], 3)
        locks = P("M -50,-28 Q -60,0 -52,26 Q -44,20 -44,0 Z", e["hair"], 2.5) + P("M 50,-28 Q 60,0 52,26 Q 44,20 44,0 Z", e["hair"], 2.5)
        back = P("M -70,10 Q -84,-80 -10,-98 Q 64,-104 80,-40 Q 86,-4 70,20 Q 60,-30 30,-62 Q 0,-76 -34,-62 Q -62,-40 -70,10 Z", col)
        brim_in = L("M -66,6 Q -62,-40 -32,-60 Q 0,-74 30,-60 Q 60,-36 68,14", 4, mul(col, 0.7))
        ribbon = P("M -60,14 Q -40,50 -6,64 L 6,64 Q 40,50 60,14 Q 44,46 8,58 L -8,58 Q -44,46 -60,14 Z", e.get("ribbon", "#c97a8a"), 2.5)
        bow = P("M 0,62 Q -26,54 -28,70 Q -24,82 0,68 Q 24,82 28,70 Q 26,54 0,62 Z", e.get("ribbon", "#c97a8a"), 2.5) + C(0, 66, 5, mul(e.get("ribbon", "#c97a8a"), 0.8), 2)
        tails = P("M -4,68 L -14,96 L -6,94 L 0,72 Z", e.get("ribbon", "#c97a8a"), 2) + P("M 4,68 L 16,98 L 8,96 L 0,72 Z", e.get("ribbon", "#c97a8a"), 2)
        return back + brim_in + locks + hair + ribbon + tails + bow
    if kind == "modernhair":
        return P("M -54,-14 Q -60,-58 -24,-70 Q 0,-84 30,-72 Q 62,-60 56,-14 Q 50,-36 34,-44 Q 40,-30 30,-26 Q 20,-46 -4,-48 Q -30,-46 -40,-34 Q -48,-24 -54,-14 Z", col) + \
               L("M -10,-66 Q 10,-74 34,-62 M -24,-58 Q 0,-68 20,-58", 2, mix(col, "#ffffff", 0.2))
    return ""

def neck_head(cid, skin, expr, hat_kind, hat_col, hat_extra=None, moustache=None, sideburns=None, cheeks=None, nose_col=None,
              soot=False, sweat=False, smoke=False, head_rot=0):
    hb = ""
    if hat_kind == "bonnet": hb += hat(hat_kind, hat_col, hat_extra)  # bonnet frames the face from behind
    hb += face(cid, skin, expr, moustache, sideburns, cheeks, nose_col, soot)
    if hat_kind != "bonnet": hb += G(f"{cid}_hat", 0, 0, hat(hat_kind, hat_col, hat_extra))
    if sweat: hb += G(f"{cid}_sweat", 40, -34, P("M 0,-12 Q 8,0 6,6 Q 0,12 -6,6 Q -8,0 0,-12 Z", "#a8d8ea", 2))
    if smoke:
        w = ""
        for i, (x, y, s) in enumerate([(-70, -130, 1.0), (60, -160, 0.8), (-20, -205, 1.1), (90, -100, 0.7)]):
            w += f'<g id="{cid}_smoke_{i}" transform="translate({x},{y}) scale({s})" opacity="0.8">' + \
                 PF("M -18,10 Q -26,-8 -10,-14 Q -6,-30 10,-24 Q 26,-26 24,-8 Q 34,4 20,12 Q 4,20 -18,10 Z", "#8c8580") + \
                 L("M -12,4 Q 0,-10 14,0", 2, "#6f6863") + "</g>"
        hb += f'<g id="{cid}_smoke">{w}</g>'
    head = G(f"{cid}_head", 0, -78, hb, head_rot)
    neck = P("M -17,10 L -16,-34 Q 0,-40 16,-34 L 17,10 Z", skin, 3.5)
    return neck + head

# ---------------------------------------------------------------- torsos (local origin = pelvis; shoulders at y=-227)
def torso_tunic(cid, c):
    """double-breasted police tunic: high collar, silver buttons, belt with brass buckle"""
    j = c["jacket"]
    body = P("M -22,-238 Q -62,-236 -84,-222 Q -92,-150 -76,-60 L -70,46 Q 0,56 70,46 L 76,-60 Q 92,-150 84,-222 Q 62,-236 22,-238 Z", j)
    shadow = PF("M -70,-40 Q 0,-30 70,-40 L 70,46 Q 0,56 -70,46 Z", mul(j, 0.82), ' opacity="0.55"')
    front = L("M 8,-228 Q 12,-120 8,46", 2.5, mul(j, 0.6)) + L("M -40,-200 Q -46,-130 -40,-60", 2, mul(j, 0.7)) + L("M 54,-200 Q 60,-130 54,-60", 2, mix(j, "#ffffff", 0.15))
    buttons = "".join(C(x, y, 5, shade(c["buttons"]), 2) for y in range(-200, -50, 34) for x in (-14, 30))
    collar = P("M -26,-252 L 26,-252 L 30,-226 Q 0,-218 -30,-226 Z", mul(j, 0.9), 3) + C(-18, -238, 3, c["buttons"], 1.2) + C(18, -238, 3, c["buttons"], 1.2)
    belt = P("M -76,-40 Q 0,-30 76,-40 L 76,-18 Q 0,-8 -76,-18 Z", c["belt"], 3)
    buckle = P("M -14,-42 L 14,-42 L 14,-12 L -14,-12 Z", c["buckle"], 2.5) + P("M -7,-35 L 7,-35 L 7,-19 L -7,-19 Z", mul(c["belt"], 1.2), 2)
    if c.get("soot"):
        body += PF("M -60,-200 Q -20,-230 40,-190 Q 70,-120 30,-80 Q -30,-60 -66,-120 Z", "url(#soot)", ' opacity="0.65"')
    return body + shadow + front + buttons + collar + belt + buckle

def torso_frock(cid, c):
    """Victorian frock coat to the knee, waistcoat, white collar, dark cravat"""
    j, v = c["jacket"], c["vest"]
    tails = P("M -80,-60 L -88,150 Q -50,160 -8,150 L -4,40 Z", mul(j, 0.92)) + P("M 80,-60 L 88,150 Q 50,160 8,150 L 4,40 Z", j)
    vest = P("M -34,-226 L 34,-226 L 38,-10 Q 0,0 -38,-10 Z", v, 3)
    vest_btn = "".join(C(0, y, 3.5, "#cfa042", 1.5) for y in range(-170, -20, 26))
    shirt = P("M -18,-240 L 18,-240 L 0,-196 Z", "#f5f5f2", 3)
    collar = P("M -22,-250 L -4,-232 L -18,-222 Z", "#f5f5f2", 2.5) + P("M 22,-250 L 4,-232 L 18,-222 Z", "#f5f5f2", 2.5)
    cravat = P("M -10,-230 L 10,-230 L 14,-212 L 0,-190 L -14,-212 Z", c["cravat"], 2.5)
    coat = P("M -22,-240 Q -62,-238 -84,-224 Q -94,-150 -80,-60 L -74,40 L -40,48 L -34,-120 L -26,-226 Z", j) + \
           P("M 22,-240 Q 62,-238 84,-224 Q 94,-150 80,-60 L 74,40 L 40,48 L 34,-120 L 26,-226 Z", j)
    lapels = P("M -26,-228 L -46,-190 L -32,-150 Z", mul(j, 0.8), 3) + P("M 26,-228 L 46,-190 L 32,-150 Z", mul(j, 1.1), 3)
    btn = "".join(C(x, y, 4, shade(c["buttons"]), 1.8) for x in (-44, 44) for y in (-110, -76, -42))
    chain = L("M -30,-80 Q -14,-66 4,-82", 2, "#cfa042")
    return tails + vest + vest_btn + shirt + cravat + collar + coat + lapels + btn + chain

def torso_coachman(cid, c):
    """stocky cabbie: layered olive coat over a vest, worn scarf"""
    j = c["jacket"]
    coat = P("M -26,-236 Q -70,-236 -94,-218 Q -104,-140 -96,-60 Q -98,10 -84,70 Q 0,84 84,70 Q 98,10 96,-60 Q 104,-140 94,-218 Q 70,-236 26,-236 Z", j)
    belly = PF("M -70,-120 Q 0,-150 70,-120 Q 80,-40 60,10 Q 0,24 -60,10 Q -80,-40 -70,-120 Z", mix(j, "#fff6e6", 0.08), ' opacity="0.6"')
    vest = P("M -30,-220 L 30,-220 L 40,-20 Q 0,-6 -40,-20 Z", c["vest"], 3)
    btn = "".join(C(x, y, 4.5, shade("#c99a3e"), 1.8) for x in (-52, 52) for y in (-170, -120, -70, -20))
    seam = L("M -52,-200 Q -60,-80 -50,66 M 52,-200 Q 60,-80 50,66", 2.5, mul(j, 0.65))
    pocket = P("M -84,0 L -50,0 L -50,24 L -84,24 Z", mul(j, 0.88), 2.5) + P("M 50,0 L 84,0 L 84,24 L 50,24 Z", mul(j, 0.95), 2.5)
    scarf = P("M -40,-250 Q 0,-232 40,-250 Q 48,-226 30,-214 Q 0,-206 -30,-214 Q -48,-226 -40,-250 Z", c["scarf"], 3) + \
            P("M 14,-218 L 34,-150 L 18,-146 L 4,-212 Z", c["scarf"], 3) + L("M 18,-160 L 32,-162 M 20,-170 L 30,-172", 2, mul(c["scarf"], 0.6))
    return coat + belly + vest + btn + seam + pocket + scarf

def torso_shirt(cid, c):
    """modern button-up overshirt, untucked"""
    j = c["jacket"]
    body = P("M -22,-238 Q -60,-236 -80,-222 Q -88,-150 -74,-60 L -70,24 Q 0,34 70,24 L 74,-60 Q 88,-150 80,-222 Q 60,-236 22,-238 Z", j)
    tee = P("M -16,-236 Q 0,-224 16,-236 L 12,-208 L -12,-208 Z", "#e9ecef", 2.5)
    collar = P("M -24,-244 L -2,-228 L -18,-206 L -30,-232 Z", mul(j, 0.88), 2.5) + P("M 24,-244 L 2,-228 L 18,-206 L 30,-232 Z", mul(j, 1.05), 2.5)
    placket = L("M 4,-222 L 4,22", 2.5, mul(j, 0.6)) + "".join(C(10, y, 3, "#e8eef6", 1.2) for y in range(-200, 20, 36))
    pockets = P("M -56,-190 L -24,-190 L -24,-158 Q -40,-152 -56,-158 Z", mul(j, 0.92), 2.5) + P("M 30,-190 L 62,-190 L 62,-158 Q 46,-152 30,-158 Z", j, 2.5)
    folds = L("M -40,-60 Q -30,-40 -36,0 M 46,-70 Q 40,-40 48,-6", 2, mul(j, 0.7))
    return body + tee + collar + placket + pockets + folds

def torso_lady(cid, c):
    """fitted bodice, shawl/cape; the skirt is its own group (see build_lady)"""
    d, s = c["dress"], c["shawl"]
    bodice = P("M -20,-238 Q -52,-236 -64,-222 Q -66,-150 -44,-70 L 44,-70 Q 66,-150 64,-222 Q 52,-236 20,-238 Z", d)
    lace = P("M -18,-242 Q 0,-232 18,-242 L 16,-226 Q 0,-218 -16,-226 Z", "#f6efe6", 2.5) + C(0, -222, 5, "#c99a3e", 2)
    shawl = P("M -24,-236 Q -70,-236 -82,-212 Q -96,-170 -84,-118 Q -40,-90 0,-70 Q 40,-90 84,-118 Q 96,-170 82,-212 Q 70,-236 24,-236 Q 0,-200 -24,-236 Z", s)
    fringe = "".join(L(f"M {x},{-118 + abs(x)*0 + (48 - abs(x)*0.57):.0f} l 0,10", 2, mul(s, 0.7)) for x in range(-80, 84, 10))
    folds = L("M -60,-200 Q -40,-150 -20,-96 M 60,-200 Q 40,-150 20,-96 M 0,-196 L 0,-80", 2, mul(s, 0.65))
    sash = P("M -46,-76 Q 0,-66 46,-76 L 44,-58 Q 0,-48 -44,-58 Z", mul(d, 0.8), 2.5)
    return bodice + lace + shawl + folds + fringe + sash

def skirt(cid, c):
    d = c["dress"]
    sk = P("M -46,-64 Q 0,-56 46,-64 Q 84,60 132,372 Q 110,392 60,388 Q 0,398 -60,388 Q -110,392 -132,372 Q -84,60 -46,-64 Z", d)
    shadow = PF("M -46,-64 Q -84,60 -132,372 Q -110,392 -60,388 Q -70,200 -30,-58 Z", mul(d, 0.8), ' opacity="0.6"')
    folds = L("M -20,-40 Q -36,160 -60,380 M 20,-40 Q 30,170 50,384 M 0,-30 Q 4,200 0,388 M -50,40 Q -80,200 -100,370 M 50,40 Q 80,220 104,374", 2.5, mul(d, 0.66))
    hem = L("M -132,372 Q -110,382 -60,378 Q 0,388 60,378 Q 110,382 132,372", 5, mul(d, 0.8))
    frill = "".join(E(x, 382 + 4 * math.cos(x / 9), 11, 6, mix(d, "#f6efe6", 0.55), 2) for x in range(-120, 130, 20))
    return G(f"{cid}_skirt", 0, 0, sk + shadow + folds + hem + frill)

# ---------------------------------------------------------------- character assembly
def person(cid, cfg, pose):
    torso_fn = {"tunic": torso_tunic, "frock": torso_frock, "coach": torso_coachman, "shirt": torso_shirt, "lady": torso_lady}[cfg["torso"]]
    skin = cfg["skin"]
    hx = cfg.get("hipx", 36)
    leg_c = dict(pants=cfg["pants"], boot=cfg["boot"], shoe=cfg.get("shoe", "boot"), bootTop=cfg.get("bootTop"), tw=cfg.get("tw", 25), tw1=cfg.get("tw1", 18), sw1=cfg.get("sw1", 14))
    legs = leg(cid, "R", -hx, leg_c, pose) + leg(cid, "L", hx, leg_c, pose)
    arm_c = dict(sleeve=cfg["sleeve"], skin=skin, cuff=cfg.get("cuff"), cuffButtons=cfg.get("cuffButtons", []), glove=cfg.get("glove"))
    shx = cfg.get("shx", 80)
    nh = neck_head(cid, skin, cfg["expr"], cfg["hat"], cfg["hatCol"], cfg.get("hatExtra"), cfg.get("moustache"), cfg.get("sideburns"),
                   cfg.get("cheeks"), cfg.get("noseCol"), cfg.get("soot", False), cfg.get("sweat", False), cfg.get("smoke", False), pose.get("head", 0))
    neck = G(f"{cid}_neck", 0, -236, nh, pose.get("neck", 0))
    arms_back = "".join(arm(cid, s, x, -222, arm_c, pose) for s, x in (("R", -shx), ("L", shx)) if pose.get(f"arm_{s}_behind"))
    arms_front = "".join(arm(cid, s, x, -222, arm_c, pose) for s, x in (("R", -shx), ("L", shx)) if not pose.get(f"arm_{s}_behind"))
    torso_body = torso_fn(cid, cfg)
    if cfg["torso"] == "lady":  # skirt hangs from the waist over the legs
        legs_and_skirt = legs + skirt(cid, cfg)
    else:
        legs_and_skirt = legs
    torso = G(f"{cid}_torso", 0, 0, arms_back + neck + torso_body + arms_front, pose.get("torso", 0))
    ground = cfg.get("thigh", 185) + cfg.get("shin", 190) + 28
    shadow = f'<ellipse id="{cid}_contact_shadow" cx="0" cy="{ground:.0f}" rx="{cfg.get("shadowW", 105)}" ry="16" fill="#3a2a20" opacity="0.18"/>'
    pelvis = G(f"{cid}_pelvis", 0, 0, legs_and_skirt + torso)
    return shadow + pelvis, ground

# ---------------------------------------------------------------- horse (side view, facing right)
def horse(cid):
    coat, dark, hi, mane, hoof, strap, brass = "#8c5332", "#633820", "#a86843", "#2e2018", "#1f1c1a", "#2b221e", "#c99a3e"
    DEFS["horseBody"] = f'<linearGradient id="horseBody" x1="0.3" y1="0" x2="0.1" y2="1"><stop offset="0" stop-color="{hi}"/><stop offset="0.4" stop-color="{coat}"/><stop offset="0.8" stop-color="{coat}"/><stop offset="1" stop-color="{dark}"/></linearGradient>'
    DEFS["horseFar"] = f'<linearGradient id="horseFar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{mul(dark, 0.95)}"/><stop offset="1" stop-color="{mul(dark, 0.75)}"/></linearGradient>'
    body_fill, far_fill = "url(#horseBody)", "url(#horseFar)"

    def foreleg(side, x, y, fill, rot=(0, 0, 0)):
        side = "fore_" + side
        hoof_g = G(f"{cid}_hoof_{side}", 0, 0, P("M -14,0 L 16,0 L 22,24 L -16,24 Z", hoof, 3.5) + L("M -14,4 L 16,4", 2, "#4a4440"))
        past = G(f"{cid}_fetlock_{side}", 0, 66, P("M -12,-6 Q 14,-8 16,4 L 18,14 Q 0,18 -12,12 Z", fill, 3) + G(f"{cid}_pastern_{side}", 2, 12, hoof_g), rot[2])
        cannon = G(f"{cid}_cannon_{side}", 0, 86, P(limb(66, 12, 11, 1.02), fill) + E(0, 4, 11, 9, fill, 2.5) + past, rot[1])
        forearm = P("M -26,-14 Q 30,-20 26,10 Q 18,50 14,86 L -12,86 Q -20,40 -26,-14 Z", fill)
        return G(f"{cid}_foreleg_{side[5:]}", x, y, forearm + cannon, rot[0])

    def hindleg(side, x, y, fill, rot=(14, -24, 8)):
        side = "hind_" + side
        hoof_g = G(f"{cid}_hoof_{side}", 0, 0, P("M -14,0 L 16,0 L 22,24 L -16,24 Z", hoof, 3.5) + L("M -14,4 L 16,4", 2, "#4a4440"))
        past = G(f"{cid}_fetlock_{side}", 0, 70, P("M -12,-6 Q 14,-8 16,4 L 18,14 Q 0,18 -12,12 Z", fill, 3) + G(f"{cid}_pastern_{side}", 2, 12, hoof_g), 0)
        cannon = G(f"{cid}_cannon_{side}", 0, 92, P(limb(70, 13, 11, 1.02), fill) + E(-3, 4, 12, 9, fill, 2.5) + past, rot[1])
        gaskin = P("M -30,-20 Q 28,-28 24,20 Q 18,60 14,92 L -14,92 Q -26,40 -30,-20 Z", fill)
        return G(f"{cid}_hindleg_{side[5:]}", x, y, gaskin + cannon, rot[0])

    # far legs (behind the body, darker)
    far = foreleg("R", 118, -205, far_fill, (6, -4, 0)) + hindleg("R", -150, -200, far_fill, (10, -20, 6))
    tail = G(f"{cid}_tail", -228, -262, P("M 0,0 Q -40,-6 -54,40 Q -66,100 -48,170 Q -40,190 -24,176 Q -36,120 -20,70 Q -10,30 12,14 Z", mane, 3.5) +
             L("M -30,30 Q -48,90 -38,160 M -18,40 Q -30,100 -26,150", 2, "#5a4636"), 0)
    body = P("M 168,-292 C 120,-276 60,-270 0,-272 C -60,-274 -122,-296 -168,-294 C -212,-292 -236,-262 -234,-222 C -232,-186 -212,-160 -180,-150 "
             "C -120,-136 60,-134 132,-148 C 180,-158 210,-192 210,-232 C 210,-266 194,-288 168,-292 Z", body_fill)
    muscles = L("M -150,-280 Q -120,-200 -170,-160 M 150,-262 Q 120,-210 150,-160 M -40,-150 Q 20,-168 90,-152", 2.5, dark) + \
              L("M -200,-270 Q -170,-292 -120,-290", 3, hi)
    near = hindleg("L", -168, -196, body_fill, (16, -26, 10)) + foreleg("L", 146, -200, body_fill, (-4, 6, 0))
    # harness: collar + hames at the neck base, saddle pad + girth, breeching, traces
    harness = P("M -40,-300 Q 0,-312 40,-300 L 46,-262 Q 0,-252 -46,-262 Z", strap, 3) + C(-30, -282, 6, brass, 2) + C(30, -282, 6, brass, 2) + \
              P("M -18,-262 L 18,-262 L 22,-142 L -22,-142 Z", strap, 3) + C(0, -228, 7, brass, 2) + \
              P("M -170,-246 Q -60,-232 60,-238 L 60,-224 Q -60,-218 -168,-232 Z", strap, 2.5) + C(60, -231, 6, brass, 2) + \
              P("M 150,-206 Q 60,-190 -20,-198 L -20,-186 Q 60,-178 152,-192 Z", strap, 2.5)
    neck = G(f"{cid}_neck", 160, -270,
             P("M -40,0 C -24,-70 10,-132 60,-168 C 76,-176 96,-168 104,-152 C 84,-100 62,-40 56,24 Q 10,30 -40,0 Z", body_fill) +
             L("M 10,-20 Q 30,-80 70,-130", 2.5, dark) +
             P("M -36,-6 C -20,-74 14,-136 62,-170 Q 52,-150 40,-150 Q 30,-120 14,-110 Q 10,-84 -4,-76 Q -6,-50 -22,-40 Q -24,-20 -36,-6 Z", mane, 3) +
             P("M 20,-38 Q 60,-20 80,10 L 56,24 Q 34,0 6,-18 Z", strap, 3) + C(56, -2, 8, brass, 2.5) + C(56, -2, 4, mul(brass, 0.7)) +
             G(f"{cid}_head", 76, -160,
               P("M -6,-10 C 26,-22 54,0 80,46 C 94,70 104,92 94,108 C 84,122 60,122 46,110 C 28,90 8,60 -14,30 C -28,12 -24,-4 -6,-10 Z", body_fill) +
               P("M 52,112 Q 76,126 94,108 Q 90,124 70,128 Q 56,126 52,112 Z", mul(coat, 0.8), 2.5) +
               G(f"{cid}_ear", -2, -10, P("M -6,0 Q -10,-34 4,-46 Q 16,-30 12,0 Z", body_fill, 3.5) + L("M 2,-6 Q 2,-28 4,-38", 2, dark)) +
               P("M -12,-12 Q 10,-30 26,-8 Q 10,-2 -4,6 Z", mane, 3) +
               G(f"{cid}_eye", 28, 18, E(0, 0, 9, 8, "#1c1512", 2.5) + C(2.5, -2.5, 2.6, "#ffffff") + L("M -10,-8 Q 0,-14 10,-8", 2.5)) +
               G(f"{cid}_nostril", 86, 92, E(0, 0, 6, 4, "#2a1a12", 2, 30)) +
               G(f"{cid}_mouth", 0, 0, L("M 58,112 Q 70,116 82,112", 2.5)) +
               # bridle: crown piece, browband, noseband, cheek strap, brass rings, rein
               L("M 4,-8 Q 2,30 32,74", 6, strap) + L("M 10,-12 L 30,-4", 5, strap) + L("M 44,70 Q 70,58 92,78", 6, strap) +
               L("M 30,74 Q 44,90 58,104", 5, strap) + C(32, 74, 6, brass, 2) + C(60, 104, 6, brass, 2) + L("M 60,104 Q 20,150 -60,120", 3.5, strap)))
    cid_g = far + tail + body + muscles + harness + neck + near
    shadow = f'<ellipse id="{cid}_contact_shadow" cx="0" cy="22" rx="250" ry="18" fill="#3a2a20" opacity="0.18"/>'
    return shadow + cid_g

# ---------------------------------------------------------------- the cast
SOOT_SKIN = "#4a423f"
POL = dict(torso="tunic", skin="#e8be9c", expr="stern", hat="helmet", hatCol="#162033", hatExtra={"badge": "#d8dee9"}, moustache="#3b2a1f",
           jacket="#1b2840", buttons="#dce2ec", belt="#1a1a1d", buckle="#c99a3e", sleeve="#1b2840", cuff="#141e31", cuffButtons=[-6, 6],
           pants="#151f33", boot="#18181b", bootTop=70, glove=None)
SOOTY = dict(POL, skin=SOOT_SKIN, expr="dizzy", moustache="#1d1715", hatCol=mix("#162033", "#2b2523", 0.5), jacket=mix("#1b2840", "#2b2523", 0.45),
             sleeve=mix("#1b2840", "#2b2523", 0.45), pants=mix("#151f33", "#2b2523", 0.4), buttons="#8f8d88", soot=True, smoke=True,
             noseCol="#3a3230", hatExtra={"badge": "#a9a8a6"})
KNIGHT = dict(torso="frock", skin="#f0c9a8", expr="smile", hat="tophat", hatCol="#241f1e", hatExtra={"band": "#3d3533"}, sideburns="#6b4a32",
              jacket="#3b2d26", vest="#5a4436", cravat="#1f1b1a", buttons="#cfa042", sleeve="#3b2d26", cuff="#f5f5f2", pants="#2b221e", boot="#1d1918",
              shoe="boot", sw1=13)
CABBIE = dict(torso="coach", skin="#d9a582", expr="shock", hat="flatcap", hatCol="#5c4433", cheeks="#c96e5b", noseCol="#c96e5b", moustache="#6b3f2a",
              jacket="#4f6137", vest="#6b5a3e", scarf="#7a5c43", sleeve="#4f6137", cuff=mul("#4f6137", 0.85), pants="#2e2c2a", boot="#473222",
              bootTop=56, shx=90, hipx=40, tw=28, tw1=20, sw1=15, shadowW=118)
LADY = dict(torso="lady", skin="#f5d5be", expr="nervous", hat="bonnet", hatCol="#e8d49c", hatExtra={"hair": "#dec078", "ribbon": "#b85c74"},
            cheeks="#e68a8a", sweat=True, dress="#a84e6b", shawl="#6e2c42", sleeve="#6e2c42", cuff="#f6efe6", pants="#a84e6b", boot="#2a2026",
            shoe="heel", shx=66, hipx=22, tw=18, tw1=13, sw1=10, shadowW=135)
DRIVER = dict(torso="shirt", skin="#c9936b", expr="bored", hat="modernhair", hatCol="#241e1c", jacket="#2f629e", sleeve="#2f629e",
              cuff=mul("#2f629e", 0.9), pants="#232b38", boot="#f4f5f7", shoe="sneaker", sw1=14)

POSES = {
    "politsiyachi": dict(upper_arm_L=-16, forearm_L=68, hand_L=24, upper_arm_R=8, forearm_R=4, thigh_L=-3, thigh_R=3, foot_L=0),  # hand on belt
    "portlashdan_keyin": dict(upper_arm_L=-28, forearm_L=-20, hand_L=-10, upper_arm_R=30, forearm_R=24, thigh_L=-6, shin_L=4, thigh_R=4, head=-8, torso=3),
    "jon_nayt": dict(upper_arm_L=-30, forearm_L=-105, hand_L=-30, upper_arm_R=8, forearm_R=6, thigh_L=-2, thigh_R=2, head=4),  # presenting gesture
    "aravakash": dict(upper_arm_L=-150, forearm_L=16, hand_L=-6, upper_arm_R=150, forearm_R=-16, hand_R=6, thigh_L=-5, thigh_R=5, head=-3),  # hands up
    "piyoda_xonim": dict(upper_arm_L=14, forearm_L=104, hand_L=14, upper_arm_R=-14, forearm_R=-104, hand_R=-14, head=-4),  # hands clasped
    "bugungi_haydovchi": dict(upper_arm_L=-4, forearm_L=-14, upper_arm_R=6, forearm_R=10, thigh_L=-3, thigh_R=5, foot_R=-6, head=6, neck=-2),
}

CAST = [
    ("politsiyachi", "Politsiyachi", "svetoforni boshqaradi", POL),
    ("portlashdan_keyin", "Portlashdan keyin", "qoshsiz, qorayib ketgan", SOOTY),
    ("jon_nayt", "Jon Nayt", "temir yo'l muhandisi", KNIGHT),
    ("aravakash", "Aravakash", "London keblari", CABBIE),
    ("piyoda_xonim", "Piyoda xonim", "ko'chadan o'tolmaydi", LADY),
    ("bugungi_haydovchi", "Bugungi haydovchi", "qizil chiroqda kutadi", DRIVER),
]

FONT = "font-family=\"'Trebuchet MS', 'DejaVu Sans', Arial, sans-serif\""
def label(x, y, title, sub):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" {FONT} font-size="44" font-weight="700" fill="{INK}">{title}</text>'
            f'<text x="{x}" y="{y + 40}" text-anchor="middle" {FONT} font-size="28" fill="#6b5a4e">{sub}</text>')

def defs():
    soot = '<radialGradient id="soot" cx="0.5" cy="0.45" r="0.6"><stop offset="0" stop-color="#2b2523" stop-opacity="0.95"/><stop offset="0.7" stop-color="#4a423f" stop-opacity="0.7"/><stop offset="1" stop-color="#4a423f" stop-opacity="0"/></radialGradient>'
    return "<defs>" + soot + "".join(DEFS.values()) + "</defs>"

def build():
    W, H = 1920, 3420
    cols = [330, 960, 1590]
    rows = [120 + 880, 120 + 880 * 2 + 40]  # pelvis y gets computed from ground line
    chars, singles = [], {}
    for i, (cid, title, sub, cfg) in enumerate(CAST):
        r, ccol = divmod(i, 3)
        x = cols[ccol]
        g, ground = person(cid, cfg, POSES[cid])
        scale = 0.92 if cid == "piyoda_xonim" else (0.96 if cid == "aravakash" else 1.0)
        gy = 1040 + r * 1100  # ground line of the row
        py = gy - ground * scale
        grp = f'<g id="{cid}" data-label="{title}" transform="translate({x},{py:.1f}) scale({scale})">{g}</g>'
        chars.append(grp + label(x, gy + 70, title, sub))
        singles[cid] = (g, ground, scale, title, sub)
    hg = horse("ot")
    hy = 3180
    chars.append(f'<g id="ot" data-label="Ot" transform="translate(960,{hy})">{hg}</g>' + label(960, hy + 100, "Ot", "aravani tortadi"))
    sheet = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
             f'<title>Portlagan svetofor: rigged character sheet</title>{defs()}'
             f'<rect id="background" width="{W}" height="{H}" fill="{BG}"/>' + "".join(chars) + "</svg>")
    open(os.path.join(OUT, "character_sheet.svg"), "w").write(sheet)
    # one file per character (same rig, own canvas) for animation import
    for cid, (g, ground, scale, title, sub) in singles.items():
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-300 -1060 600 {1060 + ground + 140:.0f}" width="600" height="{1060 + ground + 140:.0f}">{defs()}'
               f'<rect x="-300" y="-1060" width="600" height="{1060 + ground + 140:.0f}" fill="{BG}"/><g id="{cid}">{g}</g>'
               + label(0, ground + 80, title, sub) + "</svg>")
        open(os.path.join(OUT, f"{cid}.svg"), "w").write(svg)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-420 -620 900 760" width="900" height="760">{defs()}'
           f'<rect x="-420" y="-620" width="900" height="760" fill="{BG}"/><g id="ot">{hg}</g>' + label(30, 100, "Ot", "aravani tortadi") + "</svg>")
    open(os.path.join(OUT, "ot.svg"), "w").write(svg)

build()
print("ok", OUT)
