const {chromium}=require('/opt/node-tools/node_modules/playwright');const path=require('path'),fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+path.resolve(__dirname,'../film/index.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(300);
const hits=await p.evaluate(()=>window.__dcardHits());fs.writeFileSync(path.resolve(__dirname,'../film/assets/audio/hits.json'),JSON.stringify(hits));console.log(JSON.stringify(hits));await b.close()})();
