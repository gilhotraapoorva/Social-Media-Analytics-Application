"""End-to-end smoke test: register → create case → hit every module → export reports."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Use a temp DB so tests don't pollute the real instance/app.db
_tmpdir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"
os.environ["SECRET_KEY"] = "test-secret"

from app import create_app  # noqa: E402
from models import db  # noqa: E402


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as c:
        yield c


def test_full_workflow(client):
    # Register
    r = client.post("/register", data={
        "username": "alice", "email": "alice@example.com", "password": "secret"
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"My Cases" in r.data or b"Cases" in r.data

    # Create case (uses sample fallback since APIFY_API_TOKEN is empty)
    r = client.post("/cases/new", data={
        "name": "Tesla Brand Analysis",
        "brand": "Tesla",
        "keyword": "tesla",
        "platform": "twitter",
        "limit": "60",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"Tesla" in r.data

    # Find the case id from the cases list
    r = client.get("/cases")
    assert r.status_code == 200

    # Hit every module endpoint
    modules = [
        "sentiment", "trends", "network", "recommendations", "fake_news",
        "segmentation", "visualization", "ad_optimization", "influencer",
        "realtime", "competitor", "popularity",
    ]
    for m in modules:
        r = client.get(f"/cases/1/modules/{m}")
        assert r.status_code == 200, f"Module {m} returned {r.status_code}"

    # Reports
    r = client.get("/cases/1/report.html")
    assert r.status_code == 200
    r = client.get("/cases/1/report.pdf")
    assert r.status_code == 200
    assert r.data[:4] == b"%PDF"
