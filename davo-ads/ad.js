// Davo Delivery — parametric motion ad (9:16). Each ad-XX.html sets window.VARIANT, then loads this file.
// Every pixel is a function of t: window.seek(t). Text is rendered from VARIANT, never baked into images.
const W=1080,H=1920,VA=window.VARIANT;
const Y='#ffce68',PK='#fb4669',VI='#5e3a9a',G='#01bdac',BLUE='#2f6bff',WH='#ffffff';
const T=VA.T,DUR=T.dur;
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)),P=(t,s,d)=>clamp((t-s)/d),lerp=(a,b,k)=>a+(b-a)*k;
const E={out:k=>1-Math.pow(1-k,3),in:k=>k*k*k,io:k=>k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2,expo:k=>k>=1?1:1-Math.pow(2,-10*k),back:k=>{const c=1.7;return 1+(c+1)*Math.pow(k-1,3)+c*Math.pow(k-1,2)}};
function spring(t,f=2.4,z=.5){if(t<=0)return 0;const w=2*Math.PI*f,wd=w*Math.sqrt(1-z*z);return 1-Math.exp(-z*w*t)*(Math.cos(wd*t)+z*w/wd*Math.sin(wd*t))}
function rnd(i){const x=Math.sin(i*127.1+311.7)*43758.5453;return x-Math.floor(x)}
const cv=document.getElementById('c'),ctx=cv.getContext('2d');const IM={};

// ---------------------------------------------------------------- helpers
const F=(w,s,f='Montserrat')=>`${w} ${s}px "${f}"`;
function txt(s,x,y,size,o={}){ctx.save();ctx.globalAlpha*=o.a??1;ctx.font=F(o.w??800,size,o.f);ctx.textAlign=o.al??'center';ctx.textBaseline=o.base??'middle';ctx.fillStyle=o.c??WH;
  if(o.ls)ctx.letterSpacing=o.ls+'px';if(o.glow){ctx.shadowColor=o.glow;ctx.shadowBlur=o.gb??24}ctx.fillText(s,x,y);ctx.restore()}
function tw(s,size,w=800,f='Montserrat'){ctx.save();ctx.font=F(w,size,f);const v=ctx.measureText(s).width;ctx.restore();return v}
function rr(x,y,w,h,r){ctx.beginPath();ctx.roundRect(x,y,w,h,r)}
function glass(x,y,w,h,r,a=1){ctx.save();ctx.globalAlpha*=a;rr(x,y,w,h,r);ctx.fillStyle='rgba(255,255,255,.10)';ctx.fill();ctx.strokeStyle='rgba(255,255,255,.22)';ctx.lineWidth=2;ctx.stroke();
  const g=ctx.createLinearGradient(x,y,x,y+h);g.addColorStop(0,'rgba(255,255,255,.10)');g.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=g;rr(x,y,w,h/2,r);ctx.fill();ctx.restore()}
function check(x,y,s,k,col,lw){if(k<=0)return;ctx.save();ctx.strokeStyle=col;ctx.lineWidth=lw;ctx.lineCap='round';ctx.lineJoin='round';const p=[[-.5,0],[-.15,.35],[.55,-.4]],L1=Math.hypot(.35,.35),L2=Math.hypot(.7,.75),tot=(L1+L2)*k;
  ctx.beginPath();ctx.moveTo(x+p[0][0]*s,y+p[0][1]*s);if(tot<=L1){const q=tot/L1;ctx.lineTo(x+lerp(p[0][0],p[1][0],q)*s,y+lerp(p[0][1],p[1][1],q)*s)}else{ctx.lineTo(x+p[1][0]*s,y+p[1][1]*s);const q=(tot-L1)/L2;ctx.lineTo(x+lerp(p[1][0],p[2][0],q)*s,y+lerp(p[1][1],p[2][1],q)*s)}ctx.stroke();ctx.restore()}
