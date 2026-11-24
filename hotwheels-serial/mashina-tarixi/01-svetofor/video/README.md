# Portlagan svetofor: 1-qism videosi (ovozsiz versiya)

The video is built from 2D vector characters and backdrops (`../characters`, `../city`). It has animation, subtitles, music and sound effects. **There is no narration yet**: it will be added later.

## Beats (`src/beats.py`)
| # | Location | Duration | Content |
|---|---|---|---|
| b1 | night | 3.6 s | Hook: the signal flickers and explodes |
| b2 | day | 5.2 s | 1868, London, busy street, the lady can't cross |
| b3 | knight | 4.8 s | Jon Nayt and his drawing in front of Parliament |
| b4 | semaphore | 5.6 s | Railway signal → street signal (day: arms, night: gas lamp) |
| b5 | day | 5.2 s | The policeman pulls the lever: red = stop, green = go |
| b6 | day | 4.2 s | The carriages stop, the lady crosses, newspaper |
| b7 | night | 4.2 s | January 1869, snow, gas leaks out |
| b8 | night | 2.6 s | Explosion |
| b9 | night | 4.0 s | The sooty policeman, "NAFAQADA" stamp |
| b10 | stove | 7.2 s | Explanation: kitchen gas stove, lantern cut-away |
| b11 | calendar | 4.4 s | 1869 → 1920s, electric signal |
| b12 | modern | 5.6 s | Today's driver at the red light |
| b13 | end | 3.0 s | "MASHINA TARIXI", "Obuna bo'l" |

## When the narration arrives
1. Split the narration into one wav per beat: `voice/b1.wav` … `voice/b13.wav`.
2. In `beats.py`, set each beat's `dur` to its line length plus about 0.3 s. All animations use beat-local time, so they stretch on their own.
3. Re-render:
```
python3 beats.py
python3 build_pages.py
python3 make_jobs.py
node capture.mjs jobs_full.json
python3 audio.py --voice voice
python3 assemble.py mix_voice.wav final.mp4
```
`audio.py` places each line at its beat and ducks the music under the voice.
Run these commands from the `src/` folder. Capture needs Node with Playwright (`npm i playwright`).
