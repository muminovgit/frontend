"""Beat timeline for "Portlagan svetofor" (1-qism). Durations are placeholders until the narration is recorded:
when the voice arrives, set each beat's `dur` to its line length (+ pause) and re-render; every animation is
written in beat-local time, so nothing else needs to change."""
import json

FPS = 30
BEATS = [
    dict(id="b1",  page="night",     dur=3.6, text="Dunyodagi birinchi svetofor… bir oy ham ishlamay portlab ketgan."),
    dict(id="b2",  page="day",       dur=5.2, text="1868-yil. London. Ko'chalar ot aravalariga to'la, piyoda esa har gal jonini qo'liga olib o'tadi."),
    dict(id="b3",  page="knight",    dur=4.8, text="Parlament oldidagi chorraha uchun temir yo'l muhandisi Jon Nayt yechim topdi."),
    dict(id="b4",  page="semaphore", dur=5.6, text="Poyezdlardagi signalni ko'chaga olib chiqdi: kunduzi qanotchalar, kechasi gaz bilan yonadigan chiroq."),
    dict(id="b5",  page="day",       dur=5.2, text="Qizil — to'xta. Yashil — ehtiyot bo'lib yur. Hammasini qo'lda bitta politsiyachi boshqarardi."),
    dict(id="b6",  page="day",       dur=4.2, text="Aravakashlar to'xtadi, odamlar xavfsiz o'tdi. London hayratda edi."),
    dict(id="b7",  page="night",     dur=4.2, text="Keyin, 1869-yil yanvarida… quvurdan gaz sizib chiqdi."),
    dict(id="b8",  page="night",     dur=2.6, text="Va svetofor politsiyachining yuziga portladi."),
    dict(id="b9",  page="night",     dur=4.0, text="Politsiyachi qattiq kuydi. Svetofor esa o'sha kuni nafaqaga chiqdi."),
    dict(id="b10", page="stove",     dur=7.2, text="Nega? Xuddi oshxonada gazni ochiq qoldirib, keyin gugurt chaqqandek: chiroq qutisida gaz yig'ilgan, bitta uchqun yetarli bo'lgan."),
    dict(id="b11", page="calendar",  dur=4.4, text="London keyingi svetoforni qariyb 60 yil kutdi. Bu safar elektr bilan."),
    dict(id="b12", page="modern",    dur=5.6, text="Shuning uchun qizil chiroqda kutib qolsang, asabiylashma. Hech bo'lmasa… u portlamaydi."),
    dict(id="b13", page="end",       dur=3.0, text="Mashinalar tarixida bunaqa voqealar ko'p. Obuna bo'l!"),
]

def chunks(text, maxc=32):
    """split narration into subtitle cards of up to 2 lines x maxc chars, at word boundaries"""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + 1 + len(w) > maxc and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
        if cur.endswith((".", "!", "?", ":")) and len(cur) > 12:
            lines.append(cur); cur = ""
    if cur: lines.append(cur)
    # no orphans: glue a very short line onto the one before it
    k = 1
    while k < len(lines):
        if len(lines[k]) < 12 and len(lines[k - 1]) + len(lines[k]) <= maxc + 3:
            lines[k - 1] += " " + lines.pop(k)
        else:
            k += 1
    cards, i = [], 0
    while i < len(lines):
        if i + 1 < len(lines) and not lines[i].endswith((".", "!", "?")) and len(lines[i]) + len(lines[i + 1]) <= 2 * maxc:
            cards.append([lines[i], lines[i + 1]]); i += 2
        else:
            cards.append([lines[i]]); i += 1
    return cards

def timeline():
    t, out = 0.0, []
    for b in BEATS:
        cards = chunks(b["text"])
        total = sum(len(" ".join(c)) for c in cards)
        u, subs = 0.12, []
        for c in cards:  # card time proportional to its length, inside the beat (small lead-in)
            d = (b["dur"] - 0.2) * len(" ".join(c)) / total
            subs.append([round(u, 3), round(u + d, 3), c]); u += d
        out.append(dict(b, start=round(t, 3), frames=round(b["dur"] * FPS), subs=subs))
        t += b["dur"]
    return out

if __name__ == "__main__":
    tl = timeline()
    json.dump(tl, open("timeline.json", "w"), ensure_ascii=False, indent=1)
    print("total", round(sum(b["dur"] for b in BEATS), 2), "s,", sum(b["frames"] for b in tl), "frames")
    for b in tl: print(b["id"], b["page"], b["dur"], [s[2] for s in b["subs"]])
