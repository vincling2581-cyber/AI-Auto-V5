from pathlib import Path
import argparse,json,hashlib,subprocess,sys,datetime,zipfile,platform,re
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
import clip_provenance as provenance
LOADED_SOURCE_SHA256=provenance.file_record(Path(__file__))['sha256']
sys.stdout.reconfigure(encoding='utf-8')
E=Path(__file__).resolve().parents[1];CFG=json.loads((E/'00_brief/effective_defaults.json').read_text(encoding='utf-8'));DATA=json.loads((E/'03_storyboard/cards.json').read_text(encoding='utf-8'));FF=CFG['tools_local']['ffmpeg'];FP=str(Path(FF).with_name('ffprobe.exe'));QC=E/'08_qc';OUT=E/'07_exports';MASTER=OUT/'AI逆向Skill_1080p_无口播字幕.mp4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def call(args):return subprocess.check_output(args,stderr=subprocess.STDOUT)
def dependencies():
 roots=['00_brief/input','00_brief/standard_snapshot','01_script','03_storyboard','04_assets','06_project/cards']
 files=[]
 for root in roots:
  files.extend(p for p in (E/root).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 files.extend([E/'00_brief/effective_defaults.json',E/'00_brief/episode.json',E/'00_brief/standard_lock.json'])
 files.extend(p for p in (E/'06_project').glob('*.py'))
 for root in ['02_research/official','02_research/screenshots']:
  if (E/root).exists():files.extend(p for p in (E/root).rglob('*') if p.is_file())
 import importlib.metadata as md
 dep={'files':[{'path':p.relative_to(E).as_posix(),'sha256':sha(p)} for p in sorted(set(files))],'fonts':[{'path':CFG['type'][x],'sha256':sha(Path(CFG['type'][x]))} for x in ['regular_font','bold_font']],'tools':{'python':platform.python_version(),'ffmpeg':call([FF,'-version']).decode().splitlines()[0],'packages':{x:md.version(x) for x in ['playwright','Pillow','numpy','opencv-python']}},'parameters':CFG}
 if (QC/'preview_smoke.json').exists():dep['tools']['chrome']=json.loads((QC/'preview_smoke.json').read_text(encoding='utf-8'))['chrome_version']
 write(QC/'dependencies.json',dep);return sha(QC/'dependencies.json')
def assemble():
 provenance.require_loaded_source(Path(__file__),LOADED_SOURCE_SHA256)
 inputs=provenance.assembly_inputs(E,DATA['cards'],expected_config=CFG,expected_data=DATA)
 clips=E/'06_project/render';concat=clips/'concat.txt';concat.write_text('\n'.join("file '"+c['id']+".mp4'" for c in DATA['cards']),encoding='utf-8')
 assert all((clips/(c['id']+'.mp4')).exists() for c in DATA['cards'])
 call([FF,'-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-i',str(E/'00_brief/input/voice_original.mp3'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a',CFG['video']['audio_codec'],'-b:a',CFG['video']['audio_bitrate'],'-movflags','+faststart',str(MASTER)])
 provenance.require_loaded_source(Path(__file__),LOADED_SOURCE_SHA256)
 provenance.record_master(E,DATA['cards'],MASTER,inputs,expected_config=CFG,expected_data=DATA)
 print('Assembled:',MASTER.name,MASTER.stat().st_size,flush=True)
def pcm(p):return np.frombuffer(call([FF,'-v','error','-i',str(p),'-vn','-ac','1','-ar','44100','-f','f32le','pipe:1']),dtype=np.float32)
def qc():
 provenance.require_loaded_source(Path(__file__),LOADED_SOURCE_SHA256)
 assembly=provenance.validate_master(E,DATA['cards'],MASTER,expected_config=CFG,expected_data=DATA)
 dep=dependencies();meta=json.loads(call([FP,'-v','error','-show_streams','-show_format','-of','json',str(MASTER)]));v=next(x for x in meta['streams'] if x['codec_type']=='video');a=next(x for x in meta['streams'] if x['codec_type']=='audio');assert int(v['nb_frames'])==2496 and v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='30/1' and v['pix_fmt']=='yuv420p'
 decode=subprocess.run([FF,'-v','error','-i',str(MASTER),'-f','null','-'],capture_output=True);assert decode.returncode==0 and not decode.stderr,decode.stderr.decode(errors='replace')
 src=pcm(E/'00_brief/input/voice_original.mp3');dst=pcm(MASTER);anchors=[]
 for t in [1,40,77]:
  idx=int(t*44100);x=src[idx:idx+44100];y=dst[idx:idx+44100];gain=float(np.dot(x,y)/max(np.dot(x,x),1e-20));cor=float(np.corrcoef(x,y)[0,1]);assert cor>.99,(t,cor);anchors.append({'seconds':t,'correlation':cor,'gain_ratio':gain,'gain_db':float(20*np.log10(gain))})
 audio={'source_samples':len(src),'encoded_decoded_samples':len(dst),'sample_rate':44100,'source_peak_dbfs':float(20*np.log10(max(abs(src).max(),1e-20))),'output_peak_dbfs':float(20*np.log10(max(abs(dst).max(),1e-20))),'source_output_windows':anchors,'processing':'no volume filter, no speed change, no trim; AAC reencode only','full_listen':'not_performed'}
 measured=subprocess.run([FF,'-hide_banner','-i',str(MASTER),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True);(QC/'audio_loudness.log').write_bytes(measured.stderr)
 cap=subprocess.Popen([FF,'-v','error','-i',str(MASTER),'-an','-vf','scale=320:180','-f','rawvideo','-pix_fmt','bgr24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);art=[c for c in DATA['cards'] if c['type']=='animation'];refs={c['id']:cv2.resize(cv2.imdecode(np.fromfile(QC/'cards'/c['id']/'f0000.png',dtype=np.uint8),cv2.IMREAD_COLOR),(320,180)) for c in art};mask=np.ones((180,320),bool);mask[:55,128:]=False;mask[18:38,14:73]=False;mask[106:136,28:77]=False;mask[106:136,243:291]=False
 groups={}
 for c in art:groups.setdefault(c['group'],[]).append(c)
 frame=0;identified=[];black=[];thumbs=[];comparison=[]
 while True:
  chunk=cap.stdout.read(320*180*3)
  if not chunk:break
  assert len(chunk)==320*180*3
  small=np.frombuffer(chunk,dtype=np.uint8).reshape((180,320,3));gray=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
  if float(gray.std())<1.5:black.append(frame)
  c=next(c for c in DATA['cards'] if c['start_frame']<=frame<c['end_frame_exclusive'])
  if c['type']=='animation':
   scores={x['id']:float(np.abs(small.astype(np.float32)-refs[x['id']].astype(np.float32))[mask].mean()) for x in groups[c['group']]};best=min(scores,key=scores.get);identified.append((frame,best));assert best==c['id'],(frame,best,c['id']);
   if frame==c['start_frame']:comparison.append({'frame':frame,'expected':c['id'],'matched':best,'distance':scores[best]})
  if frame%15==0:thumbs.append((frame,Image.fromarray(cv2.cvtColor(small,cv2.COLOR_BGR2RGB))))
  frame+=1
 assert cap.wait()==0,cap.stderr.read().decode(errors='replace');assert frame==2496 and not black
 runs=[]
 for f,sid in identified:
  if runs and runs[-1]['state_id']==sid and runs[-1]['end_frame_exclusive']==f:runs[-1]['end_frame_exclusive']=f+1
  else:runs.append({'state_id':sid,'start_frame':f,'end_frame_exclusive':f+1})
 for r in runs:r['seconds']=(r['end_frame_exclusive']-r['start_frame'])/30
 assert max(r['seconds'] for r in runs)<=3
 font=ImageFont.truetype(CFG['type']['regular_font'],18)
 for page,start in enumerate(range(0,len(thumbs),36),1):
  batch=thumbs[start:start+36];sheet=Image.new('RGB',(1320,((len(batch)+3)//4)*216),'#e7ece5');d=ImageDraw.Draw(sheet)
  for i,(f,im) in enumerate(batch):x=10+i%4*328;y=i//4*216;sheet.paste(im,(x,y));d.text((x,y+182),f'{f/30:05.2f}s · f{f}',font=font,fill='#10281a')
  sheet.save(QC/f'final_contact_{page:02}.jpg',quality=90)
 usage=[{'id':c['id'],'path':'04_assets/'+c['art'],'sha256':sha(E/'04_assets'/c['art']),'start_frame':c['start_frame'],'end_frame_exclusive':c['end_frame_exclusive']} for c in art];assert len({x['sha256'] for x in usage})==len(usage);write(E/'03_storyboard/asset_usage.json',usage)
 # Asset usage is part of the locked dependencies and is finalized before recording their fingerprint.
 dep=dependencies()
 provenance.require_loaded_source(Path(__file__),LOADED_SOURCE_SHA256)
 final_assembly=provenance.validate_master(E,DATA['cards'],MASTER,expected_config=CFG,expected_data=DATA)
 if final_assembly!=assembly:raise provenance.ProvenanceError('检查期间成片或来源发生变化')
 report={'status':'passed','scope':'machine checks only','dependencies_manifest':'08_qc/dependencies.json','dependencies_sha256':dep,'artifact_sha256':sha(MASTER),'video':v,'audio_stream':a,'audio':audio,'decode':'passed','decoded_frames':frame,'uniform_frames':black,'animation_export_state_runs':runs,'animation_state_match':'all encoded animation frames compared against actual source frames; top-right graphic overlay regions excluded','boundary_matches':comparison,'max_animation_state_seconds':max(r['seconds'] for r in runs),'unique_illustrations':len(usage),'duplicate_sha256':0,'source_sample_and_encoded_process_checks':'08_qc/cards/frame_manifest.json','full_speed_subjective_av':'not_performed','jianying_native':'not_requested'}
 report['assembly_provenance']='08_qc/assembly_provenance.json';report['assembly_provenance_sha256']=sha(QC/'assembly_provenance.json');report['assembly_input_fingerprint']=assembly['input_fingerprint']
 write(QC/'machine_report.json',report);print(json.dumps({'machine':'passed','frames':frame,'max_state':report['max_animation_state_seconds'],'audio_correlations':[x['correlation'] for x in anchors]},ensure_ascii=False),flush=True)
def pack():
 dest=OUT/'AI逆向Skill_可重渲源工程.zip';files=[]
 for p in E.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(E)
  if rel.parts[0]=='07_exports' or '__pycache__' in rel.parts or 'edit_test' in rel.parts or rel.name in ['delivery_manifest.json','package_report.json']:continue
  if rel.parts[0]=='08_qc' and ('cards' in rel.parts and p.suffix=='.png' and p.name not in ['overview.png','process.png','contact.png']):continue
  if p.suffix in ['.log','.html'] and rel.parts[0]=='02_research' and 'reference' in rel.parts:continue
  files.append(p)
 manifest={'files':[{'path':p.relative_to(E).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)]};write(E/'delivery_manifest.json',manifest);files.append(E/'delivery_manifest.json')
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in sorted(files):z.write(p,p.relative_to(E).as_posix())
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  bad=[x['path'] for x in manifest['files'] if hashlib.sha256(z.read(x['path'])).hexdigest()!=x['sha256']];assert not bad,bad
 write(QC/'package_report.json',{'status':'passed','zip':dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size,'files':len(files),'crc':'passed','embedded_manifest_sha256':'passed','manifest_sha256':sha(E/'delivery_manifest.json')});print('Package:',dest.name,dest.stat().st_size,flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--assemble',action='store_true');ap.add_argument('--qc',action='store_true');ap.add_argument('--pack',action='store_true');args=ap.parse_args()
 if args.assemble:assemble()
 if args.qc:qc()
 if args.pack:pack()
