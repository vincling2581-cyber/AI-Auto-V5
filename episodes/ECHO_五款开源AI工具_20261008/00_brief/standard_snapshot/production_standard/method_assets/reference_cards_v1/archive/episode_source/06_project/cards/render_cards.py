"""Render actual continuous intermediate SVG frames to silent H264 card segments.
Usage: python render_cards.py [--samples] [--cards C02 C04] [--workers 2]
Requires local Chrome, Playwright, Pillow, FFmpeg; no Internet or editor UI.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import argparse,hashlib,json,subprocess,time
from PIL import Image,ImageDraw,ImageFont,ImageChops
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
EP=ROOT.parents[1]
DATA=json.loads((EP/'03_storyboard/cards.json').read_text(encoding='utf-8'))
DEFAULTS=json.loads((EP/'00_brief/standard_snapshot/production_standard/defaults.json').read_text(encoding='utf-8'))
FFMPEG=DEFAULTS['tools_local']['ffmpeg']; FFPROBE=str(Path(FFMPEG).with_name('ffprobe.exe'))
OUT=EP/'04_assets/cards'; QC=EP/'08_qc/cards'
FONT=ImageFont.truetype(DEFAULTS['type']['regular_font'],23)
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass

def render(card,url,samples_only):
    sid=card['id'];frames=card['frame_count'];errors=[];samples=card['sample_frames']
    checks={'id':sid,'start_frame':card['start_frame'],'end_frame_exclusive':card['end_frame_exclusive'],'frames':frames,'samples':samples,'text_overflow':[]}
    qc=QC/sid;qc.mkdir(parents=True,exist_ok=True)
    begin=time.monotonic()
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True,args=['--hide-scrollbars','--disable-background-timer-throttling'])
        page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url+'?card='+sid)
        page.wait_for_function('window.cardMotionReady===true')
        for f in samples:
            page.evaluate('f=>window.renderFrame(f)',f)
            page.screenshot(path=str(qc/f'f{f:04}.png'))
            overflow=page.evaluate('''()=>[...document.querySelectorAll('text')].filter(el=>{
              if(+getComputedStyle(el).opacity===0)return false;
              let e=el;while(e){if(e.tagName==='g'&&+(e.getAttribute('opacity')||1)===0)return false;e=e.parentElement}
              const r=el.getBoundingClientRect();return r.left<60||r.right>1860||r.top<16||r.bottom>916
            }).map(el=>({text:el.textContent,bounds:el.getBoundingClientRect().toJSON()}))''')
            checks['text_overflow']+=overflow
        f=samples[2]
        page.evaluate('f=>window.renderFrame(f)',f)
        assert page.screenshot()==(qc/f'f{f:04}.png').read_bytes(),sid+': arbitrary frame nondeterminism'
        checks['arbitrary_frame_order']='passed'
        assert not checks['text_overflow'],(sid,checks['text_overflow'])
        if not samples_only:
            command=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','image2pipe','-vcodec','png','-framerate','30','-i','pipe:0','-an','-frames:v',str(frames),'-c:v','libx264','-preset',DEFAULTS['video']['preset'],'-crf',str(DEFAULTS['video']['crf']),'-pix_fmt','yuv420p','-r','30','-video_track_timescale','15360','-movflags','+faststart',str(OUT/f'{sid}.mp4')]
            proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                for f in range(frames):
                    page.evaluate('f=>window.renderFrame(f)',f)
                    proc.stdin.write(page.screenshot(type='png'))
                    if f and f%120==0:print(f'{sid}: {f}/{frames}',flush=True)
                proc.stdin.close();err=proc.stderr.read().decode('utf-8',errors='replace');code=proc.wait()
                assert code==0,err
            except BaseException:
                proc.kill();raise
        assert not errors,errors
        browser.close()
    sheet=Image.new('RGB',(1440,908),'#F5F2E9');draw=ImageDraw.Draw(sheet)
    draw.text((16,12),sid+'  '+card['title'],font=FONT,fill='#24362B')
    for i,f in enumerate(samples):
        im=Image.open(qc/f'f{f:04}.png').convert('RGB');im.thumbnail((700,394))
        # Six frames, 3 columns; all labels identify exact local frames.
        im=im.resize((464,261));x=16+(i%3)*478;y=66+(i//3)*322
        sheet.paste(im,(x,y));draw.text((x,y+268),f'f{f} / {f/30:.2f}s',font=FONT,fill='#24362B')
    sheet=sheet.crop((0,0,1440,738));sheet.save(QC/f'{sid}_过程帧.jpg',quality=94)
    if not samples_only:
        video=OUT/f'{sid}.mp4'
        probe=json.loads(subprocess.check_output([FFPROBE,'-v','error','-count_frames','-show_streams','-of','json',str(video)]))
        vs=probe['streams'][0]
        assert len(probe['streams'])==1 and vs['codec_name']=='h264'
        assert (vs['width'],vs['height'],vs['r_frame_rate'],vs['pix_fmt'],vs['time_base'])==(1920,1080,'30/1','yuv420p','1/15360')
        assert int(vs['nb_read_frames'])==frames
        # Extract encoded process midpoints and compare to generated frame pixels.
        checks['encoded_midframes']=[]
        import numpy as np
        for ev in card['process_events']:
            f=ev['check_frames'][1]
            target=qc/f'encoded_f{f:04}.png'
            raw=subprocess.check_output([FFMPEG,'-v','error','-i',str(video),'-vf',f'select=between(n\\,{f-1}\\,{f+1}),format=rgb24','-vsync','0','-frames:v','3','-f','rawvideo','pipe:1'])
            triplet=np.frombuffer(raw,dtype=np.uint8).reshape(3,1080,1920,3)
            delta=[float(np.abs(triplet[i].astype(np.int16)-triplet[i+1].astype(np.int16)).mean()) for i in (0,1)]
            assert min(delta)>0,(sid,ev['target_ids'],'encoded process has identical neighboring frames')
            Image.fromarray(triplet[1]).save(target)
            checks['encoded_midframes'].append({'frame':f,'event':ev['target_ids'],'file':str(target.relative_to(EP)),'adjacent_frame_mean_difference':delta,'interpretation':'配合事件几何与图证验证过程；像素变化本身不等于语义质量通过'})
        subprocess.run([FFMPEG,'-v','error','-i',str(video),'-f','null','-'],check=True)
        checks['stream']=vs;checks['sha256']=hashlib.sha256(video.read_bytes()).hexdigest();checks['video']=str(video.relative_to(EP));checks['decode']='passed';checks['full_speed_subjective_playback']='not_performed';checks['continuous_render']='all frames rendered and encoded, not stills concat'
    checks['seconds_elapsed']=round(time.monotonic()-begin,2)
    (qc/('samples.json' if samples_only else 'render.json')).write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    print(sid+': '+('samples ready' if samples_only else 'encoded/decoded/frame-count checked'),flush=True)
    return checks

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--samples',action='store_true');ap.add_argument('--cards',nargs='*');ap.add_argument('--workers',type=int,default=2);args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);QC.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(EP)));Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/06_project/cards/card_scene.html'
    results=[]
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            jobs=[pool.submit(render,c,url,args.samples) for c in DATA['cards'] if not args.cards or c['id'] in args.cards]
            for job in as_completed(jobs):results.append(job.result())
    finally:server.shutdown()
    name='samples.json' if args.samples else 'render_check.json'
    (QC/name).write_text(json.dumps(sorted(results,key=lambda x:x['id']),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'cards':len(results),'frames':sum(x['frames'] for x in results),'mode':name},ensure_ascii=False))
if __name__=='__main__':main()
