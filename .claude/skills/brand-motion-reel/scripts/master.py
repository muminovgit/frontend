# Mux a soundtrack onto a silent/old video and iterate the master gain until the *AAC-encoded* file reads
# -14 LUFS (±0.1) with true peak <= the ceiling.  Loudness shifts after AAC, so always measure the final file.
# usage: python3 master.py <video.mp4> <out.mp4> <score_cmd> [start_gain_db] [tp_ceiling]
#   score_cmd: a shell command that takes the gain as its last argument and writes the score WAV path printed on
#   its final stdout line, e.g.  "python3 tools/score.py"  (score.py prints the path it wrote).
import subprocess, sys, re, shlex
vid, out, cmd = sys.argv[1], sys.argv[2], sys.argv[3]
g = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
ceiling = float(sys.argv[5]) if len(sys.argv) > 5 else -1.0
def measure(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1])
best = None
for it in range(8):
    wav = subprocess.run(shlex.split(cmd) + [str(g)], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", out], check=True)
    I, P = measure(out); print(f"gain {g:+.2f} dB -> {I} LUFS, true peak {P} dBTP")
    if abs(I + 14.0) <= 0.1 and P <= ceiling: break
    g += (-14.0 - I) * (1.8 if it else 1.0)   # the limiter compresses the response; overshoot later steps
