"""Module 6: User Segmentation — KMeans clustering on behavior features."""
from typing import List, Dict, Any
from collections import defaultdict

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def _build_user_features(posts: List) -> Dict[str, Dict[str, float]]:
    by_user: Dict[str, Dict[str, list]] = defaultdict(
        lambda: {"likes": [], "retweets": [], "replies": [], "hashtags": [], "posts": 0}
    )
    for p in posts:
        u = p.author or "unknown"
        by_user[u]["likes"].append(p.likes or 0)
        by_user[u]["retweets"].append(p.retweets or 0)
        by_user[u]["replies"].append(p.replies or 0)
        by_user[u]["hashtags"].append(len(p.hashtag_list))
        by_user[u]["posts"] += 1

    features = {}
    for user, data in by_user.items():
        n = max(len(data["likes"]), 1)
        features[user] = {
            "post_count": data["posts"],
            "avg_likes": sum(data["likes"]) / n,
            "avg_retweets": sum(data["retweets"]) / n,
            "avg_replies": sum(data["replies"]) / n,
            "avg_hashtags": sum(data["hashtags"]) / n,
        }
    return features


def segment_users(posts: List, k: int = 4) -> Dict[str, Any]:
    features = _build_user_features(posts)
    if not features:
        return {"clusters": [], "users": [], "k": 0}

    users = list(features.keys())
    # If we have fewer users than clusters, fall back gracefully
    k = max(2, min(k, len(users)))
    if len(users) < 2:
        return {
            "clusters": [{"id": 0, "size": len(users), "label": "Single user", "members": users}],
            "users": [{"user": users[0], "cluster": 0, **features[users[0]]}],
            "k": 1,
        }

    X = np.array([
        [features[u]["post_count"], features[u]["avg_likes"], features[u]["avg_retweets"],
         features[u]["avg_replies"], features[u]["avg_hashtags"]]
        for u in users
    ])
    scaled = StandardScaler().fit_transform(X)
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(scaled)

    # Profile each cluster
    cluster_summary = {}
    for cid in range(k):
        mask = labels == cid
        if mask.sum() == 0:
            continue
        members = [users[i] for i in range(len(users)) if mask[i]]
        avg = X[mask].mean(axis=0)
        cluster_summary[cid] = {
            "id": cid,
            "size": int(mask.sum()),
            "members": members,
            "avg_post_count": round(float(avg[0]), 2),
            "avg_likes": round(float(avg[1]), 2),
            "avg_retweets": round(float(avg[2]), 2),
            "avg_replies": round(float(avg[3]), 2),
            "avg_hashtags": round(float(avg[4]), 2),
        }

    # Label clusters with friendly names
    sorted_by_engagement = sorted(
        cluster_summary.values(),
        key=lambda c: c["avg_likes"] + c["avg_retweets"], reverse=True,
    )
    labels_map = ["Power Users", "Active Engagers", "Casual Posters", "Lurkers", "Bots/Spam"]
    for idx, cluster in enumerate(sorted_by_engagement):
        cluster["label"] = labels_map[idx] if idx < len(labels_map) else f"Cluster {cluster['id']}"

    user_rows = [
        {"user": users[i], "cluster": int(labels[i]), **{k: round(v, 2) for k, v in features[users[i]].items()}}
        for i in range(len(users))
    ]
    return {
        "k": k,
        "clusters": list(cluster_summary.values()),
        "users": user_rows,
    }
