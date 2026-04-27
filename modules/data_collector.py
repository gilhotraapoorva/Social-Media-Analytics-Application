"""Data collection from Apify (Twitter/Facebook) with live-data only."""
from __future__ import annotations

import json
import logging
import random
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests

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

    Tries Apify first and returns an empty list if no token is configured or
    if Apify fails/returns blank data. The application should render an empty
    state instead of inventing synthetic posts.
    """
    token = api_token or Config.APIFY_API_TOKEN
    if not token:
        logger.info("No Apify token configured; returning no posts for %s/%s", platform, keyword)
        return []

    try:
        posts = _collect_via_apify(keyword, platform, limit, token)
        if any((post.get("text") or "").strip() or int(post.get("likes") or 0) + int(post.get("retweets") or 0) + int(post.get("replies") or 0) + int(post.get("impressions") or 0) > 0 for post in posts):
            return posts
        logger.warning("Apify returned blank zero-signal posts for %s/%s", platform, keyword)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Apify collection failed (%s); returning no posts", exc)

    hn_posts = _collect_via_hacker_news(keyword, limit)
    if hn_posts:
        return hn_posts

    rss_posts = _collect_via_google_news(keyword, limit)
    if rss_posts:
        return rss_posts

    return []


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

    run = client.actor(actor_id).call(
        run_input=run_input,
        timeout_secs=90,
        wait_secs=30,
    )

    if not run:
        raise RuntimeError("Apify actor returned no run")

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return [_normalize_apify_item(item, platform) for item in items[:limit]]

def _collect_via_google_news(keyword: str, limit: int) -> List[Dict[str, Any]]:
    """Collect live news items for a keyword via Google News RSS."""
    url = f"https://news.google.com/rss/search?q={requests.utils.quote(keyword)}&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    channel = root.find("channel")
    if channel is None:
        return []

    posts: List[Dict[str, Any]] = []
    for item in channel.findall("item")[:limit]:
        title = (item.findtext("title") or "").strip()
        description = (item.findtext("description") or "").strip()
        link = (item.findtext("link") or "").strip() or None
        pub_date = _parse_rss_datetime(item.findtext("pubDate"))
        text = f"{title}. {description}".strip(" .")

        posts.append({
            "external_id": link or title,
            "platform": "news",
            "author": "Google News",
            "text": text,
            "url": link,
            "posted_at": pub_date,
            "likes": 0,
            "retweets": 0,
            "replies": 0,
            "impressions": 0,
            "hashtags": ",".join(_extract_hashtags(text)),
            "mentions": ",".join(_extract_mentions(text)),
        })

    if any((post.get("text") or "").strip() for post in posts):
        logger.info("Collected %s live Google News items for %s", len(posts), keyword)
        return posts
    return []


def _collect_via_hacker_news(keyword: str, limit: int) -> List[Dict[str, Any]]:
    """Collect live Hacker News stories for a keyword.

    This gives us real engagement signals via points and comment counts when
    social scraping endpoints are unavailable.
    """
    url = f"https://hn.algolia.com/api/v1/search?query={requests.utils.quote(keyword)}&tags=story&hitsPerPage={limit}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    payload = response.json()
    posts: List[Dict[str, Any]] = []
    for hit in payload.get("hits", [])[:limit]:
        title = (hit.get("title") or "").strip()
        url_value = hit.get("url")
        points = int(hit.get("points") or 0)
        comments = int(hit.get("num_comments") or 0)
        posts.append({
            "external_id": str(hit.get("objectID") or url_value or title),
            "platform": "hackernews",
            "author": hit.get("author") or "hn_user",
            "text": title,
            "url": url_value,
            "posted_at": _parse_datetime_from_epoch(hit.get("created_at_i")),
            "likes": points,
            "retweets": comments,
            "replies": comments,
            "impressions": points + comments,
            "hashtags": ",".join(_extract_hashtags(title)),
            "mentions": "",
        })

    if any((post.get("text") or "").strip() and (post.get("likes") or 0) + (post.get("retweets") or 0) + (post.get("replies") or 0) > 0 for post in posts):
        logger.info("Collected %s live Hacker News items for %s", len(posts), keyword)
        return posts
    return []


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


def _parse_rss_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except (ValueError, TypeError):
            continue
    return None


def _parse_datetime_from_epoch(value) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.utcfromtimestamp(float(value))
    except (TypeError, ValueError, OSError):
        return None


