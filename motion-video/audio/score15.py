# Original 15s score + sound design for reel5 (120 BPM). Cuts: 1.7 morph, 4.3 push, 8.4 push, 12.15 collapse, 12.4 resolve.
import numpy as np, wave, sys
SR=44100; DUR=15.0; n=int(SR*DUR); L=np.zeros(n); R=np.zeros(n)
beat=.5; bar=2.0
def nf(m): return 440*2**((m-69)/12)
def add(sig,t0,g=1.0,pan=0.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if i>=n or j<=0: return
    L[i:j]+=sig[:j-i]*g*(1-pan); R[i:j]+=sig[:j-i]*g*(1+pan)
def ts(d): return np.arange(int(d*SR))/SR
rng=np.random.default_rng(7)
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x); s=0.0
    for i,v in enumerate(x): s+=a*(v-s); y[i]=s
    return y
prog=[[45,52,57,60,64],[41,48,53,57,64],[48,55,60,64,67],[43,50,55,59,62]]  # Am F C G
# pad (whole piece)
for b in range(8):
    ch=prog[b%4]; t=ts(bar+.6); e=np.minimum(1,t/.5)*np.minimum(1,(bar+.6-t)/.6)
    pad=sum(np.sin(2*np.pi*nf(m)*t+np.sin(2*np.pi*.3*t))*.5+np.sin(2*np.pi*nf(m)*1.004*t)*.5 for m in ch)/len(ch)
    add(pad*e*.09,b*bar)
# intro ticks (odometer) 0.1–1.3
for k in range(18):
    t=ts(.03); add(rng.standard_normal(len(t))*np.exp(-t*300)*.12,.1+k*.065,pan=(.3 if k%2 else -.3))
# groove from the morph (2.0) until resolve (12.2)
for b4 in range(int(2/beat),int(12.2/beat)):
    tt=b4*beat; ch=prog[int(tt/bar)%4]
    if b4%2==0:
        t=ts(.3); f=120*np.exp(-t*20)+45; add(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*11)*.6,tt)
    else:
        t=ts(.2); add(lp(rng.standard_normal(len(t)),.5)*np.exp(-t*20)*.22,tt)
    t=ts(.06); add(np.diff(rng.standard_normal(len(t)),prepend=0)*np.exp(-t*70)*.06,tt+beat/2,pan=.25)
    t=ts(beat*.95); add(np.tanh(2*np.sin(2*np.pi*nf(ch[0]-12)*t))*np.exp(-t*4)*.18,tt)
    for k,m in enumerate([ch[2]+12,ch[4]+12]):
        t=ts(.3); add((np.sin(2*np.pi*nf(m)*t)+.25*np.sin(4*np.pi*nf(m)*t))*np.exp(-t*12)*.07,tt+k*beat/2,pan=(-.4 if k else .4))
# whooshes (filtered noise swell into the cut)
def whoosh(tc,d=.55,g=.35):
    t=ts(d); env=np.sin(np.pi*t/d)**2; x=rng.standard_normal(len(t))
    a=np.linspace(.02,.35,len(t)); y=np.empty_like(x); s=0.0
    for i,v in enumerate(x): s+=a[i]*(v-s); y[i]=s
    add(y*env*g*2.2,tc-d*.6,pan=0)
for tc in (1.95,4.5,8.6,12.3): whoosh(tc)
# verify chime at 3.3
for m,dl in ((88,0),(95,.07)):
    t=ts(1.2); add((np.sin(2*np.pi*nf(m)*t)+.3*np.sin(2*np.pi*nf(m)*2.01*t))*np.exp(-t*4)*.16,3.3+dl)
# soft UI pops on dashboard tiles (8.7..9.1) and export (10.8)
for k in range(6):
    t=ts(.08); add(np.sin(2*np.pi*(900+k*120)*t)*np.exp(-t*60)*.10,8.7+k*.07)
t=ts(.5); add(np.sin(2*np.pi*nf(84)*t)*np.exp(-t*9)*.14,10.8)
# resolve impact 12.4
t=ts(2.2); f=80*np.exp(-t*3)+38; add(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.2)*.8,12.4)
t=ts(1.0); add(lp(rng.standard_normal(len(t)),.08)*np.exp(-t*5)*.5,12.4)
for m in (57,64,69,72,76):
    t=ts(2.6); add(np.sin(2*np.pi*nf(m)*t)*np.minimum(1,t/.05)*np.exp(-t*1.3)*.07,12.4)
# echo + master
d=int(.375*SR); L[d:]+=R[:-d]*.18; R[d:]+=L[:-d]*.18
mix=np.stack([L,R],1); fo=int(1.2*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix=np.tanh(mix/np.abs(mix).max()*1.6)/np.tanh(1.6)*.92
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((mix*32767).astype('<i2').tobytes())
