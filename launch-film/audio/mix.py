# Builds the launch-film soundtrack: Cat Walk (drop on beat 12) + Mixkit SFX placed by measured peak.
import json,wave,subprocess,numpy as np
SR=48000;B=60/130;END=32*B;DROP_SONG=88.623;START=DROP_SONG-12*B
def load(p):
    w=wave.open(p);x=np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2).astype(np.float32)/32768;return x
subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',f'{START:.4f}','-t',f'{END+.05:.4f}','-i','catwalk.mp3','-ac','2','-ar',str(SR),'music.wav'],check=True)
n=int(END*SR);mix=np.zeros((n,2),np.float32)
m=load('music.wav')[:n];mix[:len(m)]+=m*.75
SFX={k:load(f'sfx/{k}.wav') for k in ['key1','key2','send','toss','impact','swoosh','click','success','whoosh','sparkle']}
SFX['key2']=SFX['key2'][:int(.12*SR)]
def peak(x):
    e=np.abs(x).mean(1);k=int(SR*.005);return np.convolve(e,np.ones(k)/k,'same').argmax()/SR
log=[]
def place(name,t,g):
    x=SFX[name];x=x/np.abs(x).max();s=int((t-peak(x))*SR)
    a=max(0,s);b=min(n,s+len(x))
    if b>a: mix[a:b]+=x[a-s:b-s]*g
    log.append((round(t,3),name,round(t-peak(x),3)))
keys=json.load(open('keys.json'));last=-1;i=0
for k in keys:
    if k-last>=.065:place('key1' if i%3 else 'key2',k,.16+.06*((i*7)%5)/4);last=k;i+=1
place('send',6*B,.55)
for bt,g in ((8,.4),(9,.4),(10,.4),(11,.4)):place('toss',bt*B,g)
for bt in (9,11):place('toss',bt*B+.12,.28)
place('impact',12*B,.85)
place('swoosh',14*B,.5)
place('click',19.6*B,.5)
place('success',19.6*B+.23,.45)
place('whoosh',21*B+.5,.5)
place('sparkle',29.05*B+.08,.5)
tail=int(.3*SR);mix[-tail:]*=np.linspace(1,0,tail)[:,None]
mix=np.clip(mix,-1,1)
with wave.open('premix.wav','wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((mix*32767).astype('<i2').tobytes())
json.dump(log,open('cue-sheet.json','w'),indent=0)
# two-pass loudnorm to -14 LUFS
r=subprocess.run(['ffmpeg','-hide_banner','-i','premix.wav','-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(r[r.rfind('{'):r.rfind('}')+1])
af=f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','premix.wav','-af',af,'-ar',str(SR),'soundtrack.wav'],check=True)
r=subprocess.run(['ffmpeg','-hide_banner','-i','soundtrack.wav','-af','loudnorm=I=-14:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(r[r.rfind('{'):r.rfind('}')+1]);print('final LUFS',j['input_i'],'TP',j['input_tp'])
print('cues',len(log))
