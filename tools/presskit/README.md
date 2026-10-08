# Farmion press kit

The public kit lives in `press/`. It is a static page with no build step required by GitHub Pages. The Farmion page at `/#farmion` shares its screenshot files and visual style. The studio landing page and its voxel transition remain in place.

## Editing

Do not use em dashes in promotional or press kit copy, including page titles and PDF metadata.

- `content.json`: facts, descriptions, contact email, gallery selection. The price is the `Price` fact row and stays TBD until it is announced.
- `page.py`: the press page template. `python tools/presskit/page.py` rebuilds `press/index.html` with only Pillow installed.
- `build.py`: builds the press HTML (through `page.py`), paginated PDF, text copy, source manifest, and three ZIP downloads.
- `../../press/styles.css` and `../../press/app.js`: press page presentation and interactions.
- `../../press/shared.css`: shared headers, heroes, banners, typography, buttons, and footer layout for both web pages.
- `../../press/assets/ui-icons.svg`: shared navigation/social icons and Netherlands/Estonia flags. Icon buttons have accessible names and hover/focus labels.
- `../../index.html`, `../../farmion.css`, and `../../farmion.js`: the public Farmion page.
- `../../assets/greenhouse-frame.svg`: decorative greenhouse frame; also copied to `press/assets/brand/` for the self-contained press page.

After editing the main page's CSS or JS, run `python tools/stamp_assets.py` so browsers fetch the new files; the press page tags its own.

Run `python tools/presskit/build.py` from the repo root with Python, Pillow, ReportLab, fontTools, and pypdf installed. The PDF builder embeds static instances of the bundled game fonts. Run `python -m http.server 8766 --bind 127.0.0.1` from the repo root to preview the whole site.

Both pages and the PDF use Farmion's in-game fonts: Baloo 2 at weight 800 for headings and Nunito for body text. The unmodified variable font files in `press/assets/fonts/` come from `Content/VoxelFarm/UI/Fonts/` in the game project. Their SIL Open Font License is included in `OFL.txt`; `fonts.css` is shared by the main site and press page.

The website hero's release line (launch window and price) also lives in `index.html`; keep it in step with the `Planned release` and `Price` facts.

## Sources

Game facts and screenshots were checked on September 24, 2026 against the [Steam page](https://store.steampowered.com/app/2426390/Farmion/) and [studio site](https://baerandhoggo.com/#farmion). `steam-source.json` preserves the Steam metadata used to build the image source manifest. All 21 original screenshot files are 1920 pixels wide; heights vary and original aspect ratios are preserved in downloads. The logo and mascot PNGs are unchanged originals from the studio website.

Jesse confirmed `baerandhoggo@gmail.com` as the press email. The price reads TBD on every page and download until it is announced. The Steam release window remains planned Q4 2026 / Early Access.

Jesse clarified progression: farm progress belongs to each save. Character progress belongs to each player and includes cosmetics and small gameplay unlocks, such as harvesting larger areas.

Jesse supplied the European Union studio bio and the developer profiles for Jesse van Vliet (Netherlands, with LinkedIn) and Kristo Hõrrak (Estonia). Those details live in `content.json` and populate the press page, PDF, and text download.

The information structure follows [presskit()](https://dopresskit.com/): clear facts, reusable descriptions, separate screenshot/logo archives, and direct contact. This is an independent static implementation, not an installation of its PHP software.

No AI-generated gameplay images were added. The new greenhouse frame is a decorative SVG overlay; the gameplay images are unchanged beneath it.

## Publishing

The existing Pages workflow deploys pushes to `main`. Review the local changes and obtain Jesse's approval before pushing.

The intended press URL is `https://baerandhoggo.com/press/`.

The October 8, 2026 feature refresh was approved by Jesse after review against the game devlogs, commits and village/Cheesery task records. It adds village progression, resident families, visitor transport and Cheesery to the press copy. Feature cards continue onto another PDF page when needed.
