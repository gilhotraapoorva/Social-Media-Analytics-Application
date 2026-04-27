"""Module 11: Competitor Analysis — compare growth, engagement, strategy."""
from typing import List, Dict, Any
from collections import defaultdict

from modules import sentiment as sentiment_mod
from modules import trends as trends_mod


def compare_cases(case_a_posts: List, case_b_posts: List,
                  label_a: str = "A", label_b: str = "B") -> Dict[str, Any]:
    def summarize(posts: List) -> Dict[str, Any]:
        n = max(len(posts), 1)
        engagement = sum(p.engagement for p in posts)
        reach = sum(p.impressions or 0 for p in posts)
        sentiment = sentiment_mod.analyze_posts(list(posts))
        trends = trends_mod.analyze_trends(list(posts), top_n=10)
        return {
            "post_count": len(posts),
            "engagement": engagement,
            "reach": reach,
            "avg_engagement": round(engagement / n, 2),
            "sentiment_distribution": sentiment["distribution"],
            "average_sentiment": sentiment["average_score"],
            "top_hashtags": trends["top_hashtags"][:5],
        }

    a = summarize(case_a_posts)
    b = summarize(case_b_posts)

    # Strategy comparison: hashtag overlap & uniqueness
    a_tags = {t["hashtag"] for t in a["top_hashtags"]}
    b_tags = {t["hashtag"] for t in b["top_hashtags"]}

    return {
        "competitors": {label_a: a, label_b: b},
        "deltas": {
            "engagement_diff": a["engagement"] - b["engagement"],
            "avg_engagement_diff": a["avg_engagement"] - b["avg_engagement"],
            "sentiment_diff": round(a["average_sentiment"] - b["average_sentiment"], 3),
        },
        "strategy": {
            "shared_hashtags": sorted(a_tags & b_tags),
            f"{label_a}_unique": sorted(a_tags - b_tags),
            f"{label_b}_unique": sorted(b_tags - a_tags),
        },
    }


def list_user_cases_summary(cases: List) -> List[Dict[str, Any]]:
    rows = []
    for c in cases:
        n = max(len(c.posts), 1)
        eng = sum(p.engagement for p in c.posts)
        rows.append({
            "id": c.id,
            "name": c.name,
            "keyword": c.keyword,
            "platform": c.platform,
            "post_count": len(c.posts),
            "total_engagement": eng,
            "avg_engagement": round(eng / n, 2),
        })
    return rows
