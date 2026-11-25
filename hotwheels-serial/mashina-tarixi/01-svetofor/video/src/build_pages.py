"""Builds one HTML page per location for "Portlagan svetofor". Each page exposes window.setFrame(f, beatId) where f is
the frame inside that beat (beat-local time t = f / 30). Shared look: 2D vector, #221d1a outlines, cream palette."""
import os, sys, re, json, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
# repo layout: ../../characters/gen_characters.py and ../../city/gen_city.py
sys.path.insert(0, os.path.join(HERE, "..", "..", "characters")); sys.path.insert(0, os.path.join(HERE, "..", "..", "city"))
import gen_characters as gen
sys.modules["gen"] = gen
import gen_city
from gen import P, PF, L, C, E, G, INK, mul, mix, shade
from beats import timeline

TL = timeline()
SUBS = {b["id"]: b["subs"] for b in TL}
SCALE = {b["id"]: round(b["anim"] / b["dur"], 5) for b in TL}
DURS = {b["id"]: b["dur"] for b in TL}
OUT = os.path.join(HERE, "pages"); os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920
FONT = "DejaVu Sans, Arial, sans-serif"

def rect(x, y, w, h, fill, sw=3, rx=0, extra=""):
    f = fill if (fill.startswith("url") or fill == "none") else shade(fill)
    s = f' stroke="{INK}" stroke-width="{sw}"' if sw else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{f}"{s}{extra}/>'
def text(x, y, s, size, fill="#ffffff", weight=800, anchor="middle", stroke=10, extra=""):
    st = f' stroke="{INK}" stroke-width="{stroke}" paint-order="stroke" stroke-linejoin="round"' if stroke else ""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-weight="{weight}" font-size="{size}" fill="{fill}"{st}{extra}>{s}</text>'

SUB_LAYER = ('<g id="subs"><rect id="subbg1" rx="18" fill="#221d1a" opacity="0"/><rect id="subbg2" rx="18" fill="#221d1a" opacity="0"/>'
             + text(540, 430, "", 54, stroke=0, extra=' id="sub1"') + text(540, 504, "", 54, stroke=0, extra=' id="sub2"') + '</g>'
             '<rect id="flash" width="1080" height="1920" fill="#fff8e6" opacity="0"/>'
             '<g id="brand" opacity="0.92">' + rect(40, 250, 400, 64, "#221d1a", 0, 32) + text(240, 293, "MASHINA TARIXI · #1", 28, fill="#ffd34a", stroke=0, weight=900) + '</g>'
             '<g id="hook1" opacity="0">' + text(540, 560, "DUNYODAGI BIRINCHI", 74, fill="#ffffff", stroke=14) + text(540, 660, "SVETOFOR…", 96, fill="#ffffff", stroke=16) + '</g>'
             '<g id="hook2" opacity="0">' + text(540, 640, "PORTLAB KETGAN!", 92, fill="#ffd34a", stroke=16, weight=900) + '</g>')

JS_LIB = r"""
const $ = (id) => document.getElementById(id);
const BASE = {};
const baseOf = (id) => { if (!(id in BASE)) { const e = $(id); BASE[id] = e ? (e.getAttribute('transform') || '') : ''; } return BASE[id]; };
const PIV = {};
function rot(id, deg, cx, cy) {
  const el = $(id); if (!el) return;
  if (!(id in PIV)) { const m = /translate\(([-\d.]+),([-\d.]+)\)(?: rotate\(([-\d.]+)\))?/.exec(el.getAttribute('transform') || ''); PIV[id] = m ? [+m[1], +m[2], +(m[3] || 0)] : [0, 0, 0]; }
  const b = PIV[id];
  el.setAttribute('transform', `translate(${b[0]},${b[1]}) rotate(${b[2] + deg}${cx !== undefined ? ' ' + cx + ' ' + cy : ''})`);
}
const tr = (id, extra) => { const e = $(id); if (e) e.setAttribute('transform', (baseOf(id) + ' ' + extra).trim()); };
const setT = (id, t) => { const e = $(id); if (e) e.setAttribute('transform', t); };
const op = (id, v) => { const e = $(id); if (e) e.setAttribute('opacity', Math.max(0, Math.min(1, v)).toFixed(3)); };
const disp = (id, on) => { const e = $(id); if (e) e.style.display = on ? '' : 'none'; };
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const sm = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const seg = (t, a, b) => sm((t - a) / (b - a));
const eo = (x) => 1 - Math.pow(1 - clamp(x, 0, 1), 3);
const back = (x) => { x = clamp(x, 0, 1); const c = 1.70158; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
const rnd = (i) => { const x = Math.sin(i * 91.7 + 13.1) * 43758.5; return x - Math.floor(x); };
function cam(s, fx, fy, sx = 0, sy = 0) {
  fx = clamp(fx, 540 / s, 1080 - 540 / s); fy = clamp(fy, 960 / s, 1920 - 960 / s);
  setT('cam', `translate(${540 + sx},${960 + sy}) scale(${s}) translate(${-fx},${-fy})`);
}
function subs(beat, t) {
  const list = (SUBS[beat] || []); let c = null;
  for (const s of list) if (t >= s[0] && t < s[1] + 0.05) c = s;
  $('sub1').textContent = c ? c[2][0] : ''; $('sub2').textContent = c && c[2].length > 1 ? c[2][1] : '';
  for (const n of ['1', '2']) { const tx = $('sub' + n), bg = $('subbg' + n);
    if (tx.textContent) { const b = tx.getBBox(); bg.setAttribute('x', b.x - 22); bg.setAttribute('y', b.y - 6); bg.setAttribute('width', b.width + 44); bg.setAttribute('height', b.height + 12); bg.setAttribute('opacity', 0.78); }
    else bg.setAttribute('opacity', 0); }
  const k = c ? clamp((t - c[0]) / 0.12, 0, 1) : 0;   // tiny pop-in per card
  setT('subs', `translate(540,465) scale(${0.92 + 0.08 * back(k)}) translate(-540,-465)`);
}
function trot(p, ph, k) {  // horse trot cycle for prefix p (ot / ot2)
  rot(p + '_foreleg_L', 18 * Math.sin(ph) * k); rot(p + '_foreleg_R', -18 * Math.sin(ph) * k);
  rot(p + '_hindleg_L', -16 * Math.sin(ph) * k); rot(p + '_hindleg_R', 16 * Math.sin(ph) * k);
  rot(p + '_cannon_fore_L', -22 * Math.max(0, Math.sin(ph)) * k); rot(p + '_cannon_fore_R', -22 * Math.max(0, -Math.sin(ph)) * k);
  rot(p + '_tail', 6 * Math.sin(ph * 0.5)); rot(p + '_neck', 3 * Math.sin(ph) * k);
}
"""

