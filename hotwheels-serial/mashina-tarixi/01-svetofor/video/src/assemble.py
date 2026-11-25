"""Join the rendered beat frames in timeline order and mux the audio.
usage: python3 assemble.py <audio.wav> <out.mp4>"""
import os, sys, subprocess, shutil
from beats import timeline

audio, out = sys.argv[1], sys.argv[2]
seq = "seq"; shutil.rmtree(seq, ignore_errors=True); os.makedirs(seq)
k = 0
for b in timeline():
    for f in range(b["frames"]):
        src = os.path.abspath(f"{os.environ.get('FRAMES', 'frames')}/{b['id']}_{f:04d}.png")
        if not os.path.exists(src): sys.exit(f"missing {src}")
        os.symlink(src, f"{seq}/{k:05d}.png"); k += 1
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", f"{seq}/%05d.png", "-i", audio,
                "-map", "0:v", "-map", "1:a", "-af", "loudnorm=I=-14:TP=-1.5", "-ar", "48000",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", out], check=True)
print("ok", k, "frames ->", out)
