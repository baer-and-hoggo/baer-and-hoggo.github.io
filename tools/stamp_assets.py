"""Tags the stylesheets and scripts the hand-written pages load with their content hash.

The CDN in front of GitHub Pages lets browsers keep CSS and JS for hours, so an untagged
deploy shows visitors a new page on old styles. Run after editing any of them:
`python tools/stamp_assets.py`. The press page is tagged by tools/presskit/page.py.
"""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / 'index.html', ROOT / 'privacy' / 'index.html']
ASSET = re.compile(r'(href|src)="((?:\.\./)*(?:[\w-]+/)*[\w.-]+\.(?:css|js))(?:\?v=[0-9a-f]+)?"')


def stamp_page(page):
    def stamp(match):
        attribute, path = match.group(1), match.group(2)
        digest = hashlib.sha1((page.parent / path).resolve().read_bytes()).hexdigest()[:10]
        return f'{attribute}="{path}?v={digest}"'

    page.write_text(ASSET.sub(stamp, page.read_text(encoding='utf-8')), encoding='utf-8')


for page in PAGES:
    stamp_page(page)
    print(f'Stamped {page.relative_to(ROOT).as_posix()}')
