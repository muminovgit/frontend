import csv, json, os, re
from . import phones, sectors

# Eskiz requires pre-approved templates; keep text short, with explicit opt-out.
TEMPLATE = ("{company}: xodimlar keldi-ketdisi, HR va loyihalarni bitta tizimda yuriting. "
            "KPI.com bepul demo: {link}  To'xtatish: STOP")

def load_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def enrich(rows):
    seen, out = set(), []
    for r in rows:
        key = (r.get("stir") or r.get("name", "")).strip().lower()
        if not key or key in seen: continue
        seen.add(key)
        emp = int(r["employees"]) if str(r.get("employees", "")).isdigit() else None
        lead = {**r, "employees": emp, "phone": phones.normalize(r.get("phone"))}
        lead["sector"] = sectors.classify(f'{r.get("name","")} {r.get("activity","")}')
        lead["score"] = sectors.score(lead)
        lead["pitch"] = sectors.pitch(lead["sector"])
        out.append(lead)
    return sorted(out, key=lambda l: (-l["score"], l["sector"]))

def by_sector(leads):
    g = {}
    for l in leads: g.setdefault(l["sector"], []).append(l)
    return dict(sorted(g.items(), key=lambda kv: -len(kv[1])))

def to_kpi_csv(leads, path):
    cols = ["name", "stir", "sector", "score", "phone", "employees", "region", "pitch", "source"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, cols, extrasaction="ignore"); w.writeheader(); w.writerows(leads)

def load_optouts(path="data/optout.txt"):
    return set(open(path).read().split()) if os.path.exists(path) else set()

def sms_queue(leads, min_score=50, link="kpi.com/uz", optouts=frozenset()):
    """Only B2B company mobiles, scored, not opted out, deduped by phone."""
    seen, q = set(), []
    for l in leads:
        p = l["phone"]
        if not p or not phones.is_mobile(p) or p in optouts or p in seen or l["score"] < min_score: continue
        seen.add(p)
        q.append((p, TEMPLATE.format(company=re.sub(r"\s+", " ", l["name"])[:30], link=link)))
    return q
