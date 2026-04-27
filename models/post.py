from datetime import datetime

from models import db


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False, index=True)

    external_id = db.Column(db.String(120), nullable=True)
    platform = db.Column(db.String(40), nullable=False, default="twitter")
    author = db.Column(db.String(120), nullable=True, index=True)
    text = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(512), nullable=True)
    posted_at = db.Column(db.DateTime, nullable=True)

    likes = db.Column(db.Integer, default=0)
    retweets = db.Column(db.Integer, default=0)
    replies = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)

    hashtags = db.Column(db.Text, nullable=True)  # comma-separated
    mentions = db.Column(db.Text, nullable=True)  # comma-separated

    sentiment_label = db.Column(db.String(20), nullable=True)
    sentiment_score = db.Column(db.Float, nullable=True)
    is_fake = db.Column(db.Boolean, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def engagement(self) -> int:
        return (self.likes or 0) + (self.retweets or 0) + (self.replies or 0)

    @property
    def hashtag_list(self) -> list:
        return [h for h in (self.hashtags or "").split(",") if h]

    @property
    def mention_list(self) -> list:
        return [m for m in (self.mentions or "").split(",") if m]