function flash(a,c='#fff'){if(a<=0)return;ctx.save();ctx.globalAlpha=clamp(a);ctx.fillStyle=c;ctx.fillRect(-50,-50,W+100,H+100);ctx.restore()}
// Davo logo: white app tile + 4 brand petals + white cross (vector rebuild of the client's mark)
function logo(x,y,s,a=1,petalK=1){ctx.save();ctx.globalAlpha*=a;ctx.translate(x,y);ctx.fillStyle=WH;ctx.shadowColor='rgba(0,0,0,.25)';ctx.shadowBlur=s*.15;rr(-s/2,-s/2,s,s,s*.24);ctx.fill();ctx.shadowBlur=0;
  const u=s/131;[[Y,-1,-1],[PK,1,-1],[VI,-1,1],[G,1,1]].forEach(([c,sx,sy],i)=>{const k=clamp(petalK*1.4-i*.1);ctx.fillStyle=c;ctx.beginPath();ctx.arc(sx*20*u*k,sy*20*u*k,28.5*u*Math.max(.01,k),0,7);ctx.fill()});
  ctx.fillStyle=WH;ctx.beginPath();const a2=10.5*u,b=29*u;ctx.moveTo(-a2,-b);ctx.lineTo(a2,-b);ctx.lineTo(a2,-a2);ctx.lineTo(b,-a2);ctx.lineTo(b,a2);ctx.lineTo(a2,a2);ctx.lineTo(a2,b);ctx.lineTo(-a2,b);ctx.lineTo(-a2,a2);ctx.lineTo(-b,a2);ctx.lineTo(-b,-a2);ctx.lineTo(-a2,-a2);ctx.closePath();ctx.fill();ctx.restore()}
const KICKS=[[T.hook,22],[T.cta,10],...(VA.kicks||[])];
function shake(t){let x=0,y=0;for(const[k,a]of KICKS){const d=t-k;if(d<0||d>.6)continue;const e=a*Math.exp(-d*12);x+=e*Math.sin(d*90);y+=e*Math.cos(d*70)}return[x,y]}

// ---------------------------------------------------------------- background
function bg(t){const g=ctx.createRadialGradient(540,900,100,540,960,1300);g.addColorStop(0,'#3a1760');g.addColorStop(.55,'#22103c');g.addColorStop(1,'#110820');ctx.fillStyle=g;ctx.fillRect(-60,-60,W+120,H+120);
  [[Y,.12,.18],[PK,.88,.32],[G,.15,.78],[VI,.85,.85]].forEach(([c,x,y],i)=>{const px=x*W+Math.sin(t*.6+i*2)*60,py=y*H+Math.cos(t*.5+i)*80,r=520;const rg=ctx.createRadialGradient(px,py,0,px,py,r);rg.addColorStop(0,c+'40');rg.addColorStop(1,c+'00');ctx.fillStyle=rg;ctx.fillRect(px-r,py-r,2*r,2*r)})}

// ---------------------------------------------------------------- headline (word pop)
let HL=null;
function layoutHeadline(){const words=VA.headline.split(' ');let size=VA.hsize||96,lines;
  for(;size>=60;size-=4){lines=[[]];let w=0;const maxW=920;for(const wd of words){const ww=tw(wd,size,900);if(w+ww>maxW&&lines[lines.length-1].length){lines.push([]);w=0}lines[lines.length-1].push(wd);w+=ww+size*.28}if(lines.length<=(VA.hlines||4))break}
  const out=[];let idx=0;lines.forEach((ln,li)=>{const tot=ln.reduce((a,wd)=>a+tw(wd,size,900),0)+(ln.length-1)*size*.28;let x=540-tot/2;ln.forEach(wd=>{const ww=tw(wd,size,900);out.push({wd,x:x+ww/2,y:VA.hy+li*size*1.12,i:idx,hl:VA.highlight.includes(idx)});idx++;x+=ww+size*.28})});
  HL={words:out,size}}
function headline(t){const ex=VA.hexit?ease(P(t,VA.hexit,.4)):0;for(const w of HL.words){const t0=T.words+w.i*(VA.wstep||.075),k=spring(t-t0,2.6,.5);if(t<t0)continue;
  ctx.save();ctx.translate(w.x,w.y+(1-Math.min(1,k))*40-ex*60);const s=lerp(.3,1,Math.min(1.15,k));ctx.scale(s,s);ctx.globalAlpha=clamp((t-t0)/.12)*(1-ex);
  if(w.hl){ctx.save();const ww=tw(w.wd,HL.size,900);const hk=E.out(P(t,t0+.25,.35));ctx.fillStyle=PK;ctx.globalAlpha*=.95;rr(-ww/2-14,-HL.size*.55,(ww+28)*hk,HL.size*1.1,18);ctx.fill();ctx.restore()}
  txt(w.wd,0,4,HL.size,{w:900,c:WH});ctx.restore()}}
