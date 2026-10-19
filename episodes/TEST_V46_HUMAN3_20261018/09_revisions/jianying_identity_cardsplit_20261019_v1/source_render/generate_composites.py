#!/usr/bin/env python3
"""Generate scoped source-based media and measured native-overlay metadata.

This is an export operation only. It intentionally performs no comparison,
calibration, output decoding, subjective playback, or native-editor operation.
"""
from __future__ import annotations

from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ORIGINAL = OUT.parent / 'identity_semantic_full_20261018_v2'
COPY = HERE / 'original'
RENDERED = OUT / 'rendered'
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0


def json_write(path, data):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def prepare():
    (COPY / 'source').mkdir(parents=True, exist_ok=True)
    (COPY / 'assets').mkdir(exist_ok=True)
    for name in ['index.html', 'app.js', 'cards.js', 'config.json', 'timeline.json',
                 'subtitles.json', 'effective_defaults.json']:
        target = COPY / 'source' / name
        with target.open('xb') as stream:
            stream.write((ORIGINAL / 'source' / name).read_bytes())
    scenes = json.loads((COPY / 'source' / 'timeline.json').read_text(encoding='utf-8-sig'))
    for scene in scenes:
        if scene['type'] == 'illustration':
            target = COPY / scene['asset_path']
            with target.open('xb') as stream:
                stream.write((ORIGINAL / scene['asset_path']).read_bytes())
    for folder in ['illustrations', 'cards', 'subtitle_plates']:
        (RENDERED / folder).mkdir(parents=True, exist_ok=True)
    return scenes, json.loads((COPY / 'source' / 'config.json').read_text(encoding='utf-8-sig'))


@contextmanager
def serve():
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(COPY)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}/source/index.html'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


# The original renderer selects subtitles by the same floating-point frame / fps
# comparisons. Enumerating those source states avoids rounding millisecond cues.
MEASURE_JS = r'''({totalFrames, fps, scenes}) => {
  function measure(el) {
    const b=el.getBBox(), m=el.getCTM(), style=getComputedStyle(el);
    const corners=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]]
      .map(([x,y])=>({x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f}));
    const x0=Math.min(...corners.map(p=>p.x)),x1=Math.max(...corners.map(p=>p.x));
    const y0=Math.min(...corners.map(p=>p.y)),y1=Math.max(...corners.map(p=>p.y));
    return {text:el.textContent,x:(x0+x1)/2,y:(y0+y1)/2,
      size:parseFloat(style.fontSize),color:el.getAttribute('fill')||style.fill,
      bold:Number(style.fontWeight)>=600,fontWeight:style.fontWeight,fontFamily:style.fontFamily,
      bbox:{x:b.x,y:b.y,width:b.width,height:b.height},
      screenBBox:{x:x0,y:y0,width:x1-x0,height:y1-y0},
      ctm:{a:m.a,b:m.b,c:m.c,d:m.d,e:m.e,f:m.f},
      anchor:el.getAttribute('text-anchor')||'start'};
  }
  const texts=[],plates=[],subtitleMap=new Map();
  const add=(el,id,kind,startFrame,endFrameExclusive,extra={})=>{
    const value=measure(el);
    const state={frame:startFrame,x:value.x,y:value.y,size:value.size,color:value.color,
      bold:value.bold,fontFamily:value.fontFamily};
    const record={id,kind,startFrame,endFrameExclusive,...value,states:[state],...extra};
    texts.push(record); return record;
  };
  window.renderFrame(0);
  document.querySelectorAll('[data-opening-hook] text').forEach((el,i)=>
    add(el,'opening_'+(i+1),'opening',0,119));
  window.renderFrame(119);
  document.querySelectorAll('[data-framework-label] text').forEach((el,i)=>
    add(el,'framework_'+(i+1),'framework',119,235));
  for(const scene of scenes){
    window.renderFrame(scene.start_frame);
    add(document.querySelector('#overlay > text'),'brand_'+scene.id,'brand',scene.start_frame,
      scene.end_frame_exclusive,{sceneId:scene.id});
  }
  for(let frame=0;frame<totalFrames;frame++){
    const result=window.renderFrame(frame);
    if(result.subtitle===null)continue;
    const key=result.subtitle,group=document.querySelector('[data-subtitle-id]');
    if(!subtitleMap.has(key)){
      const id='subtitle_'+String(key).padStart(2,'0');
      const record=add(group.querySelector('text'),id,'subtitle',frame,frame+1,{subtitleId:key});
      subtitleMap.set(key,record);
      const plate=group.querySelector('[data-subtitle-plate]');
      const number=name=>Number(plate.getAttribute(name));
      const rect={x:number('x'),y:number('y'),width:number('width'),height:number('height'),
        rx:number('rx'),fill:plate.getAttribute('fill'),opacity:number('fill-opacity')};
      const crop={x:Math.floor(rect.x),y:Math.floor(rect.y),
        width:Math.ceil(rect.x+rect.width)-Math.floor(rect.x),
        height:Math.ceil(rect.y+rect.height)-Math.floor(rect.y)};
      plates.push({id:id+'_plate',subtitleId:key,startFrame:frame,endFrameExclusive:frame+1,
        ...crop,rect,svg:plate.outerHTML});
    } else subtitleMap.get(key).endFrameExclusive=frame+1;
  }
  for(const plate of plates)plate.endFrameExclusive=subtitleMap.get(plate.subtitleId).endFrameExclusive;
  return {overlay_texts:texts,subtitle_plates:plates};
}'''


