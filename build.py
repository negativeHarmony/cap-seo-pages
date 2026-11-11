"""Build the static site: one page per row of content/pages.csv, plus an index, sitemap and robots.txt."""
from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from jinja2 import Environment, FileSystemLoader, select_autoescape

from pages import load_pages

SITE_NAME = "Crown Cover Co."
BASE_URL = "https://negativeharmony.github.io/cap-seo-pages/"
STORE_URL = ""  # set to your store's address once it exists, and the shop button appears
GOOGLE_VERIFICATION = "bdqtT8QO7ATIYSB0Kpvnw5TpCxEKoLDPyKWJNV9Zej4"  # paste the code from Google Search Console here
CONTENT = Path("content/pages.csv")
OUT = Path("docs")


def build() -> int:
    pages = load_pages(CONTENT)
    env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
    shared = {"site_name": SITE_NAME, "store_url": STORE_URL, "year": date.today().year, "google_verification": GOOGLE_VERIFICATION}

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / ".nojekyll").touch()

    page_template = env.get_template("page.html")
    for page in pages:
        folder = OUT / page.slug
        folder.mkdir()
        html = page_template.render(
            page=page, title=page.title, description=page.meta_description,
            url=f"{BASE_URL}{page.slug}/", home_url="../", **shared,
        )
        (folder / "index.html").write_text(html, encoding="utf-8")

    index_html = env.get_template("index.html").render(
        pages=sorted(pages, key=lambda p: p.h1),
        title=f"Cap Guides | {SITE_NAME}",
        description="Practical guides to choosing caps and hats for thinning hair and hair loss.",
        url=BASE_URL, home_url="./", **shared,
    )
    (OUT / "index.html").write_text(index_html, encoding="utf-8")

    urls = [BASE_URL] + [f"{BASE_URL}{page.slug}/" for page in pages]
    entries = "\n".join(f"  <url><loc>{escape(url)}</loc></url>" for url in urls)
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n</urlset>\n"
    )
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")

    print(f"Built {len(pages)} pages + index, sitemap.xml and robots.txt in {OUT}/")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(build())
    except ValueError as e:
        print(f"Build stopped. Nothing was published.\n{e}")
        raise SystemExit(1)