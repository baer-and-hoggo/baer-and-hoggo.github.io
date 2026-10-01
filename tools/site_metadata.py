"""Validate public site metadata and generate the canonical sitemap."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://baerandhoggo.com"
SITEMAP_URL = f"{ORIGIN}/sitemap.xml"
NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
LIVE_ANSWER_AGENTS = (
    "OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "Claude-User",
    "PerplexityBot", "Perplexity-User",
)


class PageMetadata(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.canonicals = []
        self.excluded = False
        self.headings = []
        self.json_ld = []
        self.json_script = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonicals.append(attrs.get("href", ""))
        if tag == "meta":
            if attrs.get("name", "").lower() in ("robots", "googlebot", "bingbot"):
                self.excluded |= "noindex" in attrs.get("content", "").lower()
            self.excluded |= attrs.get("http-equiv", "").lower() == "refresh"
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self.json_script = []

    def handle_data(self, data):
        if self.json_script is not None:
            self.json_script.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.json_script is not None:
            self.json_ld.append(json.loads("".join(self.json_script)))
            self.json_script = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def public_pages():
    pages = {}
    for path in sorted(ROOT.rglob("*.html")):
        relative = path.relative_to(ROOT)
        if any(part.startswith(".") for part in relative.parts) or relative.parts[0] == "tools":
            continue
        if relative == Path("404.html"):
            continue
        metadata = PageMetadata(path.read_text(encoding="utf-8"))
        if metadata.excluded:
            continue
        url_path = "/" + relative.as_posix()
        if url_path.endswith("/index.html"):
            url_path = url_path[:-len("index.html")]
        expected = ORIGIN + url_path
        require(metadata.canonicals == [expected],
                f"{relative}: declare exactly one canonical URL: {expected}")
        pages[expected] = metadata
    require(f"{ORIGIN}/" in pages, "The public homepage is missing")
    return pages


def validate_homepage(metadata):
    levels = metadata.headings
    require(levels.count(1) == 1, "Homepage must retain exactly one h1")
    require(len(set(levels)) > 1, "Homepage must retain more than one heading level")
    require(levels[0] == 1 and all(b <= a + 1 for a, b in zip(levels, levels[1:])),
            "Homepage heading outline must start at h1 without skipped levels")
    require(len(metadata.json_ld) == 1, "Homepage must contain one Organization JSON-LD block")
    organization = metadata.json_ld[0]
    require(isinstance(organization, dict), "Homepage JSON-LD must describe an organization")
    require(organization.get("@context") == "https://schema.org"
            and organization.get("@type") == "Organization",
            "Homepage JSON-LD must declare schema.org Organization")
    require(organization.get("name") == "Baer & Hoggo Games"
            and organization.get("url") == f"{ORIGIN}/",
            "Organization name and URL must match the studio")
    logo = urlsplit(organization.get("logo", ""))
    require(logo.scheme == "https" and logo.netloc == urlsplit(ORIGIN).netloc
            and (ROOT / logo.path.lstrip("/")).is_file(),
            "Organization logo must point to a real public site asset")
    profiles = organization.get("sameAs", [])
    require(isinstance(profiles, list) and len(profiles) >= 3
            and len(set(profiles)) == len(profiles),
            "Organization needs at least three distinct confirmed official profile URLs")
    for profile in profiles:
        url = urlsplit(profile)
        require(url.scheme == "https" and url.netloc
                and url.netloc != urlsplit(ORIGIN).netloc,
                f"sameAs must be an external HTTPS profile URL: {profile}")


def validate_robots(pages):
    text = (ROOT / "robots.txt").read_text(encoding="utf-8")
    robots = RobotFileParser()
    robots.parse(text.splitlines())
    require(robots.site_maps() == [SITEMAP_URL],
            f"robots.txt must declare Sitemap: {SITEMAP_URL}")
    for agent in (*LIVE_ANSWER_AGENTS, "Googlebot", "bingbot"):
        for url in pages:
            require(robots.can_fetch(agent, url), f"robots.txt unexpectedly blocks {agent}: {url}")


def sitemap_bytes(pages):
    require(len(pages) <= 50000, "Sitemap exceeds 50,000 URLs; split it before deploying")
    ET.register_namespace("", NAMESPACE)
    document = ET.Element(f"{{{NAMESPACE}}}urlset")
    for url in sorted(pages):
        require(len(url) < 2048, f"Sitemap URL exceeds the protocol length limit: {url}")
        entry = ET.SubElement(document, f"{{{NAMESPACE}}}url")
        ET.SubElement(entry, f"{{{NAMESPACE}}}loc").text = url
    ET.indent(document, space="  ")
    data = ET.tostring(document, encoding="utf-8", xml_declaration=True) + b"\n"
    require(len(data) <= 50 * 1024 * 1024, "Sitemap exceeds the 50 MB uncompressed limit")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate the committed sitemap without writing")
    args = parser.parse_args()
    pages = public_pages()
    validate_homepage(pages[f"{ORIGIN}/"])
    validate_robots(pages)
    data = sitemap_bytes(pages)
    sitemap = ROOT / "sitemap.xml"
    if args.check:
        require(sitemap.is_file() and sitemap.read_text(encoding="utf-8") == data.decode("utf-8"),
                "sitemap.xml is stale; run python tools/site_metadata.py")
    else:
        sitemap.write_bytes(data)
    print(f"PASS: Organization JSON-LD, heading outline, crawler rules, and {len(pages)} canonical pages")
    for url in sorted(pages):
        print(url)


if __name__ == "__main__":
    main()
