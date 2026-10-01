"""The press kit web page. Needs only Pillow, so the page can be rebuilt without the PDF toolchain.

Run `python tools/presskit/page.py` to rebuild press/index.html alone; build.py also calls it.
"""
from html import escape as E
from pathlib import Path
import json

from PIL import Image

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1] / 'press'


def icon(name):
    return f'<svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#{name}"></use></svg>'


def page_html(C):
    steam, epic = C['steam'], C['epic']
    facts = ''.join(f'<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k, v in C['facts'])
    patches = ''.join(f'<li>{E(item)}</li>' for item in C['in_game'])
    long = ''.join(f'<p>{E(p)}</p>' for p in C['long'].split('\n\n'))
    socials = ''.join(f'<a class="fs-icon-link" href="{E(x["url"])}" aria-label="{E(x["name"])}" title="{E(x["name"].lower())}" target="_blank" rel="noopener">{icon(x["icon"])}</a>' for x in C['socials'])
    prices = ''.join(f'<tr><th scope="row">{E(code)}</th><td>{E(price)}</td></tr>' for code, price in C['prices'])

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
<link rel="icon" href="assets/brand/chicken.png">
<link rel="preload" href="assets/fonts/Nunito.ttf" as="font" type="font/ttf" crossorigin><link rel="preload" href="assets/fonts/Baloo2.ttf" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="assets/fonts/fonts.css"><link rel="stylesheet" href="shared.css"><link rel="stylesheet" href="styles.css"><script src="app.js" defer></script></head>
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
  <img class="fs-panorama" src="../assets/hero.png" alt="" width="3840" height="1240" aria-hidden="true">
</header>

<main id="main" class="fs-wrap">
  <section class="fs-section" aria-labelledby="about-title"><div class="fs-flap">
    <h2 id="about-title" class="fs-tape">about</h2>
    <div class="pk-about">
      <dl class="fs-canvas pk-facts">{facts}</dl>
      <div class="pk-story">
        <p class="pk-short" id="short-copy">{E(C['short'])}</p>
        <div class="pk-copyrow"><button class="fs-strap small" data-copy="short-copy">copy short</button><button class="fs-strap small" data-copy="long-copy">copy full</button><span id="copy-status" class="fs-muted" role="status" aria-live="polite"></span></div>
        <details class="fs-canvas"><summary>full description</summary><div id="long-copy">{long}</div></details>
        <details class="fs-canvas" id="pricing"><summary>regional prices</summary><p>{E(C['pricing_note'])}</p><table><tbody>{prices}</tbody></table></details>
      </div>
    </div>
  </div></section>

  <section class="fs-section" aria-labelledby="ingame-title"><div class="fs-flap">
    <h2 id="ingame-title" class="fs-tape">in the game</h2>
    <ul class="pk-patches">{patches}</ul>
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
    <p>{E(C['studio_copy'])}</p>
    <div class="pk-team">{team}</div>
  </div></section>

  <section id="contact" class="pk-contact" aria-labelledby="contact-title">
    <img src="assets/brand/chicken.png" alt="" width="1024" height="1024" loading="lazy">
    <div><h2 id="contact-title">Press contact</h2><a class="pk-email" href="mailto:{C['contact']}">{C['contact']}</a><div class="fs-socials">{socials}</div></div>
  </section>
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
