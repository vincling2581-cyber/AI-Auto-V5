"""Check retained objects, repair ordering, layer restoration, and an actual final edit."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json

ROOT=Path(__file__).resolve().parent
QC=ROOT/'08_qc'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
report={'scope':'visual trial: semantic invariants and browser frames; no listening or subjective full-speed acceptance',
        'checks':[],'page_errors':[]}
def check(name,value):
    report['checks'].append({'name':name,'passed':bool(value)})
    assert value,name
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='chrome',headless=True)
        page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/06_project/cards/card_scene.html?card=C01')
        page.wait_for_function('window.cardMotionReady===true')
        def render(frame):
            page.evaluate('f=>window.renderFrame(f)',frame)
            return page.evaluate('window.motionState')
        snapshots={f:render(f) for f in [0,72,144,192,228,280,300,301,312,330,402,414,474,539]}
        check('source file retained throughout',[s['sourceFileRetained'] for s in snapshots.values()]==[True]*len(snapshots))
        check('three independent objects throughout',all(s['layerCount']==3 for s in snapshots.values()))
        check('repair does not move normal background',len({tuple(snapshots[f]['backgroundAnchor']) for f in [192,228,280,300,301,312,330]})==1)
        check('repair does not move tag',len({tuple(snapshots[f]['tagAnchor']) for f in [192,228,280,300,301,312,330]})==1)
        check('repair follows incoming type token',not snapshots[300]['repaired'] and snapshots[301]['repaired'])
        for key in ['backgroundAnchor','titleAnchor','tagAnchor']:
            check('rebuild restores '+key,snapshots[402][key]==snapshots[72][key])
        check('final tag has genuinely moved',snapshots[474]['tagAnchor'][0]==snapshots[402]['tagAnchor'][0]-194)
        check('final edit preserves background and title',all(snapshots[474][k]==snapshots[402][k] for k in ['backgroundAnchor','titleAnchor']))
        render(474);still=page.screenshot()
        for frame in range(475,540):
            render(frame)
            check('reading hold '+str(frame),page.screenshot()==still)
        (QC/'final_frame.png').write_bytes(still)
        sample_frames=[24,44,111,171,207,270,300,307,366,444]
        captures={}
        for frame in sample_frames:
            render(frame);captures[frame]=page.screenshot()
        for frame in reversed(sample_frames):
            render(frame);check('random access '+str(frame),captures[frame]==page.screenshot())
        render(301)
        check('selected font arrives in title',page.locator('text').evaluate_all("els=>els.some(e=>e.textContent==='山野计划'&&e.getAttribute('font-family')==='Microsoft YaHei')"))
        render(539)
        check('final label records changed position','位置已更新' in page.locator('text').all_text_contents())
        check('no browser errors',not report['page_errors'])
        report['sample_states']=snapshots
        report['passed']=True
        browser.close()
finally:
    server.shutdown()
    (QC/'semantic_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':report.get('passed',False),'checks':len(report['checks'])}))
