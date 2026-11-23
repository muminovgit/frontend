# Westminster 1868: city backdrop (2D vector, 1080x1920)

- `shahar_kunduzi.svg` / `shahar_kechasi.svg`: empty backdrop, day and night.
- `sahna_kunduzi_qahramonlar.svg` / `sahna_kechasi_qahramonlar.svg`: the same backdrop with the policeman, the lady, and the cabbie with hansom cab and horse placed in it.
- `shahar_preview.png`: all four side by side.
- `gen_city.py`: generates everything. It reuses `../characters/gen_characters.py`. Run: `python3 gen_city.py <out_dir>`.

## Layers (for parallax: `data-parallax` = suggested speed relative to the camera)
`layer_sky` (clouds or moon and stars) → `layer_far` 0.15 (Parliament + `clock_tower`) → `layer_mid` 0.45 (terraced houses `house_0..`, far pavement) → `layer_ground` 0.8 (cobbled road, puddle) → `layer_near` 1.0 (near pavement) → `layer_props` (`gas_lamp_1/2`) → `layer_foreground` 1.2 (railing) → `knight_signal` → `layer_cast`

## Animatable props
- `knight_signal`:
  - `signal_arm_L` / `signal_arm_R`: rotate at the mast. 0° = horizontal ("STOP"), about 55° = lowered ("GO").
  - `signal_lamp_red` / `signal_lamp_green`: switch them by opacity.
  - `signal_gas_leak`: gas leaking before the explosion (opacity 0 → 1).
- `gas_lamp_*_flame`: lamp flame (on at night).
- `clock_face` → `clock_hour_hand` / `clock_minute_hand`: rotate.
- `hansom_cab_wheel`: rotate.
