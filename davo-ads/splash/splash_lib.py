# Shared helpers for hand-built Lottie splashes (Davo Delivery).
import os, math
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.basePen import BasePen

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, '..', 'assets', 'fonts', 'Montserrat-900.woff2')
COL = {'y': '#ffce68', 'pk': '#fb4669', 'vi': '#5e3a9a', 'g': '#01bdac', 'ink': '#1d1430', 'wh': '#ffffff'}
# easings as (out-tangent, in-tangent) cubic handles
E = {
    'out':  ([.22, 1], [.36, 1]),      # power4.out-ish
    'in':   ([.7, 0], [.84, 0]),       # power4.in-ish (gravity / acceleration)
    'io':   ([.6, 0], [.4, 1]),
    'back': ([.34, 1.56], [.64, 1]),   # back.out(~1.6) — allowed overshoot
    'lin':  ([0, 0], [1, 1]),
}
def rgb(h, a=1): h = h.lstrip('#'); return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [a]
def st(v): return {'a': 0, 'k': v}
def anim(keys, ease='out'):
    """keys: [(frame, value[, ease_of_segment_starting_here]), ...]"""
    k = []
    for n, key in enumerate(keys):
        t, v = key[0], key[1]; e = E[key[2] if len(key) > 2 else ease]
        v = v if isinstance(v, list) else [v]; f = {'t': t, 's': v}
        if n < len(keys) - 1:
            d = len(v); f['o'] = {'x': [e[0][0]] * d, 'y': [e[0][1]] * d}; f['i'] = {'x': [e[1][0]] * d, 'y': [e[1][1]] * d}
        k.append(f)
    return {'a': 1, 'k': k}
def tr(p=None, s=None, r=None, o=None, a=None):
    return {'ty': 'tr', 'p': p or st([0, 0]), 'a': a or st([0, 0]), 's': s or st([100, 100]), 'r': r or st(0), 'o': o or st(100), 'sk': st(0), 'sa': st(0)}
def fill(c, o=100): return {'ty': 'fl', 'c': st(rgb(c)), 'o': o if isinstance(o, dict) else st(o), 'r': 1}
def stroke(c, w, o=100): return {'ty': 'st', 'c': st(rgb(c)), 'o': o if isinstance(o, dict) else st(o), 'w': w if isinstance(w, dict) else st(w), 'lc': 2, 'lj': 2}
def trim(s=None, e=None): return {'ty': 'tm', 's': s or st(0), 'e': e or st(100), 'o': st(0), 'm': 1}
def group(items, t=None, nm='g'): return {'ty': 'gr', 'nm': nm, 'it': items + [t or tr()]}
def ell(d, p=(0, 0)): return {'ty': 'el', 'p': st(list(p)), 's': d if isinstance(d, dict) else st([d, d])}
def rect(w, h, r=0, p=(0, 0)): return {'ty': 'rc', 'p': st(list(p)), 's': st([w, h]), 'r': st(r)}
def path(v, i=None, o=None, closed=True):
    z = [[0, 0]] * len(v); return {'ty': 'sh', 'ks': st({'c': closed, 'v': v, 'i': i or z, 'o': o or z})}
def cross_pts(K):
    a, b = 10.5 * K, 29 * K
    return [[-a, -b], [a, -b], [a, -a], [b, -a], [b, a], [a, a], [a, b], [-a, b], [-a, a], [-b, a], [-b, -a], [-a, -a]]

class Comp:
    def __init__(s, w, h, op, fr=60): s.w, s.h, s.op, s.fr, s.layers = w, h, op, fr, []
    def add(s, nm, shapes=None, p=None, sc=None, r=None, o=None, a=None, parent=None, null=False, ip=0, op=None):
        L = {'ddd': 0, 'ind': len(s.layers) + 1, 'ty': 3 if null else 4, 'nm': nm, 'sr': 1, 'ao': 0, 'bm': 0, 'ip': ip, 'op': op or s.op, 'st': 0,
             'ks': {'o': o or st(100), 'r': r or st(0), 'p': p or st([0, 0, 0]), 'a': a or st([0, 0, 0]), 's': sc or st([100, 100, 100])}}
        if not null: L['shapes'] = shapes or []
        if parent: L['parent'] = parent
        s.layers.append(L); return L['ind']
    def doc(s, nm):   # layers were added bottom -> top; Lottie wants top first
        return {'v': '5.7.4', 'fr': s.fr, 'ip': 0, 'op': s.op, 'w': s.w, 'h': s.h, 'nm': nm, 'ddd': 0, 'assets': [], 'layers': s.layers[::-1]}

