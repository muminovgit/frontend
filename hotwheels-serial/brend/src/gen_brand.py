"""Brand kit for "Mashina tarixi": avatar, YouTube banner, Reels/Shorts covers, Instagram highlight covers.
Same look as the episodes: 2D vector, #221d1a outlines, cream #f3ead8, shadow left/bottom + light right.

usage: python3 gen_brand.py            -> writes SVGs into ../svg/
       ./render.sh                     -> renders them to ../png/ with headless Chrome
Episode covers: add a line to EPISODES below (frame = a 1080x1920 still from the episode, without subtitles).
"""
import os, sys, base64
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "mashina-tarixi", "01-svetofor", "characters"))
import gen_characters as gen
from gen_characters import P, PF, L, C, INK, mul, mix, shade

OUT = os.path.join(HERE, "..", "svg"); os.makedirs(OUT, exist_ok=True)
CREAM, RED, YEL = "#f3ead8", "#c8352f", "#ffd34a"
FONT = "'Arial Black', 'DejaVu Sans', Arial, sans-serif"
FONT_TXT = "'Arial', 'DejaVu Sans', sans-serif"

def rect(x, y, w, h, fill, sw=3, rx=0, extra=""):
    f = fill if (fill.startswith("url") or fill == "none") else shade(fill)
    s = f' stroke="{INK}" stroke-width="{sw}"' if sw else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{f}"{s}{extra}/>'

def text(x, y, s, size, fill="#ffffff", anchor="middle", stroke=0, font=FONT, weight=900, extra=""):
    st = f' stroke="{INK}" stroke-width="{stroke}" paint-order="stroke" stroke-linejoin="round"' if stroke else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{font}" font-weight="{weight}" font-size="{size}" '
            f'fill="{fill}"{st}{extra}>{s}</text>')

def car(cid="car"):
    """the red hatchback from the end card (side view, facing right, origin = ground under the middle)"""
    body = (f'<path d="M -330,-70 Q -340,-150 -300,-170 L -200,-180 Q -140,-300 -20,-300 L 120,-300 Q 200,-290 260,-200 L 330,-180 '
            f'Q 370,-170 370,-110 L 370,-70 Z" fill="{shade(RED)}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    win = "M -150,-190 Q -110,-280 -20,-282 L 110,-282 Q 170,-276 214,-196 Z"
    glass = P(win, "#d7ecf5", 5) + PF("M -120,-200 Q -95,-262 -40,-268 L -10,-268 L -70,-200 Z", "#ffffff", ' opacity="0.55"') + L("M 40,-282 L 40,-192", 6)
    trim = (L("M -330,-120 L 370,-120", 4, mul(RED, 0.7)) + L("M 60,-150 L 92,-150", 5)
            + rect(330, -160, 40, 26, "#fff3c4", 3, 6) + rect(-338, -150, 24, 30, "#ff4a3a", 3, 4))
    wheels = "".join(f'<g transform="translate({x},-62)">' + C(0, 0, 62, "#22262b", 5) + C(0, 0, 32, "#b9bec6", 4)
                     + L("M -28,0 L 28,0 M 0,-28 L 0,28", 4, "#6b7078") + "</g>" for x in (-210, 220))
    shadow = f'<ellipse cx="20" cy="4" rx="390" ry="22" fill="#3a2a20" opacity="0.18"/>'
    return f'<g id="{cid}">{shadow}{body}{glass}{trim}{wheels}</g>'

def speed_lines(x, y, s=1.0):
    return "".join(L(f"M {x - (90 + i * 30) * s:.0f},{y + i * 46 * s:.0f} L {x - (20 + i * 10) * s:.0f},{y + i * 46 * s:.0f}", 12 * s, INK)
                   for i in range(3))

def dots(w, h, step=120, r=6, col="#e3d4b6", ox=60, oy=60):
    return "".join(C(x, y, r, col) for x in range(ox, w, step) for y in range(oy, h, step))

def doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'{gen.defs()}{body}</svg>')

def save(name, w, h, body):
    open(os.path.join(OUT, name + ".svg"), "w").write(doc(w, h, body))
    print("svg", name, f"{w}x{h}")

