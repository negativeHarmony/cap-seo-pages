# cap-seo-pages

Programmatic SEO for a cap store: one HTML template plus one spreadsheet row per page,
built into a static site and published free on GitHub Pages.

**Live site:** https://negativeharmony.github.io/cap-seo-pages/

## How it works

```
content/pages.csv   →  build.py  →  docs/   →  GitHub Pages
(one row per page)     (validate,    (20 pages, index,
                        render)       sitemap.xml)
```

- **Content** is drafted with Claude, then checked by code and reviewed by a person before publishing.
- **Validation** (`pages.py`) refuses the whole spreadsheet, listing every problem, if any row breaks a rule:
  - titles of at most 60 characters and descriptions of at most 155, so they aren't cut off in Google results
  - lowercase-hyphen slugs
  - intros of at least 150 characters and at least 3 tips, so there are no thin pages
  - no duplicate slugs, keywords or titles, so pages don't compete with each other
  - no health-claim words (cure, regrow, prevent, treatment…)
- **The build** (`build.py`) only deletes and regenerates `docs/` after validation passes, so bad
  content can never take down the live site. Content is HTML-escaped.
- **Every page** has a title, meta description, canonical URL and Open Graph tags, and is
  listed in `sitemap.xml`.

## Edit and publish

```bash
pip install -r requirements.txt
python build.py                              # validate + build into docs/
python -m http.server 8000 --directory docs  # preview at http://localhost:8000
python -m pytest -v                          # run the tests
git add . && git commit -m "Update pages" && git push   # GitHub Pages republishes
```

Never edit files in `docs/` by hand: they are regenerated on every build.
Settings (site name, URL, store link, Google verification) are at the top of `build.py`.

## License

MIT