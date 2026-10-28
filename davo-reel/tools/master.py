# Iterate the score's master gain until the AAC-encoded film reads -14.0 LUFS (+-0.1) with true peak <= -2 dBTP.
import subprocess, sys, re
VID, OUT = sys.argv[1], sys.argv[2]
def measure(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); P = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)[-1]); return I, P
g = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
for it in range(10):
    subprocess.run(["python3", "tools/score.py", str(g)], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", VID, "-i", "audio/score.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", OUT], check=True)
    I, P = measure(OUT); print(f"gain {g:+.2f} dB -> {I} LUFS, true peak {P} dBTP")
    if abs(I + 14.0) <= 0.1 and P <= -1.0: break
    g += (-14.0 - I) * 1.8   # limiter compresses the response, so overshoot the step
