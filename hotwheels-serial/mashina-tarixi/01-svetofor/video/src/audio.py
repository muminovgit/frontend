"""Music + SFX for "Portlagan svetofor", written per beat (beat-local times), so a re-timed timeline re-mixes itself.
Writes stems music.wav and sfx.wav, and mix_novoice.wav (loudnorm later). When the narration exists:
  python3 audio.py --voice voice_dir   (voice_dir/<beat>.wav placed at beat start + 0.12 s, music ducked under it)"""
import json, sys, wave, os
import numpy as np
from beats import timeline

SR = 48000
TL = timeline()
DUR = sum(b["dur"] for b in TL)
N = int(SR * DUR) + SR // 2
rng = np.random.default_rng(1868)
music = np.zeros(N); sfx = np.zeros(N)
START = {b["id"]: b["start"] for b in TL}
BEAT = {b["id"]: b for b in TL}

def put(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= N: return
    j = min(N, i + len(x)); buf[i:j] += g * x[: j - i]
def env(n, a, d):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); e *= np.exp(-np.arange(n) / max(1, d * SR)); return e
def lp(x, k):  # one-pole lowpass (vectorised via cumulative filter on chunks would be overkill; n is small here)
    from scipy.signal import lfilter
    return lfilter([k], [1, k - 1], x)
def hp(x, k): return x - lp(x, k)
def tone(f, d, harm=(1, .5, .25, .12), dec=0.25, a=0.004):
    n = int(d * SR); t = np.arange(n) / SR
    return sum(h * np.sin(2 * np.pi * f * (i + 1) * t) * np.exp(-t * (i + 1) / dec) for i, h in enumerate(harm)) * env(n, a, 10)
def noise(d): return rng.standard_normal(int(d * SR))
mid = lambda m: 440 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------------ SFX library
def hoof(): n = int(0.07 * SR); return lp(noise(0.07) * env(n, 0.002, 0.012), 0.35) * 0.9 + 0.35 * np.sin(2 * np.pi * 950 * np.arange(n) / SR) * env(n, 0.001, 0.01)
def hooves(at, dur, rate=0.24, g=0.4, slow=False):
    t, k = 0.0, 0
    while t < dur:
        put(sfx, hoof(), at + t, g * (0.8 + 0.4 * (k % 2))); k += 1
        t += rate * (1 + (1.5 * t / dur if slow else 0))
def boom(at, g=1.0):
    n = int(2.6 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * (70 * np.exp(-tt * 3) + 30) * tt) * env(n, 0.003, 0.5) + lp(noise(2.6), 0.25) * env(n, 0.001, 0.2) * 1.1
    x += (rng.random(n) > 0.9985) * rng.standard_normal(n) * 3 * env(n, 0.05, 0.6)
    put(sfx, x, at, g)
def glass(at, k=8):
    for i in range(k):
        m = int(0.25 * SR); put(sfx, np.sin(2 * np.pi * rng.uniform(2500, 5200) * np.arange(m) / SR) * env(m, 0.001, 0.05) * 0.13, at + i * 0.06 + rng.random() * 0.05)
def hiss(at, dur, g0=0.02, g1=0.2):
    n = int(dur * SR); x = hp(noise(dur), 0.05) * np.linspace(g0, g1, n) * (1 + 0.3 * np.sin(2 * np.pi * 7 * np.arange(n) / SR)); put(sfx, x, at)
