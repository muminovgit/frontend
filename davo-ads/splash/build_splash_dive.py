# Davo Delivery — bold full-screen splash ("dive"). Lottie JSON, 1080x2340 portrait (use centerCrop / aspectFill).
#  0.0  logo + "Davo Delivery" in one row
#  0.2  letters slide back into the logo, logo glides to the centre and crouches
#  0.6  camera dives into the teal petal: yellow / pink / violet / teal + the white cross sweep across the screen
#  1.1  screen is teal; white "+" crosses and yellow dots burst out from the centre in a wave
#  2.1  everything washes to white -> app opens (crossfade into the first screen)
# usage: python3 build_splash_dive.py -> davo-splash-dive.json
import json, os, math
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.basePen import BasePen

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, '..', 'assets', 'fonts', 'Montserrat-900.woff2')
FPS, W, H, OP = 60, 1080, 2340, 156
COL = {'y': '#ffce68', 'pk': '#fb4669', 'vi': '#5e3a9a', 'g': '#01bdac', 'ink': '#1d1430', 'wh': '#ffffff'}
BACK = dict(o={'x': [.34], 'y': [1.56]}, i={'x': [.64], 'y': [1]})
OUT = dict(o={'x': [.22], 'y': [1]}, i={'x': [.36], 'y': [1]})
IN = dict(o={'x': [.7], 'y': [0]}, i={'x': [.84], 'y': [0]})          # ease-in (accelerating dive)
IO = dict(o={'x': [.6], 'y': [0]}, i={'x': [.4], 'y': [1]})

def rgb(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1]
def st(v): return {'a': 0, 'k': v}
def anim(keys, ease=OUT):
    k = []
    for n, key in enumerate(keys):
        t, v = key[0], key[1]; e_ = key[2] if len(key) > 2 else ease
        v = v if isinstance(v, list) else [v]; e = {'t': t, 's': v}
        if n < len(keys) - 1:
            d = len(v); e['o'] = {a: b * d for a, b in e_['o'].items()}; e['i'] = {a: b * d for a, b in e_['i'].items()}
        k.append(e)
    return {'a': 1, 'k': k}
def tr(p=None, s=None, r=None, o=None, a=None):
    return {'ty': 'tr', 'p': p or st([0, 0]), 'a': a or st([0, 0]), 's': s or st([100, 100]), 'r': r or st(0), 'o': o or st(100), 'sk': st(0), 'sa': st(0)}
def fill(c): return {'ty': 'fl', 'c': st(rgb(c)), 'o': st(100), 'r': 1}
def group(items, nm='g', t=None): return {'ty': 'gr', 'nm': nm, 'it': items + [t or tr()]}
def path(v, i=None, o=None):
    z = [[0, 0]] * len(v); return {'ty': 'sh', 'ks': st({'c': True, 'v': v, 'i': i or z, 'o': o or z})}
def rect(w, h): return {'ty': 'rc', 'p': st([0, 0]), 's': st([w, h]), 'r': st(0)}
def layer(ind, nm, shapes, p, s=None, r=None, o=None, a=None, parent=None, ty=4, ip=0, op=OP):
    L = {'ddd': 0, 'ind': ind, 'ty': ty, 'nm': nm, 'sr': 1, 'ao': 0, 'bm': 0, 'ip': ip, 'op': op, 'st': 0,
         'ks': {'o': o or st(100), 'r': r or st(0), 'p': p, 'a': a or st([0, 0, 0]), 's': s or st([100, 100, 100])}}
    if ty == 4: L['shapes'] = shapes
    if parent: L['parent'] = parent
    return L
def cross_pts(K):
    a, b = 10.5 * K, 29 * K
    return [[-a, -b], [a, -b], [a, -a], [b, -a], [b, a], [a, a], [a, b], [-a, b], [-a, a], [-b, a], [-b, -a], [-a, -a]]

# ---------------- wordmark glyphs (Montserrat Black outlines)
font = instancer.instantiateVariableFont(TTFont(FONT), {'wght': 900})
gs, cmap, hmtx, upm = font.getGlyphSet(), font.getBestCmap(), font['hmtx'], font['head'].unitsPerEm
class Pen(BasePen):
    def __init__(s, gs, sc): super().__init__(gs); s.sc, s.cs, s.cur = sc, [], None
    def P(s, p): return [p[0] * s.sc, -p[1] * s.sc]
    def _moveTo(s, p): s.cur = {'v': [s.P(p)], 'i': [[0, 0]], 'o': [[0, 0]]}; s.cs.append(s.cur)
    def _lineTo(s, p): s.cur['v'].append(s.P(p)); s.cur['i'].append([0, 0]); s.cur['o'].append([0, 0])
    def _curveToOne(s, c1, c2, p):
        p0 = s.cur['v'][-1]; c1, c2, p = s.P(c1), s.P(c2), s.P(p)
        s.cur['o'][-1] = [c1[0] - p0[0], c1[1] - p0[1]]; s.cur['v'].append(p); s.cur['i'].append([c2[0] - p[0], c2[1] - p[1]]); s.cur['o'].append([0, 0])
    def _closePath(s):
        c = s.cur
        if len(c['v']) > 1 and all(abs(x - y) < 1e-6 for x, y in zip(c['v'][0], c['v'][-1])):
            c['i'][0] = c['i'][-1]; c['v'].pop(); c['i'].pop(); c['o'].pop()
    _endPath = _closePath

LOGO = 170; K = LOGO / 131
TEXT, SIZE = 'Davo Delivery', 92
sc = SIZE / upm; gn = [cmap[ord(c)] for c in TEXT]; adv = [hmtx[g][0] * sc for g in gn]
GAP = 34; rowW = LOGO + GAP + sum(adv)
LX0 = (W - rowW) / 2 + LOGO / 2; CY = H / 2                       # logo centre in the opening row
TX0 = LX0 + LOGO / 2 + GAP; BASE = CY + SIZE * .36                 # text baseline (cap-centred on the logo)

