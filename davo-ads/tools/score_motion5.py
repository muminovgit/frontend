# Davo Motion 5 "Bolalar" (18 s) — sound concept: TOY BOX.
# 96 BPM lullaby-pop: music-box melody, nylon/ukulele plucks, soft kick + hand claps, a baby rattle as the shaker;
# every alphabet block lands on a pitched wooden "knock" (B-O-L-A-L-A-R climb a major scale), soap bubbles pop,
# product cards arrive on a xylophone tick. No voice. usage: python3 tools/score_motion5.py [gain_db] -> WAV path
import subprocess, sys, numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]; gain = float(args[0]) if args else 0.0
T = dict(head=2.9, phone=6.1, bul=11.4, cta=15.2); DUR = 18.0
SR = 48000; N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(55)
def ts(d): return np.arange(int(d * SR)) / SR
def add(sig, t0, g=1.0, pan=0.0):
    i = int(round(t0 * SR)); j = min(N, i + len(sig))
    if j <= i or i >= N: return
    a = max(0, i); s = sig[a - i:j - i]; L[a:j] += s * g * (1 - pan); R[a:j] += s * g * (1 + pan)
def lp(x, a):
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y
def hp(x, a): return x - lp(x, a)
def nf(m): return 440 * 2 ** ((m - 69) / 12)
def noise(d): return rng.standard_normal(int(d * SR))
def musicbox(t0, m, g=.08, pan=0.0):
    x = ts(1.6); s = np.sin(2 * np.pi * nf(m) * x) + .5 * np.sin(2 * np.pi * nf(m) * 3.01 * x) * np.exp(-x * 6) + .2 * np.sin(2 * np.pi * nf(m) * 5.4 * x) * np.exp(-x * 12)
    add(s * np.exp(-x * 2.8) * np.minimum(1, x / .002) * g, t0, pan=pan)
def pluck(t0, m, g=.06, pan=0.0):                         # Karplus-Strong nylon pluck
    n = int(SR / nf(m)); buf = rng.uniform(-1, 1, n); out = np.zeros(int(.9 * SR))
    for i in range(len(out)): out[i] = buf[i % n]; buf[i % n] = .996 * .5 * (buf[i % n] + buf[(i + 1) % n])
    add(out * g, t0, pan=pan)
def knock(t0, m, g=.4, pan=0.0):                          # wooden block
    x = ts(.18); add((np.sin(2 * np.pi * nf(m) * x) * np.exp(-x * 38) + .5 * np.sin(2 * np.pi * nf(m) * 2.76 * x) * np.exp(-x * 60) + hp(noise(.18), .5) * np.exp(-x * 120) * .4) * g, t0, pan=pan)
    x2 = ts(.25); add(np.sin(2 * np.pi * np.cumsum(110 * np.exp(-x2 * 20) + 60) / SR) * np.exp(-x2 * 14) * g * .8, t0)
def rattle(t0, g=.06, pan=0.0):
    for k in range(7):
        x = ts(.01); add(np.sin(2 * np.pi * (3000 + rng.random() * 3000) * x) * np.exp(-x * 600) * g, t0 + rng.random() * .06, pan=pan)
def clap(t0, g=.18):
    for d in (0, .008, .017):
        x = ts(.12); add(hp(noise(.12), .35) * np.exp(-x * 40) * g, t0 + d, pan=.1)
def kick(t0, g=.45):
    x = ts(.3); add(np.sin(2 * np.pi * np.cumsum(120 * np.exp(-x * 25) + 50) / SR) * np.exp(-x * 10) * g, t0)
def bubble(t0, g=.12, pan=0.0):
    x = ts(.08); f = 600 + 2400 * (x / .08) ** .5; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 30) * g, t0, pan=pan)
def xylo(t0, m, g=.1, pan=0.0):
    x = ts(.5); add((np.sin(2 * np.pi * nf(m) * x) + .3 * np.sin(2 * np.pi * nf(m) * 4 * x) * np.exp(-x * 20)) * np.exp(-x * 9) * g, t0, pan=pan)
def swish(tp, d=.4, g=.12, pan=0.0):
    x = ts(d); a = np.linspace(.02, .3, len(x)); n = noise(d); y = np.empty_like(n); s = 0.0
    for i, v in enumerate(n): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * x / d) ** 2 * g * 2.4, tp - d * .6, pan=pan)
# ---- blocks: one wooden knock per landing, climbing C major; a music-box answer when the word completes
scale = [60, 62, 64, 65, 67, 69, 72]
for i in range(7): knock(.18 + i * .3 + .38, scale[i] + 12, .42, pan=(i - 3) * .12); rattle(.18 + i * .3 + .4, .04)
for i, m in enumerate([84, 88, 91, 96]): musicbox(2.45 + i * .1, m, .08, pan=(i % 2 - .5) * .5)
# ---- groove from the headline on: 96 BPM, kick / claps / rattle, nylon plucks + music-box melody
BPM = 96; beat = 60 / BPM; t0g = T["head"]
prog = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
melody = [76, 79, 81, 79, 76, 74, 72, 74, 76, 79, 84, 81, 79, 76, 77, 76]
k = 0
while t0g + k * beat / 2 < DUR - .5:
    tb = t0g + k * beat / 2; ch = prog[int((tb - t0g) // (4 * beat)) % 4]
    brk = (T["cta"] - .4 <= tb < T["cta"])
    if k % 4 == 0 and not brk: kick(tb, .45)
    if k % 4 == 2 and not brk: clap(tb, .16)
    rattle(tb + beat / 4, .035, pan=.4 if k % 2 else -.4)
    if k % 2 == 0: pluck(tb, ch[(k // 2) % 3] + 12, .05, pan=-.25)
    if k % 2 == 0 and tb > T["phone"] - .2: musicbox(tb, melody[(k // 2) % 16], .045, pan=.25)
    k += 1
x = ts(DUR - t0g); add(sum(np.sin(2 * np.pi * nf(m) * x) for m in [48, 55, 60]) / 3 * .04 * np.minimum(1, x / 1.5), t0g)
# ---- events
for i in range(16): bubble(1.2 + i * .22 + 3.0 + rng.random() * .6, .06, pan=rng.random() - .5)
swish(T["head"] + .1, .5, .12)
for i in range(3): xylo(T["head"] + i * .3, [72, 76, 79][i], .09)
swish(T["phone"] + .3, .7, .16, pan=.3)
for s in range(6): t0 = T["phone"] + 1.3 + s * .75 + .4; xylo(t0, [79, 81, 84, 86, 88, 91][s], .08, pan=.3); swish(t0 + .05, .3, .07, pan=-.3)
for i in range(3): t0 = T["bul"] + i * 1.25; knock(t0 + .05, [72, 76, 79][i], .3); xylo(t0 + .25, [84, 88, 91][i], .09)
for i, m in enumerate([72, 76, 79, 84, 88, 91]): musicbox(T["cta"] + .05 + i * .08, m, .08, pan=(i % 2 - .5) * .5)
kick(T["cta"], .6)
# ---- master
mix = np.stack([L, R], 1); fo = int(.5 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.15) / np.tanh(1.15) * .9
pre = os.path.join(ROOT, "audio/pre-motion5.wav"); out = os.path.join(ROOT, "audio/score-motion5.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), out], check=True)
os.remove(pre); print(out)
