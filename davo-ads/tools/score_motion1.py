# Davo Motion 1 "Overthinking" (15 s) — generated music + SFX + Uzbek VO. usage: python3 tools/score_motion1.py [gain_db] [--no-vo]
import subprocess, sys, numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]; gain = float(args[0]) if args else 0.0
T = dict(pull=2.75, a1=3.2, a2=4.9, a3=6.6, a4=9.0, a5=11.0, cta=13.0); DUR = 15.0
SR = 48000; N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(9)
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
# --- overthinking bed: detuned drone + accelerating ticking clock + rising heartbeat
t = ts(T["a1"]); drone = sum(np.sin(2 * np.pi * nf(m) * (1 + .004 * k) * t) for k, m in enumerate([45, 52, 56, 51])) / 4
add(lp(drone, .05) * np.minimum(1, t / .5) * (.5 + .5 * t / T["a1"]) * .22, 0)
tt = 0.0; i = 0
while tt < T["pull"]:
    x = ts(.03); add(hp(noise(.03), .5) * np.exp(-x * 200) * (.10 if i % 2 else .14), tt, pan=.4 if i % 2 else -.4)
    tt += max(.07, .36 - .11 * tt); i += 1
for k in range(6):
    hb = .3 + k * .42 - k * k * .015
    for d, g in ((0, .5), (.14, .32)):
        x = ts(.25); add(np.sin(2 * np.pi * np.cumsum(55 * np.exp(-x * 8) + 38) / SR) * np.exp(-x * 14) * g, hb + d)
x = ts(.45); add(hp(noise(.45), .2) * (x / .45) ** 3 * .35, T["pull"] - .02)                    # suck-in
# --- main track: bright pop 124 BPM from the snap
BPM = 124; beat = 60 / BPM; bar = 4 * beat; t0m = T["a1"]
prog = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]
def kick(t0, g=.85):
    x = ts(.3); add(np.sin(2 * np.pi * np.cumsum(150 * np.exp(-x * 30) + 47) / SR) * np.exp(-x * 9) * g, t0)
def clap(t0, g=.32):
    x = ts(.2); add(hp(noise(.2), .3) * np.exp(-x * 25) * g, t0)
def hat(t0, g=.055, pan=.3):
    x = ts(.04); add(hp(noise(.04), .7) * np.exp(-x * 100) * g, t0, pan=pan)
b = 0
while t0m + b * bar < DUR:
    ch = prog[b % 4]; s0 = t0m + b * bar; x = ts(bar + .3); env = np.minimum(1, x / .05) * np.exp(-x * .45)
    pad = sum(np.sin(2 * np.pi * nf(m) * x) + .4 * np.sign(np.sin(2 * np.pi * nf(m) * 1.003 * x)) for m in ch) / len(ch); add(lp(pad * env, .08) * .075, s0)
    for k in range(8):
        tb = s0 + k * beat / 2
        if tb >= DUR - .4: break
        if k % 2 == 0: kick(tb)
        if k % 4 == 2: clap(tb)
        hat(tb + beat / 4, .05, .25 if k % 2 else -.25)
        x = ts(.2); add(np.tanh(3 * np.sin(2 * np.pi * nf(ch[0] - 24) * x)) * np.exp(-x * 13) * .16, tb + beat / 4)
        for q in range(2):
            x = ts(.15); m = ch[(k * 2 + q) % 4] + 12; add(lp((2 * ((nf(m) * x) % 1) - 1) * np.exp(-x * 18), .3) * .04, tb + q * beat / 4, pan=.3 if q else -.3)
    b += 1
# --- SFX
def whoosh(tp, d=.35, g=.2, pan=0.0):
    x = ts(d); a = np.linspace(.02, .45, len(x)); n = noise(d); y = np.empty_like(n); s = 0.0
    for i, v in enumerate(n): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * x / d) ** 2 * g * 2.4, tp - d * .65, pan=pan)
def subhit(t0, g=.9):
    x = ts(1.4); add(np.sin(2 * np.pi * np.cumsum(62 * np.exp(-x * 3) + 35) / SR) * np.exp(-x * 2.8) * g, t0); add(lp(noise(.4), .15) * np.exp(-ts(.4) * 9) * .4, t0)
