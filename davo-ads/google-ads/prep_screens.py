# Prepare phone screens for Google Ads banners. Two treatments of product lists (drug names/prices):
#   blur  = rows Gaussian-blurred;  clean = rows redrawn as empty "loading skeleton" cards.
# Partner logos are blurred in both (not confirmed as partners yet).
import os
from PIL import Image, ImageDraw, ImageFilter
ROOT = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(ROOT, '..', 'figma', 'screens'); O = os.path.join(ROOT, 'screens')
def rows(top, n, step=196, h=157): return [(top + i * step, top + i * step + h) for i in range(n)]
def blur(im, box, r): im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(r)), box[:2])
def skeleton(im, y0, y1):
    d = ImageDraw.Draw(im); d.rounded_rectangle((32, y0, 754, y1), 26, fill=(245, 245, 247))
    d.rounded_rectangle((52, y0 + 14, 194, y1 - 14), 20, fill=(233, 234, 238))
    for dy, w in ((34, 400), (70, 300), (112, 170)): d.rounded_rectangle((222, y0 + dy, 222 + w, y0 + dy + 20), 10, fill=(229, 230, 235))
    d.rounded_rectangle((650, y1 - 52, 724, y1 - 18), 17, fill=(255, 255, 255))
JOBS = {'home': ('Home.png', rows(1168, 3), None), 'home2': ("Home v2 - pill widget - Eslatma hali yo'q.png", rows(1626, 1), None),
        'remind': ('Dori eslatmalari - Start page.png', [], None)}
for key, (f, rs, partners) in JOBS.items():
    for mode in ('blur', 'clean'):
        im = Image.open(os.path.join(S, f)).convert('RGB')
        if partners: blur(im, partners, 26)
        for y0, y1 in rs:
            y1 = min(y1, im.height)
            if mode == 'blur': blur(im, (32, y0, 754, y1), 9)
            else: skeleton(im, y0, y1)
        im.save(os.path.join(O, f'{key}-{mode}.png'), optimize=True)
print('ok')
