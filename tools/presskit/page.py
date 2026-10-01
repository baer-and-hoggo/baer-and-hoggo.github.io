"""The press kit web page. Needs only Pillow, so the page can be rebuilt without the PDF toolchain.

Run `python tools/presskit/page.py` to rebuild press/index.html alone; build.py also calls it.
"""
from html import escape as E
from pathlib import Path
import hashlib
import json

from PIL import Image

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1] / 'press'


def asset(path):
    """A page-relative asset URL tagged with its content hash, so a deploy is never hidden behind a cached copy."""
    digest = hashlib.sha1((ROOT / path).read_bytes()).hexdigest()[:10]
    return f'{path}?v={digest}'


def icon(name):
    return f'<svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#{name}"></use></svg>'


def copyblock(label, body, plain, extra=''):
    """A canvas block with a label and a copy button that copies `plain`, the text as an editor would paste it."""
    return (f'<div class="fs-canvas pk-copy {extra}"><div class="pk-copy-head"><span class="pk-label">{label}</span>'
            f'<button class="fs-strap small" data-copy-text="{E(plain)}">copy</button></div>{body}</div>')


def page_html(C):
    steam, epic = C['steam'], C['epic']
    facts = copyblock('fact sheet',
                      '<dl class="pk-facts">' + ''.join(f'<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k, v in C['facts']) + '</dl>',
                      '\n'.join(f'{k}: {v}' for k, v in C['facts']))
    prices = copyblock('prices',
                       f'<p>{E(C["pricing_note"])}</p><p class="pk-prices">' + ' · '.join(f'{E(code)} {E(price)}' for code, price in C['prices']) + '</p>',
                       C['pricing_note'] + '\n' + '\n'.join(f'{code}: {price}' for code, price in C['prices']),
                       'pk-pricing" id="pricing')
    short = copyblock('short description', f'<p>{E(C["short"])}</p>', C['short'])
    long = copyblock('long description', ''.join(f'<p>{E(p)}</p>' for p in C['long'].split('\n\n')), C['long'])
    features = ''.join(copyblock(E(t.lower()), f'<p>{E(b)}</p>', f'{t}\n{b}', 'pk-feature') for t, b in C['features'])
    features_all = '\n\n'.join(f'{t}\n{b}' for t, b in C['features'])
    patches = copyblock('in the game',
                        '<ul class="pk-patches">' + ''.join(f'<li>{E(item)}</li>' for item in C['in_game']) + '</ul>',
                        '\n'.join(f'- {item}' for item in C['in_game']))
    studio = copyblock('studio bio', f'<p>{E(C["studio_copy"])}</p>', C['studio_copy'])
    link_rows = ([('Steam', steam), ('Epic Games Store', epic), ('Website', C['website']), ('Discord', C['discord'])]
                 + [(x['name'], x['url']) for x in C['socials']])
    links = copyblock('links',
                      '<dl class="pk-facts">' + ''.join(
                          f'<div><dt>{E(n)}</dt><dd><a href="{E(u)}" target="_blank" rel="noopener">{E(u.replace("https://", "").replace("www.", ""))}</a></dd></div>'
                          for n, u in link_rows)
                      + f'<div><dt>Press contact</dt><dd><a href="mailto:{C["contact"]}">{C["contact"]}</a></dd></div></dl>',
                      '\n'.join(f'{n}: {u}' for n, u in link_rows) + f'\nPress contact: {C["contact"]}')
    socials = ''.join(f'<a class="fs-icon-link" href="{E(x["url"])}" aria-label="{E(x["name"])}" title="{E(x["name"].lower())}" target="_blank" rel="noopener">{icon(x["icon"])}</a>' for x in C['socials'])

    shots = []
    for s in C['screenshots']:
        src = f'assets/screenshots/steam-{s["id"]:02d}.jpg'
        w, h = Image.open(ROOT / src).size
        shots.append(
            f'<figure class="fs-shot" data-src="{src}" data-title="{E(s["title"].lower())}" data-caption="{E(s["caption"])}">'
            f'<div class="fs-pocket"><button aria-label="Enlarge: {E(s["title"])}"><img src="{src}" alt="{E(s["caption"])}" width="{w}" height="{h}" loading="lazy"></button></div>'
            f'<figcaption><span>{E(s["title"].lower())}</span><a href="{src}" download="farmion-{s["name"]}.jpg" aria-label="Download {E(s["title"])}">jpg</a></figcaption></figure>')

    logos = []
    for file, title, note in [
        ('farmion-logo.png', 'farmion logo', 'transparent png'),
        ('chicken.png', 'chicken', 'mascot, transparent png'),
        ('studio-logo.png', 'studio logo', 'transparent png'),
        ('studio-mascot.png', 'baer &amp; hoggo', 'mascot, transparent png'),
    ]:
        w, h = Image.open(ROOT / 'assets/brand' / file).size
        logos.append(
            f'<figure class="pk-logo"><div class="fs-pocket"><img src="assets/brand/{file}" alt="" width="{w}" height="{h}" loading="lazy"></div>'
            f'<figcaption><span>{title}<small>{note}</small></span><a href="assets/brand/{file}" download>png</a></figcaption></figure>')

    team = ''.join(
        f'<div class="fs-canvas pk-person"><strong>{E(p["name"])}</strong>'
        f'<svg class="site-flag" role="img" aria-label="{E(p["country"])}" viewBox="0 0 16 11"><use href="assets/ui-icons.svg#{p["flag"]}"></use></svg>'
        f'<span>{E(p["role"])}</span>'
        + (f'<a href="{E(p["linkedin"])}" target="_blank" rel="noopener">linkedin</a>' if 'linkedin' in p else '')
        + '</div>' for p in C['team'])

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="The Farmion press kit: facts, screenshots, logos and contact details from Baer &amp; Hoggo Games.">
<meta name="theme-color" content="#a3def4"><title>Farmion Press Kit | Baer &amp; Hoggo Games</title>
<link rel="canonical" href="https://baerandhoggo.com/press/">
<link rel="icon" href="assets/brand/chicken.png">
<link rel="preload" href="assets/fonts/Nunito.ttf" as="font" type="font/ttf" crossorigin><link rel="preload" href="assets/fonts/Baloo2.ttf" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="assets/fonts/fonts.css"><link rel="stylesheet" href="{asset('shared.css')}"><link rel="stylesheet" href="{asset('styles.css')}"><script src="{asset('app.js')}" defer></script></head>
<body class="farmion-site"><a class="fs-skip" href="#main">Skip to press kit</a>
<header class="fs-sky">
  <nav class="fs-wrap fs-toplinks" aria-label="Farmion links">
    <a class="fs-strap small fs-toplink-label" href="../#farmion"><span>← farmion</span></a>
    <a class="fs-icon-link" href="{steam}" aria-label="Steam" title="steam" target="_blank" rel="noopener">{icon('steam')}</a>
    <a class="fs-icon-link" href="{epic}" aria-label="Epic Games Store" title="epic games store" target="_blank" rel="noopener">{icon('epic')}</a>
    <a class="fs-icon-link" href="{C['discord']}" aria-label="Discord" title="discord" target="_blank" rel="noopener">{icon('discord')}</a>
  </nav>
  <div class="fs-wrap fs-hero">
    <h1 class="pk-title"><a href="../#farmion" class="pk-logo-link"><img src="assets/brand/farmion-logo.png" alt="Farmion" width="1280" height="720"></a><span class="fs-tape">press kit</span></h1>
    <div class="fs-actions">
      <a class="fs-brass" href="downloads/Farmion-Press-Assets.zip" download>{icon('download')}<span>download everything</span></a>
      <a class="fs-strap" href="downloads/Farmion-Press-Kit.pdf" download>{icon('press')}<span>pdf</span></a>
    </div>
    <p class="pk-credit">Please credit Baer &amp; Hoggo Games.</p>
  </div>
</header>

<main id="main" class="fs-wrap">
  <section class="fs-section" aria-labelledby="about-title"><div class="fs-flap">
    <h2 id="about-title" class="fs-tape">about</h2>
    <div class="pk-about">
      <div class="pk-col">{facts}{prices}</div>
      <div class="pk-col">{short}{long}</div>
    </div>
  </div></section>

  <section id="features" class="fs-section" aria-labelledby="features-title"><div class="fs-flap">
    <div class="fs-flap-head"><h2 id="features-title" class="fs-tape">features</h2><button class="fs-strap small" data-copy-text="{E(features_all)}">copy all</button></div>
    <div class="pk-features">{features}</div>
    {patches}
  </div></section>

  <section class="fs-section" aria-labelledby="trailer-title"><div class="fs-flap">
    <div class="fs-flap-head"><h2 id="trailer-title" class="fs-tape">trailer</h2><a href="https://youtu.be/qbWGLGrDzVk" target="_blank" rel="noopener">youtube</a></div>
    <div class="fs-pocket"><iframe class="pk-video" src="https://www.youtube-nocookie.com/embed/qbWGLGrDzVk" title="Farmion gameplay trailer" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
  </div></section>

  <section id="screenshots" class="fs-section" aria-labelledby="screenshots-title"><div class="fs-flap">
    <div class="fs-flap-head"><h2 id="screenshots-title" class="fs-tape">screenshots</h2><a href="downloads/Farmion-Screenshots.zip" download>all 21 as zip</a></div>
    <div class="fs-shots">{''.join(shots)}</div>
  </div></section>

  <section id="downloads" class="fs-section" aria-labelledby="logos-title"><div class="fs-flap">
    <div class="fs-flap-head"><h2 id="logos-title" class="fs-tape">logos</h2><a href="downloads/Farmion-Logos.zip" download>all as zip</a></div>
    <div class="pk-logos">{''.join(logos)}</div>
  </div></section>

  <section id="studio" class="fs-section" aria-labelledby="studio-title"><div class="fs-flap">
    <h2 id="studio-title" class="fs-tape">studio</h2>
    {studio}
    <div class="pk-team">{team}</div>
  </div></section>

  <section id="contact" class="pk-contact" aria-labelledby="contact-title">
    <img src="assets/brand/chicken.png" alt="" width="1024" height="1024" loading="lazy">
    <div><h2 id="contact-title">Press contact</h2><a class="pk-email" href="mailto:{C['contact']}">{C['contact']}</a><div class="fs-socials">{socials}</div></div>
  </section>
  <section class="fs-section" aria-label="Links"><div class="fs-flap">{links}</div></section>
</main>

<footer class="fs-footer"><div class="fs-wrap">
  <span class="site-identity"><span>© 2026 Baer &amp; Hoggo Games</span><span class="site-countries"><span><svg class="site-flag" role="img" aria-label="Netherlands" viewBox="0 0 16 11"><use href="assets/ui-icons.svg#nl"></use></svg></span><span><svg class="site-flag" role="img" aria-label="Estonia" viewBox="0 0 16 11"><use href="assets/ui-icons.svg#ee"></use></svg></span></span></span>
  <nav aria-label="Footer"><a href="../#farmion">website</a><a href="../privacy/">privacy</a><span>facts checked {C['verified']}</span></nav>
</div></footer>

<dialog id="lightbox" class="fs-lightbox" aria-labelledby="lightbox-title">
  <div class="fs-lightbox-bar"><strong id="lightbox-title" class="fs-tape"></strong><div><button class="fs-strap small" id="previous" aria-label="Previous screenshot">←</button><button class="fs-strap small" id="next" aria-label="Next screenshot">→</button><a class="fs-brass small" id="lightbox-download" download>jpg</a><button class="fs-strap small" id="lightbox-close">close</button></div></div>
  <img id="lightbox-image" alt="">
</dialog>
</body></html>
'''


if __name__ == '__main__':
    content = json.loads((SOURCE / 'content.json').read_text(encoding='utf-8'))
    (ROOT / 'index.html').write_text(page_html(content), encoding='utf-8')
    print('Built press/index.html')
