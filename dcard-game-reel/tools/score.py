# Dcard game reel — generated score + SFX (numpy synthesis, no samples, no licence needed).
# Timing mirrors the T table in reel.html. usage: python3 tools/score.py [gain_db]  -> prints the WAV path.
import subprocess, sys, numpy as np, wave, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = dict(boot=0, hud=1.0, plate1=1.15, aim1=1.25, shot1=2.0, plate2=2.4, aim2=2.6, shot2=3.0, head1=3.35, head2=3.7, zoom=4.35,
         pad=4.7, b1=5.15, b2=5.65, b3=6.15, combo=6.6, padOut=7.25, phone=7.4, lock=7.7, scan=8.05, done=8.75, loot=8.85,
         pick1=9.15, pick2=9.4, phoneOut=10.35, win=10.5, band=10.55, mvp=11.0, winOut=12.55, logo=12.75, land=12.95,
         word=13.15, tag=13.5, cta=14.0, dur=16.0)
ROWS = [11.3, 11.55, 11.8]
SR = 48000; DUR = T["dur"]; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
def ts(d): return np.arange(int(d * SR)) / SR
def add(sig, t0, g=1.0, pan=0.0):
    i = int(round(t0 * SR)); j = min(N, i + len(sig))
    if j <= i or i >= N: return
    a = max(0, i); s = sig[a - i:j - i]
    L[a:j] += s * g * (1 - pan); R[a:j] += s * g * (1 + pan)
def lp(x, a):
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y
def hp(x, a): return x - lp(x, a)
def nf(m): return 440 * 2 ** ((m - 69) / 12)
def noise(d): return rng.standard_normal(int(d * SR))

# ---------------------------------------------------------------- music: 140 BPM dark trap, F minor
BPM = 140; beat = 60 / BPM; bar = 4 * beat
prog = [[53, 56, 60, 65], [49, 53, 56, 61], [56, 60, 63, 68], [51, 55, 58, 63]]   # Fm Db Ab Eb
roots = [41, 37, 44, 39]
for b in range(int(DUR / bar) + 1):
    ch = prog[b % 4]; t0 = b * bar; t = ts(bar + 0.4)
    env = np.minimum(1, t / 0.15) * np.exp(-t * 0.4)
    pad = sum(np.sign(np.sin(2 * np.pi * nf(m) * t)) * 0.3 + np.sin(2 * np.pi * nf(m) * 1.004 * t) for m in ch) / len(ch)
    add(lp(pad * env, 0.05) * 0.075, t0)
# sections where the beat plays (it drops out for zooms/tension and slams back on the hit)
drum_windows = [(T["hud"], T["zoom"]), (T["pad"], T["padOut"] + 0.1), (T["done"], T["phoneOut"]), (T["band"], T["winOut"]), (T["land"], DUR - 0.9)]
def in_drums(t): return any(a <= t < b - 1e-6 for a, b in drum_windows)
def kick808(t0, root, g=0.75, d=0.55):
    t = ts(d); f = nf(root) * (1 + 2.5 * np.exp(-t * 40))
    x = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 4.5); add(x * g, t0)
def clap(t0, g=0.38):
    t = ts(0.25); x = hp(noise(0.25), 0.3); env = np.exp(-t * 22) * (1 + 0.7 * np.exp(-((t - 0.015) ** 2) / 2e-5)); add(x * env * g, t0)
def hat(t0, g=0.07, pan=0.3):
    t = ts(0.04); add(hp(noise(0.04), 0.7) * np.exp(-t * 110) * g, t0, pan=pan)
def crash(t0, g=0.22):
    t = ts(1.6); add(hp(noise(1.6), 0.4) * np.exp(-t * 2.8) * g, t0)
