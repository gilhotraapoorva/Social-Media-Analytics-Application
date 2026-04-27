"""Module 7: Data Visualization — engagement, reach, sentiment time series."""
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime


def _bucket_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d") if dt else "unknown"


def build_visualizations(posts: List) -> Dict[str, Any]:
    by_day_engagement = defaultdict(int)
    by_day_reach = defaultdict(int)
    by_day_count = defaultdict(int)
    by_day_sentiment = defaultdict(list)

    for p in posts:
        key = _bucket_key(p.posted_at)
        by_day_engagement[key] += p.engagement
        by_day_reach[key] += p.impressions or 0
        by_day_count[key] += 1
        if p.sentiment_score is not None:
            by_day_sentiment[key].append(p.sentiment_score)

    days = sorted(d for d in by_day_engagement.keys() if d != "unknown")

    sentiment_series = []
    for d in days:
        scores = by_day_sentiment.get(d, [])
        sentiment_series.append(round(sum(scores) / len(scores), 3) if scores else 0)

    top_authors = defaultdict(lambda: {"posts": 0, "engagement": 0})
    for p in posts:
        top_authors[p.author]["posts"] += 1
        top_authors[p.author]["engagement"] += p.engagement
    top_authors_sorted = sorted(
        [{"author": k, **v} for k, v in top_authors.items()],
        key=lambda r: r["engagement"], reverse=True,
    )[:10]

    return {
        "timeseries": {
            "labels": days,
            "engagement": [by_day_engagement[d] for d in days],
            "reach": [by_day_reach[d] for d in days],
            "post_count": [by_day_count[d] for d in days],
            "sentiment": sentiment_series,
        },
        "top_authors": top_authors_sorted,
        "totals": {
            "engagement": sum(by_day_engagement.values()),
            "reach": sum(by_day_reach.values()),
            "posts": len(posts),
        },
    }
