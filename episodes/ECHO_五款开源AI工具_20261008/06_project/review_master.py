from pathlib import Path
import json,subprocess,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
EP=Path(__file__).resolve().parent.parent
CFG=json.loads((EP/'00_brief/effective_defaults.json').read_text(encoding='utf-8'))
DATA=json.loads((EP/'03_storyboard/cards.json').read_text(encoding='utf-8'))
FF=CFG['tools_local']['ffmpeg'];master=EP/'07_exports/ECHO_五款AI工具_增强信息卡_1080p.mp4'
q=EP/'08_qc/master_frames';q.mkdir(parents=True,exist_ok=True)
frames=sorted(set([(c['start_frame']+c['end_frame_exclusive'])//2 for c in DATA['cards']]+[0,287,630,1155,1485,1770,2100,2430,2510,2776]))
expr='select='+ '+'.join('eq(n\\,'+str(f)+')' for f in frames)
subprocess.run([FF,'-y','-v','error','-i',str(master),'-vf',expr,'-fps_mode','vfr',str(q/'frame_%04d.png')],check=True)
mapping={str(f):f'frame_{i+1:04d}.png' for i,f in enumerate(frames)}
(q/'mapping.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8')
font=ImageFont.truetype(CFG['type']['regular_font'],22)
for page in range((len(frames)+11)//12):
 fs=frames[page*12:page*12+12];im=Image.new('RGB',(1568,50+((len(fs)+2)//3)*328),'#E7ECE5');d=ImageDraw.Draw(im);d.text((18,10),'ECHO · 最终编码抽帧 / '+str(page+1),font=font,fill='#153724')
 for i,f in enumerate(fs):
  p=Image.open(q/mapping[str(f)]).convert('RGB');p.thumbnail((512,288));x=10+i%3*520;y=48+i//3*328;im.paste(p,(x,y));shot=next(c['id'] for c in DATA['cards'] if c['start_frame']<=f<c['end_frame_exclusive']);d.text((x+5,y+292),f'{shot} · {f/30:.2f}s · frame {f}',font=font,fill='#153724')
 im.save(EP/f'07_exports/全片画面概览_{page+1}.jpg',quality=93)
shutil.copy2(q/mapping['287'],EP/'07_exports/封面.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pics=[dict(file=str(p.relative_to(EP)),sha256=sha(p),width=Image.open(p).width,height=Image.open(p).height) for p in sorted((EP/'04_assets/illustrations').glob('A??.png'))]
assert len(pics)==9 and len({x['sha256'] for x in pics})==9
events=[]
for c in DATA['cards']:
 if c['id'].startswith('A'):
  gap=c['frame_count']/30
 else:
  spans=sorted([(0,0)]+[(e['start_seconds'],e['end_seconds']) for e in c['process_events']]+[(c['frame_count']/30,c['frame_count']/30)])
  end=0;gaps=[]
  for a,b in spans:gaps.append(max(0,a-end));end=max(end,b)
  gap=max(gaps)
 assert gap<=2.8,(c['id'],gap)
 events.append(dict(id=c['id'],max_declared_semantic_hold_seconds=gap,basis='Source event plan plus sampled inspection; pixel deltas alone not semantic proof'))
asset_usage={
 'voice_clone.webp':{'shots':['C01'],'role':'官方声音克隆界面'},'voice_dub.webp':{'shots':['C01'],'role':'官方配音界面'},'paperclip_home.png':{'shots':['C02'],'role':'官方界面；预算和审批局部放大'},'webui_demo.png':{'shots':['C04'],'role':'含外部API的官方界面示例，非本地离线实测'},'impeccable_case.png':{'shots':['C05'],'role':'官方Neo Mirai案例网页截图'},'memos_architecture.png':{'shots':[],'role':'未使用；实际为官方概念插画拼图，不是架构图'},'paperclip_tour.webm':{'shots':[],'role':'调研下载，未使用'},'voice_tour.gif':{'shots':[],'role':'调研下载，未使用；避免墙钟GIF破坏确定性'},'ollama_logo.png':{'shots':[],'role':'调研下载，未使用'},'impeccable_home.png':{'shots':[],'role':'调研截图，预载但未出现在成片'}}
(EP/'08_qc/asset_usage.json').write_text(json.dumps(asset_usage,ensure_ascii=False,indent=2),encoding='utf-8')
(EP/'08_qc/visual_structure.json').write_text(json.dumps(dict(illustrations=pics,unique_illustrations=9,duplicate_sha256=0,keypose_action_pairs=[['A01','A02'],['A08','A09']],hold_checks=events,full_frame_natural_lower_edge='sampled_images_reviewed',eyes_and_arm_connections='sampled_images_reviewed_by_generation_agents_and_root',encoded_master_frames=frames,limits='Contact sheets are not full-speed subjective audiovisual review'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Master frame sheets, 9 unique artwork hashes, declared hold bounds and asset usage saved',flush=True)
