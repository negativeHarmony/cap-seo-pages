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

- **Content** is drafted with Claude, then checked by code and reviewed by a person before publishing
  (see [Content workflow](#content-workflow)).
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

## Content workflow

AI drafts, code checks the rules, a person checks the truth.

```
Round 1  Claude proposes topics          → a person approves, cuts or changes them
Round 2  Claude writes the CSV rows      → python build.py validates them
           problems? → paste the error list back to Claude to fix → build again
Round 3  A person reads every page       → fixes anything untrue, unhelpful or repetitive
```

### Round 1: Choose the topics

```text
I run a small online store selling caps designed for men with thinning hair and hair loss.
I'm building a set of helpful guide pages, one page per search question people actually type
into Google.

I already have pages for:
- caps for a thinning crown
- hats for a receding hairline

Propose 18 MORE distinct topics. For each, give:
- a slug (lowercase letters, numbers and single hyphens only)
- the search keyword it targets

Rules:
- Each topic must be a genuinely different question, not a rewording of another one or of my two
  existing pages. Two topics that would give the same advice should be merged into one.
- Practical styling, fit, fabric, care, occasion and confidence topics only.
- No medical topics (hair loss causes, treatments, products that regrow hair).
- No competitor brand names.

Give me a simple numbered list. Don't write the pages yet.
```

Update the list of existing pages and the number of topics to match the current spreadsheet.

**Review the topics before Round 2.** Validation only catches *exact* duplicate keywords, so cut or
merge topics that would give the same advice (for example "caps for bald men" and "hats for a bald
head"). Optionally, check that real people search for them: Google autocomplete, "People also ask",
or a free keyword tool.

### Round 2: Write the rows

In the same chat:

```text
Now write one CSV row for each of the 18 approved topics.

Output ONLY the CSV rows (no header, no explanation), in this exact column order:
slug,keyword,title,meta_description,h1,intro,tips

Rules for every row:
- title: at most 60 characters, ending with " | Crown Cover Co."
- meta_description: at most 155 characters, a plain summary of what the page answers
- h1: a natural heading for the page (can differ from the title)
- intro: 2-3 sentences, at least 150 characters, that answer the question directly in the first sentence
- tips: 4 or 5 specific, practical tips separated by the | character. No | anywhere else.
- Wrap any value containing a comma in double quotes.

Content rules:
- Only practical advice about choosing, wearing, fitting and caring for caps and hats.
- Make NO health or medical claims. Never use these words: cure, regrow, regrowth, prevent,
  prevents, treat, treats, treatment, clinically, proven, guaranteed, medical.
- No invented statistics, studies, reviews, quotes, prices or product names.
- Each page must give advice that is genuinely different from every other page.
- Write for a man who is a bit self-conscious about his hair: warm, direct, never mocking.
```

The rules in this prompt mirror the validation rules in `pages.py`, so the model aims for them
first time. The build still checks every row, because instructions alone are no guarantee.

Paste the rows at the end of `content/pages.csv` (keep the header and existing rows), then:

```bash
python build.py
```

### Fixing rows the build refuses

If the build stops, paste its problem list back into the same chat:

```text
The build refused these rows:

<paste the problem list from python build.py>

Fix only these rows, following all the same rules. Output only the corrected rows, in the same
CSV format.
```

Replace those rows in `content/pages.csv` and build again. Repeat until it builds.

If an error looks strange (for example a 125-character "title" or "0 tips"), the row's columns
have shifted because of a quoting problem. Ask for that row again with correct quoting, or fix it
by editing the CSV in a spreadsheet app, which handles quoting automatically.

### Round 3: Read every page

```bash
python -m http.server 8000 --directory docs   # then open http://localhost:8000
```

The build checks rules; only a person can check truth and usefulness. For every page:

| Check | Why |
|---|---|
| Is every tip actually true? | Models can state plausible but wrong advice confidently. |
| Any invented facts: statistics, "experts say", "customers love…"? | Code can't catch these, and they mislead customers. |
| Any health claims in other words, e.g. "keeps your scalp healthy"? | The word list only catches the obvious ones. |
| Is it different from every other page? | Near-duplicates compete with each other in Google. |
| Would it genuinely help the reader? | The real test for both customers and search engines. |

Fix anything in `content/pages.csv`, rebuild, and check again.

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
The shop button only appears once `STORE_URL` is set.

### Publishing setup (once)

1. Push the repo to GitHub as a **public** repository.
2. **Settings → Pages**: Source **Deploy from a branch**, branch **main**, folder **/docs**.
3. **Google Search Console**: add a **URL prefix** property for the live site, choose **HTML tag**
   verification, put the code in `GOOGLE_VERIFICATION` in `build.py`, rebuild and push, then verify.
4. In Search Console, submit **`sitemap.xml`** under **Sitemaps**.

## Tests

```bash
python -m pytest -v
```

The tests check every validation rule (including whole-word matching for health claims and
case-insensitive duplicates), and run the real build in a temporary folder to check the files
produced, absolute canonical URLs with relative navigation, the sitemap, HTML escaping, and that
a spreadsheet with errors leaves the existing site untouched.

## License

MIT