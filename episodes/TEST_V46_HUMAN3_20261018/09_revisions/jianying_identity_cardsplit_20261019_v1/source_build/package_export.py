"""Attach sources and user-run import entry, then archive once; no review or registration."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone, timedelta

R=Path(__file__).resolve().parents[1]
EP=R.parents[1]
PROJECT=EP.parents[1]
P=R/'HUMAN3_角色插画修订_文字独立_剪映草稿'
OLD=R.parent/'jianying_subtitle_fixed_20261018_v3/第一步_字幕居中版_v3_剪映分层草稿'
SKILL=Path('C:/Users/Administrator/.codex/skills/jianying-layered-export')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()

def main():
    archive=R/(P.name+'.zip')
    if archive.exists() or (P/'export_source').exists():raise FileExistsError('Package already assembled')
    source=P/'export_source';source.mkdir()
    shutil.copytree(R/'source_render',source/'source_render')
    shutil.copytree(R/'source_build',source/'source_build')
    (P/'attachments').mkdir()
    shutil.copy2(EP/'00_brief/input/10月18日.srt',P/'attachments/10月18日.srt')
    tools=P/'import_tools';tools.mkdir()
    helper=(OLD/'import_tools/import_package.py').read_text(encoding='utf-8-sig')
    helper=helper.replace("name = args.name or f'第一步_字幕居中版_v3_{stamp}'", "name = args.name or (read(args.package / 'manifest.json')['project']['name'] + '_' + stamp)")
    helper=helper.replace("'import_audit_subtitlefix_'", "'import_audit_identity_cardsplit_'")
    (tools/'import_package.py').write_text(helper,encoding='utf-8')
    for name in ('install_draft.py','validate_package.py','native_evidence.py'):
        shutil.copy2(SKILL/'scripts'/name,tools/name)
    # These entry files are delivered for a later user action; never executed here.
    shutil.copy2(OLD/'导入本机剪映.ps1',P/'import.ps1')
    (P/'双击导入剪映.cmd').write_bytes(b'@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0import.ps1"\r\npause\r\n')
    readme='''HUMAN3 角色与语义插画修订版｜剪映分层草稿

导出完成；本次未注册进剪映，未执行额外复检、原生校准、试听或播放。
55.933 秒，1920×1080，30fps。保留新版12张插画、4段信息卡及原配音。

在剪映中编辑
1. 将 ZIP 完整解压到固定文件夹，不要直接在压缩包中运行。
2. 双击“​​双击导入剪映.cmd”（文件名无开头空格）。它会调用本机已有兼容环境，新建并注册一个带时间戳的草稿；不会替换旧草稿。此动作由你点击后才执行。
3. 随后在剪映首页打开以“HUMAN3_角色插画修订_文字独立_55秒”开头的新草稿。
不要把 ZIP 或 draft_content.json 当普通视频拖入素材库。仅解压不会自动出现在剪映首页。
导入需要本机兼容的 pyJianYingDraft 环境；可用 JY_DRAFT_PYTHON 指定 Python。导入助手不会自动安装依赖、关闭或重启剪映。

图层结构
- 12个插画片段分别可替换；本版插画源是静态完整场景，因此草稿使用逐镜PNG。
- 每张信息卡的背景、框体、图标、箭头、连线及非文字动效合成一个连续视频片段，共4段。
- 信息卡57段原生文字可独立修改；标题、品牌和31条口播字幕也保留为原生文字。
- 31条口播字幕及对应底板独立，固定底部中央，不设置横移。字幕长度变化可居中，若改字显著变长，需自行相应调整该条底板宽度。
- 原配音独立音轨，音量1；画面片段静音，避免重复配音。
- “信息卡与文字编辑索引.txt/json”列出每段内容、起止时间和轨道。轨道按并发占用复用，并非每句话永久占一条轨道。
- 非文字素材内部框体、线条等不能逐个修改，需要回源工程重渲；整层可移动、裁剪、缩放或替换。

本次已确认的处理
“摘要示意”在进入接收槽遮挡处时整段隐藏。按源对象包围盒计算，截止点为第839帧，约27.967秒；文字片段仍可编辑，不另拆前景层。

继承的文字映射边界
行动指南展开时，原生文字沿用旋转及双轴缩放近似，不能精确还原SVG剪切；普通文字渐显/渐隐沿用已有原生动画和时段，不承诺与源透明度曲线逐帧相同。
本次不做原生字号/位置校准，使用已有1080p微软雅黑映射。系统微软雅黑字体未打包；换机需安装对应字体。原生动画资源由剪映解析。

旧草稿、已有成片、原插画与源工程未被本次覆盖。旧草稿中你手动做过的修改未迁入本稿。
export_source 包含本次抽层适配、原始渲染源码、12张选定插画及原生文字映射快照。参考其“重新导出说明.txt”。
'''.replace('“​​双击','“双击')
    (P/'先读我_导入与编辑.txt').write_text(readme,encoding='utf-8-sig')
    instructions='''重建说明（仅在需要时运行；本次没有重复渲染或复检）

1. 使用安装 Playwright 的 Python 与本机 Chrome，执行：
python source_render/generate_composites.py --source source_render/original --output D:/your-work/new-export-run

必须选择不存在的新输出目录。FFmpeg 路径来自 source_render/original/source/config.json；换机可仅在自己的副本中调整。

2. 使用兼容 pyJianYingDraft 的 Python，执行：
python source_build/build_draft.py --catalog D:/your-work/new-export-run/rendered/catalog.json --native-source source_build/card_native_source.json --voice ../media/original_narration.mp3 --output D:/your-work/new-draft-package

以上命令从 export_source 目录运行。构建器拒绝覆盖已有输出。
若修改信息卡文案或动画，需要相应重新提取原生文字，不应沿用过时的 card_native_source.json。
package_export.py 是本次项目内打包脚本；独立搬移后使用前两步重建，不运行依赖项目状态文件的 package_export.py。
没有复制全局技能、系统字体或Python环境。所有实际源插画和渲染JS已在此目录，无需旧集修订目录的素材。
'''
    (source/'重新导出说明.txt').write_text(instructions,encoding='utf-8-sig')
    m=read(P/'manifest.json')
    video=R.parent/'identity_semantic_full_20261018_v2/exports/full_01/HUMAN3_角色与语义插画修订完整版_1080p.mp4'
    m['dependencies'].update(sourceVideo={'path':str(video),'sha256':sha(video)},
      skill={'path':str(SKILL/'SKILL.md'),'sha256':sha(SKILL/'SKILL.md')},
      sourceRendererSha256=sha(R/'source_render/generate_composites.py'))
    write(P/'manifest.json',m)
    receipt=read(P/'导出状态.json')
    receipt.update(manifestSha256=sha(P/'manifest.json'),
      sourceVideoSha256=m['dependencies']['sourceVideo']['sha256'],
      editableCardTextSegments=57,review='not_performed',registration='not_performed',
      zipIntegrityReview='not_performed',importEntry='双击导入剪映.cmd')
    write(P/'导出状态.json',receipt)
    # Record construction inventory, then make one ZIP without CRC rereads or package review.
    listing=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
      for p in sorted(P.rglob('*')) if p.is_file()]
    write(P/'archive_manifest.json',{'status':'inventory_created_not_reviewed','files':listing})
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in sorted(P.rglob('*')):
            if p.is_file():z.write(p,Path(P.name)/p.relative_to(P))
    receipt.update(zip=str(archive),zipBytes=archive.stat().st_size,zipSha256=sha(archive))
    write(R/'export_receipt.json',receipt)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat()
    state=read(EP/'00_brief/episode_state.json')
    rel=R.relative_to(EP).as_posix()
    state.update(updated_at=now,status='exported_review_not_performed',
      next_action='交付新的文字独立/每卡非文字合成剪映草稿包；注册由用户运行导入入口，复检未执行。',
      latest_export_notes={'receipt':rel+'/export_receipt.json','draft_name':receipt['draftName'],
        'scope':'identity_semantic_full_card_text_split','native_text_segments':receipt['nativeTextSegments'],
        'review':'not_performed','registration':'not_performed','previous_outputs':'旧草稿、已有成片和素材均保留。'})
    state['acceptance']['jianying_draft_export']='identity_cardsplit_exported_review_not_performed'
    state['acceptance']['jianying_additional_review']='not_performed'
    state['outputs'].extend([
      {'type':'jianying_identity_cardsplit_draft','path':rel+'/'+P.name+'/draft_content.json','sha256':receipt['draftSha256'],'status':'exported_review_not_performed'},
      {'type':'jianying_identity_cardsplit_zip','path':rel+'/'+archive.name,'sha256':receipt['zipSha256'],'bytes':receipt['zipBytes'],'status':'exported_review_not_performed'}])
    if 'jianying_identity_cardsplit_export' not in state['completed_stages']:state['completed_stages'].append('jianying_identity_cardsplit_export')
    write(EP/'00_brief/episode_state.json',state)
    current=read(PROJECT/'CURRENT_PROJECT.json');current['updated_at']=now
    current['latest_episode']['status']='exported_review_not_performed'
    write(PROJECT/'CURRENT_PROJECT.json',current)
    write(R/'state.json',{'status':'exported_review_not_performed','sourceRevision':'identity_semantic_full_20261018_v2',
      'receipt':'export_receipt.json','registration':'not_performed','review':'not_performed',
      'approvedException':'summary hides on entering tray at frame839; no extra card visual layer'})
    print(json.dumps({'zip':str(archive),'bytes':receipt['zipBytes'],'package':str(P),
      'status':receipt['status'],'review':'not_performed','registration':'not_performed'},ensure_ascii=False))

if __name__=='__main__':main()
