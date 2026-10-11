"""Assemble already verified deterministic clips; preserve supplied narration timing."""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np
EP=Path(__file__).resolve().parent.parent
CFG=json.loads((EP/'00_brief/effective_defaults.json').read_text(encoding='utf-8'))
DATA=json.loads((EP/'03_storyboard/cards.json').read_text(encoding='utf-8'))
FF=CFG['tools_local']['ffmpeg'];PROBE=str(Path(FF).with_name('ffprobe.exe'))
def run(args):return subprocess.check_output([str(x) for x in args],stderr=subprocess.STDOUT)
def save(path,x):(EP/path).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def probe(p):return json.loads(run([PROBE,'-v','error','-show_streams','-show_format','-of','json',p]))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 render=EP/'06_project/render';out=EP/'07_exports';out.mkdir(exist_ok=True)
 for c in DATA['cards']:
  clip=render/(c['id']+'.mp4');v=probe(clip)['streams'][0]
  assert int(v['nb_frames'])==c['frame_count'],c['id']
 (render/'concat.txt').write_text(''.join("file '"+c['id']+".mp4'\n" for c in DATA['cards']),encoding='utf-8')
 visual=render/'picture_master.mp4'
 run([FF,'-y','-v','error','-f','concat','-safe','0','-i',render/'concat.txt','-c','copy','-movflags','+faststart',visual])
 master=out/'ECHO_五款AI工具_增强信息卡_1080p.mp4';voice=EP/'00_brief/input/voice_original.mp3'
 run([FF,'-y','-v','error','-i',visual,'-i',voice,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',master])
 p=probe(master);vs=[x for x in p['streams'] if x['codec_type']=='video'];au=[x for x in p['streams'] if x['codec_type']=='audio']
 assert len(vs)==len(au)==1 and len(p['streams'])==2
 v=vs[0];a=au[0]
 assert (int(v['nb_frames']),v['width'],v['height'],v['avg_frame_rate'])==(2777,1920,1080,'30/1')
 assert a['channels']==2 and a['sample_rate']=='44100'
 assert abs(float(a['duration'])-92.551833)<.03
 run([FF,'-v','error','-i',master,'-f','null','-'])
 def pcm(f):return np.frombuffer(run([FF,'-v','error','-i',f,'-vn','-f','f32le','-ac','1','-ar','8000','pipe:1']),dtype='<f4').astype('float64')
 src=pcm(voice);dst=pcm(master);measure=[]
 for sec in [2,43,84]:
  start=sec*8000;end=start+5*8000;x=src[start:end];energy=np.dot(x,x)
  vals=[]
  for lag in range(-160,161):
   y=dst[start+lag:end+lag];vals.append(np.dot(x,y)/max(1e-15,np.sqrt(energy*np.dot(y,y))))
  lag=int(np.argmax(vals))-160;y=dst[start+lag:end+lag]
  measure.append(dict(start_seconds=sec,duration_seconds=5,best_lag_ms=lag/8,correlation=float(max(vals)),rms_ratio=float(np.sqrt(np.dot(y,y)/energy))))
 assert all(abs(x['best_lag_ms'])<=1 and x['correlation']>.98 and abs(x['rms_ratio']-1)<.025 for x in measure),measure
 source_samples=int(len(run([FF,'-v','error','-i',voice,'-f','s16le','-acodec','pcm_s16le','pipe:1']))/4)
 save('08_qc/master_qc.json',dict(passed=True,path=str(master.relative_to(EP)),sha256=sha(master),bytes=master.stat().st_size,video=v,audio=a,decode='passed',audio_source_sample_frames=source_samples,audio_windows=measure,voice_processing='AAC encoding only; no speed change, offset, gain, music or SFX',burned_narration_captions=False,subjective_full_speed_audiovisual_review='not_performed',limits='Machine checks and sampled visual inspection do not establish subjective full-playback readability or listening acceptance'))
 save('07_exports/master_probe.json',p)
 import shutil
 shutil.copy2(EP/'02_timing/subtitles_names_corrected.srt',out/'ECHO_原声对应_名称更正.srt')
 print(json.dumps({'master':str(master),'frames':2777,'seconds':float(p['format']['duration']),'audio_checks':measure},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
