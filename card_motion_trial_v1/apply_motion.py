"""Replace only C04 inside the V5 episode copy; baseline remains immutable."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
original = (ROOT / 'baseline/06_project/cards/scene.js').read_bytes()
start = original.index(b'scenes.C04=')
end = original.index(b'scenes.C05=')
replacement = (ROOT / 'C04_motion.js').read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
target = ROOT / 'episode/06_project/cards/scene.js'
target.write_bytes(original[:start] + replacement + original[end:])
print('Updated only C04 in V5 episode/06_project/cards/scene.js')
