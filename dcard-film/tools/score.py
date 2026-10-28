# Generated score + SFX for the Dcard film. Everything is synthesised here (no samples) -> no licence.
# Timing comes from film/cues.js (same file the picture uses) and film/assets/audio/hits.json (physics bounces).
# Output: film/assets/audio/score.wav (48 kHz stereo), loudness-normalised so the AAC master lands at -14 LUFS / -2 dBTP.
import json, subprocess, sys, numpy as np, wave, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILM = os.path.join(ROOT, "film")
C = json.loads(subprocess.run(["node", "-e", "const vm=require('vm');const ctx={};vm.runInNewContext(require('fs').readFileSync('film/cues.js','utf8'),ctx);console.log(JSON.stringify(ctx.CUES))"], cwd=ROOT, capture_output=True, text=True, check=True).stdout)
HITS = [h for h in json.load(open(os.path.join(FILM, "assets/audio/hits.json"))) if h[2] > 380]
SR = 48000; DUR = C["dur"]; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)

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

# ---------------------------------------------------------------- music (120 BPM, sections)
BPM = 120; beat = 60 / BPM
prog = [[45, 52, 57, 60], [41, 48, 53, 57], [48, 55, 60, 64], [43, 50, 55, 62]]   # Am F C G
# pads + bass run through; drums run only inside these windows (they restart on the slam)
drum_windows = [(0.0, C["launch"]), (C["chegLand"], C["dark"]), (C["qrType"][0], C["logoDrop"]), (C["logoLand"], DUR - 0.6)]
for b in range(int(DUR / (4 * beat)) + 1):
    ch = prog[b % 4]; t0 = b * 4 * beat; t = ts(4 * beat + 0.3)
    env = np.minimum(1, t / 0.08) * np.exp(-t * 0.35)
    pad = sum(np.sign(np.sin(2 * np.pi * nf(m + 12) * t)) * 0.25 + np.sin(2 * np.pi * nf(m + 12) * 1.005 * t) for m in ch) / len(ch)
    add(lp(pad * env, 0.08) * 0.10, t0)
    for k in range(8):   # off-beat bass
        tb = t0 + k * beat / 2 + beat / 4; tt = ts(0.2)
        add(np.tanh(3 * np.sin(2 * np.pi * nf(ch[0] - 12) * tt)) * np.exp(-tt * 14) * 0.16, tb)
def in_drums(t): return any(a <= t < b - 1e-6 for a, b in drum_windows)
def kick(t0, g=0.8):
    t = ts(0.35); f = 140 * np.exp(-t * 28) + 46; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * g, t0)
def clap(t0, g=0.35):
    t = ts(0.22); x = hp(rng.standard_normal(len(t)), 0.25); env = np.exp(-t * 26) * (1 + 0.6 * np.exp(-((t - 0.012) ** 2) / 2e-5)); add(x * env * g, t0)
def hat(t0, g=0.08, pan=0.25):
    t = ts(0.05); add(hp(rng.standard_normal(len(t)), 0.6) * np.exp(-t * 90) * g, t0, pan=pan)
def crash(t0, g=0.25):
    t = ts(1.4); add(hp(rng.standard_normal(len(t)), 0.35) * np.exp(-t * 3.2) * g, t0)
for a, b in drum_windows:
    k = 0
    while a + k * beat / 2 < b - 1e-6:
        t = a + k * beat / 2
        if k % 2 == 0: kick(t)
        if k % 4 == 2: clap(t)
        hat(t + beat / 4)
        k += 1
    if a > 0: crash(a, 0.3)      # the slam back
# risers into each slam (drums are out)
for a, b in [(C["launch"], C["chegLand"]), (C["dark"], C["qrType"][0]), (C["logoDrop"], C["logoLand"])]:
    t = ts(b - a); x = hp(rng.standard_normal(len(t)), 0.2); add(x * (t / (b - a)) ** 2 * 0.12, a)

# ---------------------------------------------------------------- SFX
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

# type slams (every Anton landing)
for t in C["s1Land"] + [C["oneL"], C["oneR"], C["chegLand"]] + C["qrType"] + C["coinType"] + C["verbs"]: thud(t)
# pops
pop(C["plus"], 900); pop(C["coinPop"], 1100, 0.3); pop(C["lock"] - 0.08, 1300, 0.3); pop(C["footer"], 800, 0.22)
for i, v in enumerate(C["verbs"]): pop(v + 0.06, 1500, 0.12, pan=-0.3)            # handwritten numbers
# pen scribbles for every note write-on (windows match index.html) and marker strokes (brighter)
for a, b in [(1.0, 1.58), (2.55, 3.35), (4.66, 5.16), (6.3, 6.72), (7.85, 8.45), (8.78, 9.4), (13.2, 14.15)]: scribble(a, b, 0.11, 0.3)
for a, b in [(1.02, 1.28), (2.42, 2.9), (4.6, 4.9), (6.62, 6.9), (11.42, 11.74)]: scribble(a, b, 0.09, 0.6, pan=0.2)
for v in C["verbs"]: scribble(v + 0.04, v + 0.24, 0.07, 0.3, pan=-0.3)
# whooshes: exits, launch, phone, reel steps, wordmark wipe
for t in [C["s1Exit"] + 0.15, C["s2Exit"] + 0.15, C["s4Exit"] + 0.15, C["s7Exit"] + 0.15]: whoosh(t, 0.4, 0.2)
whoosh(C["launch"] + 0.08, 0.3, 0.26, pan=0.2); whoosh(C["phoneIn"] + 0.2, 0.45, 0.22)
for t in C["reel"]: whoosh(t + 0.06, 0.18, 0.16); pop(t + 0.1, 500, 0.1)
whoosh(C["wordWipe"] + 0.15, 0.3, 0.16, pan=0.3)
# coin bounces from the physics
for kind, t, v in HITS: clink(t, v, pan=(0.25 if kind == "rain" else 0.1) * (1 if int(t * 100) % 2 else -1))
# logo: the coin lands and becomes the mark
clink(C["logoLand"], 3000); subhit(C["logoLand"])

# ---------------------------------------------------------------- master
mix = np.stack([L, R], 1)
fo = int(0.5 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * 0.9
pre = os.path.join(FILM, "assets/audio/premaster.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
# mastering: measured static gain to the loudness target, then a 4x-oversampled peak limiter
# (AAC adds inter-sample overshoot, so the limiter leaves headroom for <= -2 dBTP after encode).
# tools/master.py iterates the gain against the encoded AAC until it reads -14 LUFS.
gain = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.56:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), os.path.join(FILM, "assets/audio/score.wav")], check=True)
os.remove(pre)
print("score.wav written; sfx hits:", len(HITS))
