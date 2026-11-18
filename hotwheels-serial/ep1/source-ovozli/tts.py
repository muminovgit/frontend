"""Synthesize narration lines with edge-tts (Uzbek voice) and build the episode timeline."""
import asyncio, ssl, json, subprocess, wave, os, sys
import edge_tts, edge_tts.communicate as C

C._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
OUT = os.path.dirname(os.path.abspath(__file__))
VOICE = "uz-UZ-SardorNeural"
STYLE = {  # rate, pitch
    "N": ("-4%", "-6Hz"),
    "OLD": ("-8%", "-20Hz"),
    "STR": ("+0%", "-14Hz"),
}
# scene id, pre-gap, [(line id, voice, text, subtitle, highlight word idx, quote)], post-gap, min duration
SCENES = [
 ("S1", 0.4, [("n1","N","Sen hozir qo'lingda bir yuz ellik ming dollar ushlab turibsan.","Sen hozir qo'lingda 150 000 dollar ushlab turibsan.",[3,4],0),
              ("n2","N","Va buni... hali hech kim bilmaydi.","Va buni hali hech kim bilmaydi…",[],0)], 0.5, 0),
 ("S2", 0.0, [], 0.0, 1.6),
 ("S3", 0.3, [("n3","N","Kecha. Yakshanba. Yangiobod bozori.","Kecha. Yakshanba. Yangiobod bozori.",[3,4],0),
              ("n4","N","Sen bu yerga eski radio izlab kelgan eding.","Sen bu yerga eski radio izlab kelgan eding.",[],0)], 0.3, 0),
 ("S4", 0.2, [("n5","N","Lekin bir cholning oldidagi bitta quti ko'zingga tushdi.","Lekin bir cholning oldidagi bitta quti ko'zingga tushdi.",[5],0)], 0.4, 0),
 ("S5", 0.3, [("o1","OLD","Hammasi ellik ming. Nevaramniki edi... Endi kerakmas.","— Hammasi 50 ming. Nevaramniki edi. Endi kerakmas.",[2,3],1)], 0.6, 0),
 ("S6", 0.2, [("n6","N","Uyda qutini stolga ag'darding.","Uyda qutini stolga ag'darding.",[],0),
              ("n7","N","Eski mashinalar. Bo'yog'i ko'chgan.","Eski mashinalar. Bo'yog'i ko'chgan.",[],0)], 0.3, 0),
 ("S7", 0.2, [("n8","N","Faqat bittasi... boshqacha edi.","Faqat bittasi boshqacha edi.",[3],0),
              ("n9","N","Pushti. Orqasida ikkita surf taxtasi.","Pushti. Orqasida ikkita surf taxtasi.",[0],0)], 0.5, 0),
 ("S8", 0.2, [("n10","N","Qiziqib, internetdan qidirding.","Qiziqib, internetdan qidirding…",[],0)], 1.6, 0),
 ("S9", 0.5, [("n11","N","Bir ming to'qqiz yuz oltmish to'qqizinchi yil. Hot Wheels kompaniyasining Beach Bomb prototipi.",None,[],0),
              ("n12","N","Surf taxtalari orqadan kiradi. U hech qachon sotuvga chiqmagan.",None,[],0),
              ("n13","N","Pushti rangdagisi esa, dunyodagi eng qimmat Hot Wheels.",None,[],0),
              ("n14","N","Qo'llaring titray boshladi.","Qo'llaring titray boshladi.",[],0)], 0.4, 0),
 ("S10", 0.5, [("n15","N","Agar bu haqiqiy bo'lsa...","Agar bu haqiqiy bo'lsa…",[],0),
               ("n16","N","sen ellik ming so'mga, deyarli ikki milliard topding.","Sen 50 ming so'mga deyarli 2 milliard topding.",[5,6],0)], 0.6, 0),
 ("S11", 0.5, [("n17","N","Lekin... bitta muammo bor.",None,[],0)], 0.7, 0),
 ("S12", 0.3, [("n18","N","Pul to'layotganingda, orqangda bir yigit turgan edi.","Pul to'layotganingda orqangda bir yigit turgan edi.",[],0)], 0.3, 0),
 ("S13", 0.2, [("n19","N","U qutini... suratga oldi.","U qutini suratga oldi.",[1,2],0)], 0.8, 0),
 ("S14", 0.3, [("n20","N","Soat tungi ikki. Telefoningga xabar keldi.","Soat tungi ikki. Telefoningga xabar keldi.",[],0),
               ("s1","STR","Assalomu alaykum. Kecha bozordan quti olgansiz.",None,[],0),
               ("s2","STR","Ichidagi pushti mashinani sotasizmi?",None,[],0),
               ("s3","STR","Narxini... o'zingiz ayting.",None,[],0)], 0.8, 0),
 ("S15", 0.3, [("n21","N","U raqamingni qayerdan oldi?","U raqamingni qayerdan oldi?…",[],0)], 0.9, 0),
 ("S16", 0.5, [("n22","N","Nima qilasan?",None,[],0),
               ("n23","N","Javob berasanmi?",None,[],0),
               ("n24","N","Bloklaysanmi?",None,[],0),
               ("n25","N","Yoki cholni topib, qutining sirini so'raysanmi?",None,[],0),
               ("n26","N","Izohga A, B yoki C deb yoz. Eng ko'p ovoz olgan tanlov bilan, ikkinchi qism davom etadi.",None,[],0)], 1.0, 0),
 ("S17", 0.3, [("n27","N","Ikkinchi qism... ertaga.",None,[],0)], 1.2, 0),
]
GAP = {"n2": 0.6, "s1": 1.6, "s2": 1.4, "s3": 1.6, "n23": 0.2, "n24": 0.2, "n25": 0.2, "n26": 0.5, "n12": 0.3, "n13": 0.3, "n14": 0.6, "n16": 0.2}

