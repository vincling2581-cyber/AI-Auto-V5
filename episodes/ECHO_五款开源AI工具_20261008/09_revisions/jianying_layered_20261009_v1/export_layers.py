from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json,hashlib,argparse,shutil,sys,math,base64,subprocess,os
R=Path(__file__).resolve().parent;S=R/'source/episode'
sys.path.insert(0,str(R/'adapter'))
from classify import classify,panels
D=json.loads((S/'03_storyboard/cards.json').read_text(encoding='utf-8'))
FF=Path(os.environ.get('JY_EXPORT_FFMPEG') or shutil.which('ffmpeg') or r'D:\ffmpeg\bin\ffmpeg.exe')
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def make_plan():
 result={k:D[k] for k in ['fps','width','height']};result['cards']=[]
 for c in D['cards']:
  sid=c['id'];cat=json.loads((R/'catalog'/f'{sid}.json').read_text(encoding='utf-8'));assert cat['full_scan']
  ps=panels(sid);owners={p['owner']:p for p in ps};groups={}
  for obj in cat['objects']:
   rule=classify(sid,obj);key=rule['layer_key'];owner=rule['owner']
   layer=groups.setdefault(key,{'id':sid+'_'+key,**rule,'owner_label':owners.get(owner,{}).get('owner_label','全局'), 'slot':owners.get(owner,{}).get('slot',-1),'source_ids':[],'bounds':[]})
   assert (layer['owner'],layer['z'],layer['role'])==(owner,rule['z'],rule['role'])
   layer['source_ids'].append(obj['id'])
   if obj['visible_union']:layer['bounds'].append(obj['visible_union'])
  for l in groups.values():
   bs=l.pop('bounds');x=max(0,math.floor(min((b['x'] for b in bs),default=0)-4));y=max(0,math.floor(min((b['y'] for b in bs),default=0)-4));right=min(1920,math.ceil(max((b['right'] for b in bs),default=2)+4));bottom=min(1080,math.ceil(max((b['bottom'] for b in bs),default=2)+4))
   w=max(2,right-x);h=max(2,bottom-y);w+=w%2;h+=h%2
   if x+w>1920:x=1920-w
   if y+h>1080:y=1080-h
   l.update(crop=[x,y,w,h],width=w,height=h,x=x+w/2,y=y+h/2,start_frame=c['start_frame'],end_frame=c['end_frame_exclusive'])
  rows=json.loads((R/'card_text'/f'{sid}.json').read_text(encoding='utf-8'))
  for row in rows:
   for t in row['texts']:
    rule=classify(sid,t,True);t.update(owner=rule['owner'],z=rule['z'],native_z=rule['z'])
  save(R/'card_text'/f'{sid}.json',rows)
  ls=sorted(groups.values(),key=lambda x:(x['z'],x['id']))
  result['cards'].append({'id':sid,'start_frame':c['start_frame'],'end_frame':c['end_frame_exclusive'],'panels':ps,'text_frames':f'card_text/{sid}.json','source_graphic_ids':[{'id':oid,'owner':l['owner']} for l in ls if l['role'] in ['graphics','graphics_shared'] for oid in l['source_ids']],'layers':ls})
 save(R/'card_layers_plan.json',result);return result
def encode_layer(layer,keys,cache):
 unique=set(keys);out=R/'card_media'/f"{layer['id']}{'.png' if len(unique)==1 else '.mov'}"
 if len(unique)==1:shutil.copy2(cache/f'{keys[0]}.png',out)
 else:
  cmd=[str(FF),'-y','-v','error','-f','image2pipe','-framerate','30','-vcodec','png','-i','pipe:0','-an','-c:v','prores_ks','-profile:v','4','-pix_fmt','yuva444p10le','-alpha_bits','16','-threads','4',str(out)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
  try:
   for key in keys:proc.stdin.write((cache/f'{key}.png').read_bytes())
   proc.stdin.close();err=proc.stderr.read().decode();rc=proc.wait()
  except BrokenPipeError:raise RuntimeError(proc.stderr.read().decode())
  if rc:raise RuntimeError(err)
 layer.update(path=out.relative_to(R).as_posix(),kind='image' if len(unique)==1 else 'video',sha256=digest(out),unique_rasters=len(unique))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--plan-only',action='store_true');ap.add_argument('--cards',nargs='*');a=ap.parse_args();data=make_plan()
 if a.plan_only:return
 html=(R/'adapter/export_page.html').read_text(encoding='utf-8').replace('<script>(async()=>','<script src="/adapter/groups.js"></script><script>(async()=>')
 (S/'06_project/cards/export_page.html').write_text(html,encoding='utf-8')
 for name in ['card_media','card_manifests','qc','raster_cache']:(R/name).mkdir(exist_ok=True)
 srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(R)));Thread(target=srv.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(channel='chrome',headless=True);page=browser.new_page(viewport={'width':1920,'height':1080});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
   for card in data['cards']:
    sid=card['id'];manifest=R/'card_manifests'/f'{sid}.json'
    if a.cards and sid not in a.cards:
     if manifest.exists():card.update(json.loads(manifest.read_text(encoding='utf-8')))
     continue
    c=next(x for x in D['cards'] if x['id']==sid);samples=set(c['overview_frames']+[0,c['frame_count']//2,c['frame_count']-1]+[f for e in c['process_events'] for f in e['check_frames']]);cache=R/'raster_cache'/sid;cache.mkdir(exist_ok=True)
    page.goto(f'http://127.0.0.1:{srv.server_port}/source/episode/06_project/cards/export_page.html?card={sid}');page.wait_for_function('window.cardMotionReady===true');seq={l['id']:[] for l in card['layers']}
    for f in range(c['frame_count']):
     page.evaluate('f=>renderFrame(f)',f);row=page.evaluate('async x=>exportGroups(x.plan,x.reference)',{'plan':card['layers'],'reference':f in samples})
     for item in row['images']:
      p=R/'qc'/f'reference_{sid}_{f}.png' if item['key']=='reference' else cache/f"{item['key']}.png";p.write_bytes(base64.b64decode(item['png']))
     for x in row['keys']:seq[x['id']].append(x['key'])
     if f%120==0:print(sid,f,'/',c['frame_count'],'raster',flush=True)
    assert not errs,errs
    for l in card['layers']:encode_layer(l,seq[l['id']],cache)
    save(manifest,card);save(R/'card_layers.json',data);print(sid,'encoded',len(card['layers']),'layers',flush=True)
   browser.close()
 finally:srv.shutdown()
 if all('path' in l for c in data['cards'] for l in c['layers']):save(R/'card_layers.json',data)
if __name__=='__main__':main()
