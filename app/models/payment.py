"""
Payment model for Super SEO Toolkit
Handles payment transactions and Razorpay integration
"""

from app.core.extensions import db
from datetime import datetime


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subscription_id = db.Column(
        db.Integer, db.ForeignKey("subscriptions.id"), nullable=True
    )

    # Razorpay details
    razorpay_payment_id = db.Column(db.String(100), nullable=False, unique=True)
    razorpay_order_id = db.Column(db.String(100), nullable=False)
    razorpay_signature = db.Column(db.String(200), nullable=True)

    # Payment details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default="USD")
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )  # pending, completed, failed, refunded
    payment_method = db.Column(db.String(50), nullable=False, default="razorpay")

    # Plan details
    plan = db.Column(db.String(50), nullable=False)
    billing_cycle = db.Column(db.String(20), nullable=False)  # monthly, annual

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship("User", backref="payments")

    def __repr__(self):
        return f"<Payment {self.razorpay_payment_id}: ${self.amount} ({self.status})>"

    @property
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == "completed"

    def mark_completed(self):
        """Mark payment as completed"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def mark_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = "failed"
        if reason:
            self.failure_reason = reason
        db.session.commit()

    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            "id": self.id,
            "payment_id": self.razorpay_payment_id,
            "order_id": self.razorpay_order_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "payment_method": self.payment_method,
            "plan": self.plan,
            "billing_cycle": self.billing_cycle,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }
