"""Build the standalone Farmion press page, designed PDF, and download archives.

Run with Python plus reportlab, Pillow, pypdf, and fontTools.
All screenshot and brand sources are copied without changing their image contents.
"""
from pathlib import Path
from html import escape
from io import BytesIO
import hashlib
import json
import zipfile

from PIL import Image
from fontTools.ttLib import TTFont as VariableFont
from fontTools.varLib.instancer import instantiateVariableFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[1] / 'press'
C = json.loads((SOURCE / "content.json").read_text(encoding="utf-8"))
DOWNLOADS = ROOT / "downloads"
DOWNLOADS.mkdir(exist_ok=True)
STEAM = C["steam"]
E = escape


def page_html():
    facts = "".join(f'<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k, v in C['facts'])
    features = "".join(f'<article class="feature"><span class="feature-number">0{i+1}</span><h3>{E(title)}</h3><p>{E(body)}</p></article>' for i, (title, body) in enumerate(C['features']))
    cards = []
    for s in C['screenshots']:
        src = f'assets/screenshots/steam-{s["id"]:02d}.jpg'
        sw, sh = Image.open(ROOT / src).size
        cards.append(f'''<figure class="shot" data-category="{s['category']}" data-src="{src}" data-title="{E(s['title'])}" data-caption="{E(s['caption'])}">
        <button class="shot-open" aria-label="Enlarge: {E(s['title'])}"><img src="{src}" alt="{E(s['caption'])}" width="{sw}" height="{sh}" loading="lazy"></button>
        <figcaption><div><strong>{E(s['title'])}</strong><br><span>IN-GAME SCREENSHOT · {sw} × {sh}</span></div><a href="{src}" download="farmion-{s['name']}.jpg" aria-label="Download {E(s['title'])}">JPG ↓</a></figcaption></figure>''')
    pricing_rows = ''.join(f'<tr><th scope="row">{code}</th><td>{E(price)}</td></tr>' for code,price in C['prices'])
    long = ''.join(f'<p>{E(p)}</p>' for p in C['long'].split('\n\n'))
    team = []
    for person in C['team']:
        flag = f'<svg class="site-flag" role="img" aria-label="{E(person["country"])}" viewBox="0 0 16 11"><use href="assets/ui-icons.svg#{person["flag"]}"></use></svg>'
        linkedin = f'<a href="{E(person["linkedin"])}" target="_blank" rel="noopener">LinkedIn ↗</a>' if 'linkedin' in person else ''
        team.append(f'<article class="team-member"><h3>{E(person["name"])}{flag}</h3><p>{E(person["role"])}</p>{linkedin}</article>')
    team_html = '<div class="team">' + ''.join(team) + '</div>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="The Farmion press kit: game facts, screenshots, logos, press copy, and contact details from Baer &amp; Hoggo Games."><meta name="theme-color" content="#183c2f"><title>Farmion — Press Kit | Baer &amp; Hoggo Games</title><link rel="icon" href="assets/brand/chicken.png"><link rel="preload" href="assets/fonts/Nunito.ttf" as="font" type="font/ttf" crossorigin><link rel="preload" href="assets/fonts/Baloo2.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="assets/fonts/fonts.css"><link rel="stylesheet" href="shared.css"><link rel="stylesheet" href="styles.css"><script src="app.js" defer></script></head>
<body class="farmion-site"><a class="skip" href="#main">Skip to press kit</a>
<header class="topbar"><nav class="wrap nav" aria-label="Main navigation"><a class="wordmark" href="../#farmion" aria-label="Farmion"><img src="assets/brand/farmion-logo.png" alt="Farmion" width="1280" height="720"></a><div class="site-links"><a class="site-nav-link" href="#screenshots" aria-label="Screenshots"><svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#screenshots"></use></svg><span class="site-nav-label" aria-hidden="true">Screenshots</span></a><a class="site-nav-link" href="./" aria-label="Press kit" aria-current="page"><svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#press"></use></svg><span class="site-nav-label" aria-hidden="true">Press kit</span></a><a class="site-nav-link site-nav-link-steam" href="https://store.steampowered.com/app/2426390/Farmion/" aria-label="Steam" target="_blank" rel="noopener"><svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#steam"></use></svg><span class="site-nav-label" aria-hidden="true">Steam</span></a><a class="site-nav-link" href="https://discord.gg/rBmkV9XXCw" aria-label="Discord" target="_blank" rel="noopener"><svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#discord"></use></svg><span class="site-nav-label" aria-hidden="true">Discord</span></a></div></nav></header>
<main id="main"><section class="wrap hero" aria-labelledby="hero-title"><div class="hero-copy"><p class="eyebrow">Baer &amp; Hoggo Games / Press kit</p><h1 id="hero-title">Farmion.<br><em>Press kit.</em></h1><p class="hero-intro">Game facts, screenshots, logos, and contact details for press and creators.</p><div class="actions"><a class="button primary" href="downloads/Farmion-Press-Assets.zip" download><svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#download"></use></svg><span>Download kit</span></a><a class="button" href="{STEAM}" target="_blank" rel="noopener"><svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#steam"></use></svg><span>Steam</span></a></div><div class="hero-meta"><p>Planned for Q4 2026 · Steam Early Access · Windows PC</p><p class="hero-price">Expected price: <strong>US{E(C['prices'][0][1])} / {E(C['prices'][2][1])}</strong><br>Planned launch offer: 15% off for the first 8 days. <a href="#pricing">Regional prices</a></p></div></div><div class="hero-art"><div class="press-window"><img class="hero-shot" src="assets/screenshots/steam-00.jpg" alt="A red tractor among golden crops, with a windmill beyond the field." width="1920" height="1080" fetchpriority="high"><img class="press-window-frame" src="assets/brand/greenhouse-frame.svg" alt="" aria-hidden="true"></div><div class="stamp"><span>PLAY SOLO</span><strong>or</strong><span>WITH FRIENDS</span></div><figure class="postcard"><img src="assets/screenshots/steam-05.jpg" alt="A farmer beside a flower-filled garden." width="1920" height="1080"><figcaption>In-game screenshot</figcaption></figure><span class="photo-note">Actual in-game imagery · In development</span></div></section>
<div class="fact-strip"><div class="wrap"><div><span>Planned release</span><strong>Q4 2026 · Early Access</strong></div><div><span>Platform</span><strong>Windows PC / Steam</strong></div><div><span>Play modes</span><strong>Solo &amp; online co-op</strong></div><div><span>Made by</span><strong>Baer &amp; Hoggo Games</strong></div></div></div>
<section id="overview" class="wrap section overview" aria-labelledby="overview-title"><aside class="facts"><h3>Factsheet.</h3><dl>{facts}</dl><nav class="press-jumps" aria-label="Press resources"><a href="#screenshots">Screenshots ↗</a><a href="#downloads">Logos &amp; downloads ↗</a><a href="#studio">About the studio ↗</a><a href="#contact">Press contact ↗</a></nav></aside><div class="story"><p class="eyebrow">01 / Factsheet &amp; description</p><h2 id="overview-title">About the game.</h2><p class="lede" id="short-copy">{E(C['short'])}</p><div class="copyrow"><button class="copy-button" data-copy="short-copy">Copy short description ↗</button><button class="copy-button" data-copy="long-copy">Copy full description ↗</button><span id="copy-status" class="copy-status" role="status" aria-live="polite"></span></div><details><summary>Full description</summary><div class="long-copy" id="long-copy">{long}</div></details><details id="pricing" class="pricing"><summary>Proposed pricing &amp; launch discount</summary><p>{E(C['pricing_note'])}</p><table><caption>Proposed regional base prices</caption><thead><tr><th scope="col">Currency</th><th scope="col">Base price</th></tr></thead><tbody>{pricing_rows}</tbody></table></details><p class="micro">Planned for Steam Early Access. The game is in development; features and visuals may change.</p></div></section>
<section class="wrap section" aria-labelledby="features-title"><p class="eyebrow">02 / Gameplay</p><h2 id="features-title">Gameplay.</h2><div class="feature-grid">{features}</div></section>
<section id="screenshots" class="wrap section" aria-labelledby="screenshots-title"><div class="section-heading"><div><p class="eyebrow">03 / Screenshots</p><h2 id="screenshots-title">Screenshots.</h2></div><a class="text-link" href="downloads/Farmion-Screenshots.zip" download>Download all 21 screenshots ↓</a></div><div class="gallery-controls" role="group" aria-label="Filter screenshots"><button class="filter" data-filter="all" aria-pressed="true">Everything</button><button class="filter" data-filter="farm" aria-pressed="false">On the farm</button><button class="filter" data-filter="shops" aria-pressed="false">Shops &amp; business</button><button class="filter" data-filter="life" aria-pressed="false">Characters &amp; scenery</button></div><p class="micro" id="gallery-status" role="status" aria-live="polite">8 screenshots shown.</p><div class="gallery">{''.join(cards)}</div><p class="gallery-note">Original images from the Farmion Steam gallery. Downloads preserve the full frame. Please credit Farmion / Baer &amp; Hoggo Games. All images show a game in development.</p></section>
<section id="downloads" class="wrap section" aria-labelledby="downloads-title"><div class="section-heading"><div><p class="eyebrow">04 / Press resources</p><h2 id="downloads-title">Downloads.</h2></div><span class="micro">Updated {C['edition']}</span></div><div class="downloads-layout"><div class="download-list"><a class="download-row" href="downloads/Farmion-Press-Assets.zip" download><span class="index">01</span><span class="label"><strong>Complete press assets</strong><small>21 screenshots, original logos, PDF &amp; press copy · ZIP</small></span><span class="arrow">↓</span></a><a class="download-row" href="downloads/Farmion-Press-Kit.pdf" download><span class="index">02</span><span class="label"><strong>Press kit PDF</strong><small>Five-page game overview · PDF</small></span><span class="arrow">↓</span></a><a class="download-row" href="downloads/Farmion-Logos.zip" download><span class="index">03</span><span class="label"><strong>Brand artwork</strong><small>Farmion and studio logos, mascots · PNG ZIP</small></span><span class="arrow">↓</span></a><a class="download-row" href="downloads/Farmion-Press-Copy.txt" download><span class="index">04</span><span class="label"><strong>Press copy</strong><small>Game descriptions, facts &amp; studio bio · TXT</small></span><span class="arrow">↓</span></a></div><div class="brand-card"><span class="eyebrow">Farmion logo</span><img class="brand-logo" src="assets/brand/farmion-logo.png" alt="Farmion logo with leaves, a chicken, and a daisy." width="1280" height="720"><p>Use the original colors and proportions.</p><a href="assets/brand/farmion-logo.png" download>Download transparent PNG ↓</a></div></div></section>
<section id="studio" class="wrap section studio" aria-labelledby="studio-title"><img class="studio-mascot" src="assets/brand/studio-mascot.png" alt="The bear and hedgehog mascots of Baer &amp; Hoggo Games." width="1019" height="1024" loading="lazy"><div><p class="eyebrow">05 / About the studio</p><h2 id="studio-title">About the studio.</h2><p>{E(C['studio_copy'])}</p>{team_html}<a class="text-link" href="https://baerandhoggo.com/" target="_blank" rel="noopener">Studio website ↗</a></div></section>
<section id="contact" class="contact" aria-labelledby="contact-title"><div class="wrap contact-grid"><div><p class="eyebrow">Contact</p><h2 id="contact-title">Press contact.</h2><p>Press and interview enquiries:</p><a class="email" href="mailto:{C['contact']}">{C['contact']}</a></div><img class="chicken" src="assets/brand/chicken.png" alt="Farmion chicken mascot." width="1024" height="1024" loading="lazy"></div></section></main>
<footer class="footer"><div class="wrap"><span class="site-identity"><span>© 2026 Baer &amp; Hoggo Games</span><span class="site-countries"><span><svg class="site-flag" role="img" aria-label="Netherlands" viewBox="0 0 16 11"><use href="assets/ui-icons.svg#nl"></use></svg>Netherlands</span><span><svg class="site-flag" role="img" aria-label="Estonia" viewBox="0 0 16 11"><use href="assets/ui-icons.svg#ee"></use></svg>Estonia</span></span></span><div class="footer-links"><a href="{STEAM}" class="site-text-link"><svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#steam"></use></svg><span>Steam</span></a><a href="{C['discord']}" class="site-text-link"><svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#discord"></use></svg><span>Discord</span></a><a href="{C['youtube']}" class="site-text-link"><svg class="site-icon" aria-hidden="true" focusable="false"><use href="assets/ui-icons.svg#youtube"></use></svg><span>Video updates</span></a><a href="{C['website']}">Website</a></div><span>Facts checked {C['verified']}</span></div></footer>
<dialog id="lightbox" class="lightbox" aria-labelledby="lightbox-title"><div class="lightbox-top"><strong id="lightbox-title"></strong><button id="lightbox-close" aria-label="Close screenshot">Close ×</button></div><img id="lightbox-image" alt=""><p class="lightbox-caption" id="lightbox-caption"></p><div class="lightbox-nav"><button id="previous" aria-label="Previous screenshot">← Previous</button><span id="lightbox-counter" class="micro"></span><a id="lightbox-download" download>Download original JPG ↓</a><button id="next" aria-label="Next screenshot">Next →</button></div></dialog>
</body></html>'''


W, H = 595.276, 841.89
PAPER, INK, MUTED, LINE, PALE = map(HexColor, ['#f6f3e9', '#183c2f', '#5c6b5f', '#cbd1bf', '#e8ecde'])
FONT_DIR = ROOT / 'assets' / 'fonts'
for name, file, weight in [('Display', 'Baloo2.ttf', 800), ('Body', 'Nunito.ttf', 400), ('BodyBold', 'Nunito.ttf', 700)]:
    # PDF text uses static instances of the same variable fonts as the game and web pages.
    font = VariableFont(FONT_DIR / file)
    font = instantiateVariableFont(font, {'wght': weight}, inplace=True, updateFontNames=True)
    font_data = BytesIO()
    font.save(font_data)
    font_data.seek(0)
    pdfmetrics.registerFont(TTFont(name, font_data))


def make_pdf():
    cv = canvas.Canvas(str(DOWNLOADS / 'Farmion-Press-Kit.pdf'), pagesize=(W, H), pageCompression=1)
    cv.setTitle('Farmion | Press Kit | September 2026')
    cv.setAuthor(C['studio'])
    cv.setSubject('Farmion game facts, features, screenshots, and press contact')
    cv.setCreator('Farmion press kit / ReportLab')

    def rect(x, top, w, h, color):
        cv.setFillColor(color); cv.rect(x, H-top-h, w, h, stroke=0, fill=1)

    def line(x1, top, x2):
        cv.setStrokeColor(LINE); cv.setLineWidth(.6); cv.line(x1, H-top, x2, H-top)

    def text(value, x, top, size=10, font='Body', color=INK):
        cv.setFillColor(color); cv.setFont(font, size); cv.drawString(x, H-top-size, value)

    def para(value, x, top, width, size=10.5, leading=16, font='Body', color=MUTED):
        style=ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=0)
        p=Paragraph(value,style); _,h=p.wrap(width,H); p.drawOn(cv,x,H-top-h); return h

    def image(path, x, top, width, height):
        cv.drawImage(str(ROOT/path),x,H-top-height,width,height,mask='auto',preserveAspectRatio=True,anchor='c')

    def logo(x, top, width):
        # Position the original transparent PNG by its visible alpha bounds.
        scale=width/1210
        cv.drawImage(str(ROOT/'assets/brand/farmion-logo.png'),x-35*scale,H-top-(720-206)*scale,1280*scale,720*scale,mask='auto')

    def link(label, url, x, top, size=10):
        text(label,x,top,size,'BodyBold'); tw=pdfmetrics.stringWidth(label,'BodyBold',size)
        cv.linkURL(url,(x,H-top-size-3,x+tw,H-top+3),relative=0,thickness=0)

    def base(page, section):
        rect(0,0,W,H,PAPER)
        text('FARMION  /  PRESS KIT',42,27,8,'BodyBold')
        text(C['edition'].upper(),421,27,8,'Body',MUTED)
        line(42,53,W-42)
        line(42,798,W-42)
        text('BAER & HOGGO GAMES',42,809,7.5,'BodyBold',MUTED)
        text(section.upper(),238,809,7.5,'Body',MUTED)
        text(f'{page:02d} / 05',515,809,7.5,'Body',MUTED)

    # 1 / Cover: a proper cover composition, not a browser printout.
    base(1,'Overview')
    logo(42,80,248)
    text('Farmion.',42,166,43,'Display')
    text('Press kit.',42,219,39,'Display')
    image('assets/screenshots/steam-00.jpg',42,353,511,287.44)
    text('IN-GAME SCREENSHOT / IN DEVELOPMENT',42,650,7,'BodyBold',MUTED)
    rect(42,683,511,63,INK)
    text('PLANNED RELEASE',57,695,7.3,'BodyBold',PALE)
    text('Q4 2026 / Early Access',57,712,11,'Body',PAPER)
    text('PLATFORM',296,695,7.3,'BodyBold',PALE)
    text('Windows PC / Steam',296,712,11,'Body',PAPER)
    link('Steam',STEAM,42,764,9)
    text('Solo & online co-op',423,764,9,'Body',MUTED)
    cv.showPage()

    # 2 / Fact sheet and descriptions.
    base(2,'Game facts')
    text('01 / GAME FACTS',42,77,8,'BodyBold',MUTED)
    text('About the game.',42,103,31,'Display')
    rect(42,164,171,428,PALE)
    text('Factsheet.',58,181,22,'Display')
    y=224
    for key,value in C['facts']:
        text(key.upper(),58,y,7,'BodyBold',MUTED)
        para(E(value.replace('·','/')),58,y+13,138,9.2,13,'Body',INK)
        y+=43
    text('GAME',238,170,8,'BodyBold',MUTED)
    h=para(E(C['short']),238,193,313,12,18,'Body',INK)
    text('PROGRESSION',238,193+h+28,8,'BodyBold',MUTED)
    overview='Farm progress belongs to the save.<br/><br/>Character progress belongs to each player: cosmetics and small gameplay unlocks, such as harvesting larger areas.'
    para(overview,238,193+h+49,313,10.1,15.8)
    rect(238,511,313,86,PALE)
    text('PROPOSED BASE PRICES',251,522,8,'BodyBold',MUTED)
    text(' / '.join(value for _,value in C['prices']),251,542,12,'Body')
    text('Planned launch discount: 15% for the first 8 days.',251,568,9,'Body',MUTED)
    text('ABOUT THE STUDIO',42,623,8,'BodyBold',MUTED)
    para(E(C['studio_copy']),42,646,240,10,15.5)
    for i, person in enumerate(C['team']):
        top = 623 + i * 78
        text(person['name'],319,top,13,'Display')
        colors = ['#ae1c28','#ffffff','#21468b'] if person['flag'] == 'nl' else ['#0072ce','#000000','#ffffff']
        for stripe, color in enumerate(colors):
            rect(531,top+5+stripe*4,20,4,HexColor(color))
        text(person['role'],319,top+23,9.5,'Body',MUTED)
        if 'linkedin' in person:
            link('LinkedIn',person['linkedin'],319,top+42,9)
    cv.showPage()

    # 3 / Six editorial feature blocks, with breathing room.
    base(3,'Gameplay')
    text('02 / GAMEPLAY',42,77,8,'BodyBold',MUTED)
    text('Gameplay.',42,104,36,'Display')
    for i,(title,body) in enumerate(C['features']):
        x=42+(i%2)*269; top=225+(i//2)*143
        line(x,top,x+241)
        text(f'0{i+1}',x,top+13,12,'Display',MUTED)
        ht=para(E(title),x+29,top+12,211,17,20,'Display',INK)
        para(E(body),x+29,top+22+ht,211,9.4,14)
    rect(42,674,511,96,PALE)
    text('BUSINESSES',61,690,8,'BodyBold',MUTED)
    para('Restaurants, cafés, groceries, and floristry.',61,711,378,10,15)
    image('assets/brand/chicken.png',463,681,75,80)
    cv.showPage()

    # 4 / Six full-frame screenshots, no generated gameplay imagery.
    base(4,'Screenshot selection')
    text('03 / SCREENSHOTS',42,77,8,'BodyBold',MUTED)
    text('Screenshots.',42,104,29,'Display')
    selection=[C['screenshots'][i] for i in [0,2,3,4,5,6]]
    for i,s in enumerate(selection):
        x=42+(i%2)*265; top=169+(i//2)*194
        image(f'assets/screenshots/steam-{s["id"]:02d}.jpg',x,top,246,138.375)
        text(s['title'],x,top+147,10,'BodyBold')
        sw, sh = Image.open(ROOT/f'assets/screenshots/steam-{s["id"]:02d}.jpg').size
        text(f'IN-GAME / {sw} x {sh}',x,top+165,7,'Body',MUTED)
    para('21 screenshots in Farmion-Screenshots.zip. Credit: Farmion / Baer &amp; Hoggo Games.',42,757,511,8.5,12)
    cv.showPage()

    # 5 / Brand assets, practical press resources, and live contact links.
    base(5,'Assets & contact')
    text('04 / PRESS RESOURCES',42,77,8,'BodyBold',MUTED)
    text('Downloads.',42,104,32,'Display')
    rect(42,162,511,138,PALE)
    logo(131,181,333)
    text('FARMION LOGO',257,283,7,'BodyBold',MUTED)
    rows=[('01','Screenshots','21 game screenshots (JPG).'),('02','Brand artwork','Game and studio logos, mascots, and chicken artwork (PNG).'),('03','Press copy','Descriptions, game facts, and studio details (TXT).')]
    for i,(n,title,body) in enumerate(rows):
        y=322+i*64; line(42,y,553); text(n,43,y+16,13,'Display',MUTED)
        text(title,78,y+12,12,'BodyBold'); para(body,78,y+32,467,9.5,13)
    rect(42,590,511,149,INK)
    text('PRESS CONTACT',59,605,9,'BodyBold',PALE)
    text('Baer & Hoggo Games',59,627,27,'Display',PAPER)
    text(C['contact'],59,671,17,'Body',PAPER)
    tw=pdfmetrics.stringWidth(C['contact'],'Body',17)
    cv.linkURL('mailto:'+C['contact'],(59,H-698,59+tw,H-669),relative=0,thickness=0)
    link('Steam',STEAM,42,762,9)
    link('Official website',C['website'],105,762,9)
    link('Video updates',C['youtube'],214,762,9)
    cv.save()


def text_copy():
    lines=['FARMION | PRESS COPY', 'Baer & Hoggo Games', 'Facts checked: '+C['verified'],'','FACT SHEET']
    lines += [f'{k}: {v}' for k,v in C['facts']]
    lines += ['', 'SHORT DESCRIPTION', C['short'], '', 'FULL DESCRIPTION', C['long'], '', 'FEATURES']
    lines += [f'{title}\n{body}\n' for title,body in C['features']]
    lines += ['', 'PROPOSED REGIONAL PRICING', C['pricing_note']]
    lines += [f'{code}: {price}' for code,price in C['prices']]
    lines += ['', 'ABOUT THE STUDIO', C['studio_copy'], '', 'TEAM']
    for person in C['team']:
        lines += [f"{person['name']} - {person['role']} - {person['country']}"]
        if 'linkedin' in person: lines += [person['linkedin']]
    lines += ['','PRESS CONTACT',C['contact'],'','OFFICIAL LINKS',STEAM,C['website'],C['discord'],C['youtube'],'','DEVELOPMENT STATUS','Farmion is in development and planned to enter Steam Early Access in Q4 2026. Features and visuals may change. Community creation tools are planned; Steam Workshop support is not confirmed.','', 'IMAGE CREDIT','Farmion / Baer & Hoggo Games.']
    return '\n'.join(lines)+'\n'


def package():
    screenshots=list(sorted((ROOT/'assets/screenshots').glob('*.jpg')))
    brands=list(sorted((ROOT/'assets/brand').glob('*.png')))
    with zipfile.ZipFile(DOWNLOADS/'Farmion-Screenshots.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in screenshots:z.write(p,'Farmion-Screenshots/'+p.name)
        z.writestr('Farmion-Screenshots/README.txt','Original Steam gallery images, 1920 pixels wide. Heights vary; original aspect ratios are preserved. In development.\nCredit: Farmion / Baer & Hoggo Games.\nSee asset-manifest.json in the full press assets for source URLs and captions.\n')
    with zipfile.ZipFile(DOWNLOADS/'Farmion-Logos.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in brands:z.write(p,'Farmion-Logos/'+p.name)
        z.writestr('Farmion-Logos/README.txt','Original transparent PNG brand artwork from baerandhoggo.com.\nPlease preserve proportions and colors. These are brand assets, not gameplay screenshots.\nCredit: Farmion / Baer & Hoggo Games.\n')
    with zipfile.ZipFile(DOWNLOADS/'Farmion-Press-Assets.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in screenshots+brands:z.write(p,'Farmion-Press-Assets/'+p.relative_to(ROOT).as_posix())
        for name in ['Farmion-Press-Kit.pdf','Farmion-Press-Copy.txt']:z.write(DOWNLOADS/name,'Farmion-Press-Assets/'+name)
        z.write(ROOT/'asset-manifest.json','Farmion-Press-Assets/asset-manifest.json')
        z.writestr('Farmion-Press-Assets/README.txt','FARMION / PRESS ASSETS\nSeptember 2026\n\nIncludes 21 original in-game screenshots, original transparent brand artwork, a five-page PDF, and editable plain-text press copy.\n\nCredit: Farmion / Baer & Hoggo Games.\nContact: '+C['contact']+'\nSteam: '+STEAM+'\n\nAll screenshots show a game in development. Logo and chicken/mascot artwork are separate brand assets. No AI-generated gameplay images have been added.\nSources and SHA-256 fingerprints are in asset-manifest.json.\n')


def manifest():
    steam=json.loads((SOURCE/'steam-source.json').read_text(encoding='utf-8-sig'))
    origin={f'assets/screenshots/steam-{s["id"]:02d}.jpg':s['path_full'] for s in steam['screenshots']}
    origin.update({'assets/brand/farmion-logo.png':'https://baerandhoggo.com/assets/farmion-logo.png','assets/brand/studio-logo.png':'https://baerandhoggo.com/logo.png','assets/brand/studio-mascot.png':'https://baerandhoggo.com/assets/bh-mascot.png','assets/brand/chicken.png':'https://baerandhoggo.com/assets/chicken.png'})
    selected={f'assets/screenshots/steam-{s["id"]:02d}.jpg':s for s in C['screenshots']}
    assets=[]
    for path,url in origin.items():
        p=ROOT/path
        with Image.open(p) as im:size=im.size
        record={'file':path,'source':url,'size':size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'kind':'in-game screenshot' if 'screenshots/' in path else 'brand artwork','modifications':'none'}
        if path in selected:record['caption']=selected[path]['caption']
        assets.append(record)
    data={'game':'Farmion','credit':C['studio'],'verified':C['verified'],'fact_sources':[C['steam'],C['website']],'new_generated_images':False,'assets':assets}
    (ROOT/'asset-manifest.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    (ROOT/'index.html').write_text(page_html(),encoding='utf-8')
    (DOWNLOADS/'Farmion-Press-Copy.txt').write_text(text_copy(),encoding='utf-8')
    manifest();make_pdf();package()
    print('Built press page, five-page PDF, copy, manifest, and three asset archives.')
