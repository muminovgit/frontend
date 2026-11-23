"""8 s hook test: night Westminster, policeman switches the 1868 signal, gas leaks, it explodes, sooty policeman.
Builds test.html (inline SVG + setFrame(f) animation driver) for frame-by-frame capture."""
import re, json
import gen, gen_city
from gen import P, PF, L, C, E, G

FPS, DUR = 30, 8.0
T = dict(v1=0.4, v2=2.3, leak=2.15, exp=3.9, v3=4.05, end=DUR)

svg = gen_city.scene("night", cast=True)
# burnt policeman at the same spot (hidden until the explosion)
bg, gb = gen.person("portlashdan_keyin", gen.SOOTY, dict(gen.POSES["politsiyachi"], arm_L=-30, forearm_L=-20, arm_R=30, forearm_R=24))
burnt = '<g id="fx_halo" opacity="0"><ellipse cx="405" cy="1640" rx="170" ry="250" fill="url(#fireglow)"/></g>' + f'<g id="stage_police_burnt" style="display:none" transform="translate(410,{1800 - gb*0.36:.1f}) scale(0.36)">{bg}</g>'
svg = svg.replace('<g id="stage_lady"', burnt + '<g id="stage_lady"', 1)
# the burnt policeman's gradients were created after the scene wrote its <defs>: rewrite the defs block
import re as _re
svg = _re.sub(r'<defs>.*?</defs>', lambda m: gen.defs(), svg, count=1, flags=_re.S)

# explosion fx at the signal lantern (signal at 230,1790; lantern centre local y -962)
LX, LY = 230, 828
star = " ".join(f"{(1 if i % 2 == 0 else 0.45) * __import__('math').cos(i * 3.14159 / 9):.3f},{(1 if i % 2 == 0 else 0.45) * __import__('math').sin(i * 3.14159 / 9):.3f}" for i in range(18))
fx = (f'<g id="fx_burst" transform="translate({LX},{LY}) scale(0.01)" opacity="0">'
      f'<polygon points="{star}" fill="#ff8a2a" stroke="#221d1a" stroke-width="0.012" transform="scale(1.0)"/>'
      f'<polygon points="{star}" fill="#ffd34a" transform="scale(0.72) rotate(10)"/>'
      f'<polygon points="{star}" fill="#fff6c8" transform="scale(0.4) rotate(20)"/></g>')
for i in range(7):
    fx += f'<g id="fx_debris_{i}" opacity="0"><rect x="-9" y="-5" width="18" height="10" rx="2" fill="#1f2a24" stroke="#221d1a" stroke-width="3"/></g>'
for i in range(6):
    fx += (f'<g id="fx_smoke_{i}" opacity="0"><circle r="60" fill="#5d5761"/><circle cx="-30" cy="10" r="44" fill="#6e6872"/>'
           f'<circle cx="34" cy="16" r="40" fill="#4f4a55"/></g>')
glow = ('<radialGradient id="fireglow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffb347" stop-opacity="0.75"/>'
        '<stop offset="0.5" stop-color="#ff8a2a" stop-opacity="0.3"/><stop offset="1" stop-color="#ff8a2a" stop-opacity="0"/></radialGradient>')
glow_el = f'<g id="fx_glow" opacity="0"><ellipse cx="{LX+80}" cy="{LY+500}" rx="560" ry="900" fill="url(#fireglow)"/></g>'
soot_lantern = f'<g id="fx_scorch" opacity="0"><ellipse cx="{LX}" cy="{LY}" rx="58" ry="62" fill="#120e0c" opacity="0.85"/></g>'

overlay = ('<rect id="fx_flash" width="1080" height="1920" fill="#fff8e6" opacity="0"/>'
           '<g id="title" opacity="0"><text x="540" y="250" text-anchor="middle" font-family="DejaVu Sans, Arial" font-weight="700" font-size="58" fill="#f3ead8" stroke="#221d1a" stroke-width="10" paint-order="stroke" letter-spacing="6">1868 · LONDON</text></g>'
           '<g id="sub"><text id="sub_t" x="540" y="1190" text-anchor="middle" font-family="DejaVu Sans, Arial" font-weight="800" font-size="64" fill="#ffffff" stroke="#221d1a" stroke-width="12" paint-order="stroke"></text></g>')

head, rest = svg.split("</defs>", 1)
rest = rest.replace('<g id="layer_cast">', glow_el + '<g id="layer_cast">', 1)
vi = rest.index('<rect width="1080" height="1920" fill="url(#vig_')
svg = head + glow + "</defs>" + '<g id="cam">' + rest[:vi] + soot_lantern + fx + "</g>" + rest[vi:].replace("</svg>", overlay + "</svg>")

