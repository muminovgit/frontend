# Davo Delivery motion ads — generated music + SFX + Uzbek VO (numpy synthesis, no samples).
# usage: python3 tools/score.py <variant 01|08|02> [gain_db] [--no-vo]   -> prints the WAV path (master.py contract)
import subprocess, sys, numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
vid = args[0]; gain = float(args[1]) if len(args) > 1 else 0.0
# timelines mirror window.VARIANT.T in ad-XX.html
V = {"01": dict(words=7, step=.075, demo=1.9, bul=4.7, cta=6.3, dur=8.6, kind="price", win=3.65),
     "08": dict(words=7, step=.075, demo=2.0, bul=5.6, cta=7.2, dur=9.5, kind="deliver", tmap=3.3),
     "02": dict(words=12, step=.06, demo=2.0, bul=6.1, cta=7.6, dur=9.9, kind="search")}[vid]
SR = 48000; DUR = V["dur"]; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(int(vid))
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

# ---------------- music: 124 BPM bright pop (C–G–Am–F), beat enters with the hook
BPM = 124; beat = 60 / BPM; bar = 4 * beat
prog = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]
for b in range(int(DUR / bar) + 1):
    ch = prog[b % 4]; t0 = b * bar; t = ts(bar + .3); env = np.minimum(1, t / .05) * np.exp(-t * .5)
    pad = sum(np.sin(2 * np.pi * nf(m) * t) + .4 * np.sign(np.sin(2 * np.pi * nf(m) * 1.003 * t)) for m in ch) / len(ch)
    add(lp(pad * env, .09) * .08, t0)
    for k in range(8):
        tt = ts(.2); add(np.tanh(3 * np.sin(2 * np.pi * nf(ch[0] - 24) * tt)) * np.exp(-tt * 13) * .16, t0 + k * beat / 2 + beat / 4)
    for k in range(16):
        tt = ts(.16); m = ch[[0, 2, 1, 3][k % 4]] + 12; x = (2 * ((nf(m) * tt) % 1) - 1) * np.exp(-tt * 18); add(lp(x, .3) * .05, t0 + k * beat / 4, pan=.3 if k % 2 else -.3)
def kick(t0, g=.8):
    t = ts(.3); f = 150 * np.exp(-t * 30) + 48; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * g, t0)
def clap(t0, g=.32):
    t = ts(.2); add(hp(noise(.2), .3) * np.exp(-t * 26) * g, t0)
def hat(t0, g=.06, pan=.3):
    t = ts(.04); add(hp(noise(.04), .7) * np.exp(-t * 100) * g, t0, pan=pan)
k = 0
while k * beat / 2 < DUR - .5:
    tb = k * beat / 2
    if not (V["bul"] - .25 < tb < V["bul"]) and not (V["cta"] - .25 < tb < V["cta"]):
        if k % 2 == 0: kick(tb)
        if k % 4 == 2: clap(tb)
        hat(tb + beat / 4, .05, .25 if k % 2 else -.25)
    k += 1

# ---------------- SFX
def whoosh(tp, d=.35, g=.2, pan=0.0):
    t = ts(d); a = np.linspace(.02, .45, len(t)); x = noise(d); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * t / d) ** 2 * g * 2.4, tp - d * .65, pan=pan)
def subhit(t0, g=.9):
    t = ts(1.4); f = 62 * np.exp(-t * 3) + 36; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * g, t0); add(lp(noise(.4), .15) * np.exp(-ts(.4) * 9) * .4, t0)
def pop(t0, f0=700, g=.2, pan=0.0):
    t = ts(.1); f = f0 * (1 + 1.5 * np.exp(-t * 60)); add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * g, t0, pan=pan)
def tick(t0, g=.1):
    t = ts(.025); add(hp(noise(.025), .5) * np.exp(-t * 220) * g, t0)
def chime(t0, notes, g=.14, step=.05):
    for i, m in enumerate(notes):
        tt = ts(.7); add((np.sin(2 * np.pi * nf(m) * tt) + .3 * np.sin(4 * np.pi * nf(m) * tt)) * np.exp(-tt * 6) * g, t0 + i * step, pan=(i % 2 - .5) * .4)
def riser(t0, t1, g=.1):
    d = t1 - t0; t = ts(d); f = 300 + 1500 * (t / d) ** 2; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * g, t0)

whoosh(.16, .22, .3); subhit(.18, .9); pop(.2, 500, .25)                                   # hook slam
for i in range(V["words"]): pop(.3 + i * V["step"], 620 + (i % 4) * 90, .11, pan=(i % 3 - 1) * .3)   # word pops
whoosh(V["demo"] + .2, .4, .2)
if V["kind"] == "price":
    for i in range(3): riser(V["demo"] + .45 + i * .18, V["demo"] + 1.35 + i * .18, .05); pop(V["demo"] + 1.35 + i * .18, 500 + i * 120, .12)
    subhit(V["win"], .5); chime(V["win"], [72, 76, 79, 84], .15)
if V["kind"] == "deliver":
    for i in range(3): whoosh(V["demo"] + .5 + i * .15, .25, .12, pan=(i - 1) * .4); pop(V["demo"] + .82 + i * .15, 420 + i * 60, .14)
    pop(V["demo"] + .95, 300, .3); whoosh(V["tmap"] + .2, .4, .2); pop(V["tmap"] + .35, 900, .15)
    for i in range(12): tick(V["tmap"] + .4 + i * .1, .07)
    chime(V["tmap"] + 1.65, [76, 84], .2, .12)                                              # doorbell
if V["kind"] == "search":
    for i in range(12): tick(V["demo"] + .5 + i * .075, .13)
    whoosh(V["demo"] + 1.7, .3, .14); pop(V["demo"] + 1.55, 700, .14); tick(V["demo"] + 2.3, .25); pop(V["demo"] + 2.32, 880, .16); chime(V["demo"] + 2.45, [79, 84], .16, .08)
whoosh(V["bul"] + .05, .3, .18)
for i in range(3): pop(V["bul"] + .12 + i * .16, 700 + i * 140, .2, pan=(i - 1) * .3)
subhit(V["cta"], .7); chime(V["cta"] + .02, [72, 76, 79, 84, 88], .14, .045); pop(V["cta"] + .3, 880, .18)
whoosh(DUR - .15, .35, .18)

# ---------------- VO (uz-UZ Madina, energetic preset) with ~8 dB ducking
def loadw(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float64) / 32768
vL = np.zeros(N); vR = np.zeros(N)
if "--no-vo" not in sys.argv:
    for name, t0 in [(f"h{vid}", .4), ("cta", V["cta"] + .15)]:
        x = loadw(os.path.join(ROOT, f"audio/vo/{name}.wav")); x = x / np.abs(x).max() * .9
        a = int(t0 * SR); b = min(N, a + len(x)); vL[a:b] += x[:b - a, 0]; vR[a:b] += x[:b - a, 1]
env = np.abs(vL) + np.abs(vR); kk = int(.12 * SR); env = np.convolve(env, np.ones(kk) / kk, "same"); env = np.convolve(env, np.ones(kk) / kk, "same")
duck = 1 - .62 * np.clip(env / (env.max() * .25 + 1e-9), 0, 1)
m = np.abs(np.stack([L, R], 1)).max(); L = L / m * .55 * duck + vL; R = R / m * .55 * duck + vR
mix = np.stack([L, R], 1); fo = int(.3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * .9
pre = os.path.join(ROOT, f"audio/pre-{vid}.wav"); out = os.path.join(ROOT, f"audio/score-{vid}.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), out], check=True)
os.remove(pre); print(out)
