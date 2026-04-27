"""Application configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
    APIFY_TWITTER_ACTOR = os.environ.get("APIFY_TWITTER_ACTOR", "apidojo/twitter-scraper-lite")
    APIFY_FACEBOOK_ACTOR = os.environ.get("APIFY_FACEBOOK_ACTOR", "apify/facebook-posts-scraper")

    REPORTS_DIR = BASE_DIR / "reports"
    DATA_DIR = BASE_DIR / "data"

    # Use sample data when Apify token is missing
    USE_SAMPLE_DATA_FALLBACK = True