function ease(k){return E.io(k)}

// ---------------------------------------------------------------- bullets + CTA + footnote
const BUL=[['clock','30 daqiqada yetkazib beramiz*',Y],['shield','Faqat litsenziyali mahsulotlar',G],['pin','200+ rasmiy dorixona',PK]];
function icon(kind,x,y,c){ctx.save();ctx.translate(x,y);ctx.fillStyle=c;ctx.beginPath();ctx.arc(0,0,36,0,7);ctx.fill();ctx.strokeStyle='#1b0d2e';ctx.fillStyle='#1b0d2e';ctx.lineWidth=6;ctx.lineCap='round';
  if(kind==='clock'){ctx.beginPath();ctx.arc(0,0,20,0,7);ctx.stroke();ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(0,-12);ctx.moveTo(0,0);ctx.lineTo(9,6);ctx.stroke()}
  if(kind==='shield'){ctx.beginPath();ctx.moveTo(0,-22);ctx.lineTo(18,-14);ctx.lineTo(16,6);ctx.quadraticCurveTo(10,18,0,24);ctx.quadraticCurveTo(-10,18,-16,6);ctx.lineTo(-18,-14);ctx.closePath();ctx.stroke();check(0,1,22,1,'#1b0d2e',5)}
  if(kind==='pin'){ctx.beginPath();ctx.arc(0,-6,13,Math.PI*.85,Math.PI*2.15);ctx.lineTo(0,22);ctx.closePath();ctx.fill();ctx.fillStyle=c;ctx.beginPath();ctx.arc(0,-6,5,0,7);ctx.fill()}
  ctx.restore()}
function bullets(t){if(t<T.bul)return;const out=E.io(P(t,T.cta,.45));BUL.forEach(([ic,l,c],i)=>{const t0=T.bul+i*.16,k=E.expo(P(t,t0,.45));if(k<=0)return;
  const y=(VA.by??800)+i*142,x=90+(1-k)*900,s=1;
  ctx.save();ctx.translate(540,y+50);ctx.scale(s,s);ctx.translate(-540,-(y+50));glass(x,y,900,124,62,k);icon(ic,x+70,y+62,c);txt(l,x+128,y+65,44,{al:'left',w:800,a:k});ctx.restore()})}
function cta(t){if(t<T.cta)return;const k=spring(t-T.cta,1.8,.6),y0=1290;
  logo(330,y0,150,clamp((t-T.cta)/.15),E.out(P(t,T.cta,.5)));const nk=E.out(P(t,T.cta+.1,.4));
  ctx.save();ctx.beginPath();ctx.rect(420,y0-90,620,180);ctx.clip();txt('Davo Delivery',430-(1-nk)*300,y0-18,62,{al:'left',w:900});txt('Medical',432-(1-nk)*300,y0+40,34,{al:'left',w:600,c:'rgba(255,255,255,.7)'});ctx.restore();
  const bk=spring(t-T.cta-.25,2,.55),pulse=1+.035*Math.max(0,Math.sin((t-T.cta-.8)*7));ctx.save();ctx.translate(540,1440);ctx.scale(bk*pulse,bk*pulse);
  ctx.shadowColor='rgba(47,107,255,.7)';ctx.shadowBlur=40;ctx.fillStyle=BLUE;rr(-350,-62,700,124,62);ctx.fill();ctx.shadowBlur=0;
  const sh=P(t,T.cta+.9,.7);if(sh>0&&sh<1){ctx.save();rr(-350,-62,700,124,62);ctx.clip();const x=lerp(-500,500,sh),g=ctx.createLinearGradient(x-90,0,x+90,0);g.addColorStop(0,'rgba(255,255,255,0)');g.addColorStop(.5,'rgba(255,255,255,.5)');g.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=g;ctx.fillRect(-350,-62,700,124);ctx.restore()}
  txt('⬇  Ilovani yuklab oling',0,3,48,{w:800});ctx.restore();
  const sk=E.out(P(t,T.cta+.45,.4));['App Store','Google Play'].forEach((s,i)=>{const x=i?680:400;ctx.save();ctx.globalAlpha=sk;rr(x-140,1528,280,60,30);ctx.fillStyle='rgba(0,0,0,.55)';ctx.fill();ctx.strokeStyle='rgba(255,255,255,.35)';ctx.lineWidth=2;ctx.stroke();txt(s,x,1559,29,{w:700,f:'Inter'});ctx.restore()})}
