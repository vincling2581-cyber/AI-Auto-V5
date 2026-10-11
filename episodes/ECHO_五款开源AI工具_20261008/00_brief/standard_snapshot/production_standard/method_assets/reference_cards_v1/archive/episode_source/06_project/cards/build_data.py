"""Compile this episode's information structure and explicit motion events."""
import hashlib,json
from pathlib import Path
EP=Path(__file__).resolve().parents[2]
SPECS=[
 ('C02',3,8.933,'两种交代方式',
  '你缺的可能不是Prompt 而是Skill。先记住一句话：Prompt是临时交代 Skill是长期工作手册。',
  'Prompt和Skill在这段类比中怎样使用？','临时交代面向本次任务；保存的工作手册可供后续任务调用。','统一维度对照',
  ['Prompt','本次任务','Skill','方法存档','任务 A','任务 B'],[['Prompt','本次任务','单次递交'],['Skill','任务 A','调用'],['Skill','任务 B','再次调用']],
  '两栏同尺度比较；左侧便签递交，右侧手册保留并分出两次调用。任务A/B是教学示例，不是产品记录。',
  '用留存和流向区分临时交代与可复用手册，而不是重复两句定义。',
  [(0.35,1.4,'便签','左侧待交代便签','进入本次任务','移动','临时交代'),(1.4,2.15,'手册','未存档纸页','进入存档文件夹','对象迁移','长期工作手册'),(2.4,3.15,'调用A','手册保留','内容副本沿关系线到任务A','路径迁移','长期工作手册'),(3.7,4.45,'调用B','同一手册保留','另一副本到任务B','路径迁移','长期工作手册')],4.8,[.1,.85,1.8,2.7,4.1,5.5]),
 ('C04',12.733,18.366,'把写作方法变成流程',
  '先找痛点 再设计冲突 然后写开头 补案例 最后加上评论区互动 他照做 确实写出来了。',
  '五个动作怎样组织成一篇稿？','五项写作动作按口播顺序推进并累积到同一成稿。','顺序与输入输出',
  ['痛点','冲突','开头','案例','互动','成稿'],[['痛点','冲突','顺序'],['冲突','开头','顺序'],['开头','案例','顺序'],['案例','互动','顺序'],['互动','成稿','流程结果']],
  '上方五节点的连线和移动对象表达顺序，下方同一稿件逐项增添内容；不表示经实测的因果增益。',
  '让观众看见五个步骤如何推进、如何累积成一份完整文案。',
  [(0.35,1,'步骤1→2','痛点节点','连接到冲突','路径生长与对象迁移','先找痛点 再设计冲突'),(1.08,1.63,'步骤2→3','冲突节点','连接到开头','路径迁移','然后写开头'),(1.81,2.36,'步骤3→4','开头节点','连接到案例','路径迁移','补案例'),(2.54,3.09,'步骤4→5','案例节点','连接到互动','路径迁移','最后加上评论区互动'),(3.9,4.55,'成稿','流程已建立','内容沿路径进入成稿','对象迁移','他照做 确实写出来了')],4.65,[.1,.72,1.92,3.08,4.22,5.2]),
 ('C07',26.7,32.133,'一份手册，四个维度',
  '什么任务使用它 具体分几步 哪些地方要注意 什么样的结果才算合格 以后你只要说。',
  '工作手册应回答哪几类问题？','使用条件、执行步骤、注意事项和合格结果是同一手册的四个并列维度。','并列维度汇聚',
  ['使用条件','执行步骤','注意事项','合格结果','工作手册'],[[x,'工作手册','并列字段汇入'] for x in ['使用条件','执行步骤','注意事项','合格结果']],
  '四项同级排列、互不连接，每项独立汇入手册对应行；先后显现只用于跟随讲解，不表示因果链。',
  '把四种提问归类为手册结构，并保留每项与成册字段的对应。',
  [(s+.4,s+1.05,k,k+'问题','手册中对应字段','对象沿独立路径迁移',a) for k,s,a in [('使用条件',.1,'什么任务使用它'),('执行步骤',.83,'具体分几步'),('注意事项',1.63,'哪些地方要注意'),('合格结果',2.8,'什么样的结果才算合格')]],4.15,[.1,.75,1.68,2.45,3.53,5]),
 ('C09',38.5,48,'把方法整理成可执行文件',
  '所以 Skill不是一句提示词 也不是让AI“认真一点” 它是把一项工作里的流程 判断标准 工具用法和验收要求 整理成AI可以重复执行的文件或文件夹。',
  'Skill保存的到底是什么？','流程、判断标准、工具用法和验收要求整理在文件或文件夹中，供重复执行。','排除误解与并列汇聚',
  ['一句提示词','认真一点','流程','判断标准','工具用法','验收要求','Skill文件夹'],[[x,'Skill文件夹','组成'] for x in ['流程','判断标准','工具用法','验收要求']],
  '先划除口播排除的两种误解，四个同级内容从独立路径汇入同一文件夹；箭头表示整理归档，不是四项先后依赖。',
  '从一句模糊要求转为四种可组织、可检查的内容类别。',
  [(.65,1.1,'误解1','一句提示词','排除','划线揭示','不是一句提示词'),(1.8,2.25,'误解2','认真一点','排除','划线揭示','也不是让AI认真一点')]+[(s+.55,s+1.4,k,k+'独立内容','进入Skill文件夹','曲线路径迁移',k) for k,s in [('流程',3.1),('判断标准',4.4),('工具用法',5.2),('验收要求',5.95)]],7.65,[.3,2.05,3.8,5.7,7,8.7]),
 ('C10',48,59.266,'一个入口，按需扩展',
  '在常见的Skill框架里 通常会有一个skill.md 里面写清楚：这个Skill叫什么 什么情况下使用 以及具体怎么执行 复杂一点的Skill 还可以搭配案例库 参考资料 脚本和数据库。',
  '核心说明文件和配套资料是什么关系？','在口播所说的常见框架中，核心说明通常包含名称、场景、步骤，复杂Skill可以配置辅助资料。','核心与可选扩展',
  ['Skill','SKILL.md','名称','适用场景','执行步骤','案例库','参考资料','脚本','数据库'],[['Skill','SKILL.md','通常的核心说明']]+[['Skill',x,'复杂时可配套'] for x in ['案例库','参考资料','脚本','数据库']],
  '文件夹连到主说明文件，文件内三项逐行揭示；随后独立资料支路展开。持续标“结构示意”，并注明复杂时可配套，非真实应用截图。',
  '将文件内部字段与外部辅助资源分开，避免把所有资料误当每个Skill的必备文件。',
  [(.4,1.15,'核心文件','文件夹','接通SKILL.md','连线与展开','通常会有一个skill.md'),(2.7,3.4,'名称字段','未填写行','名称字段展开','遮罩/线条揭示','叫什么'),(4,4.7,'场景字段','未填写行','适用场景展开','遮罩/线条揭示','什么情况下使用'),(5.8,6.5,'执行字段','未填写行','执行步骤展开','遮罩/线条揭示','具体怎么执行')]+[(7.7+i*.38,8.55+i*.38,k,'复杂Skill分支','资料归入各自节点','分支伸展与对象迁移',k) for i,k in enumerate(['案例库','参考资料','脚本','数据库'])],9.9,[.3,.95,3.05,6.2,8.4,10.6]),
 ('C11',59.266,65.666,'先匹配手册，再执行任务',
  '而Agent接到任务后 通常会先查看各个Skill的介绍 再选择最匹配的那个执行 这就像公司里分工。',
  '多个Skill都在时，任务怎样找到所需手册？','Agent通常查看介绍，并选择与任务匹配的Skill执行。','条件选择与执行',
  ['写短视频文案','文案手册','分析手册','剪辑手册','执行任务'],[['写短视频文案','文案手册','示例匹配'],['文案手册','执行任务','选中后执行']],
  '候选节点并列。阅读扫描覆盖三份介绍；最终只把文案手册接入执行线路。写文案任务为教学示例，沿用后文分工类比。',
  '明确“查看候选”和“选中执行”是两步，而不是所有Skill同时执行。',
  [(1.75,3.5,'候选介绍','第一候选','扫描三个候选介绍','框体连续纵移','查看各个Skill的介绍'),(3.65,4.1,'选择路径','候选分支','接通文案手册','路径描画','选择最匹配的那个'),(4.3,5.1,'执行','选中手册','内容沿路径进入执行任务','对象迁移','执行')],5.45,[.2,1.35,2.6,3.95,4.7,6]),
 ('C13',69.8,77.2,'把方法保存下来，供任务复用',
  '没有Skill 你每次都要重新教AI 有了Skill 你可以把自己的写作方法 运营经验 分析流程 变成AI能反复使用的能力。',
  '从每次解释到方法复用，差别在哪里？','将方法保存为可调用材料，后续任务可复用这份方法，而不是每次重新交代。','重复交代与保存复用对照',
  ['交代方法×3','任务1–3','方法存档','多任务调用'],[['交代方法×3','任务1–3','分别交代'],['方法存档','任务1–3','同一方法多次复用']],
  '左边每一任务有各自说明；右边保留同一方法库，分别把副本送向三次任务。不画脑内永久记忆，不暗示自动永久学习。',
  '相同任务数量下，对比重复输入与持久资料复用的关系。',
  [(s,s+.7,'交代'+str(i+1),'独立方法说明','各自任务','对象递交','每次都要重新教AI') for i,s in enumerate([.45,.9,1.35])]+[(2.5,3.2,'方法存档','方法纸页','归入文件夹','对象迁移','有了Skill')]+[(s,s+.9,'调用'+str(i+1),'存档手册保留','对应任务得到方法副本','一对多路径迁移','反复使用') for i,s in enumerate([3.45,4.12,4.79])],6.2,[.1,1.15,2.85,3.9,5.15,6.9]),
]
# SPECS above retains the episode's narration, relations and historical motion
# notes for traceability. Only the explicitly selected motion_specs is active.
ROOT=Path(__file__).resolve().parent
MOTION=json.loads((ROOT/'motion_specs.json').read_text(encoding='utf-8'))
PLAN=json.loads((EP/'03_storyboard/production_plan.json').read_text(encoding='utf-8'))
STYLE=json.loads((ROOT/'reference_style.json').read_text(encoding='utf-8'))
assert MOTION['revision']=='card_style_v4_reference', 'Unexpected episode motion revision'
assert PLAN['total_frames']==MOTION['timeline_lock']['total_frames']==2517
assert PLAN['fps']==MOTION['timeline_lock']['fps']==30
plan_cards={x['id']:x for x in PLAN['cards']}
assert set(MOTION['cards'])=={x[0] for x in SPECS}==set(plan_cards)
assert MOTION['typography_override']['title_px']==STYLE['typography_override']['title_px']==72
assert MOTION['typography_override']['node_px']==STYLE['typography_override']['node_px']==46
assert MOTION['typography_override']['support_px']==STYLE['typography_override']['support_px']==34
cards=[]
for id,start,end,title,source,q,claim,relation,nodes,edges,encoding,gain,_historical_events,_historical_hold,_historical_samples in SPECS:
    sf,ef=round(start*30),round(end*30)
    assert (sf,ef)==(plan_cards[id]['start_frame'],plan_cards[id]['end_frame']), id+': card boundary changed'
    motion=MOTION['cards'][id]
    count=ef-sf
    duration=count/30
    procs=[]
    for event in motion['process_events']:
        a,b=event['start'],event['end']
        assert 0<=a<b<=duration,(id,event['target'],'event outside card')
        af,bf=round(a*30),round(b*30)
        assert bf-af>=4,(id,event['target'],'process too short for triplet verification')
        # All three checks are strictly inside the process, not static endpoints.
        checks=[max(af+1,min(bf-2,round((a+(b-a)*p)*30))) for p in (.2,.5,.8)]
        assert af<checks[0]<=checks[1]<=checks[2]<bf
        assert 1<=checks[1]<count-1
        procs.append({'target_ids':[event['target']],'meaning':event['meaning'],
            'start_frame':af,'end_frame_exclusive':bf,
            'global_start_frame':sf+af,'global_end_frame_exclusive':sf+bf,
            'from':event.get('from',event['target']+'的过程起态'),
            'to':event['meaning'],'geometry':event['geometry'],
            'parameters_source':'06_project/cards/'+motion['module']+' / '+id,
            'motion_spec_source':'06_project/cards/motion_specs.json / '+id,
            'easing':'Pure frame-time functions; cubic/quadratic object changes, linear arc-length packet progression',
            'voice_anchor':event['voice_anchor'],
            'retain':'来源、已完成字段与必要关系保留；调用时方法母本不消失',
            'check_frames':checks,'check_frame_scope':'strictly inside continuous process; index 1 is encoded midpoint check'})
    hold=motion['hold_start']
    assert 0<=hold<duration,(id,'invalid reading hold')
    hold_frame=round(hold*30)
    samples=[round(x*30) for x in motion['sample_seconds']]
    assert len(samples)==6 and len(set(samples))==6,(id,'overview must contain exactly six unique frames')
    assert all(0<=f<count for f in samples),(id,'sample outside card')
    details=sorted(set(samples+[round(x*30) for x in motion.get('detail_sample_seconds',[])]+[e['check_frames'][1] for e in procs]))
    assert all(0<=f<count for f in details)
    cards.append({'id':id,'start':start,'end':end,'start_frame':sf,'end_frame_exclusive':ef,'frame_count':count,
        'title':title,'source_span':source,'viewer_question':q,'core_claim':claim,'relation_type':relation,
        'nodes':[{'id':x,'label':x} for x in nodes],'edges':[{'from':a,'to':b,'meaning':c} for a,b,c in edges],
        'visual_encoding':encoding,'screen_copy':nodes,'information_gain':gain,
        'claim_basis':{'narration':'用户提供SRT','inference':'仅对口播关系作结构化归纳',
            'examples':'任务A/B、任务1–3、文件夹结构与选择文案手册均为明确示意',
            'unknown':'未验证框架实际产品UI；不作产品事实证明'},
        'states':['初态：建立观众问题及对象','中态：连续运动建立关系，输入/方法保留','末态：关系完整，停留阅读'],
        'motion_revision':MOTION['revision'],'motion_reference':motion.get('reference',[]),
        'process_events':procs,'reading_hold':{'start_frame':hold_frame,'end_frame_exclusive':count,
            'duration_seconds':round((count-hold_frame)/30,3)},
        'sample_frames':samples,'process_sample_frames':details,
        'video':'04_assets/cards/'+id+'.mp4','renderer':'06_project/cards/card_scene.html?card='+id})
