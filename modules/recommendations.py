"""Module 4: Recommendation System — content-based + collaborative filtering."""
from typing import List, Dict, Any
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def content_based_recommendations(posts: List, target_post_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
    """Recommend posts similar in content to a given post."""
    if not posts:
        return []
    texts = [p.text or "" for p in posts]
    ids = [p.id for p in posts]

    if target_post_id not in ids:
        target_post_id = ids[0]

    target_idx = ids.index(target_post_id)

    vec = TfidfVectorizer(stop_words="english", max_features=2000)
    try:
        matrix = vec.fit_transform(texts)
    except ValueError:
        return []
    sim = cosine_similarity(matrix[target_idx:target_idx + 1], matrix).flatten()

    ranked = sorted(
        [(i, score) for i, score in enumerate(sim) if i != target_idx],
        key=lambda x: x[1], reverse=True,
    )[:top_k]

    return [
        {
            "post_id": ids[i],
            "author": posts[i].author,
            "text": posts[i].text[:140],
            "similarity": round(float(score), 3),
        }
        for i, score in ranked
    ]


def collaborative_recommendations(posts: List, target_user: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """User-user collaborative filtering on engagement patterns.

    Treat each (user, hashtag) pair as an interaction; recommend hashtags that
    similar users engage with but the target user has not yet used.
    """
    user_hashtags: Dict[str, set] = defaultdict(set)
    user_engagement: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for p in posts:
        author = p.author or "unknown"
        for tag in p.hashtag_list:
            user_hashtags[author].add(tag.lower())
            user_engagement[author][tag.lower()] += p.engagement

    if not user_hashtags:
        return []

    if target_user not in user_hashtags:
        target_user = next(iter(user_hashtags))

    users = list(user_hashtags.keys())
    all_tags = sorted({tag for tags in user_hashtags.values() for tag in tags})
    if not all_tags:
        return []

    matrix = np.zeros((len(users), len(all_tags)))
    tag_idx = {t: i for i, t in enumerate(all_tags)}
    for u_idx, u in enumerate(users):
        for tag, w in user_engagement[u].items():
            matrix[u_idx, tag_idx[tag]] = w

    target_idx = users.index(target_user)
    sim = cosine_similarity(matrix[target_idx:target_idx + 1], matrix).flatten()

    target_tags = user_hashtags[target_user]
    candidate_scores: Dict[str, float] = defaultdict(float)
    for u_idx, similarity in enumerate(sim):
        if u_idx == target_idx or similarity <= 0:
            continue
        other = users[u_idx]
        for tag in user_hashtags[other] - target_tags:
            candidate_scores[tag] += similarity * user_engagement[other][tag]

    ranked = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{"hashtag": tag, "score": round(score, 3)} for tag, score in ranked]


def analyze_recommendations(posts: List) -> Dict[str, Any]:
    if not posts:
        return {"sample_user": None, "content_based": [], "collaborative": []}

    # Pick first author with multiple posts
    author_counts: Dict[str, int] = defaultdict(int)
    for p in posts:
        author_counts[p.author] += 1
    sample_user = max(author_counts.items(), key=lambda x: x[1])[0]

    sample_post_id = posts[0].id
    return {
        "sample_user": sample_user,
        "sample_post_id": sample_post_id,
        "content_based": content_based_recommendations(posts, sample_post_id),
        "collaborative": collaborative_recommendations(posts, sample_user),
    }
