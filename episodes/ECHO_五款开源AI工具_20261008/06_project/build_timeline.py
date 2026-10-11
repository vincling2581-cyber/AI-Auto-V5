from pathlib import Path
import json
EP=Path(__file__).resolve().parent.parent
def write(p,x): (EP/p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
rows=[
 ('A01',0,67,'工具太多，成本也多','', '', ''),
 ('A02',67,134,'把工具放进工作流','', '', ''),
 ('C00',134,288,'五款 AI 工具，五个工作入口','TOOLKIT / 01—05','开源与免费不等于无条件商用 · 软件、模型和服务许可分别核对',''),
 ('A03',288,354,'VoiceStudio','', '', '01 / VoiceStudio · 声音制作'),
 ('C01',354,708,'VoiceStudio：把录音变成声音工作流','01 / VOICE','流程示意与官方界面 · 仅使用获授权声音 · 商用需核对软件与模型许可',''),
 ('A04',708,788,'Paperclip','', '', '02 / Paperclip · 任务协作'),
 ('C02',788,1219,'Paperclip：让任务找到合适的 Agent','02 / ORCHESTRATION','流程示意 · 需配置 Agent 与模型服务，调用可能付费 · 周涨星未证实',''),
 ('A05',1219,1287,'MemOS','', '', '03 / MemOS · 长期记忆'),
 ('C03',1287,1850,'MemOS：让记忆进入下一次对话','03 / MEMORY','流程示意 · 节省幅度依任务与配置 · 项目方数据不等于通用保证',''),
 ('A06',1850,1926,'Ollama + Open WebUI','', '', '04 / Ollama + Open WebUI'),
 ('C04',1926,2223,'Ollama + Open WebUI：在本地协作','04 / LOCAL','需先下载本地模型 · WebUI 品牌条款、模型许可需分别核对',''),
 ('A07',2223,2294,'Impeccable','', '', '05 / Impeccable · 界面设计'),
 ('C05',2294,2580,'Impeccable：把设计判断交给工作流','05 / DESIGN','流程示意与官网案例 · 星标为 2026-10-08 核查快照 · 效果依工具与任务',''),
 ('A08',2580,2648,'减少重复劳动','', '', ''),
 ('A09',2648,2715,'交付真正的结果','', '', ''),
 ('C06',2715,2777,'ECHO · AI 新玩法','KEEP EXPLORING','项目链接、使用条件及原声数字说明见随片核查文档',''),
]
events={
 'C00':[(.1,1.23,'五种工具按用途进入'),(2.15,3.1,'五个入口按同一基线归位'),(3.55,4.2,'选择原则出现')],
 'C01':[(.3,1.9,'参考录音输入'),(1.3,2.3,'录音特征传递，保留录音'),(2.3,3,'到达后生成音色档案'),(3.1,3.9,'音色分配三类应用'),(4.9,6.7,'语言输出逐个建立'),(8.15,8.75,'官方配音界面与授权层级'),(10,10.6,'模型许可条件进一步标记')],
 'C02':[(.25,1.0,'建立任务入口'),(1.8,2.6,'按组织角色并行派发'),(4,4.8,'成员处理分支任务'),(6.2,7,'回传进度'),(8.4,9.2,'预算观察'),(10.6,11.4,'汇合结果'),(12.1,12.8,'官方界面结果')],
 'C03':[(.2,1.0,'当前对话结构化'),(2.2,3.0,'保存记忆对象'),(4.4,5.2,'新会话开始检索'),(6.6,7.4,'双路并行检索'),(8.8,9.6,'命中筛选'),(11,11.8,'取回记忆'),(13.2,14,'复用上下文'),(15.4,16.2,'开发者接入'),(17,17.7,'实际条件说明')],
 'C04':[(.2,1,'下载本地模型'),(2,2.8,'本地服务连接'),(4,4.8,'界面与推理协作'),(6,6.8,'切断外部网络内部继续'),(8,8.7,'平台模型管理')],
 'C05':[(.2,1,'展示待排版对象'),(1.6,2.6,'同一对象重排'),(3.6,4.4,'更正星标数字'),(5.2,6,'完善视觉层级'),(7.2,8,'展示官网案例')],
 'C06':[(0,.65,'收束工具用途与关注入口')]
}
events.update(json.loads((EP/'03_storyboard/events_override.json').read_text(encoding='utf-8')))
cards=[]
for sid,start,end,title,kicker,footer,label in rows:
 es=[]
 for i,(a,b,meaning) in enumerate(events.get(sid,[(0,(end-start)/30,'人物动作关键姿势；镜头停留不超过2.8秒')])):
  fs=[min(end-start-1,round((a+(b-a)*p)*30)) for p in [.2,.5,.8]]
  es.append(dict(id=f'{sid}_E{i+1:02}',start_seconds=a,end_seconds=b,check_frames=fs,meaning=meaning))
 cards.append(dict(id=sid,title=title,kicker=kicker,footer=footer,label=label,start_frame=start,end_frame_exclusive=end,frame_count=end-start,overview_frames=[0,round((end-start-1)*.5),end-start-1],process_events=es))
preload=['illustrations/A%02d.png'%i for i in range(1,10)]+['official/'+x for x in ['voice_clone.webp','voice_dub.webp','paperclip_home.png','webui_demo.png','ollama_logo.png','impeccable_case.png','impeccable_home.png']]
write('03_storyboard/cards.json',dict(revision='new_episode_enhanced_cards_v1',fps=30,width=1920,height=1080,total_frames=2777,duration_seconds=2777/30,preload=preload,cards=cards))
write('03_storyboard/shot_plan.json',dict(audio_unchanged=True,no_burned_narration_captions=True,illustration_keypose_pairs=[['A01','A02'],['A08','A09']],cards=cards))
write('00_brief/local_visual_overrides.json',dict(scope='this episode only',sources='active v4.5 snapshot and user instruction',overrides=[{'field':'layout.footer','value':'y1018, 30px','reason':'条件与出处附注占用独立页脚，主内容保留安全区'},{'field':'illustration.native_dimensions','value':[1672,941],'reason':'内置图像工具原生返回，按比例cover到1920x1080，不拉伸'},{'field':'branding','value':'ECHO AI新玩法','reason':'新一集工具题材，保留系列角色画风与卡片规范'},{'field':'audio','value':'原配音无变速无增益无BGM/SFX','reason':'用户选择保留原配音'}]))
print('timeline',len(cards),'shots',sum(c['frame_count'] for c in cards),'frames')
