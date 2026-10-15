"""python cli.py leads.csv [--send]   -> sorted report, kpi_import.csv, SMS queue (dry-run unless --send)."""
import sys
from leadgen import pipeline, eskiz

def main(argv):
    path, live = argv[1], "--send" in argv
    leads = pipeline.enrich(pipeline.load_csv(path))
    groups = pipeline.by_sector(leads)
    print(f"{len(leads)} unique leads")
    for s, ls in groups.items():
        print(f"  {s:14} {len(ls):5}  avg score {sum(l['score'] for l in ls)//len(ls)}  | {ls[0]['pitch']}")
    pipeline.to_kpi_csv(leads, "data/kpi_import.csv")
    q = pipeline.sms_queue(leads, optouts=pipeline.load_optouts())
    print(f"SMS queue: {len(q)} (wrote data/kpi_import.csv)")
    client = eskiz.Eskiz(dry_run=not live)
    for r in client.send_many(q[:5 if not live else None]): print(r)

if __name__ == "__main__": main(sys.argv)