# ---- wordmark as vector glyphs
_font = None
def glyphs(text, size):
    """-> list of (char, shapes centred on glyph bbox centre, cx_offset_from_text_left, cy_offset_from_baseline), total width"""
    global _font
    if _font is None: _font = instancer.instantiateVariableFont(TTFont(FONT), {'wght': 900})
    f = _font; gs, cmap, hmtx, upm = f.getGlyphSet(), f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm
    sc = size / upm
    class Pen(BasePen):
        def __init__(p, g): super().__init__(g); p.cs, p.cur = [], None
        def P(p, q): return [q[0] * sc, -q[1] * sc]
        def _moveTo(p, q): p.cur = {'v': [p.P(q)], 'i': [[0, 0]], 'o': [[0, 0]]}; p.cs.append(p.cur)
        def _lineTo(p, q): p.cur['v'].append(p.P(q)); p.cur['i'].append([0, 0]); p.cur['o'].append([0, 0])
        def _curveToOne(p, c1, c2, q):
            p0 = p.cur['v'][-1]; c1, c2, q = p.P(c1), p.P(c2), p.P(q)
            p.cur['o'][-1] = [c1[0] - p0[0], c1[1] - p0[1]]; p.cur['v'].append(q); p.cur['i'].append([c2[0] - q[0], c2[1] - q[1]]); p.cur['o'].append([0, 0])
        def _closePath(p):
            c = p.cur
            if len(c['v']) > 1 and all(abs(x - y) < 1e-6 for x, y in zip(c['v'][0], c['v'][-1])):
                c['i'][0] = c['i'][-1]; c['v'].pop(); c['i'].pop(); c['o'].pop()
        _endPath = _closePath
    out, x = [], 0
    for ch in text:
        g = cmap[ord(ch)]; adv = hmtx[g][0] * sc
        if ch != ' ':
            pen = Pen(gs); gs[g].draw(pen)
            xs = [q[0] for c in pen.cs for q in c['v']]; ys = [q[1] for c in pen.cs for q in c['v']]
            cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            R = lambda L: [[round(a, 2), round(b, 2)] for a, b in L]
            shapes = [path(R([[a - cx, b - cy] for a, b in c['v']]), R(c['i']), R(c['o'])) for c in pen.cs]
            out.append((ch, shapes, x + cx, cy))
        x += adv
    return out, x

def wordmark(comp, text, size, cx, base, color, t0, stagger=2, dur=20, dx=0, dy=60, order=1):
    """waterfall entry: each letter travels (dx,dy)->0 with power4.out, fades in over the first 60%."""
    gl, w = glyphs(text, size); x0 = cx - w / 2
    seq = gl if order > 0 else gl[::-1]
    for n, (ch, shapes, gx, gy) in enumerate(seq):
        t = t0 + n * stagger; X, Y = x0 + gx, base + gy
        comp.add('ch-' + ch, [group(shapes + [fill(color)])], anim([(t, [X + dx, Y + dy, 0]), (t + dur, [X, Y, 0])], 'out'),
                 o=anim([(t, 0), (t + dur * .6, 100)], 'out'))
    return w

def sample_cubics(segs, n=400):
    """segs: list of (p0,c1,c2,p3) -> dense polyline + cumulative arc length"""
    pts = []
    for (p0, c1, c2, p3) in segs:
        for i in range(0 if not pts else 1, n + 1):
            t = i / n; u = 1 - t
            pts.append([u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p3[0],
                        u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p3[1]])
    L = [0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return pts, L
def at_len(pts, L, f):
    target = f * L[-1]
    for i in range(1, len(L)):
        if L[i] >= target:
            k = (target - L[i - 1]) / max(1e-9, L[i] - L[i - 1]); a, b = pts[i - 1], pts[i]
            return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k], math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return pts[-1], 0
def cubic_bez(y1x, y1y, y2x, y2y, x):
    """evaluate CSS cubic-bezier easing at x (Newton)"""
    t = x
    for _ in range(12):
        bx = 3 * (1 - t)**2 * t * y1x + 3 * (1 - t) * t * t * y2x + t**3 - x
        d = 3 * (1 - t)**2 * y1x + 6 * (1 - t) * t * (y2x - y1x) + 3 * t * t * (1 - y2x)
        if abs(d) < 1e-6: break
        t = min(1, max(0, t - bx / d))
    return 3 * (1 - t)**2 * t * y1y + 3 * (1 - t) * t * t * y2y + t**3
