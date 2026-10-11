from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,hashlib,argparse,shutil
R=Path(__file__).resolve().parent;S=R/'source/episode';D=json.loads((S/'03_storyboard/cards.json').read_text(encoding='utf-8'))
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cards',nargs='*');ap.add_argument('--quick',action='store_true');args=ap.parse_args()
 shutil.copy2(R/'adapter/export_page.html',S/'06_project/cards/export_page.html')
 srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(R)));Thread(target=srv.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   b=pw.chromium.launch(channel='chrome',headless=True);p=b.new_page(viewport={'width':1920,'height':1080});errs=[];p.on('pageerror',lambda e:errs.append(str(e)))
   for c in D['cards']:
    if args.cards and c['id'] not in args.cards:continue
    sid=c['id'];p.goto(f'http://127.0.0.1:{srv.server_port}/source/episode/06_project/cards/export_page.html?card={sid}');p.wait_for_function('window.cardMotionReady===true');catalog={};tc={};textrows=[]
    frames=range(c['frame_count']) if not args.quick else sorted(set(c['overview_frames']+[f for e in c['process_events'] for f in e['check_frames']]))
    for f in frames:
     p.evaluate('f=>renderFrame(f)',f);row=p.evaluate('async()=>{const r=await exportRaw();delete r.source;for(const x of r.objects)delete x.svg;return r;}')
     for x in row['objects']:
      cat=catalog.setdefault(x['id'],{k:v for k,v in x.items() if k!='svg'}|{'first_frame':f,'last_frame':f,'bounds':[]});cat['last_frame']=f
      if x['alpha']>0.01 and (x['box']['width']>0 or x['box']['height']>0):cat['bounds'].append(x['box'])
     for x in row['texts']:
      cat=tc.setdefault(x['id'],{**x,'first_frame':f,'last_frame':f});cat['last_frame']=f
     textrows.append({'frame':c['start_frame']+f,'texts':row['texts']})
     if f%120==0:print(sid,f,'/',c['frame_count'],flush=True)
    assert not errs,errs
    for cat in catalog.values():
     bs=cat.pop('bounds');cat['visible_union']=None if not bs else {'x':min(x['x'] for x in bs),'y':min(x['y'] for x in bs),'right':max(x['x']+x['width'] for x in bs),'bottom':max(x['y']+x['height'] for x in bs)}
    save(R/'catalog'/f'{sid}.json',{'id':sid,'full_scan':not args.quick,'objects':list(catalog.values()),'texts':list(tc.values())})
    if not args.quick:save(R/'card_text'/f'{sid}.json',textrows)
    print(sid,'catalog',len(catalog),'graphics',len(tc),'texts',flush=True)
   b.close()
 finally:srv.shutdown()
if __name__=='__main__':main()
