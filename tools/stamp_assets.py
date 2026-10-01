"""Tags the stylesheets and scripts index.html loads with their content hash.

The CDN in front of GitHub Pages lets browsers keep CSS and JS for hours, so an untagged
deploy shows visitors a new page on old styles. Run after editing any of them:
`python tools/stamp_assets.py`. The press page is tagged by tools/presskit/page.py.
"""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'


def stamp(match):
    attribute, path = match.group(1), match.group(2)
    digest = hashlib.sha1((ROOT / path).read_bytes()).hexdigest()[:10]
    return f'{attribute}="{path}?v={digest}"'


html = INDEX.read_text(encoding='utf-8')
html = re.sub(r'(href|src)="((?:press/)?[\w./-]+\.(?:css|js))(?:\?v=[0-9a-f]+)?"', stamp, html)
INDEX.write_text(html, encoding='utf-8')
print('Stamped index.html assets')
