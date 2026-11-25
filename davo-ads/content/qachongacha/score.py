# Music bed + SFX for the "Qachongacha?" reel, timed from timeline.js. Voice is mixed separately (ducking in ffmpeg).
# usage: python3 score.py -> music_sfx.wav
import json, os, numpy as np, wave
HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.loads(open(os.path.join(HERE, 'timeline.js')).read()[len('window.TL='):-1])
SR = 48000; DUR = TL['dur']; N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(9)
segs = {s['kind']: s for s in TL['segs']}
def wt(k, seg):
    for w in TL['words']:
        if w['seg'] == seg and w['w'].lower().replace("'", "").startswith(k): return w['s']
    return 0
def ts(d): return np.arange(int(d * SR)) / SR
def add(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if j <= i: return
    s = sig[:j - i]; L[i:j] += s * g * (1 - pan); R[i:j] += s * g * (1 + pan)
def lp(x, a):
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y
def nf(m): return 440 * 2 ** ((m - 69) / 12)
def noise(d): return rng.standard_normal(int(d * SR))
def whoosh(tp, d=.35, g=.25, up=True):
    x = ts(d); a = np.linspace(.02, .35, len(x)) if up else np.linspace(.35, .02, len(x)); n = noise(d); y = np.empty_like(n); s = 0.0
    for i, v in enumerate(n): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * x / d) ** 2 * g * 2.5, tp - d * .7)
def pop(t0, g=.3, f=900):
    x = ts(.12); add(np.sin(2 * np.pi * np.cumsum(f * np.exp(-x * 30) + 300) / SR) * np.exp(-x * 30) * g, t0)
def boom(t0, g=.9):
    x = ts(1.2); add(np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x * 4) + 38) / SR) * np.exp(-x * 3) * g, t0)
    add(lp(noise(.3), .2) * np.exp(-ts(.3) * 12) * g * .6, t0)
def tick(t0, g=.08):
    x = ts(.02); add((noise(.02) - lp(noise(.02), .6)) * np.exp(-x * 260) * g, t0)
def bell(t0, m, g=.1, pan=0):
    x = ts(1.4); mod = np.sin(2 * np.pi * nf(m) * 2 * x) * 1.2 * np.exp(-x * 3); add(np.sin(2 * np.pi * nf(m) * x + mod) * np.exp(-x * 2.6) * g, t0, pan=pan)
def pluck(t0, m, g=.05, pan=0):
    x = ts(.5); add(lp((2 * ((nf(m) * x) % 1) - 1) * np.exp(-x * 8), .25) * g, t0, pan=pan)
# ---- bed: 100 BPM soft kick + shaker + minor-ish plucks, enters after the hook impact
BPM = 100; beat = 60 / BPM; start = wt('qachongacha', 0)
prog = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]]
k = 0
while start + k * beat / 2 < DUR - .8:
    tb = start + k * beat / 2; ch = prog[int((tb - start) // (4 * beat)) % 4]
    if k % 2 == 0: x = ts(.25); add(np.sin(2 * np.pi * np.cumsum(110 * np.exp(-x * 25) + 48) / SR) * np.exp(-x * 9) * .35, tb)
    x = ts(.05); add((noise(.05) - lp(noise(.05), .5)) * np.exp(-x * 70) * .05, tb + beat / 4, pan=.3 if k % 2 else -.3)
    pluck(tb, ch[k % 3] + 12, .045, pan=(k % 3 - 1) * .3)
    k += 1
x = ts(DUR - start); add(sum(np.sin(2 * np.pi * nf(m) * x) for m in (45, 52, 57)) / 3 * .05 * np.minimum(1, x / 2), start)
# hook: tension riser into the impact
q = wt('qachongacha', 0); x = ts(q); add(lp(noise(q), .08) * (x / q) ** 2 * .12, 0); boom(q, .8); whoosh(q, .3, .2)
for k2 in ('dorixonama', 'sarson', 'bolaverasizmi'): pop(wt(k2, 0) + .35, .18, 1400)
# segment cuts
for s in TL['segs'][1:]: whoosh(s['t0'], .3, .16)
bell(segs['brand']['t0'] + .1, 84, .1); bell(segs['brand']['t0'] + .2, 88, .08)
pop(wt('sink', 2), .25); pop(wt('biotin', 2), .25, 1100)
pop(wt('havola', 3), .22); pop(wt('uyingizgacha', 3), .22, 1100)
for i in range(30): tick(segs['count']['t0'] + .1 + i * .04)
bell(wt('200', 5), 91, .1)
pop(wt('uyingizgacha', 6), .28); pop(wt('ikkinchi', 6), .28, 1200)
c = segs['cta']['t0']; whoosh(c, .5, .25)
for i, m in enumerate((76, 79, 84, 88)): bell(c + .2 + i * .08, m, .08, pan=(i % 2 - .5) * .4)
mix = np.stack([L, R], 1); fo = int(.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = mix / np.abs(mix).max() * .8
with wave.open(os.path.join(HERE, 'music_sfx.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', DUR)
