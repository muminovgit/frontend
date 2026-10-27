"""Polite parser for public yellowpages.uz company pages (reads the JSON-LD the site publishes for search engines).
Respects robots.txt, 1 request / 2s, identifies itself. Do not remove the delay."""
import csv, json, re, time, urllib.request, urllib.robotparser
from . import phones

UA = "Mozilla/5.0 (compatible; KPI-leadbot/0.1)"
ROOT = "https://www.yellowpages.uz"

_rp = urllib.robotparser.RobotFileParser(ROOT + "/robots.txt")

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def allowed(url):
    if not _rp.last_checked: _rp.parse(_get(ROOT + "/robots.txt").splitlines())
    return _rp.can_fetch("*", url)

def parse(html, url=""):
    out = {"url": url, "name": "", "phone": None, "email": "", "address": "", "website": "", "activity": ""}
    for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        try: data = json.loads(m.group(1))
        except ValueError: continue
        for node in (data.get("@graph", [data]) if isinstance(data, dict) else []):
            if "telephone" in node or node.get("@type") in ("LocalBusiness", "Organization"):
                out["name"] = out["name"] or node.get("name", "")
                out["phone"] = out["phone"] or phones.normalize(node.get("telephone"))
                out["email"] = out["email"] or node.get("email", "")
                out["website"] = out["website"] or node.get("url", "") if "yellowpages" not in node.get("url", "yellowpages") else out["website"]
                a = node.get("address")
                if isinstance(a, dict): out["address"] = out["address"] or ", ".join(str(v) for k, v in a.items() if isinstance(v, str) and k != "@type" and v)
                elif isinstance(a, str): out["address"] = out["address"] or a
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    out["name"] = out["name"] or (t.group(1).split("|")[0].strip() if t else "")
    return out

def fetch(url): 
    return parse(_get(url), url) if allowed(url) else None

def crawl(urls, delay=2.0, limit=200):
    for u in urls[:limit]:
        try: r = fetch(u)
        except Exception as e: r = {"url": u, "error": str(e)}
        if r: yield r
        time.sleep(delay)

def save(rows, path):
    cols = ["url", "name", "phone", "email", "address", "website", "activity"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