layers = []; ind = 1
def add(L): global ind; L['ind'] = ind; ind += 1; layers.append(L); return L['ind']

# top-most: white wash at the end
add(layer(0, 'wash', [group([rect(W * 2, H * 2), fill(COL['wh'])])], st([W / 2, H / 2, 0]), o=anim([(122, 0), (146, 100)], IO)))

# ---------------- burst pattern: white crosses + yellow dots, wave from the centre
items = []; sp = 132
for r_ in range(-1, int(H / sp) + 2):
    for c_ in range(-1, int(W / sp) + 2):
        x = c_ * sp + (sp / 2 if r_ % 2 else 0) + 30; y = r_ * sp + 40
        d = math.hypot(x - W / 2, y - H / 2); t0 = 70 + d / 1300 * 34
        k = 1.35 * (0.8 + 0.25 * ((r_ * 7 + c_ * 3) % 3) / 2)
        items.append(group([path(cross_pts(.9 * k)), fill(COL['wh'])], 'x',
                           tr(p=st([x, y]), s=anim([(t0, [0, 0]), (t0 + 16, [100, 100])], BACK), r=anim([(t0, -60), (t0 + 16, 0)], BACK))))
        dx, dy = x + sp / 2, y + sp / 2
        t1 = 74 + math.hypot(dx - W / 2, dy - H / 2) / 1300 * 34
        items.append(group([{'ty': 'el', 'p': st([0, 0]), 's': st([16, 16])}, fill(COL['y'])], 'dot',
                           tr(p=st([dx - sp * .5 + sp * .5, dy - sp * .5 + sp * .5]), s=anim([(t1, [0, 0]), (t1 + 12, [100, 100])], BACK))))
add(layer(0, 'pattern', items, anim([(66, [W / 2, H / 2, 0]), (150, [W / 2, H / 2 - 40, 0])], IO),
          s=anim([(66, [100, 100, 100]), (150, [108, 108, 100])], IO), a=st([W / 2, H / 2, 0]), ip=60))
# teal floor once the dive has filled the screen (guarantees full coverage on any aspect ratio)
add(layer(0, 'teal', [group([rect(W * 2, H * 2), fill(COL['g'])])], st([W / 2, H / 2, 0]), ip=66))

# ---------------- logo rig: a null we scale for the dive; anchor sits deep inside the teal petal
AX = AY = 27.87 * K                                            # largest teal-only point (cross arm & circle edge equidistant)
rig = add(layer(0, 'logo-rig', [], anim([(0, [LX0 + AX, CY + AY, 0]), (27, [LX0 + AX, CY + AY, 0]), (40, [W / 2 + AX, CY + AY, 0], IO),
                                       (45, [W / 2 + AX, CY + AY, 0], IN), (68, [W / 2, H / 2, 0])], IO),
                s=anim([(0, [100, 100, 100]), (27, [100, 100, 100], IO), (40, [165, 165, 100], IO), (45, [145, 145, 100], IN), (68, [7000, 7000, 100])], IO),
                r=anim([(45, 0, IN), (68, 28)], IN), a=st([AX, AY, 0]), ty=3))
add(layer(0, 'cross', [group([path(cross_pts(K)), fill(COL['wh'])])], st([0, 0, 0]), parent=rig, op=68))
for key, sx, sy in (('vi', -1, 1), ('g', 1, 1), ('pk', 1, -1), ('y', -1, -1)):
    d = 57 * K
    add(layer(0, 'petal-' + key, [group([{'ty': 'el', 'p': st([0, 0]), 's': st([d, d])}, fill(COL[key])])], st([sx * 20 * K, sy * 20 * K, 0]), parent=rig, op=70))

# ---------------- letters: slide back into the logo (last letter first), shrinking and fading
for n in range(len(TEXT) - 1, -1, -1):
    ch, g = TEXT[n], gn[n]
    if ch == ' ': continue
    pen = Pen(gs, sc); gs[g].draw(pen)
    xs = [p[0] for c in pen.cs for p in c['v']]; ys = [p[1] for c in pen.cs for p in c['v']]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    shapes = [path([[round(a - cx, 2), round(b - cy, 2)] for a, b in c['v']], [[round(a, 2), round(b, 2)] for a, b in c['i']],
                   [[round(a, 2), round(b, 2)] for a, b in c['o']]) for c in pen.cs]
    x0 = TX0 + sum(adv[:n]) + cx; y0 = BASE + cy
    t0 = 6 + (len(TEXT) - 1 - n) * 1.3
    add(layer(0, 'ch-' + ch, [group(shapes + [fill(COL['ink'])])], anim([(t0, [x0, y0, 0], IN), (t0 + 16, [LX0 + 30, CY, 0])], IN),
              s=anim([(t0, [100, 100, 100], IN), (t0 + 16, [20, 20, 100])], IN), o=anim([(t0 + 8, 100, IN), (t0 + 16, 0)], IN), op=40))

add(layer(0, 'bg', [group([rect(W * 2, H * 2), fill(COL['wh'])])], st([W / 2, H / 2, 0])))
doc = {'v': '5.7.4', 'fr': FPS, 'ip': 0, 'op': OP, 'w': W, 'h': H, 'nm': 'Davo Delivery splash - dive', 'ddd': 0, 'assets': [], 'layers': layers}
out = os.path.join(HERE, 'davo-splash-dive.json'); json.dump(doc, open(out, 'w'), separators=(',', ':'))
print('ok', len(layers), 'layers', os.path.getsize(out) // 1024, 'KB')