function foot(t){if(t<T.bul)return;const a=E.out(P(t,T.bul,.4))*.75;const lines=['*Yetkazish vaqti manzil va buyurtmaga qarab farq qilishi mumkin.',...(VA.footExtra||[])];
  lines.forEach((l,i)=>txt(l,540,1618+i*28,22,{w:500,f:'Inter',c:'rgba(255,255,255,.75)',a}))}

// ---------------------------------------------------------------- hooks
function hook(t){const H=VA.hookObj;const d=t-T.hook;if(d<0)return;const out=E.io(P(t,VA.hookOut??1.6,.45));if(out>=1)return;
  const s=d<.18?lerp(2.6,1,E.in(d/.18)):1+.08*Math.exp(-(d-.18)*8)*Math.cos((d-.18)*30);const x=lerp(540,VA.hookTo?.[0]??540,out),y=lerp(VA.hookY??1000,VA.hookTo?.[1]??1000,out);
  ctx.save();ctx.translate(x,y);ctx.scale(s*lerp(1,VA.hookToS??.0,out),s*lerp(1,VA.hookToS??0,out));ctx.rotate(Math.sin(d*3)*.04);ctx.globalAlpha=clamp(d/.06);
  if(H.kind==='emoji'){ctx.font='300px "Noto Color Emoji"';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(H.e,0,0)}
  if(H.kind==='tag'){ctx.rotate(-.12);ctx.fillStyle=PK;ctx.beginPath();ctx.moveTo(-200,-110);ctx.lineTo(120,-110);ctx.lineTo(210,0);ctx.lineTo(120,110);ctx.lineTo(-200,110);ctx.closePath();ctx.fill();ctx.fillStyle='#1b0d2e';ctx.beginPath();ctx.arc(140,0,22,0,7);ctx.fill();txt("so'm?",-40,6,92,{w:900})}
  if(H.kind==='search'){ctx.strokeStyle=WH;ctx.lineWidth=34;ctx.lineCap='round';ctx.beginPath();ctx.arc(-30,-30,110,0,7);ctx.stroke();ctx.beginPath();ctx.moveTo(52,52);ctx.lineTo(150,150);ctx.stroke();ctx.fillStyle=Y;ctx.beginPath();ctx.arc(-30,-30,60,0,7);ctx.globalAlpha*=.35;ctx.fill()}
  ctx.restore()}

