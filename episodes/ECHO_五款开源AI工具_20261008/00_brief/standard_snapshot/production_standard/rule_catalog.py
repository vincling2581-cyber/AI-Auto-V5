"""Compatibility reader: canonical rules.json is the only current rule source."""
from pathlib import Path
import json
from standard_loader import safe_path

def rules():
    root = Path(__file__).resolve().parent.parent
    manifest = json.loads((root / 'production_standard.json').read_text(encoding='utf-8-sig'))
    return json.loads(safe_path(root, manifest['rules']).read_text(encoding='utf-8-sig'))
