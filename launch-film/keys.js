const {chromium}=require('/opt/node-tools/node_modules/playwright');const path=require('path');
(async()=>{const b=await chromium.launch({args:['--allow-file-access-from-files']});const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+path.resolve(__dirname,'film.html'));await p.evaluate(()=>window.ready);
console.log(JSON.stringify(await p.evaluate(()=>KEYS.map(k=>+k.t.toFixed(4)))));await b.close()})();
