// usage: node render.js out_dir "f=1&t=1&w=300&h=250" ...  -> out_dir/<name>.png (raw, before compression)
const {chromium}=require('playwright'),path=require('path');
(async()=>{const [out,...jobs]=process.argv.slice(2);const b=await chromium.launch();
  for(const q of jobs){const p=new URLSearchParams(q),w=+p.get('w'),h=+p.get('h'),f=p.get('f'),ss=+(p.get('s')||(f==='2'?2:1));
    const pg=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:ss});
    pg.on('pageerror',e=>{console.error('PAGEERR',e.message);process.exitCode=1});
    await pg.goto('file://'+path.resolve(__dirname,'banner.html')+'?'+q);await pg.waitForFunction('window.READY===true');
    const name=`f${f}-t${p.get('t')||0}-${p.get('v')||'a'}-${w}x${h}`;
    await pg.screenshot({path:path.join(out,name+(ss>1?'@2x':'')+'.png')});await pg.close();console.log(name)}
  await b.close()})();
