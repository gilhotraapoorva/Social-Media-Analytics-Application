"""Module 2: Trending Topics Detection — hashtag frequency + keyword trends."""
from collections import Counter
from typing import List, Dict, Any
import re

WORD_RE = re.compile(r"\b[a-zA-Z]{4,}\b")
STOPWORDS = {
    "this", "that", "with", "have", "from", "they", "your", "what", "when",
    "will", "been", "were", "their", "there", "would", "could", "should",
    "about", "which", "than", "then", "into", "like", "just", "very", "much",
    "some", "more", "most", "also", "over", "after", "before", "still", "even",
    "only", "make", "made", "does", "doesn", "isn",
}


def extract_hashtags(posts: List) -> Counter:
    counter = Counter()
    for p in posts:
        for tag in p.hashtag_list:
            counter[tag.lower()] += 1
    return counter


def extract_keywords(posts: List) -> Counter:
    counter = Counter()
    for p in posts:
        for word in WORD_RE.findall((p.text or "").lower()):
            if word not in STOPWORDS:
                counter[word] += 1
    return counter


def analyze_trends(posts: List, top_n: int = 15) -> Dict[str, Any]:
    hashtag_counts = extract_hashtags(posts)
    keyword_counts = extract_keywords(posts)

    top_hashtags = hashtag_counts.most_common(top_n)
    top_keywords = keyword_counts.most_common(top_n)

    # Build a simple trend score per hashtag (frequency * avg engagement)
    hashtag_engagement = {}
    for p in posts:
        for tag in p.hashtag_list:
            hashtag_engagement.setdefault(tag.lower(), []).append(p.engagement)

    ranked = []
    for tag, freq in top_hashtags:
        engagements = hashtag_engagement.get(tag, [0])
        avg_eng = sum(engagements) / max(len(engagements), 1)
        ranked.append({
            "hashtag": tag,
            "count": freq,
            "avg_engagement": round(avg_eng, 1),
            "trend_score": round(freq * (1 + avg_eng / 100), 2),
        })
    ranked.sort(key=lambda r: r["trend_score"], reverse=True)

    return {
        "total_posts": len(posts),
        "unique_hashtags": len(hashtag_counts),
        "unique_keywords": len(keyword_counts),
        "top_hashtags": [{"hashtag": h, "count": c} for h, c in top_hashtags],
        "top_keywords": [{"keyword": k, "count": c} for k, c in top_keywords],
        "ranked_trends": ranked,
    }
