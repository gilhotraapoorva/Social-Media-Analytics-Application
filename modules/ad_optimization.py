"""Module 8: Ad Campaign Optimization — CTR, conversion rate, ROI."""
from typing import List, Dict, Any
import random


def simulate_ad_campaigns(posts: List) -> List[Dict[str, Any]]:
    """Treat top-engagement posts as 'ad creatives' and simulate campaign metrics.

    A real product would consume actual ad-platform data; here we derive
    deterministic but realistic numbers from each post's engagement signal.
    """
    if not posts:
        return []

    rng = random.Random(42)
    sorted_posts = sorted(posts, key=lambda p: p.engagement, reverse=True)[:10]

    campaigns = []
    for idx, p in enumerate(sorted_posts):
        impressions = max(p.impressions or p.engagement * 50, 1000)
        clicks = max(int(impressions * rng.uniform(0.01, 0.06)), 1)
        conversions = max(int(clicks * rng.uniform(0.02, 0.10)), 0)
        spend = round(impressions * 0.005 + rng.uniform(20, 200), 2)
        revenue = round(conversions * rng.uniform(15, 80), 2)
        ctr = round(clicks / impressions * 100, 2)
        conv_rate = round((conversions / clicks * 100) if clicks else 0.0, 2)
        roi = round(((revenue - spend) / spend * 100) if spend else 0.0, 2)

        campaigns.append({
            "id": idx + 1,
            "creative": (p.text[:80] + "...") if len(p.text) > 80 else p.text,
            "author": p.author,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "spend_usd": spend,
            "revenue_usd": revenue,
            "ctr_pct": ctr,
            "conversion_rate_pct": conv_rate,
            "roi_pct": roi,
        })

    return campaigns


def analyze_campaigns(posts: List) -> Dict[str, Any]:
    campaigns = simulate_ad_campaigns(posts)
    if not campaigns:
        return {"campaigns": [], "summary": {}}

    n = len(campaigns)
    summary = {
        "campaign_count": n,
        "avg_ctr": round(sum(c["ctr_pct"] for c in campaigns) / n, 2),
        "avg_conversion_rate": round(sum(c["conversion_rate_pct"] for c in campaigns) / n, 2),
        "avg_roi": round(sum(c["roi_pct"] for c in campaigns) / n, 2),
        "total_spend": round(sum(c["spend_usd"] for c in campaigns), 2),
        "total_revenue": round(sum(c["revenue_usd"] for c in campaigns), 2),
        "best_campaign": max(campaigns, key=lambda c: c["roi_pct"]),
        "worst_campaign": min(campaigns, key=lambda c: c["roi_pct"]),
    }
    return {"campaigns": campaigns, "summary": summary}
