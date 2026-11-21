# Prototypes for the dev team's splash proposal: everything is built only from the logo (4 circles + white cross),
# white background, logo centred, no wordmark. 1080x2340, 60 fps.
#   p1-bloom    ⭐ intro (cross alone -> petals open behind it, 60 ms apart, small overshoot) ~700 ms
#                 + loop (petals orbit the cross while the app is still loading; seamless, 3 s per turn)
#                 + outro (cross grows to fill the screen = home's white background) 350 ms
#               Lottie markers: "intro", "loop", "outro" -> playSegments / controller.animateTo
#   p2-pulse    the cross beats once, the circles ripple out as waves
#   p3-route    a line draws across the screen; its end dot opens into the logo
#   p4-capsule  a capsule cracks open, the four circles come out
#   p5-minimal  soft fade + scale 0.95 -> 1
# usage: python3 build_splash_proposal.py
import json, os
from splash_lib import *
import build_splash_styles as S

W, H = 1080, 2340
CX, CY = W / 2, H / 2
LOGO = 330; K = LOGO / 131; D = 57 * K; OFF = 20 * K
CYAN = '#09bbd4'                     # brand primary — the native splash shows the cross in this colour on white
PET = [('y', -1, -1), ('pk', 1, -1), ('g', 1, 1), ('vi', -1, 1)]
def bg(c): c.add('bg', [group([rect(W * 3, H * 3), fill('#ffffff')])], st([W / 2, H / 2, 0]))
def save(c, name, markers=None):
    d = c.doc('Davo splash ' + name)
    if markers: d['markers'] = [{'tm': a, 'cm': n, 'dr': b - a} for n, a, b in markers]
    out = os.path.join(HERE, f'davo-splash-{name}.json'); json.dump(d, open(out, 'w'), separators=(',', ':'))
    print(name, os.path.getsize(out) // 1024, 'KB', d['op'], 'frames')
def cross_layer(c, parent=None, **kw):
    """white cross; starts in brand cyan (visible on white) and whitens as the petals arrive behind it"""
    col = kw.pop('col', None) or {'a': 1, 'k': [{'t': kw.pop('w0'), 's': rgb(CYAN), 'o': {'x': [.4], 'y': [0]}, 'i': {'x': [.2], 'y': [1]}},
                                               {'t': kw.pop('w1'), 's': rgb('#ffffff')}]}
    return c.add('cross', [group([path(cross_pts(K)), {'ty': 'fl', 'c': col, 'o': st(100), 'r': 1}])], parent=parent, **kw)

# ------------------------------------------------------------------ 1. BLOOM: intro + loop + outro
def p1():
    I1, L1, O1 = 42, 222, 243                       # intro end, loop end (3 s turn), outro end (350 ms)
    c = Comp(W, H, O1); bg(c)
    spin = c.add('petals', null=True, p=st([CX, CY, 0]), r=anim([(I1, 0, 'lin'), (L1, 360)], 'lin'),
                 sc=anim([(L1, [100, 100, 100], 'in'), (O1, [80, 80, 100])], 'in'))
    for n, (k, sx, sy) in enumerate(PET):            # sariq -> pushti -> yashil -> binafsha, 60 ms (≈4 frames) apart
        t = 4 + n * 4
        c.add('petal-' + k, [group([ell(D), fill(COL[k])])], anim([(t, [0, 0, 0]), (t + 24, [sx * OFF, sy * OFF, 0])], 'back'),
              sc=anim([(t, [25, 25, 100]), (t + 24, [100, 100, 100])], 'back'), parent=spin)
    # cross: on screen from frame 0 (matches the native splash), whitens, then grows to swallow the screen on exit
    cross_layer(c, p=st([CX, CY, 0]), w0=6, w1=26, sc=anim([(0, [100, 100, 100]), (10, [100, 100, 100], 'out'), (16, [94, 94, 100], 'back'),
                                                              (34, [100, 100, 100]), (L1, [100, 100, 100], 'in'), (O1, [6500, 6500, 100])]))
    save(c, 'p1-bloom', [('intro', 0, I1), ('loop', I1, L1), ('outro', L1, O1)])

# ------------------------------------------------------------------ 2. PULSE
def p2():
    TB = 14; c = Comp(W, H, 100); bg(c)
    for n, (k, sx, sy) in enumerate(PET):
        t = TB + 2 + n * 2
        c.add('wave-' + k, [group([ell(anim([(t, [D, D]), (t + 34, [D * 4.2, D * 4.2])], 'out')), stroke(COL[k], anim([(t, 18), (t + 34, 2)], 'out'))])],
              st([CX + sx * OFF, CY + sy * OFF, 0]), o=anim([(t, 85), (t + 34, 0)], 'out'), ip=t, op=t + 35)
    rig = c.add('rig', null=True, p=st([CX, CY, 0]))
    for n, (k, sx, sy) in enumerate(PET):
        t = TB + 2 + n * 2
        c.add('petal-' + k, [group([ell(D), fill(COL[k])])], anim([(t, [0, 0, 0]), (t + 22, [sx * OFF, sy * OFF, 0])], 'back'),
              sc=anim([(t, [0, 0, 100]), (t + 22, [100, 100, 100])], 'back'), parent=rig, ip=t)
    # the beat: anticipation (shrink) -> thump (125%) -> settle; waves leave on the thump frame
    cross_layer(c, p=st([CX, CY, 0]), w0=TB + 2, w1=TB + 14, sc=anim([(0, [100, 100, 100]), (TB - 6, [100, 100, 100], 'io'), (TB, [90, 90, 100], 'out'),
                                                                    (TB + 6, [125, 125, 100], 'io'), (TB + 18, [96, 96, 100], 'io'), (TB + 28, [100, 100, 100])]))
    save(c, 'p2-pulse')

# ------------------------------------------------------------------ 3/4 reuse the full-screen styles, cleaned to the brief
def p3():
    S.CY = CY; c_ = S.route.__wrapped__ if hasattr(S.route, '__wrapped__') else S.route
    c_('p3-route', back='#ffffff', street='#ffffff', line=CYAN, dash='#ffffff', courier=COL['pk'], text=False)
def p4():
    S.CY = CY
    S.capsule('p4-capsule', back='#ffffff', glow=('#ffffff', '#ffffff'), ink=COL['ink'], spark=COL['vi'], text=False)

# ------------------------------------------------------------------ 5. MINIMAL
def p5():
    c = Comp(W, H, 60); bg(c)
    rig = c.add('rig', null=True, p=st([CX, CY, 0]), sc=anim([(0, [95, 95, 100]), (36, [100, 100, 100])], 'out'))
    for k, sx, sy in PET:
        c.add('petal-' + k, [group([ell(D), fill(COL[k])])], st([sx * OFF, sy * OFF, 0]), parent=rig, o=anim([(0, 0), (24, 100)], 'out'))
    c.add('cross', [group([path(cross_pts(K)), fill('#ffffff')])], parent=rig)
    save(c, 'p5-minimal')

for f in (p1, p2, p3, p4, p5): f()
