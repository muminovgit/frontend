# Nine distinct Davo Delivery splash choreographies (Lottie, 1080x2340, 60 fps). Same palette on purpose — the
# difference is the motion idea. Colours get tuned after a pick.
# usage: python3 build_splash_nine.py -> davo-splash-n{1..9}-<name>.json
import json, math, os, random
from splash_lib import *

W, H = 1080, 2340
LOGO = 330; K = LOGO / 131; D = 57 * K; OFF = 20 * K
CX, CY = W / 2, 1040
TEXT, TS, TB = 'Davo Delivery', 112, 1040 + LOGO / 2 + 175
PET = [('y', -1, -1), ('pk', 1, -1), ('g', 1, 1), ('vi', -1, 1)]
KAP = .5523
def circ(r, cx=0, cy=0):
    v = [[cx, cy - r], [cx + r, cy], [cx, cy + r], [cx - r, cy]]
    i = [[-r * KAP, 0], [0, -r * KAP], [r * KAP, 0], [0, r * KAP]]; o = [[r * KAP, 0], [0, r * KAP], [-r * KAP, 0], [0, -r * KAP]]
    return {'c': True, 'v': v, 'i': i, 'o': o}
def bg(c, col='#ffffff'): c.add('bg', [group([rect(W * 3, H * 3), fill(col)])], st([W / 2, H / 2, 0]))
def save(c, name):
    out = os.path.join(HERE, f'davo-splash-{name}.json'); json.dump(c.doc('Davo splash ' + name), open(out, 'w'), separators=(',', ':'))
    print(name, os.path.getsize(out) // 1024, 'KB')
def seat(k): sx, sy = next((a, b) for kk, a, b in PET if kk == k); return sx * OFF, sy * OFF
def cross(c, rig, t, rot=-90, col='#ffffff'):
    c.add('cross', [group([path(cross_pts(K)), fill(col)])], st([0, 0, 0]), parent=rig,
          sc=anim([(t, [0, 0, 100]), (t + 18, [100, 100, 100])], 'back'), r=anim([(t, rot), (t + 18, 0)], 'back'), ip=t)
def cross_wipe(c, rig, t, col='#ffffff'):
    a, b = 10.5 * K, 29 * K
    c.add('cross-v', [group([rect(2 * a, 2 * b), fill(col)])], st([0, 0, 0]), sc=anim([(t + 4, [100, 0, 100]), (t + 16, [100, 100, 100])], 'back'), parent=rig, ip=t + 4)
    c.add('cross-h', [group([rect(2 * b, 2 * a), fill(col)])], st([0, 0, 0]), sc=anim([(t, [0, 100, 100]), (t + 12, [100, 100, 100])], 'back'), parent=rig, ip=t)
def word(c, t, ink=COL['ink'], **kw): wordmark(c, TEXT, TS, CX, TB, ink, t, **{'stagger': 2, 'dur': 22, 'dy': 70, **kw})
def sampled(fn, t0, t1, step=2):
    """keyframes from a python function of normalised time (linear between samples)"""
    return [(t, fn((t - t0) / (t1 - t0)), 'lin') for t in list(range(t0, t1, step)) + [t1]]

# ------------------------------------------------------------------ 1. ORBIT — petals spiral in, ghosts trail them, snap
def n1():
    c = Comp(W, H, 150); bg(c); rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    T0, T1 = 0, 58
    ez = lambda x: cubic_bez(.5, 0, .2, 1, x)
    for n, (k, sx, sy) in enumerate(PET):
        a_end = math.atan2(sy, sx); r_end = OFF * math.sqrt(2)
        def pos(u, lag=0, a_end=a_end, r_end=r_end, n=n):
            e = ez(max(0, u)); a = a_end - (1 - e) * (2.2 * math.pi) ; r = r_end + (1 - e) * (560 + n * 40)
            return [math.cos(a) * r, math.sin(a) * r, 0]
        for g, (lag, op_) in enumerate([(6, 14), (4, 26), (2, 45), (0, 100)]):   # ghosts first (drawn under)
            keys = sampled(lambda u, lag=lag: pos(u - lag / (T1 - T0)), T0, T1)
            c.add(f'{k}-{g}', [group([ell(D), fill(COL[k])])], anim(keys), parent=rig,
                  sc=anim([(T0, [35, 35, 100]), (T1, [100, 100, 100])], 'io'),
                  o=st(op_) if lag == 0 else anim([(T1 - 4, op_), (T1 + 2, 0)]), op=OP_ if False else (150 if lag == 0 else T1 + 3))
    # impact on arrival: the whole mark squashes, then the cross spins in
    c.layers[0]  # (bg)
    c.add('impact', null=True)
    rig_s = anim([(T1, [100, 100, 100], 'out'), (T1 + 4, [108, 92, 100], 'back'), (T1 + 16, [100, 100, 100])])
    c.layers[rig - 1]['ks']['s'] = rig_s
    cross(c, rig, T1 + 4)
    word(c, T1 + 30)
    save(c, 'n1-orbit')

# ------------------------------------------------------------------ 2. HEARTBEAT — an ECG trace; the logo is the beat
def n2():
    c = Comp(W, H, 140); bg(c); y = CY
    pts = [[-60, y], [300, y], [340, y - 40], [380, y], [440, y], [470, y + 60], [CX, y - 520], [610, y + 240], [650, y], [720, y], [760, y - 50], [800, y], [1140, y]]
    T0, T1 = 2, 54; ez = lambda x: cubic_bez(.3, .1, .3, 1, x)
    TBt = 24                                          # the spike passes the centre: the logo is born on this beat
    # head = trim end; tail chases it so a glowing segment travels across
    E_ = c.add('ecg', [group([path(pts, closed=False), stroke(COL['pk'], 16), trim(s=anim(sampled(lambda u: max(0, 138 * ez(u) - 38), T0 + 8, T1 + 16)),
                                                                                    e=anim(sampled(lambda u: 100 * ez(u), T0, T1)))])], st([0, 0, 0]), op=T1 + 17)
    # fix 1: the trace never crosses the logo — a hole (subtract mask) opens around the logo on the beat
    R0, R1 = 4, LOGO * .62
    def oval(rx, ry):   # the hole is a tall oval so the whole spike (up to -520 / +240) disappears with it
        o = circ(1, CX, CY)
        o['v'] = [[CX, CY - ry], [CX + rx, CY], [CX, CY + ry], [CX - rx, CY]]
        o['i'] = [[-rx * KAP, 0], [0, -ry * KAP], [rx * KAP, 0], [0, ry * KAP]]; o['o'] = [[rx * KAP, 0], [0, ry * KAP], [-rx * KAP, 0], [0, -ry * KAP]]
        return o
    hole = {'a': 1, 'k': [{'t': TBt - 6, 's': [oval(R0, R0)], 'o': {'x': [.22], 'y': [1]}, 'i': {'x': [.36], 'y': [1]}}, {'t': TBt + 4, 's': [oval(R1, 600)]}]}
    lay = c.layers[E_ - 1]; lay['hasMask'] = True
    lay['masksProperties'] = [{'inv': False, 'mode': 's', 'pt': hole, 'o': st(100), 'x': st(0), 'nm': 'logo-hole'}]
    # logo thumps twice (lub-dub); fix 5: one gentle beat (1.0 -> 1.05 -> 1.0) near the end so the hold keeps living
    rig = c.add('rig', null=True, p=st([CX, CY, 0]), sc=anim([(TBt, [0, 0, 100], 'back'), (TBt + 10, [86, 86, 100], 'io'), (TBt + 16, [76, 76, 100], 'back'),
                                                              (TBt + 26, [104, 104, 100], 'io'), (TBt + 36, [100, 100, 100]), (104, [100, 100, 100], 'io'),
                                                              (112, [105, 105, 100], 'io'), (124, [100, 100, 100])]))
    # fix 3: rings thicker and darker so they read on a phone
    for tb in (TBt, TBt + 16):
        c.add(f'pulse{tb}', [group([ell(anim([(tb, [260, 260]), (tb + 30, [900, 900])], 'out')), stroke(COL['pk'], anim([(tb, 12), (tb + 30, 7)], 'out'))])],
              st([CX, CY, 0]), o=anim([(tb, 95), (tb + 30, 0)], 'out'), ip=tb, op=tb + 31)
    for k, sx, sy in PET:
        c.add('petal-' + k, [group([ell(D), fill(COL[k])])], st([sx * OFF, sy * OFF, 0]), parent=rig)
    # fix 2: the cross pops (0 -> 1) together with the circles, no cross-less frame
    c.add('cross', [group([path(cross_pts(K)), fill('#ffffff')])], st([0, 0, 0]), parent=rig,
          sc=anim([(TBt + 2, [0, 0, 100]), (TBt + 12, [100, 100, 100])], 'out'), ip=TBt + 2)
    # fix 4: the name simply fades in while rising ~10 pt, as one calm piece (no per-letter drop)
    word(c, TBt + 46, stagger=0, dur=26, dy=32)
    save(c, 'n2-heartbeat')

# ------------------------------------------------------------------ 3. TILES — four squares slam in from four edges, then round off
def n3():
    c = Comp(W, H, 150); bg(c); rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    src = {'y': (-900, 0), 'pk': (0, -1300), 'g': (900, 0), 'vi': (0, 1300)}
    TM = 44
    for n, (k, sx, sy) in enumerate(PET):
        t = 4 + n * 6; th = t + 16; X, Y = sx * OFF, sy * OFF; dx, dy = src[k]
        c.add('tile-' + k, [group([{'ty': 'rc', 'p': st([0, 0]), 's': st([D, D]), 'r': anim([(TM, 14, 'io'), (TM + 14, D / 2)], 'back')}, fill(COL[k])])],
              anim([(t, [X + dx, Y + dy, 0], 'in'), (th, [X, Y, 0])]), parent=rig,
              sc=anim([(th, [100, 100, 100], 'out'), (th + 3, [100 - abs(dy) / 130, 100 - abs(dx) / 90, 100], 'back'), (th + 12, [100, 100, 100])]),
              r=anim([(t, (n - 1.5) * 30, 'in'), (th, 0)]))
    cross_wipe(c, rig, TM + 14)
    word(c, TM + 40)
    save(c, 'n3-tiles')

# ------------------------------------------------------------------ 4. DRAW-ON — outlines are drawn, then colour floods in
def n4():
    c = Comp(W, H, 156); bg(c); rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    for n, (k, sx, sy) in enumerate(PET):
        t = 2 + n * 5; X, Y = sx * OFF, sy * OFF
        c.add('fill-' + k, [group([ell(D), fill(COL[k])])], st([X, Y, 0]), parent=rig, sc=anim([(t + 30, [0, 0, 100]), (t + 48, [100, 100, 100])], 'out'), ip=t + 30)
        c.add('line-' + k, [group([ell(D - 10), stroke(COL[k], 10), trim(e=anim([(t, 0), (t + 32, 100)], 'io'))])], st([X, Y, 0]), parent=rig,
              r=st(-90 + n * 90), o=anim([(t + 44, 100), (t + 52, 0)]), op=t + 53)
    cross_wipe(c, rig, 72)
    word(c, 96)
    save(c, 'n4-draw')

# ------------------------------------------------------------------ 5. FLIP — an app icon flips through the colours and lands on the logo
def n5():
    c = Comp(W, H, 156); bg(c, '#eef1f6'); S = LOGO * 1.18
    flips = [16, 30, 42, 52, 60]                     # each flip faster than the last
    card = c.add('card', null=True, p=anim([(0, [CX, CY + 500, 0]), (16, [CX, CY, 0])]),
                 sc=anim(sum([[(a, [100, 100, 100], 'in'), ((a + b) / 2, [0, 100, 100], 'out')] for a, b in zip(flips, flips[1:])], []) + [(flips[-1], [100, 100, 100], 'back'), (flips[-1] + 6, [100, 100, 100])]))
    c.add('shadow', [group([rect(S, S, S * .24), fill('#1d1430', 7)])], st([CX, CY + 26, 0]),
          sc=anim(sum([[(a, [100, 100, 100], 'in'), ((a + b) / 2, [0, 100, 100], 'out')] for a, b in zip(flips, flips[1:])], []) + [(flips[-1], [100, 100, 100])]))
    faces = ['y', 'pk', 'g', 'vi']
    for n, k in enumerate(faces):
        a = 0 if n == 0 else (flips[n - 1] + flips[n]) / 2; b = (flips[n] + flips[n + 1]) / 2
        c.add('face-' + k, [group([path(cross_pts(K * .9)), fill('#ffffff')]), group([rect(S, S, S * .24), fill(COL[k])])], st([0, 0, 0]), parent=card, ip=a, op=b)
    a = (flips[-2] + flips[-1]) / 2
    c.add('face-logo', [group([rect(S, S, S * .24), fill('#ffffff')])], st([0, 0, 0]), parent=card, ip=a)
    for k, sx, sy in PET:
        c.add('lp-' + k, [group([ell(D * .82), fill(COL[k])])], st([sx * OFF * .82, sy * OFF * .82, 0]), parent=card, ip=a)
    c.add('lx', [group([path(cross_pts(K * .82)), fill('#ffffff')])], st([0, 0, 0]), parent=card, ip=a)
    word(c, flips[-1] + 16)
    save(c, 'n5-flip')

# ------------------------------------------------------------------ 6. TYPE — the name is typed; its "o" becomes the logo
def n6():
    c = Comp(W, H, 160); bg(c)
    gl, w = glyphs(TEXT, TS); x0 = CX - w / 2; Y0 = CY + TS * .36
    TT, TM = 4, 62                                 # typing starts, text moves down
    o_idx = TEXT.index('o')
    rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    for k, sx, sy in PET:
        c.add('petal-' + k, [group([ell(D), fill(COL[k])])], anim([(TM + 4, [0, 0, 0]), (TM + 24, [sx * OFF, sy * OFF, 0])], 'back'),
              sc=anim([(TM + 4, [0, 0, 100]), (TM + 24, [100, 100, 100])], 'back'), parent=rig, ip=TM + 4)
    cross(c, rig, TM + 18)
    n_ch = 0
    for i, (ch, shapes, gx, gy) in enumerate(gl):
        t = TT + n_ch * 3; n_ch += 1
        X = x0 + gx; Ytyped, Yfinal = Y0 + gy, TB + gy
        if i == 2:   # gl index 2 is the 'o' of "Davo" ('D','a','v','o' -> but spaces skipped) — find by char instead
            pass
        if ch == 'o' and i == [j for j, g in enumerate(gl) if g[0] == 'o'][0]:
            # the carrier: the typed "o" swells into the logo position and dissolves as the petals burst from it
            c.add('o-carrier', [group(shapes + [fill(COL['ink'])])], anim([(TM - 6, [X, Ytyped, 0], 'in'), (TM + 4, [CX, CY, 0])]),
                  sc=anim([(TM - 6, [100, 100, 100], 'in'), (TM + 4, [260, 260, 100]), (TM + 12, [60, 60, 100])]),
                  o=anim([(t, 0, 'lin'), (t + 1, 100), (TM + 4, 100, 'out'), (TM + 12, 0)]), op=TM + 13)
            c.add('o-final', [group(shapes + [fill(COL['ink'])])], anim([(TM + 10, [X, Yfinal + 40, 0]), (TM + 28, [X, Yfinal, 0])]), o=anim([(TM + 10, 0), (TM + 22, 100)]), ip=TM + 10)
            continue
        c.add('ch-' + ch, [group(shapes + [fill(COL['ink'])])], anim([(TM, [X, Ytyped, 0], 'io'), (TM + 22, [X, Yfinal, 0])]),
              o=anim([(t, 0, 'lin'), (t + 1, 100)]), sc=anim([(t, [70, 70, 100], 'back'), (t + 6, [100, 100, 100])]))
    # caret rides the typing head, then leaves
    keys = [(TT + n * 3, [x0 + (gl[n][2] + 36 if n < len(gl) else w + 10), Y0 - TS * .36, 0], 'lin') for n in range(len(gl))]
    c.add('caret', [group([rect(10, TS * 1.05, 5), fill(COL['pk'])])], anim(keys + [(TT + len(gl) * 3 + 2, [x0 + w + 18, Y0 - TS * .36, 0])]),
          o=anim([(TM - 8, 100), (TM - 2, 0)]), op=TM)
    save(c, 'n6-type')

# ------------------------------------------------------------------ 7. LIQUID — empty rings fill up with a moving wave
def n7():
    c = Comp(W, H, 160); bg(c); rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    for n, (k, sx, sy) in enumerate(PET):
        X, Y = sx * OFF, sy * OFF; t = 14 + n * 7; R = D / 2
        c.add('ring-' + k, [group([ell(D - 8), stroke(COL[k], 8, 35)])], st([X, Y, 0]), parent=rig, sc=anim([(n * 3, [0, 0, 100]), (n * 3 + 14, [100, 100, 100])], 'back'), op=t + 46)
        # wave: wide shape with a sinus crest, masked by the petal circle; rises and slides sideways
        wv, wi, wo = [], [], []; seg = R * .9; N = 8
        for j in range(N + 1):
            x = -N / 2 * seg + j * seg; amp = 22 if j % 2 else -22
            wv.append([x, amp]); wi.append([-seg * .4, 0]); wo.append([seg * .4, 0])
        wv += [[N / 2 * seg, R * 3], [-N / 2 * seg, R * 3]]; wi += [[0, 0], [0, 0]]; wo += [[0, 0], [0, 0]]
        L = c.add('liquid-' + k, [group([{'ty': 'sh', 'ks': st({'c': True, 'v': wv, 'i': wi, 'o': wo})}, fill(COL[k])],
                                         tr(p=anim([(t, [-seg * 2, R + 30]), (t + 40, [0, -R - 30])], 'io')))], st([X, Y, 0]), parent=rig, ip=t)
        lay = c.layers[L - 1]; lay['hasMask'] = True
        lay['masksProperties'] = [{'inv': False, 'mode': 'a', 'pt': st(circ(R)), 'o': st(100), 'x': st(0), 'nm': 'm'}]
    cross_wipe(c, rig, 76)
    word(c, 100)
    save(c, 'n7-liquid')

# ------------------------------------------------------------------ 8. NOTIFICATION — "order arrived" drops in and becomes the app icon
def n8():
    c = Comp(W, H, 170); bg(c, '#eef1f6')
    CWd, CHt = 940, 230; TY = 330; TM = 58; S = LOGO * 1.18
    sz = anim([(TM, [CWd, CHt], 'io'), (TM + 20, [S, S])]); rad = anim([(TM, 52, 'io'), (TM + 20, S * .24)])
    pos = anim([(4, [CX, -200, 0]), (24, [CX, TY, 0], 'back'), (30, [CX, TY, 0]), (TM, [CX, TY, 0], 'io'), (TM + 20, [CX, CY, 0])])
    c.add('n-shadow', [group([{'ty': 'rc', 'p': st([0, 24]), 's': sz, 'r': rad}, fill('#1d1430', 8)])], pos)
    card = c.add('n-card', [group([{'ty': 'rc', 'p': st([0, 0]), 's': sz, 'r': rad}, fill('#ffffff')])], pos)
    # card content: tiny app icon + two lines; fades the moment the morph starts
    ico = c.add('n-ico', null=True, p=st([-CWd / 2 + 110, 0, 0]), parent=card, sc=st([36, 36, 100]))
    for k, sx, sy in PET: c.add('ni-' + k, [group([ell(D), fill(COL[k])])], st([sx * OFF, sy * OFF, 0]), parent=ico, op=TM + 6)
    c.add('ni-x', [group([path(cross_pts(K)), fill('#ffffff')])], st([0, 0, 0]), parent=ico, op=TM + 6)
    for txt, size, y, col in (('Davo Delivery', 42, -34, COL['ink']), ('Buyurtmangiz yetib keldi!', 36, 34, '#6a6580')):
        gl, w = glyphs(txt, size)
        for ch, shapes, gx, gy in gl:
            c.add('nt', [group(shapes + [fill(col)])], st([-CWd / 2 + 200 + gx, y + gy, 0]), parent=card, o=anim([(TM - 2, 100), (TM + 6, 0)]), op=TM + 7)
    rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    for n, (k, sx, sy) in enumerate(PET):
        t = TM + 18 + n * 2
        c.add('petal-' + k, [group([ell(D * .82), fill(COL[k])])], anim([(t, [0, 0, 0]), (t + 18, [sx * OFF * .82, sy * OFF * .82, 0])], 'back'),
              sc=anim([(t, [0, 0, 100]), (t + 18, [100, 100, 100])], 'back'), parent=rig, ip=t)
    c.add('cross', [group([path(cross_pts(K * .82)), fill('#ffffff')])], st([0, 0, 0]), parent=rig,
          sc=anim([(TM + 30, [0, 0, 100]), (TM + 46, [100, 100, 100])], 'back'), r=anim([(TM + 30, -90), (TM + 46, 0)], 'back'), ip=TM + 30)
    word(c, TM + 50)
    save(c, 'n8-notification')

# ------------------------------------------------------------------ 9. PARTICLES — scattered dots stream in and assemble the petals
def n9():
    c = Comp(W, H, 156); bg(c); rig = c.add('rig', null=True, p=st([CX, CY, 0])); rnd = random.Random(7)
    TA = 44
    for n, (k, sx, sy) in enumerate(PET):
        X, Y = sx * OFF, sy * OFF
        c.add('petal-' + k, [group([ell(D), fill(COL[k])])], st([X, Y, 0]), parent=rig, sc=anim([(TA - 18 + n * 2, [0, 0, 100], 'io'), (TA + 6 + n * 2, [100, 100, 100])], 'back'))
        for j in range(16):
            a = rnd.random() * 2 * math.pi; r = 500 + rnd.random() * 900
            x0, y0 = math.cos(a) * r, math.sin(a) * r * 1.3; t0 = rnd.randint(0, 10); t1 = TA - 16 + rnd.randint(0, 18) + n * 2
            s0 = 24 + rnd.random() * 30
            c.add(f'p{k}{j}', [group([ell(s0), fill(COL[k])])], anim([(0, [x0, y0, 0]), (t0, [x0, y0, 0], 'in'), (t1, [X, Y, 0])]), parent=rig,
                  sc=anim([(0, [0, 0, 100]), (t0 + 6, [100, 100, 100], 'in'), (t1, [40, 40, 100])], 'back'), op=t1 + 1)
    c.add('flash', [group([ell(anim([(TA + 6, [LOGO, LOGO]), (TA + 32, [LOGO * 2.6, LOGO * 2.6])], 'out')), stroke('#1d1430', anim([(TA + 6, 6), (TA + 32, 1)]), 12)])],
          st([CX, CY, 0]), o=anim([(TA + 6, 100), (TA + 32, 0)]), ip=TA + 6, op=TA + 33)
    cross_wipe(c, rig, TA + 10)
    word(c, TA + 34)
    save(c, 'n9-particles')

for f in (n1, n2, n3, n4, n5, n6, n7, n8, n9): f()
