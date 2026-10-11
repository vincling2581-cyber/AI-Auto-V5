"""One representative text edit and real local re-render in an isolated copy."""
from pathlib import Path
import json,shutil,subprocess,sys,hashlib
EP=Path(__file__).resolve().parent.parent
DEST=EP/'08_qc/edit_roundtrip/workspace'
DEST.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=list((EP/'06_project/cards').rglob('*'))+[EP/'00_brief/effective_defaults.json',EP/'03_storyboard/cards.json',EP/'04_assets/official/impeccable_case.png',EP/'04_assets/official/impeccable_home.png']
files=[p for p in files if p.is_file() and '__pycache__' not in str(p)]
before={str(p.relative_to(EP)):sha(p) for p in files}
for p in files:
 d=DEST/p.relative_to(EP);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
datafile=DEST/'03_storyboard/cards.json';data=json.loads(datafile.read_text(encoding='utf-8'));c=next(x for x in data['cards'] if x['id']=='C05');old=c['title'];c['title']='Impeccable：本地修改验证';datafile.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
subprocess.run([sys.executable,'-B','-X','utf8',str(DEST/'06_project/cards/render_cards.py'),'--cards','C05','--workers','1'],check=True)
r=json.loads((DEST/'08_qc/cards/C05/render_check.json').read_text(encoding='utf-8'))
assert r['frame_count']==286 and r['decode']=='passed' and not r['text_overflow'] and r['deterministic']
after={str(p.relative_to(EP)):sha(p) for p in files};assert before==after
qc=EP/'08_qc/edit_roundtrip';shutil.copy2(DEST/'08_qc/cards/C05/f0000.png',qc/'edited_first_frame.png')
(qc/'result.json').write_text(json.dumps(dict(passed=True,mode='isolated_copy_real_segment_render',change={'field':'C05.title','before':old,'after':c['title']},rendered_frames=r['frame_count'],encoded_sha256=r['sha256'],source_project_unchanged=True,source_hashes=before,changed_copy='08_qc/edit_roundtrip/workspace',limits='Proves representative text edit and local source render, not native AE/Jianying editability'),ensure_ascii=False,indent=2),encoding='utf-8')
print('Representative edit and local re-render: passed; production sources unchanged',flush=True)
