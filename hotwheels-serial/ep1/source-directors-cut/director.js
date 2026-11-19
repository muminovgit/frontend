// Director's-cut layer: grain, handheld drift, 2.5D tilt, whip cuts, inserts, kinetic slams, grade, letterbox.
(function () {
  const $ = id => document.getElementById(id);
  const cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const eo = x => 1 - Math.pow(1 - x, 3);
  const lerp = (a, b, x) => a + (b - a) * x;
  const SCN = TL.scenes, L = {}; TL.lines.forEach(l => L[l.id] = l);
  const mid = (id, f) => L[id].start + (L[id].end - L[id].start) * f;

  // ---------- DOM
  const css = document.createElement('style');
  css.textContent = `
  #grade{position:absolute;inset:0;z-index:5;pointer-events:none;mix-blend-mode:soft-light}
  #leak{position:absolute;inset:-20%;z-index:6;pointer-events:none;mix-blend-mode:screen;opacity:0}
  #grain{position:absolute;inset:0;width:720px;height:1280px;z-index:7;pointer-events:none;opacity:.13;mix-blend-mode:overlay}
  .bar{position:absolute;left:0;right:0;height:0;background:#000;z-index:8}
  #barT{top:0}#barB{bottom:0}
  .ins{position:absolute;inset:0;display:none;overflow:hidden;z-index:4;background:#000}
  .ins img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:contrast(1.12) saturate(.9)}
  #slam{position:absolute;left:0;right:0;top:46%;transform:translateY(-50%);text-align:center;z-index:9;opacity:0;
    font-family:'Inter Display',Inter,sans-serif;font-weight:900;letter-spacing:-.04em;line-height:.9;
    text-shadow:-5px 0 rgba(255,0,70,.75),5px 0 rgba(0,220,255,.75),0 8px 40px rgba(0,0,0,.8)}
  #tc{position:absolute;right:30px;bottom:150px;z-index:9;font-family:'JetBrains Mono',monospace;font-size:18px;color:rgba(255,255,255,.55);letter-spacing:.12em}
  #rec{display:inline-block;width:12px;height:12px;border-radius:50%;background:#ff3434;margin-right:8px;vertical-align:middle}
  `;
  document.head.appendChild(css);
  const cam = $('cam');
  const add = html => { const d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; };
  const INS = [
    // id, img, start, end, objectPosition, scale0, scale1, grade
    ['iEye', 'c_eye.jpg', mid('n1', .25), mid('n1', .25) + 0.55, '42% 30%', 2.6, 2.9],
    ['iMoney', 'c_money.jpg', L.o1.start + 0.55, L.o1.start + 1.35, '50% 100%', 2.0, 2.2],
    ['iPink', 'c_pink.jpg', L.n9.start - 0.05, L.n9.start + 0.75, '50% 45%', 1.15, 1.35],
    ['iCrowd', 'c_crowd.jpg', mid('n18', .55), SCN.S12[1], '35% 40%', 1.1, 1.3],
    ['iHall', 'c_hall.jpg', SCN.S14[0], SCN.S14[0] + 1.1, '50% 50%', 1.0, 1.12],
  ];
  INS.forEach(([id, src, a, b, op]) => {
    const e = add(`<div class="ins" id="${id}"><img src="${src}" style="object-position:${op}"></div>`);
    cam.appendChild(e);
  });
  cam.appendChild(add('<div id="grade"></div>'));
  cam.appendChild(add('<div id="leak"></div>'));
  document.body.appendChild(add('<canvas id="grain" width="360" height="640"></canvas>'));
  document.body.appendChild(add('<div class="bar" id="barT"></div>'));
  document.body.appendChild(add('<div class="bar" id="barB"></div>'));
  document.body.appendChild(add('<div id="slam"></div>'));
  document.body.appendChild(add('<div id="tc"><span id="rec"></span><span id="tct"></span></div>'));

  const SLAMS = [ // text, start, dur, color, size
    ['$150 000', mid('n1', .62), 0.75, '#ff4fa3', 150],
    ['50 000', L.o1.start + 0.6, 0.7, '#fff', 170],
    ['PUSHTI', L.n9.start, 0.7, '#ff4fa3', 170],
        ['SURATGA<br>OLDI', TL.lines.find(l => l.id === 'n19').start + (L.n19.end - L.n19.start) * .62, 0.75, '#ff3434', 120],
    ['QAYERDAN?', L.n21.end - 0.2, 0.8, '#fff', 120],
  ];
  // grade colour per scene
  const GRADE = { S1: 'rgba(0,90,120,.35)', S3: 'rgba(255,150,40,.35)', S4: 'rgba(255,150,40,.35)', S5: 'rgba(255,140,40,.32)',
    S6: 'rgba(255,120,30,.3)', S7: 'rgba(255,60,140,.28)', S9: 'rgba(255,40,120,.2)', S10: 'rgba(255,40,120,.22)',
    S12: 'rgba(120,100,60,.35)', S13: 'rgba(0,80,90,.4)', S14: 'rgba(0,70,160,.4)', S15: 'rgba(0,70,160,.45)' };
  const LEAK = ['S3', 'S4', 'S5', 'S7'];

  function rnd(n) { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); }
  const g = $('grain').getContext('2d'); const img = g.createImageData(360, 640);
  function grain(frame) {
    let s = (frame * 2654435761) >>> 0;
    for (let i = 0; i < img.data.length; i += 4) {
      s ^= s << 13; s ^= s >>> 17; s ^= s << 5; s >>>= 0;
      const v = s & 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
  }
  const base = window.render;
  window.render = function (t) {
    base(t);
    const frame = Math.round(t * 30);
    // current scene
    let cid = 'S1', ca = 0; for (const id in SCN) if (t >= SCN[id][0] && t < SCN[id][1]) { cid = id; ca = SCN[id][0]; }
    // 2.5D tilt on scene image
    const scEl = $(cid), bg = scEl && scEl.querySelector('.bg');
    if (bg) {
      const p = cl((t - ca) / (SCN[cid][1] - ca)); const dir = (parseInt(cid.slice(1)) % 2) ? 1 : -1;
      bg.style.transform = `perspective(1100px) rotateY(${dir * lerp(-2.2, 2.2, p)}deg) rotateX(${lerp(1.2, -1.2, p)}deg) ` + bg.style.transform;
    }
    // handheld drift (Safdie) + whip-pan in on each cut
    const sinceCut = t - ca, wp = cl(sinceCut / 0.2);
    const dx = Math.sin(t * 1.3) * 5 + Math.sin(t * 3.1) * 2, dy = Math.cos(t * 1.7) * 4, rot = Math.sin(t * 0.9) * 0.35;
    const whip = cid === 'S1' ? 0 : (1 - eo(wp));
    cam.style.transform += ` translate(${dx + whip * -160}px,${dy}px) rotate(${rot}deg) scale(1.03)`;
    cam.style.filter = `contrast(1.08) saturate(1.06) blur(${whip * 9}px)`;
    // inserts
    INS.forEach(([id, src, a, b, op, s0, s1]) => {
      const on = t >= a && t < b; const e = $(id); e.style.display = on ? 'block' : 'none';
      if (on) { const p = cl((t - a) / (b - a)); e.firstChild.style.transformOrigin = op; e.firstChild.style.transform = `scale(${lerp(s0, s1, p)})`; }
    });
    // grade + light leak
    $('grade').style.background = GRADE[cid] || 'transparent';
    const lk = LEAK.includes(cid) ? 0.35 + 0.25 * Math.sin(t * 0.8) : 0;
    const lx = 30 + 40 * Math.sin(t * 0.21), ly = 20 + 30 * Math.cos(t * 0.17);
    $('leak').style.opacity = lk;
    $('leak').style.background = `radial-gradient(circle at ${lx}% ${ly}%, rgba(255,140,40,.55), rgba(255,60,90,.15) 35%, transparent 60%)`;
    // letterbox in flashback
    const fb = (t >= SCN.S12[0] && t < SCN.S13[1]) ? eo(cl((t - SCN.S12[0]) / 0.4)) * cl((SCN.S13[1] - t) / 0.3) : 0;
    $('barT').style.height = $('barB').style.height = (fb * 150) + 'px';
    // kinetic slams
    const sl = $('slam'); let shown = false;
    SLAMS.forEach(([txt, a, d, col, size]) => {
      if (t >= a && t < a + d) {
        shown = true; const p = (t - a) / d;
        if (sl.dataset.k !== txt) { sl.innerHTML = txt; sl.dataset.k = txt; }
        sl.style.color = col; sl.style.fontSize = size + 'px';
        sl.style.opacity = cl(p / 0.08) * cl((1 - p) / 0.2);
        sl.style.transform = `translateY(-50%) scale(${lerp(1.9, 1, eo(cl(p / 0.15))) * (1 + 0.05 * p)}) translateX(${(rnd(frame) - .5) * 8 * (1 - p)}px)`;
      }
    });
    if (!shown) sl.style.opacity = 0;
    // timecode / REC (documentary feel) during night scenes
    const night = t >= SCN.S14[0] && t < SCN.S16[0];
    $('tc').style.opacity = night ? 1 : 0;
    const clock = 2 * 3600 + 14 * 60 + Math.floor(t - SCN.S14[0]);
    $('tct').textContent = `REC  0${Math.floor(clock / 3600)}:${String(Math.floor(clock / 60) % 60).padStart(2, '0')}:${String(clock % 60).padStart(2, '0')}`;
    $('rec').style.opacity = Math.floor(t * 2) % 2 ? 1 : 0.2;
    grain(frame);
  };
  window.DIRECTOR = { SLAMS: SLAMS.map(s => [s[1], s[2]]), INS: INS.map(i => [i[2], i[3]]) };
  render(0);
})();
