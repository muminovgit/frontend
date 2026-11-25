# "Qachongacha?" reel — edit decision list over the two usable takes (IMG_3259, IMG_3260; IMG_3261 intro dropped).
# Builds: frames/v/%05d.jpg (1350x2400 so the comp can punch in), voice_raw.wav (cut + 12 ms fades), timeline.js
# (segments + corrected, re-timed word list for captions).   usage: python3 edl.py <dir with the .MOV files> <frames dir>
import json, os, subprocess, sys
SRC, FR = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
# (take, in, out, corrected words aligned 1:1 with whisper words inside [in,out] — '' drops a word)
EDL = [
 ('IMG_3260', 21.70, 25.15, 'hook', "Dorixonama-dorixona sarson bo'laverasizmi? Qachongacha?"),
 ('IMG_3259', 3.52, 6.40, 'brand', "Davo Delivery nomli yangi ilova chiqqan."),
 ('IMG_3259', 6.38, 9.40, 'hands', "Ko'rib turganingizdek, qo'limda ikkita dori: sink hamda biotin."),
 ('IMG_3259', 9.42, 20.05, 'app', "Ushbu dorilarni va sizga kerakli bo'lgan barcha dori vositalarini mana shu havola orqali o'tib, dostavka qildiradigan bo'lsangiz, uyingizgacha sifatli olib kelib berishadi."),
 ('IMG_3259', 21.00, 25.05, 'nohassle', "Dorixonama-dorixona kezib, sarson bo'lib yurishning hojati yo'q."),
 ('IMG_3259', 25.62, 29.62, 'count', "Toshkent bo'yicha 200 dan ortiq dorixona bilan ishlaydi."),
 ('IMG_3260', 3.98, 7.50, 'plus1', "Uyingizgacha yetkazib berish — bu birinchi plus bo'lsa, ikkinchi plus:"),
 ('IMG_3260', 13.66, 20.55, 'plus2', "bu ilova orqali dorini qaysi mahal va necha mahal ichish kerakligini ushbu ilova sizga xabar berib turadi."),
 ('IMG_3260', 20.60, 21.62, 'cta', "Davo Delivery."),
]
TAIL = 1.6      # end card hold after the last word (voice silent)
os.makedirs(os.path.join(FR, 'v'), exist_ok=True)
tr = {t: json.load(open(os.path.join(HERE, f'{t}_tr.json'))) for t in ('IMG_3259', 'IMG_3260')}
segs, words, t_out, nframe, wavs = [], [], 0.0, 0, []
for i, (take, a, b, kind, text) in enumerate(EDL):
    d = b - a; n = round(d * FPS)
    # frames
    tmp = os.path.join(FR, f'seg{i}'); os.makedirs(tmp, exist_ok=True)
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-ss', f'{a:.3f}', '-i', os.path.join(SRC, take + '.MOV'), '-t', f'{n / FPS:.4f}',
                    '-vf', f'fps={FPS},scale=1350:2400:flags=lanczos,eq=contrast=1.06:saturation=1.12:gamma=1.04', '-q:v', '4', os.path.join(tmp, '%05d.jpg')], check=True)
    got = sorted(os.listdir(tmp))[:n]
    for k, f in enumerate(got): os.replace(os.path.join(tmp, f), os.path.join(FR, 'v', f'{nframe + k + 1:05d}.jpg'))
    n = len(got)
    # audio
    wv = os.path.join(FR, f'a{i}.wav'); wavs.append(wv)
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-ss', f'{a:.3f}', '-i', os.path.join(SRC, take + '.MOV'), '-map', '0:a:0', '-t', f'{n / FPS:.4f}',
                    '-af', f'afade=t=in:d=0.012,afade=t=out:st={n / FPS - 0.012:.4f}:d=0.012', '-ar', '48000', '-ac', '1', wv], check=True)
    # captions: whisper word timings inside the cut, corrected spelling spread proportionally over them
    ws = [w for s in tr[take] for w in s['w'] if w[0] >= a - .05 and w[1] <= b + .05]
    s0, s1 = (ws[0][0], ws[-1][1]) if ws else (a, b)
    toks = text.split(); L = [len(x) + 2 for x in toks]; tot = sum(L); t = s0
    for tok, l in zip(toks, L):
        dd = (s1 - s0) * l / tot; words.append({'w': tok, 's': round(t - a + t_out, 3), 'e': round(t - a + dd + t_out, 3), 'seg': i}); t += dd
    segs.append({'i': i, 'kind': kind, 'take': take, 't0': round(t_out, 4), 't1': round(t_out + n / FPS, 4), 'f0': nframe + 1, 'n': n})
    t_out += n / FPS; nframe += n
DUR = t_out + TAIL
with open(os.path.join(FR, 'alist.txt'), 'w') as f:
    for w in wavs: f.write(f"file '{w}'\n")
subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(FR, 'alist.txt'), '-af', f'apad=pad_dur={TAIL}', '-ar', '48000', os.path.join(HERE, 'voice_raw.wav')], check=True)
open(os.path.join(HERE, 'timeline.js'), 'w').write('window.TL=' + json.dumps({'segs': segs, 'words': words, 'dur': round(DUR, 3), 'nframes': nframe}, ensure_ascii=False) + ';')
for s in segs: print(s)
print('total', round(DUR, 2), 's', nframe, 'frames')
