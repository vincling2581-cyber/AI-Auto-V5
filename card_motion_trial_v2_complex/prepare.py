"""Prepare an isolated new visual trial from the active method, not old episode content."""
from pathlib import Path
import json, shutil, hashlib

ROOT=Path(__file__).resolve().parent
SOURCE=Path('D:/AI-Auto-V4（Codex）')
V1=ROOT.parent/'card_motion_trial_v1'
def write(path,data):
    dest=ROOT/path;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def copy(src,dest):
    out=ROOT/dest;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)

manifest=json.loads((SOURCE/'production_standard.json').read_text(encoding='utf-8'))
copy(SOURCE/'production_standard.json','00_brief/standard_lock.json')
for key in ('sop','prompts','defaults','rules'):
    rel=manifest[key]
    copy(SOURCE/rel,Path('00_brief/standard_snapshot')/rel)
cfg=json.loads((SOURCE/manifest['defaults']).read_text(encoding='utf-8'))
cfg['brand']['episode_title']='复杂信息卡视觉试验：工程结构恢复'
cfg['video']['duration_basis']='visual_trial_timing_pending_supplied_voice'
cfg['notes'].append('Only this isolated visual trial: 18 seconds, no narration supplied; not final voice-aligned production.')
write('00_brief/effective_defaults.json',cfg)
for name in ('card_kit.js','vendor/flubber.min.js','vendor/flubber-LICENSE'):
    copy(SOURCE/'production_standard/method_assets/reference_cards_v1'/name,Path('06_project/cards')/name)
for name in ('render_cards.py','card_scene.html'):
    copy(V1/'episode/06_project/cards'/name,Path('06_project/cards')/name)
html=ROOT/'06_project/cards/card_scene.html'
html.write_text(html.read_text(encoding='utf-8').replace('Compositor · 本集信息卡','复杂信息卡 · 视觉试样'),encoding='utf-8')

specs=[
 ('import',12,72,'导入工程','保留来源文件；文件副本沿路径进入编辑区并展开为海报'),
 ('split',78,144,'识别图层、文字和对象位置','同一海报拆成背景、标题和标签，分层过程中内容身份与层级保留'),
 ('inspect',150,192,'识别图层、文字和对象位置','从三个图层提取关系线，结构检查逐项建立，标题局部问题被定位'),
 ('focus',192,222,'如果缺少字体','展开与标题层连接的局部修复区，其他图层保持原位'),
 ('repair',228,312,'保留对象关系，完成替换','替代字体条目沿路径送回同一标题层，到达后字形变清晰，字号与锚点保持'),
 ('rebuild',330,402,'恢复原有结构','已修复标题与原背景、标签沿分解路线逆向重组，右侧图层列表仍保留'),
 ('edit',414,474,'继续编辑','选中标签，以光标拖动到新位置并吸附；背景和标题不移动，保持新终态'),
]
events=[]
for name,a,b,voice,meaning in specs:
    events.append({'id':name,'target_ids':['poster','background','title','tag'],'meaning':meaning,
      'start_frame':a,'end_frame_exclusive':b,'global_start_frame':a,'global_end_frame_exclusive':b,
      'check_frames':[round(a+(b-a)*p) for p in (.2,.5,.8)],'voice_anchor':voice,
      'easing':'smoothstep for transport; cubic_out for local reveals; no overshoot',
      'retained':'源文件、对象身份、层级和已完成结果保留；字体替换和最终标签位置为明确的状态改变',
      'occlusion':'图片受背景画布遮罩；局部修复区在右侧纸白框内；图层按背景、标题、标签依次覆盖'})
card={'id':'C01','title':'复杂工程，也能清晰恢复','start_frame':0,'end_frame_exclusive':540,
 'frame_count':540,'source_span':'导入工程时，先识别图层、文字和对象位置。如果缺少字体，保留对象关系，定位冲突并完成替换。处理后恢复原有结构，继续编辑。',
 'viewer_question':'文件有多种对象和局部问题时，怎样保留结构并继续编辑？',
 'core_claim':'以虚构海报演示结构识别、局部修复和可编辑性，不构成任何真实软件的功能承诺。',
 'relation_type':'结构拆解—局部修复—关系恢复',
 'overview_frames':[44,138,209,299,391,520],
 'reading_hold':{'start_frame':474,'end_frame_exclusive':540},'process_events':events}
write('03_storyboard/cards.json',{'schema':'episode_cards_v1','revision':'complex_motion_trial_v2',
 'fps':30,'width':1920,'height':1080,'total_video_frames':540,'subtitle_mode':'none','cards':[card]})
write('00_brief/trial_scope.json',{'visual_trial':True,'narration_provided':False,'timing_requires_voice_alignment_for_production':True,
 'source_standard':manifest['version'],'protect':['V4 entire tree','V5 card_motion_trial_v1'],
 'allowed_changes':'V5/card_motion_trial_v2_complex only; new card content, layout and semantic motion',
 'flow':'existing deterministic SVG > Chrome frames > FFmpeg; no AE or new animation framework',
 'episode_overrides':{'brand.episode_title':cfg['brand']['episode_title'],'video.duration_basis':cfg['video']['duration_basis']}})
(ROOT/'00_brief/narration.txt').write_text(card['source_span'],encoding='utf-8')
print('Prepared independent v2 complex trial, active standard '+manifest['version'])
