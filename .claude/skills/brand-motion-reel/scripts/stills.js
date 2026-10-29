// Single-sample review stills: node stills.js <page.html> <width> <height> <outdir> <t1,t2,...>
const {chromium}=require(process.env.PLAYWRIGHT_PATH||'/opt/node-tools/node_modules/playwright');const path=require('path'),fs=require('fs');
(async()=>{const [page,w,h,out,times]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:+w,height:+h}});
  p.on('pageerror',e=>console.log('PAGEERR',e.message));await p.goto('file://'+path.resolve(page));await p.evaluate(()=>window.ready);
  for(const t of times.split(',')){await p.evaluate(t=>seek(t),+t);await p.screenshot({path:`${out}/s_${t}.png`});console.log(`${out}/s_${t}.png`)}
  await b.close()})();
