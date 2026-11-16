# Davo Motion 3 "BFQ va vitaminlar" (15 s) — sound concept: PILL-BOTTLE HOUSE.
# A 120 BPM house groove whose percussion is made from the product world: pill-bottle shakers (grain clusters),
# a capsule "snap" as the snare, effervescent-tablet fizz as risers, and a chord stab on every visual cut.
# No voice. usage: python3 tools/score_motion3.py [gain_db]  -> prints WAV path
import subprocess, sys, numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]; gain = float(args[0]) if args else 0.0
T = dict(words=1, shapes=3, phone=6, bul=9, logo=12); DUR = 15.0
SR = 48000; N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(33)
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
beat = .5
def kick(t0, g=.95):
    x = ts(.32); add(np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(160 * np.exp(-x * 32) + 46) / SR)) * np.exp(-x * 8) * g, t0)
def bottle(t0, g=.09, pan=0.0, d=.09):                    # pill-bottle shake: a cluster of tiny clicks
    for k in range(9):
        x = ts(.012); f = 3500 + rng.random() * 4500; add(np.sin(2 * np.pi * f * x) * np.exp(-x * 500) * g * (.5 + rng.random()), t0 + rng.random() * d, pan=pan)
    add(hp(noise(d), .5) * np.exp(-ts(d) * 30) * g * .5, t0, pan=pan)
def snap(t0, g=.5):                                       # capsule snapping open = snare
    x = ts(.25); add((hp(noise(.25), .3) * np.exp(-x * 22) * .7 + np.sin(2 * np.pi * 210 * x) * np.exp(-x * 30)) * g, t0)
    add(hp(noise(.03), .7) * np.exp(-ts(.03) * 200) * g * .8, t0)
def fizz(t0, t1, g=.18):                                  # effervescent tablet riser
    d = t1 - t0; x = ts(d); n = hp(noise(d), .45); grains = (rng.random(len(x)) < (.002 + .02 * (x / d) ** 2)).astype(float)
    add((n * .25 + lp(grains, .6) * 8) * (x / d) ** 1.6 * g, t0)
def stab(t0, notes, g=.2, d=.32):
    x = ts(d); s = sum((2 * ((nf(m) * x) % 1) - 1) + (2 * ((nf(m) * 1.007 * x) % 1) - 1) for m in notes) / (2 * len(notes))
    add(lp(s, .35) * np.exp(-x * 7) * np.minimum(1, x / .004) * g, t0)
def pluck(t0, m, g=.07, pan=0.0):
    x = ts(.2); add(lp((2 * ((nf(m) * x) % 1) - 1) * np.exp(-x * 16), .3) * g, t0, pan=pan)
def subhit(t0, g=.9):
    x = ts(1.4); add(np.sin(2 * np.pi * np.cumsum(60 * np.exp(-x * 3) + 34) / SR) * np.exp(-x * 2.6) * g, t0)
def whoosh(tp, d=.3, g=.2, pan=0.0):
    x = ts(d); a = np.linspace(.03, .5, len(x)); n = noise(d); y = np.empty_like(n); s = 0.0
    for i, v in enumerate(n): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * x / d) ** 2 * g * 2.4, tp - d * .6, pan=pan)
def tick(t0, g=.12):
    x = ts(.02); add(hp(noise(.02), .6) * np.exp(-x * 260) * g, t0)
CH = {"Fm": [53, 56, 60, 63], "Db": [49, 53, 56, 60], "Ab": [56, 60, 63, 67], "Eb": [51, 55, 58, 63]}
prog = ["Fm", "Db", "Ab", "Eb"]
# ---------------- hook (0–1): capsule slam + burst, then the beat drops on 1.0
subhit(.0, .8); whoosh(.22, .22, .3); snap(.42, .8)
for i in range(30): tick(.44 + rng.random() * .5, .06 + rng.random() * .08)
fizz(.45, 1.0, .2)
# ---------------- groove (1–15) with breaks
for k in range(int((DUR - 1) / (beat / 2))):
    tb = 1 + k * beat / 2
    if tb >= DUR - .35: break
    bar = int((tb - 1) // 2); ch = CH[prog[bar % 4]]
    brk = (T["phone"] - .5 <= tb < T["phone"]) or (T["logo"] - .5 <= tb < T["logo"])
    if k % 2 == 0 and not brk: kick(tb)
    if k % 4 == 2 and not brk: snap(tb, .38)
    bottle(tb + beat / 4, .07, pan=.4 if k % 2 else -.4)
    if not brk: x = ts(.22); add(np.tanh(2.5 * np.sin(2 * np.pi * nf(ch[0] - 24) * x)) * np.exp(-x * 10) * .2, tb + beat / 4)
x = ts(DUR - 1); pad = sum(np.sin(2 * np.pi * nf(m + 12) * x) for m in CH["Fm"]) / 4; add(lp(pad, .03) * .05 * np.minimum(1, x / 1), 1)
# ---------------- cut stabs: word beats, bullets, section cuts
for i, t0 in enumerate([1, 1.5, 2, 2.5]): stab(t0, [m + 12 for m in CH[prog[i]]], .24); whoosh(t0 + .05, .2, .2, pan=(i % 2 - .5) * .6)
for t0 in (T["shapes"], T["phone"], T["bul"], T["bul"] + 1, T["bul"] + 2): stab(t0, [m + 12 for m in CH["Ab"]], .22); whoosh(t0 + .05, .3, .24)
# ---------------- shape play: rising arpeggio swirl while the field folds into the helix
for i in range(24):
    t0 = T["shapes"] + .2 + i * .115; m = [65, 68, 72, 75, 77, 80][i % 6] + (12 if i > 15 else 0); pluck(t0, m, .06, pan=np.sin(i * .9) * .6)
fizz(T["phone"] - .9, T["phone"], .16)
# ---------------- phone: UI taps
for i in range(6): tick(T["phone"] + .45 + i * .2, .14); pluck(T["phone"] + .45 + i * .2, 84 + i, .04)
whoosh(T["phone"] + 1.9, .5, .12)
# ---------------- bullets: capsule snap + check pluck on each
for i in range(3): snap(T["bul"] + i + .02, .45); pluck(T["bul"] + i + .25, 84 + [0, 3, 7][i], .1)
# ---------------- logo: petals converge (reverse swell) -> big chord -> clean tail
x = ts(.95); add(hp(noise(.95), .3) * (x / .95) ** 3 * .25, T["logo"])
subhit(T["logo"] + .95, 1.0); stab(T["logo"] + .95, [53, 60, 65, 68, 72, 77], .3, 1.4)
for i, m in enumerate([77, 80, 84, 89]): pluck(T["logo"] + 1.3 + i * .06, m, .08, pan=(i % 2 - .5) * .5)
# ---------------- master
mix = np.stack([L, R], 1); fo = int(.35 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * .9
pre = os.path.join(ROOT, "audio/pre-motion3.wav"); out = os.path.join(ROOT, "audio/score-motion3.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), out], check=True)
os.remove(pre); print(out)
