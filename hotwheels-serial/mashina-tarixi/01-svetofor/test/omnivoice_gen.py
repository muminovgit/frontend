import sys, time, wave, numpy as np, torch
from omnivoice import OmniVoice
torch.set_num_threads(4)
t0 = time.time()
m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
print("loaded", round(time.time() - t0, 1), flush=True)
lines = [
 ("v1", "Dunyodagi birinchi svetofor..."),
 ("v2", "bir oy ham ishlamay..."),
 ("v3", "portlab ketgan!"),
]
for instruct in ["female, middle-aged, low pitch", "male, middle-aged, moderate pitch"]:
    tag = instruct.split(",")[0]
    for lid, text in lines:
        t1 = time.time()
        audio = m.generate(text=text, language="Uzbek", instruct=instruct)
        a = audio[0] if isinstance(audio, list) else audio
        a = torch.as_tensor(a).float().reshape(1, -1)
        x = (a.numpy().reshape(-1).clip(-1, 1) * 32767).astype(np.int16)
        w = wave.open(f"{tag}_{lid}.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(x.tobytes()); w.close()
        print(tag, lid, round(a.shape[1] / 24000, 2), "s audio in", round(time.time() - t1, 1), "s", flush=True)
