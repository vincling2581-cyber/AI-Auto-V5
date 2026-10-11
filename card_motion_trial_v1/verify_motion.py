"""Compare settled images with the untouched V5 baseline, plus random frame access."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from collections import Counter
import hashlib
import json
from io import BytesIO
from PIL import Image, ImageChops
import numpy as np
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'checks'
OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
report={'scope':'C04 only; source browser frames, not subjective video acceptance',
        'restored_hold_frames':list(range(72,126)), 'final_hold_frames':list(range(240,278)),
        'settled_frames_checked':[], 'deterministic_frames':[], 'errors':[],
        'settled_comparison_tolerance':{'max_channel_difference':1,'max_changed_pixels':64},
        'settled_comparisons':[]}
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='chrome',headless=True)
        pages={}
        for version in ('baseline','episode'):
            page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
            page.on('pageerror',lambda error:report['errors'].append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/{version}/06_project/cards/card_scene.html?card=C04')
            page.wait_for_function('window.cardMotionReady===true')
            pages[version]=page
        def shot(version,frame):
            page=pages[version]
            page.evaluate('f=>window.renderFrame(f)',frame)
            return page.screenshot(type='png')
        for start,end,label in ((72,126,'restored'),(240,278,'final')):
            reference=shot('baseline',start)
            first=shot('episode',start)
            a=np.asarray(Image.open(BytesIO(reference)).convert('RGB')).astype(int)
            b=np.asarray(Image.open(BytesIO(first)).convert('RGB')).astype(int)
            diff=np.abs(a-b)
            maximum=int(diff.max());changed=int(np.count_nonzero(diff.max(axis=2)))
            report['settled_comparisons'].append({'window':label,'max_channel_difference':maximum,'changed_pixels':changed})
            assert maximum<=1 and changed<=64,f'{label} artwork changed: max={maximum}, pixels={changed}'
            for f in range(start,end):
                actual=shot('episode',f)
                assert actual==first,f'{label} reading hold moves at frame {f}'
                report['settled_frames_checked'].append(f)
            (OUT/f'{label}_unchanged.png').write_bytes(reference)
        # Compare opening frame independently, then revisit disordered process frames.
        a=np.asarray(Image.open(BytesIO(shot('baseline',0))).convert('RGB')).astype(int)
        b=np.asarray(Image.open(BytesIO(shot('episode',0))).convert('RGB')).astype(int)
        diff=np.abs(a-b)
        report['initial_frame_comparison']={'max_channel_difference':int(diff.max()),'changed_pixels':int(np.count_nonzero(diff.max(axis=2)))}
        assert diff.max()<=1 and np.count_nonzero(diff.max(axis=2))<=64,'Initial artwork changed'
        frames=[13,45,60,64,142,178,220]
        captured={f:shot('episode',f) for f in frames}
        for f in [220,13,178,60,45,142,64]:
            assert shot('episode',f)==captured[f],f'Nondeterministic frame {f}'
            report['deterministic_frames'].append(f)
        for f in [60,72,142,178,220,240]:
            texts={}
            for version,page in pages.items():
                page.evaluate('f=>window.renderFrame(f)',f)
                texts[version]=Counter(page.locator('text').all_text_contents())
            assert texts['baseline']==texts['episode'],f'Wording changed at {f}'
        report['wording_preserved']=True
        assert not report['errors'],report['errors']
        report['result']='passed'
        browser.close()
finally:
    server.shutdown()
    (OUT/'motion_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('restored_hold_frames','final_hold_frames','settled_frames_checked')},ensure_ascii=False))
