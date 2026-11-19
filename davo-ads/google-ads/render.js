// usage: node render.js out_dir "n=name&f=1&t=1&w=300&h=250&s=2&c=mint&m=blur" ...  -> out_dir/<n>.png
const {chromium}=require('playwright'),path=require('path');
(async()=>{const [out,...jobs]=process.argv.slice(2);const b=await chromium.launch();
  const one=async q=>{const p=new URLSearchParams(q),w=+p.get('w'),h=+p.get('h'),ss=+(p.get('s')||1);
    const pg=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:ss});
    pg.on('pageerror',e=>{console.error('PAGEERR',q,e.message);process.exitCode=1});
    await pg.goto('file://'+path.resolve(__dirname,'banner.html')+'?'+q);await pg.waitForFunction('window.READY===true');
    await pg.screenshot({path:path.join(out,p.get('n')+'.png'),omitBackground:p.get('f')==='3'});await pg.close()};
  for(let i=0;i<jobs.length;i+=6)await Promise.all(jobs.slice(i,i+6).map(one));
  await b.close();console.log('rendered',jobs.length)})();
