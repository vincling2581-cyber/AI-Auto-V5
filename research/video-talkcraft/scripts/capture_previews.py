"""Silent upstream-demo keyframe evidence; not V5 adaptation or normal-speed QA."""
from __future__ import annotations
import argparse
import asyncio
from io import BytesIO
import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'previews'
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


async def capture(browser, item, sem):
    slug = item['id']
    dest = OUT / f'{slug}.jpg'
    async with sem:
        page = await browser.new_page(viewport={'width': 960, 'height': 540}, device_scale_factor=1)
        errors, failed = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('requestfailed', lambda r: failed.append(r.url))
        result = {'id': slug, 'normal_speed_review': 'not_performed',
                  'production_adaptation': 'not_performed'}
        try:
            # These pinned demos are self-contained. No remote media or model calls.
            await page.route('https://**/*', lambda route: route.abort())
            url = (ROOT / f'upstream/demos/{slug}/index.html').as_uri() + '?embed=1'
            await page.goto(url, wait_until='load', timeout=20000)
            await page.wait_for_function('window.DemoShell && DemoShell.getDuration() > 0 && window.gsap', timeout=8000)
            await page.evaluate('document.fonts.ready')
            shell_duration = await page.evaluate('DemoShell.getDuration()')
            duration = shell_duration
            sampling_note = 'Three normalized upstream-demo states; not semantic timing validation'
            if shell_duration >= 59:
                tsx = (ROOT / f'upstream/template/cards/{slug}.tsx').read_text(encoding='utf-8')
                frames = re.search(r'durationInFrames:\s*(\d+)\s*[,}]', tsx)
                if frames:
                    duration = int(frames[1]) / 30
                    sampling_note = 'DemoShell capped an infinite tween at 60s; numeric TSX meta / 30fps used only as research sampling span'
                else:
                    finite = await page.evaluate('Math.max(0,...gsap.globalTimeline.getChildren(true,true,true).filter(t=>t.repeat()!==-1 && t.totalDuration()<30).map(t=>t.endTime(true)))')
                    duration = min(15, finite + 1.5)
                    sampling_note = 'DemoShell capped an infinite tween at 60s; finite GSAP actions plus 1.5s used only as research sampling span'
            times = [round(duration * x, 3) for x in (0.22, 0.5, 0.78)]
            frames = []
            for index, t in enumerate(times):
                # Some upstream demos add ticker listeners without replay cleanup.
                # Reload per state so a prior sample cannot overwrite the new state.
                if index:
                    await page.reload(wait_until='load', timeout=20000)
                    await page.wait_for_function('window.DemoShell && DemoShell.getDuration() > 0 && window.gsap', timeout=8000)
                    await page.evaluate('document.fonts.ready')
                await page.evaluate('t => { gsap.globalTimeline.pause(); DemoShell.seek(t); document.querySelectorAll("video").forEach(v => v.pause()); }', t)
                await page.wait_for_timeout(35)
                png = await page.screenshot(type='png')
                frame = Image.open(BytesIO(png)).convert('RGB').resize((320, 180), Image.Resampling.LANCZOS)
                frames.append(frame)
            strip = Image.new('RGB', (960, 208), '#f7f7f5')
            draw = ImageDraw.Draw(strip)
            draw.text((8, 5), slug + ' | ' + ' / '.join(f'{t:.2f}s' for t in times), fill='#1c242b')
            for i, frame in enumerate(frames):
                strip.paste(frame, (i * 320, 28))
            strip.save(dest, quality=89)
            result.update({'capture': 'completed', 'duration_seconds': duration,
                           'shell_duration_seconds': shell_duration, 'sampling_note': sampling_note,
                           'sample_times': times, 'preview': f'previews/{slug}.jpg',
                           'errors': errors, 'failed_requests': failed,
                           'keyframe_visual_review': 'pending'})
        except Exception as e:
            result.update({'capture': 'failed', 'reason': str(e), 'errors': errors, 'failed_requests': failed,
                           'keyframe_visual_review': 'not_performed'})
        finally:
            await page.close()
        if result['capture'] != 'completed' or errors:
            print(json.dumps({'id': slug, 'capture': result['capture'], 'errors': len(errors)}, ensure_ascii=False), flush=True)
        return result


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', nargs='*')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((ROOT / 'inventory.json').read_text(encoding='utf-8'))
    prior = {}
    report_path = OUT / 'capture_report.json'
    if report_path.exists():
        prior = {x['id']: x for x in json.loads(report_path.read_text(encoding='utf-8'))['cards']}
    selected = [x for x in inventory if not args.ids or x['id'] in args.ids]
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path=CHROME, headless=True, args=['--allow-file-access-from-files', '--mute-audio'])
        sem = asyncio.Semaphore(3)
        results = await asyncio.gather(*(capture(browser, x, sem) for x in selected))
        await browser.close()
    for item in results:
        prior[item['id']] = item
    ordered = [prior[x['id']] for x in inventory if x['id'] in prior]
    for n in range(0, len(inventory), 9):
        sheet = Image.new('RGB', (960, 208 * 9), '#e9e9e6')
        for row, item in enumerate(inventory[n:n + 9]):
            p = OUT / f'{item["id"]}.jpg'
            if p.exists():
                sheet.paste(Image.open(p).convert('RGB'), (0, row * 208))
        sheet.save(OUT / f'contact_{n // 9 + 1:02d}.jpg', quality=88)
    report = {'scope': 'Three sampled upstream HTML keyframes per card, silent and independent of V5 production',
              'normal_speed_review': 'not_performed', 'cards': ordered}
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'cards': len(ordered), 'completed': sum(x['capture'] == 'completed' for x in ordered),
                      'failed': [x['id'] for x in ordered if x['capture'] != 'completed']}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())
