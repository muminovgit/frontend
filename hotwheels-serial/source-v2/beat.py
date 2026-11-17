import numpy as np, wave, sys
SR = 44100
BPM = 150
B = 60 / BPM
TOTAL = 21.6
DROP_START, DROP_END = 12.8, 14.0   # build-up gap
N = int(SR * TOTAL)
out = np.zeros(N)
rng = np.random.default_rng(7)

def add(sig, t, gain=1.0):
    i = int(t * SR)
    j = min(N, i + len(sig))
    if i < N:
        out[i:j] += gain * sig[: j - i]

def kick(d=0.35):
    t = np.arange(int(SR * d)) / SR
    f = 45 + 110 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)

def snare(d=0.22):
    t = np.arange(int(SR * d)) / SR
    n = rng.uniform(-1, 1, len(t))
    n = n - np.concatenate([[0], n[:-1]]) * 0.6
    return (0.8 * n * np.exp(-t * 18) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25))

def hat(d=0.05):
    t = np.arange(int(SR * d)) / SR
    n = rng.uniform(-1, 1, len(t))
    n = n - np.concatenate([[0], n[:-1]])
    return n * np.exp(-t * 90)

def impact(d=1.6):
    t = np.arange(int(SR * d)) / SR
    f = 38 + 80 * np.exp(-t * 12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    n = rng.uniform(-1, 1, len(t))
    return np.sin(ph) * np.exp(-t * 2.2) + 0.35 * n * np.exp(-t * 7)

def riser(d):
    t = np.arange(int(SR * d)) / SR
    n = rng.uniform(-1, 1, len(t))
    # crude rising filter: mix of differentiated noise increasing
    hp = n - np.concatenate([[0], n[:-1]])
    env = (t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(200 + 1400 * (t / d) ** 2) / SR)
    return env * (0.5 * hp + 0.25 * tone)

def bass(d, freq):
    t = np.arange(int(SR * d)) / SR
    s = np.sign(np.sin(2 * np.pi * freq * t)) * 0.5 + np.sin(2 * np.pi * freq * t)
    return s * np.exp(-t * 4) * 0.5

def beep(d=0.12, f=880):
    t = np.arange(int(SR * d)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 10)

# drag tree beeps (intro)
for k, tt in enumerate([0.0, 0.4, 0.8]):
    add(beep(0.15, 660), tt, 0.5)
add(beep(0.35, 1320), 1.2, 0.6)
add(impact(), 1.6, 0.9)

notes = [55, 55, 65.4, 49]  # A1 A1 C2 G1
beat = 0
t = 1.6
while t < TOTAL - 0.01:
    in_gap = DROP_START <= t < DROP_END
    if not in_gap:
        add(kick(), t, 0.95)
        if beat % 2 == 1:
            add(snare(), t, 0.55)
        add(hat(), t + B / 2, 0.22)
        add(hat(), t, 0.12)
        add(bass(B * 0.9, notes[(beat // 4) % 4]), t, 0.35)
    beat += 1
    t = round(t + B, 6)

add(riser(DROP_END - DROP_START), DROP_START, 0.7)
add(impact(), DROP_END, 1.1)
# scene-cut whooshes
for tt in [4.0, 6.4, 8.0, 9.6, 11.2, 16.0, 17.6]:
    add(riser(0.18)[::-1] * 0.6, tt - 0.02, 0.5)

# stopwatch ticks 8.0-9.6
for k in range(16):
    add(beep(0.03, 2400), 8.0 + k * 0.1, 0.15)

out = np.tanh(out * 1.2) * 0.85
fade = int(SR * 0.6)
out[-fade:] *= np.linspace(1, 0, fade)
pcm = (out * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