# ------------------------------------------------------------------------------------------------- avatar
def avatar(name="avatar", size=1080, with_text=False):
    """profile picture: shown as a circle (Instagram ~110 px, YouTube 98 px, Telegram ~50 px), so the car must read tiny"""
    gen.DEFS.clear()
    c = size / 2
    bg = f'<rect width="{size}" height="{size}" fill="{CREAM}"/>' + f'<circle cx="{c}" cy="{c}" r="{c}" fill="{CREAM}"/>'
    sun = C(c + 170, c - 150, 190, YEL, 6) if not with_text else ""
    road = rect(0, c + 205, size, 360, "#4a4f57", 0) + "".join(rect(x, c + 290, 90, 18, CREAM, 0) for x in range(30, size, 190)) if not with_text else ""
    ring = f'<circle cx="{c}" cy="{c}" r="{c - 26}" fill="none" stroke="{INK}" stroke-width="14"/>'
    if with_text:
        body = (bg + f'<g transform="translate({c - 14},{c - 20}) scale(0.92)">{car("acar")}</g>' + speed_lines(c - 330, c - 220, 0.9)
                + text(c, c + 150, "MASHINA", 150, fill=RED, stroke=16) + text(c, c + 290, "TARIXI", 150, fill=INK) + ring)
    else:
        body = (bg + sun + road + f'<g transform="translate({c - 5},{c + 210}) scale(1.0)">{car("acar")}</g>'
                + speed_lines(c - 360, c - 20, 0.9) + ring)
    save(name, size, size, f'<clipPath id="circ"><circle cx="{c}" cy="{c}" r="{c}"/></clipPath><g clip-path="url(#circ)">{body}</g>'
         if not with_text else body)

# ------------------------------------------------------------------------------------------------- YouTube banner
def yt_banner():
    """2560x1440. Text-safe area (all devices) is the centre 1546x423: x 507-2053, y 508-931.
    Desktop shows the full-width strip y 508-931; TV shows everything."""
    gen.DEFS.clear()
    W, H = 2560, 1440
    bg = f'<rect width="{W}" height="{H}" fill="{CREAM}"/>' + dots(W, H)
    road = rect(0, 905, W, 140, "#4a4f57", 0) + rect(0, 895, W, 16, "#b9bec6", 0) + "".join(rect(x, 965, 120, 16, CREAM, 0) for x in range(20, W, 260))
    under = f'<rect x="0" y="1045" width="{W}" height="{H - 1045}" fill="#e6dac0"/>'
    # cast on both sides (outside the text area, visible on wide screens)
    pol, gp = gen.person("politsiyachi", gen.POL, gen.POSES["politsiyachi"])
    kn, gk = gen.person("jon_nayt", gen.KNIGHT, dict(gen.POSES["jon_nayt"]))
    s = 0.52
    cast = (f'<g transform="translate(330,{905 - gp * s:.0f}) scale({s})">{pol}</g>'
            f'<g transform="translate(2250,{905 - gk * s:.0f}) scale(-{s},{s})">{kn}</g>')
    title = (text(560, 700, "MASHINA", 165, fill=RED, anchor="start", stroke=18)
             + text(560, 860, "TARIXI", 165, fill=INK, anchor="start"))
    tag = (rect(1540, 540, 500, 76, INK, 0, 38) + text(1790, 591, "har hafta yangi qism", 36, fill=YEL, font=FONT_TXT, weight=800))
    vehicle = f'<g transform="translate(1770,905) scale(0.68)">{car("bcar")}</g>' + speed_lines(1500, 735, 0.75)
    save("youtube_banner", W, H, bg + under + road + cast + title + tag + vehicle)

# ------------------------------------------------------------------------------------------------- episode cover
EPISODES = [
    # n, title line 1, title line 2, small line, still (relative to this file)
    (1, "PORTLAGAN", "SVETOFOR", "London, 1868", "kadr_01.jpg"),
]

