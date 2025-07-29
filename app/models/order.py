"""
Order model for tracking user orders.
"""

from app.core.extensions import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    user = db.relationship("User", back_populates="orders")

    def __repr__(self):
        return f"<Order {self.id}>"


class Download(db.Model):
    __tablename__ = "downloads"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", back_populates="downloads")

    def __repr__(self):
        return f"<Download {self.file_name}>"
