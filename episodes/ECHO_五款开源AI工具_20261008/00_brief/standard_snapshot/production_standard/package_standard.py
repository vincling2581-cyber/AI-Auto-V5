"""Package the manifest-selected standard without importing an old episode."""
from pathlib import Path
import json
import zipfile
import hashlib
from standard_loader import load, ROOT, safe_path
HERE = Path(__file__).resolve().parent

def main():
    manifest = load()
    version = manifest['version']
    prefix = f'视频制作标准_v{version}'
    names = {item['path'] for item in manifest['files']}
    names.update(['production_standard.json', manifest['review'], 'production_standard/先读我.txt'])
    for name in [f'production_standard/全部制作规则_v{version}.md', f'production_standard/冲突与取舍_v{version}.md', 'production_standard/来源与影响清单.md']:
        if safe_path(ROOT, name).is_file():
            names.add(name)
    names.update(manifest.get('package_supplemental_files', []))
    output = ROOT / f'{prefix}_完整审阅包.zip'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in sorted(names):
            path = safe_path(ROOT, name)
            if not path.is_file():
                raise FileNotFoundError(path)
            archive.write(path, arcname=prefix + '/' + name)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        for item in manifest['files']:
            assert hashlib.sha256(archive.read(prefix + '/' + item['path'])).hexdigest() == item['sha256'], item['path']
        count = len(archive.namelist())
    qc = {'standard_version': version, 'zip': str(output), 'bytes': output.stat().st_size, 'entries': count, 'crc': 'passed', 'standard_hashes': 'passed', 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'scope': 'manifest-selected production standard, source methods and review; no automatic historic project or Jianying import package'}
    (HERE / 'checks').mkdir(exist_ok=True)
    (HERE / 'checks/package_qc.json').write_text(json.dumps(qc, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(qc, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