def cover(n, t1, t2, small, frame):
    """1080x1920 Reels/Shorts cover. Instagram's profile grid crops to the centre 1080x1440 (y 240-1680), so every word
    sits inside that box."""
    gen.DEFS.clear()
    W, H = 1080, 1920
    img = base64.b64encode(open(os.path.join(HERE, frame), "rb").read()).decode()
    still = f'<image href="data:image/jpeg;base64,{img}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>'
    gen.DEFS["topfade"] = ('<linearGradient id="topfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#221d1a" stop-opacity="0.92"/>'
                           '<stop offset="0.75" stop-color="#221d1a" stop-opacity="0.7"/><stop offset="1" stop-color="#221d1a" stop-opacity="0"/></linearGradient>')
    shade_top = f'<rect width="{W}" height="840" fill="url(#topfade)"/>'
    chip = rect(330, 290, 420, 74, INK, 0, 37) + text(540, 341, f"MASHINA TARIXI · #{n}", 34, fill=YEL, font=FONT_TXT)
    size = 150 if max(len(t1), len(t2)) <= 9 else 118
    title = text(540, 520, t1, size, fill=YEL, stroke=20) + text(540, 680, t2, size, fill="#ffffff", stroke=20)
    sm_ = text(540, 760, small, 46, fill="#ffffff", font=FONT_TXT, weight=700, stroke=8)
    badge = (f'<g transform="translate(900,1560) rotate(-8)">' + C(0, 0, 105, RED, 7) + text(0, 30, f"#{n}", 92, fill="#ffffff") + "</g>")
    save(f"muqova_{n:02d}", W, H, still + shade_top + chip + title + sm_ + badge)

# ------------------------------------------------------------------------------------------------- highlight covers
def icon(kind):
    if kind == "qismlar":   # play button on a film frame
        return (rect(-190, -140, 380, 280, INK, 0, 34) + "".join(rect(x, y, 34, 28, CREAM, 0, 6) for x in range(-170, 180, 62) for y in (-122, 94))
                + P("M -50,-70 L 80,0 L -50,70 Z", YEL, 8))
    if kind == "hotwheels":
        return f'<g transform="translate(0,95) scale(0.52)">{car("hcar")}</g>' + speed_lines(-205, -10, 0.6)
    if kind == "savollar":
        return (P("M -170,-140 Q -170,-190 -120,-190 L 120,-190 Q 170,-190 170,-140 L 170,60 Q 170,110 120,110 L -10,110 L -90,180 L -80,110 "
                  "L -120,110 Q -170,110 -170,60 Z", "#ffffff", 9) + text(0, 40, "?", 210, fill=RED))
    if kind == "buyurtma":  # parcel box
        return (P("M -170,-60 L 0,-140 L 170,-60 L 170,130 L 0,200 L -170,130 Z", "#d9a66b", 9) + L("M -170,-60 L 0,20 L 170,-60 M 0,20 L 0,200", 9)
                + P("M -85,-100 L 85,-20 L 85,40 L 55,25 L 55,-5 L -115,-85 Z", YEL, 7))
    if kind == "faktlar":   # open book
        return (P("M 0,-110 Q -90,-160 -200,-130 L -200,130 Q -90,100 0,150 Z", "#ffffff", 9) + P("M 0,-110 Q 90,-160 200,-130 L 200,130 Q 90,100 0,150 Z", "#ffffff", 9)
                + "".join(L(f"M {sx * 50},{y} Q {sx * 110},{y - 20} {sx * 165},{y - 10}", 7, "#8a7d70") for sx in (-1, 1) for y in (-70, -20, 30, 80)))
    raise ValueError(kind)

HIGHLIGHTS = [("qismlar", "QISMLAR"), ("hotwheels", "HOT WHEELS"), ("buyurtma", "BUYURTMA"), ("savollar", "SAVOLLAR"), ("faktlar", "MANBALAR")]

def highlight(kind, label):
    """1080x1920 story; Instagram shows only the centre circle (about 600 px wide) as the highlight cover"""
    gen.DEFS.clear()
    W, H = 1080, 1920
    body = (f'<rect width="{W}" height="{H}" fill="{CREAM}"/>' + dots(W, H)
            + C(540, 960, 330, RED, 14) + C(540, 960, 290, "none", 0, f' stroke="{CREAM}" stroke-width="10" stroke-dasharray="4 26" stroke-linecap="round"')
            + f'<g transform="translate(540,960)">{icon(kind)}</g>'
            + text(540, 1400, label, 72, fill=INK))
    save(f"highlight_{kind}", W, H, body)

if __name__ == "__main__":
    avatar("avatar")
    avatar("avatar_yozuvli", with_text=True)
    yt_banner()
    for ep in EPISODES: cover(*ep)
    for k, lb in HIGHLIGHTS: highlight(k, lb)
