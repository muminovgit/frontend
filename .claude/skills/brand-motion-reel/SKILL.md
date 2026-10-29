---
name: brand-motion-reel
description: >
  End-to-end motion-graphics ads and Instagram Reels for a product or app: read the brand's website,
  use real app screenshots, animate in a single seek(t) HTML page, render 60 fps MP4 with real motion
  blur, generate music + SFX, add an Uzbek (or other) TTS voiceover, master to -14 LUFS and review
  frame by frame. Use this whenever the user asks for a reel, "motion video", promo/launch/explainer
  video, ad, showreel, "video yasab ber", "reels qilib ber", "ovozli qil", or sends a website / app
  screenshots / an Instagram reference and wants a video for it — even if they only say "make it like
  this" or "add voice".
---

# Brand motion reel

You make the whole video yourself: copy, design, animation, render, sound, voice, mastering, review,
commit, delivery. Talk to the user in their language (this user writes Uzbek, often casually); keep
technical detail out of the chat unless it matters to them.

## 1. Intake — facts before pixels

1. **Read the site with Playwright** (not WebFetch — it misses colours/fonts): title, meta description,
   body text, computed colours (count usage), font families, `<img>`/svg assets, app-store links.
   Download the logo, product renders and fonts (Google Fonts css2 with a desktop UA → woff2).
2. **Ask for real material when it would change the result** — real app screenshots / screen
   recordings (native resolution, not Telegram-compressed), SVG logo, licensed voice or music.
   Real screens beat drawn mock-ups every time; the user explicitly preferred them.
3. **Truthfulness checks** (the user relies on you for this):
   - Features marked "tez orada" / "coming soon" in the app must be shown as such, never as live.
   - No invented results, prices, %, customer names. Use the product's own copy where possible.
   - If a template brief names a different product than the link (e.g. "Trezio" vs davodelivery.uz),
     go with the link and say so.
   - Don't make claims about competitors you can't verify.
4. **Privacy-clean screenshots**: replace the status bar with a clean "9:41", and paint over personal
   addresses/names (use the site's own demo values instead). Blur real employee names in admin UIs.
5. Default format for this user: **1080×1920 Reels, 60 fps, Uzbek copy**, 15 s unless a voiceover
   needs longer (then pace scenes to the voice, ~20–25 s is fine).

## 2. Build — one HTML page, every pixel a function of t

Start from `references/reel_example.html` (Davo Delivery reel) — copy its helpers rather than rewriting.

- **Contract**: `window.ready` (Promise) and `window.seek(t)`. `seek` hides everything, then each scene
  shows/poses only its own elements from `t`. No CSS transitions, timers or state between frames
  (renders are seek-order independent and run in parallel workers).
- **Load fonts before building** (`document.fonts.load(...)` → `build()` → wait for images → `seek(0)`);
  headline layout measures text. Cache widths; a hidden element measures 0.
- **Motion vocabulary** (one primary move per transition, a new idea every ~1.5–2.5 s):
  closed-form springs for pops/settles, squash on landings, gravity drops, masked word rises,
  circular colour wipes from the object that caused them (a "+" button, a check badge), camera
  push into an element that becomes the next background, hard background switches for a "new" beat.
- **Real app inside a phone**: stitch screenshots into one tall page image (seam in white space),
  place it in a phone frame scaled ~1.15, scroll it by `translateY`, and put live overlays
  (typing in the real search field, counters 0/2→2/2, rings, badges) **in page coordinates** inside
  the scrolled layer so they stay locked to the UI. Give the status bar a background once content
  scrolls under it.
- **Vector-rebuild tiny raster logos** (a 96 px PNG won't survive a zoom) when the geometry is simple.
- Watch for: headline exit times hard-coded to old scene starts after re-pacing; long words overflowing
  1080 px (fit or shrink); falling objects crossing text; notifications whose drug/name disagree with
  the screen underneath.

## 3. Review stills, then render

```bash
node scripts/stills.js reel.html 1080 1920 /path/to/out 0.9,3.2,6.6,...   # then hstack into a sheet and look
# full render: 4 workers on disjoint frame ranges, then concat
for r in "0 354" "354 708" "708 1062" "1062 1413"; do node scripts/render.js reel.html 1080 1920 $r part_${r%% *}.mp4 & done; wait
printf "file '%s'\n" part_*.mp4 > list.txt; ffmpeg -f concat -safe 0 -i list.txt -c copy raw.mp4
```
60 fps × 8 subframes (ffmpeg `tmix`) gives real motion blur; 4 subframes leaves ghost copies on fast moves.
Frames = duration × 60. Expect ~1 min per 2 s of video with 4 workers.

## 4. Sound

- **Music + SFX are synthesised** (numpy; no licence questions) — see `references/score_example.py`:
  pad + offbeat bass, drums in sections (drop out on transitions / while something is airborne, slam back
  with a crash on the next hit), risers into slams, and **a sound on every visual hit** (pop, thud,
  tick for typing, whoosh peaking at the cut, plastic clink, two-tone chime for notifications, sub-hit
  on the logo). Keep the scene table in the score identical to the page's `T` table.
- **Voiceover** (`scripts/tts.py` + `scripts/voice_fx.sh`): Uzbek `uz-UZ-MadinaNeural`.
  The user's approved "energetic, cheerful, bright" preset: rate `+8%`, pitch `+18Hz`, every line ending
  in "!", then `voice_fx.sh bright` (high-shelf +3.5 dB, low-mid cut, compressor). Calm version: rate `-4%`,
  pitch 0, `voice_fx.sh calm`. Generate lines, **measure each duration, then pace scenes** so each line
  sits inside its scene with ~0.3 s lead. Duck music/SFX ~-8 dB under the voice (envelope-smoothed).
  There is no emotion-style control for the Uzbek voices — say so if they want more feeling, and offer a
  real recording.
- **Licensing caveat to repeat every time**: Edge TTS is the free read-aloud endpoint — not licensed for
  paid ads. Licensed options: Azure Speech (same voices) or a human recording. API keys go in the
  environment's Network secrets, never in chat.
- **Master on the final AAC**: `python3 scripts/master.py raw.mp4 final.mp4 "python3 tools/score.py" 0 -1`
  iterates gain until the encoded file reads -14 LUFS (±0.1), true peak ≤ -1 dBTP (use -2 if the brief says so).
  `score.py` must accept the gain as its last arg and print the WAV path on its last stdout line.

## 5. Check and deliver

```bash
python3 scripts/review.py final.mp4 /tmp/rev 60 send:2.7:3.8 drop:5.4:6.1   # pop scan + frame sheets
```
Look at every fast moment's sheet (wipes, zooms, drops). Fix, re-render only the affected frame range
when possible. Then: commit + push to the session branch, `SendUserFile` the MP4 (display: render),
and reply in Uzbek with: what's in each scene (short table), sound summary, measured loudness,
honest caveats (made-up demo data, voice licence, anything not verified by ear), and 2–3 offers.

## Known pitfalls (learned the hard way)
- ffmpeg inside `while read` loops eats stdin → always `-nostdin`.
- aiohttp/edge-tts ignores `SSL_CERT_FILE`; patch `certifi.where` to the proxy CA bundle (done in tts.py).
- Instagram/Pexels pages are blocked or login-walled: ask for MP4 files or screenshots instead of links.
- Small contact-sheet thumbnails lie (fake "double" glyphs) — confirm at full size before "fixing".
- A loudness loop can oscillate by ±0.2 LU because of the limiter; accept ±0.2 and say the number.