// ---------------------------------------------------------------- DEMO A: price comparison race (sample prices)
function pillIcon(x,y,s){ctx.save();ctx.translate(x,y);ctx.rotate(-.6);rr(-s,-s*.42,s*2,s*.84,s*.42);ctx.fillStyle=WH;ctx.fill();ctx.beginPath();ctx.rect(0,-s*.42,s,s*.84);ctx.clip();rr(-s,-s*.42,s*2,s*.84,s*.42);ctx.fillStyle=PK;ctx.fill();ctx.restore()}
function demoPrice(t){const d0=T.demo,out=E.io(P(t,T.bul-.15,.4));if(t<d0||out>=1)return;const k=E.expo(P(t,d0,.5));const D=VA.demo;
  ctx.save();ctx.globalAlpha=k*(1-out);ctx.translate(0,(1-k)*200-out*120);const X=100,Y0=VA.dy??720,Wc=880,Hc=640;glass(X,Y0,Wc,Hc,44);
  pillIcon(X+80,Y0+82,40);txt(D.drug,X+150,Y0+70,44,{al:'left',w:800});txt(D.drugSub,X+150,Y0+118,30,{al:'left',w:600,f:'Inter',c:'rgba(255,255,255,.7)'});
  const max=Math.max(...D.rows.map(r=>r[2]));const win=D.rows.reduce((a,r,i)=>r[2]<D.rows[a][2]?i:a,0);const hl=E.out(P(t,D.tWin,.35));
  D.rows.forEach(([nm,km,pr],i)=>{const y=Y0+190+i*140,g=E.io(P(t,d0+.45+i*.18,.9)),isW=i===win;const dim=isW?1:lerp(1,.45,hl);
    ctx.save();ctx.globalAlpha*=dim;if(isW&&hl>0){ctx.save();ctx.globalAlpha*=hl;rr(X+24,y-18,Wc-48,124,28);ctx.fillStyle='rgba(1,189,172,.22)';ctx.fill();ctx.strokeStyle=G;ctx.lineWidth=4;ctx.stroke();ctx.restore()}
    txt(nm,X+56,y+16,34,{al:'left',w:700});txt(km,X+56+tw(nm,34,700)+16,y+18,28,{al:'left',w:500,f:'Inter',c:'rgba(255,255,255,.6)'});
    const bw=480*(pr/max)*g;rr(X+56,y+52,480,26,13);ctx.fillStyle='rgba(255,255,255,.12)';ctx.fill();if(bw>2){rr(X+56,y+52,bw,26,13);ctx.fillStyle=isW&&hl>0?G:Y;ctx.fill()}
    const val=Math.round(pr*g/100)*100;txt(val.toLocaleString('ru-RU').replace(/,/g,' ')+" so'm",X+Wc-56,y+64,40,{al:'right',w:900});ctx.restore()});
  if(hl>0){const by=Y0+190+win*140+16,bs=spring(t-D.tWin,2.4,.45);ctx.save();ctx.translate(X+Wc-190,by);ctx.scale(bs,bs);rr(-130,-30,260,60,30);ctx.fillStyle=G;ctx.fill();txt('✓ Eng arzon',0,3,30,{w:800,c:'#06231f'});ctx.restore()}
  txt('Narxlar namuna sifatida',X+Wc-40,Y0+Hc-34,24,{al:'right',w:500,f:'Inter',c:'rgba(255,255,255,.55)'});ctx.restore()}