for a, e in drum_windows:
    k = 0
    while True:
        tb = a + k * beat / 2
        if tb >= e - 1e-6: break
        bi = int((tb) // bar) % 4; pos = k % 8
        if pos in (0, 3, 5): kick808(tb, roots[bi] - 12 + 24, 0.7)
        if pos in (2, 6): clap(tb)
        hat(tb, 0.06, 0.25); hat(tb + beat / 4, 0.045, -0.25)
        if pos == 7:   # 1/32 roll into the next bar
            for r in range(4): hat(tb + beat / 4 + r * beat / 8, 0.04 + 0.01 * r, 0.1)
        k += 1
    if a > 0.5: crash(a, 0.25)
# tension bed while the QR is scanned: hats + ticking sub pulse, no kick/clap (the beat drops back on "done")
tb = T["phone"]
while tb < T["done"] - 1e-6:
    hat(tb, 0.05, 0.3); hat(tb + beat / 4, 0.035, -0.3)
    tt = ts(0.18); add(np.sin(2 * np.pi * nf(29) * tt) * np.exp(-tt * 10) * 0.35, tb)
    tb += beat / 2
# pluck arpeggio on the busy sections
def pluck(t0, m, g=0.09, pan=0.0):
    t = ts(0.3); x = (2 * ((nf(m) * t) % 1) - 1) * np.exp(-t * 12); add(lp(x, 0.25) * g, t0, pan=pan)
for a, e in [(T["pad"], T["padOut"]), (T["done"], T["phoneOut"]), (T["band"], T["winOut"]), (T["land"], DUR - 1.2)]:
    k = 0
    while a + k * beat / 4 < e - 1e-6:
        tb = a + k * beat / 4; ch = prog[int(tb // bar) % 4]; pluck(tb, ch[[0, 2, 1, 3, 2, 1, 3, 0][k % 8]] + 12, 0.07, 0.3 if k % 2 else -0.3); k += 1

# ---------------------------------------------------------------- SFX
def whoosh(tp, d=0.35, g=0.22, pan=0.0):   # peaks at tp
    t = ts(d); a = np.linspace(0.02, 0.45, len(t)); x = noise(d); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a[i] * (v - s); y[i] = s
    add(y * np.sin(np.pi * t / d) ** 2 * g * 2.4, tp - d * 0.65, pan=pan)
def riser(t0, t1, g=0.14):
    d = t1 - t0; t = ts(d); f = 300 + 2400 * (t / d) ** 2
    x = hp(noise(d), 0.15) * (t / d) ** 2 * 0.8 + np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 3 * 0.25; add(x * g, t0)
def subhit(t0, g=0.95):
    t = ts(2.0); f = 60 * np.exp(-t * 2.5) + 33; add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * g, t0)
    add(lp(noise(0.5), 0.12) * np.exp(-ts(0.5) * 8) * 0.45, t0)
def thud(t0, g=0.6):
    t = ts(0.3); f = 95 * np.exp(-t * 18) + 48; add((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 13) + lp(noise(0.3), 0.3) * np.exp(-t * 55) * 0.6) * g, t0)
def gunshot(t0, g=0.85):
    t = ts(0.9); crack = hp(noise(0.9), 0.35) * np.exp(-t * 55)
    body = lp(noise(0.9), 0.08) * np.exp(-t * 14) * 2.2
    punch = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t * 30) + 45) / SR) * np.exp(-t * 16)
    tail = lp(noise(0.9), 0.04) * np.exp(-t * 4) * 0.9
    x = np.tanh((crack * 1.4 + body + punch * 1.2 + tail) * 1.6); add(x * g, t0, pan=0.12)
    add(hp(noise(0.03), 0.6) * np.exp(-ts(0.03) * 150) * 0.3, t0 + 0.09, pan=0.3)   # bolt
def hitmarker(t0, g=0.3):
    t = ts(0.06); add(np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 80) * g, t0); add(np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 80) * g * 0.7, t0 + 0.012)
def shatter(t0, g=0.3):
    for i in range(22):
        tt = ts(0.25); f = 2800 + rng.random() * 5000
        add(np.sin(2 * np.pi * f * tt) * np.exp(-tt * (30 + rng.random() * 40)) * g * (0.4 + rng.random() * 0.6), t0 + rng.random() * 0.35 * (i / 22) ** 0.7, pan=rng.random() * 0.8 - 0.4)
    add(hp(noise(0.4), 0.3) * np.exp(-ts(0.4) * 12) * g * 0.8, t0)
