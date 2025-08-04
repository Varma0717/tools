from utils.extensions import db
from datetime import datetime


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default="#6B7280")  # Hex color for UI

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, slug, **kwargs):
        self.name = name
        self.slug = slug
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)

    def __repr__(self):
        return f"<Tag {self.name}>"
