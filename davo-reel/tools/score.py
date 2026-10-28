# Davo Delivery reel — generated score + SFX (no samples, no licence needed). Timing mirrors reel.html's T table.
import json, subprocess, sys, numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000; DUR = 15.0; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(21)
T = dict(s1=0, s2=1.85, s3=3.7, s4=5.5, s5=7.3, s6=9.9, s7=11.7, s8=13.1)
def ts(d): return np.arange(int(d * SR)) / SR
def add(sig, t0, g=1.0, pan=0.0):
    i = int(round(t0 * SR)); j = min(N, i + len(sig))
    if j <= i or i >= N: return
    a = max(0, i); s = sig[a - i:j - i]
    L[a:j] += s * g * (1 - pan) ; R[a:j] += s * g * (1 + pan)
def lp(x, a):
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y
def hp(x, a): return x - lp(x, a)
def nf(m): return 440 * 2 ** ((m - 69) / 12)


BPM = 120; beat = 60 / BPM
prog = [[45, 52, 57, 60], [41, 48, 53, 57], [48, 55, 60, 64], [43, 50, 55, 62]]
for bb in range(int(DUR / (4 * beat)) + 1):
    ch = prog[bb % 4]; t0 = bb * 4 * beat; t = ts(4 * beat + 0.3)
    env = np.minimum(1, t / 0.08) * np.exp(-t * 0.35)
    pad = sum(np.sin(2 * np.pi * nf(m + 12) * t) + 0.5 * np.sin(2 * np.pi * nf(m + 24) * 1.003 * t) for m in ch) / len(ch)
    add(lp(pad * env, 0.1) * 0.09, t0)
    for k in range(8):
        tb = t0 + k * beat / 2 + beat / 4; tt = ts(0.2)
        add(np.tanh(3 * np.sin(2 * np.pi * nf(ch[0] - 12) * tt)) * np.exp(-tt * 14) * 0.15, tb)
def kick(t0, g=0.8):
    t = ts(0.35); f = 140 * np.exp(-t * 28) + 46; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * g, t0)
def clap(t0, g=0.35):
    t = ts(0.22); x = hp(rng.standard_normal(len(t)), 0.25); env = np.exp(-t * 26) * (1 + 0.6 * np.exp(-((t - 0.012) ** 2) / 2e-5)); add(x * env * g, t0)
def hat(t0, g=0.08, pan=0.25):
    t = ts(0.05); add(hp(rng.standard_normal(len(t)), 0.6) * np.exp(-t * 90) * g, t0, pan=pan)
def crash(t0, g=0.25):
    t = ts(1.4); add(hp(rng.standard_normal(len(t)), 0.35) * np.exp(-t * 3.2) * g, t0)

# drums: in on the cross stamp, out while the camera pushes into it, slam back on each new scene beat
drum_windows = [(0.72, 1.22), (T["s2"], T["s5"]), (7.45, T["s8"]), (13.52, DUR - 0.5)]
for a, b in drum_windows:
    k = 0
    while a + k * beat / 2 < b - 1e-6:
        t = a + k * beat / 2
        if k % 2 == 0: kick(t)
        if k % 4 == 2: clap(t)
        hat(t + beat / 4)
        k += 1
    crash(a, 0.28)
for a, b in [(1.22, T["s2"]), (T["s5"], 7.45), (T["s8"], 13.52)]:
    t = ts(b - a); x = hp(rng.standard_normal(len(t)), 0.2); add(x * (t / (b - a)) ** 2 * 0.12, a)
def thud(t0, g=0.7):   # type slam: low body + paper slap
    t = ts(0.3); f = 90 * np.exp(-t * 18) + 50; body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    slap = lp(rng.standard_normal(len(t)), 0.35) * np.exp(-t * 60)
    add((body + slap * 0.6) * g, t0)
def pop(t0, f0=700, g=0.35, pan=0.0):
    t = ts(0.12); f = f0 * (1 + 1.6 * np.exp(-t * 60)); add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38) * g, t0, pan=pan)
def clink(t0, v, pan=0.0):   # coin on hard surface: inharmonic partials, level from impact speed
    t = ts(0.5); g = min(0.32, 0.06 + v / 14000)
    x = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(2400, 1), (3890, 0.6), (5210, 0.45), (7330, 0.25)]) * np.exp(-t * 16)
    add(x * g / 2.2, t0, pan=pan); add(lp(rng.standard_normal(len(ts(0.03))), 0.4) * g * 0.6, t0, pan=pan)
def scribble(t0, t1, g=0.12, bright=0.35, pan=0.0):   # pen / marker on paper: band-limited noise with stroke rhythm
    d = max(0.05, t1 - t0); t = ts(d); x = hp(lp(rng.standard_normal(len(t)), bright), 0.08)
    am = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * (7 + 3 * np.sin(t * 5)) * t)); env = np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.04)
    add(x * am * env * g, t0, pan=pan)
