"""Load the page spreadsheet and check every row before anything is built."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

REQUIRED_COLUMNS = ["slug", "keyword", "title", "meta_description", "h1", "intro", "tips"]
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MAX_TITLE = 60
MAX_DESCRIPTION = 155
MIN_INTRO = 150
MIN_TIPS = 3
RISKY_CLAIMS = [
    "cure", "cures", "regrow", "regrows", "regrowth", "prevent", "prevents",
    "treat", "treats", "treatment", "clinically", "proven", "guaranteed", "medical",
]


@dataclass
class Page:
    slug: str
    keyword: str
    title: str
    meta_description: str
    h1: str
    intro: str
    tips: List[str]


def _text(row: Dict[str, str], column: str) -> str:
    return (row.get(column) or "").strip()


def problems_with(page: Page) -> List[str]:
    """Every rule this one page breaks. An empty list means the page is fine."""
    problems = []
    for name in ["slug", "keyword", "title", "meta_description", "h1", "intro"]:
        if not getattr(page, name):
            problems.append(f"{name} is empty")
    if page.slug and not SLUG.fullmatch(page.slug):
        problems.append(f"slug '{page.slug}' must be lowercase letters, numbers and single hyphens")
    if len(page.title) > MAX_TITLE:
        problems.append(f"title is {len(page.title)} characters (max {MAX_TITLE})")
    if len(page.meta_description) > MAX_DESCRIPTION:
        problems.append(f"meta_description is {len(page.meta_description)} characters (max {MAX_DESCRIPTION})")
    if page.intro and len(page.intro) < MIN_INTRO:
        problems.append(f"intro is {len(page.intro)} characters (min {MIN_INTRO})")
    if len(page.tips) < MIN_TIPS:
        problems.append(f"has {len(page.tips)} tips (min {MIN_TIPS})")

    text = " ".join([page.title, page.meta_description, page.h1, page.intro, *page.tips]).lower()
    risky = [word for word in RISKY_CLAIMS if re.search(rf"\b{word}\b", text)]
    if risky:
        problems.append(f"possible health claims: {risky}. Reword, or remove the claim")
    return problems


def duplicates(pages: List[Page], field: str) -> List[str]:
    """Pages that reuse another page's slug, keyword or title (ignoring case)."""
    first_use = {}
    problems = []
    for page in pages:
        value = getattr(page, field).lower()
        if value in first_use:
            problems.append(f"duplicate {field} '{getattr(page, field)}' (also used by {first_use[value]})")
        else:
            first_use[value] = page.slug
    return problems


def load_pages(path: Path) -> List[Page]:
    """Read pages.csv and refuse it, listing every problem, unless every row passes."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path} is missing columns: {missing}")
        rows = list(reader)

    pages = []
    problems = []
    for line, row in enumerate(rows, start=2):
        page = Page(
            slug=_text(row, "slug"),
            keyword=_text(row, "keyword"),
            title=_text(row, "title"),
            meta_description=_text(row, "meta_description"),
            h1=_text(row, "h1"),
            intro=_text(row, "intro"),
            tips=[tip.strip() for tip in _text(row, "tips").split("|") if tip.strip()],
        )
        problems += [f"row {line} ({page.slug or 'no slug'}): {p}" for p in problems_with(page)]
        pages.append(page)

    for field in ["slug", "keyword", "title"]:
        problems += duplicates(pages, field)
    if problems:
        raise ValueError(f"{path} has {len(problems)} problem(s):\n" + "\n".join(f"- {p}" for p in problems))
    return pages