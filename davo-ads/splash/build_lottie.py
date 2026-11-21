# Davo Delivery — animated splash (Lottie JSON). Pure vectors: logo petals/cross + "Davo Delivery" wordmark
# converted from Montserrat Black glyph outlines (no font needed in the app).
# usage: python3 build_lottie.py [bg] -> davo-splash.json (transparent) and davo-splash-<bg>.json if bg given
import json, os, sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.basePen import BasePen

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, '..', 'assets', 'fonts', 'Montserrat-900.woff2')
FPS, W, H, OP = 60, 800, 800, 120               # 2.0 s; animation settles at ~1.3 s, then holds
CX, CY, LOGO = 400, 300, 270                    # logo centre and size (logo is drawn in a 131-unit box)
K = LOGO / 131
COL = {'y': '#ffce68', 'pk': '#fb4669', 'vi': '#5e3a9a', 'g': '#01bdac', 'ink': '#1d1430', 'wh': '#ffffff'}
BACK = dict(o={'x': [.34], 'y': [1.56]}, i={'x': [.64], 'y': [1]})     # ease-out-back (overshoot)
OUT = dict(o={'x': [.22], 'y': [1]}, i={'x': [.36], 'y': [1]})         # ease-out-quint-ish
IO = dict(o={'x': [.45], 'y': [0]}, i={'x': [.55], 'y': [1]})

def rgb(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1]
def st(v): return {'a': 0, 'k': v}
def anim(keys, ease=OUT):
    """keys: [(frame, value), ...] — same easing on every segment; last key holds."""
    k = []
    for n, (t, v) in enumerate(keys):
        v = v if isinstance(v, list) else [v]
        e = {'t': t, 's': v}
        if n < len(keys) - 1:
            d = len(v); e['o'] = {a: b * d for a, b in ease['o'].items()}; e['i'] = {a: b * d for a, b in ease['i'].items()}
        k.append(e)
    return {'a': 1, 'k': k}
def tr(): return {'ty': 'tr', 'p': st([0, 0]), 'a': st([0, 0]), 's': st([100, 100]), 'r': st(0), 'o': st(100), 'sk': st(0), 'sa': st(0)}
def fill(c): return {'ty': 'fl', 'c': st(rgb(c)), 'o': st(100), 'r': 1, 'nm': 'fill'}
def group(items, nm): return {'ty': 'gr', 'nm': nm, 'it': items + [tr()]}
def path(v, i=None, o=None, closed=True):
    z = [[0, 0]] * len(v); return {'ty': 'sh', 'ks': st({'c': closed, 'v': v, 'i': i or z, 'o': o or z})}
def layer(ind, nm, shapes, p, s=None, r=None, o=None, ip=0):
    return {'ddd': 0, 'ind': ind, 'ty': 4, 'nm': nm, 'sr': 1, 'ao': 0, 'bm': 0, 'ip': ip, 'op': OP, 'st': 0, 'shapes': shapes,
            'ks': {'o': o or st(100), 'r': r or st(0), 'p': p, 'a': st([0, 0, 0]), 's': s or st([100, 100, 100])}}

layers = []
# ---- cross: spins in from -90° with overshoot after the petals have opened
a, b = 10.5 * K, 29 * K
cross = [[-a, -b], [a, -b], [a, -a], [b, -a], [b, a], [a, a], [a, b], [-a, b], [-a, a], [-b, a], [-b, -a], [-a, -a]]
layers.append(layer(1, 'cross', [group([path(cross), fill(COL['wh'])], 'cross')], st([CX, CY, 0]),
                    s=anim([(24, [0, 0, 100]), (46, [100, 100, 100])], BACK), r=anim([(24, -90), (46, 0)], BACK)))