assert sum(c['frame_count'] for c in cards)==MOTION['timeline_lock']['card_frames']==1547
active_sources=['card_scene.html','card_kit.js','cards_main.js','cards_middle.js','reference_style.json','motion_specs.json','vendor/flubber.min.js']
data={'sop_version':'4.4.1','fps':30,'resolution':[1920,1080],'card_subtitles':False,
    'motion_revision':MOTION['revision'],'episode_total_frames':PLAN['total_frames'],
    'implementation':'Episode-specific reference adaptation; deterministic SVG card_kit + cards_main + cards_middle. Local vendored flubber supplies real shape interpolation; no network imports. Original episode narration and timing retained.',
    'active_sources':['06_project/cards/'+x for x in active_sources],
    'source_sha256':{x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in active_sources},
    'historical_inactive_sources':['06_project/cards/card_motion.js','06_project/cards/palette_override.json'],
    'type_defaults':'This-episode explicit reference override: title72px, main node46px, support34px; local headings/fields40/44/48/52px preserve hierarchy. Snapshot defaults and SOP are unchanged.',
    'typography_override':MOTION['typography_override'],
    'process_sample_policy':MOTION['overview_policy'],'cards':cards}
(EP/'03_storyboard/cards.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'revision':MOTION['revision'],'cards':len(cards),'card_frames':sum(c['frame_count'] for c in cards),
    'episode_total_frames':PLAN['total_frames'],'process_events':sum(len(c['process_events']) for c in cards)},ensure_ascii=False))
