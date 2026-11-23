import time, wave, numpy as np, torch
from omnivoice import OmniVoice
torch.set_num_threads(4)
m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
lines = [("v1", "Dunyodagi birinchi svetofor..."), ("v2", "bir oy ham ishlamay..."), ("v3", "portlab ketgan!")]
for tag, instruct in [("narrA", "male, middle-aged, low pitch"), ("narrB", "male, middle-aged, moderate pitch")]:
    for lid, text in lines:
        a = m.generate(text=text, language="Uzbek", instruct=instruct, speed=0.95)
        a = a[0] if isinstance(a, list) else a
        x = (torch.as_tensor(a).float().numpy().reshape(-1).clip(-1, 1) * 32767).astype(np.int16)
        w = wave.open(f"{tag}_{lid}.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(x.tobytes()); w.close()
        print(tag, lid, round(len(x) / 24000, 2), flush=True)
