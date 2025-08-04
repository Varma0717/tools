from utils.extensions import db
from datetime import datetime


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default="#3B82F6")  # Hex color for UI
    icon = db.Column(db.String(50), nullable=True)  # CSS class or icon name
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    # SEO
    meta_description = db.Column(db.String(500), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, name, slug, **kwargs):
        self.name = name
        self.slug = slug
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)

    def __repr__(self):
        return f"<Category {self.name}>"
