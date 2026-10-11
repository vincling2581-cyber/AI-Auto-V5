"""Create this new episode from pinned standards and original input, all writes in V5."""
from pathlib import Path
import json,hashlib,shutil,re,math,subprocess
EP=Path(__file__).resolve().parents[1]
V4=Path('D:/AI-Auto-V4（Codex）')
INPUT=Path('D:/Downloads/Video/10月8日')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(rel,data):
    p=EP/rel;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def copy(src,rel):
    p=EP/rel;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        assert sha(p)==sha(src),f'Refusing to overwrite differing prepared input {p}'
    else:shutil.copy2(src,p)
for d in ['00_brief/input','01_audio','02_timing','03_storyboard','04_assets/illustrations','04_assets/official','04_assets/prompts','05_sample','06_project/cards','06_project/render','07_exports','08_qc']:(EP/d).mkdir(parents=True,exist_ok=True)
manifest=json.loads((V4/'production_standard.json').read_text(encoding='utf-8'))
for item in manifest['files']:
    source=V4/item['path'];assert sha(source)==item['sha256'],item['path']
    copy(source,Path('00_brief/standard_snapshot')/item['path'])
copy(V4/'production_standard.json','00_brief/standard_snapshot/production_standard.json')
copy(V4/'production_standard.json','00_brief/standard_lock.json')
copy(INPUT/'10月8日.mp3','00_brief/input/voice_original.mp3')
copy(INPUT/'10月8日.srt','00_brief/input/subtitles_original.srt')
cfg=json.loads((V4/manifest['defaults']).read_text(encoding='utf-8'))
cfg['brand']['episode_title']='五款AI工具，放进你的工作流'
cfg['brand']['series_label_template']='ECHO · AI新玩法'
cfg['delivery']['caption_mode']='no_burned_narration_captions'
cfg['audio']['bgm_default']='none_for_this_master'
cfg['audio']['sfx_default']='none_preserve_supplied_narration'
cfg['notes'].append('User authorized enhanced semantic card motion, original voice retention, corrected on-screen names/conditions and a fact-check appendix. All writes remain inside this V5 episode.')
save('00_brief/effective_defaults.json',cfg)
voice=EP/'00_brief/input/voice_original.mp3';ff=cfg['tools_local']['ffmpeg'];probe=str(Path(ff).with_name('ffprobe.exe'))
metadata=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-show_format','-of','json',str(voice)]))
duration=float(metadata['format']['duration']);frames=math.ceil(duration*30)
save('01_audio/source_probe.json',metadata)
save('00_brief/episode.json',{'project_name':EP.name,'standard_version':manifest['version'],'standard_status':manifest['status'],
 'topic':'五款AI工具与工作流：VoiceStudio / Paperclip / MemOS / Ollama + Open WebUI / Impeccable',
 'inputs':{'voice':{'original_path':str(INPUT/'10月8日.mp3'),'local':'00_brief/input/voice_original.mp3','sha256':sha(voice)},'srt':{'original_path':str(INPUT/'10月8日.srt'),'local':'00_brief/input/subtitles_original.srt','sha256':sha(EP/'00_brief/input/subtitles_original.srt')}},
 'duration_seconds':duration,'fps':30,'frame_count':frames,'subtitle_mode':'no_burned_narration_captions','bgm_mode':'none','sfx_mode':'none','project_format':'source_project','jianying_import_requested':False,
 'user_authorized_fact_handling':'保留原配音，画面更正名称、注明使用条件，并附核查说明',
 'card_motion_adoption':'Adapt semantic transport, masking, layer decomposition/reassembly, local corrections and result holds from the two V5 trials; new content and event times for this voice.',
 'per_episode_overrides':{'brand.episode_title':cfg['brand']['episode_title'],'brand.series_label_template':cfg['brand']['series_label_template'],'delivery.caption_mode':cfg['delivery']['caption_mode'],'audio.bgm_default':cfg['audio']['bgm_default'],'audio.sfx_default':cfg['audio']['sfx_default']},
 'render_status':'in_progress','scope':'new episode only; protect V4, V5 trial v1 and v2, original inputs'})
source=(EP/'00_brief/input/subtitles_original.srt').read_text(encoding='utf-8-sig')
def seconds(s):
    h,m,rest=s.split(':');return int(h)*3600+int(m)*60+float(rest.replace(',','.'))
items=[]
for block in re.split(r'\n\s*\n',source.strip()):
    lines=block.splitlines();a,b=lines[1].split(' --> ')
    items.append({'index':int(lines[0]),'start':seconds(a),'end':seconds(b),'text':' '.join(lines[2:])})
save('02_timing/subtitle_segments.json',items)
replacements={'Git Hub':'GitHub','voicestudio':'VoiceStudio','paper clip':'Paperclip','Memos':'MemOS','欧拉玛加openwebview':'Ollama 加 Open WebUI','impactable':'Impeccable','长兴':'涨星'}
normalized=source
for old,new in replacements.items():normalized=normalized.replace(old,new)
(EP/'02_timing/subtitles_names_corrected.srt').write_text(normalized,encoding='utf-8')
save('02_timing/subtitle_name_corrections.json',{'changes':replacements,'timings_preserved':True,'numerical_claims_not_silently_rewritten':True,'not_claimed_as_manually_listened_alignment':True})
method=V4/'production_standard/method_assets/reference_cards_v1'
for rel in ['card_kit.js','vendor/flubber.min.js','vendor/flubber-LICENSE']:
    copy(method/rel,Path('06_project/cards')/rel)
print(json.dumps({'episode':str(EP),'frames':frames,'duration':duration,'srt_segments':len(items),'standard_files_copied':len(manifest['files'])},ensure_ascii=False))
