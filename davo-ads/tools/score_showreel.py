# Davo Delivery showreel (24 s) — generated music + SFX + Uzbek VO. usage: python3 tools/score_showreel.py [gain_db] [--no-vo]
import subprocess, sys, numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]; gain = float(args[0]) if args else 0.0
T = dict(type=1.4, s2=4.0, s3=7.6, cut=9.7, s4=12.0, arrive=15.0, s5=16.0, s6=20.4); DUR = 24.0
SR = 48000; N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(5)
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
BPM = 126; beat = 60 / BPM; bar = 4 * beat
prog = [[57, 60, 64, 69], [53, 57, 60, 65], [60, 64, 67, 72], [55, 59, 62, 67]]   # Am F C G
def kick(t0, g=.85):
    t = ts(.32); f = 150 * np.exp(-t * 30) + 47; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * g, t0)
def clap(t0, g=.34):
    t = ts(.22); add(hp(noise(.22), .3) * np.exp(-t * 24) * g, t0)
def hat(t0, g=.06, pan=.3):
    t = ts(.04); add(hp(noise(.04), .7) * np.exp(-t * 100) * g, t0, pan=pan)
def crash(t0, g=.22):
    t = ts(1.5); add(hp(noise(1.5), .4) * np.exp(-t * 3) * g, t0)
# beat windows: drop on the logo stamp, breaks before each scene hit
wins = [(1.12, T["s2"] - .3), (T["s2"] + .1, T["s3"] - .45), (T["s3"], T["cut"] - .35), (T["cut"], T["s4"] - .3), (T["s4"] + .1, T["s5"] - .3), (T["s5"], T["s6"]), (T["s6"] + .55, DUR - .8)]
for b in range(int(DUR / bar) + 1):
    ch = prog[b % 4]; t0 = b * bar; t = ts(bar + .3); env = np.minimum(1, t / .06) * np.exp(-t * .45)
    pad = sum(np.sin(2 * np.pi * nf(m) * t) + .4 * np.sign(np.sin(2 * np.pi * nf(m) * 1.003 * t)) for m in ch) / len(ch); add(lp(pad * env, .08) * .075, t0)
for a, e in wins:
    k = 0
    while a + k * beat / 2 < e - 1e-6:
        tb = a + k * beat / 2; ch = prog[int(tb // bar) % 4]
        if k % 2 == 0: kick(tb)
        if k % 4 == 2: clap(tb)
        hat(tb + beat / 4, .05, .25 if k % 2 else -.25)
        tt = ts(.2); add(np.tanh(3 * np.sin(2 * np.pi * nf(ch[0] - 24) * tt)) * np.exp(-tt * 13) * .17, tb + beat / 4)
        for q in range(2):
            tt = ts(.15); m = ch[(k * 2 + q) % 4] + 12; add(lp((2 * ((nf(m) * tt) % 1) - 1) * np.exp(-tt * 18), .3) * .045, tb + q * beat / 4, pan=.3 if q else -.3)
        k += 1
    crash(a, .2)
def whoosh(tp, d=.35, g=.2, pan=0.0):
    t = ts(d); a = np.linspace(.02, .45, len(t)); x = noise(d); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * t / d) ** 2 * g * 2.4, tp - d * .65, pan=pan)
def subhit(t0, g=.9):
    t = ts(1.5); f = 62 * np.exp(-t * 3) + 35; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.8) * g, t0); add(lp(noise(.4), .15) * np.exp(-ts(.4) * 9) * .4, t0)
def thud(t0, g=.6):
    t = ts(.3); f = 95 * np.exp(-t * 18) + 48; add((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 13) + lp(noise(.3), .3) * np.exp(-t * 55) * .6) * g, t0)
def pop(t0, f0=700, g=.2, pan=0.0):
    t = ts(.1); f = f0 * (1 + 1.5 * np.exp(-t * 60)); add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * g, t0, pan=pan)
def tick(t0, g=.1):
    t = ts(.025); add(hp(noise(.025), .5) * np.exp(-t * 220) * g, t0)
def chime(t0, notes, g=.14, step=.05):
    for i, m in enumerate(notes):
        tt = ts(.8); add((np.sin(2 * np.pi * nf(m) * tt) + .3 * np.sin(4 * np.pi * nf(m) * tt)) * np.exp(-tt * 5) * g, t0 + i * step, pan=(i % 2 - .5) * .4)
def riser(t0, t1, g=.12):
    d = t1 - t0; t = ts(d); x = hp(noise(d), .2) * (t / d) ** 2 * .7 + np.sin(2 * np.pi * np.cumsum(300 + 2200 * (t / d) ** 2) / SR) * (t / d) ** 3 * .25; add(x * g, t0)