# ---- petals: burst out of the centre one by one (clockwise: yellow, pink, green, violet), then a soft "breath"
petals = [('y', -1, -1, 4), ('pk', 1, -1, 8), ('g', 1, 1, 12), ('vi', -1, 1, 16)]
draw_order = ['vi', 'g', 'pk', 'y']   # top -> bottom, matches the 2D logo (yellow drawn first)
for n, key in enumerate(draw_order):
    c, sx, sy, t0 = next(p for p in petals if p[0] == key)
    d = 57 * K; px, py = CX + sx * 20 * K, CY + sy * 20 * K
    layers.append(layer(2 + n, 'petal-' + key, [group([{'ty': 'el', 'p': st([0, 0]), 's': st([d, d])}, fill(COL[c])], key)],
                        anim([(t0, [CX, CY, 0]), (t0 + 22, [px, py, 0])], BACK),
                        s=anim([(t0, [0, 0, 100]), (t0 + 22, [100, 100, 100]), (50, [100, 100, 100]), (60, [104, 104, 100]), (72, [100, 100, 100])], IO)))

# ---- wordmark: Montserrat Black outlines, letters rise in with a stagger
font = instancer.instantiateVariableFont(TTFont(FONT), {'wght': 900})
gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font['hmtx']
upm = font['head'].unitsPerEm
class LottiePen(BasePen):
    def __init__(s, gs, sc): super().__init__(gs); s.sc, s.cs, s.cur = sc, [], None
    def P(s, p): return [p[0] * s.sc, -p[1] * s.sc]
    def _moveTo(s, p): s.cur = {'v': [s.P(p)], 'i': [[0, 0]], 'o': [[0, 0]]}; s.cs.append(s.cur)
    def _lineTo(s, p): s.cur['v'].append(s.P(p)); s.cur['i'].append([0, 0]); s.cur['o'].append([0, 0])
    def _curveToOne(s, c1, c2, p):
        p0 = s.cur['v'][-1]; c1, c2, p = s.P(c1), s.P(c2), s.P(p)
        s.cur['o'][-1] = [c1[0] - p0[0], c1[1] - p0[1]]
        s.cur['v'].append(p); s.cur['i'].append([c2[0] - p[0], c2[1] - p[1]]); s.cur['o'].append([0, 0])
    def _closePath(s):
        c = s.cur
        if len(c['v']) > 1 and all(abs(x - y) < 1e-6 for x, y in zip(c['v'][0], c['v'][-1])):
            c['i'][0] = c['i'][-1]; c['v'].pop(); c['i'].pop(); c['o'].pop()
    _endPath = _closePath
TEXT, SIZE, BASE = "Davo Delivery", 84, 552
sc = SIZE / upm
gnames = [font.getBestCmap()[ord(ch)] for ch in TEXT]
adv = [hmtx[g][0] * sc for g in gnames]; total = sum(adv) - 0; x = (W - total) / 2
ind = 10
for n, (ch, g, w) in enumerate(zip(TEXT, gnames, adv)):
    if ch != ' ':
        pen = LottiePen(gs, sc); gs[g].draw(pen)
        shapes = [path([[round(a, 2), round(b, 2)] for a, b in c['v']], [[round(a, 2), round(b, 2)] for a, b in c['i']],
                       [[round(a, 2), round(b, 2)] for a, b in c['o']]) for c in pen.cs]
        t0 = 44 + n * 2.2
        layers.append(layer(ind, 'ch-' + ch, [group(shapes + [fill(COL['ink'])], ch)],
                            anim([(t0, [x, BASE + 46, 0]), (t0 + 20, [x, BASE, 0])], OUT),
                            o=anim([(t0, 0), (t0 + 12, 100)], OUT))); ind += 1
    x += w

def doc(bg=None):
    L = list(layers)
    if bg: L.append(layer(99, 'bg', [group([{'ty': 'rc', 'p': st([0, 0]), 's': st([W * 4, H * 4]), 'r': st(0)}, fill(bg)], 'bg')], st([W / 2, H / 2, 0])))
    return {'v': '5.7.4', 'fr': FPS, 'ip': 0, 'op': OP, 'w': W, 'h': H, 'nm': 'Davo Delivery splash', 'ddd': 0, 'assets': [], 'layers': L}
json.dump(doc(), open(os.path.join(HERE, 'davo-splash.json'), 'w'), separators=(',', ':'))
if len(sys.argv) > 1: json.dump(doc(sys.argv[1]), open(os.path.join(HERE, f'davo-splash-{sys.argv[1].lstrip("#")}.json'), 'w'), separators=(',', ':'))
print('ok', len(layers), 'layers', os.path.getsize(os.path.join(HERE, 'davo-splash.json')) // 1024, 'KB')
