# Make the separately recorded tagline sound like the street takes: match its long-term spectrum to the street
# speech (STFT EQ, ±10 dB, 1/3-octave smoothed) and lay the street's own noise floor under it.
# The result is inserted into voice_raw.wav, so the whole voice then goes through one processing chain.
# usage: python3 match_tag.py  (needs timeline.js 'tag')
import json, os, subprocess, numpy as np, wave
HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000; N = 2048; HOP = 512
TL = json.loads(open(os.path.join(HERE, 'timeline.js')).read()[len('window.TL='):-1])
def load(path, ss=None, to=None):
    cmd = ['ffmpeg', '-nostdin', '-loglevel', 'error'] + (['-ss', str(ss)] if ss is not None else []) + ['-i', path] + (['-t', str(to)] if to else []) + ['-ac', '1', '-ar', str(SR), '-f', 's16le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.int16).astype(np.float64) / 32768
def stft(x):
    w = np.hanning(N); n = 1 + (len(x) - N) // HOP
    return np.stack([np.fft.rfft(x[i * HOP:i * HOP + N] * w) for i in range(n)])
def istft(S, L):
    w = np.hanning(N); M = max(L, len(S) * HOP) + N; y = np.zeros(M); z = np.zeros(M)
    for i, f in enumerate(S): y[i * HOP:i * HOP + N] += np.fft.irfft(f) * w; z[i * HOP:i * HOP + N] += w * w
    return (y / np.maximum(z, 1e-6))[:L]
street = load(os.path.join(HERE, 'voice_raw.wav'), 0, TL['segs'][-1]['t1'])
tag = load(os.path.join(HERE, 'tag_dorixona_uyingizda.ogg'), 0.0)   # full line: 'Davo Delivery, dorixona uyingizda'
Ss, St = stft(street), stft(tag)
es, et = (np.abs(Ss) ** 2).sum(1), (np.abs(St) ** 2).sum(1)
voiced_s, quiet_s, voiced_t = es > np.percentile(es, 55), es < np.percentile(es, 8), et > np.percentile(et, 40)
ltas_s = (np.abs(Ss[voiced_s]) ** 2).mean(0); ltas_t = (np.abs(St[voiced_t]) ** 2).mean(0)
f = np.fft.rfftfreq(N, 1 / SR)
def smooth(p):   # 1/3-octave smoothing
    out = np.empty_like(p)
    for i, fi in enumerate(f):
        lo, hi = fi / 2 ** (1 / 6), fi * 2 ** (1 / 6); m = (f >= lo) & (f <= hi); out[i] = p[m].mean() if m.any() else p[i]
    return out
corr = np.sqrt(smooth(ltas_s) / np.maximum(smooth(ltas_t), 1e-12))
corr /= np.median(corr[(f > 300) & (f < 3000)])
corr = np.clip(corr, 10 ** (-10 / 20), 10 ** (10 / 20)); corr[f < 60] = corr[f >= 60][0]
y = istft(St * corr[None, :], len(tag))
# street noise floor: spectrum of the quietest street frames, random phase
nmag = np.sqrt((np.abs(Ss[quiet_s]) ** 2).mean(0)); rng = np.random.default_rng(3)
noise = istft(np.stack([nmag * np.exp(2j * np.pi * rng.random(len(f))) for _ in range(len(St) + 4)]), len(tag) + N * 2)[:len(tag)]
# level: match the tagline's voiced RMS to the street's voiced RMS (pre-chain), keep the noise at the street's own level
def vrms(x, mask):
    m = np.zeros(len(x), bool); r = np.repeat(mask, HOP)[:len(x)]; m[:len(r)] = r
    return np.sqrt(np.mean(x[m] ** 2))
vs, vt = vrms(street, voiced_s), vrms(y, voiced_t); y *= vs / max(vt, 1e-9)
fade = np.minimum(1, np.minimum(np.arange(len(y)) / (.03 * SR), (len(y) - np.arange(len(y))) / (.06 * SR)))
y = y * fade + noise
# insert into voice_raw at TL.tag (+ a little street noise bridging the gap before it)
raw = load(os.path.join(HERE, 'voice_raw.wav')); i0 = int((TL.get('tag') or 0) * SR)
# continuous street room tone under the whole voice track: the noise floor no longer jumps at cuts / between takes
bed = istft(np.stack([nmag * np.exp(2j * np.pi * rng.random(len(f))) for _ in range(len(raw) // HOP + 8)]), len(raw))[:len(raw)]
raw += bed * .7
if TL.get('tag') is not None: raw[i0:i0 + len(y)] += y[:len(raw) - i0]
with wave.open(os.path.join(HERE, 'voice_raw_tag.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(raw, -1, 1) * 32767).astype('<i2').tobytes())
print('eq range dB', round(20 * np.log10(corr.min()), 1), round(20 * np.log10(corr.max()), 1), 'level x', round(vs / max(vt, 1e-9), 2))
