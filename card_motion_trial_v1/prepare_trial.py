"""Copy only the C04 dependencies. Never writes to the source checkout."""
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
SOURCE = Path('D:/AI-Auto-V4（Codex）/episodes/ECHO_开源修图工具_20261006')
FILES = [
    '00_brief/effective_defaults.json', '00_brief/standard_lock.json',
    '03_storyboard/cards.json', '06_project/cards/scene.js',
    '06_project/cards/card_kit.js', '06_project/cards/card_scene.html',
    '06_project/cards/render_cards.py', '06_project/cards/vendor/flubber.min.js',
    '06_project/cards/vendor/flubber-LICENSE', '06_project/render/C04.mp4',
]

if __name__ == '__main__':
    for target in ('baseline', 'episode'):
        for relative in FILES:
            dest = HERE / target / relative
            assert dest.resolve().is_relative_to(HERE)
            if dest.exists():
                raise RuntimeError(f'Refusing to overwrite existing trial input: {dest}')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE / relative, dest)
    audio = HERE / 'baseline/01_audio/mixed_audio.wav'
    audio.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE / '01_audio/mixed_audio.wav', audio)
    print('Copied C04 sources to V5 baseline and episode; audio copied to V5 baseline.')