def clunk(at, f=180, g=0.4): n = int(0.14 * SR); put(sfx, (np.sin(2 * np.pi * f * np.arange(n) / SR) + 0.6 * noise(0.14)) * env(n, 0.001, 0.03), at, g)
def ding(at, f=1320, g=0.18): n = int(1.2 * SR); put(sfx, tone(f, 1.2, (1, .3, .1), 0.5), at, g)
def pop(at, g=0.3): n = int(0.09 * SR); t = np.arange(n) / SR; put(sfx, np.sin(2 * np.pi * (300 + 900 * t / 0.09) * t) * env(n, 0.002, 0.03), at, g)
def whoosh(at, d=0.5, g=0.35): n = int(d * SR); put(sfx, lp(noise(d), 0.08) * np.sin(np.linspace(0, np.pi, n)) ** 2, at, g)
def tweet(at, d=1.4, g=0.08): n = int(d * SR); t = np.arange(n) / SR; put(sfx, np.sin(2 * np.pi * (1800 + 400 * np.sin(2 * np.pi * 6 * t)) * t) * env(n, 0.05, 0.6), at, g)
def wahwah(at, g=0.22):  # comedic sad trombone: 4 falling notes, last one wobbles
    t0 = at
    for i, (m, d) in enumerate([(58, 0.32), (57, 0.32), (56, 0.32), (55, 1.0)]):
        n = int(d * SR); t = np.arange(n) / SR; f = mid(m) * (1 + (0.03 * np.sin(2 * np.pi * 6 * t) if i == 3 else 0))
        x = sum(np.sign(np.sin(2 * np.pi * f * k * t)) / k for k in (1, 2, 3)) * env(n, 0.02, d * 0.9)
        put(sfx, lp(x, 0.12), t0, g); t0 += d
def chuff(at, g=0.3): n = int(0.18 * SR); put(sfx, lp(noise(0.18), 0.2) * env(n, 0.005, 0.06), at, g)
def whistle(at, d=0.8, g=0.12): n = int(d * SR); t = np.arange(n) / SR; put(sfx, (np.sin(2 * np.pi * 880 * t) + 0.5 * np.sin(2 * np.pi * 1108 * t)) * np.sin(np.linspace(0, np.pi, n)), at, g)
def steps(at, dur, rate=0.32, g=0.25):
    t = 0
    while t < dur: n = int(0.05 * SR); put(sfx, lp(noise(0.05), 0.5) * env(n, 0.001, 0.012), at + t, g); t += rate
def flips(at, dur, k=24, g=0.2):
    for i in range(k): n = int(0.06 * SR); put(sfx, hp(noise(0.06), 0.3) * env(n, 0.002, 0.02), at + dur * (i / k) ** 0.8, g)
def hum(at, dur, f=100, g=0.04): n = int(dur * SR); t = np.arange(n) / SR; put(sfx, (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t)) * np.minimum(1, t / 0.2), at, g)
def engine(at, dur, rev_at=None, g=0.12):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 32 + (np.maximum(0, t - rev_at) ** 1.4 * 40 if rev_at is not None else 0)
    put(sfx, lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) + 0.3 * noise(dur), 0.06) * np.minimum(1, t / 0.3), at, g)
def murmur(at, dur, g=0.05): put(sfx, lp(noise(dur), 0.03) * (1 + 0.4 * np.sin(np.arange(int(dur * SR)) / SR * 3)), at, g)

