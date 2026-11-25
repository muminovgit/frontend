# Uzbek subtitles for IMG_3293: whisper large-v3 timings + hand-corrected text (whisper's Uzbek was rough).
# Each segment's corrected words are spread over that segment's real speech span (whisper word times).
# Lines marked (?) were hard to hear in the source — check them before publishing.
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, 'whisper_raw.json')))
FIX = [  # one corrected line per whisper segment, same order
 "Assalomu alaykum, do'stlar! Hozir sizlarga kerakli va foydali bir reklama haqida aytib bermoqchi edim.",
 "Qiziq bo'lsa, oxirigacha ko'ring.",
 "Xullas, sizlarga aytmoqchi bo'lgan foydali va kerakli reklama —",
 "ya'ni Davo Delivery nomli yangi ilova chiqqan.",
 "Ko'rib turganingizdek, qo'limda ikkita dori: sink hamda biotin.",
 "Ushbu dorilarni va sizga kerakli bo'lgan barcha dori vositalarini",
 "mana shu ilova orqali",
 "qidirib topasiz-da, buyurtma berasiz, (?)",
 "ular esa uyingizgacha sifatli olib kelib berishadi.",
 "Bu orqali dorilaringizni qachon va qaysi vaqtda qabul qilish kerakligini ilova sizga eslatib turishi mumkin.",
 "Xullas, Davo Delivery — kerakli dorilarni topish, buyurtma qilish va uyingizgacha yetkazib berish uchun juda qulay ilova.",
 "Endi dorixona izlab vaqtingizni sarflamang.",
 "Hozir ta'kidlaganimdek, uyingizgacha yetkazib berish — bu birinchi plus bo'lsa, ikkinchi plus:",
 "ushbu ilova orqali dori buyurtma qilsangiz, uyingizgacha olib kelib berishdan tashqari,",
 "bu ilova dorini qaysi mahal",
 "va necha mahal ichish kerakligini",
 "sizga xabar berib turadi.",
 "Davo Delivery.",
 "Dorixonama-dorixona sarson bo'laverasizmi?",
 "Qachongacha?",
]
assert len(FIX) == len(raw), (len(FIX), len(raw))
caps = []
for seg, line in zip(raw, FIX):
    ws = seg['w'] or [[seg['s'], seg['e'], '']]
    s0, s1 = ws[0][0], ws[-1][1]
    words = line.replace('(?)', '').split()
    L = [len(re.sub(r'\W', '', w)) + 2 for w in words]; tot = sum(L); t = s0; out = []
    for w, l in zip(words, L):
        d = (s1 - s0) * l / tot; out.append({'w': w, 's': round(t, 3), 'e': round(t + d, 3)}); t += d
    # group into captions of <= 3 words / 18 chars, break after punctuation
    grp = []
    for w in out:
        grp.append(w)
        txt = ' '.join(x['w'] for x in grp)
        if len(grp) >= 3 or len(txt) >= 18 or re.search(r'[.,!?:—]$', w['w']):
            caps.append({'s': grp[0]['s'], 'e': grp[-1]['e'], 'words': grp}); grp = []
    if grp: caps.append({'s': grp[0]['s'], 'e': grp[-1]['e'], 'words': grp})
for a, b in zip(caps, caps[1:]): a['e'] = max(a['e'], min(b['s'], a['e'] + .35))   # brief hold, never overlapping
json.dump(caps, open(os.path.join(HERE, 'captions.json'), 'w'), ensure_ascii=False)
# also an .srt for the client to proofread
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f"{h:02}:{m:02}:{int(s):02},{int((s % 1) * 1000):03}"
with open(os.path.join(HERE, 'subtitles_uz.srt'), 'w') as f:
    for i, (seg, line) in enumerate(zip(raw, FIX), 1): f.write(f"{i}\n{ts(seg['s'])} --> {ts(seg['e'])}\n{line}\n\n")
print(len(caps), 'captions')
open(os.path.join(HERE, 'captions.js'), 'w').write('window.CAPS=' + json.dumps(caps, ensure_ascii=False) + ';')
