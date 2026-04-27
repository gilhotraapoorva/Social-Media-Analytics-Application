"""Module 5: Fake News Detection — heuristic + ML classifier (Logistic Regression)."""
from typing import List, Dict, Any
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# Lightweight, deterministic seed dataset to bootstrap the classifier.
# The real product could swap in a larger LIAR / FakeNewsNet dataset.
_SEED_FAKE = [
    "BREAKING: Celebrity arrested in massive cover-up — share before deleted!",
    "SHOCKING government conspiracy exposed by anonymous insider!!",
    "URGENT: free iPhones for first 1000 people who click this link",
    "Scientists CONFIRM the moon is hollow — media silent",
    "Doctors HATE this one weird trick to cure all diseases overnight",
    "EXPOSED: secret elite plan to control population via 5G chips",
    "Click here to claim your $5000 reward — limited time!!!",
    "This billionaire vanished after revealing the truth — repost now",
]
_SEED_REAL = [
    "Quarterly earnings report released; revenue grew 8% year-over-year.",
    "City council approved the new transit plan after public consultation.",
    "Researchers published a peer-reviewed study on solar panel efficiency.",
    "The team announced new accessibility features in the latest release.",
    "Storm forecast indicates heavy rainfall through the weekend in coastal areas.",
    "Annual conference returns to in-person format this October.",
    "Customer support hours have been extended on weekends starting next month.",
    "Regulators approved the merger pending standard antitrust review.",
]

URGENCY_RE = re.compile(r"\b(BREAKING|URGENT|SHOCKING|EXPOSED|CONFIRMED|MUST READ)\b", re.I)
EXCESS_PUNCT_RE = re.compile(r"(!{2,}|\?{2,})")
ALLCAPS_RE = re.compile(r"\b[A-Z]{4,}\b")
CLICKBAIT_RE = re.compile(r"\b(click here|share before|repost now|won.t believe)\b", re.I)


def _heuristic_features(text: str) -> Dict[str, float]:
    return {
        "urgency": float(bool(URGENCY_RE.search(text or ""))),
        "excess_punct": float(bool(EXCESS_PUNCT_RE.search(text or ""))),
        "allcaps": float(len(ALLCAPS_RE.findall(text or "")) > 2),
        "clickbait": float(bool(CLICKBAIT_RE.search(text or ""))),
    }


def _train_pipeline() -> Pipeline:
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    X = _SEED_FAKE + _SEED_REAL
    y = [1] * len(_SEED_FAKE) + [0] * len(_SEED_REAL)
    pipeline.fit(X, y)
    return pipeline


_pipeline = _train_pipeline()


def classify(text: str) -> Dict[str, Any]:
    features = _heuristic_features(text)
    heuristic_score = sum(features.values()) / 4.0  # 0..1

    proba = _pipeline.predict_proba([text or ""])[0]
    ml_fake_prob = float(proba[1])

    # Blend: heuristic + ML
    fake_prob = 0.4 * heuristic_score + 0.6 * ml_fake_prob
    label = "fake" if fake_prob >= 0.5 else "real"

    return {
        "label": label,
        "fake_probability": round(fake_prob, 3),
        "ml_probability": round(ml_fake_prob, 3),
        "heuristic_score": round(heuristic_score, 3),
        "signals": features,
    }


def analyze_posts(posts: List) -> Dict[str, Any]:
    fake_count = 0
    flagged = []
    details = []
    for p in posts:
        result = classify(p.text)
        p.is_fake = result["label"] == "fake"
        if p.is_fake:
            fake_count += 1
            flagged.append({
                "id": p.id,
                "author": p.author,
                "text": p.text[:200],
                "fake_probability": result["fake_probability"],
            })
        details.append({
            "id": p.id,
            "label": result["label"],
            "fake_probability": result["fake_probability"],
        })
    n = max(len(posts), 1)
    return {
        "total": len(posts),
        "fake": fake_count,
        "real": n - fake_count,
        "fake_ratio": round(fake_count / n, 3),
        "flagged": flagged,
        "details": details,
    }
