import numpy as np, wave
SR = 48000; T = 8.0; N = int(SR * T); rng = np.random.default_rng(7)
t = np.arange(N) / SR; out = np.zeros(N)
def rd(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
def put(x, at, g=1.0):
    i = int(at * SR); j = min(N, i + len(x)); out[i:j] += g * x[:j - i]
def env(n, a, d):  # attack/decay envelope
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); e *= np.exp(-np.arange(n) / (d * SR)); return e
def lp(x, k):  # simple one-pole lowpass
    y = np.zeros_like(x); a = k
    for i in range(1, len(x)): y[i] = y[i - 1] + a * (x[i] - y[i - 1])
    return y
# night ambience: low drone + soft wind, ducked under the voice
voice_spans = [(0.4, 2.1), (2.3, 3.5), (4.05, 5.0)]
duck = np.ones(N)
for a, b in voice_spans: duck[int(a * SR):int(b * SR)] = 0.55
drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t) + 0.25 * np.sin(2 * np.pi * 110 * t)) * 0.035
drone *= np.clip(t / 1.0, 0, 1) * np.where(t < 3.9, 1 + 0.8 * np.clip((t - 2.2) / 1.7, 0, 1), 0.6)
out += drone * duck
out += lp(rng.standard_normal(N), 0.02) * 0.05 * duck
# hooves on cobbles (stop at the blast)
k = 0
for at in np.arange(0.15, 3.85, 0.26):
    n = int(0.06 * SR); x = rng.standard_normal(n) * env(n, 0.002, 0.012); x = lp(x, 0.35) * 0.9
    put(x + 0.4 * np.sin(2 * np.pi * (900 + 200 * (k % 2)) * np.arange(n) / SR) * env(n, 0.001, 0.01), at, 0.45); k += 1
# signal: lever clunk + semaphore arms clack + gas-lamp ding
for at, f in ((1.35, 180), (1.55, 260), (1.75, 220)):
    n = int(0.12 * SR); x = (np.sin(2 * np.pi * f * np.arange(n) / SR) + 0.6 * rng.standard_normal(n)) * env(n, 0.001, 0.03); put(x, at, 0.35)
n = int(1.2 * SR); put(np.sin(2 * np.pi * 1320 * np.arange(n) / SR) * env(n, 0.002, 0.35) * 0.18, 1.8)
# gas hiss, swelling until the blast
a, b = 2.15, 3.9; n = int((b - a) * SR)
hiss = rng.standard_normal(n) - lp(rng.standard_normal(n), 0.05)
hiss *= np.linspace(0.02, 0.22, n) * (1 + 0.3 * np.sin(2 * np.pi * 7 * np.arange(n) / SR)); put(hiss, a)
# explosion: low boom + noise burst + crackles, then falling debris and glass
n = int(2.5 * SR); tt = np.arange(n) / SR
boom = np.sin(2 * np.pi * (70 * np.exp(-tt * 3) + 32) * tt) * env(n, 0.003, 0.45) * 1.0
burst = lp(rng.standard_normal(n), 0.25) * env(n, 0.001, 0.18) * 1.1
crack = (rng.random(n) > 0.9985) * rng.standard_normal(n) * 3 * env(n, 0.05, 0.6)
put(boom + burst + crack, 3.9, 1.0)
for i in range(9):
    at = 4.15 + i * 0.07 + rng.random() * 0.05; m = int(0.25 * SR)
    put(np.sin(2 * np.pi * rng.uniform(2500, 5200) * np.arange(m) / SR) * env(m, 0.001, 0.05) * 0.12, at)
for i in range(5):
    m = int(0.08 * SR); put(lp(rng.standard_normal(m), 0.4) * env(m, 0.001, 0.02) * 0.5, 4.6 + i * 0.18 + rng.random() * 0.1)
# comic dizzy tweet after the blast (sooty policeman)
m = int(1.4 * SR); tt = np.arange(m) / SR
put(np.sin(2 * np.pi * (1800 + 400 * np.sin(2 * np.pi * 6 * tt)) * tt) * env(m, 0.05, 0.6) * 0.08, 5.3)
# voice
put(rd('v1.wav'), 0.4, 1.0); put(rd('v2.wav'), 2.3, 1.0); put(rd('v3.wav'), 4.05, 1.15)
out = np.tanh(out * 1.1) / 1.1
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out / max(1e-9, np.abs(out).max()) * 0.95 * 32767).astype(np.int16).tobytes())
print("ok")
