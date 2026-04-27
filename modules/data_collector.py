"""Data collection from Apify (Twitter/Facebook) with sample-data fallback."""
from __future__ import annotations

import json
import logging
import random
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import Config

logger = logging.getLogger(__name__)

HASHTAG_RE = re.compile(r"#(\w+)")
MENTION_RE = re.compile(r"@(\w+)")


def _extract_hashtags(text: str) -> List[str]:
    return [h.lower() for h in HASHTAG_RE.findall(text or "")]


def _extract_mentions(text: str) -> List[str]:
    return [m.lower() for m in MENTION_RE.findall(text or "")]


def collect_posts(keyword: str, platform: str, limit: int = 100,
                  api_token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Collect posts for a keyword on a platform.

    Tries Apify first; falls back to a deterministic synthetic dataset if no
    token is configured (or if Apify fails). The synthetic dataset is shaped
    so that all 12 analytics modules produce meaningful output.
    """
    token = api_token or Config.APIFY_API_TOKEN
    if token:
        try:
            return _collect_via_apify(keyword, platform, limit, token)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Apify collection failed (%s); falling back to sample data", exc)

    return _generate_sample_posts(keyword, platform, limit)


def _collect_via_apify(keyword: str, platform: str, limit: int, token: str) -> List[Dict[str, Any]]:
    """Run an Apify actor for the given platform and return normalized posts."""
    try:
        from apify_client import ApifyClient  # type: ignore
    except ImportError as exc:
        raise RuntimeError("apify-client not installed") from exc

    client = ApifyClient(token)

    if platform.lower() in ("twitter", "x"):
        actor_id = Config.APIFY_TWITTER_ACTOR
        run_input = {
            "searchTerms": [keyword],
            "maxItems": limit,
            "sort": "Latest",
        }
    elif platform.lower() == "facebook":
        actor_id = Config.APIFY_FACEBOOK_ACTOR
        run_input = {
            "startUrls": [{"url": f"https://www.facebook.com/search/posts?q={keyword}"}],
            "resultsLimit": limit,
        }
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    run = client.actor(actor_id).call(run_input=run_input)
    if not run:
        raise RuntimeError("Apify actor returned no run")

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return [_normalize_apify_item(item, platform) for item in items[:limit]]


def _normalize_apify_item(item: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Normalize Apify output into our internal post schema."""
    text = item.get("text") or item.get("full_text") or item.get("content") or ""
    return {
        "external_id": str(item.get("id") or item.get("postId") or item.get("url", "")),
        "platform": platform,
        "author": item.get("user", {}).get("screen_name")
                  or item.get("authorName")
                  or item.get("user_name")
                  or "unknown",
        "text": text,
        "url": item.get("url") or item.get("permalink"),
        "posted_at": _parse_datetime(item.get("created_at") or item.get("time")),
        "likes": int(item.get("favorite_count") or item.get("likes") or 0),
        "retweets": int(item.get("retweet_count") or item.get("shares") or 0),
        "replies": int(item.get("reply_count") or item.get("comments") or 0),
        "impressions": int(item.get("views") or item.get("impressions") or 0),
        "hashtags": ",".join(_extract_hashtags(text)),
        "mentions": ",".join(_extract_mentions(text)),
    }


def _parse_datetime(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ("%a %b %d %H:%M:%S %z %Y", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(value), fmt)
        except (ValueError, TypeError):
            continue
    return None


# ---------------------------------------------------------------------------
# Synthetic dataset — designed so all 12 analytics modules produce results.
# ---------------------------------------------------------------------------

POSITIVE_TEMPLATES = [
    "I absolutely love {kw}! Best decision ever. #{kw} #love #amazing",
    "Just got my {kw} and it's incredible. Highly recommend! #{kw} #greatproduct",
    "{kw} is changing the game. Innovation at its finest. #innovation #{kw}",
    "Unboxing my new {kw} - quality is top-notch. #unboxing #{kw} #premium",
    "Customer service at {kw} was outstanding today! #{kw} #customerservice",
]
NEGATIVE_TEMPLATES = [
    "Disappointed with {kw}. Quality has dropped significantly. #{kw} #fail",
    "Worst experience ever with {kw}. Avoid at all costs. #{kw} #scam",
    "{kw} is overpriced and underwhelming. Returning it. #{kw} #refund",
    "Customer support at {kw} was unhelpful and rude. #{kw} #badservice",
    "{kw} keeps breaking. Build quality is awful. #{kw} #broken",
]
NEUTRAL_TEMPLATES = [
    "{kw} announced new features today. Curious to see how they perform. #{kw} #news",
    "Reading reviews about {kw} before deciding. #{kw} #research",
    "{kw} stock moved 2% today. #{kw} #stocks #market",
    "Comparing {kw} with competitors. Each has trade-offs. #{kw} #comparison",
    "Question: does anyone use {kw} professionally? #{kw} #askingforafriend",
]
FAKE_TEMPLATES = [
    "BREAKING: {kw} CEO arrested in massive fraud scandal! Share before deleted! #{kw} #fake",
    "SHOCKING: {kw} secretly tracks your data 24/7. Government cover-up! #{kw} #conspiracy",
    "URGENT!! {kw} giving away free products to first 1000! Click link! #{kw} #scam",
]

USERNAMES = [
    "alice_t", "bob_dev", "carla_v", "dan_w", "eva_m", "frank_x",
    "gina_r", "henry_p", "ivy_q", "jack_s", "kim_y", "lola_z",
    "mike_a", "nora_b", "oscar_c", "paula_d", "quinn_e", "rita_f",
    "sam_g", "tara_h", "uma_i", "victor_j", "wendy_k", "xander_l",
    "yara_n", "zane_o",
]


def _generate_sample_posts(keyword: str, platform: str, limit: int) -> List[Dict[str, Any]]:
    """Build a deterministic synthetic dataset for a keyword."""
    rng = random.Random(hash(keyword) & 0xFFFFFFFF)
    posts: List[Dict[str, Any]] = []
    now = datetime.utcnow()

    kw_clean = re.sub(r"\W+", "", keyword).lower() or "topic"

    for i in range(limit):
        bucket = rng.random()
        if bucket < 0.45:
            template = rng.choice(POSITIVE_TEMPLATES)
        elif bucket < 0.75:
            template = rng.choice(NEUTRAL_TEMPLATES)
        elif bucket < 0.93:
            template = rng.choice(NEGATIVE_TEMPLATES)
        else:
            template = rng.choice(FAKE_TEMPLATES)

        # Add a mention to seed network edges
        if rng.random() < 0.6:
            mentioned = rng.choice(USERNAMES)
            text = template.format(kw=kw_clean) + f" @{mentioned}"
        else:
            text = template.format(kw=kw_clean)

        author = rng.choice(USERNAMES)
        posted_at = now - timedelta(hours=rng.randint(0, 24 * 30))

        # Engagement is correlated with sentiment-positive templates and a few
        # power users, so influencer detection has signal.
        is_influencer = author in ("alice_t", "frank_x", "mike_a")
        base_engagement = rng.randint(5, 40) if not is_influencer else rng.randint(80, 500)

        posts.append({
            "external_id": f"sample-{kw_clean}-{i}",
            "platform": platform,
            "author": author,
            "text": text,
            "url": f"https://example.com/{platform}/{kw_clean}/{i}",
            "posted_at": posted_at,
            "likes": base_engagement + rng.randint(0, 50),
            "retweets": int(base_engagement * 0.3) + rng.randint(0, 20),
            "replies": int(base_engagement * 0.15) + rng.randint(0, 10),
            "impressions": base_engagement * rng.randint(20, 100),
            "hashtags": ",".join(_extract_hashtags(text)),
            "mentions": ",".join(_extract_mentions(text)),
        })

    return posts


# Optional: persist a generated sample dataset to disk for reuse
def save_sample_dataset(keyword: str, platform: str, limit: int = 100) -> Path:
    posts = _generate_sample_posts(keyword, platform, limit)
    out = Config.DATA_DIR / f"sample_{platform}_{keyword}.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    def _default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        return str(o)

    out.write_text(json.dumps(posts, indent=2, default=_default))
    return out
