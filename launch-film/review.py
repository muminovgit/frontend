# Usage: python3 review.py film.mp4 outdir
# 1) single-frame pop scan  2) frame-by-frame contact sheets for the fast moments
import sys,subprocess,numpy as np,os
src,out=sys.argv[1],sys.argv[2];os.makedirs(out,exist_ok=True)
w,h=240,135
raw=subprocess.run(['ffmpeg','-loglevel','error','-i',src,'-vf',f'scale={w}:{h},format=gray','-f','rawvideo','-'],capture_output=True).stdout
F=np.frombuffer(raw,np.uint8).reshape(-1,h,w).astype(np.float32)
d=lambda a,b:np.abs(F[a]-F[b]).mean()
print('frames',len(F))
pops=[]
for i in range(1,len(F)-1):
    a,b,c=d(i-1,i),d(i,i+1),d(i-1,i+1)
    if min(a,b)>2.0 and c<0.35*min(a,b):pops.append((i,round(a,2),round(b,2),round(c,2)))
print('single-frame pops:',pops if pops else 'none')
dd=[d(i,i+1) for i in range(len(F)-1)];top=np.argsort(dd)[-8:][::-1]
print('largest frame-to-frame changes (frame, t, diff):',[(int(i),round(i/60,3),round(dd[i],1)) for i in top])
moments={'send':(2.70,3.75),'drop':(5.48,6.05),'contract':(7.36,8.00),'pagefill':(9.66,10.75),'mark':(13.30,13.90)}
for name,(a,b) in moments.items():
    fa,fb=int(a*60),int(b*60);n=fb-fa;cols=8;rows=(n+cols-1)//cols
    subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',f'{fa/60:.4f}','-i',src,'-frames:v',str(n),'-vf',f'scale=320:180,tile={cols}x{rows}',f'{out}/{name}.png'])
    print('sheet',name,fa,fb)
