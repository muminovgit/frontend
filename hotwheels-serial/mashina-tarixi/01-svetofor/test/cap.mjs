import { chromium } from "playwright"; import path from "node:path"; import fs from "node:fs";
const [html, outDir, from, to] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
p.on("pageerror", (e) => console.log("PAGEERR", e.message));
await p.goto("file://" + path.resolve(html));
for (let f = +from; f < +to; f++) {
  await p.evaluate((f) => window.setFrame(f), f);
  await p.screenshot({ path: `${outDir}/f_${String(f).padStart(4, "0")}.png` });
}
await b.close();
