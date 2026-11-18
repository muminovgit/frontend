import numpy as np, wave, json, subprocess, os, sys
D = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(f"{D}/timeline.json")); EV = json.loads(sys.argv[1])
SR = 44100; TOTAL = TL["total"]; N = int(SR * TOTAL) + SR
S = {k: v for k, v in TL["scenes"].items()}; L = {l["id"]: l for l in TL["lines"]}
rng = np.random.default_rng(3); T = np.arange(N) / SR

def readwav(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768

def writewav(p, x):
    x = np.clip(x, -1, 1)
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())

def add(buf, sig, t, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if 0 <= i < N: buf[i:j] += g * sig[: j - i]

# ---------- voice track
FX = {"N": "acompressor=threshold=-20dB:ratio=3:attack=5:release=80,equalizer=f=120:t=q:w=1:g=3,aecho=0.8:0.5:35:0.12",
      "OLD": "equalizer=f=150:t=q:w=1:g=2,aecho=0.8:0.6:45:0.18",
      "STR": "highpass=f=320,lowpass=f=3200,acompressor=threshold=-18dB:ratio=4,volume=1.3"}
voice = np.zeros(N)
for l in TL["lines"]:
    src = f"{D}/v_{l['id']}.wav"; fx = f"{D}/fx_{l['id']}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", FX[l["voice"]], "-ar", str(SR), "-ac", "1", fx], check=True)
    add(voice, readwav(fx), l["start"], 1.0)
writewav(f"{D}/voice.wav", voice / max(1e-6, np.abs(voice).max()) * 0.95)

# ---------- music & sfx
out = np.zeros(N)
def seg(t0, t1, a=0.8):
    e = np.zeros(N); i0, i1 = int(t0 * SR), min(N, int(t1 * SR)); n = i1 - i0; r = min(int(a * SR), n // 2)
    s = np.ones(n); s[:r] = np.linspace(0, 1, r); s[-r:] = np.linspace(1, 0, r); e[i0:i1] = s; return e
def tone(f, d, dec=3.0):
    t = np.arange(int(SR * d)) / SR; return np.sin(2 * np.pi * f * t) * np.exp(-t * dec)
def noise(d, dec):
    t = np.arange(int(SR * d)) / SR; return rng.uniform(-1, 1, len(t)) * np.exp(-t * dec)
def lp(x, k=8): return np.convolve(x, np.ones(k) / k, mode="same")
def impact(d=2.0):
    t = np.arange(int(SR * d)) / SR; f = 35 + 90 * np.exp(-t * 10)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8) + 0.3 * lp(noise(d, 6), 20)
def heartbeat(t0, t1, bpm=72, g=0.8):
    t = t0
    while t < t1:
        add(out, tone(50, 0.25, 14), t, g); add(out, tone(46, 0.25, 16), t + 0.22, g * 0.7); t += 60 / bpm
def riser(d):
    t = np.arange(int(SR * d)) / SR
    return (t / d) ** 2 * (0.5 * lp(rng.uniform(-1, 1, len(t)), 3) + 0.3 * np.sin(2 * np.pi * np.cumsum(150 + 900 * (t / d) ** 2) / SR))

drone = (0.08 * np.sin(2 * np.pi * 55 * T) + 0.06 * np.sin(2 * np.pi * 82.4 * T) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * T))
         + 0.03 * np.sin(2 * np.pi * 164.8 * T) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * T)))
out += drone * (seg(0, S["S11"][0], 1.5) + 1.35 * seg(S["S12"][0], TOTAL, 1.5))
pad = 0.04 * (np.sin(2 * np.pi * 220 * T) + np.sin(2 * np.pi * 277.2 * T) + np.sin(2 * np.pi * 329.6 * T)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.2 * T))
out += pad * seg(S["S3"][0], S["S7"][1], 1.5)
# pulsing tension bass from the fact card to the problem
pulse = 0.09 * np.sin(2 * np.pi * 41.2 * T) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 1.6 * T)))
out += lp(pulse, 30) * seg(S["S9"][0], S["S10"][1], 1.0)

heartbeat(0.15, S["S1"][1] - 0.1, 70, 0.9)
add(out, impact(), S["S2"][0], 1.0)
for k, f in enumerate([880, 1108.7, 1318.5, 1760]): add(out, tone(f, 2.5, 1.6), L["n9"]["start"] + k * 0.08, 0.14)
for k in range(28): add(out, lp(noise(0.03, 120), 2), S["S8"][0] + 0.3 + k * 0.072 + rng.uniform(0, .02), 0.25)
add(out, tone(1400, 0.15, 20), S["S9"][0], 0.25); add(out, impact(1.5), S["S9"][0], 0.5)
for k in range(20): add(out, tone(2200 + k * 40, 0.03, 60), EV["cnt"] + k * 0.1, 0.13)
add(out, impact(), S["S10"][0], 0.6)
add(out, riser(1.6), S["S11"][0] - 1.6, 0.4)
add(out, impact(2.5), S["S11"][0] + 0.05, 1.2)
sh = EV["shutter"]; add(out, lp(noise(0.06, 60), 3), sh, 0.9); add(out, lp(noise(0.05, 70), 3), sh + 0.08, 0.6); add(out, impact(1.2), sh, 0.5)
v0 = S["S14"][0] + 0.2
for a, b in [(v0, v0 + 0.8), (v0 + 1.1, v0 + 1.7)]:
    t = np.arange(int(SR * (b - a))) / SR
    add(out, np.sign(np.sin(2 * np.pi * 160 * t)) * 0.15 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 12 * t))), a, 0.6)
for k in ["s1", "s2", "s3"]:
    a = L[k]["start"]; add(out, tone(988, 0.12, 25), a - 0.25, 0.3); add(out, tone(1318, 0.18, 18), a - 0.18, 0.3)
heartbeat(L["s3"]["start"], S["S15"][1] - 0.2, 96, 0.9)
add(out, riser(2.4), S["S16"][0] - 2.4, 0.45)
add(out, impact(2.5), S["S16"][0], 1.1)
t = S["S16"][0] + 0.5
while t < S["S16"][1] - 0.3: add(out, tone(55, 0.3, 8), t, 0.6); t += 0.5
add(out, impact(2.0), S["S17"][0], 0.8)
out = np.tanh(out * 1.3) * 0.9
writewav(f"{D}/sfx.wav", out)

# ---------- duck music under voice, mix, normalize
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{D}/sfx.wav", "-i", f"{D}/voice.wav", "-filter_complex",
    "[1]asplit=2[v][sc];[0][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[duck];"
    "[duck]volume=0.75[m];[m][v]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st=%.2f:d=1.2[o]" % (TOTAL - 1.2),
    "-map", "[o]", "-ar", str(SR), "-t", str(TOTAL), f"{D}/final_audio.wav"], check=True)
print("ok")
