# Build every Davo Google Ads asset: 4 versions (palette x product-list treatment).
#   out/V1-mint-blur ... out/V4-beige-clean
#     1-format/1x|2x/t<N>-<WxH>.png|jpg   (uploaded display, <=150 KB each)
#     2-format/<screen>-<WxH>.png|jpg      (responsive display, 2x pixels, no text)
#   out/logos/logo-1200x1200.png, logo-1200x300.png
import os, sys, subprocess, shutil
from PIL import Image
ROOT = os.path.dirname(os.path.abspath(__file__)); RAW = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '_raw'); OUT = os.path.join(ROOT, 'out')
F1 = [(300, 250), (336, 280), (728, 90), (300, 600), (160, 600), (320, 50), (320, 100)]
F2 = [(1200, 628), (1200, 1200), (900, 1600)]
VERS = [('V1-mint-blur', 'mint', 'blur'), ('V2-mint-clean', 'mint', 'clean'), ('V3-beige-blur', 'beige', 'blur'), ('V4-beige-clean', 'beige', 'clean')]
os.makedirs(RAW, exist_ok=True); shutil.rmtree(OUT, ignore_errors=True)
jobs, plan = [], []
for v, c, m in VERS:
    for t in range(1, 6):
        for w, h in F1:
            for s in (1, 2):
                n = f'{v}_f1_t{t}_{w}x{h}_{s}x'; jobs.append(f'n={n}&f=1&t={t}&w={w}&h={h}&s={s}&c={c}&m={m}')
                plan.append((n, f'{v}/1-format/{s}x/t{t}-{w}x{h}', 150_000, None))
    for sc in ('home', 'home2', 'remind'):
        for w, h in F2:
            n = f'{v}_f2_{sc}_{w}x{h}'; jobs.append(f'n={n}&f=2&sc={sc}&w={w}&h={h}&s=2&c={c}&m={m}')
            plan.append((n, f'{v}/2-format/{sc}-{w*2}x{h*2}', 5_000_000, None))
for w, h in ((1200, 1200), (1200, 300)):
    n = f'logo_{w}x{h}'; jobs.append(f'n={n}&f=3&w={w}&h={h}&s=1'); plan.append((n, f'logos/logo-{w}x{h}', 5_000_000, 'rgba'))
for i in range(0, len(jobs), 60):
    r = subprocess.run(['node', os.path.join(ROOT, 'render.js'), RAW] + jobs[i:i + 60], capture_output=True, text=True)
    if r.returncode or 'PAGEERR' in r.stderr: sys.exit('render failed:\n' + r.stderr)
for n, dst, cap, mode in plan:
    im = Image.open(os.path.join(RAW, n + '.png')); im = im.convert('RGBA' if mode else 'RGB')
    o = os.path.join(OUT, dst + '.png'); os.makedirs(os.path.dirname(o), exist_ok=True); im.save(o, optimize=True)
    if os.path.getsize(o) > cap and not mode:
        os.remove(o); o = o[:-4] + '.jpg'
        for q in range(94, 50, -2):
            im.save(o, quality=q, optimize=True, subsampling=0 if q > 85 else 2)
            if os.path.getsize(o) <= cap: break
    if os.path.getsize(o) > cap: print('OVER LIMIT', o, os.path.getsize(o))
print('done', len(plan))
