# Generates a simple, original upbeat corporate background loop (no samples).
import numpy as np, wave, sys
SR=44100; DUR=float(sys.argv[2]) if len(sys.argv)>2 else 33.1; BPM=100
beat=60/BPM; n=int(SR*DUR); L=np.zeros(n); Rr=np.zeros(n)
def note(m): return 440*2**((m-69)/12)
def add(sig,t0,pan=0.0,gain=1.0):
    i=int(t0*SR); j=min(n,i+len(sig))
    if i>=n: return
    L[i:j]+=sig[:j-i]*gain*(1-pan)/1; Rr[i:j]+=sig[:j-i]*gain*(1+pan)/1
def env(len_s,a=.01,d=.3,s=.0,r=.1):
    t=np.arange(int(len_s*SR))/SR; e=np.minimum(1,t/a)*np.exp(-t/d)*(1-s)+s*np.minimum(1,t/a)
    rel=int(r*SR); e[-rel:]*=np.linspace(1,0,rel); return t,e
prog=[[48,52,55,59],[43,50,55,59],[45,52,57,60],[41,48,53,57]]  # Cmaj7 G Am F
bar=beat*4
for b in range(int(DUR/bar)+1):
    ch=prog[b%4]; t0=b*bar
    # pad
    t,e=env(bar+.4,a=.6,d=99,s=1,r=.5)
    pad=sum(np.sin(2*np.pi*note(m+12)*t)*.5+np.sin(2*np.pi*note(m+12)*1.003*t)*.5 for m in ch)/len(ch)
    add(pad*e*.10,t0)
    # bass on each beat
    for k in range(4):
        t,e=env(beat*.9,a=.005,d=.25,r=.05); add(np.sin(2*np.pi*note(ch[0]-12)*t)*e*.30,t0+k*beat)
    # pluck arpeggio 8ths
    arp=[ch[0]+24,ch[1]+24,ch[2]+24,ch[3]+24,ch[2]+24,ch[1]+24,ch[2]+24,ch[3]+24]
    for k,m in enumerate(arp):
        t,e=env(.45,a=.002,d=.12,r=.05); f=note(m)
        add((np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t))*e*.09,t0+k*beat/2,pan=(.35 if k%2 else -.35))
    # drums
    for k in range(4):
        tt=t0+k*beat
        if k in (0,2):
            t=np.arange(int(.25*SR))/SR; f=110*np.exp(-t*18)+45; ph=2*np.pi*np.cumsum(f)/SR
            add(np.sin(ph)*np.exp(-t*14)*.55,tt)
        if k in (1,3):
            t=np.arange(int(.18*SR))/SR; nz=np.random.default_rng(b*8+k).standard_normal(len(t))
            add(nz*np.exp(-t*22)*.10,tt)
        t=np.arange(int(.05*SR))/SR; hz=np.random.default_rng(1000+b*8+k).standard_normal(len(t)); hz=np.diff(hz,prepend=0)
        add(hz*np.exp(-t*80)*.05,tt+beat/2,pan=.2)
# simple stereo echo
d=int(beat*.75*SR)
L[d:]+=Rr[:-d]*.22; Rr[d:]+=L[:-d]*.22
mix=np.stack([L,Rr],1)
# fades
fi=int(1.0*SR); fo=int(2.5*SR)
mix[:fi]*=np.linspace(0,1,fi)[:,None]; mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix/=np.abs(mix).max()*1.12
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((mix*32767).astype('<i2').tobytes())
