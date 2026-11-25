"""Shrink pauses longer than 0.5 s (quieter than peak - 28 dB) to 0.28 s, with 15 ms crossfades. Speech is untouched."""
import wave, sys, numpy as np, os
src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
for i in range(1, 14):
    w = wave.open(f"{src}/b{i}.wav"); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    hop = int(0.02 * sr); n = len(x) // hop
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[k*hop:(k+1)*hop] ** 2)) + 1e-9) for k in range(n)])
    quiet = db < db.max() - 28
    out, k, pos = [], 0, 0
    keep_frames, min_frames = int(0.28 / 0.02), int(0.5 / 0.02)
    while k < n:
        if quiet[k]:
            j = k
            while j < n and quiet[j]: j += 1
            if j - k >= min_frames and k > 0 and j < n:   # interior long pause
                a = k * hop + (keep_frames // 2) * hop; b = j * hop - (keep_frames // 2) * hop
                out.append(x[pos:a]); pos = b
            k = j
        else: k += 1
    out.append(x[pos:])
    xf = int(0.015 * sr); y = out[0]
    for seg in out[1:]:
        if len(y) > xf and len(seg) > xf:
            r = np.linspace(0, 1, xf); y = np.concatenate([y[:-xf], y[-xf:] * (1 - r) + seg[:xf] * r, seg[xf:]])
        else: y = np.concatenate([y, seg])
    wo = wave.open(f"{dst}/b{i}.wav", "wb"); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(sr); wo.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); wo.close()
    print(f"b{i} {len(x)/sr:.2f} -> {len(y)/sr:.2f}")
