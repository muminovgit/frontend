const {chromium}=require('/opt/node-tools/node_modules/playwright');
const fs=require('fs'),path=require('path'),{execSync}=require('child_process');
(async()=>{
  const out=process.argv[2]||'kpi-reel.mp4', FPS=30, DUR=10;
  const dir=fs.mkdtempSync(path.join(process.env.TMPDIR||'/tmp','frames-'));
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+path.resolve(__dirname,'reel.html'));
  for(let i=0;i<FPS*DUR;i++){
    const d=await p.evaluate(t=>{draw(t);return document.getElementById('c').toDataURL('image/png')},i/FPS);
    fs.writeFileSync(path.join(dir,`f${String(i).padStart(4,'0')}.png`),Buffer.from(d.split(',')[1],'base64'));
  }
  await b.close();
  execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${dir}/f%04d.png -c:v libx264 -pix_fmt yuv420p -crf 16 ${out}`);
  fs.rmSync(dir,{recursive:true});
  console.log('done',out);
})();