def casing(t0):
    for i, dt in enumerate([0, 0.13, 0.21, 0.27]):
        tt = ts(0.15); add((np.sin(2 * np.pi * 4100 * tt) + 0.6 * np.sin(2 * np.pi * 6230 * tt)) * np.exp(-tt * 40) * 0.07 / (1 + i), t0 + dt, pan=0.5)
def clank(t0, g=0.2):
    t = ts(0.5); x = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(420, 1), (1130, 0.6), (1870, 0.4), (2950, 0.3)]) * np.exp(-t * 9); add(x * g / 2, t0, pan=-0.2)
def blip(t0, f, g=0.18, d=0.12, pan=0.0):
    t = ts(d); add(np.sign(np.sin(2 * np.pi * f * t)) * 0.4 * np.exp(-t * 30) * g + np.sin(2 * np.pi * f * t) * np.exp(-t * 25) * g, t0, pan=pan)
def glitch(t0, d=0.25, g=0.18):
    t = ts(d); x = noise(d); hold = np.repeat(x[::120], 120)[:len(t)]
    gate = (np.sin(2 * np.pi * 37 * t) > 0).astype(float); add(np.round(hold * 3) / 3 * gate * np.exp(-t * 6) * g, t0)
def chime(t0, notes, g=0.16, step=0.06):
    for i, m in enumerate(notes):
        tt = ts(0.8); add((np.sin(2 * np.pi * nf(m) * tt) + 0.3 * np.sin(2 * np.pi * nf(m) * 2 * tt)) * np.exp(-tt * 5) * g, t0 + i * step, pan=(i % 2 - 0.5) * 0.4)
def coin(t0, g=0.12, pan=0.0):
    t = ts(0.35); x = (np.sin(2 * np.pi * 1975 * t) * (t < 0.06) + np.sin(2 * np.pi * 2637 * t) * (t >= 0.06)) * np.exp(-t * 12); add(x * g, t0, pan=pan)
def click(t0, g=0.25):
    t = ts(0.03); add(hp(noise(0.03), 0.5) * np.exp(-t * 200) * g, t0)
def hum(t0, t1, g=0.08):
    d = t1 - t0; t = ts(d); f = 600 + 500 * np.abs(np.sin(np.pi * t / (d / 2)))
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.05) * g, t0)

# S0 boot: match found
glitch(0.0, 0.3, 0.2); chime(0.05, [77, 84], 0.12, 0.09)
for i in range(5): blip(0.18 + i * 0.08, 900 + i * 120, 0.06)
click(0.6, 0.4); blip(0.6, 1760, 0.2); riser(0.55, 1.0, 0.16); whoosh(1.0, 0.4, 0.25)
subhit(T["hud"], 0.8)
# S1 FPS
clank(T["plate1"] + 0.08); clank(T["plate2"] + 0.08, 0.16)
whoosh(T["aim1"] + 0.35, 0.4, 0.08, pan=0.3); whoosh(T["aim2"] + 0.15, 0.2, 0.12, pan=-0.3)
for s in (T["shot1"], T["shot2"]):
    gunshot(s); hitmarker(s + 0.03); shatter(s + 0.03); casing(s + 0.35)
for f in (T["shot1"] + 0.08, T["shot2"] + 0.08): blip(f, 1320, 0.1, pan=0.4); blip(f + 0.05, 1760, 0.08, pan=0.4)
thud(T["head1"] + 0.05); thud(T["head1"] + 0.13)
subhit(T["head2"], 0.6); glitch(T["head2"], 0.2, 0.15); glitch(T["head2"] + 0.5, 0.06, 0.12)
riser(T["zoom"] - 0.35, T["zoom"] + 0.33, 0.18); whoosh(T["zoom"] + 0.33, 0.45, 0.3)
subhit(T["pad"], 0.85)
# S2 gamepad combo
for t0, m in zip((T["b1"], T["b2"], T["b3"]), (72, 76, 79)):
    click(t0, 0.35); blip(t0, nf(m), 0.18); thud(t0 + 0.01, 0.35)
