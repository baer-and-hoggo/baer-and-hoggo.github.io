# Public site metadata

Run `python tools/site_metadata.py` from the website root to validate the homepage
and robots.txt and regenerate sitemap.xml. Run with `--check` to verify the
committed sitemap without changing files. GitHub Pages runs the generator before
uploading the site, so a new public page updates the deployed sitemap.

Each public HTML page needs exactly one absolute canonical link using
`https://baerandhoggo.com`. Directory index pages use trailing slash URLs.
The generator excludes tools, hidden directories, the error page, pages marked
noindex, and HTML redirects. Do not place private content in the public website
repository. A missing or mismatched canonical fails deployment.

The homepage Organization JSON-LD uses the studio name, its existing logo, and
the X, Instagram and YouTube profiles already linked by the site. Confirm account
ownership and public access before changing sameAs; never substitute a game's
store listing or an individual developer's profile for the studio.

The homepage outline retains one h1 followed by h2 sections. Deployment validation
rejects additional h1 tags, a single-level outline, or skipped heading levels.
These checks do not rewrite the page's claims.

robots.txt explicitly permits the homepage and public pages for OAI-SearchBot,
ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot and Perplexity-User.
This preserves the initially unrestricted robots access. The existing
Cloudflare content-signal explanatory comments are retained in this file because
Cloudflare stops supplying that preamble when an origin robots.txt exists. No
content-signal permission or training restriction is added or changed. After any
policy change, fetch the live robots.txt and public pages again: Cloudflare can
affect the delivered response.

Crawler definitions:

- [OpenAI](https://developers.openai.com/api/docs/bots)
- [Anthropic](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)
- [Perplexity](https://docs.perplexity.ai/docs/resources/perplexity-crawlers)
- [Sitemap protocol](https://www.sitemaps.org/protocol.html)
