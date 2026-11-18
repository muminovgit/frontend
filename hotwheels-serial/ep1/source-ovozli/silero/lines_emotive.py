"""Narrator lines with per-line delivery (rate, pitch) for Silero SSML. Writes lines.json."""
import json, os
# id, text ("..." = dramatic pause), rate, pitch
L = [
 ("n1", "Sen hozir qo'lingda... bir yuz ellik ming dollar ushlab turibsan.", "medium", "low"),
 ("n2", "Va buni... hali hech kim bilmaydi.", "slow", "x-low"),
 ("n3", "Kecha. Yakshanba. Yangiobod bozori.", "fast", "medium"),
 ("n4", "Sen bu yerga eski radio izlab kelgan eding.", "fast", "medium"),
 ("n5", "Lekin... bir cholning oldidagi bitta quti ko'zingga tushdi!", "medium", "high"),
 ("n6", "Uyda qutini stolga ag'darding.", "fast", "medium"),
 ("n7", "Eski mashinalar. Bo'yog'i ko'chgan.", "fast", "low"),
 ("n8", "Faqat bittasi... boshqacha edi.", "medium", "low"),
 ("n9", "Pushti! Orqasida... ikkita surf taxtasi!", "medium", "high"),
 ("n10", "Qiziqib, internetdan qidirding.", "fast", "medium"),
 ("n11", "Bir ming to'qqiz yuz oltmish to'qqizinchi yil. Xot Vils kompaniyasining Bich Bomb prototipi.", "fast", "medium"),
 ("n12", "Surf taxtalari orqadan kiradi. U hech qachon... sotuvga chiqmagan!", "fast", "medium"),
 ("n13", "Pushti rangdagisi esa... dunyodagi eng qimmat Xot Vils!", "medium", "high"),
 ("n14", "Qo'llaring... titray boshladi.", "slow", "low"),
 ("n15", "Agar bu haqiqiy bo'lsa...", "medium", "low"),
 ("n16", "sen ellik ming so'mga... deyarli ikki milliard topding!", "fast", "high"),
 ("n17", "Lekin... bitta muammo bor.", "slow", "x-low"),
 ("n18", "Pul to'layotganingda, orqangda bir yigit turgan edi.", "fast", "low"),
 ("n19", "U qutini... suratga oldi.", "slow", "x-low"),
 ("n20", "Soat tungi ikki. Telefoningga... xabar keldi.", "medium", "low"),
 ("n21", "U raqamingni... qayerdan oldi?", "slow", "low"),
 ("n22", "Nima qilasan?", "fast", "high"),
 ("n23", "Javob berasanmi?", "fast", "medium"),
 ("n24", "Bloklaysanmi?", "fast", "medium"),
 ("n25", "Yoki cholni topib, qutining sirini so'raysanmi?", "medium", "high"),
 ("n26", "Izohga A, B yoki C deb yoz! Eng ko'p ovoz olgan tanlov bilan, ikkinchi qism davom etadi.", "fast", "medium"),
 ("n27", "Ikkinchi qism... ertaga!", "medium", "high"),
]
json.dump([list(x) for x in L], open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lines.json"), "w"), ensure_ascii=False)
print(len(L))