// ---------------------------------------------------------------- DEMO B: products -> bag -> map route -> door
function bag(x,y,s,a){ctx.save();ctx.globalAlpha*=a;ctx.translate(x,y);ctx.scale(s,s);ctx.fillStyle=VI;rr(-120,-90,240,210,30);ctx.fill();ctx.strokeStyle=VI;ctx.lineWidth=16;ctx.beginPath();ctx.arc(0,-90,55,Math.PI,0);ctx.stroke();ctx.restore();logo(x,y+15*s,110*s,a)}
function demoDeliver(t){const d0=T.demo,out=E.io(P(t,T.bul-.15,.4));if(t<d0||out>=1)return;const D=VA.demo,mapT=D.tMap;
  ctx.save();ctx.globalAlpha=1-out;ctx.translate(0,-out*120);
  if(t<mapT+.3){const a=1-P(t,mapT,.3);const items=[['aidkit',-270],['capsule',0],['vitamins',270]];const bs=spring(t-d0-.2,2,.6);
    items.forEach(([n,dx],i)=>{const q=E.io(P(t,d0+i*.15,.8)),sz=230*(1-.6*q);const x=lerp(540+dx,540,q),y=lerp(900,1100,q)-Math.sin(q*Math.PI)*150;ctx.save();ctx.globalAlpha*=a*(1-P(q,.92,.08))*clamp((t-d0-i*.15+.2)/.2);ctx.translate(x,y);ctx.rotate((1-q)*(i-1)*.3);
      if(n==='capsule'){pillIcon(0,0,sz*.42)}else{const im=IM[n];ctx.drawImage(im,-sz/2,-sz/2*im.height/im.width,sz,sz*im.height/im.width)}ctx.restore()});
    bag(540,1150,bs*(1+.08*Math.exp(-Math.max(0,t-d0-.95)*9)*Math.sin(Math.max(0,t-d0-.95)*30)),a)}
  if(t>=mapT){const k=E.expo(P(t,mapT,.5)),X=100,Y0=VA.dy??720,Wm=880,Hm=640;ctx.save();ctx.globalAlpha*=k;ctx.translate(0,(1-k)*160);
    ctx.save();rr(X,Y0,Wm,Hm,44);ctx.clip();ctx.fillStyle='#eef1f6';ctx.fillRect(X,Y0,Wm,Hm);ctx.fillStyle='#d9f2e6';[[.1,.1,.25,.3],[.65,.55,.3,.35]].forEach(([a,b,c,d])=>{rr(X+a*Wm,Y0+b*Hm,c*Wm,d*Hm,30);ctx.fill()});
    ctx.strokeStyle='#ffffff';ctx.lineWidth=18;for(let i=0;i<6;i++){ctx.beginPath();ctx.moveTo(X,Y0+80+i*110+rnd(i)*20);ctx.lineTo(X+Wm,Y0+40+i*115);ctx.stroke();ctx.beginPath();ctx.moveTo(X+70+i*160,Y0);ctx.lineTo(X+40+i*165+rnd(i+3)*30,Y0+Hm);ctx.stroke()}
    const pts=[[X+150,Y0+500],[X+310,Y0+430],[X+360,Y0+270],[X+560,Y0+230],[X+700,Y0+150]];const rk=E.io(P(t,mapT+.35,1.3));const seg=pts.length-1,pos=rk*seg,si=Math.min(seg-1,Math.floor(pos)),sf=pos-si;
    ctx.strokeStyle=PK;ctx.lineWidth=10;ctx.lineCap='round';ctx.setLineDash([2,22]);ctx.beginPath();ctx.moveTo(...pts[0]);for(let i=1;i<=si;i++)ctx.lineTo(...pts[i]);const cx=lerp(pts[si][0],pts[si+1][0],sf),cy=lerp(pts[si][1],pts[si+1][1],sf);ctx.lineTo(cx,cy);ctx.stroke();ctx.setLineDash([]);
    const pin=(x,y,c,lab)=>{ctx.fillStyle=c;ctx.beginPath();ctx.arc(x,y-34,26,Math.PI*.8,Math.PI*2.2);ctx.lineTo(x,y);ctx.closePath();ctx.fill();ctx.fillStyle=WH;ctx.beginPath();ctx.arc(x,y-34,10,0,7);ctx.fill();txt(lab,x,y+26,26,{w:700,f:'Inter',c:'#2a2140'})};
    pin(pts[0][0],pts[0][1],PK,'Dorixona');const done=P(t,mapT+1.65,.3);const hp=1+.15*Math.sin(done*Math.PI);ctx.save();ctx.translate(pts[4][0],pts[4][1]);ctx.scale(hp,hp);pin(0,0,G,'Uyingiz');ctx.restore();
    ctx.save();ctx.translate(cx,cy);ctx.fillStyle=VI;ctx.beginPath();ctx.arc(0,0,30,0,7);ctx.fill();ctx.font='34px "Noto Color Emoji"';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('🛵',0,2);ctx.restore();ctx.restore();
    ctx.strokeStyle='rgba(255,255,255,.4)';ctx.lineWidth=3;rr(X,Y0,Wm,Hm,44);ctx.stroke();
    const ek=spring(t-mapT-.3,2.2,.5);ctx.save();ctx.translate(X+Wm-170,Y0+70);ctx.scale(ek,ek);rr(-130,-34,260,68,34);ctx.fillStyle='#1b0d2e';ctx.fill();txt('⏱ ~30 daq*',0,3,32,{w:800});ctx.restore();
    if(done>0){const ds=spring(t-mapT-1.65,2.4,.45);ctx.save();ctx.translate(X+Wm/2,Y0+Hm-70);ctx.scale(ds,ds);rr(-230,-38,460,76,38);ctx.fillStyle=G;ctx.fill();txt('✓ Eshigingizgacha',0,3,34,{w:800,c:'#06231f'});ctx.restore()}
    ctx.restore()}
  ctx.restore()}

