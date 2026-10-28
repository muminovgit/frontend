# python3 tools/review.py film.mp4 outdir : single-frame pop scan + frame-by-frame sheets of the fast moments
import sys, subprocess, numpy as np, os
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
w, h = 108, 192
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32); d = lambda a, b: np.abs(F[a] - F[b]).mean()
pops = [(i, round(i / 60, 3)) for i in range(1, len(F) - 1) if min(d(i - 1, i), d(i, i + 1)) > 3 and d(i - 1, i + 1) < 0.35 * min(d(i - 1, i), d(i, i + 1))]
print("frames", len(F), "single-frame pops:", pops or "none")
for name, (a, b) in {"coin-flight": (3.50, 4.55), "dark-switch": (5.10, 5.70), "coin-rain": (7.90, 8.75), "reel": (8.75, 10.45), "logo": (12.25, 13.15)}.items():
    n = int((b - a) * 60); cols = 10; rows = (n + cols - 1) // cols
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a}", "-t", f"{b - a}", "-i", src, "-vf", f"scale=180:320,tile={cols}x{rows}", "-frames:v", "1", "-update", "1", f"{out}/{name}.png"])
    print("sheet", name)
