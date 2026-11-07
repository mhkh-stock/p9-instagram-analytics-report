# P9 — Instagram Business Analytics Report

**Repo:** https://github.com/mhkh-stock/p9-instagram-analytics-report

**Client pain:** a small business owner posts regularly but has no
idea why some posts grow the page and others do nothing — so every
week's content is a guess, and the guess usually repeats the weakest
format.
**This delivery:** a 90-day engagement audit that turns post data
into a short PDF report: what reached, what engaged, what to post
more of, and what to stop — in priority order, with the numbers
behind every recommendation.
**Status: SAMPLE delivery**
**Tools:** Python (reportlab + matplotlib) · CSV data · PDF report
**Deliverable:** `outputs/instagram_analytics_report_SAMPLE.pdf`
(2 pages: headline, weekly reach chart, engagement-by-type chart,
type table, top-5 posts, 6 prioritised actions)

> ⚠️ **What this is and is not.** "DesiBites PK" is a fictional
> Lahore home-food business and all 36 posts are generated SAMPLE
> data (`src/generate_sample_data.py`, seed 42 — re-running
> reproduces the identical file). What is real is the audit: every
> number in the PDF is recomputed from the CSV by
> `src/build_report.py`, engagement rate is defined once
> ((likes + comments + shares + saves) / reach) and used everywhere,
> and every action traces to a computed figure, not a hunch. A real
> order replaces the CSV with the client's exported Insights data
> and the same scripts produce their report.

## Business question it answers

> "Why isn't my page growing — in numbers — and what exactly should
> I post next?"

## What is inside

| File | What it does |
|---|---|
| `outputs/instagram_analytics_report_SAMPLE.pdf` | The deliverable: 90-day audit report with charts, tables and 6 actions |
| `outputs/weekly_reach.png`, `outputs/er_by_type.png` | The report's two charts, also usable standalone |
| `data/raw/posts_SAMPLE.csv` | The 36 SAMPLE posts (date, type, topic, reach, impressions, likes, comments, shares, saves, engagement, profile visits, new followers) |
| `src/generate_sample_data.py` | Generates the sample CSV (deterministic, seed 42) |
| `src/build_report.py` | Recomputes every KPI from the CSV and builds the PDF + charts |
| `src/checks.py` | Data-quality checks as code — 22 checks, all passing |
| `requirements.txt` | Pinned Python dependencies (reportlab, matplotlib) |

## 3 key findings (from this sample)

1. **Reels win reach, carousels win engagement.** Reels average
   6,745 reach per post — the page's reach engine — but carousels
   hold the highest engagement rate (12.71% vs 11.14% for Reels).
   *So what:* the cheapest growth lever is one more menu carousel a
   week, not more of everything.
2. **Social proof is the single best post.** The top post overall
   (15.03% engagement rate) is a customer-review screenshot, ahead
   of every recipe and announcement. *So what:* one real review a
   week beats another new-dish announcement — proof converts better
   than novelty.
3. **The page is growing, but the tail drags.** Followers grew from
   8,420 to 9,581 (net +1,161, +13.8%) in 90 days, with posts driving
   1,219 gross new followers against 58 unfollows — while image
   posts average only ~2,056 reach. *So what:* pair every low-reach
   image announcement with a Reel the same week instead of posting
   it alone.

## Verified numbers

| KPI | Value |
|---|---|
| Audit window | 1 Aug – 29 Oct 2026 (90 days) |
| Posts audited | 36 (18 Reels, 9 Carousels, 9 Images) |
| Total reach | 178,122 |
| Total engagement | 20,538 |
| Overall engagement rate | 11.53% |
| Engagement rate by type | Carousel 12.71% · Image 11.68% · Reel 11.14% |
| Followers | 8,420 → 9,581 (net +1,161, +13.8%) |
| Gross new followers from posts | 1,219 (58 unfollows in window) |
| Top post | P36, customer-review screenshot, 15.03% |
| Checks | 22 passing (`python3 src/checks.py`) |

Verification: `python3 src/checks.py` (22 checks pass) plus an
independent reopen of the PDF — 2 pages, headline + both charts +
type table + top-5 table + 6 actions all present and legible.

## How to run it (under 5 steps)

1. Open `outputs/instagram_analytics_report_SAMPLE.pdf` — that is
   the deliverable.
2. To regenerate the sample data: `python3 src/generate_sample_data.py`.
3. To rebuild the report: `python3 src/build_report.py`.
4. To check the data: `python3 src/checks.py`.
5. To reuse it for a real client: replace
   `data/raw/posts_SAMPLE.csv` with the client's exported post data
   (same 15 columns) and re-run steps 3–4 — the report rebuilds
   itself from the new lines. Note: `src/checks.py` pins the SAMPLE's
   expected values, so it will fail on real-client data by design —
   update its expected numbers to the client's figures before
   treating it as a pass/fail gate for a real order.

## How it fits together

```
src/generate_sample_data.py (seed 42) ──> data/raw/posts_SAMPLE.csv
                                              │
                              ┌─────────────────┘
                              ▼
                 src/build_report.py ──> outputs/*.png + *_SAMPLE.pdf
                              │
                 src/checks.py ──> 22 pass/fail checks on the CSV + outputs
```

## Data dictionary (`data/raw/posts_SAMPLE.csv`, 15 columns)

| Column | Meaning |
|---|---|
| `post_id` | Post key, P01–P36 in date order |
| `date` | Post date (YYYY-MM-DD); `weekday` is its 3-letter day |
| `post_type` | Reel, Carousel or Image |
| `topic` | Short content label (e.g. "Biryani recipe reel") |
| `reach`, `impressions` | Accounts reached; total views (impressions ≥ reach) |
| `likes`, `comments`, `shares`, `saves` | Engagement components |
| `engagement` | likes + comments + shares + saves (checked on every row) |
| `engagement_rate_pct` | 100 × engagement / reach, rounded to 2 dp |
| `profile_visits`, `new_followers` | Visits and gross new followers attributed to the post |

Engagement rate is defined once — (likes + comments + shares +
saves) / reach — and used everywhere, per post and in aggregate.
By-type rates are aggregate (total engagement / total reach for the
type), not the mean of per-post rates.

## Limits

- **SAMPLE data only.** DesiBites PK is fictional; nothing here is a
  real account's analytics. A real order needs the client's own
  Instagram Insights export.
- **Three post types only** (Reel / Carousel / Image). A CSV with a
  fourth type, or a type with zero posts, will not build cleanly.
- **Follower start/end (8,420 → 9,581) and 58 unfollows are sample
  constants** in `src/build_report.py` — a real order replaces them
  with the client's actual figures.
- **No Instagram API is used.** Data comes from a manual Insights
  export (CSV); the scripts never log in to or fetch from Instagram.
- **Checks pin the sample.** `src/checks.py` hardcodes the SAMPLE's
  expected totals, so it fails on real-client data until its expected
  values are updated (see step 5 above).

## Tools

- Python 3 · reportlab (PDF) · matplotlib (charts)
- Instagram Insights export (the client's data source, not a new
  tool to learn)

## Data source note

**SAMPLE data, generated 5 Nov 2026.** No real account's analytics
is involved. The audit method, the report structure and the action
framework are the product; the numbers exist to prove them.
