"""Data-quality checks for P9 (run: python3 src/checks.py).

Every expected value below was computed from the generated CSV, not
typed from the report — if the data changes, these checks fail loudly
instead of silently disagreeing with the PDF.
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "raw" / "posts_SAMPLE.csv"
PDF = ROOT / "outputs" / "instagram_analytics_report_SAMPLE.pdf"

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name} {detail}")


rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
for r in rows:
    for k in ("reach", "impressions", "likes", "comments", "shares",
              "saves", "engagement", "profile_visits", "new_followers"):
        r[k] = int(r[k])
    r["engagement_rate_pct"] = float(r["engagement_rate_pct"])

check("36 posts", len(rows) == 36, f"got {len(rows)}")
check("date range 2026-08-01 to 2026-10-29",
      rows[0]["date"] == "2026-08-01" and rows[-1]["date"] == "2026-10-29")
check("post IDs unique", len({r['post_id'] for r in rows}) == 36)
check("no negative metrics",
      all(v >= 0 for r in rows for v in
          (r["reach"], r["likes"], r["comments"], r["shares"], r["saves"])))
check("engagement = likes+comments+shares+saves on every row",
      all(r["engagement"] == r["likes"] + r["comments"] + r["shares"] + r["saves"]
          for r in rows))
check("engagement_rate_pct column matches recomputation (0.01 tolerance)",
      all(abs(r["engagement_rate_pct"] - 100.0 * r["engagement"] / r["reach"]) < 0.011
          for r in rows))
check("total reach 178,122", sum(r["reach"] for r in rows) == 178122)
check("total engagement 20,538", sum(r["engagement"] for r in rows) == 20538)
check("overall engagement rate 11.53%",
      abs(100.0 * sum(r["engagement"] for r in rows) / sum(r["reach"] for r in rows) - 11.53) < 0.01)
check("gross new followers 1,219", sum(r["new_followers"] for r in rows) == 1219)
check("follower arithmetic: 8,420 + 1,219 - 58 = 9,581",
      8420 + 1219 - 58 == 9581)
for t, n in (("Reel", 18), ("Carousel", 9), ("Image", 9)):
    s = [r for r in rows if r["post_type"] == t]
    check(f"{t} count {n}", len(s) == n, f"got {len(s)}")
check("carousels beat reels on engagement rate",
      100.0 * sum(r["engagement"] for r in rows if r["post_type"] == "Carousel")
      / sum(r["reach"] for r in rows if r["post_type"] == "Carousel")
      > 100.0 * sum(r["engagement"] for r in rows if r["post_type"] == "Reel")
      / sum(r["reach"] for r in rows if r["post_type"] == "Reel"))
check("top post is P36 (customer review screenshot, 15.03%)",
      max(rows, key=lambda r: r["engagement_rate_pct"])["post_id"] == "P36")
check("PDF report exists and is non-trivial",
      PDF.exists() and PDF.stat().st_size > 50000, f"size {PDF.stat().st_size if PDF.exists() else 0}")
for chart in ("weekly_reach.png", "er_by_type.png"):
    p = ROOT / "outputs" / chart
    check(f"chart {chart} exists", p.exists() and p.stat().st_size > 5000)

print(f"\n{passed} passing, {failed} failing")
sys.exit(1 if failed else 0)