JS = r"""
const T = __T__, FPS = __FPS__;
const $ = (id) => document.getElementById(id);
const base = {};
function rot(id, deg, cx, cy) {
  const el = $(id); if (!el) return;
  if (!(id in base)) { const m = /translate\(([-\d.]+),([-\d.]+)\)(?: rotate\(([-\d.]+)\))?/.exec(el.getAttribute('transform') || ''); base[id] = m ? [+m[1], +m[2], +(m[3] || 0)] : [0, 0, 0]; }
  const b = base[id];
  el.setAttribute('transform', `translate(${b[0]},${b[1]}) rotate(${b[2] + deg}${cx !== undefined ? ' ' + cx + ' ' + cy : ''})`);
}
const sm = (x) => { x = Math.max(0, Math.min(1, x)); return x * x * (3 - 2 * x); };
const seg = (t, a, b) => sm((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
function op(id, v) { const e = $(id); if (e) e.setAttribute('opacity', v.toFixed(3)); }
function rnd(i) { const x = Math.sin(i * 91.7 + 13.1) * 43758.5; return x - Math.floor(x); }

window.setFrame = (f) => {
  const t = f / FPS, ex = T.exp, after = t - ex;
  // ---- camera: slow push toward the signal + policeman, shake on the blast, small pull-back after
  let s = lerp(1.0, 1.32, seg(t, 0.2, ex)), fx = lerp(540, 400, seg(t, 0.2, ex)), fy = lerp(1080, 1230, seg(t, 0.2, ex));
  if (after > 0) { s = lerp(1.32, 1.22, seg(after, 0.2, 2.5)); }
  let sx = 0, sy = 0;
  if (after > 0 && after < 0.6) { const k = (1 - after / 0.6) * 26; sx = (f % 2 ? 1 : -1) * k; sy = (rnd(f) - 0.5) * k; }
  fx = Math.max(540 / s, Math.min(1080 - 540 / s, fx)); fy = Math.max(960 / s, Math.min(1920 - 960 / s, fy));
  $('cam').setAttribute('transform', `translate(${540 + sx},${960 + sy}) scale(${s}) translate(${-fx},${-fy})`);
  // parallax drift of the far layers
  $('layer_far').setAttribute('transform', `translate(${-t * 4},0)`);
  $('layer_mid').setAttribute('transform', `translate(${-t * 8},0)`);
  // ---- title
  op('title', seg(t, 0.1, 0.5) * (1 - seg(t, 2.0, 2.5)));
  // ---- policeman: looks up, reaches for the lever, signal goes from STOP to GO
  rot('politsiyachi_head', -6 * seg(t, 0.6, 1.0) + 1.5 * Math.sin(t * 2));
  rot('politsiyachi_arm_R', 100 * seg(t, 0.9, 1.35));
  rot('politsiyachi_forearm_R', -30 * seg(t, 0.9, 1.35) - 22 * seg(t, 1.35, 1.6));
  const go = seg(t, 1.35, 1.75);
  rot('signal_arm_L', 50 * go); rot('signal_arm_R', -50 * go);
  // lamp: red -> green; then flickers as the gas builds up
  const flick = (t > T.leak && t < ex) ? (0.55 + 0.45 * Math.abs(Math.sin(t * 37) * Math.sin(t * 11))) : 1;
  op('signal_lamp_red', after > 0 ? 0 : (1 - go));
  op('signal_lamp_green', after > 0 ? 0 : go * flick);
  // gas leak: green wisps grow and wobble
  const leak = seg(t, T.leak, T.leak + 0.8) * (after > 0 ? 0 : 1);
  const lk = $('signal_gas_leak'); if (lk) { lk.setAttribute('opacity', (leak * 0.9).toFixed(3)); lk.setAttribute('transform', `translate(26,-880) scale(${1 + 0.25 * leak + 0.05 * Math.sin(t * 9)}) rotate(${4 * Math.sin(t * 6)})`); }
  // policeman notices the smell: head turns, nose up
  if (t > T.leak) rot('politsiyachi_head', -6 + 8 * Math.sin((t - T.leak) * 5) * seg(t, T.leak, T.leak + 0.3));
  // ---- horse + cab trot to the right, stop and spook at the blast
  const run = Math.min(t, ex), cx = 600 + run * 22;
  $('stage_cab').setAttribute('transform', `translate(${cx + (after > 0 ? -18 * seg(after, 0, 0.3) : 0)},1630) scale(0.42)`);
  const ph = run * 2.2 * Math.PI * 2, trot = after > 0 ? Math.max(0, 1 - after * 3) : 1;
  rot('ot_foreleg_L', 18 * Math.sin(ph) * trot); rot('ot_foreleg_R', -18 * Math.sin(ph) * trot);
  rot('ot_hindleg_L', -16 * Math.sin(ph) * trot); rot('ot_hindleg_R', 16 * Math.sin(ph) * trot);
  rot('ot_cannon_fore_L', -20 * Math.max(0, Math.sin(ph)) * trot); rot('ot_cannon_fore_R', -20 * Math.max(0, -Math.sin(ph)) * trot);
  rot('ot_tail', 6 * Math.sin(ph * 0.5));
  rot('ot_neck', after > 0 ? -22 * seg(after, 0, 0.25) : 3 * Math.sin(ph));
  rot('hansom_cab_wheel', run * 140, 0, -140);
  // ---- lady: startled at the blast, hands up
  const fear = after > 0 ? seg(after, 0.05, 0.3) : 0;
  rot('piyoda_xonim_arm_L', -150 * fear); rot('piyoda_xonim_arm_R', 150 * fear);
  rot('piyoda_xonim_forearm_L', -40 * fear); rot('piyoda_xonim_forearm_R', 40 * fear);
  rot('piyoda_xonim_head', 4 * Math.sin(t * 2) + (after > 0 ? 6 * Math.sin(after * 30) * Math.max(0, 1 - after) : 0));
  // ---- explosion
  const b = $('fx_burst');
  if (after > 0 && after < 0.7) { const k = Math.sqrt(after / 0.7); b.setAttribute('transform', `translate(230,828) scale(${40 + 300 * k}) rotate(${after * 60})`); b.setAttribute('opacity', (1 - sm(after / 0.7)).toFixed(3)); }
  else b.setAttribute('opacity', 0);
  op('fx_flash', after > 0 ? 0.92 * Math.max(0, 1 - after / 0.28) : 0);
  op('fx_scorch', after > 0 ? 1 : 0);
  op('fx_halo', after > 0.05 ? Math.min(1, (after - 0.05) * 4) * (0.92 + 0.08 * Math.sin(t * 17)) : 0);
  op('fx_glow', after > 0 ? Math.max(0.35, 1 - after * 0.5) * (0.9 + 0.1 * Math.sin(t * 23)) : 0);
  for (let i = 0; i < 7; i++) {
    const e = $('fx_debris_' + i), a = rnd(i) * Math.PI * 2, v = 500 + rnd(i + 9) * 600, tt = Math.max(0, after);
    const x = 230 + Math.cos(a) * v * tt, y = 828 + Math.sin(a) * v * tt + 900 * tt * tt;
    e.setAttribute('transform', `translate(${x},${y}) rotate(${tt * 720 * (rnd(i + 3) - 0.5)})`); e.setAttribute('opacity', after > 0 && tt < 1.2 ? 1 : 0);
  }
  for (let i = 0; i < 6; i++) {
    const e = $('fx_smoke_' + i), tt = Math.max(0, after - 0.05 * i), a = rnd(i + 20) * Math.PI * 2;
    const x = 230 + Math.cos(a) * 120 * Math.sqrt(tt) + 30 * tt, y = 828 + Math.sin(a) * 70 * Math.sqrt(tt) - 90 * tt;
    e.setAttribute('transform', `translate(${x},${y}) scale(${0.4 + 1.3 * Math.sqrt(tt)})`); e.setAttribute('opacity', (after > 0 ? 0.85 * Math.max(0, 1 - tt / 3.5) : 0).toFixed(3));
  }
  // ---- swap to the sooty policeman behind the flash, dizzy wobble + rising smoke puffs
  const burnt = after > 0.08;
  $('stage_police').style.display = burnt ? 'none' : '';
  $('stage_police_burnt').style.display = burnt ? '' : 'none';
  if (burnt) {
    rot('portlashdan_keyin_head', 9 * Math.sin(after * 5));
    rot('portlashdan_keyin_torso', 3 * Math.sin(after * 5 + 1));
    rot('portlashdan_keyin_arm_L', 8 * Math.sin(after * 4)); rot('portlashdan_keyin_arm_R', -8 * Math.sin(after * 4 + 1));
    for (let i = 0; i < 4; i++) { const e = $('portlashdan_keyin_smoke_' + i); if (!e) continue;
      if (!e.dataset.b) e.dataset.b = e.getAttribute('transform');
      const m = /translate\(([-\d.]+),([-\d.]+)\) scale\(([-\d.]+)\)/.exec(e.dataset.b);
      const k = ((after * 0.6 + i * 0.25) % 1); e.setAttribute('transform', `translate(${+m[1] + 10 * Math.sin(k * 6 + i)},${+m[2] - 120 * k}) scale(${+m[3] * (0.7 + 0.8 * k)})`); e.setAttribute('opacity', (0.9 * (1 - k)).toFixed(3)); }
  }
  // ---- subtitles
  const st = $('sub_t');
  st.textContent = t >= T.v3 - 0.05 ? 'PORTLAB KETGAN!' : t >= T.v2 ? 'bir oy ham ishlamay…' : t >= T.v1 ? 'Dunyodagi birinchi svetofor…' : '';
  st.setAttribute('font-size', t >= T.v3 - 0.05 ? 92 : 62);
  st.setAttribute('fill', t >= T.v3 - 0.05 ? '#ffd34a' : '#ffffff');
};
""".replace("__T__", json.dumps(T)).replace("__FPS__", str(FPS))

html = f"<!doctype html><html><head><meta charset='utf-8'><style>html,body{{margin:0;background:#000}}svg{{display:block}}</style></head><body>{svg}<script>{JS}</script></body></html>"
open("test.html", "w").write(html)
print("frames", int(FPS * DUR), "T", T)
