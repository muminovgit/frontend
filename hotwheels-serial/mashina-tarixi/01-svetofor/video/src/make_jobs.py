"""Writes jobs_full.json (every frame of every beat) for capture.mjs."""
import json
from beats import timeline
jobs = [dict(page=b["page"], beat=b["id"], frames=list(range(b["frames"])), out="frames") for b in sorted(timeline(), key=lambda b: b["page"])]
json.dump(jobs, open("jobs_full.json", "w")); print(sum(len(j["frames"]) for j in jobs), "frames")