def whoosh(t0, d=0.35, g=0.22, pan=0.0):   # peaks at t0
    t = ts(d); a = np.linspace(0.02, 0.4, len(t)); x = rng.standard_normal(len(t)); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * t / d) ** 2 * g * 2.4, t0 - d * 0.65, pan=pan)
def subhit(t0):
    t = ts(2.2); f = 62 * np.exp(-t * 2.5) + 34; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.0) * 0.95, t0)
    add(lp(rng.standard_normal(len(ts(0.6))), 0.1) * np.exp(-ts(0.6) * 7) * 0.4, t0)


def tick(t0, g=0.08, pan=0.0):
    t = ts(0.03); add(hp(rng.standard_normal(len(t)), 0.5) * np.exp(-t * 160) * g, t0, pan=pan)
def plastic(t0, g=0.3):   # capsule into a plastic compartment
    t = ts(0.25); x = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(1800, 1), (2950, .5), (4400, .3)]) * np.exp(-t * 30)
    add(x * g / 1.8, t0); add(lp(rng.standard_normal(len(ts(0.04))), 0.5) * g * 0.5, t0)
def chime(t0, g=0.3):
    for m, dl in ((84, 0), (91, 0.11)):
        t = ts(1.0); add((np.sin(2 * np.pi * nf(m) * t) + 0.3 * np.sin(2 * np.pi * nf(m) * 2.01 * t)) * np.exp(-t * 5) * g, t0 + dl)

# S1 logo build
for i, a in enumerate([.18, .3, .42, .54]): pop(a + 0.06, 600 + i * 140, 0.28, pan=[-.3, .3, -.3, .3][i])
thud(0.74, 0.7); pop(0.76, 1300, 0.2); whoosh(1.83, 0.6, 0.3)
# S2 search
whoosh(T["s2"] + 0.2, 0.25, 0.1); pop(T["s2"] + 0.2, 700, 0.22)
for k in range(12): tick(T["s2"] + 0.37 + k * 0.042, 0.07, pan=0.2)
for i in range(2): thud(T["s2"] + 1.12 + i * 0.12, 0.35)
pop(T["s2"] + 1.33, 1500, 0.15); whoosh(T["s3"] - 0.02, 0.35, 0.25)
# S3 map
scribble(T["s3"] + 0.05, T["s3"] + 0.5, 0.06, 0.5)
for i in range(6): pop(T["s3"] + 0.3 + i * 0.07 + 0.18, 500 + i * 60, 0.2, pan=((i % 3) - 1) * 0.4)
for i in range(3): pop(T["s3"] + 0.9 + i * 0.14, 1700, 0.13, pan=0.3)
whoosh(T["s4"] - 0.02, 0.36, 0.25)
# S4 delivery
pop(T["s4"] + 0.15, 800, 0.2); pop(T["s4"] + 0.25, 650, 0.2)
whoosh(T["s4"] + 1.4, 1.0, 0.1, pan=0.3)
for i, a in enumerate([.2, .55, .9, 1.55]): pop(T["s4"] + a + 0.02, 900 + i * 220, 0.18)
thud(T["s4"] + 1.5, 0.35)
# S5 the new pill reminder
thud(T["s5"] + 0.16, 0.8); pop(T["s5"] + 0.2, 1100, 0.25)
chime(T["s5"] + 0.62, 0.28)
whoosh(T["s5"] + 0.75, 0.3, 0.12)
for i in range(3): plastic(T["s5"] + 1.05 + i * 0.42 + 0.26, 0.35); pop(T["s5"] + 1.05 + i * 0.42 + 0.33, 1400 + i * 200, 0.15)
whoosh(T["s6"] - 0.02, 0.36, 0.25)
# S6 carousel steps
for a in [.25, .6, .95, 1.3]: whoosh(T["s6"] + a + 0.15, 0.22, 0.12); tick(T["s6"] + a + 0.28, 0.1)
# S7 four steps
for i in range(4): thud(T["s7"] + 0.32 + i * 0.2, 0.45); pop(T["s7"] + 0.33 + i * 0.2, 700 + i * 180, 0.14)
# S8 outro
for i in range(4): pop(T["s8"] + 0.14 + i * 0.06, 600 + i * 140, 0.24, pan=[-.3, .3, -.3, .3][i])
thud(13.52, 0.8); subhit(13.52); whoosh(T["s8"] + 0.75, 0.3, 0.14, pan=0.3)
for i in range(2): pop(T["s8"] + 1.3 + i * 0.1, 900 + i * 200, 0.2)

mix = np.stack([L, R], 1); fo = int(0.45 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * 0.9
pre = os.path.join(ROOT, "audio/premaster.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
gain = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), os.path.join(ROOT, "audio/score.wav")], check=True)
os.remove(pre); print("score.wav written")
