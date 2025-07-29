from app.core.extensions import db
from datetime import datetime


class Testimonial(db.Model):
    __tablename__ = "testimonials"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    avatar = db.Column(db.String(255), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(
        self,
        author,
        content,
        company=None,
        rating=5,
        avatar=None,
        position=None,
        featured=False,
    ):
        self.author = author
        self.content = content
        self.company = company
        self.rating = rating
        self.avatar = avatar
        self.position = position
        self.featured = featured