RENDER_NON_TEXT_JS = r'''async frame => {
  const state=window.renderFrame(frame);
  document.querySelectorAll('svg text').forEach(el=>el.remove());
  document.querySelectorAll('[data-subtitle-id]').forEach(el=>el.remove());
  const img=document.getElementById('illustration');
  if(img.style.display!=='none')await img.decode();
  await document.fonts.ready;
  await new Promise(resolve=>requestAnimationFrame(resolve));
  return state;
}'''


def object_ids(scene):
    name=scene['asset']
    if scene['type']=='illustration':
        result=[f'assets/{name}.png', 'source/app.js::renderFrame/headerBg']
        if scene['start_frame']<119:
            result.append('source/app.js::illustrationOverlay/hook_wash')
        elif name=='open_study':
            result.append('source/app.js::illustrationOverlay/framework-label/rect')
        return result
    prefix=f'source/cards.js::{name}'
    result=[prefix+'/bg/base',prefix+'/bg/paper-pattern',prefix+'/bg/top-rule']
    if name=='quadrants':
        result += [prefix+'/center/outer-circle',prefix+'/center/inner-circle',
                   prefix+'/divider/vertical',prefix+'/divider/horizontal']
        for dimension in ['mind','body','spirit','career']:
            result += [prefix+f'/dimensions/{dimension}/{part}'
                       for part in ['clipped-slice','route','moving-dot','icon']]
    elif name=='prompt':
        result += [prefix+'/'+part for part in [
            'transfer/route','tray/back','document/shadow','document/page','document/fold',
            'document/accent','document/rule','tray/foreground-lip']]
        for dimension in ['mind','body','spirit','career']:
            result += [prefix+f'/dimensions/{dimension}/{part}'
                       for part in ['route-guide','route-active','moving-packet','packet-line','circle','icon']]
    elif name=='plan':
        result.append(prefix+'/shadow')
        for index in range(3):
            result += [prefix+f'/faces/{index}/'+part for part in ['page','icon']]
            if index>0: result.append(prefix+f'/faces/{index}/fold-shade')
    elif name=='choice':
        for dimension in ['mind','body','spirit','career']:
            result += [prefix+f'/dimensions/{dimension}/'+part for part in ['disc','icon','pulse-ring']]
        result += [prefix+'/'+part for part in ['collect/bracket','collect/stem','callout/plate']]
    return result


