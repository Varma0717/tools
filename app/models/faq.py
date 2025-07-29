from app.core.extensions import db
from datetime import datetime


class FAQ(db.Model):
    __tablename__ = "faqs"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    order_position = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(
        self, question, answer, category=None, order_position=0, featured=False
    ):
        self.question = question
        self.answer = answer
        self.category = category
        self.order_position = order_position
        self.featured = featured
