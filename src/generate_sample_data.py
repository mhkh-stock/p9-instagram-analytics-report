"""Generate SAMPLE Instagram post data for a fictional business page.

Business: "DesiBites PK" — a fictional Lahore home-food business.
Every number here is generated (seed 42) to demonstrate the audit
method. No real account's data is involved, and nothing here is
claimed as a real client's analytics.

Output: data/raw/posts_SAMPLE.csv — one row per post, 90 days.
Post types and topics are weighted so Reels outperform images, the
way they do on most real food pages — but the exact figures are
sample-only and the report says so.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "posts_SAMPLE.csv"

random.seed(42)

START = date(2026, 8, 1)
N_DAYS = 90
N_POSTS = 36

TOPICS = [
    ("Biryani recipe reel", "Reel"),
    ("Karahi cooking reel", "Reel"),
    ("Weekly menu carousel", "Carousel"),
    ("Customer review screenshot", "Image"),
    ("Kitchen behind the scenes", "Reel"),
    ("New dish announcement", "Carousel"),
    ("Price list post", "Image"),
    ("Festival special reel", "Reel"),
    ("Packing orders timelapse", "Reel"),
    ("Menu poll / question", "Image"),
    ("Desi dessert reel", "Reel"),
    ("Bulk order announcement", "Carousel"),
]

# Base reach by type; reels reach further, images reach least.
BASE_REACH = {"Reel": 6200, "Carousel": 3400, "Image": 2100}

rows = []
post_dates = sorted(random.sample(range(N_DAYS), N_POSTS))
for i, day_offset in enumerate(post_dates, start=1):
    topic, ptype = TOPICS[(i * 5 + 3) % len(TOPICS)]
    d = START + timedelta(days=day_offset)
    # Weekend posts (Fri/Sat in PKT) get a reach bump.
    weekend = 1.25 if d.weekday() in (4, 5) else 1.0
    reach = int(BASE_REACH[ptype] * weekend * random.uniform(0.75, 1.35))
    likes = int(reach * random.uniform(0.055, 0.115))
    comments = int(reach * random.uniform(0.004, 0.016))
    shares = int(reach * random.uniform(0.003, 0.014))
    saves = int(reach * random.uniform(0.004, 0.018))
    impressions = int(reach * random.uniform(1.15, 1.45))
    profile_visits = int(reach * random.uniform(0.02, 0.06))
    new_followers = int(profile_visits * random.uniform(0.08, 0.28))
    engagement = likes + comments + shares + saves
    rows.append({
        "post_id": f"P{i:02d}",
        "date": d.isoformat(),
        "weekday": d.strftime("%a"),
        "post_type": ptype,
        "topic": topic,
        "reach": reach,
        "impressions": impressions,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "saves": saves,
        "engagement": engagement,
        "engagement_rate_pct": round(100.0 * engagement / reach, 2),
        "profile_visits": profile_visits,
        "new_followers": new_followers,
    })

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} posts to {OUT}")
print(f"Date range: {rows[0]['date']} to {rows[-1]['date']}")
print(f"Total reach: {sum(r['reach'] for r in rows):,}")
print(f"Total engagement: {sum(r['engagement'] for r in rows):,}")
print(f"Total new followers from posts: {sum(r['new_followers'] for r in rows):,}")
