# Review status - September 24, 2026

- Rendered and inspected all five PDF pages using Baloo 2 and Nunito. The pricing block on page 2 includes all three currency symbols.
- Extracted the final PDF and verified all three proposed prices (USD, GBP, EUR).
- Confirmed the final USD/EUR prices ($10.95 / 9,95€) in both web pages, the factsheet, PDF, text copy, and complete asset archive. Brand artwork and Press copy use matching download labels and return the expected files.
- Checked both web pages in a desktop browser and at phone widths, including the font update at 355px CSS width. No horizontal document overflow observed.
- After extracting the shared layout, compared both pages at 1280px and 390px viewport widths. Header, title, hero image, and fact-banner bounds match exactly. Footer copyright and country labels share the same vertical center.
- Checked named icon links, Dutch/Estonian flags, the USD/EUR hero price, developer profiles and LinkedIn destination. Removed Discord only from the studio landing page's button row.
- Verified that the bundled Baloo 2 and Nunito files match the game's font files exactly. Browser headings use Baloo 2 at weight 800; PDF text embeds Baloo 2 ExtraBold and Nunito Regular/Bold.
- Checked the clean greenhouse center joint on both pages. Farm/save and player/character progression match Jesse's clarification in the site, press descriptions, PDF, and text download.
- Checked press screenshot filters, image dialogs, next navigation, Escape dismissal, and copy-button feedback.
- Checked the game-page gallery, deep-linked screenshot section after reload, and both directions of the existing studio/Farmion transition.
- Retested both transition directions after giving the page/particle fade a single completion loop and clearing the rendered canvas. Both finish with canvas opacity 0, destination opacity 1, and no browser errors.
- Checked the direct regional-pricing link; it opens the price table.
- Verified 93 local HTML references and SVG symbols, with no duplicate HTML attributes. Earlier original-asset hash and shared-frame checks remain valid. All three ZIP archives pass integrity checks; the complete archive contains the current PDF.
- Re-rendered all five PDF pages after shortening the copy. Verified names, Unicode characters, LinkedIn link, studio location, proposed prices, and progression in the PDF text/annotations.
- Updated farming copy across the main page, press page, PDF, and text download to name crops, trees, and flowers; animals and fish are listed as planned husbandry. Re-rendered and reviewed the two affected PDF pages.
- JavaScript syntax checks passed for `farmion.js`, `press/app.js`, and `voxel-transition.js`. `git diff --check` passed.

Reviewed on branch `codex/farmion-press-kit`. The existing main-branch Pages workflow publishes the site.

Preview from the repository root with `python -m http.server 8766 --bind 127.0.0.1`:

- Game page: `http://127.0.0.1:8766/#farmion`
- Press page: `http://127.0.0.1:8766/press/`
- PDF: `press/downloads/Farmion-Press-Kit.pdf`
