/*
 * WashReveal — wipe the mud off a car photo with the cursor / finger.
 *
 *   const w = WashReveal(el, {
 *     clean: 'clean.jpg',        // required: the washed car
 *     dirty: 'dirty.jpg',        // optional: the muddy car. Omit to generate procedural mud on top of `clean`.
 *     brush: 0.09,               // brush radius as a fraction of the shorter side
 *     position: 'center',        // object-position used for both images
 *     onProgress: p => {},       // 0..1 share of the mud wiped off
 *     onClean: () => {},         // fired once when ~all mud is gone
 *   });
 *   w.ready (Promise), w.reset(), w.sweep(), w.setImages({clean, dirty}), w.destroy()
 *
 * The wiped area is tracked on an untainted mask canvas, so progress works even when the
 * images come from another origin without CORS headers.
 */
(function (global) {
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));

  function loadImage(src) {
    return new Promise(resolve => {
      if (!src) return resolve(null);
      const img = new Image();
      img.decoding = 'async';
      img.onload = () => resolve(img);
      img.onerror = () => resolve(null);
      img.src = src;
    });
  }

  // Seeded PRNG so the generated mud looks the same on every load.
  function rng(seed) {
    return () => {
      seed |= 0; seed = seed + 0x6d2b79f5 | 0;
      let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  // Procedural mud: splatters, sprays and drips, heavier towards the bottom (wheels/sills).
  function paintMud(ctx, W, H, seed = 7) {
    const r = rng(seed);
    const tones = ['97,69,27', '112,84,44', '84,60,30', '128,98,58', '70,52,26'];
    const tone = () => tones[(r() * tones.length) | 0];
    const yBias = () => H * (0.25 + Math.pow(r(), 0.55) * 0.75);
    const s = Math.min(W, H) / 800;
    ctx.save();
    // base film of dust
    const film = ctx.createLinearGradient(0, 0, 0, H);
    film.addColorStop(0, 'rgba(120,95,60,0.10)');
    film.addColorStop(0.55, 'rgba(110,84,48,0.28)');
    film.addColorStop(1, 'rgba(90,66,34,0.55)');
    ctx.fillStyle = film;
    ctx.fillRect(0, 0, W, H);
    // big blobs
    for (let i = 0; i < 140; i++) {
      const x = r() * W, y = yBias(), rad = (20 + r() * 90) * s;
      const g = ctx.createRadialGradient(x, y, 0, x, y, rad);
      const c = tone();
      g.addColorStop(0, `rgba(${c},${0.55 + r() * 0.35})`);
      g.addColorStop(0.7, `rgba(${c},${0.25 + r() * 0.2})`);
      g.addColorStop(1, `rgba(${c},0)`);
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.ellipse(x, y, rad * (1 + r()), rad, r() * Math.PI, 0, Math.PI * 2); ctx.fill();
    }
    // splatter clusters with flung droplets
    for (let i = 0; i < 90; i++) {
      const cx = r() * W, cy = yBias(), c = tone(), n = 6 + (r() * 18) | 0;
      for (let k = 0; k < n; k++) {
        const a = r() * Math.PI * 2, d = Math.pow(r(), 2) * 70 * s, rad = (1 + r() * 7) * s;
        ctx.fillStyle = `rgba(${c},${0.6 + r() * 0.4})`;
        ctx.beginPath(); ctx.arc(cx + Math.cos(a) * d, cy + Math.sin(a) * d, rad, 0, Math.PI * 2); ctx.fill();
      }
    }
    // sprayed streaks (like mud flung from the wheels)
    ctx.lineCap = 'round';
    for (let i = 0; i < 260; i++) {
      const x = r() * W, y = yBias(), len = (10 + r() * 60) * s, ang = -Math.PI / 2 + (r() - 0.5) * 1.2;
      ctx.strokeStyle = `rgba(${tone()},${0.35 + r() * 0.5})`;
      ctx.lineWidth = (1 + r() * 4) * s;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(ang) * len, y + Math.sin(ang) * len); ctx.stroke();
    }
    // drips running down
    for (let i = 0; i < 70; i++) {
      const x = r() * W, y = H * (0.3 + r() * 0.5), len = (20 + r() * 120) * s, w = (2 + r() * 5) * s;
      const c = tone();
      const g = ctx.createLinearGradient(x, y, x, y + len);
      g.addColorStop(0, `rgba(${c},0.75)`); g.addColorStop(1, `rgba(${c},0)`);
      ctx.strokeStyle = g; ctx.lineWidth = w;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + (r() - 0.5) * 6 * s, y + len); ctx.stroke();
    }
    // fine speckle
    for (let i = 0; i < 2500; i++) {
      ctx.fillStyle = `rgba(${tone()},${0.3 + r() * 0.6})`;
      ctx.fillRect(r() * W, yBias(), (0.6 + r() * 2.2) * s, (0.6 + r() * 2.2) * s);
    }
    ctx.restore();
  }

  function WashReveal(el, opts) {
    const o = Object.assign({ brush: 0.09, position: 'center', seed: 7, onProgress() {}, onClean() {} }, opts);
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    el.classList.add('wash-reveal');
    Object.assign(el.style, { touchAction: 'pan-y', userSelect: 'none', WebkitUserSelect: 'none' });

    const cleanImg = document.createElement('img');
    cleanImg.alt = o.alt || '';
    cleanImg.draggable = false;
    Object.assign(cleanImg.style, { position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', objectPosition: o.position, pointerEvents: 'none' });
    const view = document.createElement('canvas');   // what the visitor sees: dirt minus wiped mask
    const fx = document.createElement('canvas');     // water spray particles
    [view, fx].forEach(c => Object.assign(c.style, { position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }));
    el.prepend(cleanImg, view, fx);

    const vctx = view.getContext('2d'), fctx = fx.getContext('2d');
    const dirtLayer = document.createElement('canvas'), dctx = dirtLayer.getContext('2d');  // dirty image / mud, sized to el
    const mask = document.createElement('canvas'), mctx = mask.getContext('2d');           // wiped area (untainted)
    const probe = document.createElement('canvas'); probe.width = 64; probe.height = 36;
    const pctx = probe.getContext('2d', { willReadFrequently: true });

    let W = 0, H = 0, dpr = 1, dirty = null, clean = null;
    let dirtyDirty = true, last = null, progress = 0, cleaned = false, restoring = 0, alive = true;
    const drops = [];

    function coverRect(img) {
      const iw = img.naturalWidth, ih = img.naturalHeight, s = Math.max(W / iw, H / ih);
      const [px, py] = o.position === 'center' ? [0.5, 0.5] : o.position.split(' ').map(v => v === 'left' || v === 'top' ? 0 : v === 'right' || v === 'bottom' ? 1 : 0.5);
      return [(W - iw * s) * px, (H - ih * s) * (py ?? 0.5), iw * s, ih * s];
    }

    function buildDirt() {
      dctx.setTransform(1, 0, 0, 1, 0, 0);
      dctx.clearRect(0, 0, dirtLayer.width, dirtLayer.height);
      dctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (dirty) {
        dctx.drawImage(dirty, ...coverRect(dirty));
      } else if (clean) {
        // no dirty photo: dirty up the clean one
        dctx.save(); dctx.filter = 'saturate(.75) brightness(.92) sepia(.15)';
        dctx.drawImage(clean, ...coverRect(clean)); dctx.restore();
        paintMud(dctx, W, H, o.seed);
      }
      dirtyDirty = true;
    }

    function resize() {
      dpr = Math.min(global.devicePixelRatio || 1, 2);
      const nw = el.clientWidth, nh = el.clientHeight;
      if (!nw || !nh) return;
      // keep the already wiped area when the viewport resizes
      const keep = W && mask.width ? (() => { const c = document.createElement('canvas'); c.width = mask.width; c.height = mask.height; c.getContext('2d').drawImage(mask, 0, 0); return c; })() : null;
      W = nw; H = nh;
      [view, fx, dirtLayer, mask].forEach(c => { c.width = Math.round(W * dpr); c.height = Math.round(H * dpr); });
      if (keep) mctx.drawImage(keep, 0, 0, mask.width, mask.height);
      buildDirt();
    }

    const radius = () => Math.max(28, Math.min(W, H) * o.brush);

    function stamp(x, y, r) {
      mctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const g = mctx.createRadialGradient(x, y, r * 0.2, x, y, r);
      g.addColorStop(0, 'rgba(0,0,0,1)');
      g.addColorStop(0.6, 'rgba(0,0,0,.65)');
      g.addColorStop(1, 'rgba(0,0,0,0)');
      mctx.fillStyle = g;
      mctx.beginPath(); mctx.arc(x, y, r, 0, Math.PI * 2); mctx.fill();
    }

    // Interpolate between pointer samples so fast strokes leave a continuous clean path.
    function wipeTo(x, y, speed = 1) {
      const r = radius();
      if (last) {
        const dx = x - last.x, dy = y - last.y, dist = Math.hypot(dx, dy), step = r * 0.25;
        for (let d = step; d < dist; d += step) stamp(last.x + dx * d / dist, last.y + dy * d / dist, r);
      }
      stamp(x, y, r);
      if (!reduce) spray(x, y, last ? x - last.x : 0, last ? y - last.y : 0, speed);
      last = { x, y };
      dirtyDirty = true;
    }

    function spray(x, y, vx, vy, k) {
      const n = Math.min(6, 2 + Math.hypot(vx, vy) / 12) * k;
      for (let i = 0; i < n; i++) {
        const a = Math.random() * Math.PI * 2, sp = 1 + Math.random() * 4;
        drops.push({
          x: x + Math.cos(a) * radius() * 0.6, y: y + Math.sin(a) * radius() * 0.6,
          vx: Math.cos(a) * sp + vx * 0.08, vy: Math.sin(a) * sp - 1.5 + vy * 0.08,
          r: 1 + Math.random() * 3, life: 1, mud: Math.random() < 0.45,
        });
      }
      if (drops.length > 400) drops.splice(0, drops.length - 400);
    }

    function measure() {
      pctx.clearRect(0, 0, 64, 36);
      pctx.drawImage(mask, 0, 0, 64, 36);
      const d = pctx.getImageData(0, 0, 64, 36).data;
      let sum = 0;
      for (let i = 3; i < d.length; i += 4) sum += d[i];
      progress = sum / (255 * 64 * 36);
      o.onProgress(progress);
      if (!cleaned && progress > 0.82) { cleaned = true; o.onClean(); }
    }

    function render() {
      if (!alive) return;
      if (restoring) {
        // mud flows back gradually after a full clean
        mctx.setTransform(1, 0, 0, 1, 0, 0);
        mctx.globalCompositeOperation = 'destination-out';
        mctx.fillStyle = 'rgba(0,0,0,0.06)';
        mctx.fillRect(0, 0, mask.width, mask.height);
        mctx.globalCompositeOperation = 'source-over';
        if (--restoring === 0) { mctx.clearRect(0, 0, mask.width, mask.height); cleaned = false; measure(); }
        dirtyDirty = true;
      }
      if (dirtyDirty) {
        vctx.setTransform(1, 0, 0, 1, 0, 0);
        vctx.globalCompositeOperation = 'source-over';
        vctx.clearRect(0, 0, view.width, view.height);
        vctx.drawImage(dirtLayer, 0, 0);
        vctx.globalCompositeOperation = 'destination-out';
        vctx.drawImage(mask, 0, 0);
        vctx.globalCompositeOperation = 'source-over';
        dirtyDirty = false;
      }
      fctx.setTransform(1, 0, 0, 1, 0, 0);
      fctx.clearRect(0, 0, fx.width, fx.height);
      if (drops.length) {
        fctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        for (let i = drops.length - 1; i >= 0; i--) {
          const p = drops[i];
          p.vy += 0.25; p.x += p.vx; p.y += p.vy; p.life -= 0.022;
          if (p.life <= 0) { drops.splice(i, 1); continue; }
          fctx.globalAlpha = p.life;
          fctx.fillStyle = p.mud ? 'rgba(97,69,27,.9)' : 'rgba(255,255,255,.95)';
          fctx.beginPath(); fctx.ellipse(p.x, p.y, p.r, p.r * 1.4, Math.atan2(p.vy, p.vx), 0, Math.PI * 2); fctx.fill();
          if (!p.mud) { fctx.strokeStyle = 'rgba(160,210,255,.8)'; fctx.lineWidth = 0.6; fctx.stroke(); }
        }
        fctx.globalAlpha = 1;
      }
      requestAnimationFrame(render);
    }

    const local = e => { const r = el.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
    let lastT = 0, measureT = 0;
    el.addEventListener('pointermove', e => {
      const now = performance.now();
      if (now - lastT > 120) last = null; // new stroke after a pause
      lastT = now;
      const evs = e.getCoalescedEvents ? e.getCoalescedEvents() : [e];
      (evs.length ? evs : [e]).forEach(ev => wipeTo(...local(ev)));
      if (now - measureT > 250) { measureT = now; measure(); }
    });
    el.addEventListener('pointerleave', () => { last = null; measure(); });
    el.addEventListener('pointerdown', e => { last = null; wipeTo(...local(e), 2); });

    let ro;
    if ('ResizeObserver' in global) { ro = new ResizeObserver(() => resize()); ro.observe(el); }
    else global.addEventListener('resize', resize);

    const api = {
      get progress() { return progress; },
      ready: null,
      async setImages({ clean: c, dirty: d }) {
        [clean, dirty] = await Promise.all([loadImage(c), loadImage(d)]);
        if (clean) cleanImg.src = clean.src;
        mctx.clearRect(0, 0, mask.width, mask.height);
        cleaned = false; progress = 0;
        resize();
        return !!clean;
      },
      reset() { restoring = 45; },
      destroy() { alive = false; if (ro) ro.disconnect(); else global.removeEventListener('resize', resize); },
      // automatic demo stroke across the car
      sweep(duration = 2200) {
        if (reduce) return;
        const t0 = performance.now();
        last = null;
        const run = t => {
          const p = clamp((t - t0) / duration);
          wipeTo(W * (0.12 + p * 0.76), H * (0.58 + Math.sin(p * Math.PI * 3) * 0.12), 0.6);
          if (p < 1) requestAnimationFrame(run); else { last = null; measure(); }
        };
        requestAnimationFrame(run);
      },
    };
    api.ready = api.setImages({ clean: o.clean, dirty: o.dirty });
    requestAnimationFrame(render);
    return api;
  }

  global.WashReveal = WashReveal;
})(window);
