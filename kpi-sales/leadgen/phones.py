import re
# Uzbek mobile prefixes only (6x/7x codes are landlines, e.g. 71 = Tashkent)
MOBILE = {"20","33","50","55","77","88","90","91","93","94","95","97","98","99"}

def normalize(raw):
    """-> '998901234567' or None. Landlines are kept out of SMS via is_mobile()."""
    d = re.sub(r"\D", "", raw or "")
    if len(d) == 9: d = "998" + d
    if len(d) == 12 and d.startswith("998"): return d
    return None

def is_mobile(p): return bool(p) and p[3:5] in MOBILE
