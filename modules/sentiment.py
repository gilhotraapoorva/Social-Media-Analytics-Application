"""Module 1: Sentiment Analysis using VADER (NLTK)."""
from collections import Counter
from typing import List, Dict, Any

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def classify(text: str) -> Dict[str, Any]:
    scores = _analyzer.polarity_scores(text or "")
    compound = scores["compound"]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return {"label": label, "score": compound, "scores": scores}


def analyze_posts(posts: List) -> Dict[str, Any]:
    """Run sentiment over a list of Post objects, return summary + per-post details."""
    counts = Counter()
    details = []
    total_score = 0.0

    for p in posts:
        result = classify(p.text)
        p.sentiment_label = result["label"]
        p.sentiment_score = result["score"]
        counts[result["label"]] += 1
        total_score += result["score"]
        details.append({
            "id": p.id,
            "author": p.author,
            "text": (p.text[:140] + "...") if len(p.text) > 140 else p.text,
            "label": result["label"],
            "score": round(result["score"], 3),
            "engagement": p.engagement,
        })

    n = max(len(posts), 1)
    return {
        "total": len(posts),
        "distribution": {
            "positive": counts.get("positive", 0),
            "neutral": counts.get("neutral", 0),
            "negative": counts.get("negative", 0),
        },
        "average_score": round(total_score / n, 3),
        "details": details,
        "alerts": [d for d in details if d["label"] == "negative" and d["engagement"] > 100],
    }
