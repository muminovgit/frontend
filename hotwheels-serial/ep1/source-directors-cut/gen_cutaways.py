"""Generate cutaway shots with the free Pollinations image API (no key)."""
import urllib.parse, urllib.request, sys, os, time, concurrent.futures as cf
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(OUT, exist_ok=True)
STYLE = ("cinematic film still, Safdie brothers Uncut Gems style, gritty 35mm film grain, anxious handheld feel, "
         "teal and amber color grade, practical neon lights, shallow depth of field, dramatic contrast, no text, no watermark. ")
SHOTS = {
 "c_box2": "Top-down photo looking into an open dusty cardboard box filled with many small old metal toy cars, red blue yellow, scratched paint, flea market",
 "c_phone2": "Close-up of a smartphone lying on a dark nightstand, screen lit up with a new message notification, blue glow on the wood, 2 AM",
 "c_pink": "Macro photo of a small pink vintage toy volkswagen bus with two tiny surfboards in the back, on dark wood, glowing like a treasure, bokeh",
 "c_search": "Over the shoulder view of a young man in olive green bomber jacket looking at a laptop in a dark room, screen glow on his face, tense",
}

def get(name, prompt, seed):
    path = f"{OUT}/{name}.jpg"
    if os.path.exists(path): return name, "cached"
    q = urllib.parse.quote(STYLE + prompt)
    url = f"https://image.pollinations.ai/prompt/{q}?width=768&height=1344&nologo=true&seed={seed}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                data = r.read()
            if len(data) > 10000:
                open(path, "wb").write(data); return name, len(data)
        except Exception as e:
            err = str(e)
        time.sleep(5 * (attempt + 1))
    return name, "FAILED"

with cf.ThreadPoolExecutor(2) as ex:
    for res in ex.map(lambda kv: get(kv[1][0], kv[1][1], 100 + kv[0]), enumerate(SHOTS.items())):
        print(*res, flush=True)
