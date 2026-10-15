"""Sector classification + HR-pain scoring for KPI.com (HR attendance, HR automation, projects)."""
import re

# sector -> (keywords uz/ru/en, base fit 0-40, pitch)
SECTORS = {
    "retail":        (r"savdo|do'kon|dokon|магазин|торгов|retail|supermarket|market", 35, "smenali xodimlar: keldi-ketdi + jadval"),
    "manufacturing": (r"ishlab chiqar|zavod|fabrika|завод|производ|manufactur|tikuv|to'qimachilik|textile", 40, "ko'p ishchi, smena, jarima/kechikish hisobi"),
    "construction":  (r"qurilish|строит|construction|подряд", 35, "obyektlar bo'yicha davomat + loyihalar"),
    "logistics":     (r"logist|transport|yuk|логист|перевоз|cargo|taksi|taxi", 30, "haydovchilar, marshrut/loyiha vaqti"),
    "security":      (r"qo'riqlash|xavfsizlik|охран|security", 38, "postlar, smena grafigi, kelib-ketish nazorati"),
    "call_center":   (r"call.?center|kontakt.?markaz|колл|аутсорс|outsourc", 38, "operatorlar jadvali va KPI"),
    "it_agency":     (r"dastur|it |software|soft|digital|marketing|agent|IT-|разработ|реклам", 30, "loyihalar + timesheet + KPI"),
    "education":     (r"o'quv|ta'lim|maktab|school|образован|учебн|academy|akademiya", 25, "o'qituvchilar davomati/ish haqi"),
    "healthcare":    (r"klinika|shifoxona|tibbiy|медиц|клиник|apteka|аптек|pharm", 28, "smenali shifokor/hamshira jadvali"),
    "hospitality":   (r"restoran|mehmonxona|hotel|кафе|ресторан|cafe|oshxona", 30, "smenali xodimlar, tez aylanish"),
    "finance":       (r"bank|moliya|sug'urta|финанс|страхов|mikromoliya|insurance", 22, "filial xodimlari, hisobot"),
    "agri":          (r"qishloq|agro|фермер|сельск|paxta|cotton|klaster", 28, "mavsumiy ishchilar hisobi"),
    "other":         (r"", 10, "umumiy HR avtomatlashtirish"),
}

def classify(text: str) -> str:
    t = (text or "").lower()
    for name, (rx, _, _) in SECTORS.items():
        if rx and re.search(rx, t):
            return name
    return "other"

def employee_points(n):
    if n is None: return 10
    return 0 if n < 10 else 10 if n < 20 else 25 if n < 50 else 35 if n < 250 else 30  # 50-250 sweet spot; >250 -> enterprise deal

def score(lead: dict) -> int:
    sector = lead.get("sector") or classify(f'{lead.get("name","")} {lead.get("activity","")}')
    s = SECTORS[sector][1] + employee_points(lead.get("employees"))
    if lead.get("phone"): s += 15
    if lead.get("decision_maker"): s += 10
    return min(s, 100)

def pitch(sector): return SECTORS[sector][2]
