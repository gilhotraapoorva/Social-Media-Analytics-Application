"""
Social Media Analytics Dashboard Application — Flask entrypoint.

Modules implemented:
  1. Sentiment Analysis            7. Data Visualization
  2. Trending Topics Detection     8. Ad Campaign Optimization
  3. Network Analysis              9. Influencer Detection
  4. Recommendation System        10. Real-Time Monitoring
  5. Fake News Detection          11. Competitor Analysis
  6. User Segmentation            12. Popularity Prediction
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from flask import (
    Flask, render_template, redirect, url_for, request, flash, jsonify,
    abort, send_file,
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user,
)

from config import Config
from models import db, User, Case, Post

# Module imports
from modules import data_collector
from modules import sentiment as m_sentiment
from modules import trends as m_trends
from modules import network as m_network
from modules import recommendations as m_recs
from modules import fake_news as m_fake
from modules import segmentation as m_seg
from modules import visualization as m_viz
from modules import ad_optimization as m_ads
from modules import influencer as m_inf
from modules import realtime as m_rt
from modules import competitor as m_comp
from modules import popularity as m_pop
from modules import report as m_report


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance dir exists for SQLite
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_owned_case(case_id: int) -> Case:
    case = db.session.get(Case, case_id)
    if case is None or case.user_id != current_user.id:
        abort(404)
    return case


def _persist_collected_posts(case: Case, raw_posts: list) -> None:
    """Replace existing posts for a case with newly collected ones."""
    for old in list(case.posts):
        db.session.delete(old)
    db.session.flush()

    for raw in raw_posts:
        post = Post(
            case_id=case.id,
            external_id=raw.get("external_id"),
            platform=raw.get("platform", case.platform),
            author=raw.get("author"),
            text=raw.get("text", ""),
            url=raw.get("url"),
            posted_at=raw.get("posted_at"),
            likes=raw.get("likes", 0),
            retweets=raw.get("retweets", 0),
            replies=raw.get("replies", 0),
            impressions=raw.get("impressions", 0),
            hashtags=raw.get("hashtags", ""),
            mentions=raw.get("mentions", ""),
        )
        db.session.add(post)
    db.session.commit()


def _run_full_analytics(case: Case) -> dict:
    """Run all 12 analytics modules over a case's posts and return a bundle."""
    posts = list(case.posts)

    # Mutating analyses (sentiment, fake_news) update the post rows
    sentiment = m_sentiment.analyze_posts(posts)
    fake_news = m_fake.analyze_posts(posts)
    db.session.commit()

    return {
        "sentiment": sentiment,
        "trends": m_trends.analyze_trends(posts),
        "network": m_network.analyze_network(posts),
        "recommendations": m_recs.analyze_recommendations(posts),
        "fake_news": fake_news,
        "segmentation": m_seg.segment_users(posts),
        "visualization": m_viz.build_visualizations(posts),
        "ad_optimization": m_ads.analyze_campaigns(posts),
        "influencer": m_inf.detect_influencers(posts),
        "realtime": m_rt.monitor_keywords(posts),
        "popularity": m_pop.train_and_predict(posts),
        "negative_alerts": m_rt.negative_sentiment_alerts(posts),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def register_routes(app: Flask) -> None:

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("cases"))
        return redirect(url_for("login"))

    # ------------------- Auth -------------------

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            if not username or not email or not password:
                flash("All fields are required", "danger")
                return render_template("register.html")
            if User.query.filter((User.username == username) | (User.email == email)).first():
                flash("Username or email already taken", "warning")
                return render_template("register.html")
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("cases"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            identifier = request.form.get("identifier", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter(
                (User.username == identifier) | (User.email == identifier.lower())
            ).first()
            if not user or not user.check_password(password):
                flash("Invalid credentials", "danger")
                return render_template("login.html")
            login_user(user)
            return redirect(url_for("cases"))
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    # ------------------- Cases -------------------

    @app.route("/cases")
    @login_required
    def cases():
        my_cases = Case.query.filter_by(user_id=current_user.id).order_by(Case.created_at.desc()).all()
        return render_template("cases.html", cases=my_cases)

    @app.route("/cases/new", methods=["GET", "POST"])
    @login_required
    def new_case():
        if request.method == "POST":
            name = request.form.get("name", "").strip() or "Untitled Case"
            keyword = request.form.get("keyword", "").strip()
            if not keyword:
                flash("Keyword is required to collect data", "danger")
                return render_template("new_case.html")
            case = Case(
                user_id=current_user.id,
                name=name,
                brand=request.form.get("brand", "").strip() or None,
                keyword=keyword,
                platform=request.form.get("platform", "twitter"),
                api_source=request.form.get("api_source", "").strip() or None,
                post_urls=request.form.get("post_urls", "").strip() or None,
                description=request.form.get("description", "").strip() or None,
            )
            for field in ("start_date", "end_date"):
                value = request.form.get(field)
                if value:
                    try:
                        setattr(case, field, datetime.strptime(value, "%Y-%m-%d").date())
                    except ValueError:
                        pass
            db.session.add(case)
            db.session.commit()

            # Auto-collect on creation
            try:
                limit = int(request.form.get("limit", "100"))
            except ValueError:
                limit = 100
            raw = data_collector.collect_posts(keyword, case.platform, limit=limit)
            _persist_collected_posts(case, raw)

            flash(f"Case '{case.name}' created with {len(raw)} posts collected.", "success")
            return redirect(url_for("dashboard", case_id=case.id))
        return render_template("new_case.html")

    @app.route("/cases/<int:case_id>/delete", methods=["POST"])
    @login_required
    def delete_case(case_id):
        case = _get_owned_case(case_id)
        db.session.delete(case)
        db.session.commit()
        flash(f"Case '{case.name}' deleted.", "info")
        return redirect(url_for("cases"))

    @app.route("/cases/<int:case_id>/refresh", methods=["POST"])
    @login_required
    def refresh_case(case_id):
        case = _get_owned_case(case_id)
        try:
            limit = int(request.form.get("limit", "100"))
        except ValueError:
            limit = 100
        raw = data_collector.collect_posts(case.keyword, case.platform, limit=limit)
        _persist_collected_posts(case, raw)
        flash(f"Re-collected {len(raw)} posts.", "success")
        return redirect(url_for("dashboard", case_id=case.id))

    # ------------------- Dashboard (multi-tab) -------------------

    @app.route("/cases/<int:case_id>/dashboard")
    @login_required
    def dashboard(case_id):
        case = _get_owned_case(case_id)
        analytics = _run_full_analytics(case)
        return render_template("dashboard.html", case=case, analytics=analytics)

    # ------------------- Module-level views -------------------

    @app.route("/cases/<int:case_id>/modules/<module_name>")
    @login_required
    def module_view(case_id, module_name):
        case = _get_owned_case(case_id)
        analytics = _run_full_analytics(case)
        valid = {
            "sentiment", "trends", "network", "recommendations", "fake_news",
            "segmentation", "visualization", "ad_optimization", "influencer",
            "realtime", "competitor", "popularity",
        }
        if module_name not in valid:
            abort(404)
        # Competitor view needs all of the user's other cases
        other_cases = []
        if module_name == "competitor":
            other_cases = (
                Case.query.filter(Case.user_id == current_user.id, Case.id != case.id).all()
            )
        return render_template(
            f"modules/{module_name}.html",
            case=case,
            analytics=analytics,
            other_cases=other_cases,
        )

    # ------------------- Competitor compare endpoint -------------------

    @app.route("/cases/<int:case_id>/competitor/<int:other_id>")
    @login_required
    def competitor_compare(case_id, other_id):
        case_a = _get_owned_case(case_id)
        case_b = _get_owned_case(other_id)
        comparison = m_comp.compare_cases(
            list(case_a.posts), list(case_b.posts),
            label_a=case_a.name, label_b=case_b.name,
        )
        analytics = _run_full_analytics(case_a)
        analytics["competitor_comparison"] = comparison
        analytics["competitor_other"] = case_b
        return render_template(
            "modules/competitor.html",
            case=case_a, analytics=analytics, other_cases=[case_b],
            comparison=comparison, other=case_b,
        )

    # ------------------- API endpoints (JSON) -------------------

    @app.route("/api/cases/<int:case_id>/network")
    @login_required
    def api_network(case_id):
        case = _get_owned_case(case_id)
        return jsonify(m_network.analyze_network(list(case.posts)))

    @app.route("/api/cases/<int:case_id>/sentiment")
    @login_required
    def api_sentiment(case_id):
        case = _get_owned_case(case_id)
        return jsonify(m_sentiment.analyze_posts(list(case.posts)))

    # ------------------- Reports -------------------

    @app.route("/cases/<int:case_id>/report.<fmt>")
    @login_required
    def report(case_id, fmt):
        case = _get_owned_case(case_id)
        analytics = _run_full_analytics(case)
        if fmt == "html":
            path = m_report.write_html_report(case, analytics)
            return send_file(path, mimetype="text/html", as_attachment=True,
                             download_name=path.name)
        if fmt == "pdf":
            path = m_report.write_pdf_report(case, analytics)
            return send_file(path, mimetype="application/pdf", as_attachment=True,
                             download_name=path.name)
        abort(400)


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