S = START
# b1 hook: flicker hiss, BOOM, glass, dizzy tweet
hiss(S["b1"], 1.25, 0.06, 0.22); boom(S["b1"] + 1.25); glass(S["b1"] + 1.45); tweet(S["b1"] + 2.4)
# b2 busy street
murmur(S["b2"], 5.2); hooves(S["b2"], 5.2, 0.24, 0.45); hooves(S["b2"] + 0.1, 5.0, 0.3, 0.18); whoosh(S["b2"] + 2.05, 0.6, 0.3)
# b3 Knight + blueprint
whoosh(S["b3"] + 0.1, 0.4, 0.25); whoosh(S["b3"] + 1.05, 0.35, 0.3); ding(S["b3"] + 1.35, 1568, 0.12)
# b4 train + semaphore
for i in range(10): chuff(S["b4"] + i * 0.24, 0.32 - 0.02 * i)
whistle(S["b4"] + 0.3); clunk(S["b4"] + 1.6, 220, 0.3); clunk(S["b4"] + 1.75, 260, 0.3); whoosh(S["b4"] + 3.3, 0.6, 0.25)
put(sfx, lp(noise(0.5), 0.2) * env(int(0.5 * SR), 0.02, 0.15), S["b4"] + 3.6, 0.35)
# b5 lever, stop, badges
hooves(S["b5"], 2.4, 0.22, 0.45, slow=True); murmur(S["b5"], 5.2, 0.04)
clunk(S["b5"] + 0.4, 160, 0.5); clunk(S["b5"] + 0.9, 240, 0.35); clunk(S["b5"] + 1.02, 280, 0.3); ding(S["b5"] + 1.05, 1320, 0.14)
pop(S["b5"] + 2.36); pop(S["b5"] + 3.46)
# b6 lady crosses + newspaper
murmur(S["b6"], 4.2, 0.04); steps(S["b6"] + 0.3, 2.3); whoosh(S["b6"] + 2.0, 0.45, 0.35); flips(S["b6"] + 2.2, 0.25, 4, 0.25)
# b7 winter night, gas leak builds
put(sfx, lp(noise(4.2), 0.015) * 0.12, S["b7"]); hiss(S["b7"] + 1.6, 2.6, 0.02, 0.25)
# b8 explosion
boom(S["b8"] + 0.1); glass(S["b8"] + 0.3)
# b9 sooty policeman + retired stamp
tweet(S["b9"] + 0.1, 1.6); wahwah(S["b9"] + 0.3); clunk(S["b9"] + 2.32, 90, 0.7)
# b10 stove analogy + lantern diagram
clunk(S["b10"] + 0.3, 600, 0.2); hiss(S["b10"] + 0.6, 2.15, 0.05, 0.15)
put(sfx, hp(noise(0.15), 0.4) * env(int(0.15 * SR), 0.001, 0.05), S["b10"] + 2.35, 0.5)  # match strike
boom(S["b10"] + 2.75, 0.45); whoosh(S["b10"] + 3.5, 0.5, 0.3); hiss(S["b10"] + 3.9, 1.7, 0.03, 0.16)
for i in range(6): pop(S["b10"] + 5.7 + i * 0.05, 0.12)
boom(S["b10"] + 6.05, 0.9)
# b11 calendar flips, electric light
flips(S["b11"] + 0.2, 2.3, 26); whoosh(S["b11"] + 2.7, 0.5); hum(S["b11"] + 3.2, 1.2, 120, 0.05); clunk(S["b11"] + 3.25, 900, 0.15)
clunk(S["b11"] + 3.5, 700, 0.12); clunk(S["b11"] + 3.9, 700, 0.12)
# b12 modern driver
engine(S["b12"], 5.6, rev_at=4.4, g=0.1); murmur(S["b12"], 5.6, 0.03)
for i in range(10): pop(S["b12"] + 0.2 + i * 0.22, 0.06)  # drumming on the wheel
put(sfx, hp(noise(0.5), 0.5) * (rng.random(int(0.5 * SR)) > 0.7) * 0.4, S["b12"] + 2.75); ding(S["b12"] + 4.1, 988, 0.12)
# b13 end card
whoosh(S["b13"], 0.7, 0.35); pop(S["b13"] + 0.45, 0.35); ding(S["b13"] + 0.95, 1760, 0.15); ding(S["b13"] + 1.1, 2217, 0.1)

# ------------------------------------------------------------------ music (original, procedural)
BPM = 112; Q = 60 / BPM
def pluck(m, at, d=0.45, g=0.25): put(music, tone(mid(m), d, (1, .45, .2, .1, .05), 0.18), at, g)
def bell(m, at, g=0.08): put(music, tone(mid(m), 1.0, (1, .0, .35, 0, .15), 0.45), at, g)
def drone(at, dur, m=36, g=0.05):
    n = int(dur * SR); t = np.arange(n) / SR
    put(music, (np.sin(2 * np.pi * mid(m) * t) + 0.5 * np.sin(2 * np.pi * mid(m + 7) * t * 1.003)) * np.minimum(1, t / 0.5) * np.minimum(1, (dur - t) / 0.4), at, g)