NARRATOR = os.environ.get("NARRATOR", "edge")
TIGHT = float(os.environ.get("TIGHT", "1.0"))   # "silero" -> narrator lines from silero_<id>.wav

def phonetic(text):
    return text.replace("Hot Wheels", "Xot Vils").replace("Beach Bomb", "Bich Bomb")

async def synth(lid, voice, text):
    mp3 = f"{OUT}/v_{lid}.mp3"; wav = f"{OUT}/v_{lid}.wav"
    if voice == "N" and NARRATOR == "silero":
        mp3 = f"{OUT}/silero/sil_{lid}.wav"
    elif not os.path.exists(mp3):
        rate, pitch = STYLE[voice]
        await edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch).save(mp3)
    # trim leading/trailing silence, 44.1k mono
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-af",
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" + (",atempo=1.07" if (voice == "N" and NARRATOR == "silero") else ""),
        "-ar", "44100", "-ac", "1", wav], check=True)
    with wave.open(wav) as w:
        return w.getnframes() / w.getframerate()

async def main():
    t = 0.0; scenes = {}; lines = []
    for sid, pre, ls, post, mind in SCENES:
        s0 = t; t += pre * TIGHT
        for i, (lid, voice, text, sub, hl, q) in enumerate(ls):
            if i > 0: t += GAP.get(lid, 0.35) * TIGHT
            d = await synth(lid, voice, text)
            lines.append(dict(id=lid, voice=voice, start=round(t, 3), end=round(t + d, 3), sub=sub, hl=hl, quote=q, scene=sid))
            t += d
        t += post * TIGHT
        t = max(t, s0 + mind)
        scenes[sid] = [round(s0, 3), round(t, 3)]
    tl = dict(total=round(t, 3), scenes=scenes, lines=lines)
    json.dump(tl, open(f"{OUT}/timeline.json", "w"), indent=1, ensure_ascii=False)
    print("total", round(t, 2))
    for sid, (a, b) in scenes.items(): print(sid, a, b)

asyncio.run(main())
