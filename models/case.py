from datetime import datetime

from models import db


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    name = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(120), nullable=True)
    keyword = db.Column(db.String(120), nullable=False)
    platform = db.Column(db.String(40), nullable=False, default="twitter")
    api_source = db.Column(db.String(255), nullable=True)
    post_urls = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship("Post", backref="case", lazy=True, cascade="all, delete-orphan")

    @property
    def post_count(self) -> int:
        return len(self.posts)
