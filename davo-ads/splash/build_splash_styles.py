# Three more Davo Delivery splash styles (Lottie, 1080x2340 portrait, 60 fps). Each is a causal chain that ends
# on a held logo + wordmark, so the app can crossfade in.
#   drop    — white:   a yellow drop falls, splashes (squash + shock ring), splits into the four petals, the cross cuts in
#   route   — sky:     a courier dot races along a winding route, arrives, the route snaps in behind it, the logo bursts out
#   capsule — violet:  a two-tone capsule tumbles in, lands, a beat of stillness, it cracks open and the logo bursts out of it
# usage: python3 build_splash_styles.py   -> davo-splash-{drop,route,capsule}.json
import json, math, os
from splash_lib import *

W, H = 1080, 2340
LOGO = 330; K = LOGO / 131; D = 57 * K; OFF = 20 * K
CX, CY = W / 2, 1040
TEXT, TS, TB = 'Davo Delivery', 112, 1040 + LOGO / 2 + 175
PET = [('y', -1, -1), ('pk', 1, -1), ('g', 1, 1), ('vi', -1, 1)]          # clockwise from top-left
def bg(c, col):
    c.add('bg', [group([rect(W * 3, H * 3), fill(col)])], st([W / 2, H / 2, 0]))
def save(c, name):
    out = os.path.join(HERE, f'davo-splash-{name}.json'); json.dump(c.doc('Davo Delivery splash - ' + name), open(out, 'w'), separators=(',', ':'))
    print(name, len(c.layers), 'layers', os.path.getsize(out) // 1024, 'KB')
def cross_wipe(c, rig, t, col='#ffffff'):
    """white cross cut in as two bars: horizontal then vertical (negative space carved through the petals)"""
    a, b = 10.5 * K, 29 * K
    c.add('cross-v', [group([rect(2 * a, 2 * b), fill(col)])], st([0, 0, 0]), sc=anim([(t + 4, [100, 0, 100]), (t + 16, [100, 100, 100])], 'back'), parent=rig)
    c.add('cross-h', [group([rect(2 * b, 2 * a), fill(col)])], st([0, 0, 0]), sc=anim([(t, [0, 100, 100]), (t + 12, [100, 100, 100])], 'back'), parent=rig)

# ======================================================================= 1. DROP
def drop():
    c = Comp(W, H, 150); bg(c, '#ffffff')
    rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    T_HIT = 30
    # shock ring on the impact frame
    c.add('ring', [group([ell(anim([(T_HIT, [40, 40]), (T_HIT + 26, [760, 760])], 'out')), stroke(COL['y'], anim([(T_HIT, 22), (T_HIT + 26, 2)], 'out'))])],
          st([CX, CY, 0]), o=anim([(T_HIT, 90), (T_HIT + 26, 0)], 'out'), ip=T_HIT)
    # three sibling droplets spawn from the splash and fly to their petal seats
    for n, (k, sx, sy) in enumerate(PET[1:]):
        t = T_HIT + 1 + n * 2
        c.add('petal-' + k, [group([ell(D), fill(COL[k])])], anim([(t, [0, 0, 0]), (t + 20, [sx * OFF, sy * OFF, 0])], 'back'),
              sc=anim([(t, [10, 10, 100]), (t + 20, [100, 100, 100])], 'back'), parent=rig, ip=t)
    # the carrier: the yellow drop falls (gravity), stretches, squashes on impact, then becomes the yellow petal
    k, sx, sy = PET[0]
    c.add('drop', [group([ell(D), fill(COL[k])])],
          anim([(0, [0, -1250, 0], 'in'), (T_HIT, [0, 0, 0], 'out'), (T_HIT + 20, [sx * OFF, sy * OFF, 0])], 'out'),
          sc=anim([(0, [34, 46, 100], 'in'), (T_HIT - 2, [30, 52, 100], 'out'), (T_HIT, [62, 24, 100], 'back'), (T_HIT + 20, [100, 100, 100])], 'out'),
          parent=rig)
    cross_wipe(c, rig, 52)
    # stillness 66-76, then the name rises in a waterfall
    wordmark(c, TEXT, TS, CX, TB, COL['ink'], 78, stagger=2, dur=22, dy=70)
    save(c, 'drop')

# ======================================================================= 2. ROUTE
def route():
    c = Comp(W, H, 156); bg(c, '#dff6fd')
    # faint city grid (static map texture: streets)
    streets = []
    for i in range(-2, 14): streets.append(path([[i * 120 - 300, -200], [i * 120 + 500, 2600]], closed=False))
    for j in range(-2, 24): streets.append(path([[-200, j * 120], [1300, j * 120 - 180]], closed=False))
    c.add('streets', [group(streets + [stroke('#c4ebf6', 6)])], st([0, 0, 0]))
    segs = [((-80, 2180), (260, 2140), (180, 1780), (520, 1720)), ((520, 1720), (900, 1650), (980, 1380), (700, 1300)),
            ((700, 1300), (380, 1210), (180, 1000), (420, 880)), ((420, 880), (600, 790), (640, 930), (CX, CY))]
    pts, L = sample_cubics(segs, 200)
    T0, T1 = 2, 56                                    # courier travel
    ease = lambda x: cubic_bez(.45, 0, .2, 1, x)      # accelerate out of the corner, brake into the destination
    # route line: drawn by the courier (trim end), then snapped in behind it (trim start)
    v = [[round(x, 1), round(y, 1)] for x, y in pts[::3]] + [[CX, CY]]
    ekeys = [(t, 100 * ease((t - T0) / (T1 - T0)), 'lin') for t in range(T0, T1 + 1, 2)]
    c.add('route', [group([path(v, closed=False), stroke(COL['g'], 18), trim(s=anim([(T1 - 2, 0), (T1 + 14, 100)], 'out'), e=anim(ekeys))])], st([0, 0, 0]), op=T1 + 16)
    c.add('route-dash', [group([path(v, closed=False), {'ty': 'st', 'c': st(rgb('#ffffff')), 'o': st(100), 'w': st(5), 'lc': 2, 'lj': 2,
          'd': [{'n': 'd', 'nm': 'dash', 'v': st(14)}, {'n': 'g', 'nm': 'gap', 'v': st(22)}, {'n': 'o', 'nm': 'offset', 'v': st(0)}]},
          trim(s=anim([(T1 - 2, 0), (T1 + 14, 100)], 'out'), e=anim(ekeys))])], st([0, 0, 0]), op=T1 + 16)
    # logo bursts out of the arrival point (scale-burst), staggered clockwise; confetti flies outward on the same frame
    rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    for n, (k, sx, sy) in enumerate(PET):
        t = T1 + 2 + n * 2
        c.add('petal-' + k, [group([ell(D), fill(COL[k])])], anim([(t, [0, 0, 0]), (t + 18, [sx * OFF, sy * OFF, 0])], 'back'),
              sc=anim([(t, [0, 0, 100]), (t + 18, [100, 100, 100])], 'back'), parent=rig, ip=t)
    c.add('cross', [group([path(cross_pts(K)), fill('#ffffff')])], st([0, 0, 0]), parent=rig,
          sc=anim([(T1 + 10, [0, 0, 100]), (T1 + 28, [100, 100, 100])], 'back'), r=anim([(T1 + 10, -90), (T1 + 28, 0)], 'back'))
    for i in range(12):
        a = i / 12 * 2 * math.pi + .2; dist = 430 + (i % 3) * 70; col = COL[['y', 'pk', 'vi', 'g'][i % 4]]
        c.add(f'conf{i}', [group([ell(18 + (i % 3) * 6), fill(col)])],
              anim([(T1, [CX, CY, 0]), (T1 + 30, [CX + math.cos(a) * dist, CY + math.sin(a) * dist, 0])], 'out'),
              o=anim([(T1 + 14, 100), (T1 + 30, 0)], 'out'), ip=T1, op=T1 + 31)
    # courier pin: rides the line head, squashes on arrival and dives into the logo centre
    pkeys, rkeys = [], []
    for t in range(T0, T1 + 1, 2):
        p, ang = at_len(pts, L, ease((t - T0) / (T1 - T0))); pkeys.append((t, [p[0], p[1], 0], 'lin'))
    c.add('courier', [group([ell(64), fill(COL['pk'])]), group([ell(26), fill('#ffffff')])], anim(pkeys),
          sc=anim([(T1 - 1, [100, 100, 100]), (T1 + 2, [135, 70, 100], 'in'), (T1 + 8, [0, 0, 100])], 'out'), op=T1 + 9)
    wordmark(c, TEXT, TS, CX, TB, COL['ink'], T1 + 36, stagger=2, dur=22, dx=110, dy=0)   # enters on the current (moving LEFT)
    save(c, 'route')

# ======================================================================= 3. CAPSULE
def capsule():
    c = Comp(W, H, 160); bg(c, '#2a1748')
    c.add('glow', [group([ell(1500), {'ty': 'gf', 'o': st(100), 'r': 1, 't': 2, 's': st([0, 0]), 'e': st([750, 0]), 'g': {'p': 2, 'k': st([0, .37, .23, .6, 1, .16, .09, .28])}}])],
          st([CX, CY, 0]), o=anim([(0, 60), (70, 60, 'out'), (90, 100)]))
    CW, CH = 170, 380; T_LAND, T_OPEN = 32, 62                   # land, hold ~0.45 s (stillness before climax), crack open
    cap = c.add('capsule', null=True, p=anim([(0, [CX, -300, 0], 'in'), (T_LAND, [CX, CY, 0])]),
                r=anim([(0, -200, 'out'), (T_LAND, -12, 'out'), (T_LAND + 10, 0)]),
                sc=anim([(T_LAND, [100, 100, 100], 'out'), (T_LAND + 3, [112, 86, 100], 'out'), (T_LAND + 14, [100, 100, 100])]))
    half = lambda col, sgn: [group([ell(CW, (0, sgn * (CH / 2 - CW / 2))), fill(col)]), group([rect(CW, CH / 2 - CW / 2 + 2, 0, (0, sgn * (CH / 2 - CW / 2) / 2)), fill(col)]),
                             group([rect(CW * .16, CH * .3, CW * .08, (-CW * .22, sgn * CH * .2)), fill('#ffffff', 28)])]
    # halves fly apart along their own axis the instant it cracks; fade as they leave
    c.add('top', half(COL['pk'], -1), anim([(T_OPEN, [0, 0, 0]), (T_OPEN + 26, [0, -900, 0])], 'out'),
          r=anim([(T_OPEN, 0), (T_OPEN + 26, -35)], 'out'), o=anim([(T_OPEN + 8, 100), (T_OPEN + 24, 0)], 'out'), parent=cap, op=T_OPEN + 27)
    c.add('bottom', half(COL['g'], 1), anim([(T_OPEN, [0, 0, 0]), (T_OPEN + 26, [0, 900, 0])], 'out'),
          r=anim([(T_OPEN, 0), (T_OPEN + 26, 35)], 'out'), o=anim([(T_OPEN + 8, 100), (T_OPEN + 24, 0)], 'out'), parent=cap, op=T_OPEN + 27)
    # tension: a hairline of light opens along the seam just before the crack
    c.add('seam', [group([rect(CW + 30, 6, 3), fill('#ffffff')])], st([CX, CY, 0]),
          sc=anim([(T_OPEN - 10, [0, 100, 100], 'in'), (T_OPEN, [100, 100, 100], 'out'), (T_OPEN + 6, [300, 0, 100])]), ip=T_OPEN - 10, op=T_OPEN + 7)
    rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    for n, (k, sx, sy) in enumerate(PET):
        t = T_OPEN + 1 + n * 2
        c.add('petal-' + k, [group([ell(D), fill(COL[k])])], anim([(t, [0, 0, 0]), (t + 20, [sx * OFF, sy * OFF, 0])], 'back'),
              sc=anim([(t, [0, 0, 100]), (t + 20, [100, 100, 100])], 'back'), parent=rig, ip=t)
    c.add('cross', [group([path(cross_pts(K)), fill('#ffffff')])], st([0, 0, 0]), parent=rig,
          sc=anim([(T_OPEN + 10, [0, 0, 100]), (T_OPEN + 28, [100, 100, 100])], 'back'), r=anim([(T_OPEN + 10, 90), (T_OPEN + 28, 0)], 'back'))
    for i in range(10):   # little white crosses spray out of the capsule
        a = i / 10 * 2 * math.pi + .3; dist = 520 + (i % 2) * 120; s = 30 + (i % 3) * 10
        c.add(f'spark{i}', [group([path(cross_pts(s / 58)), fill('#ffffff')])],
              anim([(T_OPEN, [CX, CY, 0]), (T_OPEN + 34, [CX + math.cos(a) * dist, CY + math.sin(a) * dist, 0])], 'out'),
              r=anim([(T_OPEN, 0), (T_OPEN + 34, 140)], 'out'), o=anim([(T_OPEN + 16, 100), (T_OPEN + 34, 0)], 'out'), ip=T_OPEN, op=T_OPEN + 35)
    wordmark(c, TEXT, TS, CX, TB, '#ffffff', T_OPEN + 34, stagger=2, dur=22, dy=70)
    save(c, 'capsule')

drop(); route(); capsule()
