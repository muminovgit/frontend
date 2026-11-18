"""Render narrator lines with Silero v4_uz (speaker 'dilnavoz') using SSML pauses.
usage: python3 -I silero_lines.py <model.pt> <lines.json> <out_dir>"""
import sys, json, wave, re
import torch
from xml.sax.saxutils import escape

model_path, lines_path, out_dir = sys.argv[1:4]
m = torch.package.PackageImporter(model_path).load_pickle("tts_models", "model")
lines = json.load(open(lines_path))

def to_ssml(text, rate="medium", pitch="medium"):
    parts = re.split(r"\.\.\.", text)
    body = '<break time="380ms"/>'.join(escape(p.strip()) for p in parts)
    body = body.replace(". ", '. <break time="180ms"/>')
    return f'<speak><prosody rate="{rate}" pitch="{pitch}">{body}</prosody></speak>'

for entry in lines:
    lid, text = entry[0], entry[1]
    rate, pitch = (entry[2], entry[3]) if len(entry) > 3 else ("medium", "medium")
    a = m.apply_tts(ssml_text=to_ssml(text, rate, pitch), speaker="dilnavoz", sample_rate=48000)
    x = (a.numpy() * 32767).astype("int16")
    with wave.open(f"{out_dir}/sil_{lid}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(x.tobytes())
    print(lid, round(len(x) / 48000, 2))
