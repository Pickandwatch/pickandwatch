import sys,time
from faster_whisper import WhisperModel
src,out,model=sys.argv[1],sys.argv[2],sys.argv[3]
t=time.time()
m=WhisperModel(model,device='cpu',compute_type='int8',cpu_threads=2)
import subprocess,numpy as np
raw=subprocess.run(['ffmpeg','-v','error','-i',src,'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True,check=True).stdout
audio=np.frombuffer(raw,np.int16).astype(np.float32)/32768
segs,info=m.transcribe(audio,language='fr',beam_size=1,vad_filter=True)
with open(out,'w') as f:
    for s in segs:
        mm,ss=divmod(int(s.start),60)
        f.write(f'[{mm:02d}:{ss:02d}] {s.text.strip()}\n'); f.flush()
print('done',round(time.time()-t),'s',file=open(out+'.done','w'))