def pop(t0, f0=700, g=.2, pan=0.0):
    x = ts(.1); add(np.sin(2 * np.pi * np.cumsum(f0 * (1 + 1.5 * np.exp(-x * 60))) / SR) * np.exp(-x * 40) * g, t0, pan=pan)
def tick(t0, g=.1):
    x = ts(.025); add(hp(noise(.025), .5) * np.exp(-x * 220) * g, t0)
def chime(t0, notes, g=.14, step=.05):
    for i, m in enumerate(notes):
        x = ts(.7); add((np.sin(2 * np.pi * nf(m) * x) + .3 * np.sin(4 * np.pi * nf(m) * x)) * np.exp(-x * 6) * g, t0 + i * step, pan=(i % 2 - .5) * .4)
bub = [.18 + i * .22 - max(0, i - 5) * .07 for i in range(10)]
for i, b0 in enumerate(bub): pop(b0, 500 + (i % 5) * 110, .16, pan=(i % 3 - 1) * .5)
x = ts(.6); add(np.sin(2 * np.pi * np.cumsum(1200 + 2600 * np.exp(-x * 9)) / SR) * np.exp(-x * 7) * .18, T["pull"] + .4)       # string "twang" snap
subhit(T["pull"] + .42, 1.0); whoosh(T["a1"] + .05, .3, .25)
for i in range(3): pop(T["a1"] + .05 + i * .1, 620 + i * 120, .14)
for t0 in (T["a2"], T["a3"], T["a4"], T["a5"], T["cta"]): whoosh(t0 + .05, .36, .26)
tick(T["a2"] + .55, .35); pop(T["a2"] + .6, 300, .25)
for i in range(16): tick(T["a2"] + 1.0 + i * .045, .06)
chime(T["a2"] + 1.15, [72, 79, 84], .16, .05); subhit(T["a2"] + 1.15, .5)
for i in range(3): pop(T["a3"] + 1.3 + i * .15, 500 + i * 120, .13)
subhit(T["a3"] + 1.55, .45); chime(T["a3"] + 1.55, [72, 76, 79, 84], .15)
tick(T["a4"] + .72, .35); pop(T["a4"] + .75, 880, .2); whoosh(T["a4"] + 1.3, .4, .15); pop(T["a4"] + 1.45, 260, .35); pop(T["a4"] + 1.47, 1300, .16)
for i in range(10): tick(T["a5"] + .4 + i * .12, .07)
chime(T["a5"] + 1.55, [76, 84], .2, .12)
subhit(T["cta"] + .05, .8); chime(T["cta"] + .45, [72, 76, 79, 84, 88], .14, .045); pop(T["cta"] + .6, 880, .18)
for i in range(6): pop(T["cta"] + 1.2 + i * .06, 1800 + i * 200, .03, pan=.3)
# --- VO: overlapping anxious questions, then the calm answers
def loadw(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float64) / 32768
vL = np.zeros(N); vR = np.zeros(N)
if "--no-vo" not in sys.argv:
    for name, t0, g, pan in [("q1", .25, .75, -.35), ("q2", .95, .7, .35), ("q3", 1.5, .7, -.3), ("q4", 1.95, .7, .3),
                             ("a1", 3.3, .9, 0), ("a2", 5.0, .9, 0), ("a3", 6.75, .9, 0), ("a4", 9.1, .9, 0), ("a5", 11.1, .9, 0), ("a6", 12.98, .9, 0)]:
        x = loadw(os.path.join(ROOT, f"audio/vo3/{name}.wav")); x = x / np.abs(x).max() * g
        a = int(t0 * SR); b = min(N, a + len(x)); vL[a:b] += x[:b - a, 0] * (1 - pan); vR[a:b] += x[:b - a, 1] * (1 + pan)
env = np.abs(vL) + np.abs(vR); kk = int(.12 * SR); env = np.convolve(env, np.ones(kk) / kk, "same"); env = np.convolve(env, np.ones(kk) / kk, "same")
duck = 1 - .6 * np.clip(env / (env.max() * .25 + 1e-9), 0, 1)
m = np.abs(np.stack([L, R], 1)).max(); L = L / m * .55 * duck + vL; R = R / m * .55 * duck + vR
mix = np.stack([L, R], 1); fo = int(.3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * .9
pre = os.path.join(ROOT, "audio/pre-motion1.wav"); out = os.path.join(ROOT, "audio/score-motion1.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), out], check=True)
os.remove(pre); print(out)
