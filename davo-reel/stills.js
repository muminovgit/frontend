// node stills.js out_dir t1,t2,...  -> PNG per time (single sample, for review)
const {chromium}=require('/opt/node-tools/node_modules/playwright');
const path=require('path'),fs=require('fs');
(async()=>{
  const [out,times]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch({args:['--allow-file-access-from-files']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>console.log('PAGEERR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text())});
  await p.goto('file://'+path.resolve(__dirname,'reel.html'));await p.evaluate(()=>window.ready);
  for(const t of times.split(',')){await p.evaluate(t=>seek(t),+t);await p.screenshot({path:`${out}/s_${t}.png`});console.log(`${out}/s_${t}.png`)}
  await b.close();
})();
