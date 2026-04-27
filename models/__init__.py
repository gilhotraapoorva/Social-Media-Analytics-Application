from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User  # noqa: E402,F401
from models.case import Case  # noqa: E402,F401
from models.post import Post  # noqa: E402,F401
