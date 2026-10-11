"""Deliver the verified silent visual trial without another encode."""
from pathlib import Path
import hashlib, json, shutil, subprocess

ROOT=Path(__file__).resolve().parent
cfg=json.loads((ROOT/'00_brief/effective_defaults.json').read_text(encoding='utf-8'))
check=json.loads((ROOT/'08_qc/cards/C01/render_check.json').read_text(encoding='utf-8'))
source=ROOT/'06_project/render/C01.mp4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==check['sha256'],'Render evidence does not match the video'
out=ROOT/'07_exports';out.mkdir(exist_ok=True)
dest=out/'complex_card_1080p.mp4';shutil.copy2(source,dest)
assert sha(source)==sha(dest)
probe=str(Path(cfg['tools_local']['ffmpeg']).with_name('ffprobe.exe'))
media=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-show_format','-of','json',str(dest)]))
streams=media['streams'];video=streams[0]
assert len(streams)==1 and video['codec_type']=='video'
assert (video['width'],video['height'],int(video['nb_frames']))==(1920,1080,540)
assert video['r_frame_rate']=='30/1' and abs(float(video['duration'])-18)<.001
report={'status':'passed','scope':'silent visual review trial, not final narration-aligned master',
 'file':str(dest.relative_to(ROOT)),'sha256':sha(dest),'width':1920,'height':1080,'fps':30,'frames':540,
 'duration_seconds':18,'audio_stream_count':0,'extra_encode':False,
 'render_evidence':'08_qc/cards/C01/render_check.json','semantic_evidence':'08_qc/semantic_check.json',
 'subjective_normal_speed_review':'pending_user_review'}
(out/'delivery_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
