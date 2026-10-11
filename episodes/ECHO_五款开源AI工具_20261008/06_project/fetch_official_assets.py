"""Download only cited public media. Do not install or execute any featured project."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import urllib.request,json,hashlib,time,subprocess
from PIL import Image
EP=Path(__file__).resolve().parents[1];OUT=EP/'04_assets/official';OUT.mkdir(parents=True,exist_ok=True)
assets=[
 ('voice_clone.webp','https://voicestudio.sh/img/screenshots/clone.webp','https://voicestudio.sh/'),
 ('voice_dub.webp','https://voicestudio.sh/img/screenshots/dub.webp','https://voicestudio.sh/'),
 ('voice_tour.gif','https://raw.githubusercontent.com/debpalash/VoiceStudio/main/docs/media/electron/voicestudio.gif','https://github.com/debpalash/VoiceStudio'),
 ('paperclip_tour.webm','https://paperclip.ing/videos/full-tour.webm','https://paperclip.ing/'),
 ('paperclip_home.png','https://raw.githubusercontent.com/paperclipai/paperclip/master/screenshots/PR-8000-home-flag-on.png','https://github.com/paperclipai/paperclip'),
 ('memos_architecture.png','https://raw.githubusercontent.com/MemTensor/MemOS/main/assets/readme/memos-agent-ecosystem.png','https://github.com/MemTensor/MemOS'),
 ('webui_demo.png','https://raw.githubusercontent.com/open-webui/open-webui/main/demo.png','https://github.com/open-webui/open-webui'),
 ('ollama_logo.png','https://ollama.com/public/ollama-nav.png','https://ollama.com/'),
]
def fetch(item):
    name,url,source=item;p=OUT/name
    row={'path':str(p.relative_to(EP)),'url':url,'source_page':source,'role':'official editorial evidence, not local product testing'}
    try:
        if not p.exists():
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 editorial-source-check'})
            with urllib.request.urlopen(req,timeout=40) as r:
                data=r.read(60*1024*1024+1)
                if len(data)>60*1024*1024:raise ValueError('Asset exceeds editorial size limit')
            p.write_bytes(data)
        row.update(status='downloaded',bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        if p.suffix in ('.png','.webp','.gif'):
            with Image.open(p) as im:row.update(width=im.width,height=im.height,frames=getattr(im,'n_frames',1))
    except Exception as e:row.update(status='failed',error=str(e))
    return row
rows=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    for job in as_completed([pool.submit(fetch,a) for a in assets]):
        row=job.result();rows.append(row);print(row['path']+' '+row['status'],flush=True)
(OUT/'source_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'downloaded':sum(r['status']=='downloaded' for r in rows),'failed':sum(r['status']=='failed' for r in rows)}))
