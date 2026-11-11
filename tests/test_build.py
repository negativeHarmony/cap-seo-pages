import shutil
from pathlib import Path

import pytest

import build
from test_pages import GOOD, second, write_csv

PROJECT = Path(__file__).resolve().parent.parent


@pytest.fixture
def site(tmp_path, monkeypatch):
    """A throwaway copy of the project: the real templates, an empty content folder."""
    shutil.copytree(PROJECT / "templates", tmp_path / "templates")
    (tmp_path / "content").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_builds_every_file(site):
    write_csv(site / "content/pages.csv", [GOOD, second()])
    build.build()
    files = {str(p.relative_to(site / "docs")) for p in (site / "docs").rglob("*") if p.is_file()}
    assert files == {
        ".nojekyll", "index.html", "sitemap.xml", "robots.txt",
        "best-caps-for-thinning-crown/index.html", "hats-for-receding-hairline/index.html",
    }


def test_canonical_is_absolute_and_navigation_is_relative(site):
    write_csv(site / "content/pages.csv", [GOOD])
    build.build()
    html = (site / "docs/best-caps-for-thinning-crown/index.html").read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="{build.BASE_URL}best-caps-for-thinning-crown/">' in html
    assert '<a href="../">More guides</a>' in html


def test_sitemap_lists_every_page(site):
    write_csv(site / "content/pages.csv", [GOOD, second()])
    build.build()
    assert (site / "docs/sitemap.xml").read_text(encoding="utf-8").count("<url>") == 3


def test_content_is_escaped(site):
    write_csv(site / "content/pages.csv", [{**GOOD, "intro": "A" * 150 + " <script>alert(1)</script>"}])
    build.build()
    html = (site / "docs/best-caps-for-thinning-crown/index.html").read_text(encoding="utf-8")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_bad_content_leaves_the_old_site_alone(site):
    write_csv(site / "content/pages.csv", [GOOD])
    build.build()
    write_csv(site / "content/pages.csv", [{**GOOD, "title": "x" * 61}])
    with pytest.raises(ValueError):
        build.build()
    assert (site / "docs/best-caps-for-thinning-crown/index.html").exists()