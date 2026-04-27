# Architecture

## Layers

1. **Presentation** — Jinja2 templates rendered server-side, styled with Bootstrap 5 and
   custom CSS. Charts use Chart.js (bar, line, pie, doughnut, scatter) and D3.js (force-directed
   network graph).
2. **Application** — Flask handles routing, authentication (Flask-Login), session management,
   and report generation. Each route is a thin controller that delegates analytics work to a
   pure-function module under `modules/`.
3. **Analytics** — `modules/` contains one file per analytical capability. Each exports a
   function `analyze_*(posts) -> dict` that is independently testable and stateless.
4. **Data Access** — SQLAlchemy ORM models map to SQLite tables. Switching to MySQL or
   PostgreSQL only requires a `DATABASE_URL` env var.
5. **Ingestion** — `modules/data_collector.py` hits the Apify API for X (Twitter) and
   Facebook actors, normalizes results into the internal `Post` schema, and falls back to a
   deterministic synthetic dataset when no Apify token is configured.

## Request Flow Example — "Open Dashboard for Case 5"

1. Browser → `GET /cases/5/dashboard`
2. Flask route handler authenticates `current_user`, fetches the `Case` and its `Post`s
3. The handler calls `_run_full_analytics(case)` which runs all 12 module functions in
   sequence. Sentiment + fake-news mutate the Post rows (so labels persist).
4. The bundled analytics dict is rendered into `templates/dashboard.html`
5. Client-side: Chart.js + D3 render charts and the network graph from JSON embedded in the
   template

## Modules

```
modules/
├── data_collector.py    # Apify fetch + sample fallback
├── sentiment.py         # VADER
├── trends.py            # Frequency + trend score
├── network.py           # NetworkX graph + communities + centrality
├── recommendations.py   # Content + collaborative filtering
├── fake_news.py         # TF-IDF + Logistic Regression + heuristics
├── segmentation.py      # KMeans clustering
├── visualization.py     # Time series for charts
├── ad_optimization.py   # CTR / Conv / ROI
├── influencer.py        # Eigenvector + PageRank composite
├── realtime.py          # Anomaly detection on hourly buckets
├── competitor.py        # Cross-case comparison
├── popularity.py        # Gradient Boosting prediction
└── report.py            # HTML + PDF rendering
```

## Why This Shape?

- **Pure functions over hidden state** — every analytics module is a function of `posts`,
  which makes it trivial to unit-test, parallelize, and reason about.
- **One stack** — Python + Flask + Bootstrap means a single language across backend, ML,
  and templating. Tradeoff: heavier server-side rendering vs. a React SPA, but much simpler
  setup for an academic project.
- **SQLite default** — zero install, no Docker required. Easy to swap to Postgres for prod.
- **Apify-or-sample** — the app demonstrates the full feature set without requiring paid
  API keys, which matters for graders who may not have Apify credentials.
