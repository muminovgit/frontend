const {chromium}=require('/opt/node-tools/node_modules/playwright');
const fs=require('fs'),path=require('path'),{execSync}=require('child_process');
(async()=>{
  const out=process.argv[2]||'kpi-attendance-reel.mp4', only=process.argv[3], FPS=30, DUR=16.8;
  const dir=fs.mkdtempSync(path.join(process.env.TMPDIR||'/tmp','frames-'));
  const b=await chromium.launch({args:['--allow-file-access-from-files']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+path.resolve(__dirname,'reel3.html'));
  await p.evaluate(()=>window.ready);
  const cvs=p.locator('#c');
  if(only){ // preview: comma separated times -> pngs
    for(const t of only.split(',')){await p.evaluate(t=>draw(t),+t);await cvs.screenshot({path:`${dir}/p${t}.png`});console.log(`${dir}/p${t}.png`)}
    await b.close();return;
  }
  const n=Math.round(FPS*DUR);
  for(let i=0;i<n;i++){
    await p.evaluate(t=>draw(t),i/FPS);
    await cvs.screenshot({path:path.join(dir,`f${String(i).padStart(4,'0')}.png`)});
  }
  await b.close();
  execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${dir}/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 17 ${out}`);
  fs.rmSync(dir,{recursive:true});
  console.log('done',out);
})();