# S1
for i in range(4): thud(.05 + i * .09 + .36, .5); pop(.05 + i * .09 + .36, 260 + i * 50, .2, pan=(i % 2 - .5) * .6)
whoosh(1.0, .25, .2); subhit(1.12, 1.0); chime(1.12, [69, 72, 76, 81], .16, .03)
for t0 in (1.4, 1.75, 2.1): whoosh(t0 + .03, .16, .25); thud(t0 + .04, .9)
pop(2.5, 600, .15); pop(2.62, 700, .15); thud(2.87, .7); subhit(2.87, .5)
riser(T["s2"] - .5, T["s2"], .12); whoosh(T["s2"] + .15, .45, .28)
# S2
pop(T["s2"] + .3, 520, .16)
for i in range(3): pop(T["s2"] + .37 + i * .1, 640 + i * 90, .11)
for i in range(12): tick(T["s2"] + .75 + i * .075, .14)
for i in range(3): whoosh(T["s2"] + 1.85 + i * .13, .22, .12, pan=(i - 1) * .3); pop(T["s2"] + 1.95 + i * .13, 480 + i * 80, .14)
tick(T["s2"] + 2.72, .3); pop(T["s2"] + 2.75, 900, .2); chime(T["s2"] + 2.78, [79, 84], .12, .07)
riser(T["s3"] - .55, T["s3"], .16); whoosh(T["s3"] + .1, .5, .3)
# S3
subhit(T["s3"] + .05, .7)
for i in range(3): whoosh(T["s3"] + .5 + i * .12, .3, .12, pan=(i - 1) * .4)
for i in range(18): tick(T["s3"] + .75 + i * .06, .07)
for i in range(3): pop(T["s3"] + 1.75 + i * .1, 500 + i * 100, .13, pan=(i - 1) * .4)
tick(T["cut"] - .02, .5); pop(T["cut"], 1400, .2); subhit(T["cut"], .8); chime(T["cut"] + .05, [72, 76, 79, 84, 88], .16, .04)
whoosh(T["cut"] + .45, .5, .12, pan=-.5); whoosh(T["cut"] + .5, .5, .12, pan=.5); thud(T["cut"] + .58, .5)
riser(T["s4"] - .45, T["s4"], .14); whoosh(T["s4"] + .15, .5, .3)
# S4
pop(T["s4"] + .15, 600, .16); pop(T["s4"] + .3, 760, .16)
t = ts(2.4); eng = np.sign(np.sin(2 * np.pi * np.cumsum(70 + 40 * np.sin(np.pi * t / 2.4)) / SR)) * .5 + lp(noise(2.4), .2); add(lp(eng, .12) * np.sin(np.pi * t / 2.4) ** .5 * .07, T["s4"] + .55, pan=.1)
for i in range(5): whoosh(T["s4"] + .9 + i * .42, .3, .07, pan=(i % 2 - .5) * .6)
chime(T["arrive"], [76, 84], .22, .13); subhit(T["arrive"], .45); pop(T["arrive"] + .1, 880, .16)
# S5
whoosh(T["s5"] + .15, .4, .25)
for i in range(3): whoosh(T["s5"] + i * .45 + .18, .22, .26, pan=(.5 if i % 2 else -.5)); thud(T["s5"] + i * .45 + .28, .95); pop(T["s5"] + i * .45 + .3, 500 + i * 130, .18)
for i in range(14): tick(T["s5"] + 1.1 + i * .055, .08)
# S6
riser(T["s6"] - .1, T["s6"] + .5, .13); whoosh(T["s6"] + .3, .5, .25); subhit(T["s6"] + .55, 1.0); chime(T["s6"] + .55, [69, 72, 76, 81, 84, 88], .16, .04)
whoosh(T["s6"] + .95, .35, .14); pop(T["s6"] + 1.37, 880, .2); pop(T["s6"] + 1.62, 1100, .12)
for i in range(6): pop(T["s6"] + 2.05 + i * .06, 1800 + i * 200, .03, pan=.3)
# VO
def loadw(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float64) / 32768
vL = np.zeros(N); vR = np.zeros(N)
if "--no-vo" not in sys.argv:
    for name, t0 in [("v1", 1.38), ("v2", 4.55), ("v3", 7.95), ("v4", 12.45), ("v5", 16.15), ("v6", 21.1)]:
        x = loadw(os.path.join(ROOT, f"audio/vo2/{name}.wav")); x = x / np.abs(x).max() * .9
        a = int(t0 * SR); b = min(N, a + len(x)); vL[a:b] += x[:b - a, 0]; vR[a:b] += x[:b - a, 1]
env = np.abs(vL) + np.abs(vR); kk = int(.12 * SR); env = np.convolve(env, np.ones(kk) / kk, "same"); env = np.convolve(env, np.ones(kk) / kk, "same")
duck = 1 - .62 * np.clip(env / (env.max() * .25 + 1e-9), 0, 1)
m = np.abs(np.stack([L, R], 1)).max(); L = L / m * .55 * duck + vL; R = R / m * .55 * duck + vR
mix = np.stack([L, R], 1); fo = int(.4 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * .9
pre = os.path.join(ROOT, "audio/pre-showreel.wav"); out = os.path.join(ROOT, "audio/score-showreel.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), out], check=True)
os.remove(pre); print(out)
