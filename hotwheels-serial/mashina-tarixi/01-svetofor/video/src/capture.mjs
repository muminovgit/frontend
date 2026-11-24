// usage: node capture.mjs jobs.json   jobs = [{page, beat, frames:[...], out}]  -> PNGs <out>/<beat>_<frame>.png
import { chromium } from "playwright"; import fs from "node:fs"; import path from "node:path";
const jobs = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
p.on("pageerror", (e) => console.log("PAGEERR", e.message));
let cur = null;
for (const j of jobs) {
  if (cur !== j.page) { await p.goto("file://" + path.resolve("pages", j.page + ".html")); cur = j.page; }
  fs.mkdirSync(j.out, { recursive: true });
  for (const f of j.frames) {
    await p.evaluate(([f, beat]) => window.setFrame(f, beat), [f, j.beat]);
    await p.screenshot({ path: `${j.out}/${j.name ?? j.beat}_${String(f).padStart(4, "0")}.png` });
  }
  console.log("done", j.beat, j.frames.length);
}
await b.close();
