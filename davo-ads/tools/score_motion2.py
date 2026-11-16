# Davo Motion 2 "Tibbiy uskunalar" (7.5 s) — sound concept: CLINICAL PRECISION.
# A patient-monitor beep is the metronome: the music is built around its pitch, every visual event is a monitor tone,
# devices "draw" with a pen-on-blueprint scratch and "fill" with a glassy tick; the CTA lands on a cuff-release "pssht".
# No voice. usage: python3 tools/score_motion2.py [gain_db]  -> prints WAV path
import subprocess, sys, numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]; gain = float(args[0]) if args else 0.0
T = dict(head=.55, search=1.15, car=1.75, step=.55, bul=4.55, cta=5.75); DUR = 7.5
SR = 48000; N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N); rng = np.random.default_rng(2)
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
def monitor(t0, m=86, g=.16, d=.11, pan=0.0):            # patient-monitor beep: pure sine, square-ish gate
    x = ts(d + .02); env = np.minimum(1, x / .004) * np.clip((d - x) / .01, 0, 1)
    add((np.sin(2 * np.pi * nf(m) * x) + .12 * np.sin(6 * np.pi * nf(m) * x)) * env * g, t0, pan=pan)
def thump(t0, g=.55):
    x = ts(.28); add(np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x * 14) + 40) / SR) * np.exp(-x * 13) * g, t0)
def glass(t0, m, g=.1, pan=0.0):                          # FM glass bell
    x = ts(1.2); mod = np.sin(2 * np.pi * nf(m) * 3.5 * x) * 2.2 * np.exp(-x * 4)
    add(np.sin(2 * np.pi * nf(m) * x + mod) * np.exp(-x * 3.2) * g, t0, pan=pan)
def scratch(t0, d=.3, g=.07, pan=0.0):                    # pen drawing on blueprint
    x = ts(d); n = hp(lp(noise(d), .5), .15); am = .5 + .5 * np.abs(np.sin(2 * np.pi * 14 * x))
    add(n * am * np.minimum(1, x / .02) * np.clip((d - x) / .05, 0, 1) * g, t0, pan=pan)
def swipe(tp, d=.28, g=.12, pan=0.0):
    x = ts(d); a = np.linspace(.03, .5, len(x)); n = noise(d); y = np.empty_like(n); s = 0.0
    for i, v in enumerate(n): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * x / d) ** 2 * g * 2.4, tp - d * .6, pan=pan)
def tick(t0, g=.12):
    x = ts(.02); add(hp(noise(.02), .6) * np.exp(-x * 260) * g, t0)
def pssht(t0, g=.3):                                      # blood-pressure cuff release
    x = ts(.9); n = noise(.9); y = np.empty_like(n); s = 0.0; a = np.linspace(.5, .04, len(x))
    for i, v in enumerate(n): s += a[i] * (v - s); y[i] = s
    add(y * np.exp(-x * 3.2) * np.minimum(1, x / .01) * g * 2.2, t0)

# ---- bed: airy Dmaj9 pad + sub pulse locked to a 112 BPM grid; the monitor beep (D6) is the hi-hat
BPM = 112; beat = 60 / BPM
x = ts(DUR); pad = sum(np.sin(2 * np.pi * nf(m) * x * (1 + .003 * k)) for k, m in enumerate([62, 66, 69, 73, 76])) / 5
add(lp(pad, .04) * np.minimum(1, x / .8) * np.clip((DUR - x) / .5, 0, 1) * .11, 0)
k = 0
while k * beat < DUR - .3:
    tb = .55 + k * beat
    if tb >= DUR - .3: break
    if tb < T["cta"] - .1 or tb > T["cta"] + .3:
        thump(tb, .5 if k % 2 == 0 else .35)
        x = ts(.22); add(np.sin(2 * np.pi * nf(38) * x) * np.exp(-x * 9) * .22, tb)
        tick(tb + beat / 2, .07)
    k += 1
# ---- events
# ECG opener: one real monitor beep on each spike + heartbeat under it
for i, t0 in enumerate([.1, .33, .55]): monitor(t0, 86, .14 if i < 2 else .2); thump(t0 + .02, .45)
glass(T["head"], 86, .12); glass(T["head"] + .09, 90, .09, .3); glass(T["head"] + .18, 93, .08, -.3)
swipe(T["search"] + .1, .3, .12)
for i in range(16): tick(T["search"] + .2 + i * .031, .1)
for i in range(5):
    t0 = T["car"] + i * T["step"]
    if i: swipe(t0 + .3, .26, .11, pan=.3)
    scratch(t0 - .05 if i == 0 else t0 + .28, .32, .06, pan=-.2)
    monitor(t0 + .45 if i else t0 + .1, [81, 83, 85, 86, 88][i], .1)
    glass(t0 + .5 if i else t0 + .15, [74, 76, 78, 81, 83][i], .07, pan=(i % 2 - .5) * .5)
swipe(T["bul"] - .05, .35, .14)
for i, m in enumerate([84, 88, 91]): monitor(T["bul"] + i * .18 + .12, m, .15, .09, pan=(i - 1) * .3); tick(T["bul"] + i * .18 + .14, .2)
pssht(T["cta"] - .05, .32); thump(T["cta"] + .05, .8)
for i, m in enumerate([74, 78, 81, 86, 90]): glass(T["cta"] + .06 + i * .045, m, .12, pan=(i % 2 - .5) * .4)
monitor(T["cta"] + .4, 86, .12, .22)
# ---- master
mix = np.stack([L, R], 1); fo = int(.3 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.15) / np.tanh(1.15) * .9
pre = os.path.join(ROOT, "audio/pre-motion2.wav"); out = os.path.join(ROOT, "audio/score-motion2.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), out], check=True)
os.remove(pre); print(out)
