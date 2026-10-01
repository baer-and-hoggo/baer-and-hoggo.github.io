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

from page import page_html

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


W, H = 595.276, 841.89
# The PDF uses the same kit as the web pages: cream paper, sky, bridle leather with a
# stitched seam, sewn name tapes, dark pockets for pictures and brass for links.
CREAM, INK, MUTED, SKY = map(HexColor, ['#f8efd9', '#3b2a1e', '#7a6250', '#a3def4'])
HIDE, HIDE_EDGE, STITCH = map(HexColor, ['#55311f', '#301a10', '#c9b48e'])
TAPE, TAPE_INK, POCKET, CANVAS = map(HexColor, ['#ece2c4', '#33291b', '#333a2d', '#3a4033'])
THREAD, PRESSED, BRASS = map(HexColor, ['#ffd98a', '#f3dcbc', '#e2c079'])
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
    cv.setTitle(f'Farmion | Press Kit | {C["edition"]}')
    cv.setAuthor(C['studio'])
    cv.setSubject('Farmion game facts, features, screenshots, and press contact')
    cv.setCreator('Farmion press kit / ReportLab')

    def rect(x, top, w, h, color, radius=0):
        cv.setFillColor(color)
        if radius: cv.roundRect(x, H-top-h, w, h, radius, stroke=0, fill=1)
        else: cv.rect(x, H-top-h, w, h, stroke=0, fill=1)

    def text(value, x, top, size=10, font='Body', color=INK):
        cv.setFillColor(color); cv.setFont(font, size); cv.drawString(x, H-top-size, value)

    def centered(value, top, size, font, color=INK):
        cv.setFillColor(color); cv.setFont(font, size); cv.drawCentredString(W/2, H-top-size, value)

    def para(value, x, top, width, size=10.5, leading=16, font='Body', color=INK):
        style = ParagraphStyle('p', fontName=font, fontSize=size, leading=leading, textColor=color, spaceAfter=0)
        p = Paragraph(value, style); _, h = p.wrap(width, H); p.drawOn(cv, x, H-top-h); return h

    def image(path, x, top, width, height):
        cv.drawImage(str(path), x, H-top-height, width, height, mask='auto', preserveAspectRatio=True, anchor='c')

    def logo(x, top, width):
        # Position the original transparent PNG by its visible alpha bounds.
        scale = width/1210
        cv.drawImage(str(ROOT/'assets/brand/farmion-logo.png'), x-35*scale, H-top-(720-206)*scale, 1280*scale, 720*scale, mask='auto')

    def leather(x, top, w, h):
        rect(x, top+2, w, h, HIDE_EDGE, 12)
        rect(x, top, w, h, HIDE, 12)
        cv.setStrokeColor(STITCH); cv.setLineWidth(1.1); cv.setDash(4, 3)
        cv.roundRect(x+5, H-top-h+5, w-10, h-10, 8, stroke=1, fill=0)
        cv.setDash()

    def tape(label, x, top, size=14):
        tw = pdfmetrics.stringWidth(label, 'Display', size)
        rect(x, top, tw+20, size+9, TAPE, 1.5)
        text(label, x+10, top+3, size, 'Display', TAPE_INK)

    def pocket(path, x, top, w, h):
        rect(x, top, w, h, POCKET, 4)
        image(path, x+4, top+4, w-8, h-8)
        for rx in (x+1, x+w-1):
            cv.setFillColor(BRASS); cv.circle(rx, H-top-1, 2.6, stroke=0, fill=1)

    def link(label, url, x, top, size=10, color=INK):
        text(label, x, top, size, 'BodyBold', color); tw = pdfmetrics.stringWidth(label, 'BodyBold', size)
        cv.linkURL(url, (x, H-top-size-3, x+tw, H-top+3), relative=0, thickness=0)
        return tw

    def chips(items, x, top, width, size=9.5):
        cx, cy = x, top
        for item in items:
            tw = pdfmetrics.stringWidth(item, 'BodyBold', size) + 16
            if cx + tw > x + width: cx, cy = x, cy + size + 15
            rect(cx, cy, tw, size+9, POCKET, 4)
            text(item, cx+8, cy+4, size, 'BodyBold', PRESSED)
            cx += tw + 7
        return cy + size + 9 - top

    def base(page, section):
        rect(0, 0, W, H, CREAM)
        text(f'farmion / press kit / {section}', 42, 808, 8, 'BodyBold', MUTED)
        text(f'{page} / 5', 527, 808, 8, 'Body', MUTED)

    # 1 / Cover: sky, logo, screenshots, and the facts on a leather strap.
    rect(0, 0, W, H, CREAM)
    rect(0, 0, W, 262, SKY)
    logo(122, 48, 351)
    centered('A cozy voxel farming game. Grow crops, run little shops', 150, 13, 'BodyBold')
    centered('and play with friends.', 168, 13, 'BodyBold')
    tw = pdfmetrics.stringWidth('press kit', 'Display', 18) + 24
    rect((W-tw)/2, 198, tw, 27, TAPE, 1.5); centered('press kit', 202, 18, 'Display', TAPE_INK)
    pocket(ROOT/'assets/screenshots/steam-00.jpg', 42, 300, 511, 291)
    pocket(ROOT/'assets/screenshots/steam-06.jpg', 42, 608, 250, 130)
    pocket(ROOT/'assets/screenshots/steam-05.jpg', 303, 608, 250, 130)
    leather(42, 752, 511, 46)
    for i, (label, value) in enumerate([('release', 'Q4 2026 · Early Access'), ('platform', 'Windows PC'), ('play', 'Solo & online co-op')]):
        text(label, 60+i*170, 761, 7.5, 'BodyBold', STITCH)
        text(value, 60+i*170, 774, 10.5, 'BodyBold', PRESSED)
    text(f'Baer & Hoggo Games · {C["edition"]}', 42, 812, 8, 'BodyBold', MUTED)
    cv.showPage()

    # 2 / About: facts, descriptions, prices, studio.
    base(2, 'about')
    leather(42, 40, 511, 404)
    tape('about', 56, 54)
    rect(56, 90, 200, 340, CANVAS, 5)
    y = 102
    for key, value in C['facts']:
        text(key.lower(), 68, y, 7.5, 'BodyBold', STITCH)
        para(E(value), 68, y+12, 178, 9.2, 12.5, 'BodyBold', PRESSED)
        y += 41
    h = para(E(C['short']), 272, 92, 266, 11.5, 17, 'Body', PRESSED)
    rect(272, 110+h, 266, 82, CANVAS, 5)
    text('regional prices', 284, 120+h, 8, 'BodyBold', STITCH)
    text('   '.join(f'{code} {price}' for code, price in C['prices']), 284, 136+h, 11.5, 'BodyBold', PRESSED)
    para(E(C['pricing_note']), 284, 156+h, 244, 8.8, 12.5, 'Body', PRESSED)
    leather(42, 464, 511, 300)
    tape('studio', 56, 478)
    para(E(C['studio_copy']), 56, 512, 483, 10.5, 16, 'Body', PRESSED)
    for i, person in enumerate(C['team']):
        x = 56 + i*246
        rect(x, 560, 237, 92, CANVAS, 5)
        text(person['name'], x+12, 572, 14, 'Display', PRESSED)
        colors = ['#ae1c28', '#ffffff', '#21468b'] if person['flag'] == 'nl' else ['#0072ce', '#000000', '#ffffff']
        for stripe, color in enumerate(colors):
            rect(x+205, 575+stripe*4, 20, 4, HexColor(color))
        text(person['role'], x+12, 596, 9.5, 'Body', STITCH)
        if 'linkedin' in person: link('linkedin', person['linkedin'], x+12, 616, 9.5, THREAD)
    image(ROOT/'assets/brand/studio-mascot.png', 430, 664, 110, 90)
    para('Two friends making Farmion alongside their jobs, from the Netherlands and Estonia.', 56, 684, 340, 10.5, 16, 'Body', PRESSED)
    cv.showPage()

    # 3 / In the game.
    base(3, 'in the game')
    ch = chips(C['in_game'], 56, 92, 483)
    leather(42, 40, 511, 66+ch)
    tape('in the game', 56, 54)
    chips(C['in_game'], 56, 92, 483)
    row = 132
    for i, (title, body) in enumerate(C['features']):
        x = 42 + (i % 2)*261; top = 122 + ch + (i//2)*row
        leather(x, top, 250, row - 12)
        tape(title.lower(), x+14, top+14, 12)
        para(E(body), x+14, top+44, 222, 9.3, 13.6, 'Body', PRESSED)
    top = 122 + ch + 3*row
    leather(42, top, 511, 764 - top)
    tape('farmion', 56, top+14, 12)
    para(E(C['short']), 56, top+44, 483, 9.8, 14.5, 'Body', PRESSED)
    cv.showPage()

    # 4 / Screenshots.
    base(4, 'screenshots')
    leather(42, 40, 511, 724)
    tape('screenshots', 56, 54)
    selection = [C['screenshots'][i] for i in [0, 1, 2, 3, 6, 5]]
    for i, s in enumerate(selection):
        x = 58 + (i % 2)*244; top = 98 + (i//2)*214
        pocket(ROOT/f'assets/screenshots/steam-{s["id"]:02d}.jpg', x, top, 235, 136)
        text(s['title'].lower(), x+2, top+144, 10, 'BodyBold', PRESSED)
        sw, sh = Image.open(ROOT/f'assets/screenshots/steam-{s["id"]:02d}.jpg').size
        text(f'in-game · {sw} × {sh}', x+2, top+159, 7.5, 'Body', STITCH)
    para('All 21 screenshots are in Farmion-Screenshots.zip. Please credit Baer &amp; Hoggo Games.', 58, 738, 470, 9, 12, 'Body', STITCH)
    cv.showPage()

    # 5 / Logos and contact.
    base(5, 'logos & contact')
    leather(42, 40, 511, 300)
    tape('logos', 56, 54)
    for i, (file, label) in enumerate([('farmion-logo.png', 'farmion logo'), ('chicken.png', 'chicken'), ('studio-logo.png', 'studio logo'), ('studio-mascot.png', 'baer & hoggo')]):
        x = 56 + i*122
        rect(x, 96, 113, 150, POCKET, 4)
        rect(x+5, 101, 103, 140, SKY, 3)
        image(ROOT/'assets/brand'/file, x+12, 110, 89, 122)
        text(label, x+2, 256, 9, 'BodyBold', PRESSED)
    para('Transparent PNGs in Farmion-Logos.zip. Please keep the original colours and proportions.', 56, 290, 483, 9.5, 14, 'Body', STITCH)
    rect(0, 356, W, 190, SKY)
    image(ROOT/'assets/brand/chicken.png', 262, 370, 70, 70)
    centered('Press contact', 446, 26, 'Display')
    centered(C['contact'], 480, 16, 'BodyBold')
    tw = pdfmetrics.stringWidth(C['contact'], 'BodyBold', 16)
    cv.linkURL('mailto:'+C['contact'], ((W-tw)/2, H-500, (W+tw)/2, H-478), relative=0, thickness=0)
    leather(42, 566, 511, 120)
    tape('links', 56, 578, 13)
    x = 58
    for label, url in [('steam', STEAM), ('epic games store', C['epic']), ('discord', C['discord']), ('website', C['website'])]:
        x += link(label, url, x, 612, 11, THREAD) + 20
    x = 58
    for social in C['socials']:
        x += link(social['name'].lower(), social['url'], x, 634, 11, THREAD) + 20
    para('Farmion is in development; features and visuals may change.', 58, 660, 470, 8.5, 12, 'Body', STITCH)
    cv.save()


def text_copy():
    lines=['FARMION | PRESS COPY', 'Baer & Hoggo Games', 'Facts checked: '+C['verified'],'','FACT SHEET']
    lines += [f'{k}: {v}' for k,v in C['facts']]
    lines += ['', 'SHORT DESCRIPTION', C['short'], '', 'FULL DESCRIPTION', C['long'], '', 'IN THE GAME', ', '.join(C['in_game']), '', 'FEATURES']
    lines += [f'{title}\n{body}\n' for title,body in C['features']]
    lines += ['', 'PROPOSED REGIONAL PRICING', C['pricing_note']]
    lines += [f'{code}: {price}' for code,price in C['prices']]
    lines += ['', 'ABOUT THE STUDIO', C['studio_copy'], '', 'TEAM']
    for person in C['team']:
        lines += [f"{person['name']} - {person['role']} - {person['country']}"]
        if 'linkedin' in person: lines += [person['linkedin']]
    lines += ['','PRESS CONTACT',C['contact'],'','OFFICIAL LINKS',STEAM,C['epic'],C['website'],C['discord'],*[x['name']+': '+x['url'] for x in C['socials']],'','DEVELOPMENT STATUS','Farmion is in development and planned to enter Steam Early Access in Q4 2026. Features and visuals may change. Community creation tools are planned; Steam Workshop support is not confirmed.','', 'IMAGE CREDIT','Farmion / Baer & Hoggo Games.']
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
        z.writestr('Farmion-Press-Assets/README.txt','FARMION / PRESS ASSETS\n'+C['edition']+'\n\nIncludes 21 original in-game screenshots, original transparent brand artwork, a five-page PDF, and editable plain-text press copy.\n\nCredit: Farmion / Baer & Hoggo Games.\nContact: '+C['contact']+'\nSteam: '+STEAM+'\nEpic Games Store: '+C['epic']+'\n\nAll screenshots show a game in development. Logo and chicken/mascot artwork are separate brand assets. No AI-generated gameplay images have been added.\nSources and SHA-256 fingerprints are in asset-manifest.json.\n')


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
    (ROOT/'index.html').write_text(page_html(C),encoding='utf-8')
    (DOWNLOADS/'Farmion-Press-Copy.txt').write_text(text_copy(),encoding='utf-8')
    manifest();make_pdf();package()
    print('Built press page, five-page PDF, copy, manifest, and three asset archives.')
