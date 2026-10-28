// node render.js <first> <last> <out.mp4> : renders frames [first,last) at 60fps, 8 subframes each, tmix-blended.
const {chromium}=require('/opt/node-tools/node_modules/playwright');
const path=require('path'),{spawn}=require('child_process');
const FPS=60,SUB=8;
(async()=>{
  const [a,b,out]=[+process.argv[2],+process.argv[3],process.argv[4]];
  const br=await chromium.launch({args:['--allow-file-access-from-files']});
  const p=await br.newPage({viewport:{width:1920,height:1080}});
  p.on('pageerror',e=>{console.error('PAGEERR',e.message);process.exit(1)});
  await p.goto('file://'+path.resolve(__dirname,'film.html'));await p.evaluate(()=>window.ready);
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS*SUB),'-i','-',
    '-vf',`tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB-1})',setpts=N/(${FPS}*TB)`,
    '-r',String(FPS),'-c:v','libx264','-preset','medium','-crf','12','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
  const t0=Date.now();
  for(let i=a;i<b;i++){
    for(let k=0;k<SUB;k++){
      const t=Math.max(0,(i+(k+.5)/SUB-.5)/FPS);
      await p.evaluate(t=>seek(t),t);
      const buf=await p.screenshot({type:'png'});
      if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
    }
    if((i-a)%60===0)console.log(`[${a}-${b}] frame ${i} ${((Date.now()-t0)/1000).toFixed(0)}s`);
  }
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await br.close();console.log('done',out);
})();
