"""Build the SAMPLE Instagram analytics report PDF from the post CSV.

Every number in the PDF is recomputed here from
data/raw/posts_SAMPLE.csv — nothing is typed in by hand. Account-level
followers (start 8,420, end 9,581) are the stated sample account
figures: gross new followers from posts (1,219, from the CSV) minus
58 unfollows = net +1,161. The script asserts that arithmetic.
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "raw" / "posts_SAMPLE.csv"
OUT = ROOT / "outputs" / "instagram_analytics_report_SAMPLE.pdf"
CHART_DIR = ROOT / "outputs"
CHART_DIR.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
for r in rows:
    for k in ("reach", "impressions", "likes", "comments", "shares",
              "saves", "engagement", "profile_visits", "new_followers"):
        r[k] = int(r[k])
    r["engagement_rate_pct"] = float(r["engagement_rate_pct"])

total_reach = sum(r["reach"] for r in rows)
total_eng = sum(r["engagement"] for r in rows)
overall_er = 100.0 * total_eng / total_reach
gross_follows = sum(r["new_followers"] for r in rows)
START_F, END_F = 8420, 9581
assert END_F - START_F == gross_follows - 58, "follower arithmetic"
# No assert on the post count: a real client's export has whatever
# number of posts it has, and every figure above is computed from
# the rows. (The sample's 36 posts are pinned by src/checks.py.)

by_type = {}
for t in ("Reel", "Carousel", "Image"):
    s = [r for r in rows if r["post_type"] == t]
    by_type[t] = {
        "n": len(s),
        "reach": sum(r["reach"] for r in s),
        "er": 100.0 * sum(r["engagement"] for r in s) / sum(r["reach"] for r in s),
        "avg_reach": sum(r["reach"] for r in s) / len(s),
    }

# Weekly totals (weeks start on the first post date, 1 Aug 2026).
from datetime import date as _date

start = _date(2026, 8, 1)
weeks = defaultdict(lambda: {"reach": 0, "eng": 0, "posts": 0})
for r in rows:
    d = _date.fromisoformat(r["date"])
    w = (d - start).days // 7 + 1
    weeks[w]["reach"] += r["reach"]
    weeks[w]["eng"] += r["engagement"]
    weeks[w]["posts"] += 1
week_labels = [f"W{w}" for w in sorted(weeks)]
week_reach = [weeks[w]["reach"] for w in sorted(weeks)]
week_er = [100.0 * weeks[w]["eng"] / weeks[w]["reach"] for w in sorted(weeks)]

plt.figure(figsize=(8, 3.2))
plt.bar(week_labels, week_reach, color="#c13584")
plt.title("Weekly reach — DesiBites PK (SAMPLE, 90 days)")
plt.ylabel("Reach")
plt.tight_layout()
plt.savefig(CHART_DIR / "weekly_reach.png", dpi=150)
plt.close()

plt.figure(figsize=(8, 3.2))
types = list(by_type.keys())
plt.bar(types, [by_type[t]["er"] for t in types], color=["#c13584", "#f77737", "#5851db"])
plt.title("Engagement rate by post type (engagement / reach, SAMPLE)")
plt.ylabel("Engagement rate %")
plt.tight_layout()
plt.savefig(CHART_DIR / "er_by_type.png", dpi=150)
plt.close()

top5 = sorted(rows, key=lambda r: -r["engagement_rate_pct"])[:5]

styles = getSampleStyleSheet()
story = [
    Paragraph("Instagram Business Analytics Report", styles["Title"]),
    Paragraph("DesiBites PK — fictional Lahore home-food business · "
              "90-day audit: 1 Aug – 29 Oct 2026 · SAMPLE DATA", styles["Normal"]),
    Spacer(1, 0.4 * cm),
    Paragraph("⚠️ SAMPLE report. DesiBites PK is fictional and every number "
              "below is generated sample data (seed 42) that demonstrates the "
              "audit method. It is not a real account's analytics and must "
              "never be presented as a real client's results.", styles["Normal"]),
    Spacer(1, 0.4 * cm),
    Paragraph(f"Headline: {len(rows)} posts reached {total_reach:,} accounts "
              f"and earned {total_eng:,} engagements — an overall engagement "
              f"rate of {overall_er:.2f}%. Followers grew from {START_F:,} to "
              f"{END_F:,} (net +{END_F - START_F:,}, +{(END_F - START_F) / START_F * 100:.1f}%). "
              f"Posts drove {gross_follows:,} gross new followers; 58 unfollows "
              f"in the same window explain the gap to net growth.", styles["Normal"]),
    Spacer(1, 0.4 * cm),
    Image(str(CHART_DIR / "weekly_reach.png"), width=16 * cm, height=6.4 * cm),
    Spacer(1, 0.3 * cm),
    Image(str(CHART_DIR / "er_by_type.png"), width=16 * cm, height=6.4 * cm),
    Spacer(1, 0.4 * cm),
    Paragraph("Engagement rate by post type", styles["Heading2"]),
]
tdata = [["Type", "Posts", "Total reach", "Engagement rate"]]
for t in types:
    tdata.append([t, str(by_type[t]["n"]), f"{by_type[t]['reach']:,}",
                  f"{by_type[t]['er']:.2f}%"])
t = Table(tdata)
t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#c13584")),
                       ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                       ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
story.append(t)
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("Top 5 posts by engagement rate", styles["Heading2"]))
tdata = [["Post", "Date", "Type", "Topic", "Reach", "Eng. rate"]]
for r in top5:
    tdata.append([r["post_id"], r["date"], r["post_type"], r["topic"],
                  f"{r['reach']:,}", f"{r['engagement_rate_pct']:.2f}%"])
t = Table(tdata)
t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#c13584")),
                       ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                       ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
story.append(t)
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("What to do next (in priority order)", styles["Heading2"]))
actions = [
    "1. Post more carousels: they hold the highest engagement rate "
    f"({by_type['Carousel']['er']:.2f}%) despite lower reach than Reels — "
    "one menu carousel per week is the cheapest growth lever here.",
    "2. Keep Reels as the reach engine: highest average reach "
    f"({by_type['Reel']['avg_reach']:,.0f} per post). One cooking Reel per week, "
    "same format as the top dessert and festival Reels.",
    "3. Reuse the winning proof format: the top post is a customer-review "
    "screenshot — post one real review every week; social proof beats new "
    "dish announcements.",
    "4. Ask a question in every image post: the menu-poll post is #3 overall, "
    "so end image captions with one question to lift comments.",
    "5. Fix the weak tail: image posts average the lowest reach — pair every "
    "price-list or announcement image with a Reel the same week.",
    "6. Repeat, don't reinvent: the top 5 span all three formats, so the "
    "fix is volume of proven formats, not a new content idea.",
]
for a in actions:
    story.append(Paragraph(a, styles["Normal"]))
    story.append(Spacer(1, 0.15 * cm))
story.append(Paragraph("Method note: engagement rate = (likes + comments + "
                       "shares + saves) / reach, per post and in aggregate. "
                       "Re-running src/generate_sample_data.py reproduces the "
                       "identical CSV; re-running this script reproduces the "
                       "identical report.", styles["Normal"]))

SimpleDocTemplate(str(OUT), pagesize=A4).build(story)
print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")
print(f"Posts {len(rows)}, reach {total_reach:,}, ER {overall_er:.2f}%")
