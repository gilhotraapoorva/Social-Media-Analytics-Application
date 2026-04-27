<<<<<<< HEAD
# Social-Media-Analytics-Application
=======
# Social Media Analytics Dashboard Application

> **SocialPulse Analytics** — a full-stack, AI-powered social media analytics platform.
> Ingests posts from **X (Twitter)** and **Facebook** via the **Apify API**, runs
> **12 analytical modules** (NLP, network science, machine learning), and renders the
> results through interactive multi-tab dashboards with **PDF & HTML report export**.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)]()
[![Flask](https://img.shields.io/badge/Flask-3.0-green)]()
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)]()
[![License](https://img.shields.io/badge/License-Educational-yellow)]()

---

## Table of Contents

1. [What This App Does](#what-this-app-does)
2. [Live Demo Walkthrough](#live-demo-walkthrough)
3. [Installation (5 minutes)](#installation-5-minutes)
4. [Configure Apify (Optional)](#configure-apify-optional)
5. [Run the App](#run-the-app)
6. [How to Use — Step by Step](#how-to-use--step-by-step)
7. [What Each Module Shows You](#what-each-module-shows-you)
8. [Generating Reports](#generating-reports)
9. [Project Structure](#project-structure)
10. [Architecture](#architecture)
11. [Tech Stack](#tech-stack)
12. [Running Tests](#running-tests)
13. [Troubleshooting](#troubleshooting)
14. [FAQ](#faq)
15. [Deployment](#deployment)
16. [License](#license)

---

## What This App Does

SocialPulse is a **single Flask web app** that lets a user:

1. **Sign up / log in** to a private workspace
2. **Create a "Case"** — a topic, brand, or campaign you want to analyze
3. **Auto-collect posts** for the case (real Apify data if a token is set, otherwise a
   built-in synthetic dataset so the app works out of the box)
4. **View an interactive dashboard** with charts, KPI cards, and 12 analytics modules
5. **Export a PDF or HTML report** with the full case study, methodology, and results

**Built for the *Social Media Analytics Dashboard Application* assignment.** Implements
every required feature: authentication, case-based workspaces, all 12 modules, multi-tab
dashboard, search filters, PDF/HTML reports.

### Feature checklist (from the assignment)

| Required                                             | Status |
|------------------------------------------------------|--------|
| Login authentication                                 | ✅ Flask-Login + pbkdf2 password hashing |
| Per-case workspaces                                  | ✅ Cases organized by user, topic, brand |
| Apify integration for X/Facebook                     | ✅ With synthetic fallback when no token |
| 12 analytics modules                                 | ✅ All implemented as separate features  |
| Multi-tab dashboard (Sentiment/Trends/Network/Ads/Prediction) | ✅ Plus Overview tab |
| KPIs, bar/line/pie charts, filters, insights        | ✅ Bootstrap 5 + Chart.js + D3.js |
| Search by keyword/hashtag/user/post URL              | ✅ Via case keyword + module filters |
| PDF & HTML report export                             | ✅ xhtml2pdf + Jinja2 |
| ML/NLP libraries                                     | ✅ VADER, scikit-learn, NetworkX |
| Real-time monitoring / anomaly detection             | ✅ Bonus feature |
| Negative-sentiment alerts                            | ✅ Bonus feature |

---

## Live Demo Walkthrough

Here's what the user journey looks like end-to-end (takes ~2 minutes after install):

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Register   │ →  │  Create Case │ →  │  Dashboard   │ →  │   Report     │
│              │    │              │    │              │    │              │
│ username     │    │ name: Tesla  │    │ 6 tabs       │    │ HTML or PDF  │
│ email        │    │ keyword:     │    │ 12 modules   │    │ download     │
│ password     │    │   tesla      │    │ Charts &     │    │              │
│              │    │ platform: X  │    │ KPIs         │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                          │
                          ▼
                    ~100 posts auto
                    -collected from
                    Apify or sample
                    dataset
```

---

## Installation (5 minutes)

### Prerequisites

- **Python 3.9+** (3.10+ recommended)
- **pip** (comes with Python)
- About **200 MB** disk space (for the virtualenv with sklearn/numpy/pandas)
- A modern browser (Chrome, Firefox, Safari, Edge)

### Steps

```bash
# 1. Clone the repo (or unzip the source)
git clone https://github.com/<your-username>/Social-Media-Analytics-Application.git
cd Social-Media-Analytics-Application

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate            # Windows

# 3. Upgrade pip (some pinned packages need a recent pip)
pip install --upgrade pip

# 4. Install all dependencies
pip install -r requirements.txt
```

That's it — no database setup, no Docker, no Node. SQLite + Python only.

---

## Configure Apify (Optional)

The app **works out of the box without any API keys** — it falls back to a deterministic
synthetic dataset shaped so all 12 modules produce realistic results.

If you want **real Twitter/Facebook data**:

### 1. Get an Apify token

1. Sign up free at [https://apify.com](https://apify.com)
2. Go to **Settings → Integrations → API tokens**
3. Copy your token (starts with `apify_api_...`)

### 2. Set environment variables

Either copy `.env.example` to `.env` and edit, or export directly:

```bash
export APIFY_API_TOKEN="apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Optional: override which Apify actor to use
export APIFY_TWITTER_ACTOR="apidojo/twitter-scraper-lite"
export APIFY_FACEBOOK_ACTOR="apify/facebook-posts-scraper"
```

### 3. Other recommended settings

```bash
# Random secret for session signing (REQUIRED in production)
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"

# Custom database (default is SQLite at instance/app.db)
# export DATABASE_URL="postgresql://user:pass@host:5432/socialpulse"
# export DATABASE_URL="mysql+pymysql://user:pass@host:3306/socialpulse"
```

If `APIFY_API_TOKEN` is unset (or the Apify call fails), the app silently falls back to
the synthetic dataset — so you always get working analytics.

---

## Run the App

```bash
python app.py
```

You should see:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5050
```

Open **http://127.0.0.1:5050** in your browser.

---

## How to Use — Step by Step

### Step 1 — Register an account

- Visit `http://127.0.0.1:5050` → you'll be redirected to `/login`
- Click **"Register here"** at the bottom
- Fill in **username**, **email**, **password** → click **Create Account**
- You're auto-logged in and sent to **My Cases**

### Step 2 — Create your first Case

A "Case" is one isolated analytics workspace. You'll typically have one per
brand/topic/campaign you want to analyze.

- Click **+ New Case** in the top-right
- Fill in:
  - **Case Name** *(required)* — e.g. `Tesla Q1 Brand Sentiment`
  - **Brand / Topic** *(optional)* — e.g. `Tesla`
  - **Keyword** *(required)* — what to search for, e.g. `tesla`, `#tsla`, `@elonmusk`
  - **Platform** — X (Twitter) or Facebook
  - **Apify Source URL** *(optional)* — if you have a specific actor in mind
  - **Post URLs / IDs** *(optional)* — paste specific URLs to focus the analysis
  - **Date range** *(optional)* — start / end dates
  - **Posts to collect** — default 100 (range 10–500)
  - **Description** — your goal for this case
- Click **Create & Collect Data**

The app collects ~100 posts (Apify or synthetic fallback) and drops you into the dashboard.

### Step 3 — Explore the Dashboard

The dashboard has **6 tabs**:

| Tab          | Shows                                                                       |
|--------------|-----------------------------------------------------------------------------|
| Overview     | KPI cards (positive/negative/engagement/fake), top influencers, hashtags    |
| Sentiment    | Pie chart + per-post sentiment table                                         |
| Trends       | Top hashtags + top keywords (bar charts)                                     |
| Network      | D3.js force-directed graph with community-colored nodes                     |
| Ads          | CTR / Conversion / ROI per simulated ad campaign                            |
| Prediction   | ML-predicted vs. actual engagement (Gradient Boosting)                       |

Below the tabs, the **Overview** tab also lists all 12 modules — click any to open its
**dedicated dashboard** with deeper detail (KPI cards, charts, full data tables, insights
summary).

### Step 4 — Export a Report

In the dashboard header, click:
- **HTML Report** → downloads `report_case_<id>.html` (open in any browser)
- **PDF Report** → downloads `report_case_<id>.pdf` (3-page formatted report)

Both reports include:
1. Introduction
2. Problem statement
3. Case study description
4. System architecture
5. Methodology
6. Implementation snippets
7. Results & analysis (sentiment, hashtags, network, influencers, segments, fake news, ads, prediction)
8. Conclusion
9. References

### Step 5 — Refresh or Delete

Back on the **Cases** page or via the dashboard:
- **🔄 Refresh Data** re-collects posts (useful when running real-time tracking)
- **🗑️ Delete** removes the case and all its posts

---

## What Each Module Shows You

### Module 1 — Sentiment Analysis 🙂
Classifies every post as **positive / neutral / negative** using VADER. Shows distribution
pie chart, average sentiment score, per-post details, and **high-engagement negative
alerts** (posts with score ≤ -0.4 and engagement ≥ 50).

### Module 2 — Trending Topics 🔥
Extracts hashtags and keywords, ranks them by frequency, and computes a **trend score**
that combines frequency with average engagement.

### Module 3 — Network Analysis 🔗
Builds a directed graph of *author → mention* edges, detects communities using greedy
modularity, and computes eigenvector + betweenness centrality. Renders an interactive
**D3.js force-directed graph** with community-colored nodes sized by influence.

### Module 4 — Recommendations 💡
Two engines:
- **Content-based**: TF-IDF cosine similarity on post text → "posts similar to this one"
- **Collaborative**: cosine similarity on a user×hashtag engagement matrix → "users like
  you also engaged with these hashtags"

### Module 5 — Fake News Detection 🛡️
Hybrid classifier: Logistic Regression on TF-IDF n-grams (60% weight) + linguistic
heuristics (urgency words, excessive punctuation, ALL CAPS, clickbait phrases — 40% weight).

### Module 6 — User Segmentation 👥
KMeans clustering on standardized behavioral features (post count, avg likes, retweets,
replies, hashtags). Auto-labels clusters as *Power Users / Active Engagers / Casual
Posters / Lurkers*.

### Module 7 — Data Visualization 📊
Time-bucketed (daily) charts for engagement, reach, sentiment, and a top-authors leaderboard.

### Module 8 — Ad Optimization 📢
Treats top-engagement posts as ad creatives, simulates campaign metrics (CTR, conversion
rate, ROI), and surfaces the **best vs. worst** campaign.

### Module 9 — Influencer Detection ⭐
Composite score = `0.5 × eigenvector + 0.3 × pagerank + 0.2 × engagement_share`. More
robust than any single centrality metric.

### Module 10 — Real-Time Monitoring 📡
Hourly keyword volume timeline + statistical anomaly detection (mean + 2σ threshold) +
negative-sentiment alert feed.

### Module 11 — Competitor Analysis 🆚
Pick another case to compare. Side-by-side KPIs, engagement deltas, sentiment differences,
shared vs. unique hashtag strategy.

### Module 12 — Popularity Prediction 📈
Gradient Boosting Regressor on TF-IDF + structural features + author one-hot encoding.
Predicts engagement on a 80/20 holdout. Shows MAE, R², and per-post predictions.
*(On the bundled synthetic dataset: R² ≈ 0.89, MAE ≈ 26.)*

---

## Generating Reports

Reports are generated **on demand** from the dashboard header — there's no separate report
build step. Each click re-runs all 12 modules against the latest collected posts and
renders a fresh document.

```
HTML report → reports/report_case_<id>.html  (rendered with Jinja2)
PDF report  → reports/report_case_<id>.pdf   (xhtml2pdf, ~3 pages)
```

The same template (`templates/report.html`) is used for both formats.

---

## Project Structure

```
Social-Media-Analytics-Application/
├── app.py                      # Flask app + all routes (~330 lines)
├── config.py                   # SECRET_KEY, DATABASE_URL, Apify token
├── requirements.txt
├── README.md                   # ← you are here
├── .env.example                # Sample environment config
├── docs/
│   ├── REPORT.md               # Full project report (markdown)
│   └── ARCHITECTURE.md         # Architecture deep-dive
├── models/                     # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py                 # User (auth)
│   ├── case.py                 # Case (workspace)
│   └── post.py                 # Post (collected social media post)
├── modules/                    # All analytics + collection + report
│   ├── data_collector.py       # Apify client + synthetic fallback
│   ├── sentiment.py            # M1 — VADER
│   ├── trends.py               # M2 — Hashtag/keyword frequency
│   ├── network.py              # M3 — Graph + communities
│   ├── recommendations.py      # M4 — Content + collaborative
│   ├── fake_news.py            # M5 — TF-IDF + heuristics
│   ├── segmentation.py         # M6 — KMeans
│   ├── visualization.py        # M7 — Time series
│   ├── ad_optimization.py      # M8 — CTR/Conv/ROI
│   ├── influencer.py           # M9 — Composite centrality
│   ├── realtime.py             # M10 — Anomaly detection
│   ├── competitor.py           # M11 — Cross-case comparison
│   ├── popularity.py           # M12 — Gradient Boosting
│   └── report.py               # HTML / PDF rendering
├── templates/                  # Jinja2 + Bootstrap 5
│   ├── base.html               # Master layout
│   ├── login.html · register.html
│   ├── cases.html · new_case.html
│   ├── dashboard.html          # Multi-tab dashboard
│   ├── report.html             # Report template
│   └── modules/                # One template per module
├── static/css/app.css          # Custom styling
├── instance/app.db             # SQLite DB (auto-created on first run)
├── reports/                    # Generated HTML/PDF reports land here
└── tests/
    └── test_smoke.py           # End-to-end test (all 12 modules)
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Browser (Bootstrap 5)                        │
│   Multi-tab Dashboard · Chart.js charts · D3.js network graph   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼ HTTP
┌─────────────────────────────────────────────────────────────────┐
│                       Flask Application                          │
│   Auth (Flask-Login) · Routes · Jinja2 templates · Reports     │
│                                                                 │
│   ┌────────────────────────────────────────────────────────┐    │
│   │ 12 analytics modules — one file per capability         │    │
│   │ VADER · scikit-learn · NetworkX · xhtml2pdf            │    │
│   └────────────────────────────────────────────────────────┘    │
│                               │                                 │
│                               ▼                                 │
│       data_collector.py  ──►  Apify API (X / Facebook)         │
│                               (synthetic-data fallback)         │
│                                                                 │
│       SQLAlchemy  ◄──►  SQLite (users · cases · posts)         │
└─────────────────────────────────────────────────────────────────┘
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for a deep dive.

---

## Tech Stack

| Layer            | Tools                                                                |
|------------------|----------------------------------------------------------------------|
| Backend          | **Python 3.9+** · **Flask 3** · Flask-Login · Flask-SQLAlchemy       |
| NLP              | **VADER** · NLTK · TextBlob                                          |
| Machine Learning | **scikit-learn** (TF-IDF, Logistic Regression, Gradient Boosting, KMeans) |
| Network science  | **NetworkX** (eigenvector centrality, betweenness, modularity)       |
| Frontend         | **Bootstrap 5** · **Chart.js 4** · **D3.js 7** · Bootstrap Icons     |
| Reporting        | Jinja2 + **xhtml2pdf** + reportlab                                   |
| Database         | **SQLite** (default) — switchable to MySQL/PostgreSQL via env var    |
| Data ingestion   | **Apify Client** (X & Facebook actors) + synthetic fallback          |
| Auth             | Flask-Login + Werkzeug **pbkdf2** password hashing                   |

---

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

The smoke test (`tests/test_smoke.py`) does a full end-to-end check:

1. Boots the Flask app with a temp SQLite DB
2. Registers a new user
3. Creates a case (with auto data collection via the synthetic fallback)
4. Hits **all 12 module endpoints** and asserts 200
5. Downloads both the HTML and PDF reports and asserts validity (PDF magic bytes)

Expected output:

```
tests/test_smoke.py::test_full_workflow PASSED [100%]
========================= 1 passed in ~3s =========================
```

---

## Troubleshooting

### `pycairo` build fails on `pip install`
Some `xhtml2pdf` versions transitively pull `pycairo`, which needs the native cairo lib.
The pinned versions in `requirements.txt` (`xhtml2pdf==0.2.11` + `reportlab==3.6.13`)
avoid this. If you've upgraded those, downgrade back, or install cairo via your OS:

```bash
# macOS
brew install cairo pkg-config

# Ubuntu / Debian
sudo apt install libcairo2-dev pkg-config python3-dev
```

### `AttributeError: module 'hashlib' has no attribute 'scrypt'`
Some Python builds (notably Python 3.9 on macOS without OpenSSL) lack scrypt. The app
already uses `pbkdf2:sha256` which works everywhere — but if you've forked
`models/user.py`, make sure `set_password` calls
`generate_password_hash(password, method="pbkdf2:sha256")`.

### "Address already in use" on port 5050
Another process is using port 5050. Either kill it or change the port:

```bash
# Edit app.py, last line: app.run(port=5050) → app.run(port=5051)
# Or via env var (simplest):
FLASK_RUN_PORT=5051 python app.py
```

### "No posts collected"
Two causes:
1. **No Apify token set** — this is fine; the app falls back to synthetic data
2. **Apify call failed** (network, quota, invalid actor) — check the Flask log; the app
   silently falls back to synthetic data so the case still works

### Database errors after upgrading the schema
The bundled SQLite DB is at `instance/app.db`. To wipe and start fresh:

```bash
rm instance/app.db
python app.py    # auto-creates a new DB on startup
```

### Charts don't render
Check the browser console (F12). Most likely causes:
- CDN blocked → app loads Chart.js & D3 from `cdn.jsdelivr.net` and `d3js.org`. If
  you're offline or behind a corporate proxy, mirror these to `static/` and update
  `templates/base.html`.
- Empty case (0 posts) → all module endpoints handle this gracefully and show empty states

### PDF report is blank or corrupt
Make sure `xhtml2pdf` and `reportlab` are pinned to the versions in `requirements.txt`.
Also check the Flask log for `xhtml2pdf` warnings.

---

## FAQ

**Q: Do I need an Apify account to use this?**
No. The app works out of the box with a built-in synthetic dataset that's deterministic
and shaped so all 12 modules produce realistic, non-trivial output.

**Q: Where is my data stored?**
SQLite database at `instance/app.db` (auto-created). To use Postgres or MySQL, set
`DATABASE_URL` to a SQLAlchemy connection string.

**Q: Can I add more analytics modules?**
Yes — drop a new file in `modules/<your_module>.py` exporting an `analyze_*(posts)`
function, then add a route + template. The pattern is identical for all 12 existing modules.

**Q: How do I switch from SQLite to MySQL/Postgres?**
```bash
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
python app.py    # tables are auto-created on first boot
```

**Q: Is there a chatbot or natural-language-query feature?**
Not in this version. The "Bonus" feature list mentions one as a future enhancement. The
existing real-time monitoring + anomaly detection + negative-sentiment alerts cover the
other listed bonus features.

**Q: How accurate is the Popularity Prediction model?**
On the bundled synthetic dataset (~80 posts), it scores **R² ≈ 0.89** and **MAE ≈ 26**
with an 80/20 holdout. Real-world accuracy depends heavily on how representative your
training data is — for production, swap in a transformer-based encoder (e.g. DistilBERT)
and a larger labeled corpus.

**Q: Can it run on Windows?**
Yes. Use `.venv\Scripts\activate` instead of `source .venv/bin/activate`. All Python
dependencies are cross-platform. The `xhtml2pdf` PDF export works on Windows too.

---

## Deployment

The app is a standard Flask WSGI application. For production:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5050 app:app
```

Required environment variables in production:

```bash
SECRET_KEY=<random 64-char string>
DATABASE_URL=postgresql://...        # don't use SQLite in prod
APIFY_API_TOKEN=apify_api_...
```

For a containerized deploy, a sample `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 5050
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5050", "app:app"]
```

---

## License

Educational / academic use. Built as a final project deliverable for the
*Social Media Analytics Dashboard Application* assignment.

---

## Credits

Built with: Flask · scikit-learn · NetworkX · VADER · Bootstrap · Chart.js · D3.js · Apify
>>>>>>> 7a5b439 (initial commit)
