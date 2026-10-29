# python3 review.py film.mp4 outdir [fps=60] [name:start:end ...]
# 1) single-frame pop scan (a frame unlike BOTH neighbours while the neighbours match) 2) frame-by-frame contact sheets.
import sys, subprocess, numpy as np, os
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
fps = float(sys.argv[3]) if len(sys.argv) > 3 else 60
w, h = 120, 213
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32); d = lambda a, b: np.abs(F[a] - F[b]).mean()
pops = [(i, round(i / fps, 3)) for i in range(1, len(F) - 1) if min(d(i - 1, i), d(i, i + 1)) > 3 and d(i - 1, i + 1) < 0.35 * min(d(i - 1, i), d(i, i + 1))]
print("frames", len(F), "single-frame pops:", pops or "none")
for spec in sys.argv[4:]:
    name, a, b = spec.split(":"); a, b = float(a), float(b); n = int((b - a) * fps); cols = 10; rows = (n + cols - 1) // cols
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-t", str(b - a), "-i", src, "-vf", f"scale=180:-2,tile={cols}x{rows}",
                    "-frames:v", "1", "-update", "1", f"{out}/{name}.png"]); print("sheet", f"{out}/{name}.png")
