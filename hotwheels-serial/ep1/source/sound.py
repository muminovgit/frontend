import numpy as np, wave, sys
SR = 44100; TOTAL = 100.0; N = int(SR * TOTAL)
out = np.zeros(N); rng = np.random.default_rng(3)
T = np.arange(N) / SR

def add(sig, t, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if 0 <= i < N: out[i:j] += g * sig[: j - i]

def env_seg(t0, t1, a=0.8):
    e = np.zeros(N); i0, i1 = int(t0 * SR), int(t1 * SR)
    n = i1 - i0; ramp = int(a * SR)
    seg = np.ones(n); seg[:ramp] = np.linspace(0, 1, ramp); seg[-ramp:] = np.linspace(1, 0, ramp)
    e[i0:i1] = seg; return e

def tone(f, d, dec=3.0):
    t = np.arange(int(SR * d)) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * dec)

def noise(d, dec):
    t = np.arange(int(SR * d)) / SR
    return rng.uniform(-1, 1, len(t)) * np.exp(-t * dec)

def lp(x, k=8):
    return np.convolve(x, np.ones(k) / k, mode='same')

def impact(d=2.0):
    t = np.arange(int(SR * d)) / SR
    f = 35 + 90 * np.exp(-t * 10)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8) + 0.3 * lp(noise(d, 6), 20)

def heartbeat(t0, t1, bpm=72, g=0.8):
    t = t0
    while t < t1:
        add(tone(50, 0.25, 14), t, g); add(tone(46, 0.25, 16), t + 0.22, g * 0.7)
        t += 60 / bpm

def riser(d):
    t = np.arange(int(SR * d)) / SR
    return (t / d) ** 2 * (0.5 * lp(rng.uniform(-1, 1, len(t)), 3) + 0.3 * np.sin(2 * np.pi * np.cumsum(150 + 900 * (t / d) ** 2) / SR))

# --- ambient drone (whole video, darker in tense parts)
drone = (0.07 * np.sin(2 * np.pi * 55 * T) + 0.05 * np.sin(2 * np.pi * 82.4 * T) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * T))
         + 0.025 * np.sin(2 * np.pi * 164.8 * T) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * T)))
mask = env_seg(0, 56.4, 1.5) + env_seg(59.4, 99.5, 1.5) * 1.3
out += drone * mask
# warm pad for market/home scenes (major-ish)
pad = 0.035 * (np.sin(2 * np.pi * 220 * T) + np.sin(2 * np.pi * 277.2 * T) + np.sin(2 * np.pi * 329.6 * T)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.2 * T))
out += pad * env_seg(7.0, 31.5, 1.5)

heartbeat(0.2, 5.4, 70, 0.9)
add(impact(), 5.5, 1.0)                       # title
for k, f in enumerate([880, 1108.7, 1318.5, 1760]):  # magic shimmer at pink reveal
    add(tone(f, 2.5, 1.6), 34.2 + k * 0.08, 0.12)
for k in range(28):                           # typing
    add(lp(noise(0.03, 120), 2), 37.8 + k * 0.072 + rng.uniform(0, .02), 0.25)
add(tone(1400, 0.15, 20), 41.5, 0.25); add(impact(1.5), 41.5, 0.5)   # fact card
for k in range(20):                           # counter ticks
    add(tone(2200 + k * 40, 0.03, 60), 51.5 + k * 0.1, 0.12)
add(impact(), 50.5, 0.6)
add(riser(1.5), 55.0, 0.35)
add(impact(2.5), 56.6, 1.2)                   # "bitta muammo"
add(lp(noise(0.06, 60), 3), 65.3, 0.9); add(lp(noise(0.05, 70), 3), 65.38, 0.6)   # shutter
add(impact(1.2), 65.3, 0.5)
for a, b in [(68.3, 69.1), (69.4, 70.0)]:      # phone vibrate
    t = np.arange(int(SR * (b - a))) / SR
    add(np.sign(np.sin(2 * np.pi * 160 * t)) * 0.15 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 12 * t))), a, 0.6)
for a in [71.5, 74.5, 77.5]:                  # message pops
    add(tone(988, 0.12, 25), a, 0.3); add(tone(1318, 0.18, 18), a + 0.07, 0.3)
heartbeat(78.0, 85.3, 96, 0.9)
add(riser(2.5), 83.0, 0.45)
add(impact(2.5), 85.5, 1.1)                   # choice
t = 86.0                                      # pulse under choice
while t < 96.8:
    add(tone(55, 0.3, 8), t, 0.6); t += 0.5
add(impact(2.0), 97.0, 0.8)

out = np.tanh(out * 1.3) * 0.9
f = int(SR * 1.0); out[-f:] *= np.linspace(1, 0, f)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
