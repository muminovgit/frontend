# Dcard 15s film — sources log

## Picture
| Asset | Source | Licence |
|---|---|---|
| `film/assets/img/dcard-mark.svg`, `coin.svg` | dcard.uz (`/assets/`) — the brand's own mark and coin | Client brand assets |
| `film/assets/img/app-qr-crop.png` | dcard.uz `/assets/app-qr.png`, cropped above the cashback line (no % on screen) | Client brand asset |
| Anton (kinetic type) | Google Fonts | SIL OFL 1.1 |
| Inter (wordmark, UI) | Google Fonts — the site's own font | SIL OFL 1.1 |
| Caveat + baked centerlines (`assets/baked/caveat-pen.js`) | HyperFrames registry `hw-write-title` | Caveat: SIL OFL 1.1; registry item: HyperFrames (Apache-2.0) |
| GSAP 3.14.2 | cdn.jsdelivr.net | GSAP standard licence (free) |

Copy is taken from dcard.uz (Qahva/kechki ovqat, 1+1, QR-kodni ko'rsating, coin yig'ing, Toping/Ko'rsating/Yig'ing, "Har bir xariddan ko'proq foyda", "iOS va Android uchun"). No %, multipliers, customer names or figures.

## Sound — all generated, no samples
`tools/score.py` synthesises everything (numpy): 120 BPM groove (kick, clap, hats, bass, pad) in sections,
risers, and SFX (paper thuds on every type landing, pops, pen/marker scribbles, whooshes, coin clinks timed
from the physics in `film/assets/audio/hits.json`, logo sub-hit). Original work — no third-party audio, CC0-equivalent.
Master: −14 LUFS integrated, ≤ −2 dBTP, re-measured on the final AAC (`tools/measure.sh`).

## HyperFrames registry items checked / installed
hw-write-title (Caveat stroke write-on data), marker-highlight, hw-arrow, echo-smear, motion-blur, camera-scan-gate.
The composition reuses the baked Caveat centerlines and pen-velocity easing; marker strokes, physics, smear and
onion-skin are authored in `film/index.html`.

## Ending (added)
The closing sequence recreates Dcard's own app close/open animation (reference: the client's screen recording
IMG_6174.MP4, not included in the film): the wordmark tucks into the mark, the mark zooms into its blue, and the
white glyph + yellow sparkle pattern ripples out from the centre. Rebuilt in code from the real mark's glyph path
(`assets/img/dcard-mark.svg`, path "Subtract"), so it stays sharp at 1080×1920.
