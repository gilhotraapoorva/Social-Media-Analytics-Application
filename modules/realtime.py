"""Module 10: Real-Time Monitoring — track keywords, anomaly detection, alerts."""
from typing import List, Dict, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics


def monitor_keywords(posts: List, keywords: List[str] = None,
                     window_hours: int = 24) -> Dict[str, Any]:
    """Build a rolling, time-bucketed view of mentions for tracked keywords."""
    if not posts:
        return {"keywords": [], "alerts": [], "timeline": {}}

    # Default to top hashtags if no explicit watchlist provided
    if not keywords:
        from modules.trends import extract_hashtags
        keywords = [tag for tag, _ in extract_hashtags(posts).most_common(5)]

    keywords = [k.lower().lstrip("#") for k in keywords]

    by_hour: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for p in posts:
        if not p.posted_at:
            continue
        bucket = p.posted_at.strftime("%Y-%m-%d %H:00")
        text = (p.text or "").lower()
        for kw in keywords:
            if kw in text:
                by_hour[bucket][kw] += 1

    # Anomaly detection: flag any hour where a keyword exceeds mean + 2*std
    alerts = []
    timeline: Dict[str, List[Dict[str, Any]]] = {kw: [] for kw in keywords}
    for kw in keywords:
        series = [(h, by_hour[h].get(kw, 0)) for h in sorted(by_hour.keys())]
        values = [v for _, v in series]
        mean = statistics.mean(values) if values else 0
        std = statistics.pstdev(values) if len(values) > 1 else 0
        threshold = mean + 2 * std
        for hour, v in series:
            timeline[kw].append({"hour": hour, "count": v})
            if v > threshold and v >= 3:
                alerts.append({
                    "keyword": kw,
                    "hour": hour,
                    "count": v,
                    "threshold": round(threshold, 2),
                })

    return {
        "keywords": keywords,
        "alerts": alerts,
        "timeline": timeline,
        "window_hours": window_hours,
    }


def negative_sentiment_alerts(posts: List, threshold_score: float = -0.4,
                              min_engagement: int = 50) -> List[Dict[str, Any]]:
    alerts = []
    for p in posts:
        if (p.sentiment_score is not None
                and p.sentiment_score <= threshold_score
                and p.engagement >= min_engagement):
            alerts.append({
                "post_id": p.id,
                "author": p.author,
                "text": (p.text[:160] + "...") if len(p.text) > 160 else p.text,
                "score": round(p.sentiment_score, 3),
                "engagement": p.engagement,
            })
    return alerts
