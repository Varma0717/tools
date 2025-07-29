# models/subscription.py

from app.core.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum


class SubscriptionType(enum.Enum):
    FREE = "free"
    PRO = "pro"


class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_type = Column(
        Enum(SubscriptionType), default=SubscriptionType.FREE, nullable=False
    )
    status = Column(
        Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False
    )
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)
    paypal_subscription_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship
    user = relationship("User", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription")

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False
        if self.end_date and datetime.utcnow() > self.end_date:
            return False
        return True

    @property
    def is_pro(self):
        """Check if user has pro subscription"""
        return self.subscription_type == SubscriptionType.PRO and self.is_active

    def upgrade_to_pro(self, paypal_subscription_id=None):
        """Upgrade subscription to Pro"""
        self.subscription_type = SubscriptionType.PRO
        self.status = SubscriptionStatus.ACTIVE
        self.start_date = datetime.utcnow()
        self.end_date = datetime.utcnow() + timedelta(days=30)  # 30 days
        self.paypal_subscription_id = paypal_subscription_id
        self.updated_at = datetime.utcnow()

    def cancel_subscription(self):
        """Cancel the subscription"""
        self.status = SubscriptionStatus.CANCELLED
        self.updated_at = datetime.utcnow()


class Payment(db.Model):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)

    # PayPal fields
    paypal_payment_id = Column(String(100), nullable=True)
    paypal_order_id = Column(String(100), nullable=True)

    # Stripe fields
    stripe_payment_intent_id = Column(String(100), nullable=True)
    stripe_session_id = Column(String(100), nullable=True)

    # Common fields
    amount = Column(String(20), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String(20), default="completed", nullable=False)
    payment_method = Column(
        String(20), default="paypal", nullable=False
    )  # 'paypal' or 'stripe'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    subscription = relationship("Subscription", back_populates="payments")


class AIToolUsage(db.Model):
    __tablename__ = "ai_tool_usage"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    usage_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    month_year = Column(String(7), nullable=False)  # Format: "2025-01"

    # Relationship
    user = relationship("User")

    @classmethod
    def get_monthly_usage(cls, user_id, tool_name=None):
        """Get monthly usage count for user"""
        current_month = datetime.utcnow().strftime("%Y-%m")
        query = cls.query.filter_by(user_id=user_id, month_year=current_month)
        if tool_name:
            query = query.filter_by(tool_name=tool_name)
        return query.count()

    @classmethod
    def record_usage(cls, user_id, tool_name):
        """Record AI tool usage"""
        current_month = datetime.utcnow().strftime("%Y-%m")
        usage = cls(user_id=user_id, tool_name=tool_name, month_year=current_month)
        db.session.add(usage)
        db.session.commit()
