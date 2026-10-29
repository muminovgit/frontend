// Render a seek(t) HTML composition to MP4 with real motion blur.
// usage: node render.js <page.html> <width> <height> <firstFrame> <lastFrame> <out.mp4> [fps=60] [subframes=8]
// The page must expose window.ready (Promise) and window.seek(t). Frames [first,last) are rendered;
// each frame averages `subframes` samples across a 360° shutter via ffmpeg tmix. Run 4 workers on
// disjoint frame ranges in parallel, then concat the parts (see SKILL.md).
const {chromium}=require(process.env.PLAYWRIGHT_PATH||'/opt/node-tools/node_modules/playwright');
const path=require('path'),{spawn}=require('child_process');
(async()=>{
  const [page,w,h,a,b,out,fpsA,subA]=process.argv.slice(2);const W=+w,H=+h,FPS=+(fpsA||60),SUB=+(subA||8);
  const br=await chromium.launch({args:['--allow-file-access-from-files']});
  const p=await br.newPage({viewport:{width:W,height:H}});
  p.on('pageerror',e=>{console.error('PAGEERR',e.message);process.exit(1)});
  await p.goto('file://'+path.resolve(page));await p.evaluate(()=>window.ready);
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS*SUB),'-i','-',
    '-vf',`tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB-1})',setpts=N/(${FPS}*TB)`,
    '-r',String(FPS),'-c:v','libx264','-preset','medium','-crf','14','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
  for(let i=+a;i<+b;i++){for(let k=0;k<SUB;k++){const t=Math.max(0,(i+(k+.5)/SUB-.5)/FPS);await p.evaluate(t=>seek(t),t);
    const buf=await p.screenshot({type:'png'});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r))}
    if((i-a)%120===0)console.log(`[${a}-${b}] frame ${i}`)}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await br.close();console.log('done',out);
})();
