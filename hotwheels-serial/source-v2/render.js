const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const dir = __dirname, out = path.join(dir, 'frames');
  fs.mkdirSync(out, { recursive: true });
  const only = process.argv[2] ? process.argv[2].split(',').map(Number) : null;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(dir, 'index.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const FPS = 30, TOTAL = 21.6;
  const times = only || [...Array(Math.round(FPS * TOTAL)).keys()].map(i => i / FPS);
  for (let i = 0; i < times.length; i++) {
    await p.evaluate(t => render(t), times[i]);
    const name = only ? `check_${times[i]}.jpg` : `f${String(i).padStart(4, '0')}.jpg`;
    await p.screenshot({ path: path.join(only ? dir : out, name), type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