WARP = r"""
const __sf = window.setFrame;
window.setFrame = (f, beat) => {
  const tr = f / 30, D = DURS[beat]; let ta = tr * SCALE[beat];
  if (beat === 'b1') { const hit = D - 1.45; ta = tr < hit ? 1.25 * tr / hit : 1.25 + (tr - hit); }          // boom on "portlab ketgan"
  if (beat === 'b8') { const hit = D - 1.0; ta = tr < hit ? -0.737 + 0.842 * tr / hit : 0.105 + (tr - hit) * 0.95; }  // boom on "portladi"
  __sf(ta * 30, beat);
  subs(beat, tr);
  if (beat === 'b1') {   // big hook text instead of the subtitle
    const hit = D - 1.45;
    for (const n of ['sub1', 'sub2']) $(n).textContent = '';
    for (const n of ['subbg1', 'subbg2']) $(n).setAttribute('opacity', 0);
    op('hook1', tr < hit ? seg(tr, 0, 0.15) : 0); tr_('hook1', `translate(540,600) scale(${0.85 + 0.15 * back(seg(tr, 0, 0.3)) + 0.03 * tr}) translate(-540,-600)`);
    op('hook2', tr >= hit ? 1 : 0); tr_('hook2', `translate(540,620) scale(${0.5 + 0.5 * back(seg(tr - hit, 0, 0.25))}) rotate(${-4 * seg(tr - hit, 0, 0.25)}) translate(-540,-620)`);
  } else { op('hook1', 0); op('hook2', 0); }
  op('brand', beat === 'b13' ? 0 : 0.92);
};
function tr_(id, t) { const e = $(id); if (e) e.setAttribute('transform', t); }
"""

