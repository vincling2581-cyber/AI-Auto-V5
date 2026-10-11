"""Collect final evidence, then package relative-path sources and validate ZIP bytes."""
from pathlib import Path
import json,hashlib,zipfile,platform,importlib.metadata,re
EP=Path(__file__).resolve().parent.parent
def read(p):return json.loads((EP/p).read_text(encoding='utf-8'))
def save(p,obj):(EP/p).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 data=read('03_storyboard/cards.json');master=read('08_qc/master_qc.json');protected=read('08_qc/protection/protected_sources_verification.json');edit=read('08_qc/edit_roundtrip/result.json');ind=read('08_qc/independent_review.json');semantic=read('03_storyboard/semantic_design.json')
 assert master['passed'] and protected['passed'] and edit['passed']
 clips=[];last=0
 for c in data['cards']:
  assert c['start_frame']==last;last=c['end_frame_exclusive']
  r=read('08_qc/cards/'+c['id']+'/render_check.json')
  assert r['deterministic'] and not r['text_overflow'] and r['decode']=='passed'
  assert r['frame_count']==c['frame_count'] and sha(EP/r['path'])==r['sha256']
  actual={e['event']:e['check_frames'] for e in r['source_sample_motion']}
  assert all(actual[e['id']]==e['check_frames'] for e in c['process_events'])
  clips.append(r)
 assert last==2777
 # A merged manifest avoids presenting only the last incremental render invocation.
 save('08_qc/cards/frame_manifest.json',dict(revision=data['revision'],fps=30,width=1920,height=1080,total_card_frames=2777,cards=clips))
 save('08_qc/environment.json',dict(python=platform.python_version(),platform=platform.platform(),packages={n:importlib.metadata.version(n) for n in ['playwright','Pillow','numpy']},ffmpeg=read('00_brief/effective_defaults.json')['tools_local']['ffmpeg'],fonts='Microsoft YaHei regular/bold from Windows; font binaries not redistributed'))
 report=dict(status='rendered_complete_for_user_review',master=master['path'],duration_seconds=2777/30,frame_count=2777,resolution=[1920,1080],fps=30,voice='original timing/content preserved; AAC transcode only',caption_mode='no burned narration captions; separate corrected-name SRT',cards=7,illustrations=9,scene_count=16,checks={'stream_decode_and_structure':'passed','audio_begin_middle_end_alignment':'passed; zero measured lag in three windows','deterministic_frame_seeking':'passed','text_bounds_sampled':'passed','encoded_motion_midpoint_neighbors':'inspected via samples and numerical deltas; not a standalone semantic pass','source_semantic_motion_review':ind['status'],'encoded_master_contact_sheet_review':'performed by root on three sheets','edit_and_local_rerender':'passed in isolated copy','protected_sources':'passed','source_package_integrity':'see source_package_report.json'},not_performed=['full-speed subjective viewing of the complete video','full-episode subjective listening','native AE or Jianying editor validation; these are not this source format'],review_focus=['VoiceStudio许可页较密，完整条件见附录','片尾2.07秒，主标题为优先阅读目标','原声数值与画面核查结果的有意差异'],official_assets='08_qc/asset_usage.json',fact_check='00_brief/事实核查与画面更正.md',editable_source='06_project/cards',generation_mode='builtin image_gen for nine raster scenes; local SVG source for cards',prompts=['04_assets/prompts','04_assets/illustrations/Axx.prompt.json'],v4_modified=False,prior_trials_modified=False,input_files_modified=False)
 save('08_qc/delivery_report.json',report)
 episode=read('00_brief/episode.json');episode['render_status']='rendered_complete_for_user_review';episode['delivery_report']='08_qc/delivery_report.json';save('00_brief/episode.json',episode)
 bundle=EP/'07_exports/ECHO_五款AI工具_可编辑源工程.zip'
 def include(p):
  rel=p.relative_to(EP).as_posix()
  if p.suffix=='.zip' or '__pycache__' in rel:return False
  if rel.startswith('08_qc/edit_roundtrip/workspace/'):return False
  if rel=='06_project/render/picture_master.mp4':return False
  if rel in ['08_qc/source_package_report.json','08_qc/source_package_manifest.json']:return False
  # Full raw frame evidence remains in the working episode; sheets and mappings are bundled.
  if re.search(r'08_qc/cards/[^/]+/(f\d+\.png|encoded/frame_\d+\.png)$',rel):return False
  if re.search(r'08_qc/master_frames/frame_\d+\.png$',rel):return False
  return True
 files=sorted(p for p in EP.rglob('*') if p.is_file() and include(p))
 manifest={p.relative_to(EP).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in files}
 save('08_qc/source_package_manifest.json',manifest)
 with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in files:z.write(p,p.relative_to(EP).as_posix())
  z.write(EP/'08_qc/source_package_manifest.json','08_qc/source_package_manifest.json')
 with zipfile.ZipFile(bundle) as z:
  assert z.testzip() is None
  assert all(not name.startswith('/') and '..' not in Path(name).parts for name in z.namelist())
  for name,expected in manifest.items():
   b=z.read(name);assert len(b)==expected['bytes'] and hashlib.sha256(b).hexdigest()==expected['sha256'],name
 receipt=dict(passed=True,files=len(manifest)+2,verification='Every payload entry SHA256 matched source_package_manifest.json and all ZIP CRCs passed before adding this receipt.',relative_paths=True,contains_master=True,contains_per_shot_clips=True,raw_frame_evidence='Full raw frames remain in the working episode; ZIP contains sheets, event mappings and reports',archive_hash='The external sibling source_package_report.json records the final archive SHA256.')
 with zipfile.ZipFile(bundle,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  z.writestr('08_qc/source_package_report.json',json.dumps(receipt,ensure_ascii=False,indent=2))
 with zipfile.ZipFile(bundle) as z:assert z.testzip() is None
 save('08_qc/source_package_report.json',dict(**{k:v for k,v in receipt.items() if k!='archive_hash'},path=str(bundle.relative_to(EP)),bytes=bundle.stat().st_size,sha256=sha(bundle),final_crc_test='passed including embedded receipt'))
 print(json.dumps({'master':master['path'],'package':str(bundle),'files':len(manifest)+2,'package_bytes':bundle.stat().st_size,'all_integrity_checks':'passed','subjective_full_speed_review':'pending user'},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