subhit(T["combo"], 0.7); chime(T["combo"], [65, 72, 77, 84], 0.13, 0.03); glitch(T["combo"], 0.15, 0.12)
whoosh(T["padOut"] + 0.1, 0.3, 0.3, pan=-0.4)
# S3 phone
whoosh(T["phone"] + 0.15, 0.4, 0.2, pan=0.4); blip(T["phone"] + 0.12, 880, 0.1)
for i in range(3): blip(T["lock"] + i * 0.11, 1568, 0.1, 0.07)
blip(T["lock"] + 0.35, 2093, 0.12, 0.15)
hum(T["scan"], T["done"] - 0.03, 0.07)
subhit(T["done"], 0.7); chime(T["done"], [72, 76, 79, 84], 0.16, 0.05)
for i in range(16): coin(T["loot"] + 0.04 * i + rng.random() * 0.05 + (i // 6) * 0.25, 0.08, pan=rng.random() * 0.8 - 0.4)
blip(T["pick1"], 1046, 0.12); blip(T["pick1"] + 0.06, 1568, 0.1); coin(T["pick2"], 0.14); blip(T["pick2"] + 0.06, 1760, 0.08)
whoosh(T["phoneOut"] + 0.15, 0.3, 0.25)
# S4 round win
whoosh(T["band"] + 0.2, 0.35, 0.3, pan=-0.3); subhit(T["band"] + 0.08, 0.8); chime(T["band"] + 0.08, [65, 69, 72, 77], 0.14, 0.04)
whoosh(T["mvp"] + 0.25, 0.3, 0.16)
for r in ROWS: click(r, 0.25); blip(r + 0.1, 1568, 0.1); blip(r + 0.14, 2093, 0.08)
# S5 logo level up
whoosh(T["winOut"] + 0.2, 0.3, 0.2); riser(T["logo"] - 0.1, T["land"], 0.14)
subhit(T["land"], 1.0); crash(T["land"], 0.28); chime(T["land"] + 0.05, [65, 69, 72, 77, 81, 84], 0.14, 0.05)
whoosh(T["word"] + 0.25, 0.35, 0.15, pan=0.3); blip(T["cta"] + 0.02, 1046, 0.14); blip(T["cta"] + 0.07, 1568, 0.12)
for i in range(6): blip(T["cta"] + 0.5 + i * 0.06, 2093 + i * 220, 0.03, pan=0.3)

# ---------------------------------------------------------------- master
# voiceover: uz-UZ Madina, energetic preset (+12%, +18Hz, bright EQ); lines in audio/vo/lines.txt. Music ducks ~8 dB under it.
def loadw(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2).astype(np.float64) / 32768
VO = [(0, 0.15), (1, T["head1"] + 0.1), (2, T["b1"] + 0.02), (3, T["b2"] + 0.02), (4, T["b3"] + 0.02), (5, T["phone"] + 0.25), (6, T["band"] + 0.12), (7, T["tag"] + 0.05)]
vL = np.zeros(N); vR = np.zeros(N)
if "--no-vo" not in sys.argv and os.path.exists(os.path.join(ROOT, "audio/vo/v0.wav")):
    for i, t0 in VO:
        x = loadw(os.path.join(ROOT, f"audio/vo/v{i}.wav")); x = x / np.abs(x).max() * 0.9
        a = int(t0 * SR); b = min(N, a + len(x)); vL[a:b] += x[:b - a, 0]; vR[a:b] += x[:b - a, 1]
env = np.abs(vL) + np.abs(vR); k = int(0.12 * SR); env = np.convolve(env, np.ones(k) / k, "same"); env = np.convolve(env, np.ones(k) / k, "same")
duck = 1 - 0.62 * np.clip(env / (env.max() * 0.25 + 1e-9), 0, 1)
m = np.abs(np.stack([L, R], 1)).max(); L = L / m * 0.55 * duck + vL; R = R / m * 0.55 * duck + vR
mix = np.stack([L, R], 1)
fo = int(0.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * 0.9
os.makedirs(os.path.join(ROOT, "audio"), exist_ok=True)
pre = os.path.join(ROOT, "audio/premaster.wav"); out = os.path.join(ROOT, "audio/score.wav")
with wave.open(pre, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
args = [x for x in sys.argv[1:] if not x.startswith("--")]
gain = float(args[0]) if args else 0.0
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", pre, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
af = f"volume={-14.0 - I + gain:.2f}dB,aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=0,aresample=48000"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), out], check=True)
os.remove(pre); print(out)
