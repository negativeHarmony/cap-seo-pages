import csv

import pytest

from pages import load_pages

GOOD = {
    "slug": "best-caps-for-thinning-crown",
    "keyword": "caps for a thinning crown",
    "title": "Best Caps for a Thinning Crown | Crown Cover Co.",
    "meta_description": "Which cap styles cover a thinning crown best and stay comfortable all day.",
    "h1": "The Best Caps for a Thinning Crown",
    "intro": "A" * 160,
    "tips": "Tip one|Tip two|Tip three",
}


def second(**changes):
    """A second valid page, different from GOOD, with optional changes."""
    return {**GOOD, "slug": "hats-for-receding-hairline", "keyword": "hats for a receding hairline",
            "title": "Hats for a Receding Hairline | Crown Cover Co.", **changes}


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(GOOD))
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_good_row_loads(tmp_path):
    pages = load_pages(write_csv(tmp_path / "pages.csv", [GOOD]))
    assert pages[0].tips == ["Tip one", "Tip two", "Tip three"]


@pytest.mark.parametrize("changes, message", [
    ({"title": "x" * 61}, "title is 61 characters"),
    ({"meta_description": "x" * 156}, "meta_description is 156 characters"),
    ({"intro": "Too short."}, "intro is 10 characters"),
    ({"tips": "One|Two"}, "has 2 tips"),
    ({"h1": ""}, "h1 is empty"),
    ({"intro": "A" * 150 + " This cap helps prevent thinning."}, "possible health claims"),
])
def test_rule_breaks_are_refused(tmp_path, changes, message):
    with pytest.raises(ValueError, match=message):
        load_pages(write_csv(tmp_path / "pages.csv", [{**GOOD, **changes}]))


@pytest.mark.parametrize("slug", ["Best-Caps", "best caps", "best--caps", "-best", "best-"])
def test_bad_slugs_are_refused(tmp_path, slug):
    with pytest.raises(ValueError, match="slug"):
        load_pages(write_csv(tmp_path / "pages.csv", [{**GOOD, "slug": slug}]))


def test_claims_check_matches_whole_words_only(tmp_path):
    row = {**GOOD, "intro": "A" * 150 + " Signed as a treaty of comfort."}
    assert len(load_pages(write_csv(tmp_path / "pages.csv", [row]))) == 1


def test_duplicate_keywords_ignore_case(tmp_path):
    rows = [GOOD, second(keyword="CAPS for a Thinning Crown")]
    with pytest.raises(ValueError, match="duplicate keyword"):
        load_pages(write_csv(tmp_path / "pages.csv", rows))


def test_every_problem_is_reported_at_once(tmp_path):
    with pytest.raises(ValueError, match="2 problem"):
        load_pages(write_csv(tmp_path / "pages.csv", [{**GOOD, "title": "x" * 61, "tips": "One"}]))


def test_missing_column_is_refused(tmp_path):
    path = tmp_path / "pages.csv"
    path.write_text("slug,title\nabc,Title\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        load_pages(path)