def tremolo(at, dur, ms, g=0.05):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * mid(m) * t) for m in ms) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 9 * t))) * np.minimum(1, t / 0.6)
    put(music, lp(x, 0.2), at, g)
THEME = [72, 76, 79, 76, 74, 71, 67, None, 72, 76, 79, 84, 83, 79, 74, None]   # bouncy 8th-note line (original)
BASS = [48, 55, 47, 55, 45, 52, 43, 50]
def playful(at, dur, transpose=0, g=1.0):
    k, t = 0, 0.0
    while t < dur - 0.05:
        if k % 2 == 0: pluck(BASS[(k // 2) % 8] + transpose - 12, at + t, 0.5, 0.3 * g)
        m = THEME[k % 16]
        if m is not None: pluck(m + transpose, at + t, 0.35, 0.16 * g)
        if k % 8 == 0: bell(m + transpose + 12 if m else 84, at + t, 0.05 * g)
        k += 1; t += Q / 2
B = BEAT
drone(S["b1"], 1.3, 36, 0.06); tremolo(S["b1"], 1.3, [60, 63, 66], 0.03)
playful(S["b1"] + 1.9, B["b1"]["dur"] - 1.9 + B["b2"]["dur"] + B["b3"]["dur"] + B["b4"]["dur"] + B["b5"]["dur"] + B["b6"]["dur"])
drone(S["b7"], B["b7"]["dur"] + 0.2, 33, 0.07); tremolo(S["b7"] + 0.5, B["b7"]["dur"] - 0.4, [57, 60, 63], 0.035)
playful(S["b10"] + 0.2, B["b10"]["dur"] - 1.4, -5, 0.7)                     # curious, lower
playful(S["b11"], B["b11"]["dur"] + B["b12"]["dur"] - 2.4, 0, 0.8)
for i, m in enumerate([72, 76, 79, 84]): pluck(m, S["b13"] + 0.3 + i * Q / 2, 0.5, 0.22); bell(m + 12, S["b13"] + 0.3 + i * Q / 2, 0.05)
pluck(48, S["b13"] + 0.3 + 2 * Q, 1.2, 0.35); bell(96, S["b13"] + 0.3 + 2 * Q, 0.08)

def save(name, x, peak=None):
    p = peak or max(1e-9, np.abs(x).max())
    w = wave.open(name, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x / p * 0.95, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

music = music[: int(SR * DUR)]; sfx = sfx[: int(SR * DUR)]
voice = np.zeros_like(music)
if "--voice" in sys.argv:  # narration later: one wav per beat, placed at the beat start, music ducked under it
    vd = sys.argv[sys.argv.index("--voice") + 1]
    for b in TL:
        p = os.path.join(vd, b["id"] + ".wav")
        if os.path.exists(p):
            w = wave.open(p); v = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
            i = int((b["start"] + 0.12) * SR); voice[i:i + len(v)] += v[: len(voice) - i]
    envv = np.convolve(np.abs(voice), np.ones(int(0.15 * SR)) / int(0.15 * SR), "same")
    music *= 1 - 0.6 * np.clip(envv / (envv.max() + 1e-9) * 6, 0, 1)
save("music.wav", music); save("sfx.wav", sfx)
mix = 0.55 * music / (np.abs(music).max() + 1e-9) + 0.9 * sfx / (np.abs(sfx).max() + 1e-9) + (voice * 1.3 if voice.any() else 0)
mix = np.tanh(mix * 1.1) / 1.1
save("mix_voice.wav" if voice.any() else "mix_novoice.wav", mix)
print("audio", round(DUR, 2), "s")