def main():
    import argparse
    global OUT, ORIGINAL, COPY, RENDERED
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=COPY if (COPY/'source/timeline.json').is_file() else ORIGINAL)
    parser.add_argument('--output',type=Path,default=OUT,help='New revision directory; existing renders are never overwritten')
    args=parser.parse_args()
    ORIGINAL=args.source.resolve()
    OUT=args.output.resolve()
    COPY=OUT/'source_render/original'
    RENDERED=OUT/'rendered'
    if COPY.exists() or RENDERED.exists():
        raise FileExistsError('Choose a new output directory; existing source/media will not be overwritten')
    from playwright.sync_api import sync_playwright
    scenes,cfg=prepare()
    catalog={
        'schemaVersion':1,'width':cfg['width'],'height':cfg['height'],'fps':cfg['fps'],
        'totalFrames':cfg['total_frames'],
        'sourceRevision':'identity_semantic_full_20261018_v2',
        'sourceCopy':'source_render/original',
        'generationOnly':True,
        'items':[],
        'sourceObjectIdScheme':'Stable renderer semantic source branches; icon IDs include their component SVG paths.',
        'notes':[
            'Source SVG text, spoken subtitle group and subtitle plate are removed before media capture.',
            'Opening wash, study label plate and illustration brand plate remain in illustration PNG assets.',
            'All card nontext states are generated directly from source renderFrame at original integer frames.',
            'Prompt foreground tray lip occludes document text in source; a base-only composite cannot reproduce that occlusion over native text without a separate treatment.',
            'Plan source text follows clipped affine/skew page transforms; native text treatment is delegated to draft packaging.',
            'Native overlay x/y values are raw SVG getBBox plus getCTM center positions, with no font mapping compensation.',
            'No verification, comparison, calibration, output decode, playback, or native-editor action is included.'
        ]}
    started=time.monotonic()
    with serve() as url, sync_playwright() as playwright:
        browser=playwright.chromium.launch(channel='chrome',headless=True,args=[
            '--hide-scrollbars','--force-color-profile=srgb',
            '--disable-background-timer-throttling','--disable-renderer-backgrounding'])
        try:
            page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
            page.set_default_timeout(60000)
            page.goto(url,wait_until='domcontentloaded')
            page.evaluate('async()=>{await window.ready;await document.fonts.ready;}')
            measured=page.evaluate(MEASURE_JS,{'totalFrames':cfg['total_frames'],'fps':cfg['fps'],'scenes':scenes})
            catalog['overlay_texts']=measured['overlay_texts']
            catalog['subtitle_plates']=measured['subtitle_plates']
            json_write(RENDERED/'overlay_texts.json',catalog['overlay_texts'])
            # Separate transparent plates are directly rasterized from the source
            # rect markup, using its measured crop and its original subpixel x.
            transparent=page.add_style_tag(content='html,body,#stage{background:transparent!important}')
            for plate in catalog['subtitle_plates']:
                page.evaluate('svg=>{document.getElementById("illustration").style.display="none";document.getElementById("graphics").innerHTML="";document.getElementById("overlay").innerHTML=svg;}',plate.pop('svg'))
                rel=f'rendered/subtitle_plates/subtitle_{plate["subtitleId"]:02d}.png'
                plate['path']=rel
                page.screenshot(path=str(OUT/rel),type='png',omit_background=True,
                    clip={key:plate[key] for key in ['x','y','width','height']},caret='hide')
            transparent.evaluate('(el)=>el.remove()')
            json_write(RENDERED/'subtitle_plates.json',catalog['subtitle_plates'])
            print(f'Generated {len(catalog["overlay_texts"])} measured overlay records and {len(catalog["subtitle_plates"])} plates',flush=True)
            for scene in scenes:
                name=scene['id']; count=scene['end_frame_exclusive']-scene['start_frame']
                ext='png' if scene['type']=='illustration' else 'mp4'
                category='illustrations' if scene['type']=='illustration' else 'cards'
                rel=f'rendered/{category}/{name}.{ext}'
                item={'id':name,'type':scene['type'],'path':rel,
                    'startFrame':scene['start_frame'],'endFrameExclusive':scene['end_frame_exclusive'],
                    'width':1920,'height':1080,'sourceObjectIds':object_ids(scene)}
                if scene['type']=='illustration':
                    page.evaluate(RENDER_NON_TEXT_JS,scene['start_frame'])
                    page.screenshot(path=str(OUT/rel),type='png',caret='hide')
                else:
                    item.update({'fps':cfg['fps'],'frameCount':count,'hasAudio':False,
                                 'composition':'all original nontext vector layers merged'})
                    video=cfg['video']
                    command=[str(cfg['ffmpeg']),'-hide_banner','-loglevel','warning','-nostats','-n',
                        '-f','image2pipe','-vcodec','png','-framerate',str(cfg['fps']),'-i','pipe:0',
                        '-an','-c:v',video['codec'],'-crf',str(video['crf']),'-preset',video['preset'],
                        '-pix_fmt',video['pixel_format'],'-frames:v',str(count),'-movflags','+faststart',str(OUT/rel)]
                    with (HERE/f'encode_{name}.log').open('xb') as log:
                        process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,
                            stderr=log,creationflags=NO_WINDOW)
                        try:
                            for index,frame in enumerate(range(scene['start_frame'],scene['end_frame_exclusive']),1):
                                page.evaluate(RENDER_NON_TEXT_JS,frame)
                                process.stdin.write(page.screenshot(type='png',caret='hide'))
                                if index%60==0:
                                    print(f'{name}: generated {index}/{count} source frames',flush=True)
                            process.stdin.close()
                            status=process.wait(timeout=180)
                            if status:raise RuntimeError(f'Encoder failed for {name}: {status}')
                        except BaseException:
                            if process.poll() is None:process.terminate();process.wait(timeout=15)
                            raise
                catalog['items'].append(item)
                print(f'Generated {rel} for {scene["start_frame"]}..{scene["end_frame_exclusive"]}',flush=True)
            catalog['generationSeconds']=round(time.monotonic()-started,2)
            json_write(RENDERED/'catalog.json',catalog)
            print(json.dumps({'catalog':str(RENDERED/'catalog.json'),'items':len(catalog['items']),
                'overlayTexts':len(catalog['overlay_texts']),'subtitlePlates':len(catalog['subtitle_plates']),
                'seconds':catalog['generationSeconds']},ensure_ascii=False),flush=True)
        finally:
            browser.close()


if __name__=='__main__':
    import sys
    for stream in [sys.stdout,sys.stderr]:
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8',errors='replace')
    main()
