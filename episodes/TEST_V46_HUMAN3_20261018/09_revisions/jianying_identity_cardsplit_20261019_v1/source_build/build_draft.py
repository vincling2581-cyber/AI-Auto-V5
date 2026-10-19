"""Build a new portable draft from rendered assets and a scoped native-text snapshot.

Export only. No review, editor, installation, or overwrite operation is performed.
Run with the existing pyJianYingDraft Python runtime.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import shutil
import uuid

REV = Path(__file__).resolve().parents[1]
NAME = 'HUMAN3_角色插画修订_文字独立_55秒'
SCENES = {'C02':'quadrants', 'C03':'prompt', 'C04':'plan', 'C05':'choice'}
LABELS = {'quadrants':'四个方向', 'prompt':'提示交给AI', 'plan':'行动指南', 'choice':'选择与关注'}

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def write(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def rgb(v):
    if v.startswith('#'):
        v = v[1:]
        if len(v)==3:
            v=''.join(x*2 for x in v)
        return tuple(int(v[i:i+2],16)/255 for i in (0,2,4))
    if v.startswith('rgb'):
        return tuple(float(n)/255 for n in re.findall(r'[\d.]+',v)[:3])
    raise ValueError('Unsupported source color '+v)

def remap_ids(data):
    ids = set()
    def collect(node):
        if isinstance(node, dict):
            v=node.get('id')
            if isinstance(v,str) and re.fullmatch(r'[0-9a-fA-F-]{32,36}',v):
                ids.add(v)
            for v in node.values(): collect(v)
        elif isinstance(node,list):
            for v in node: collect(v)
    collect(data)
    mapping={v:uuid.uuid4().hex for v in ids}
    def rewrite(node):
        if isinstance(node,dict): return {k:rewrite(v) for k,v in node.items()}
        if isinstance(node,list): return [rewrite(v) for v in node]
        return mapping.get(node,node) if isinstance(node,str) else node
    return rewrite(data)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=REV/'HUMAN3_角色插画修订_文字独立_剪映草稿')
    ap.add_argument('--catalog',type=Path,default=REV/'rendered/catalog.json')
    ap.add_argument('--native-source',type=Path,default=REV/'source_build/card_native_source.json')
    ap.add_argument('--voice',type=Path,required=True)
    args=ap.parse_args()
    import pyJianYingDraft as d
    out=args.output.resolve()
    if out.exists(): raise FileExistsError('Refuse to overwrite '+str(out))
    cat=read(args.catalog)
    card=remap_ids(read(args.native_source))
    W,H,FPS,TOTAL=cat['width'],cat['height'],cat['fps'],cat['totalFrames']
    us=lambda f:round(f*1000000/FPS)
    root=args.catalog.resolve().parent.parent
    if len([x for x in cat['items'] if x['type']=='card'])!=4:
        raise ValueError('This episode expects its four source cards')
    out.mkdir(parents=True)
    (out/'media').mkdir()
    script=d.ScriptFile(W,H,FPS,False)
    manifest={'schemaVersion':1,'layeringMode':'card_text_split',
      'project':{'name':NAME,'width':W,'height':H,'fps':FPS,'durationUs':us(TOTAL)},
      'media':[],'panels':[],'sources':[],'segments':[],
      'fontDependencies':card['fontDependencies'],
      'nativeAnimationDependencies':card['nativeAnimationDependencies'],
      'exportStatus':'exported','registered':False,'automaticGroups':False,
      'structuralValidation':'not_performed','nativeValidation':'not_performed',
      'nativeOpenPlayback':'not_performed','nativeExport':'not_performed',
      'zipIntegrityReview':'not_performed',
      'dependencies':{'nativeTextSourceSha256':sha(args.native_source),
        'renderCatalogSha256':sha(args.catalog),'builderSha256':sha(__file__),
        'fontMapping':card['mapping'],'cardTextProvenance':card['provenance']},
      'builderRuntime':{'pythonLibrary':d.__file__,
        'version':importlib.metadata.version('pyJianYingDraft')}}
    entries=[]
    paths={}
    exported={}
    def media(src, name):
        src=Path(src).resolve()
        if src in exported:return exported[src]
        if not src.is_file():raise FileNotFoundError(src)
        relative='media/'+name+src.suffix.lower()
        dest=out/relative
        if dest.exists():raise FileExistsError(dest)
        shutil.copy2(src,dest)
        paths[str(dest).casefold()]=relative
        manifest['media'].append({'path':relative,'bytes':dest.stat().st_size,'sha256':sha(dest)})
        exported[src]=(dest,relative)
        return dest,relative
    def add(segment,row,kind,z):
        track=script.append_track(d.TrackSpec(getattr(d.TrackType,kind),name='build_'+str(len(entries))))
        script.add_segment(segment,track)
        row.update(id=segment.segment_id,materialId=segment.material_id,sourceZ=z)
        manifest['segments'].append(row)
        entries.append({'id':segment.segment_id,'row':row,'kind':kind,'z':z,'ordinal':len(entries)})
    for item in cat['items']:
        a,b=item['startFrame'],item['endFrameExclusive']
        dest,relative=media(root/item['path'],item['id'])
        mat=d.VideoMaterial(str(dest),material_name=item['id'])
        segment=d.VideoSegment(mat,d.Timerange(us(a),us(b)-us(a)),volume=0)
        role='graphics' if item['type']=='card' else 'animation'
        owner='card_visual' if role=='graphics' else 'shared'
        row={'scene':item['id'],'role':role,'owner':owner,'path':relative,
          'sourceLayerId':item['id'],'startFrame':a,'endFrameExclusive':b,
          'startUs':us(a),'durationUs':us(b)-us(a),'expectedVolume':0}
        if role=='graphics':
            ids=item['sourceObjectIds']
            if not ids or len(ids)!=len(set(ids)):raise ValueError('Invalid source map')
            row['sourceObjectIds']=ids
            manifest['panels'].append({'scene':item['id'],'id':owner,'label':LABELS[item['id']]+'｜非文字合成'})
            manifest['sources'].append({'scene':item['id'],'objects':[{'id':s,'owner':owner} for s in ids]})
        add(segment,row,'video',0)
    for item in cat['subtitle_plates']:
        a,b=item['startFrame'],item['endFrameExclusive']
        dest,relative=media(root/item['path'],item['id'])
        mat=d.VideoMaterial(str(dest),material_name=item['id'])
        scale=1/min(W/mat.width,H/mat.height)
        # Plate x/y are its source crop origin; retain its original center/baseline.
        settings=d.ClipSettings(transform_x=0,transform_y=1-2*(item['y']+item['height']/2)/H,
          scale_x=scale*item['width']/mat.width,scale_y=scale*item['height']/mat.height)
        segment=d.VideoSegment(mat,d.Timerange(us(a),us(b)-us(a)),volume=0,clip_settings=settings)
        add(segment,{'scene':'CAPTIONS','role':'background','owner':'shared',
          'sourceLayerId':item['id'],'subtype':'subtitle_plate','path':relative,
          'startFrame':a,'endFrameExclusive':b,'startUs':us(a),'durationUs':us(b)-us(a),
          'expectedVolume':0,'positionPolicy':'fixed_bottom_center'},'video',8000)
    for item in cat['overlay_texts']:
        a,b=item['startFrame'],item['endFrameExclusive']
        size=item['size']; nx=item['x']; ny=item['y']+size*.105
        if item['kind']=='subtitle': nx=W/2
        native_size=size/(H/100)*1.035
        style=d.TextStyle(size=native_size,bold=item['bold'],color=rgb(item['color']),align=1,auto_wrapping=False)
        segment=d.TextSegment(item['text'],d.Timerange(us(a),us(b)-us(a)),font_path='',style=style,
          clip_settings=d.ClipSettings(transform_x=2*nx/W-1,transform_y=1-2*ny/H,alpha=1))
        role='brand' if item['kind']=='brand' else 'text'
        row={'scene':'OVERLAY','role':role,'owner':'shared','sourceLayerId':item['id'],
          'textKey':item['id'],'text':item['text'],'subtype':item['kind'],
          'fontFamily':'Microsoft YaHei','nativeFontSize':native_size,'bold':item['bold'],
          'startFrame':a,'endFrameExclusive':b,'startUs':us(a),'durationUs':us(b)-us(a),
          'motionIntent':{'visibilityMethod':'segment_ranges','scalePurpose':'source_animation'}}
        if item['kind']=='subtitle':row['positionPolicy']='fixed_bottom_center'
        add(segment,row,'text',10000 if item['kind']=='subtitle' else 1000)
    dest,relative=media(args.voice,'original_narration')
    audio=d.AudioMaterial(str(dest),material_name='原配音｜独立音轨')
    duration=min(audio.duration,us(TOTAL))
    voice=d.AudioSegment(audio,d.Timerange(0,duration),volume=1)
    add(voice,{'scene':'EPISODE','role':'narration','owner':'shared','path':relative,
      'startUs':0,'durationUs':duration,'sourceDurationUs':audio.duration,
      'expectedVolume':1,'audioGainBakedDb':0,'sourceSampleModification':'none'},'audio',11000)
    draft=json.loads(script.dumps())
    # Resolve paths and system-font mapping while generating the portable payload.
    new_rows={x['materialId']:x for x in manifest['segments'] if x['role'] in ('text','brand')}
    for category,materials in draft['materials'].items():
        if not isinstance(materials,list):continue
        for mat in materials:
            if mat.get('path'):mat['path']=paths[str(Path(mat['path']).resolve()).casefold()]
            if category=='texts':
                row=new_rows[mat['id']]
                mat.update(font_name=row['fontFamily'],font_path='',font_size=row['nativeFontSize'],global_alpha=1)
                content=json.loads(mat['content'])
                for style in content['styles']:
                    style['font']={'id':'','path':''};style['bold']=row['bold']
                    style['fill']['alpha']=1;style['fill']['content']['solid']['alpha']=1
                mat['content']=json.dumps(content,ensure_ascii=False)
    actual={s['id']:s for t in draft['tracks'] for s in t['segments']}
    # User-approved hide-on-entry for the summary occluded by the tray lip.
    hits=[]
    for state in card['summarySource']['states']:
        x,y,w,h=state['transformedBBox']
        if x<1032 and x+w>758 and y<713 and y+h>660:hits.append(state['frame'])
    if not hits:raise ValueError('No source overlap for the approved visibility adjustment')
    cut=min(hits)
    old_actual={s['id']:s for s in card['segments']}
    for row in card['rows']:
        row=copy.deepcopy(row);segment=copy.deepcopy(old_actual[row['id']])
        if row['sourceLayerId']=='C03.document.summary':
            end=us(cut);start=segment['target_timerange']['start']
            segment['target_timerange']['duration']=end-start
            for keyframes in segment.get('common_keyframes',[]):
                keys=keyframes['keyframe_list']
                # Every source frame is sampled; retaining offsets within the new span
                # preserves the trajectory until the requested visibility cutoff.
                keyframes['keyframe_list']=[k for k in keys if k['time_offset']<end-start]
            row.update(endFrameExclusive=cut,durationUs=end-start,
              visibilityOverride={'userApproved':True,'hideAtFrame':cut,
                'reason':'hide whole editable text when entering tray foreground'})
        row['scene']=SCENES[row['scene']];row['owner']='card_visual'
        row.pop('trackId',None);row.pop('trackName',None);row.pop('renderIndex',None)
        row['sourceZ']=100+row.get('sourceZ',0)
        row['logicalTextKey']=row['sourceLayerId']
        segment['group_id']=''
        if any(k['property_type']=='KFTypeAlpha' for k in segment.get('common_keyframes',[])):
            raise ValueError('Unexpected unsupported alpha in reused native text')
        actual[segment['id']]=segment
        manifest['segments'].append(row)
        entries.append({'id':segment['id'],'row':row,'kind':'text','z':row['sourceZ'],'ordinal':len(entries)})
    for category,materials in card['materials'].items():
        if materials:draft['materials'].setdefault(category,[]).extend(materials)
    # Reuse tracks by concurrent occupancy, retaining z order among overlapping units.
    def overlap(a,b):
        return a['a']<b['b'] and b['a']<a['b']
    lanes=[]
    for entry in entries:
        span=actual[entry['id']]['target_timerange']
        entry['a']=span['start'];entry['b']=span['start']+span['duration']
    for entry in sorted(entries,key=lambda x:(x['z'],x['a'],x['ordinal'])):
        lower=0
        for i,lane in enumerate(lanes):
            if any(overlap(entry,other) for other in lane['entries']):lower=i+1
        lane=next((l for l in lanes[lower:] if l['kind']==entry['kind'] and not any(overlap(entry,o) for o in l['entries'])),None)
        if lane is None:lane={'kind':entry['kind'],'entries':[]};lanes.append(lane)
        lane['entries'].append(entry)
    draft['tracks']=[]
    for i,lane in enumerate(lanes):
        kinds={e['row'].get('subtype',e['row']['role']) for e in lane['entries']}
        label=('画面｜每卡非文字合成／插画' if i==0 else
          '口播字幕｜固定底部中央' if kinds=={'subtitle'} else
          '字幕底板｜固定底部中央' if kinds=={'subtitle_plate'} else
          '原配音' if lane['kind']=='audio' else '可编辑文字｜按时间复用')
        name=f'{i+1:02d}｜{label}'
        track={'attribute':0,'flag':0,'id':uuid.uuid4().hex,'is_default_name':False,
          'name':name,'type':lane['kind'],'segments':[]}
        for e in sorted(lane['entries'],key=lambda x:x['a']):
            row=e['row'];segment=actual[e['id']]
            segment['render_index']=i;segment['track_render_index']=i
            segment['desc']=f'{row["scene"]}｜{LABELS.get(row["scene"],row["scene"])}｜'+row.get('text',row.get('sourceLayerId',row['role']))
            row.update(trackId=track['id'],trackName=name,renderIndex=i)
            track['segments'].append(segment)
        draft['tracks'].append(track)
    draft.update(id=str(uuid.uuid4()).upper(),name=NAME,duration=us(TOTAL))
    manifest['approvedExceptions']=[{'sourceText':'摘要示意','scene':'prompt',
      'hideAtFrame':cut,'hideAtSeconds':cut/FPS,'policy':'hide_on_first_occlusion',
      'nativeTextStillEditable':True,'extraGraphicLayers':0}]
    manifest['knownLimits']=[
      '原生文字继续使用现有1080p微软雅黑字号和位置映射；本次未做原生校准。',
      '行动指南展开时的文字沿用旋转及双轴缩放近似，无法精确还原源SVG的剪切；到达后的文字仍可编辑。',
      '原生渐显/渐隐沿用已有资源及时间窗口，不承诺与源透明度曲线逐帧一致。',
      '系统微软雅黑字体未打包；迁移机器需安装对应字体。']
    write(out/'draft_content.json',draft)
    write(out/'manifest.json',manifest)
    write(out/'信息卡与文字编辑索引.json',manifest['segments'])
    lines=['信息卡文字独立；每卡其他元素合成一层。',
      '非文字素材内部框体/图标/连线需回源工程修改；文字可直接编辑。',
      '时间（秒） | 场景 | 类型 | 内容 | 轨道']
    for row in sorted(manifest['segments'],key=lambda x:(x['startUs'],x['renderIndex'])):
        text=row.get('text',row.get('sourceLayerId',row['role'])).replace('\n',' ')
        lines.append(f'{row["startUs"]/1e6:.3f}–{(row["startUs"]+row["durationUs"])/1e6:.3f} | {row["scene"]} | {row["role"]} | {text} | {row["trackName"]}')
    (out/'信息卡与文字编辑索引.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8-sig')
    receipt={'status':'exported_review_not_performed','draftName':NAME,
      'package':str(out),'durationSeconds':us(TOTAL)/1e6,'fps':FPS,'width':W,'height':H,
      'illustrationClips':sum(x['type']=='illustration' for x in cat['items']),
      'cardComposites':4,'nativeCardTextSegments':len(card['rows']),
      'nativeSubtitleSegments':sum(x['kind']=='subtitle' for x in cat['overlay_texts']),
      'nativeTextSegments':sum(x['role'] in ('text','brand') for x in manifest['segments']),
      'tracks':len(draft['tracks']),'segments':len(manifest['segments']),
      'draftSha256':sha(out/'draft_content.json'),'manifestSha256':sha(out/'manifest.json'),
      'approvedExceptions':manifest['approvedExceptions'],
      'structuralValidation':'not_performed','nativeCalibration':'not_performed',
      'nativeOpenPlayback':'not_performed','nativeExport':'not_performed',
      'registration':'not_performed','zipIntegrityReview':'not_performed',
      'createdAt':datetime.now(timezone(timedelta(hours=8))).isoformat()}
    write(out/'导出状态.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
