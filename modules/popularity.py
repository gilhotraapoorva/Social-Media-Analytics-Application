"""Module 12: Popularity Prediction — ML model that predicts engagement."""
from typing import List, Dict, Any
import numpy as np
import re

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score


def _featurize(post) -> Dict[str, Any]:
    text = post.text or ""
    return {
        "text": text,
        "length": len(text),
        "word_count": len(text.split()),
        "hashtag_count": len(post.hashtag_list),
        "mention_count": len(post.mention_list),
        "exclamations": text.count("!"),
        "questions": text.count("?"),
        "uppercase_ratio": (sum(1 for c in text if c.isupper()) / max(len(text), 1)),
        "url_present": int("http" in text),
    }


def train_and_predict(posts: List) -> Dict[str, Any]:
    if len(posts) < 6:
        return {
            "trained": False,
            "reason": "Need at least 6 posts to train",
            "predictions": [],
            "metrics": {},
        }

    feats = [_featurize(p) for p in posts]
    targets_raw = np.array([p.engagement for p in posts], dtype=float)
    # Engagement is heavily right-skewed; log1p transform stabilizes variance
    # so GBR can actually learn the signal instead of fitting noise.
    targets = np.log1p(targets_raw)

    texts = [f["text"] for f in feats]
    numeric = np.array([
        [f["length"], f["word_count"], f["hashtag_count"], f["mention_count"],
         f["exclamations"], f["questions"], f["uppercase_ratio"], f["url_present"]]
        for f in feats
    ], dtype=float)

    # Author identity is a strong signal in social engagement; encode each
    # author as a one-hot column. (Frequency encoding alone leaks the target
    # at training time; one-hot is cleaner and lets the tree learn per-user effects.)
    authors = [p.author or "unknown" for p in posts]
    unique_authors = sorted(set(authors))
    author_idx = {a: i for i, a in enumerate(unique_authors)}
    X_author = np.zeros((len(posts), len(unique_authors)))
    for i, a in enumerate(authors):
        X_author[i, author_idx[a]] = 1.0

    tfidf = TfidfVectorizer(max_features=200, stop_words="english")
    X_text = tfidf.fit_transform(texts).toarray()
    scaler = StandardScaler()
    X_num = scaler.fit_transform(numeric)
    X = np.hstack([X_text, X_num, X_author])

    n = len(posts)
    split = max(1, int(n * 0.8))
    rng = np.random.RandomState(42)
    indices = rng.permutation(n)
    train_idx, test_idx = indices[:split], indices[split:]

    model = GradientBoostingRegressor(random_state=42, n_estimators=100, max_depth=3)
    model.fit(X[train_idx], targets[train_idx])

    if len(test_idx) > 0:
        # Evaluate in original engagement space (after expm1)
        preds_log = model.predict(X[test_idx])
        preds = np.expm1(preds_log)
        actual = targets_raw[test_idx]
        mae = float(mean_absolute_error(actual, preds))
        r2 = float(r2_score(actual, preds)) if len(test_idx) > 1 else 0.0
    else:
        mae, r2 = 0.0, 0.0

    all_preds = np.expm1(model.predict(X))
    rows = []
    for i, p in enumerate(posts):
        rows.append({
            "post_id": p.id,
            "author": p.author,
            "text": (p.text[:120] + "...") if len(p.text) > 120 else p.text,
            "actual_engagement": int(p.engagement),
            "predicted_engagement": round(float(all_preds[i]), 1),
        })

    rows.sort(key=lambda r: r["predicted_engagement"], reverse=True)
    return {
        "trained": True,
        "predictions": rows,
        "top_predicted": rows[:10],
        "metrics": {
            "train_size": int(split),
            "test_size": int(n - split),
            "mae": round(mae, 2),
            "r2": round(r2, 3),
        },
    }
