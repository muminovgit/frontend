// node stills.js out t1,t2,...  (uses GPU-less Chromium with SwiftShader WebGL)
const {chromium}=require('/opt/node-tools/node_modules/playwright');const path=require('path'),fs=require('fs');
(async()=>{const [out,times]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch({args:['--allow-file-access-from-files','--use-angle=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage({viewport:{width:1080,height:1920}});
 p.on('pageerror',e=>console.log('PAGEERR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text())});
 await p.goto('file://'+path.resolve(__dirname,'previz.html'));await p.evaluate(()=>window.ready);
 for(const t of times.split(',')){const t0=Date.now();await p.evaluate(t=>seek(t),+t);await p.screenshot({path:`${out}/s_${t}.png`});console.log(t,Date.now()-t0,'ms')}
 await b.close()})();
