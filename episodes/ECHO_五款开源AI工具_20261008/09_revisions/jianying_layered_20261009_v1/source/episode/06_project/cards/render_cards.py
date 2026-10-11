"""Render this episode's SVG cards, with actual encoded process-frame checks."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse,json,hashlib,subprocess,sys
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent;EP=ROOT.parents[1]
DATA=json.loads((EP/'03_storyboard/cards.json').read_text(encoding='utf-8'));CFG=json.loads((EP/'00_brief/effective_defaults.json').read_text(encoding='utf-8'))
FPS=DATA['fps'];WIDTH=DATA['width'];HEIGHT=DATA['height'];FFMPEG=CFG['tools_local']['ffmpeg'];FFPROBE=str(Path(FFMPEG).with_name('ffprobe.exe'))
OUT=EP/'06_project/render';QC=EP/'08_qc/cards'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
def call(cmd):return subprocess.check_output(cmd,stderr=subprocess.STDOUT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def delta(a,b):return sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
def sheet(c,frames,qc,name):
 rows=(len(frames)+2)//3;im=Image.new('RGB',(1568,60+rows*328),'#E7ECE5');draw=ImageDraw.Draw(im);font=ImageFont.truetype(CFG['type']['regular_font'],21);draw.text((15,12),c['id']+' · '+c['title'],font=font,fill='#12251A')
 for i,f in enumerate(frames):
  x=10+i%3*520;y=50+i//3*328;pic=Image.open(qc/f'f{f:04d}.png').convert('RGB');pic.thumbnail((512,288));im.paste(pic,(x,y));draw.text((x,y+291),f'local {f}  /  global {c["start_frame"]+f}  /  {f/FPS:.2f}s',font=font,fill='#12251A')
 im.save(qc/name)
def render(c,url,samples_only,verify_existing=False):
 sid=c['id'];qc=QC/sid;qc.mkdir(parents=True,exist_ok=True);n=c['frame_count'];events=c['process_events'];wanted=sorted(set(c['overview_frames']+[f for e in events for f in e['check_frames']]))
 r={'id':sid,'start_frame':c['start_frame'],'end_frame_exclusive':c['end_frame_exclusive'],'frame_count':n,'fps':FPS,'sample_frames':wanted,'text_overflow':[],'source_sample_motion':[]};errors=[]
 with sync_playwright() as pw:
  b=pw.chromium.launch(channel=CFG['tools_local']['browser_channel'],headless=True,args=['--hide-scrollbars','--disable-background-timer-throttling','--disable-features=PaintHolding']);page=b.new_page(viewport={'width':WIDTH,'height':HEIGHT},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url+'?card='+sid);page.wait_for_function('window.cardMotionReady===true',timeout=30000);assert not page.evaluate('window.assetErrors||[]'),page.evaluate('window.assetErrors')
  for f in wanted:
   page.evaluate('f=>window.renderFrame(f)',f);page.screenshot(path=str(qc/f'f{f:04d}.png'))
   r['text_overflow']+=page.evaluate("()=>[...document.querySelectorAll('text')].filter(el=>{let a=1,e=el;while(e){a*=+(e.getAttribute?.('opacity')??1);e=e.parentElement;}if(a<.02)return false;const r=el.getBoundingClientRect();return r.left<58||r.right>1862||r.top<45||r.bottom>1032}).map(el=>({text:el.textContent,bounds:el.getBoundingClientRect().toJSON()}))")
  f=wanted[len(wanted)//2];page.evaluate('f=>window.renderFrame(f)',f);r['deterministic']=page.screenshot()==(qc/f'f{f:04d}.png').read_bytes();assert r['deterministic'],sid+' nondeterminism';assert not r['text_overflow'],(sid,r['text_overflow']);assert not errors,errors
  if not samples_only:
   dest=OUT/f'{sid}.mp4'
   if not verify_existing:
    cmd=[FFMPEG,'-y','-hide_banner','-loglevel','error','-f','image2pipe','-vcodec','png','-framerate',str(FPS),'-i','pipe:0','-an','-frames:v',str(n),'-c:v','libx264','-threads','2','-preset',CFG['video']['preset'],'-crf',str(CFG['video']['crf']),'-vf','scale=1920:1080:out_color_matrix=bt709:out_range=tv,format=yuv420p','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-r',str(FPS),'-video_track_timescale','15360','-movflags','+faststart',str(dest)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
     static_png=(qc/'f0000.png').read_bytes() if sid.startswith('A') else None
     for f in range(n):
      if static_png is None:
       page.evaluate('f=>window.renderFrame(f)',f);proc.stdin.write(page.screenshot(type='png'))
      else:proc.stdin.write(static_png)
      if f and f%120==0:print(f'{sid}: {f}/{n}',flush=True)
     proc.stdin.close();err=proc.stderr.read().decode('utf-8',errors='replace');code=proc.wait();assert code==0,err
    except BaseException:proc.kill();raise
   streams=json.loads(call([FFPROBE,'-v','error','-show_streams','-of','json',str(dest)]))['streams'];v=streams[0];assert len(streams)==1 and int(v['nb_frames'])==n and v['width']==WIDTH and v['height']==HEIGHT,(sid,streams);call([FFMPEG,'-v','error','-i',str(dest),'-f','null','-'])
   assert all(v.get(k)==val for k,val in [('color_primaries','bt709'),('color_transfer','bt709'),('color_space','bt709'),('color_range','tv')]),v
   r.update(path=str(dest.relative_to(EP)),sha256=sha(dest),bytes=dest.stat().st_size,codec=v['codec_name'],pixel_format=v['pix_fmt'],stream_count=len(streams),decode='passed',color_primaries=v['color_primaries'],color_transfer=v['color_transfer'],color_space=v['color_space'],color_range=v['color_range'],rgb_to_yuv_filter='scale=1920:1080:out_color_matrix=bt709:out_range=tv,format=yuv420p')
   mids=sorted(set(max(0,min(n-1,e['check_frames'][1]+d)) for e in events for d in [-1,0,1]));ed=qc/'encoded';ed.mkdir(exist_ok=True);filt='select='+ '+'.join('eq(n\\,'+str(f)+')' for f in mids)
   call([FFMPEG,'-y','-hide_banner','-loglevel','error','-i',str(dest),'-vf',filt,'-vsync','0',str(ed/'frame_%04d.png')]);encoded={f:ed/f'frame_{i+1:04d}.png' for i,f in enumerate(mids)};r['encoded_midpoint_neighbors']=[]
   for e in events:
    mid=e['check_frames'][1];fs=[max(0,min(n-1,mid+d)) for d in [-1,0,1]];ims=[Image.open(encoded[x]).convert('RGB') for x in fs];r['encoded_midpoint_neighbors'].append({'event':e['id'],'frames':fs,'mean_rgb_delta':[delta(ims[i],ims[i+1]) for i in [0,1]],'pixel_change_only':True})
   (ed/'frame_mapping.json').write_text(json.dumps({str(k):v.name for k,v in encoded.items()},indent=2),encoding='utf-8')
  b.close()
 for e in events:
  fs=e['check_frames'];ims=[Image.open(qc/f'f{f:04d}.png').convert('RGB') for f in fs];r['source_sample_motion'].append({'event':e['id'],'check_frames':fs,'mean_rgb_delta':[delta(ims[i],ims[i+1]) for i in [0,1]],'meaning':e['meaning'],'pixel_change_only':True})
 sheet(c,c['overview_frames'],qc,'overview.png');sheet(c,[f for e in events for f in e['check_frames']],qc,'process.png');(qc/('samples.json' if samples_only else 'render_check.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(sid+' completed '+('samples' if samples_only else 'video'),flush=True);return r
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--samples',action='store_true');ap.add_argument('--verify-existing',action='store_true');ap.add_argument('--cards',nargs='*');ap.add_argument('--workers',type=int,default=2);args=ap.parse_args();
 OUT.mkdir(parents=True,exist_ok=True);QC.mkdir(parents=True,exist_ok=True);server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(EP)));Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/06_project/cards/card_scene.html';result=[]
 try:
  with ThreadPoolExecutor(max_workers=args.workers) as pool:
   for job in as_completed([pool.submit(render,c,url,args.samples,args.verify_existing) for c in DATA['cards'] if not args.cards or c['id'] in args.cards]):result.append(job.result())
 finally:server.shutdown()
 result.sort(key=lambda x:x['start_frame']);(QC/('sample_manifest.json' if args.samples else 'frame_manifest.json')).write_text(json.dumps({'revision':DATA['revision'],'fps':FPS,'width':WIDTH,'height':HEIGHT,'total_card_frames':sum(c['frame_count'] for c in result),'cards':result},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'cards':len(result),'frames':sum(c['frame_count'] for c in result),'samples_only':args.samples}))
if __name__=='__main__':main()
