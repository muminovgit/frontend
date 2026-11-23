# Portlagan svetofor: rigged vector characters

- `character_sheet.svg`: all 7 characters on one sheet (background `#f3ead8`, outlines `#221d1a`). Preview: `character_sheet_preview.png`.
- Single-character files: `politsiyachi.svg`, `portlashdan_keyin.svg`, `jon_nayt.svg`, `aravakash.svg`, `piyoda_xonim.svg`, `bugungi_haydovchi.svg`, `ot.svg`.
- `gen_characters.py` generates all the files. Edit colours, poses (`POSES`) or proportions there, then run `python3 gen_characters.py <out_dir>`.

## Rig
Every joint is its own `<g>`, already translated to its pivot (also stored in `data-pivot`). To animate a joint, append `rotate(deg)` to that group's `transform`. Children follow automatically.

People (prefix = character id, e.g. `politsiyachi_`):
```
<id>_pelvis
 ├ <id>_thigh_L/R → <id>_shin_L/R → <id>_foot_L/R
 ├ <id>_skirt                      (lady only, hangs from the waist)
 └ <id>_torso
    ├ <id>_neck → <id>_head → <id>_hat, <id>_eye_L/R, <id>_brow_L/R, <id>_nose, <id>_mouth, <id>_moustache, <id>_ear_L/R
    │                         (+ <id>_sweat, <id>_smoke_0..3 where used)
    └ <id>_upper_arm_L/R → <id>_forearm_L/R → <id>_hand_L/R
<id>_contact_shadow
```
L/R means the character's own left and right, so L is on the viewer's right.

Horse (`ot_`): `ot_neck → ot_head → ot_ear, ot_eye, ot_nostril, ot_mouth`; `ot_tail`; and for each of the four legs (`foreleg_L/R`, `hindleg_L/R`): `→ ot_cannon_* → ot_fetlock_* → ot_pastern_* → ot_hoof_*`. Here L is the near side and R is the far side.

All shapes are vector: paths and gradients only, with no raster images.
