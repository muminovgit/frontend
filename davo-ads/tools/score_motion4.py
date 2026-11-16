# Davo Motion 4 "Kosmetika" (18 s) — sound concept: SILK & GLOSS (slow luxury R&B).
# 84 BPM, warm electric-piano chords, finger snaps, soft sub, vinyl air; a serum-drop "plip" opens it, cosmetic
# cap clicks mark cuts, a perfume "psst" accents the add-to-bag, glossy shimmer sweeps on reveals. No voice.
# usage: python3 tools/score_motion4.py [gain_db]  -> prints WAV path
import subprocess, sys, numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]; gain = float(args[0]) if args else 0.0
T = dict(word=.85, head=2.4, phone=5.6, swap=8.6, add=10.3, bul=11.4, cta=15.2); DUR = 18.0
SR = 48000; N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(44)
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
def epiano(t0, notes, d=2.6, g=.08):                      # rhodes-ish: sine + bell partial with tremolo
    x = ts(d); env = np.minimum(1, x / .01) * np.exp(-x * 1.1); trem = 1 + .12 * np.sin(2 * np.pi * 4.5 * x)
    s = sum(np.sin(2 * np.pi * nf(m) * x) + .25 * np.sin(2 * np.pi * nf(m) * 7.02 * x) * np.exp(-x * 9) for m in notes) / len(notes)
    add(s * env * trem * g, t0, pan=-.15); add(s * env * trem * g * .8, t0 + .012, pan=.15)
def snap(t0, g=.3, pan=.25):
    x = ts(.12); add((hp(noise(.12), .55) * np.exp(-x * 55) + np.sin(2 * np.pi * 1750 * x) * np.exp(-x * 90) * .4) * g, t0, pan=pan)
def kick(t0, g=.6):
    x = ts(.4); add(np.sin(2 * np.pi * np.cumsum(90 * np.exp(-x * 18) + 44) / SR) * np.exp(-x * 7) * g, t0)
def shimmer(t0, d=1.2, g=.05, up=True):
    x = ts(d); f = (2000 + 4000 * (x / d)) if up else (6000 - 4000 * (x / d))
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / d) ** 2 * g, t0, pan=.3); add(hp(noise(d), .6) * np.sin(np.pi * x / d) ** 2 * g * .5, t0, pan=-.3)
def cap(t0, g=.35):                                       # cosmetic cap click
    x = ts(.05); add((np.sin(2 * np.pi * 2400 * x) * np.exp(-x * 160) + hp(noise(.05), .6) * np.exp(-x * 200) * .6) * g, t0)
def plip(t0, g=.35):                                      # serum drop into liquid
    x = ts(.25); f = 900 + 1600 * np.exp(-x * 25); add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 20) * g, t0)
def psst(t0, g=.22):                                      # perfume atomiser
    x = ts(.45); n = hp(noise(.45), .35); add(n * np.minimum(1, x / .01) * np.exp(-x * 7) * g, t0, pan=.2)
def silk(tp, d=.6, g=.15, pan=0.0):                       # soft fabric whoosh
    x = ts(d); a = np.linspace(.01, .22, len(x)); n = noise(d); y = np.empty_like(n); s = 0.0
    for i, v in enumerate(n): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * x / d) ** 2 * g * 2.6, tp - d * .55, pan=pan)
def bell(t0, m, g=.07, pan=0.0):
    x = ts(1.5); mod = np.sin(2 * np.pi * nf(m) * 2.0 * x) * 1.4 * np.exp(-x * 3); add(np.sin(2 * np.pi * nf(m) * x + mod) * np.exp(-x * 2.5) * g, t0, pan=pan)
# ---- bed
BPM = 84; beat = 60 / BPM; bar = 4 * beat
prog = [[62, 65, 69, 72, 76], [60, 64, 67, 71, 74], [58, 62, 65, 69, 72], [57, 60, 64, 67, 71]]   # Dm9 Cmaj9 Bbmaj9 Am9
x = ts(DUR); air = lp(noise(DUR), .02) * .015 + (rng.random(len(x)) < .0004) * rng.standard_normal(len(x)) * .08; add(air, 0)
for b in range(int(DUR / bar) + 1): epiano(.55 + b * bar, prog[b % 4], bar + .3, .085)
k = 0
while .55 + k * beat < DUR - .6:
    tb = .55 + k * beat
    if k % 4 == 0: kick(tb, .55)
    if k % 4 == 2: kick(tb + beat * .5, .35)
    if k % 2 == 1: snap(tb, .26, pan=.25 if k % 4 == 1 else -.25)
    x2 = ts(beat * .9); add(np.sin(2 * np.pi * nf(prog[int((tb - .55) // bar) % 4][0] - 24) * x2) * np.exp(-x2 * 2.2) * .16, tb)
    k += 1
# ---- events
plip(.55, .4); shimmer(.6, 1.4, .05)
for i in range(9): bell(T["word"] + i * .06, [74, 77, 81, 84, 86, 89, 93, 96, 98][i], .035, pan=(i % 3 - 1) * .4)
silk(T["head"] + .2, .7, .14)
for i in range(3): cap(T["head"] + i * .28 + .02, .25)
silk(T["phone"] + .25, .8, .18, pan=-.3); cap(T["phone"] + .5, .3)
cap(T["swap"] - .42, .35); silk(T["swap"] + .35, .7, .2, pan=.3)
cap(T["add"], .4); psst(T["add"] + .05, .24); bell(T["add"] + .15, 86, .09); bell(T["add"] + .22, 93, .07)
for i in range(3): t0 = T["bul"] + i * 1.25; silk(t0 + .2, .5, .12, pan=(i - 1) * .4); bell(t0 + .3, [81, 84, 88][i], .08); cap(t0 + .28, .22)
shimmer(T["cta"] - .9, 1.0, .06); kick(T["cta"], .7)
for i, m in enumerate([74, 77, 81, 84, 88]): bell(T["cta"] + .05 + i * .07, m, .07, pan=(i % 2 - .5) * .5)
shimmer(T["cta"] + 1.8, .9, .04, up=False)
# ---- master
mix = np.stack([L, R], 1); fo = int(.5 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.1) / np.tanh(1.1) * .9
pre = os.path.join(ROOT, "audio/pre-motion4.wav"); out = os.path.join(ROOT, "audio/score-motion4.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), out], check=True)
os.remove(pre); print(out)
