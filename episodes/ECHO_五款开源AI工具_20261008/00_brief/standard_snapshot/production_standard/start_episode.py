"""Create a new episode brief and exact standard snapshot; never render an old episode."""
from pathlib import Path
import argparse,json,re,hashlib,shutil
from standard_loader import load,ROOT

def main():
    ap=argparse.ArgumentParser(description='新集输入与标准锁；不会自动生成视频，也不会操作剪映。')
    ap.add_argument('--name',required=True);ap.add_argument('--srt');ap.add_argument('--voice');ap.add_argument('--out')
    args=ap.parse_args();m=load()
    if not re.fullmatch(r'[^<>:"/\\|?*\x00-\x1f]+',args.name) or args.name.strip(' .')!=args.name or args.name in {'.','..'}:ap.error('项目名不能包含路径或Windows保留字符。')
    inputs={}
    for key,raw in [('srt',args.srt),('voice',args.voice)]:
        if raw:
            p=Path(raw).expanduser().resolve()
            if not p.is_file():ap.error('输入不存在：'+str(p))
            inputs[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        else:inputs[key]=None
    dest=Path(args.out).resolve() if args.out else ROOT/'episodes'/args.name
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir())):ap.error('输出目录非空，保留原项目，请用新目录：'+str(dest))
    for folder in ['00_brief','01_audio','02_timing','03_storyboard','04_assets','05_sample','06_project','07_exports','08_qc']:(dest/folder).mkdir(parents=True,exist_ok=True)
    snap=dest/'00_brief/standard_snapshot'
    for item in m['files']:
        target=snap/item['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/item['path'],target)
    shutil.copy2(ROOT/'production_standard.json',snap/'production_standard.json')
    baseline=m.get('baseline_manifest',m.get('baseline'))
    brief={'project_name':args.name,'standard_version':m['version'],'standard_status':m['status'],'standard_user_approved':m['user_approved'],'user_confirmed_changes':m.get('user_confirmed_changes',{}),'inputs':inputs,'topic':None,'audience':None,'per_episode_overrides':{},'subtitle_mode':None,'bgm_mode':None,'sfx_mode':None,'project_format':'source_project','jianying_import_requested':False,'jianying_import_authorization':None,'production_baseline':baseline,'baseline_resolution':'Read the pinned baseline and its assets inside 00_brief/standard_snapshot; do not execute a historical episode as new content.','requested_stage':None,'render_status':'not_started','note':'本文件只建立输入与标准快照；继续完成内容、分镜、素材、过程动效与实际检查。默认交付视频制作源码；剪映导入不属于本流程。技术配置、历史工程或安装环境均不能替代用户另行明确请求。'}
    brief['standard_approval_mode']=m.get('approval_mode')
    brief['standard_approval']=m.get('approval',{})
    brief['standard_self_check']=m.get('self_check')
    (dest/'00_brief/episode.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2),encoding='utf-8')
    (dest/'00_brief/standard_lock.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
    fields=['镜头号','对应文案','预估时长','画面类型（动画/信息卡）','大概画面简介']
    (dest/'03_storyboard/storyboard.json').write_text(json.dumps({'review_columns':fields,'shots':[],'production_events':[],'cards':[],'sop_version':m['version'],'source_status':'awaiting_content_design'},ensure_ascii=False,indent=2),encoding='utf-8')
    (dest/'00_brief/开始制作.txt').write_text('先读取本目录episode.json、standard_lock.json和standard_snapshot中的完整SOP/提示词/制作基准及参考资产。\n默认工程是可改源码source_project，不生成或导入剪映草稿。只有用户另行明确提出剪映导入，才建立独立任务；不得用技术配置替代请求。\n填写真正缺失的本集配置；已明确要求不重复确认。\n当前目录没有视频、图片、分镜内容或验收结果，不能称为生产完成。\n',encoding='utf-8')
    print(json.dumps({'project':str(dest),'version':m['version'],'status':m['status'],'created':'brief_and_standard_snapshot','video_generated':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