def page(name, svg_body, js, defs_extra="", bg="#f3ead8", overlay=""):
    """svg_body is placed inside <g id="cam">; subtitles + flash overlay on top"""
    html = (f"<!doctype html><html><head><meta charset='utf-8'><style>html,body{{margin:0;background:{bg}}}svg{{display:block}}</style></head><body>"
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{gen.defs()[6:-7]}{defs_extra}</defs><g id="cam">{svg_body}</g>{overlay}{SUB_LAYER}</svg>'
            f"<script>const SUBS = {json.dumps(SUBS, ensure_ascii=False)}; const SCALE = {json.dumps(SCALE)}; const DURS = {json.dumps(DURS)};{JS_LIB}{js}{WARP}</script></body></html>")
    open(os.path.join(OUT, name + ".html"), "w").write(html)
    print("page", name, len(html) // 1024, "KB")

def svg_inner(svg):
    """strip the outer <svg> + its <defs>, keep the drawing (defs stay in gen.DEFS)"""
    body = re.sub(r"^<svg[^>]*>", "", svg); body = re.sub(r"</svg>$", "", body)
    body = re.sub(r"<title>.*?</title>", "", body); body = re.sub(r"<defs>.*?</defs>", "", body, count=1, flags=re.S)
    return body

FIREGLOW = ('<radialGradient id="fireglow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffb347" stop-opacity="0.75"/>'
            '<stop offset="0.5" stop-color="#ff8a2a" stop-opacity="0.3"/><stop offset="1" stop-color="#ff8a2a" stop-opacity="0"/></radialGradient>')
def star_pts(n=9, inner=0.45):
    return " ".join(f"{(1 if i % 2 == 0 else inner) * math.cos(i * math.pi / n):.3f},{(1 if i % 2 == 0 else inner) * math.sin(i * math.pi / n):.3f}" for i in range(2 * n))
def burst(gid, x, y):
    s = star_pts()
    return (f'<g id="{gid}" transform="translate({x},{y}) scale(0.01)" opacity="0">'
            f'<polygon points="{s}" fill="#ff8a2a" stroke="{INK}" stroke-width="0.012"/>'
            f'<polygon points="{s}" fill="#ffd34a" transform="scale(0.72) rotate(10)"/><polygon points="{s}" fill="#fff6c8" transform="scale(0.4) rotate(20)"/></g>')

# =====================================================================================================================
# NIGHT: winter night, the signal flickers, gas leaks, it explodes, sooty policeman, "retired" stamp  (b1 b7 b8 b9)
# =====================================================================================================================
def build_night():
    gen.DEFS.clear()
    svg = gen_city.scene("night", cast=True)
    bg, gb = gen.person("portlashdan_keyin", gen.SOOTY, dict(gen.POSES["politsiyachi"], arm_L=-30, forearm_L=-20, arm_R=30, forearm_R=24))
    body = svg_inner(svg)
    LX, LY = 230, 828
    halo = '<g id="fx_halo" opacity="0"><ellipse cx="405" cy="1640" rx="170" ry="250" fill="url(#fireglow)"/></g>'
    burnt = halo + f'<g id="stage_police_burnt" style="display:none" transform="translate(410,{1800 - gb*0.36:.1f}) scale(0.36)">{bg}</g>'
    body = body.replace('<g id="stage_lady"', burnt + '<g id="stage_lady"', 1)
    glow_el = f'<g id="fx_glow" opacity="0"><ellipse cx="{LX+80}" cy="{LY+500}" rx="560" ry="900" fill="url(#fireglow)"/></g>'
    body = body.replace('<g id="layer_cast">', glow_el + '<g id="layer_cast">', 1)
    fx = f'<g id="fx_scorch" opacity="0"><ellipse cx="{LX}" cy="{LY}" rx="58" ry="62" fill="#120e0c" opacity="0.85"/></g>' + burst("fx_burst", LX, LY)
    for i in range(7):
        fx += f'<g id="fx_debris_{i}" opacity="0"><rect x="-9" y="-5" width="18" height="10" rx="2" fill="#1f2a24" stroke="{INK}" stroke-width="3"/></g>'
    for i in range(6):
        fx += (f'<g id="fx_smoke_{i}" opacity="0"><circle r="60" fill="#5d5761"/><circle cx="-30" cy="10" r="44" fill="#6e6872"/>'
               f'<circle cx="34" cy="16" r="40" fill="#4f4a55"/></g>')
    # "retired" stamp on the scorched signal
    stamp = (f'<g id="stamp" opacity="0" transform="translate({LX + 120},{LY + 150}) rotate(-12)">'
             f'<rect x="-200" y="-56" width="400" height="112" rx="14" fill="none" stroke="#d8322b" stroke-width="12"/>'
             + text(0, 22, "NAFAQADA", 64, fill="#d8322b", stroke=0) + "</g>")
    # cold-air snow (screen space, inside the scene so it is under the subtitles)
    snow = "".join(f'<circle id="sn{i}" r="{2 + (i % 3) * 1.6:.1f}" fill="#f4f2ff" opacity="{0.55 + 0.4 * ((i * 37) % 10) / 10:.2f}"/>' for i in range(90))
    vi = body.index('<rect width="1080" height="1920" fill="url(#vig_')
    body = body[:vi] + fx + stamp + body[vi:]
    js = r"""
const T = { leak: 2.15, exp: 4.0 };
function sceneAt(ts) {
  const ex = T.exp, after = ts - ex;
  const go = seg(ts, 1.35, 1.75);
  rot('politsiyachi_head', -6 * seg(ts, 0.6, 1.0) + 1.5 * Math.sin(ts * 2));
  rot('politsiyachi_arm_R', 100 * seg(ts, 0.9, 1.35) * (1 - seg(ts, 1.9, 2.3)));
  rot('politsiyachi_forearm_R', (-30 * seg(ts, 0.9, 1.35) - 22 * seg(ts, 1.35, 1.6)) * (1 - seg(ts, 1.9, 2.3)));
  rot('signal_arm_L', 50 * go); rot('signal_arm_R', -50 * go);
  const flick = (ts > T.leak && ts < ex) ? (0.55 + 0.45 * Math.abs(Math.sin(ts * 37) * Math.sin(ts * 11))) : 1;
  op('signal_lamp_red', after > 0 ? 0 : (1 - go)); op('signal_lamp_green', after > 0 ? 0 : go * flick);
  const leak = seg(ts, T.leak, T.leak + 0.8) * (after > 0 ? 0 : 1);
  const lk = $('signal_gas_leak'); if (lk) { lk.setAttribute('opacity', (leak * 0.9).toFixed(3)); lk.setAttribute('transform', `translate(26,-880) scale(${1 + 0.35 * leak + 0.05 * Math.sin(ts * 9)}) rotate(${4 * Math.sin(ts * 6)})`); }
  if (ts > T.leak && after < 0) rot('politsiyachi_head', -6 + 10 * Math.sin((ts - T.leak) * 5) * seg(ts, T.leak, T.leak + 0.3));
  const run = Math.min(ts, ex), cx = 600 + run * 22;
  setT('stage_cab', `translate(${cx + (after > 0 ? -18 * seg(after, 0, 0.3) : 0)},1630) scale(0.42)`);
  const k = after > 0 ? Math.max(0, 1 - after * 3) : 1; trot('ot', run * 2.2 * Math.PI * 2, k);
  if (after > 0) rot('ot_neck', -22 * seg(after, 0, 0.25));
  rot('hansom_cab_wheel', run * 140, 0, -140);
  const fear = after > 0 ? seg(after, 0.05, 0.3) : 0;
  rot('piyoda_xonim_arm_L', -150 * fear); rot('piyoda_xonim_arm_R', 150 * fear);
  rot('piyoda_xonim_forearm_L', -40 * fear); rot('piyoda_xonim_forearm_R', 40 * fear);
  rot('piyoda_xonim_head', 4 * Math.sin(ts * 2) + (after > 0 ? 6 * Math.sin(after * 30) * Math.max(0, 1 - after) : 0));
  const b = $('fx_burst');
  if (after > 0 && after < 0.7) { const q = Math.sqrt(after / 0.7); b.setAttribute('transform', `translate(230,828) scale(${40 + 300 * q}) rotate(${after * 60})`); b.setAttribute('opacity', (1 - sm(after / 0.7)).toFixed(3)); } else b.setAttribute('opacity', 0);
  op('fx_scorch', after > 0 ? 1 : 0);
  op('fx_glow', after > 0 ? Math.max(0.35, 1 - after * 0.5) * (0.9 + 0.1 * Math.sin(ts * 23)) : 0);
  op('fx_halo', after > 0.05 ? Math.min(1, (after - 0.05) * 4) * (0.92 + 0.08 * Math.sin(ts * 17)) : 0);
  for (let i = 0; i < 7; i++) { const e = $('fx_debris_' + i), a = rnd(i) * Math.PI * 2, v = 500 + rnd(i + 9) * 600, tt = Math.max(0, after);
    e.setAttribute('transform', `translate(${230 + Math.cos(a) * v * tt},${828 + Math.sin(a) * v * tt + 900 * tt * tt}) rotate(${tt * 720 * (rnd(i + 3) - 0.5)})`); e.setAttribute('opacity', after > 0 && tt < 1.2 ? 1 : 0); }
  for (let i = 0; i < 6; i++) { const e = $('fx_smoke_' + i), tt = Math.max(0, after - 0.05 * i), a = rnd(i + 20) * Math.PI * 2;
    e.setAttribute('transform', `translate(${230 + Math.cos(a) * 120 * Math.sqrt(tt) + 30 * tt},${828 + Math.sin(a) * 70 * Math.sqrt(tt) - 90 * tt}) scale(${0.4 + 1.3 * Math.sqrt(tt)})`);
    e.setAttribute('opacity', (after > 0 ? 0.85 * Math.max(0, 1 - tt / 3.5) : 0).toFixed(3)); }
  const burnt = after > 0.08; disp('stage_police', !burnt); disp('stage_police_burnt', burnt);
  if (burnt) {
    rot('portlashdan_keyin_head', 9 * Math.sin(after * 5)); rot('portlashdan_keyin_torso', 3 * Math.sin(after * 5 + 1));
    rot('portlashdan_keyin_arm_L', 8 * Math.sin(after * 4)); rot('portlashdan_keyin_arm_R', -8 * Math.sin(after * 4 + 1));
    for (let i = 0; i < 4; i++) { const e = $('portlashdan_keyin_smoke_' + i); if (!e) continue; if (!e.dataset.b) e.dataset.b = e.getAttribute('transform');
      const m = /translate\(([-\d.]+),([-\d.]+)\) scale\(([-\d.]+)\)/.exec(e.dataset.b), q = ((after * 0.6 + i * 0.25) % 1);
      e.setAttribute('transform', `translate(${+m[1] + 10 * Math.sin(q * 6 + i)},${+m[2] - 120 * q}) scale(${+m[3] * (0.7 + 0.8 * q)})`); e.setAttribute('opacity', (0.9 * (1 - q)).toFixed(3)); }
  }
  return after;
}
function snow(t) {
  for (let i = 0; i < 90; i++) { const e = $('sn' + i); const sp = 60 + rnd(i) * 80, x0 = rnd(i + 5) * 1080, y = ((rnd(i + 9) * 1920 + t * sp) % 1980) - 30;
    e.setAttribute('cx', (x0 + 26 * Math.sin(t * 1.3 + i)).toFixed(1)); e.setAttribute('cy', y.toFixed(1)); }
}
window.setFrame = (f, beat) => {
  const t = f / 30; let ts = 0, after, s = 1.0, fx = 540, fy = 1080, shake = 0;
  if (beat === 'b1') { ts = 2.75 + t; }
  if (beat === 'b7') { ts = 1.0 + t * (2.9 / 4.2); }
  if (beat === 'b8') { ts = 3.9 + t * 0.95; }
  if (beat === 'b9') { ts = 6.3 + t; }
  after = sceneAt(ts);
  // camera per beat
  if (beat === 'b1') { s = lerp(1.25, 1.45, t / 3.6); fx = 380; fy = 1150; }
  if (beat === 'b7') { s = lerp(1.0, 1.35, sm(t / 4.2)); fx = lerp(540, 380, sm(t / 4.2)); fy = lerp(1080, 1180, sm(t / 4.2)); }
  if (beat === 'b8') { s = 1.35; fx = 380; fy = 1180; }
  if (beat === 'b9') { const p = seg(t, 1.7, 2.4); s = lerp(2.1, 1.4, p); fx = lerp(420, 400, p); fy = lerp(1640, 1000, p); }
  if (after > 0 && after < 0.6) shake = (1 - after / 0.6) * 26;
  cam(s, fx, fy, shake * (f % 2 ? 1 : -1), shake * (rnd(f) - 0.5));
  op('flash', after > 0 ? 0.92 * Math.max(0, 1 - after / 0.28) : 0);
  const st = beat === 'b9' ? back(seg(t, 2.3, 2.6)) : 0;
  op('stamp', beat === 'b9' ? seg(t, 2.3, 2.45) : 0); tr('stamp', `scale(${lerp(1.8, 1, st)})`);
  snow(t + (beat === 'b8' ? 4.2 : beat === 'b9' ? 6.8 : 0));
  subs(beat, t);
};
"""
    page("night", body + f'<g id="snow">{snow}</g>', js, FIREGLOW)

# =====================================================================================================================
# DAY: busy street, the signal + policeman, carriages stop, the lady crosses, newspaper  (b2 b5 b6)
# =====================================================================================================================
def build_day():
    gen.DEFS.clear()
    svg = gen_city.scene("day", cast=True)
    body = svg_inner(svg)
    # second cab on the far lane (faces right), own ids
    hg2 = gen.horse("ot2")
    cg2, _ = gen.person("aravakash2", gen.CABBIE, dict(gen.POSES["aravakash"], arm_L=16, forearm_L=78, hand_L=10, arm_R=-16, forearm_R=-78, hand_R=-10))
    cab2 = (f'<g id="stage_cab2" transform="translate(-300,1490) scale(0.3)"><g transform="translate(-110,-445) scale(0.62)">{cg2}</g>'
            + gen_city.cab("hansom_cab2") + f'<g transform="translate(700,0)">{hg2}</g></g>')
    body = body.replace('<g id="layer_cast">', '<g id="layer_cast">' + cab2, 1)
    # lady stands between the policeman and the lamp
    body = body.replace('<g id="stage_lady" transform="translate(860,', '<g id="stage_lady" transform="translate(560,', 1)
    # explainer badges + newspaper
    badges = (f'<g id="badge_red" opacity="0" transform="translate(620,1000)">' + rect(-230, -62, 460, 124, "#fff7ea", 5, 62) + C(-168, 0, 40, "#e8322a", 4)
              + text(40, 20, "TO'XTA", 56, fill="#d8322b", stroke=0) + "</g>"
              + f'<g id="badge_green" opacity="0" transform="translate(620,1150)">' + rect(-230, -62, 460, 124, "#fff7ea", 5, 62) + C(-168, 0, 40, "#2fb36a", 4)
              + text(40, 20, "YUR", 56, fill="#1f8a4e", stroke=0) + "</g>")
    paper = (f'<g id="paper" opacity="0" transform="translate(540,1020)">'
             + rect(-330, -420, 660, 840, "#f4ecd8", 6, 6) + rect(-300, -390, 600, 110, "#221d1a", 0)
             + text(0, -318, "LONDON KUNDALIGI", 50, fill="#f4ecd8", stroke=0, weight=900)
             + L("M -300,-265 L 300,-265", 3) + text(0, -235, "1868-yil, dekabr", 26, fill="#6b5a4e", stroke=0, weight=600)
             + text(0, -150, "KO'CHADA", 78, fill=INK, stroke=0, weight=900) + text(0, -66, "MO'JIZA!", 92, fill="#c8352f", stroke=0, weight=900)
             + rect(-270, -20, 250, 330, "#e6dcc4", 3)
             + f'<g transform="translate(-145,300) scale(0.27)">' + svg_inner_signal() + "</g>"
             + "".join(L(f"M 10,{y} L 270,{y}", 7, "#b9ad95") for y in range(10, 310, 30))
             + text(0, 380, "Parlament oldida yangi signal", 30, fill="#6b5a4e", stroke=0, weight=700) + "</g>")
    vi = body.index('<rect width="1080" height="1920" fill="url(#vig_')
    body = body[:vi] + badges + body[vi:] + paper
    js = r"""
function cabs(xNear, xFar, runNear, runFar, kNear, kFar) {
  setT('stage_cab', `translate(${xNear},1630) scale(-0.42,0.42)`);   // near lane, faces left
  setT('stage_cab2', `translate(${xFar},1490) scale(0.3)`);          // far lane, faces right
  trot('ot', runNear * 4.4 * Math.PI, kNear); trot('ot2', runFar * 4.4 * Math.PI, kFar);
  rot('hansom_cab_wheel', -runNear * 160, 0, -140); rot('hansom_cab2_wheel', runFar * 160, 0, -140);
}
function signal(stop) { rot('signal_arm_L', 50 * (1 - stop)); rot('signal_arm_R', -50 * (1 - stop)); op('signal_lamp_red', stop); op('signal_lamp_green', 1 - stop); }
function lady(x, ground, sc, t, walk) {
  const bob = walk ? Math.abs(Math.sin(t * 7)) * -6 : 0;
  setT('stage_lady', `translate(${x},${ground - 403 * sc + bob}) scale(${sc})`);
  rot('piyoda_xonim_torso', walk ? 2.5 * Math.sin(t * 7) : 0);
}
window.setFrame = (f, beat) => {
  const t = f / 30;
  rot('politsiyachi_head', 4 * Math.sin(t * 1.3));
  if (beat === 'b2') {
    cam(lerp(1.0, 1.06, t / 5.2), 540, 1150);
    signal(0);
    const xn = 1650 - 260 * t, xf = -420 + 150 * t; cabs(xn, xf, t, t, 1, 1);
    const step = seg(t, 1.3, 1.7) * (1 - seg(t, 2.05, 2.25));
    lady(560 - 10 * step, 1850 - 22 * step, 0.33, t, false);
    rot('piyoda_xonim_head', 10 * Math.sin(t * 3) * seg(t, 2.1, 2.3) * (1 - seg(t, 3.2, 3.6)));
    rot('piyoda_xonim_arm_L', -60 * seg(t, 2.1, 2.25) * (1 - seg(t, 3.0, 3.5))); rot('piyoda_xonim_arm_R', 60 * seg(t, 2.1, 2.25) * (1 - seg(t, 3.0, 3.5)));
    rot('politsiyachi_arm_R', 0); rot('politsiyachi_forearm_R', 0);
    op('badge_red', 0); op('badge_green', 0); op('paper', 0);
  }
  if (beat === 'b5') {
    cam(lerp(1.06, 1.18, sm(t / 5.2)), lerp(540, 420, sm(t / 5.2)), lerp(1150, 1200, sm(t / 5.2)));
    const lever = seg(t, 0.35, 0.85) * (1 - seg(t, 1.6, 2.0));
    rot('politsiyachi_arm_R', 100 * lever); rot('politsiyachi_forearm_R', -30 * lever);
    const stop = seg(t, 0.85, 1.05); signal(stop);
    const kn = eo(t / 2.4), xn = lerp(1750, 1060, kn), xf = lerp(-520, -70, kn);
    cabs(xn, xf, kn * 2.4, kn * 2.4, 1 - seg(t, 1.8, 2.4), 1 - seg(t, 1.8, 2.4));
    lady(560, 1850, 0.33, t, false);
    const br = back(seg(t, 2.35, 2.6)), bg = back(seg(t, 3.45, 3.7));
    op('badge_red', seg(t, 2.35, 2.45)); tr('badge_red', `scale(${0.6 + 0.4 * br})`);
    op('badge_green', seg(t, 3.45, 3.55)); tr('badge_green', `scale(${0.6 + 0.4 * bg})`);
    op('paper', 0);
  }
  if (beat === 'b6') {
    cam(lerp(1.18, 1.1, sm(t / 4.2)), 470, 1220);
    signal(1); cabs(1060, -70, 2.4, 2.4, 0, 0);
    rot('ot_neck', 2 * Math.sin(t * 2)); rot('ot_tail', 8 * Math.sin(t * 2.5));
    rot('politsiyachi_arm_L', -95 * seg(t, 0.1, 0.4)); rot('politsiyachi_forearm_L', -10 * seg(t, 0.1, 0.4));
    const c = seg(t, 0.25, 2.6);
    lady(lerp(560, 470, c), lerp(1850, 1350, c), lerp(0.33, 0.22, c), t, c > 0 && c < 1);
    op('badge_red', 1 - seg(t, 0, 0.3)); op('badge_green', 1 - seg(t, 0, 0.3));
    const pp = back(seg(t, 2.0, 2.45));
    op('paper', seg(t, 2.0, 2.1)); tr('paper', `rotate(${lerp(-28, -4, pp)}) scale(${lerp(0.2, 1, pp)})`);
  }
  subs(beat, t);
};
"""
    page("day", body, js)

def svg_inner_signal():
    return gen_city.signal("day", x=0, y=0, k=1.0).replace('id="', 'id="paper_')

# =====================================================================================================================
# KNIGHT: John Peake Knight presents his drawing in front of Parliament  (b3)
# =====================================================================================================================
def build_knight():
    gen.DEFS.clear()
    svg = gen_city.scene("day", cast=False)
    body = svg_inner(svg)
    body = body.replace('<g id="knight_signal"', '<g id="knight_signal" style="display:none"', 1)
    kg, kgnd = gen.person("jon_nayt", gen.KNIGHT, dict(gen.POSES["jon_nayt"], arm_L=0, forearm_L=0, hand_L=0))
    knight = f'<g id="knight" transform="translate(740,{1980 - kgnd*1.05:.1f}) scale(1.05)">{kg}</g>'
    bp = '<g id="blueprint" opacity="0" transform="translate(300,860) rotate(-5)">' + rect(-230, -170, 460, 340, "#2f5f9e", 6, 8)
    for x in range(-210, 230, 40): bp += L(f"M {x},-160 L {x},160", 1.2, "#5c86bf")
    for y in range(-150, 170, 40): bp += L(f"M -220,{y} L 220,{y}", 1.2, "#5c86bf")
    bp += (L("M 0,150 L 0,-90 M -16,-90 L 16,-90 M -110,-70 L 110,-70 M -22,-150 L 22,-150 L 22,-96 L -22,-96 Z", 6, "#f3f7ff")
           + C(0, -123, 14, "none", 4, ' stroke="#f3f7ff"') + L("M -40,150 L 40,150 M -60,110 L -110,-60", 4, "#f3f7ff")
           + text(120, 130, "1868", 34, fill="#f3f7ff", stroke=0) + text(-120, -110, "J.P.N.", 26, fill="#f3f7ff", stroke=0, weight=600) + "</g>")
    tag = ('<g id="nametag" opacity="0" transform="translate(60,1540)">' + rect(0, 0, 560, 140, "#221d1a", 0, 18)
           + rect(0, 0, 14, 140, "#d9a845", 0) + text(40, 62, "Jon Peyk Nayt", 52, fill="#f3ead8", anchor="start", stroke=0)
           + text(40, 112, "temir yo'l muhandisi", 34, fill="#d9a845", anchor="start", stroke=0, weight=600) + "</g>")
    js = r"""
window.setFrame = (f, beat) => {
  const t = f / 30;
  cam(lerp(1.12, 1.2, t / 4.8), lerp(700, 640, t / 4.8), lerp(900, 940, t / 4.8));
  setT('knight', baseOf('knight') + ` translate(${lerp(260, 0, eo(t / 0.7))},0)`);
  const g = seg(t, 0.8, 1.3);
  rot('jon_nayt_arm_R', 125 * g + 5 * Math.sin(t * 3) * g); rot('jon_nayt_forearm_R', -30 * g); rot('jon_nayt_hand_R', -15 * g);
  rot('jon_nayt_head', -5 * g + 2 * Math.sin(t * 2.5)); rot('jon_nayt_torso', -2 * g);
  rot('jon_nayt_arm_L', -10 * Math.sin(t * 1.7) * 0.3); rot('jon_nayt_forearm_L', 70); rot('jon_nayt_hand_L', 15);
  const b = back(seg(t, 1.1, 1.5)); op('blueprint', seg(t, 1.1, 1.2)); tr('blueprint', `scale(${0.3 + 0.7 * b})`);
  op('nametag', seg(t, 0.4, 0.7)); tr('nametag', `translate(${lerp(-80, 0, eo((t - 0.4) / 0.4))},0)`);
  subs(beat, t);
};
"""
    page("knight", body + knight + bp, js, overlay=tag)

# =====================================================================================================================
# SEMAPHORE: railway signal (left) and the street signal (right) move together  (b4)
# =====================================================================================================================
def build_semaphore():
    gen.DEFS.clear()
    sky = f'<rect width="1080" height="1920" fill="{gen_city.grad("semsky", [(0, "#8ec0ea"), (1, "#f4e3c0")])}"/>'
    left = '<g clip-path="url(#leftclip)">' + f'<rect x="0" y="1500" width="540" height="420" fill="{shade("#9b8a70")}"/>'
    for x in range(-20, 560, 46): left += rect(x, 1612, 26, 36, "#6b4a2a", 2.5)
    left += L("M 0,1616 L 540,1616 M 0,1644 L 540,1644", 7, "#5b5f66")
    # lattice mast + one arm + lamp
    mx = 300
    mast = P(f"M {mx-22},1600 L {mx-12},700 L {mx+12},700 L {mx+22},1600 Z", "#3a3f46", 3)
    for y in range(720, 1600, 60): mast += L(f"M {mx-20 + (y-700)*0.011:.0f},{y} L {mx+20 - (y-700)*0.011:.0f},{y+50}", 2.5, "#7a8089")
    arm = G("rail_arm", mx - 14, 760, P("M 0,-14 L -230,-16 L -236,16 L 0,14 Z", "#c8352f") + L("M -190,-14 L -190,14", 8, "#f3ead8"))
    lamp = G("rail_lamp", mx + 30, 830, rect(-24, -30, 48, 60, "#1f2a24", 3) + G("rail_lamp_red", 0, 0, E(0, 0, 16, 18, "#e8322a", 2.5)) +
             G("rail_lamp_green", 0, 0, E(0, 0, 16, 18, "#2fb36a", 2.5), extra=' opacity="0"'))
    left += mast + arm + lamp + C(mx, 690, 14, "#d9a845", 3)
    # little steam train crossing the left half
    loco = ('<g id="loco" transform="translate(-500,1600)">' + rect(0, -180, 300, 120, "#2a2a30", 4, 10) + rect(200, -260, 120, 200, "#7a2a2a", 4, 6)
            + rect(40, -250, 46, 80, "#2a2a30", 4) + rect(218, -240, 80, 60, "#f2d68a", 3)
            + "".join(C(x, -50, 46, "#3a3f46", 4) + C(x, -50, 10, "#d9a845", 2) for x in (60, 170, 270))
            + "".join(f'<circle id="steam{i}" cx="63" cy="-270" r="30" fill="#f4f1ea" opacity="0"/>' for i in range(6)) + "</g>")
    left += loco + text(270, 330, "POYEZD", 64, fill="#ffffff") + "</g>"
    right = '<g clip-path="url(#rightclip)">' + rect(540, 1600, 540, 320, "#cdc4b2", 3) + rect(540, 1590, 540, 16, "#a59e90", 3)
    right += f'<g transform="translate(270,0)">{gen_city.signal("day", x=540, y=1600, k=0.95)}</g>'
    right += text(810, 330, "KO'CHA", 64, fill="#ffffff") + "</g>"
    divider = rect(532, 0, 16, 1920, "#f3ead8", 4)
    labels = ('<g id="lbl_day" opacity="0">' + rect(240, 1730, 600, 100, "#221d1a", 0, 50) + text(540, 1797, "kunduzi — qanotchalar", 46, fill="#f3ead8", stroke=0) + "</g>"
              '<g id="lbl_night" opacity="0">' + rect(190, 1730, 700, 100, "#221d1a", 0, 50) + text(540, 1797, "kechasi — gaz chiroq", 46, fill="#ffd34a", stroke=0) + "</g>")
    night = '<rect id="nightveil" width="1080" height="1920" fill="#0d1530" opacity="0"/>'
    glows = ('<circle id="glow_rail" cx="330" cy="830" r="90" fill="#3aff8a" opacity="0"/>'
             '<circle id="glow_street" cx="810" cy="686" r="110" fill="#3aff8a" opacity="0"/>')
    defs = ('<clipPath id="leftclip"><rect x="0" y="0" width="540" height="1920"/></clipPath>'
            '<clipPath id="rightclip"><rect x="540" y="0" width="540" height="1920"/></clipPath>')
    js = r"""
window.setFrame = (f, beat) => {
  const t = f / 30;
  setT('loco', `translate(${lerp(-420, 760, t / 2.4)},1600)`);
  for (let i = 0; i < 6; i++) { const q = ((t * 1.6 + i / 6) % 1), e = $('steam' + i);
    e.setAttribute('cx', (63 - 160 * q).toFixed(1)); e.setAttribute('cy', (-270 - 140 * q).toFixed(1)); e.setAttribute('r', (24 + 40 * q).toFixed(1));
    e.setAttribute('opacity', (t < 2.6 ? 0.8 * (1 - q) : 0).toFixed(3)); }
  const go = seg(t, 1.6, 2.1);
  rot('rail_arm', -40 * go);               // both arms lower together
  rot('signal_arm_L', 50 * go); rot('signal_arm_R', -50 * go);
  op('rail_lamp_red', 1 - go); op('rail_lamp_green', go); op('signal_lamp_red', 1 - go); op('signal_lamp_green', go);
  op('lbl_day', seg(t, 1.9, 2.1) * (1 - seg(t, 3.3, 3.45)));
  const n = seg(t, 3.3, 3.9); op('nightveil', 0.62 * n); op('lbl_night', seg(t, 3.6, 3.8));
  op('glow_rail', 0.55 * n * (0.9 + 0.1 * Math.sin(t * 20))); op('glow_street', 0.55 * n * (0.9 + 0.1 * Math.sin(t * 17 + 1)));
  cam(1.0, 540, 960);
  subs(beat, t);
};
"""
    page("semaphore", sky + left + right + divider + night + glows + labels, js, defs)

# =====================================================================================================================
# STOVE: the kitchen gas-stove analogy, then the lantern cut-away  (b10)
# =====================================================================================================================
def build_stove():
    gen.DEFS.clear()
    wall = f'<rect width="1080" height="1920" fill="{shade("#e9dcc4")}"/>'
    for y in range(0, 1300, 90):
        for x in range(0 if (y // 90) % 2 == 0 else -45, 1080, 90):
            wall += f'<rect x="{x+3}" y="{y+3}" width="84" height="84" rx="6" fill="#f1e8d6" stroke="#d6c7ab" stroke-width="2"/>'
    floor = rect(0, 1300, 1080, 620, "#b98b5a", 0) + "".join(L(f"M 0,{y} L 1080,{y}", 2, "#a37a4c") for y in range(1340, 1920, 60))
    stove = ('<g id="stove">' + rect(230, 900, 620, 480, "#f6f3ec", 6, 18) + rect(210, 870, 660, 50, "#dcd6ca", 5, 10)
             + rect(270, 1010, 540, 300, "#3a3f46", 5, 10) + rect(300, 1040, 480, 240, "#22262b", 3, 6) + L("M 320,1060 L 400,1060", 6, "#4a5058")
             + "".join(G(f"knob{i}", 330 + i * 140, 960, C(0, 0, 24, "#2a2a30", 4) + L("M 0,0 L 0,-18", 5, "#f6f3ec")) for i in range(4))
             + E(400, 865, 110, 18, "#2a2a30", 4) + E(400, 860, 70, 10, "#4a5058", 3) + E(680, 865, 110, 18, "#2a2a30", 4) + E(680, 860, 70, 10, "#4a5058", 3)
             + "</g>")
    gas = "".join(f'<path id="gas{i}" d="M 0,0 q 20,-30 0,-60 q -20,-30 0,-60" fill="none" stroke="#9fe08a" stroke-width="14" stroke-linecap="round" opacity="0"/>' for i in range(8))
    match = ('<g id="match" opacity="0" transform="translate(900,700) rotate(-35)">' + rect(-6, 0, 12, 220, "#e8c48a", 3, 4)
             + E(0, -6, 14, 18, "#c8352f", 3) + '<g id="match_flame" opacity="0">' + PF("M 0,-60 Q 22,-26 0,-14 Q -22,-26 0,-60 Z", "#ffb347") + PF("M 0,-46 Q 10,-28 0,-20 Q -10,-28 0,-46 Z", "#fff3b0") + "</g></g>")
    puf = burst("puf", 400, 830) + '<g id="puf_text" opacity="0">' + text(400, 640, "PUF!", 130, fill="#ffd34a", weight=900, stroke=14) + "</g>"
    # lantern cut-away diagram
    lan = ('<g id="diagram" opacity="0"><rect width="1080" height="1920" fill="#f3ead8"/>'
           + rect(340, 640, 400, 520, "#1f2a24", 8, 10) + rect(380, 690, 320, 420, "#cfe6f2", 5, 6)
           + '<rect id="gasfill" x="383" y="1107" width="314" height="0" fill="#9fe08a" opacity="0.75"/>'
           + P("M 480,1160 L 480,1500 L 600,1500 L 600,1160", "none", 0) + rect(510, 1160, 60, 360, "#6b6f76", 5)
           + P("M 300,640 L 780,640 L 540,520 Z", "#1f2a24", 6)
           + '<g id="spark" opacity="0">' + f'<polygon points="{star_pts(6, 0.35)}" transform="translate(540,1050) scale(46)" fill="#fff3b0" stroke="{INK}" stroke-width="0.06"/>' + "</g>"
           + burst("boom2", 540, 900)
           + '<g id="lbl_gas" opacity="0">' + text(860, 900, "gaz", 64, fill="#3a8a3a", stroke=8) + L("M 800,900 L 700,960", 6, "#3a8a3a") + "</g>"
           + '<g id="lbl_spark" opacity="0">' + text(230, 1140, "uchqun", 64, fill="#d08a1a", stroke=8) + L("M 330,1120 L 500,1060", 6, "#d08a1a") + "</g>"
           + '<g id="boom_text" opacity="0">' + text(540, 470, "BUMM!", 150, fill="#ff8a2a", weight=900, stroke=16) + "</g>"
           + text(540, 1650, "Chiroq qutisi", 60, fill=INK, stroke=0) + "</g>")
    js = r"""
window.setFrame = (f, beat) => {
  const t = f / 30;
  cam(lerp(1.0, 1.08, t / 3.6), 540, 980);
  rot('knob0', -90 * seg(t, 0.3, 0.6));
  for (let i = 0; i < 8; i++) { const e = $('gas' + i), q = ((t * 0.7 + i / 8) % 1);
    e.setAttribute('transform', `translate(${400 + (i % 3 - 1) * 40 + 30 * Math.sin(q * 6 + i)},${850 - 260 * q}) scale(${0.6 + 0.8 * q})`);
    e.setAttribute('opacity', (seg(t, 0.6, 1.0) * (1 - q) * 0.8 * (1 - seg(t, 2.75, 2.85))).toFixed(3)); }
  const m = seg(t, 1.5, 2.1); op('match', m * (1 - seg(t, 3.3, 3.5)));
  setT('match', `translate(${lerp(980, 560, eo(m))},${lerp(760, 720, m) + (t > 2.3 && t < 2.45 ? 20 : 0)}) rotate(-35)`);
  op('match_flame', t > 2.45 ? 1 : 0);
  const pa = t - 2.75, pb = $('puf');
  if (pa > 0 && pa < 0.6) { const q = Math.sqrt(pa / 0.6); pb.setAttribute('transform', `translate(400,830) scale(${30 + 260 * q}) rotate(${pa * 50})`); pb.setAttribute('opacity', (1 - sm(pa / 0.6)).toFixed(3)); } else pb.setAttribute('opacity', 0);
  op('puf_text', pa > 0 ? 1 - seg(pa, 0.7, 0.9) : 0); tr('puf_text', `translate(400,640) scale(${0.6 + 0.4 * back(seg(pa, 0, 0.2))}) translate(-400,-640)`);
  op('flash', pa > 0 ? 0.6 * Math.max(0, 1 - pa / 0.2) : 0);
  // lantern cut-away from 3.6 s
  const d = seg(t, 3.5, 3.8); op('diagram', d);
  const fill = seg(t, 3.9, 5.6); const gf = $('gasfill'); gf.setAttribute('height', (414 * fill).toFixed(1)); gf.setAttribute('y', (1107 - 414 * fill).toFixed(1));
  op('lbl_gas', seg(t, 4.4, 4.6)); op('spark', t > 5.7 && t < 6.05 ? (Math.sin(t * 60) > 0 ? 1 : 0.3) : 0); op('lbl_spark', seg(t, 5.7, 5.85) * (1 - seg(t, 6.1, 6.2)));
  const ba = t - 6.05, bb = $('boom2');
  if (ba > 0 && ba < 0.7) { const q = Math.sqrt(ba / 0.7); bb.setAttribute('transform', `translate(540,900) scale(${40 + 380 * q}) rotate(${ba * 60})`); bb.setAttribute('opacity', (1 - sm(ba / 0.7)).toFixed(3)); } else bb.setAttribute('opacity', 0);
  op('boom_text', ba > 0 ? 1 : 0); tr('boom_text', `translate(540,470) scale(${0.5 + 0.5 * back(seg(ba, 0, 0.2))}) translate(-540,-470)`);
  if (ba > 0) { op('flash', 0.85 * Math.max(0, 1 - ba / 0.25)); const sh = Math.max(0, 1 - ba / 0.5) * 22; cam(1.0, 540, 960, sh * (f % 2 ? 1 : -1), sh * (rnd(f) - 0.5)); }
  else if (t > 3.5) cam(1.0, 540, 960);
  subs(beat, t);
};
"""
    page("stove", wall + floor + stove + gas + match + puf + lan, js)

# =====================================================================================================================
# CALENDAR: 1869 -> 1920s, then the electric traffic light  (b11)
# =====================================================================================================================
def build_calendar():
    gen.DEFS.clear()
    bg = f'<rect width="1080" height="1920" fill="{shade("#efe2c6")}"/>'
    cal = ('<g id="cal">' + rect(290, 620, 500, 560, "#f8f3e8", 6, 14) + rect(290, 620, 500, 140, "#c8352f", 6, 14) + rect(290, 700, 500, 60, "#c8352f", 0)
           + "".join(C(x, 640, 14, "#221d1a", 3) for x in (380, 540, 700))
           + text(540, 725, "YIL", 64, fill="#f8f3e8", stroke=0, weight=900)
           + '<text id="year" x="540" y="1040" text-anchor="middle" font-family="DejaVu Sans, Arial" font-weight="900" font-size="190" fill="#221d1a">1869</text></g>')
    pages = "".join(f'<g id="pg{i}" opacity="0">' + rect(-250, -210, 500, 420, "#f8f3e8", 5, 6) + "</g>" for i in range(10))
    # 1920s electric light: pole + 3-lamp head
    tl = ('<g id="elight" opacity="0" transform="translate(540,1700)">' + rect(-16, -900, 32, 900, "#3a3f46", 4) + rect(-70, -1240, 140, 360, "#22262b", 6, 20)
          + "".join(G(f"el_{n}", 0, y, C(0, 0, 46, c, 5)) for n, y, c in (("r", -1180, "#5a1e1e"), ("a", -1060, "#5a4a1e"), ("g", -940, "#1e4a2e")))
          + "".join(f'<circle id="elg_{n}" cx="0" cy="{y}" r="52" fill="{c}" opacity="0"/>' for n, y, c in (("r", -1180, "#ff3b30"), ("a", -1060, "#ffc23a"), ("g", -940, "#34d27a")))
          + "</g>")
    era = ('<g id="era" opacity="0">' + rect(200, 1760, 680, 110, "#221d1a", 0, 55) + text(540, 1835, "1920-YILLAR · ELEKTR", 52, fill="#ffd34a", stroke=0) + "</g>")
    bolt = '<g id="bolt" opacity="0"><polygon points="800,520 740,650 790,650 730,800 860,610 805,610 860,520" fill="#ffd34a" stroke="#221d1a" stroke-width="6"/></g>'
    js = r"""
window.setFrame = (f, beat) => {
  const t = f / 30;
  cam(1.0, 540, 960);
  const k = eo(seg(t, 0.15, 2.4) * 1.0); const y = Math.round(lerp(1869, 1925, k));
  $('year').textContent = t > 2.45 ? '1920-lar' : String(y);
  $('year').setAttribute('font-size', t > 2.45 ? 150 : 190);
  for (let i = 0; i < 10; i++) { const s = 0.2 + i * 0.22, q = (t - s) / 0.6, e = $('pg' + i);
    if (q > 0 && q < 1) { e.setAttribute('opacity', (1 - q).toFixed(3)); e.setAttribute('transform', `translate(${540 + 500 * q * (i % 2 ? 1 : -1)},${970 - 300 * q + 900 * q * q}) rotate(${(i % 2 ? 1 : -1) * 160 * q})`); }
    else e.setAttribute('opacity', 0); }
  const out = seg(t, 2.7, 3.0); tr('cal', `translate(0,${-900 * out})`); op('cal', 1 - out);
  const inn = eo(seg(t, 2.8, 3.3)); op('elight', seg(t, 2.8, 2.9)); setT('elight', `translate(540,${1700 + 600 * (1 - inn)})`);
  const c = t < 3.5 ? 'r' : t < 3.9 ? 'a' : 'g';
  for (const n of ['r', 'a', 'g']) op('elg_' + n, t > 3.2 && n === c ? 0.95 : 0);
  op('era', seg(t, 3.3, 3.5)); op('bolt', seg(t, 3.25, 3.35) * (0.8 + 0.2 * Math.sin(t * 30)));
  subs(beat, t);
};
"""
    page("calendar", bg + cal + pages + tl + bolt + era, js)

# =====================================================================================================================
# MODERN: today's driver at a red light  (b12)
# =====================================================================================================================
def modern_car(cid="car"):
    """modern hatchback, side view facing right, origin = ground under the middle; window is a hole (driver shows)"""
    body = (f'<path d="M -330,-70 Q -340,-150 -300,-170 L -200,-180 Q -140,-300 -20,-300 L 120,-300 Q 200,-290 260,-200 L 330,-180 Q 370,-170 370,-110 L 370,-70 Z '
            f'M -150,-190 Q -110,-280 -20,-282 L 110,-282 Q 170,-276 214,-196 Z" fill-rule="evenodd" fill="{shade("#c8352f")}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>')
    glass = PF("M -150,-190 Q -110,-280 -20,-282 L 110,-282 Q 170,-276 214,-196 Z", "#bfe3f5", ' opacity="0.28"') + L("M 40,-282 L 40,-192", 6)
    trim = L("M -330,-120 L 370,-120", 4, mul("#c8352f", 0.7)) + rect(330, -160, 40, 26, "#fff3c4", 3, 6) + rect(-338, -150, 24, 30, "#ff4a3a", 3, 4)
    wheels = "".join(G(f"{cid}_wheel_{i}", x, -62, C(0, 0, 62, "#22262b", 5) + C(0, 0, 32, "#b9bec6", 4) + L("M -28,0 L 28,0 M 0,-28 L 0,28", 4, "#6b7078")) for i, x in enumerate((-210, 220)))
    return body, glass + trim + wheels

def build_modern():
    gen.DEFS.clear()
    sky = f'<rect width="1080" height="1920" fill="{gen_city.grad("msky", [(0, "#7fb8ea"), (1, "#e9f1f7")])}"/>'
    city = ""
    R = random.Random(7)
    for i, x in enumerate(range(-40, 1100, 170)):
        h = R.randint(600, 1050); col = R.choice(["#9aa8b8", "#b8c3cf", "#8796a8", "#c7cfd8"])
        city += rect(x, 1300 - h, 160, h, col, 4)
        for wy in range(1300 - h + 40, 1260, 70):
            for wx in range(x + 18, x + 150, 46): city += rect(wx, wy, 28, 40, "#dfeef8" if (wx + wy) % 3 else "#a9c7e0", 0)
    road = rect(0, 1300, 1080, 620, "#4a4f57", 0) + rect(0, 1300, 1080, 70, "#b9bec6", 4) + "".join(rect(x, 1640, 110, 16, "#f3ead8", 0) for x in range(-40, 1100, 220))
    light = ('<g id="mlight" transform="translate(900,1380)">' + rect(-14, -820, 28, 820, "#3a3f46", 4) + rect(-62, -1130, 124, 330, "#22262b", 6, 18)
             + "".join(C(0, y, 40, c, 5) for y, c in ((-1070, "#5a1e1e"), (-965, "#5a4a1e"), (-860, "#1e4a2e")))
             + '<circle id="ml_r" cx="0" cy="-1070" r="44" fill="#ff3b30"/><circle id="ml_r_glow" cx="0" cy="-1070" r="90" fill="#ff3b30" opacity="0.25"/>'
             + '<circle id="ml_g" cx="0" cy="-860" r="44" fill="#34d27a" opacity="0"/><circle id="ml_g_glow" cx="0" cy="-860" r="90" fill="#34d27a" opacity="0"/>'
             + '<g id="ml_spark" opacity="0">' + f'<polygon points="{star_pts(6, 0.35)}" transform="translate(48,-1110) scale(30)" fill="#fff3b0" stroke="{INK}" stroke-width="0.08"/>' + "</g></g>")
    dg, dgnd = gen.person("haydovchi", gen.DRIVER, dict(gen.POSES["bugungi_haydovchi"], arm_L=-60, forearm_L=-70, arm_R=60, forearm_R=70))
    cbody, cdet = modern_car()
    car = (f'<g id="car" transform="translate(420,1560)">' + f'<g clip-path="url(#winclip)"><rect x="-160" y="-290" width="390" height="110" fill="#5d6a78"/><g id="driver" transform="translate(30,-75) scale(0.5)">{dg}</g></g>'
           + rect(-120, -230, 260, 170, "#3a3f46", 0) + f'<g id="driver_front" transform="translate(30,-75) scale(0.5)"></g>' + cbody + cdet + "</g>")
    # the driver is drawn behind the body; only the head/shoulders show through the window
    car = car.replace(rect(-120, -230, 260, 170, "#3a3f46", 0), "")
    sweat = '<g id="sweat" opacity="0">' + P("M 0,-12 Q 8,0 6,6 Q 0,12 -6,6 Q -8,0 0,-12 Z", "#a8d8ea", 2) + "</g>"
    js = r"""
window.setFrame = (f, beat) => {
  const t = f / 30;
  cam(lerp(1.0, 1.1, sm(t / 4.0)), lerp(540, 620, sm(t / 4.0)), 1150);
  // bored driver: head bob, drums on the wheel
  rot('haydovchi_head', 5 * Math.sin(t * 1.6) + (t > 2.6 && t < 3.6 ? -14 * seg(t, 2.6, 2.8) : 0));
  rot('haydovchi_forearm_L', -70 + 12 * Math.max(0, Math.sin(t * 9)) * (t < 2.6 ? 1 : 0));
  // the light flickers once (tension) ... and just turns green
  const flick = t > 2.7 && t < 3.3 ? (Math.sin(t * 50) > 0 ? 1 : 0.25) : 1;
  op('ml_r', t < 4.1 ? flick : 0); op('ml_r_glow', t < 4.1 ? 0.25 * flick : 0);
  op('ml_spark', t > 2.75 && t < 2.95 ? 1 : 0);
  op('ml_g', t >= 4.1 ? 1 : 0); op('ml_g_glow', t >= 4.1 ? 0.25 : 0);
  const sweat = $('sweat'); op('sweat', t > 2.8 && t < 4.3 ? 1 : 0); sweat.setAttribute('transform', `translate(${420 + 30 + 34},${1560 - 75 - 0.5 * 320 + 40 * seg(t, 2.8, 4.0)})`);
  const go = Math.max(0, t - 4.4); setT('car', `translate(${420 + 260 * go * go},1560)`);
  rot('car_wheel_0', go * go * 400); rot('car_wheel_1', go * go * 400);
  subs(beat, t);
};
"""
    page("modern", sky + city + road + light + car + sweat, js, '<clipPath id="winclip"><path d="M -150,-190 Q -110,-280 -20,-282 L 110,-282 Q 170,-276 214,-196 Z"/></clipPath>')

# =====================================================================================================================
# END CARD  (b13)
# =====================================================================================================================
def build_end():
    gen.DEFS.clear()
    bg = f'<rect width="1080" height="1920" fill="{shade("#f3ead8")}"/>' + "".join(C(x, y, 6, "#e3d4b6") for x in range(60, 1080, 120) for y in range(80, 1920, 120))
    cbody, cdet = modern_car("ecar")
    car = f'<g id="ecar" transform="translate(-400,1250) scale(0.9)">{cbody}{cdet}</g>'
    title = ('<g id="title" opacity="0">' + text(540, 700, "MASHINA", 140, fill="#c8352f", weight=900, stroke=16) + text(540, 860, "TARIXI", 160, fill="#221d1a", weight=900, stroke=0) + "</g>")
    btn = ('<g id="sub_btn" opacity="0" transform="translate(540,1500)">' + rect(-300, -80, 600, 160, "#c8352f", 6, 80)
           + text(50, 22, "OBUNA BO'L", 62, fill="#ffffff", stroke=0, weight=900)
           + P("M -250,-30 Q -250,-62 -224,-62 Q -198,-62 -198,-30 L -194,10 L -254,10 Z", "#ffd34a", 4) + C(-224, 22, 9, "#ffd34a", 3) + "</g>")
    js = r"""
window.setFrame = (f, beat) => {
  const t = f / 30;
  cam(1.0, 540, 960);
  const k = eo(seg(t, 0, 0.8)); setT('ecar', `translate(${lerp(-420, 540, k)},1250) scale(0.9)`);
  rot('ecar_wheel_0', 720 * k); rot('ecar_wheel_1', 720 * k);
  op('title', seg(t, 0.4, 0.6)); tr('title', `translate(540,840) scale(${0.6 + 0.4 * back(seg(t, 0.4, 0.75))}) translate(-540,-840)`);
  op('sub_btn', seg(t, 0.9, 1.05)); tr('sub_btn', `scale(${(0.7 + 0.3 * back(seg(t, 0.9, 1.2))) * (1 + 0.05 * Math.sin(Math.max(0, t - 1.3) * 7))})`);
  subs(beat, t);
};
"""
    page("end", bg + car + title + btn, js)

if __name__ == "__main__":
    for fn in (build_night, build_day, build_knight, build_semaphore, build_stove, build_calendar, build_modern, build_end):
        fn()
