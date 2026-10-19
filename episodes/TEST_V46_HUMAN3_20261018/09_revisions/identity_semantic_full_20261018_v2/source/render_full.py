#!/usr/bin/env python3
"""Independent full revision renderer. Writes only new run directories."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent
EPISODE = ROOT.parents[1]
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
CFG = json.loads((SOURCE / 'config.json').read_text(encoding='utf-8-sig'))
SCENES = json.loads((SOURCE / 'timeline.json').read_text(encoding='utf-8-sig'))
FFMPEG = Path(CFG['ffmpeg'])
FFPROBE = FFMPEG.with_name('ffprobe.exe' if os.name == 'nt' else 'ffprobe')
ORIGINAL = EPISODE / CFG['original_video']
FPS, COUNT = CFG['fps'], CFG['total_frames']
FILENAME = 'HUMAN3_角色与语义插画修订完整版_1080p.mp4'
CARD_FRAMES = {
    'quadrants': [312, 386, 410, 449, 488, 524],
    'prompt': [744, 831, 845, 869, 890, 924, 946],
    'plan': [1198, 1225, 1246, 1260, 1287, 1318],
    'choice': [1446, 1504, 1537, 1573, 1592, 1610, 1632, 1677],
}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_new(path, content):
    mode = 'xb' if isinstance(content, bytes) else 'x'
    with Path(path).open(mode, **({} if mode == 'xb' else {'encoding': 'utf-8'})) as stream:
        stream.write(content)


def json_new(path, value):
    write_new(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def run(command, log, timeout=180):
    command = [str(x) for x in command]
    log.write(json.dumps(command, ensure_ascii=False) + '\n'); log.flush()
    result = subprocess.run(command, capture_output=True, creationflags=NO_WINDOW, timeout=timeout)
    if result.stderr:
        log.write(result.stderr.decode('utf-8', errors='replace') + '\n'); log.flush()
    if result.returncode:
        raise RuntimeError(f'Command failed ({result.returncode}); see {log.name}')
    return result.stdout


def ffmpeg(args, log, timeout=180):
    return run([FFMPEG, '-hide_banner', '-loglevel', 'warning', '-nostats', '-n', *args], log, timeout)


def parse_srt(path):
    def sec(text):
        h, m, s, ms = map(int, re.split('[:,]', text))
        return h * 3600 + m * 60 + s + ms / 1000
    blocks = re.split(r'\r?\n\s*\r?\n', path.read_text(encoding='utf-8-sig').strip())
    result = []
    for block in blocks:
        lines = block.splitlines()
        start, end = lines[1].split(' --> ')
        result.append({'id': int(lines[0]), 'start': sec(start), 'end': sec(end), 'text': '\n'.join(lines[2:])})
    return result


def preflight(require_assets=False):
    from PIL import Image
    if (CFG['width'], CFG['height'], FPS, COUNT) != (1920, 1080, 30, 1678):
        raise ValueError('Required dimensions / fps / total frames changed')
    for path, expected in CFG['baseline_hashes'].items():
        if digest(EPISODE / path) != expected:
            raise ValueError(f'Original dependency changed: {path}')
    copies = [('cards.js', '06_project/cards.js'), ('effective_defaults.json', '00_brief/effective_defaults.json'),
              ('subtitles.json', '02_timing/subtitles.json'), ('original.srt', CFG['original_srt'])]
    for local, old in copies:
        if digest(SOURCE / local) != digest(EPISODE / old):
            raise ValueError(f'Reused source copy differs: {local}')
    subs = json.loads((SOURCE / 'subtitles.json').read_text(encoding='utf-8-sig'))
    if subs != parse_srt(SOURCE / 'original.srt'):
        raise ValueError('Subtitle JSON differs from exact SRT text or timing')
    cursor = 0
    old_scenes = json.loads((EPISODE / '03_storyboard/scenes.json').read_text(encoding='utf-8-sig'))
    old_cards = {s['asset']: s for s in old_scenes if s['type'] == 'card'}
    for scene in SCENES:
        if scene['start_frame'] != cursor or scene['end_frame_exclusive'] <= cursor:
            raise ValueError('Timeline gap, overlap, or empty segment')
        cursor = scene['end_frame_exclusive']
        if scene['type'] == 'card':
            old = old_cards[scene['asset']]
            if any(scene[k] != old[k] for k in ['start_frame', 'end_frame_exclusive']):
                raise ValueError('Card scene timing changed')
    if cursor != COUNT or {s['asset'] for s in SCENES if s['type'] == 'card'} != set(CARD_FRAMES):
        raise ValueError('Incomplete full timeline or wrong card set')
    missing, images = [], []
    for scene in SCENES:
        if scene['type'] != 'illustration':
            continue
        path = ROOT / scene['asset_path']
        if not path.is_file():
            missing.append(scene['asset_path']); continue
        with Image.open(path) as im:
            size = im.size
            aspect_error = abs((size[0] / size[1]) / (16 / 9) - 1)
            if aspect_error > .002:
                raise ValueError(f'Illustration aspect differs from 16:9 by more than approved 0.2%: {path.name}, {size}')
            im.verify()
        images.append({'path': scene['asset_path'], 'size': size, 'aspect_error_fraction': aspect_error,
                       'display': 'stable full-frame cover; no animated zoom or pan', 'sha256': digest(path)})
    if require_assets and missing:
        raise FileNotFoundError('Missing illustrations: ' + ', '.join(missing))
    for path in [FFMPEG, FFPROBE, Path('C:/Windows/Fonts/msyh.ttc'), Path('C:/Windows/Fonts/msyhbd.ttc')]:
        if not path.is_file(): raise FileNotFoundError(path)
    return {'status': 'ready' if not missing else 'waiting_assets', 'segments': len(SCENES),
            'illustration_count': len(images), 'missing_assets': missing, 'images': images,
            'subtitle_count': len(subs), 'subtitle_text_and_timing': 'identical_to_original_srt',
            'cards_code_defaults_and_timing': 'identical_to_original_sources',
            'card_visual_acceptance_inherited': False}


def frame_groups():
    illustrations = [(s['start_frame'] + s['end_frame_exclusive'] - 1) // 2
                     for s in SCENES if s['type'] == 'illustration']
    joins = [f for s in SCENES[1:] for f in [s['start_frame'] - 1, s['start_frame']]]
    return {'illustrations': illustrations, 'joins': joins, 'cards': sum(CARD_FRAMES.values(), [])}


@contextmanager
def server():
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True); thread.start()
    try:
        yield f'http://127.0.0.1:{httpd.server_port}/source/index.html'
    finally:
        httpd.shutdown(); httpd.server_close(); thread.join(timeout=2)


RENDER_JS = '''async frame=>{
  const result=window.renderFrame(frame);
  const im=document.getElementById('illustration');
  if(im.style.display!=='none')await im.decode();
  await document.fonts.ready;
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  const group=document.querySelector('[data-subtitle-id]');
  if(group){
    const plate=group.querySelector('rect'),text=group.querySelector('text');
    const center=+plate.getAttribute('x')+(+plate.getAttribute('width'))/2;
    if(center!==960||+plate.getAttribute('y')!==947||+text.getAttribute('x')!==960||+text.getAttribute('y')!==1004||text.getAttribute('text-anchor')!=='middle')throw new Error('Subtitle position changed');
    result.subtitle_center_x=center;result.subtitle_plate_y=947;
  }
  if(result.type==='card')result.card_svg=document.getElementById('graphics').innerHTML;
  return result;
}'''


def capture(out, qa, log, mode):
    from playwright.sync_api import sync_playwright
    errors, timeline = [], []
    frames = range(COUNT) if mode == 'render' else sorted(set(sum(frame_groups().values(), [])))
    with server() as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='chrome', headless=True, args=[
            '--hide-scrollbars', '--force-color-profile=srgb',
            '--disable-background-timer-throttling', '--disable-renderer-backgrounding'])
        try:
            version = browser.version
            page = browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda message: errors.append(message.text) if message.type=='error' else None)
            page.set_default_timeout(60000)
            page.goto(url, wait_until='domcontentloaded')
            page.evaluate('async()=>{await window.ready;await document.fonts.ready;}')
            process = None
            if mode == 'render':
                v = CFG['video']
                command = [str(FFMPEG),'-hide_banner','-loglevel','warning','-nostats','-n',
                           '-f','image2pipe','-vcodec','mjpeg','-framerate',str(FPS),'-i','pipe:0',
                           '-an','-c:v',v['codec'],'-crf',str(v['crf']),'-preset',v['preset'],
                           '-pix_fmt',v['pixel_format'],'-frames:v',str(COUNT),'-movflags','+faststart',
                           str(out/'picture_silent.mp4')]
                log.write(json.dumps(command,ensure_ascii=False)+'\n');log.flush()
                encoder_log=(qa/'encode.log').open('xb')
                process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,
                                         stderr=encoder_log,creationflags=NO_WINDOW)
            else:
                (qa/'composed').mkdir()
            started = time.monotonic()
            try:
                for i,frame in enumerate(frames,1):
                    result=page.evaluate(RENDER_JS,frame)
                    if errors: raise RuntimeError('Browser errors: '+' | '.join(errors))
                    if 'card_svg' in result:
                        result['card_svg_sha256']=hashlib.sha256(result.pop('card_svg').encode()).hexdigest()
                    timeline.append(result)
                    if process:
                        if process.poll() is not None:raise RuntimeError('Encoder stopped early')
                        process.stdin.write(page.screenshot(type='jpeg',quality=94,caret='hide'))
                    else:
                        write_new(qa/'composed'/f'frame_{frame:04d}.png',page.screenshot(type='png',caret='hide'))
                    if i%300==0:
                        print(f'Rendered {i}/{len(frames)} frames in {time.monotonic()-started:.1f}s',flush=True)
                if process:
                    process.stdin.close()
                    if process.wait(timeout=180):raise RuntimeError('Video encoding failed')
            except BaseException:
                if process and process.poll() is None:
                    process.terminate();process.wait(timeout=15)
                raise
            finally:
                if process:
                    if process.stdin and not process.stdin.closed:
                        try:process.stdin.close()
                        except (BrokenPipeError,OSError):pass
                    encoder_log.close()
        finally:
            browser.close()
    json_new(qa/'render_timeline.json',timeline)
    return {'browser_errors':errors,'frames':len(timeline),'chrome_version':version,
            'subtitle_center_checked_on_every_captioned_frame':True}


def packet_report(path, log):
    return json.loads(run([FFPROBE,'-v','error','-select_streams','a:0','-show_packets',
                         '-show_data_hash','sha256','-show_entries',
                         'packet=pts,dts,duration,size,data_hash,side_data_list','-of','json',path],log))


def make_sheets(qa, directory, label):
    from PIL import Image, ImageDraw, ImageFont
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
    records=[]
    for group,frames in frame_groups().items():
        cols=3 if group=='illustrations' else 4
        cell_w,cell_h=480,300
        sheet=Image.new('RGB',(cols*cell_w,((len(frames)+cols-1)//cols)*cell_h),'#f5f2e9')
        draw=ImageDraw.Draw(sheet)
        for i,frame in enumerate(frames):
            scene=next(s for s in SCENES if s['start_frame']<=frame<s['end_frame_exclusive'])
            x,y=(i%cols)*cell_w,(i//cols)*cell_h
            path=directory/f'frame_{frame:04d}.png'
            with Image.open(path) as im:sheet.paste(im.resize((480,270)),(x,y+30))
            draw.text((x+8,y+2),f'{frame:04d} | {scene["asset"]}',font=font,fill='#24443c')
            records.append({'frame':frame,'scene':scene['asset'],'group':group,'path':str(path.relative_to(ROOT)),
                            'sha256':digest(path)})
        target=qa/f'{label}_{group}.jpg'
        if target.exists():raise FileExistsError(target)
        sheet.save(target,quality=94)
    json_new(qa/f'{label}_frame_index.json',records)


def validate(output, qa, log, rendered):
    media=json.loads(run([FFPROBE,'-v','error','-show_streams','-show_format','-of','json',output],log))
    original_media=json.loads(run([FFPROBE,'-v','error','-show_streams','-show_format','-of','json',ORIGINAL],log))
    json_new(qa/'media.json',media)
    video=[s for s in media['streams'] if s['codec_type']=='video']
    audio=[s for s in media['streams'] if s['codec_type']=='audio']
    if not(len(video)==len(audio)==1 and video[0]['codec_name']=='h264' and video[0]['width']==1920
           and video[0]['height']==1080 and video[0]['r_frame_rate']=='30/1' and int(video[0]['nb_frames'])==COUNT):
        raise RuntimeError('Final video media properties failed')
    old_audio=next(s for s in original_media['streams'] if s['codec_type']=='audio')
    for field in ['codec_name','sample_rate','channels','time_base','start_pts','duration_ts']:
        if audio[0].get(field)!=old_audio.get(field):raise RuntimeError('Audio stream property changed: '+field)
    selected=sorted(set(sum(frame_groups().values(),[])))
    encoded=qa/'encoded';encoded.mkdir()
    selection='+'.join(f'eq(n\\,{frame})' for frame in selected)
    # One full decode of both streams; selected video frames are saved during it.
    run([FFMPEG,'-v','error','-xerror','-n','-i',output,'-map','0:v:0','-vf','select='+selection,
         '-fps_mode','vfr',encoded/'extract_%03d.png','-map','0:a:0','-f','null','-'],log)
    extracted=sorted(encoded.glob('extract_*.png'))
    if len(extracted)!=len(selected):raise RuntimeError('Encoded frame sample count mismatch')
    for frame,path in zip(selected,extracted):path.rename(encoded/f'frame_{frame:04d}.png')
    original_packets=packet_report(ORIGINAL,log)
    final_packets=packet_report(output,log)
    json_new(qa/'original_audio_packets.json',original_packets)
    json_new(qa/'final_audio_packets.json',final_packets)
    if original_packets!=final_packets:
        raise RuntimeError('Original and final audio packets or timestamps differ')
    make_sheets(qa,encoded,'encoded')
    return {'status':'passed','checked_at':datetime.now(timezone.utc).isoformat(),
            'output':str(output.relative_to(ROOT)),'sha256':digest(output),'bytes':output.stat().st_size,
            'media_properties':'passed','complete_audio_video_decode':'passed','render':rendered,
            'original_audio':{'packet_data_and_timestamps':'identical','packet_count':len(final_packets['packets']),
                              'codec':'copy','gain_speed_or_mixing_filters':False,
                              'entire_audio_track_preserved':True},
            'encoded_frames':{'count':len(selected),'all_12_illustrations':True,'all_15_joins_before_after':True,
                              'all_4_cards_process_states':True,'visual_review':'pending'},
            'full_speed_subjective_av':'not_performed','jianying_native_open_playback':'not_performed',
            'jianying_native_export':'not_performed','ae_project':'not_requested'}


def dependencies(log):
    files=[p for p in SOURCE.iterdir() if p.is_file()]
    files += [ROOT/s['asset_path'] for s in SCENES if s['type']=='illustration']
    files += [EPISODE/p for p in CFG['baseline_hashes']]
    files += [Path('C:/Windows/Fonts/msyh.ttc'),Path('C:/Windows/Fonts/msyhbd.ttc')]
    records=[{'path':str(p),'sha256':digest(p)} for p in sorted(set(files))]
    return {'files':records,'python':sys.version,'playwright':importlib.metadata.version('playwright'),
            'pillow':importlib.metadata.version('Pillow'),
            'ffmpeg_version':run([FFMPEG,'-version'],log).decode('utf-8',errors='replace').splitlines()[0],
            'ffmpeg_sha256':digest(FFMPEG),'ffprobe_sha256':digest(FFPROBE),
            'parameters':CFG,'rule_scope':'T01-T08, E01-E09, Q01-Q09 as applicable; current scoped user request prevails'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['preflight','preview','render'],default='preflight')
    parser.add_argument('--run',default='full_01')
    args=parser.parse_args()
    if args.mode=='preflight':
        print(json.dumps(preflight(),ensure_ascii=False,indent=2));return
    check=preflight(require_assets=True)
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.run):raise ValueError('Run name must be plain alphanumeric/underscore/hyphen')
    out,qa=ROOT/'exports'/args.run,ROOT/'qa'/args.run
    if out.exists() or qa.exists():raise FileExistsError('Run directory exists; use a new --run value')
    out.mkdir(parents=True);qa.mkdir(parents=True)
    with (qa/'pipeline.log').open('x',encoding='utf-8') as log:
        started=time.monotonic()
        try:
            json_new(qa/'preflight.json',check)
            deps=dependencies(log)
            json_new(qa/'dependencies_before.json',deps)
            rendered=capture(out,qa,log,args.mode)
            if args.mode=='preview':
                make_sheets(qa,qa/'composed','composed')
                report={'status':'composed_preview_ready','render':rendered,'visual_review':'pending',
                        'full_speed_subjective_av':'not_performed'}
            else:
                output=out/FILENAME
                ffmpeg(['-i',out/'picture_silent.mp4','-i',ORIGINAL,'-map','0:v:0','-map','1:a:0',
                        '-c:v','copy','-c:a','copy','-movflags','+faststart',output],log)
                report=validate(output,qa,log,rendered)
            for record in deps['files']:
                if digest(record['path'])!=record['sha256']:raise RuntimeError('Dependency changed during render: '+record['path'])
            deps['chrome_version']=rendered['chrome_version']
            json_new(qa/'dependencies_manifest.json',deps)
            report['dependencies_manifest_sha256']=digest(qa/'dependencies_manifest.json')
            json_new(qa/'machine_checks.json',report)
            print(json.dumps({'status':report['status'],'run':args.run,'qa':str(qa),
                              'output':report.get('output'),'seconds':round(time.monotonic()-started,1)},ensure_ascii=False),flush=True)
        except BaseException as error:
            import traceback
            log.write(traceback.format_exc());log.flush()
            json_new(qa/'failure.json',{'error':str(error),'partial_outputs_retained':True})
            raise


if __name__=='__main__':
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8',errors='replace')
    main()