// ---------------------------------------------------------------- DEMO D: phone search -> results -> ETA
function demoSearch(t){const d0=T.demo,out=E.io(P(t,T.bul-.15,.4));if(t<d0||out>=1)return;const D=VA.demo;const k=spring(t-d0,1.6,.62);
  const pw=640,sc=pw/590,ph=640,px=540-pw/2,py=VA.dy??700;ctx.save();ctx.globalAlpha=clamp(k*1.3)*(1-out);ctx.translate(540,py+ph/2);ctx.rotate((1-k)*.18-.03+Math.sin(t*1.2)*.008);ctx.scale(lerp(.7,1,k)*(1-out*.15),lerp(.7,1,k)*(1-out*.15));ctx.translate(-540,-(py+ph/2));
  ctx.save();ctx.shadowColor='rgba(0,0,0,.5)';ctx.shadowBlur=60;ctx.fillStyle='#0d0d12';rr(px-16,py-16,pw+32,ph+32,64);ctx.fill();ctx.restore();
  ctx.save();rr(px,py,pw,ph,50);ctx.clip();ctx.drawImage(IM.app,0,0,590,ph/sc,px,py,pw,ph);
  // status bar
  ctx.fillStyle='rgba(255,255,255,0)';txt('9:41',px+70,py+38,26,{w:700,f:'Inter',c:'#111'});
  // typing in the real search field
  const fx=px+26*sc,fy=py+192*sc,fw=538*sc,fh=82*sc;const typ=P(t,d0+.5,.9),s=D.query.slice(0,Math.round(typ*D.query.length));
  if(typ>0){rr(fx,fy,fw,fh,fh/2);ctx.fillStyle='#ffffff';ctx.fill();ctx.strokeStyle='#5ecdf0';ctx.lineWidth=3;ctx.stroke();txt(s+(Math.floor(t*3)%2?'|':''),fx+70,fy+fh/2+2,30,{al:'left',w:600,f:'Inter',c:'#111'});
    ctx.strokeStyle='#666';ctx.lineWidth=4;ctx.beginPath();ctx.arc(fx+38,fy+fh/2-2,11,0,7);ctx.moveTo(fx+46,fy+fh/2+6);ctx.lineTo(fx+54,fy+fh/2+14);ctx.stroke()}
  // results sheet
  const rk=E.expo(P(t,d0+1.5,.5));if(rk>0){const ry=fy+fh+14;ctx.save();ctx.globalAlpha*=rk;ctx.translate(0,(1-rk)*40);rr(fx,ry,fw,3*96+20,26);ctx.fillStyle='#fff';ctx.shadowColor='rgba(0,0,0,.18)';ctx.shadowBlur=30;ctx.fill();ctx.shadowBlur=0;
    D.results.forEach((r,i)=>{const y=ry+14+i*96,sel=i===0&&t>d0+2.3;if(sel){rr(fx+8,y,fw-16,88,18);ctx.fillStyle='#e9fbf8';ctx.fill()}
      ctx.save();ctx.translate(fx+46,y+44);ctx.fillStyle='#f3f3f6';rr(-30,-30,60,60,14);ctx.fill();ctx.restore();pillIcon(fx+46,y+44,16);
      txt(r,fx+92,y+32,24,{al:'left',w:600,f:'Inter',c:'#111'});txt('✓ Dorixonalarda mavjud',fx+92,y+64,20,{al:'left',w:600,f:'Inter',c:'#01a596'})});ctx.restore()}
  ctx.restore();ctx.restore();
  // ETA sticker outside the phone
  if(t>d0+2.4){const ek=spring(t-d0-2.4,2.2,.45);ctx.save();ctx.globalAlpha=1-out;ctx.translate(810,py+ph-60);ctx.rotate(-.08);ctx.scale(ek,ek);rr(-170,-56,340,112,56);ctx.fillStyle=Y;ctx.fill();txt('⏱ ~30 daq*',0,4,46,{w:900,c:'#1b0d2e'});ctx.restore()}}

// ---------------------------------------------------------------- frame
const DEMOS={price:demoPrice,deliver:demoDeliver,search:demoSearch};
function draw(t){ctx.setTransform(1,0,0,1,0,0);bg(t);const[sx,sy]=shake(t);ctx.translate(sx,sy);
  hook(t);headline(t);DEMOS[VA.demo.kind](t);bullets(t);cta(t);foot(t);
  ctx.setTransform(1,0,0,1,0,0);flash(E.in(P(t,DUR-.35,.35)),'#110820');flash((1-P(t,0,.12))*.0)}
function loadImg(src){return new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src=src})}
window.ready=(async()=>{await Promise.all(['900 90px Montserrat','800 90px Montserrat','600 90px Montserrat','500 30px Inter','600 30px Inter','700 30px Inter','300px "Noto Color Emoji"'].map(f=>document.fonts.load(f,"Oʻ‘’'✓⬇⏱🛵🤧")));
  for(const n of['aidkit','vitamins'])IM[n]=await loadImg('assets/'+n+'.png');IM.app=await loadImg('assets/app-page.png');layoutHeadline();draw(0);return true})();
window.seek=t=>draw(Math.min(Math.max(t,0),DUR-1e-4));window.DUR=DUR;
