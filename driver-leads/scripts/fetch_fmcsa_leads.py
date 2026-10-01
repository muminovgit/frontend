#!/usr/bin/env python3
"""Pull new OTR owner-operator leads from the FMCSA open data (data.transportation.gov).

Usage:
    python scripts/fetch_fmcsa_leads.py --days 1            # yesterday + today
    python scripts/fetch_fmcsa_leads.py --days 30 --out data/leads_30d.csv

Source: FMCSA Company Census File (public US government registry).
Filter: active, 1 power unit (owner-operator), interstate for-hire, 100+ miles,
general freight, US address, phone present. Non-trucking names are excluded.
Stdlib only.
"""
import argparse
import csv
import datetime
import io
import sys
import urllib.parse
import urllib.request

URL = "https://data.transportation.gov/resource/az4n-8mr2.csv"
EXCLUDE_WORDS = ["TOWING", "LIMO", "CONSTRUCTION", "LANDSCAP", "MOVING", "HANDY",
                 "RECOVERY", "AUTO", "TREE", "DELIVERY", "LEASING"]
SELECT = ("company_officer_1 as owner_operator,legal_name as company,phone,"
          "email_address as email,phy_city as city,phy_state as state,phy_zip as zip,"
          "add_date,dot_number,docket1prefix as mc_prefix,docket1 as mc_number,"
          "business_org_desc as org_type")


def build_where(since: str) -> str:
    where = [
        "status_code='A'",
        "power_units='1'",
        "carrier_operation='A'",
        "interstate_beyond_100_miles='1'",
        "classdef like '%AUTHORIZED FOR HIRE%'",
        "crgo_genfreight='X'",
        "phone is not null",
        "company_officer_1 is not null",
        "phy_country='US'",
        f"add_date>='{since}'",
    ]
    where += [f"upper(legal_name) not like '%{w}%'" for w in EXCLUDE_WORDS]
    return " AND ".join(where)


def fetch(since: str, limit: int) -> list[dict]:
    params = urllib.parse.urlencode({
        "$select": SELECT,
        "$where": build_where(since),
        "$order": "add_date DESC",
        "$limit": str(limit),
    })
    with urllib.request.urlopen(f"{URL}?{params}", timeout=120) as resp:
        text = resp.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=1, help="how many days back (default 1)")
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--out", default=None, help="output CSV (default data/leads_<date>.csv)")
    args = ap.parse_args()

    today = datetime.date.today()
    since = (today - datetime.timedelta(days=args.days)).strftime("%Y%m%d")
    rows = fetch(since, args.limit)

    seen, out = set(), []
    for r in rows:
        if r["phone"] in seen:
            continue
        seen.add(r["phone"])
        added = datetime.datetime.strptime(r["add_date"], "%Y%m%d").date()
        r["days_since_registered"] = (today - added).days
        out.append(r)

    path = args.out or f"data/leads_{today.isoformat()}.csv"
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fields = list(out[0].keys()) if out else ["owner_operator", "company", "phone", "email"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} leads -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
