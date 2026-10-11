"""Compatibility reader: canonical prompts.json is the only current prompt source."""
from pathlib import Path
import json
from standard_loader import safe_path
ROOT = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / 'production_standard.json').read_text(encoding='utf-8-sig'))
DATA = json.loads(safe_path(ROOT, MANIFEST.get('prompts_data', 'production_standard/prompts.json')).read_text(encoding='utf-8-sig'))
PROMPTS = [(p['id'], p['title'], p['text']) for p in DATA]
